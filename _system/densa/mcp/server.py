"""Stdio JSON-RPC 2.0 server exposing the eight read-only Densa tools.

Transport per ``SPEC.md``: each message is a single newline-delimited
JSON object on ``stdin``/``stdout``. Stdlib-only (``json`` + ``sys``).

Error model (design decision D1): a tool raising :class:`~densa.mcp.tools.ToolError`
maps to its JSON-RPC code (an *expected* failure — bad params, missing
path). Any *other* exception is an implementation bug; this layer is the
single place that contains it, mapping it to ``-32603`` so one bad
request can never kill the long-lived stdio loop. Tools stay transport-
and catch-free; the boundary lives here.

The server is stateless: pagination cursors are opaque and self-describing
(see :func:`densa.mcp.tools._encode_cursor`), so no session state is held
between requests.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import IO, Any

from densa.mcp.tools import TOOL_SCHEMAS, ToolError, call_tool

# MCP protocol revision this server implements (handshake echo).
PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "densa"

# JSON-RPC 2.0 standard error codes (SPEC.md "Transport").
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def _ok(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _server_version() -> str:
    from densa import __version__  # noqa: PLC0415 (lazy: avoids import cycle)

    return __version__


def handle(repo: Path, request: Any) -> dict[str, Any] | None:
    """Map one parsed JSON-RPC request to a response, or ``None``.

    Returns ``None`` for a notification (a message with no ``id``): per
    JSON-RPC 2.0 the server MUST NOT reply to notifications, even on error.
    """
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        # A malformed request object still has no id we can trust.
        return _err(None, INVALID_REQUEST, "invalid request")

    is_notification = "id" not in request
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params")
    if not isinstance(params, dict):
        params = {}

    try:
        result = _dispatch(repo, method, params)
    except ToolError as exc:
        # Expected, client-visible failure — surface its JSON-RPC code.
        return None if is_notification else _err(req_id, exc.code, exc.message)
    except _MethodNotFound:
        return None if is_notification else _err(
            req_id, METHOD_NOT_FOUND, f"method not found: {method!r}"
        )
    except Exception as exc:  # D1: contain any tool/impl bug at this boundary
        return None if is_notification else _err(
            req_id, INTERNAL_ERROR, f"internal error: {exc}"
        )

    if result is None:  # a handled notification (e.g. notifications/initialized)
        return None
    return None if is_notification else _ok(req_id, result)


class _MethodNotFound(Exception):
    """Internal sentinel so dispatch stays a pure mapping."""


def _dispatch(repo: Path, method: Any, params: dict[str, Any]) -> dict[str, Any] | None:
    """Return the result dict for *method*, or ``None`` for a notification
    that needs no result. Raises :class:`_MethodNotFound` for unknown methods
    and :class:`ToolError` for bad params."""
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": _server_version()},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOL_SCHEMAS}
    if method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str) or not name:
            raise ToolError("tools/call requires a string 'name'")
        arguments = params.get("arguments")
        if not isinstance(arguments, dict):
            arguments = {}
        payload = call_tool(repo, name, arguments)
        return {
            "content": [
                {"type": "text", "text": json.dumps(payload, ensure_ascii=False)}
            ]
        }
    if isinstance(method, str) and method.startswith("notifications/"):
        return None  # notification: acknowledged, no result
    raise _MethodNotFound


def serve(repo: Path, in_stream: IO[str], out_stream: IO[str]) -> None:
    """Read newline-delimited JSON-RPC requests until EOF, writing one
    newline-delimited response per non-notification message."""
    for raw in in_stream:
        line = raw.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            _write(out_stream, _err(None, PARSE_ERROR, "parse error"))
            continue
        response = handle(repo, request)
        if response is not None:
            _write(out_stream, response)


def _write(out_stream: IO[str], obj: dict[str, Any]) -> None:
    out_stream.write(json.dumps(obj, ensure_ascii=False) + "\n")
    out_stream.flush()


def main(argv: list[str] | None = None) -> int:
    from densa.cli import _resolve_repo  # noqa: PLC0415 (lazy: avoids import cycle)

    serve(_resolve_repo(), sys.stdin, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
