"""git plumbing the validator depends on.

Wraps ``subprocess`` calls into typed helpers. Every function takes the
repo root as :class:`pathlib.Path`; nothing relies on the current
working directory.

A single :class:`StagedEntry` carries the ``--name-status`` letter and
the path. Diffs are returned as :class:`StagedDiff` (separate removed
and added line lists).

This module deliberately does **not** parse markdown or YAML — those
are upstairs concerns. Callers that want frontmatter or wikilinks from
a staged blob fetch the blob via :func:`staged_blob` and hand it to the
relevant module.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StagedEntry:
    """One entry from ``git diff --cached --name-status``.

    ``letter`` is the standard porcelain status character:
    ``A`` add, ``M`` modify, ``D`` delete, ``R`` rename, ``C`` copy.
    For renames and copies, ``path`` is the *destination* path.
    """

    letter: str
    path: str


@dataclass(frozen=True)
class StagedDiff:
    """Separated removed/added lines for one file's cached diff.

    Both lists preserve order; no de-duplication. Hunk headers,
    ``+++``/``---`` markers, ``new file``/``deleted file`` summaries,
    and binary markers are stripped.
    """

    removed: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)


# --- Process helpers ------------------------------------------------------

_DIFF_HEADERS = (
    "---",
    "+++",
    "diff ",
    "index ",
    "new file",
    "deleted file",
    "rename ",
    "similarity ",
    "Binary ",
    "@@ ",
)
_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo,
        text=True,
        stderr=subprocess.DEVNULL,
    )


# --- Public API -----------------------------------------------------------

def staged_entries(repo: Path) -> list[StagedEntry]:
    """List every path with a staged change."""
    parts = _git(repo, "diff", "--cached", "--name-status", "-z").split("\x00")
    result: list[StagedEntry] = []
    i = 0
    while i < len(parts):
        status = parts[i]
        if not status:
            i += 1
            continue
        if status[0] in ("R", "C"):
            dest = parts[i + 2] if i + 2 < len(parts) else ""
            result.append(StagedEntry(status[0], dest))
            i += 3
        else:
            path = parts[i + 1] if i + 1 < len(parts) else ""
            result.append(StagedEntry(status[0], path))
            i += 2
    return result


def staged_blob(repo: Path, path: str) -> str | None:
    """Return the blob content for *path* in the index, or ``None`` on
    error (path not in index, binary, etc.).
    """
    try:
        return _git(repo, "show", f":0:{path}")
    except subprocess.CalledProcessError:
        return None


def staged_diff(repo: Path, path: str) -> StagedDiff:
    """Return separated ``removed`` / ``added`` lines for *path*."""
    try:
        out = _git(repo, "diff", "--cached", "-U0", "--", path)
    except subprocess.CalledProcessError:
        return StagedDiff()
    removed: list[str] = []
    added: list[str] = []
    for ln in out.split("\n"):
        if ln.startswith(_DIFF_HEADERS):
            continue
        if ln.startswith("-"):
            removed.append(ln[1:])
        elif ln.startswith("+"):
            added.append(ln[1:])
    return StagedDiff(removed=removed, added=added)


def staged_deletions(repo: Path, path: str) -> list[tuple[int, str]]:
    """Return (old_lineno, content) for every ``-`` line in *path*'s diff."""
    try:
        out = _git(repo, "diff", "--cached", "-U0", "--", path)
    except subprocess.CalledProcessError:
        return []
    result: list[tuple[int, str]] = []
    cur = 0
    for ln in out.split("\n"):
        h = _HUNK_RE.match(ln)
        if h:
            cur = int(h.group(1))
            continue
        if ln.startswith(_DIFF_HEADERS):
            continue
        if ln.startswith("-"):
            result.append((cur, ln[1:]))
            cur += 1
        elif not ln.startswith("+"):
            cur += 1
    return result
