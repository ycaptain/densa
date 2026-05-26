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
    For renames and copies, ``path`` is the *destination* path and
    ``src`` is the *source* path. For other letters ``src`` is ``None``.

    Keeping ``src`` matters for rules that must distinguish "rename
    into protected scope" (allowed, e.g. ``git mv inbox/x raw/y`` per
    AGENTS.md §"process-inbox") from "rename within protected scope" (forbidden).
    """

    letter: str
    path: str
    src: str | None = None


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

# Lines that appear above the first hunk header in a unified diff and
# carry diff metadata, not file content. Critically, the bare ``---``
# and ``+++`` file markers are matched STRICTLY (with a trailing space)
# so that a markdown frontmatter delimiter ``---`` showing up as
# ``----`` (one diff marker + three content chars) inside a hunk body
# is not mistaken for a header — that bug silently weakened AGENTS002
# (log-append-only) detection.
_DIFF_HEADER_PREFIXES = (
    "--- ",
    "+++ ",
    "diff ",
    "index ",
    "new file",
    "deleted file",
    "rename ",
    "similarity ",
    "Binary ",
)
_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def _is_diff_header(line: str) -> bool:
    """Return True if *line* is unified-diff metadata (not file content).

    Recognises ``--- a/...``, ``--- /dev/null``, ``+++ b/...``, hunk
    headers (``@@ ... @@``), and the pre-hunk preamble
    (``diff --git``, ``index``, ``new file mode``, etc.). Does NOT
    treat a bare ``---`` or ``----`` content line inside a hunk as a
    header — those are valid markdown frontmatter delimiters and must
    flow through as ordinary diff content.
    """
    return line.startswith(_DIFF_HEADER_PREFIXES) or line.startswith("@@ ")


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo,
        text=True,
        stderr=subprocess.DEVNULL,
    )


# --- Public API -----------------------------------------------------------

def _parse_name_status(raw: str) -> list[StagedEntry]:
    parts = raw.split("\x00")
    result: list[StagedEntry] = []
    i = 0
    while i < len(parts):
        status = parts[i]
        if not status:
            i += 1
            continue
        if status[0] in ("R", "C"):
            src = parts[i + 1] if i + 1 < len(parts) else ""
            dest = parts[i + 2] if i + 2 < len(parts) else ""
            result.append(StagedEntry(status[0], dest, src=src or None))
            i += 3
        else:
            path = parts[i + 1] if i + 1 < len(parts) else ""
            result.append(StagedEntry(status[0], path))
            i += 2
    return result


def staged_entries(repo: Path) -> list[StagedEntry]:
    """List every path with a staged change."""
    return _parse_name_status(
        _git(repo, "diff", "--cached", "--name-status", "-z"),
    )


def diff_entries(repo: Path, base_ref: str) -> list[StagedEntry]:
    """List every path that changed between *base_ref* and ``HEAD``.

    Used by ``densa --diff <ref>`` so CI / batch jobs can apply the
    staged rules (AGENTS001/002/007) over a push or PR range without a
    real git index — pre-commit alone cannot catch a ``--no-verify``
    bypass.
    """
    return _parse_name_status(
        _git(repo, "diff", "--name-status", "-z", f"{base_ref}..HEAD"),
    )


def staged_blob(repo: Path, path: str) -> str | None:
    """Return the blob content for *path* in the index, or ``None`` on
    error (path not in index, binary, etc.).
    """
    try:
        return _git(repo, "show", f":0:{path}")
    except subprocess.CalledProcessError:
        return None


def ref_blob(repo: Path, ref: str, path: str) -> str | None:
    """Return the blob content for *path* at *ref* (e.g. ``HEAD``), or
    ``None`` on error.
    """
    try:
        return _git(repo, "show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return None


def staged_diff(repo: Path, path: str) -> StagedDiff:
    """Return separated ``removed`` / ``added`` lines for *path*.

    Pre-hunk metadata (file markers, ``index`` lines, ``@@`` headers)
    is stripped; the rest is content. A bare ``---`` content line is
    preserved as the string ``"--"`` in ``removed`` (the leading ``-``
    is the diff marker; what follows is the actual line).
    """
    try:
        out = _git(repo, "diff", "--cached", "-U0", "--", path)
    except subprocess.CalledProcessError:
        return StagedDiff()
    removed: list[str] = []
    added: list[str] = []
    in_hunk = False
    for ln in out.split("\n"):
        if _HUNK_RE.match(ln):
            in_hunk = True
            continue
        # Header lines only appear before the first hunk; once we're
        # in a hunk, every `-` / `+` line is content.
        if not in_hunk and _is_diff_header(ln):
            continue
        if not in_hunk:
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
    in_hunk = False
    for ln in out.split("\n"):
        h = _HUNK_RE.match(ln)
        if h:
            cur = int(h.group(1))
            in_hunk = True
            continue
        if not in_hunk and _is_diff_header(ln):
            continue
        if not in_hunk:
            continue
        if ln.startswith("-"):
            result.append((cur, ln[1:]))
            cur += 1
        elif not ln.startswith("+"):
            cur += 1
    return result
