"""Protocol tests for the stdio JSON-RPC server (``densa.mcp.server``).

Covers the transport state table: handshake, tools/list, tools/call
happy path, every JSON-RPC error code the SPEC lists (-32700/-32600/
-32601/-32602/-32603), and the notification rule (no reply, ever).
"""

from __future__ import annotations

import io
import json

import pytest

from densa.mcp import server
from densa.mcp.tools import TOOL_SCHEMAS

from .conftest import MiniVault, make_wiki_page


def _run(repo, raw_lines: list[str]) -> list[dict]:
    """Feed raw stdin lines through ``serve``; return parsed responses."""
    out = io.StringIO()
    server.serve(repo, io.StringIO("\n".join(raw_lines) + "\n"), out)
    return [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]


def _req(req_id, method, **params) -> str:
    msg: dict = {"jsonrpc": "2.0", "method": method}
    if req_id is not None:
        msg["id"] = req_id
    if params:
        msg["params"] = params
    return json.dumps(msg)


# --- Handshake + discovery ------------------------------------------------

def test_initialize(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, [_req(1, "initialize")])
    assert resp["id"] == 1
    result = resp["result"]
    assert result["protocolVersion"] == server.PROTOCOL_VERSION
    assert result["serverInfo"]["name"] == "densa"
    assert "tools" in result["capabilities"]


def test_tools_list_mirrors_schemas(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, [_req(2, "tools/list")])
    names = [t["name"] for t in resp["result"]["tools"]]
    assert names == [t["name"] for t in TOOL_SCHEMAS]
    assert len(names) == 8


def test_ping(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, [_req(3, "ping")])
    assert resp["result"] == {}


# --- tools/call happy path ------------------------------------------------

def test_tools_call_read_page(mini_vault: MiniVault) -> None:
    rel = "domains/psychology/wiki/concepts/c.md"
    mini_vault.write(rel, make_wiki_page())
    [resp] = _run(
        mini_vault.root,
        [_req(4, "tools/call", name="read_page", arguments={"path": rel})],
    )
    content = resp["result"]["content"]
    assert content[0]["type"] == "text"
    payload = json.loads(content[0]["text"])  # tool dict is JSON-encoded text
    assert payload["path"] == rel
    assert payload["is_raw"] is False


# --- Error codes (SPEC "Transport") ---------------------------------------

def test_unknown_tool_is_invalid_params(mini_vault: MiniVault) -> None:
    [resp] = _run(
        mini_vault.root,
        [_req(5, "tools/call", name="nope", arguments={})],
    )
    assert resp["error"]["code"] == server.INVALID_PARAMS  # -32602


def test_tools_call_missing_required_arg_is_invalid_params(
    mini_vault: MiniVault,
) -> None:
    [resp] = _run(
        mini_vault.root,
        [_req(6, "tools/call", name="read_page", arguments={})],
    )
    assert resp["error"]["code"] == server.INVALID_PARAMS


def test_tools_call_without_name_is_invalid_params(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, [_req(7, "tools/call", arguments={})])
    assert resp["error"]["code"] == server.INVALID_PARAMS


def test_unknown_method_is_method_not_found(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, [_req(8, "frobnicate")])
    assert resp["error"]["code"] == server.METHOD_NOT_FOUND  # -32601


def test_parse_error(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, ["{ this is not json"])
    assert resp["error"]["code"] == server.PARSE_ERROR  # -32700
    assert resp["id"] is None


def test_invalid_request_wrong_jsonrpc(mini_vault: MiniVault) -> None:
    [resp] = _run(mini_vault.root, [json.dumps({"id": 9, "method": "ping"})])
    assert resp["error"]["code"] == server.INVALID_REQUEST  # -32600


def test_internal_error_is_contained(mini_vault: MiniVault, monkeypatch) -> None:
    """D1: an unexpected (non-ToolError) exception from a tool must be
    caught and mapped to -32603, not crash the loop."""
    def boom(*_a, **_k):
        raise ValueError("kaboom")

    monkeypatch.setattr(server, "call_tool", boom)
    [resp] = _run(
        mini_vault.root,
        [_req(10, "tools/call", name="vault_status", arguments={})],
    )
    assert resp["error"]["code"] == server.INTERNAL_ERROR  # -32603


# --- Notification rule: never reply ---------------------------------------

def test_notification_initialized_gets_no_reply(mini_vault: MiniVault) -> None:
    assert _run(mini_vault.root, [_req(None, "notifications/initialized")]) == []


def test_notification_even_on_error_gets_no_reply(mini_vault: MiniVault) -> None:
    # A notification for an unknown method must still produce no response.
    assert _run(mini_vault.root, [_req(None, "frobnicate")]) == []


# --- Loop survives a bad message and keeps serving ------------------------

def test_loop_continues_after_parse_error(mini_vault: MiniVault) -> None:
    responses = _run(
        mini_vault.root,
        ["{ broken", _req(11, "ping")],
    )
    codes = [r.get("error", {}).get("code") for r in responses]
    assert server.PARSE_ERROR in codes
    assert any(r.get("id") == 11 and "result" in r for r in responses)


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_lines_ignored(mini_vault: MiniVault, blank: str) -> None:
    assert _run(mini_vault.root, [blank, _req(12, "ping")]) == [
        {"jsonrpc": "2.0", "id": 12, "result": {}}
    ]
