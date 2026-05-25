"""``--auto-inject`` — start an AI coding agent with the bootstrap prompt loaded.

Strategy by agent (in priority order for ``auto``):

1. **Cursor** (``agent`` CLI). We spawn ``agent --print "<prompt>"`` if
   the user wants one-shot, or ``agent "<prompt>"`` for an interactive
   session that takes over the terminal. We default to interactive
   because bootstrap is multi-step.
2. **Claude Code** (``claude`` CLI). ``claude "<prompt>"`` for
   interactive; ``claude -p "<prompt>"`` for one-shot.
3. **Codex CLI** (``codex`` CLI). Similar surface to Cursor.

Fallback: copy the bootstrap prompt to the system clipboard (pbcopy on
macOS, xclip on Linux, clip on Windows) and print instructions. The
fallback is what runs when ``--auto-inject=none`` or when no agent CLI
is on PATH.

This module is loaded lazily by :mod:`densa.commands.init` so the
common ``densa init`` (without ``--auto-inject``) doesn't pay any
import cost for agent detection logic.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final

# Map ``--auto-inject`` choice → (CLI binary name, interactive-launch arg list).
# The argv list is templated with ``{prompt}``; we splice the prompt in at run time.
_AGENT_LAUNCHERS: Final[dict[str, tuple[str, list[str]]]] = {
    "cursor":      ("agent",  ["{prompt}"]),
    "claude-code": ("claude", ["{prompt}"]),
    "codex":       ("codex",  ["{prompt}"]),
}

_AUTO_PRIORITY: Final[tuple[str, ...]] = ("cursor", "claude-code", "codex")

_BOOTSTRAP_REL: Final[str] = "_system/prompts/bootstrap.md"


def inject(vault: Path, choice: str) -> int:
    """Start the chosen agent CLI inside ``vault`` with the bootstrap
    prompt loaded. Returns the CLI exit code (or a clipboard-fallback
    return code).

    ``choice``: ``"cursor"`` / ``"claude-code"`` / ``"codex"`` /
    ``"auto"``. ``"none"`` should never reach this function — the
    caller skips invocation altogether.
    """
    prompt = _read_bootstrap_prompt(vault)
    if prompt is None:
        return 1

    agent = _resolve_agent(choice)
    if agent is None:
        return _clipboard_fallback(prompt, requested=choice)

    bin_name, argv_template = _AGENT_LAUNCHERS[agent]
    argv = [bin_name] + [a.replace("{prompt}", prompt) for a in argv_template]

    print(f"Starting {bin_name} in {vault} ...")
    # cwd=vault is load-bearing — Cursor and Claude Code both treat the
    # cwd as the workspace they're opening against.
    try:
        return subprocess.run(argv, cwd=vault, check=False).returncode
    except FileNotFoundError:
        # Race condition: shutil.which succeeded but spawn failed. Fall
        # back to clipboard so the user still gets the prompt.
        print(f"warning: failed to spawn {bin_name}", file=sys.stderr)
        return _clipboard_fallback(prompt, requested=choice)


# --- internals --------------------------------------------------------------


def _read_bootstrap_prompt(vault: Path) -> str | None:
    p = vault / _BOOTSTRAP_REL
    if not p.is_file():
        print(
            f"agent-inject: error: {_BOOTSTRAP_REL} not found in vault",
            file=sys.stderr,
        )
        return None
    return p.read_text(encoding="utf-8")


def _resolve_agent(choice: str) -> str | None:
    """Return the agent key to launch, or None if none available."""
    if choice == "auto":
        for candidate in _AUTO_PRIORITY:
            if shutil.which(_AGENT_LAUNCHERS[candidate][0]):
                return candidate
        return None
    if choice not in _AGENT_LAUNCHERS:
        print(f"agent-inject: unknown agent {choice!r}", file=sys.stderr)
        return None
    if shutil.which(_AGENT_LAUNCHERS[choice][0]):
        return choice
    return None


def _clipboard_fallback(prompt: str, requested: str) -> int:
    """Copy the prompt to the system clipboard and print instructions.

    Returns 0 if the clipboard write succeeded, 2 otherwise (the user
    can still copy manually from the printed path).
    """
    cmd = _clipboard_command()
    copied = False
    if cmd is not None:
        try:
            subprocess.run(cmd, input=prompt, text=True, check=True)
            copied = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    print()
    if requested != "auto":
        print(
            f"note: --auto-inject={requested} requested but the "
            f"{_AGENT_LAUNCHERS.get(requested, ('?',))[0]} CLI was not on PATH."
        )
    else:
        print("note: no AI agent CLI detected on PATH "
              "(cursor `agent`, `claude`, `codex`).")
    print()
    if copied:
        print("✓ Bootstrap prompt copied to clipboard.")
        print()
    print("Next step:")
    print("  1. Open the vault folder in your AI-pair IDE.")
    if copied:
        print("  2. Paste (⌘V / Ctrl-V) the bootstrap prompt into the chat.")
    else:
        print(f"  2. Open {_BOOTSTRAP_REL} and paste its contents into the chat.")
    print()
    return 0 if copied else 2


def _clipboard_command() -> list[str] | None:
    """Return the platform-appropriate clipboard-write command, or None
    if no candidate is on PATH."""
    system = platform.system()
    candidates: list[list[str]]
    if system == "Darwin":
        candidates = [["pbcopy"]]
    elif system == "Windows":
        # cmd's `clip` is present on every modern Windows.
        candidates = [["clip"]]
    else:  # Linux / BSD
        candidates = [["xclip", "-selection", "clipboard"], ["wl-copy"]]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            return cmd
    return None
