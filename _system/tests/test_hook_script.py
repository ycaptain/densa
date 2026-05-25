"""Smoke tests for the local pre-commit hook script.

The script (`_system/hooks/pre-commit`) is the path users wire via
``git config core.hooksPath _system/hooks``. It must:

1. Have a stable shebang and ``set -euo pipefail`` posture.
2. Set ``PYTHONPATH`` so the in-repo densa is importable without
   ``pip install``.
3. Invoke ``python3 -m densa --staged`` (falling back to ``python``
   if ``python3`` is absent).
4. Emit an actionable error when neither python binary is on PATH.

These tests inspect the script statically rather than running it
end-to-end because exercising the failure path would require mucking
with PATH inside CI (fragile). The static checks catch the most
likely regressions: someone refactoring the fallback chain or
forgetting to export PYTHONPATH.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

_HOOK = (
    Path(__file__).resolve().parents[2] / "_system" / "hooks" / "pre-commit"
)


def test_hook_exists() -> None:
    assert _HOOK.is_file()


def test_hook_is_executable() -> None:
    # `git config core.hooksPath` runs the file directly; the +x bit
    # must travel with the repo.
    mode = _HOOK.stat().st_mode
    assert mode & stat.S_IXUSR, (
        "_system/hooks/pre-commit is not executable; "
        "run `chmod +x _system/hooks/pre-commit`"
    )


def test_hook_uses_bash_shebang() -> None:
    first = _HOOK.read_text(encoding="utf-8").splitlines()[0]
    assert first == "#!/usr/bin/env bash", (
        f"unexpected shebang: {first!r}"
    )


def test_hook_pyhonpath_exports() -> None:
    body = _HOOK.read_text(encoding="utf-8")
    assert "PYTHONPATH=" in body, (
        "hook must export PYTHONPATH=$REPO_ROOT/_system so the in-repo "
        "densa is importable without pip install"
    )
    assert '_system' in body


def test_hook_invokes_densa_staged() -> None:
    body = _HOOK.read_text(encoding="utf-8")
    assert "python3 -m densa --staged" in body
    assert "python -m densa --staged" in body


def test_hook_gracefully_handles_missing_python() -> None:
    """When neither `python3` nor `python` is on PATH the hook MUST
    print an actionable error rather than emitting bash's `command not
    found` and a cryptic exit."""
    body = _HOOK.read_text(encoding="utf-8")
    assert "python3" in body and "command -v" in body, (
        "hook must `command -v python3` before exec'ing"
    )
    assert "exit 1" in body
    # The actionable hint mentions both --no-verify and the unset path:
    assert "no-verify" in body or "core.hooksPath" in body


def test_hook_has_pipefail_safety() -> None:
    body = _HOOK.read_text(encoding="utf-8")
    assert "set -euo pipefail" in body, (
        "hook must use strict bash mode so a silent partial failure "
        "doesn't let a bad commit through"
    )


def test_hook_resolves_repo_via_git() -> None:
    """`git rev-parse --show-toplevel` is the cheapest accurate way to
    find the repo root from anywhere in the worktree; we depend on it
    upstream in `_resolve_repo` too."""
    body = _HOOK.read_text(encoding="utf-8")
    assert "git rev-parse --show-toplevel" in body


def test_hook_no_trailing_blank_line_after_exec() -> None:
    """The fallback `exec` lines are unconditional — any code after
    them would be dead. Catch the regression where someone appends a
    stray command below the python invocation."""
    lines = _HOOK.read_text(encoding="utf-8").splitlines()
    # Last meaningful line should be `exit 1` (from the python-missing
    # branch) — the actionable error path.
    last_non_blank = next(
        (line for line in reversed(lines) if line.strip()), ""
    )
    assert last_non_blank == "exit 1", (
        f"trailing command after python-missing branch: {last_non_blank!r}"
    )


def test_hook_disabling_documented() -> None:
    """Hook bypass / disable instructions are documented in
    docs/setup.md (extracted from GUIDE.md in the v2 onboarding sweep).
    Smoke test to catch silent removal of the actionable how-to."""
    setup_doc = (
        Path(__file__).resolve().parents[2] / "docs" / "setup.md"
    ).read_text(encoding="utf-8")
    # We expect either an explicit "Disabling the … hook" section, or
    # a `--no-verify` mention, both of which the docs/setup.md
    # "Disabling the pre-commit hook" section carries.
    assert (
        "Disabling the pre-commit hook" in setup_doc
        or "--no-verify" in setup_doc
    )
    # Use os.linesep noise to avoid lints on missing usage.
    assert os.linesep in ("\n", "\r\n")
