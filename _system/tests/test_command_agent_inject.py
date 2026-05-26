"""Tests for ``densa.commands.agent_inject``.

We avoid spawning real AI-agent CLIs. The interesting surface is:

- ``_resolve_agent`` — choice + PATH detection.
- ``_clipboard_command`` — platform routing.
- ``inject`` fallback path (clipboard) when no agent CLI is on PATH.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from densa.commands import agent_inject

# --- _resolve_agent ---------------------------------------------------------


def test_resolve_agent_explicit_choice_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ``choice`` is explicit and that CLI is on PATH, we return it."""
    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert agent_inject._resolve_agent("cursor") == "cursor"


def test_resolve_agent_explicit_choice_when_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the requested CLI is not on PATH, return None so the caller
    falls back to clipboard."""
    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: None)
    assert agent_inject._resolve_agent("cursor") is None


def test_resolve_agent_auto_prefers_cursor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``auto`` walks the priority list (cursor > claude-code > codex)."""
    monkeypatch.setattr(
        agent_inject.shutil,
        "which",
        lambda name: f"/usr/bin/{name}" if name in ("agent", "claude") else None,
    )
    assert agent_inject._resolve_agent("auto") == "cursor"


def test_resolve_agent_auto_falls_through(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``auto`` returns None when nothing on PATH."""
    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: None)
    assert agent_inject._resolve_agent("auto") is None


def test_resolve_agent_invalid_choice(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Unknown agent keys are rejected with a clean error."""
    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: "/usr/bin/agent")
    assert agent_inject._resolve_agent("unknown-agent") is None
    err = capsys.readouterr().err
    assert "unknown agent" in err


# --- _clipboard_command -----------------------------------------------------


def test_clipboard_command_macos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent_inject.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert agent_inject._clipboard_command() == ["pbcopy"]


def test_clipboard_command_linux_xclip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent_inject.platform, "system", lambda: "Linux")
    # xclip present, wl-copy absent.
    monkeypatch.setattr(
        agent_inject.shutil,
        "which",
        lambda name: "/usr/bin/xclip" if name == "xclip" else None,
    )
    assert agent_inject._clipboard_command() == ["xclip", "-selection", "clipboard"]


def test_clipboard_command_linux_wl_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    """When only wl-copy is on PATH, return that."""
    monkeypatch.setattr(agent_inject.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        agent_inject.shutil,
        "which",
        lambda name: "/usr/bin/wl-copy" if name == "wl-copy" else None,
    )
    assert agent_inject._clipboard_command() == ["wl-copy"]


def test_clipboard_command_none_when_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(agent_inject.platform, "system", lambda: "Linux")
    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: None)
    assert agent_inject._clipboard_command() is None


# --- inject() integration ---------------------------------------------------


def test_inject_missing_bootstrap_prompt(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without docs/bootstrap.md the function fails cleanly."""
    rc = agent_inject.inject(tmp_path, choice="auto")
    assert rc == 1
    err = capsys.readouterr().err
    assert "bootstrap.md" in err


def test_inject_clipboard_fallback_when_no_agent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When no agent CLI is on PATH, we fall back to clipboard +
    instructions, and return 0 (the user can still proceed)."""
    bootstrap = tmp_path / "docs"
    bootstrap.mkdir(parents=True)
    (bootstrap / "bootstrap.md").write_text("hello world prompt")

    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: None)

    # Stub the clipboard command to a no-op that succeeds.
    monkeypatch.setattr(agent_inject, "_clipboard_command", lambda: ["true"])
    fake_run = MagicMock(return_value=None)
    monkeypatch.setattr(agent_inject.subprocess, "run", fake_run)

    rc = agent_inject.inject(tmp_path, choice="auto")
    assert rc == 0

    out = capsys.readouterr().out
    assert "no AI agent CLI detected" in out
    assert "copied to clipboard" in out

    fake_run.assert_called_once()
    args, kwargs = fake_run.call_args
    assert args[0] == ["true"]
    assert kwargs["input"] == "hello world prompt"
    assert kwargs["text"] is True
    assert kwargs["check"] is True


def test_inject_explicit_agent_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--auto-inject=cursor`` with no `agent` on PATH falls back to
    clipboard and tells the user *which* agent was missing."""
    bootstrap = tmp_path / "docs"
    bootstrap.mkdir(parents=True)
    (bootstrap / "bootstrap.md").write_text("prompt body")

    monkeypatch.setattr(agent_inject.shutil, "which", lambda name: None)
    monkeypatch.setattr(agent_inject, "_clipboard_command", lambda: None)

    rc = agent_inject.inject(tmp_path, choice="cursor")
    # Clipboard write failed (cmd=None), so we return 2 — user still
    # gets the instructions to read the file manually.
    assert rc == 2
    out = capsys.readouterr().out
    assert "--auto-inject=cursor requested" in out
    assert "was not on PATH" in out
