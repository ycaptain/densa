"""Shared pytest fixtures.

The :func:`mini_vault` fixture builds a throwaway repo on disk with
exactly the layout the validator expects (an ``AGENTS.md`` at the root,
``domains/<X>/raw/sessions/`` etc.). Tests then write whichever files
they need into it via :class:`MiniVault.write` and run the rules.

We deliberately do not depend on the *real* vault under
``share/domains/`` for unit testing: tests should be hermetic and
fast, and the real vault's content changes as the template evolves.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Make ``densa`` importable when pytest is invoked from the repo root.
_HERE = Path(__file__).resolve().parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


@dataclass
class MiniVault:
    root: Path
    written: list[Path] = field(default_factory=list)

    def write(self, rel: str, text: str) -> Path:
        """Create a file at *rel* relative to the vault root."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.written.append(path)
        return path


@pytest.fixture
def mini_vault(tmp_path: Path) -> MiniVault:
    """A barebones vault layout: AGENTS.md root marker, no content yet."""
    (tmp_path / "AGENTS.md").write_text(
        "---\ntype: schema\n---\n# AGENTS\n", encoding="utf-8",
    )
    return MiniVault(root=tmp_path)


def make_wiki_page(
    type_: str = "concept",
    sources: str | list[str] | None = None,
    extra: str = "",
) -> str:
    """Produce a minimally-valid wiki page body for a given page type.

    Carries all nine universal frontmatter keys per AGENTS.md §3 so
    AGENTS003 does not fire spuriously on fixtures.
    """
    if sources is None:
        src_block = "sources: []\n"
    elif isinstance(sources, list):
        if sources:
            inner = ", ".join(f'"{s}"' for s in sources)
            src_block = f"sources: [{inner}]\n"
        else:
            src_block = "sources: []\n"
    else:
        src_block = f"sources: [\"{sources}\"]\n"
    return (
        "---\n"
        f"type: {type_}\n"
        "domain: psychology\n"
        "created: 2026-01-01\n"
        "updated: 2026-01-01\n"
        f"{src_block}"
        "aliases: []\n"
        "tags: []\n"
        "status: active\n"
        "compiled_against: 1\n"
        "---\n"
        "# Test page\n"
        f"{extra}"
    )
