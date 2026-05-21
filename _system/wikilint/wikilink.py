"""Wikilink scanning and resolution.

Obsidian uses ``[[shortest-unique-slug]]`` to link between pages. We
mirror the resolver's behaviour: a target resolves if there's exactly
one file in the repo whose path-without-extension *ends with* the
target's path components.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from wikilint.config import SKIP_DIRS

WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
"""Match ``[[anything-but-brackets-or-newline]]``. Greedy non-empty body."""

_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


class ResolutionStatus(str, Enum):
    """How a wikilink resolved against the index."""

    OK = "ok"
    AMBIGUOUS = "ambiguous"
    MISSING = "missing"
    ANCHOR_ONLY = "anchor-only"


@dataclass(frozen=True)
class Resolution:
    status: ResolutionStatus
    hits: tuple[str, ...] = ()


# --- Slug index -----------------------------------------------------------

SlugIndex = dict[str, list[str]]
"""Map ``"slug"`` / ``"sub/path/slug"`` → list of full repo-relative
paths-without-extension that end with that suffix.
"""


def _walk_markdown(repo: Path) -> Iterator[Path]:
    for p in repo.rglob("*.md"):
        rel = p.relative_to(repo)
        if not any(part in SKIP_DIRS for part in rel.parts):
            yield rel


def build_index(repo: Path) -> SlugIndex:
    """Build the slug → paths map for every markdown file under *repo*."""
    idx: SlugIndex = {}
    for rel in _walk_markdown(repo):
        no_ext = str(rel.with_suffix("")).replace("\\", "/")
        parts = no_ext.split("/")
        for i in range(len(parts)):
            suffix = "/".join(parts[i:])
            idx.setdefault(suffix, []).append(no_ext)
    return idx


# --- Resolution -----------------------------------------------------------

def resolve(target: str, idx: SlugIndex) -> Resolution:
    """Resolve a single wikilink body (everything between ``[[`` ``]]``).

    Strips display labels (``slug|Display``), section anchors
    (``slug#section`` or ``slug#^block-id``), and trailing ``.md``.
    """
    target = target.replace("\\|", "|")
    main = target.split("|", 1)[0].split("#", 1)[0].strip()
    main = main[:-3] if main.endswith(".md") else main
    if not main:
        return Resolution(ResolutionStatus.ANCHOR_ONLY)
    hits = sorted(set(idx.get(main, [])))
    if not hits:
        return Resolution(ResolutionStatus.MISSING)
    if len(hits) > 1:
        return Resolution(ResolutionStatus.AMBIGUOUS, tuple(hits))
    return Resolution(ResolutionStatus.OK, tuple(hits))


# --- Scanning -------------------------------------------------------------

@dataclass(frozen=True)
class WikilinkHit:
    """A single ``[[…]]`` occurrence in a file, with location."""

    lineno: int
    target: str


def scan(text: str) -> Iterator[WikilinkHit]:
    """Yield every wikilink in *text*, skipping fenced and inline code.

    Lines starting with triple backticks or tildes toggle a fence flag;
    inline ``` `code` ``` regions on a line are masked out before
    wikilink matching, so a literal ``[[example]]`` inside backticks
    is not reported as a link.
    """
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        scan_line = _INLINE_CODE_RE.sub(
            lambda m: " " * len(m.group(0)),
            line,
        )
        for m in WIKILINK_RE.finditer(scan_line):
            yield WikilinkHit(lineno=lineno, target=m.group(1).strip())
