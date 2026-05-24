"""Sanity test for the .pre-commit-hooks.yaml manifest.

This file is the public interface for users adopting densa via the
`pre-commit <https://pre-commit.com>` framework. If we accidentally
rename the entry point or change the language, downstream consumers
break with a cryptic "unknown id" error. A 30-line YAML lint here
catches that at the validator's own CI time.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = _REPO_ROOT / ".pre-commit-hooks.yaml"


def _parse_manifest() -> list[dict[str, str]]:
    """Minimal top-level-list YAML parser for our manifest.

    `.pre-commit-hooks.yaml` is a top-level list of mappings. Tests are
    stdlib-only so we hand-parse the trivial shape we ship: each hook
    block starts with ``- id: <name>`` and continues with indented
    ``  key: value`` lines until the next ``- `` or EOF.
    """
    text = _MANIFEST.read_text(encoding="utf-8")
    # Strip full-line comments (and blank lines for simpler splitting).
    body_lines = [
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    hooks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in body_lines:
        line = raw_line
        if line.startswith("- "):
            if current is not None:
                hooks.append(current)
            current = {}
            line = line[2:]  # drop "- " prefix
        if current is None:
            continue
        m = re.match(r"^\s*([A-Za-z0-9_\-]+)\s*:\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            # Strip surrounding brackets/quotes for trivial scalars.
            if value.startswith(("'", '"')) and value.endswith(value[0]):
                value = value[1:-1]
            current[key] = value
    if current is not None:
        hooks.append(current)
    return hooks


def test_manifest_exists() -> None:
    assert _MANIFEST.is_file(), "missing .pre-commit-hooks.yaml"


def test_densa_hook_declared() -> None:
    hooks = _parse_manifest()
    ids = [h.get("id") for h in hooks]
    assert "densa" in ids, f"hook id `densa` missing; got {ids!r}"


def test_densa_entry_invokes_module() -> None:
    """Entry must call ``python -m densa --staged`` so the manifest
    stays in sync with the local hook and CI."""
    [hook] = [h for h in _parse_manifest() if h.get("id") == "densa"]
    entry = str(hook.get("entry", ""))
    assert entry.endswith("python -m densa --staged"), (
        f"entry has drifted: {entry!r}"
    )


def test_densa_language_is_python() -> None:
    """`language: python` makes pre-commit build an isolated venv and
    install the repo via pyproject.toml — that's how `densa` becomes
    importable."""
    [hook] = [h for h in _parse_manifest() if h.get("id") == "densa"]
    assert hook.get("language") == "python"


def test_densa_always_runs() -> None:
    """We need always_run + pass_filenames=false because `--staged` is
    a whole-changeset operation; pre-commit's per-file invocation
    model would double-count or partition incorrectly."""
    [hook] = [h for h in _parse_manifest() if h.get("id") == "densa"]
    assert hook.get("always_run") == "true"
    assert hook.get("pass_filenames") == "false"
