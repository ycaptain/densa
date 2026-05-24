"""Tests for git plumbing in :mod:`densa.git_io`.

The critical regression these tests guard against: ``staged_diff`` /
``staged_deletions`` previously matched ``"---"`` and ``"+++"`` as
diff-header prefixes via ``ln.startswith(_DIFF_HEADERS)``. In a real
unified diff, a deleted markdown frontmatter delimiter line ``---``
appears as ``----`` (one ``-`` marker + the three content chars),
which ``startswith("---")`` greedily matched — silently dropping it
and weakening AGENTS002 (log-append-only) detection whenever a user
edited the frontmatter block above the entry insertion point.

The fixed implementation:
- Requires a trailing space on the ``--- a/`` / ``+++ b/`` markers so
  bare ``---`` content lines flow through.
- Tracks whether the parser is inside a hunk; only pre-hunk text can
  be a header.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from densa.git_io import staged_deletions, staged_diff

_GIT = shutil.which("git")

pytestmark = pytest.mark.skipif(
    _GIT is None, reason="git binary not available",
)


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.check_call(
        ["git", "init", "--quiet", "-b", "main", str(repo)],
    )
    # A user.email / user.name is required for `git commit` in CI.
    for key, val in (("user.email", "t@t.t"), ("user.name", "t")):
        subprocess.check_call(
            ["git", "-C", str(repo), "config", key, val],
        )
    return repo


def _write(repo: Path, rel: str, body: str) -> None:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(body, encoding="utf-8")


def _stage(repo: Path, rel: str) -> None:
    subprocess.check_call(["git", "-C", str(repo), "add", rel])


def _commit(repo: Path, message: str) -> None:
    subprocess.check_call(
        ["git", "-C", str(repo), "commit", "--quiet", "-m", message],
    )


class TestStagedDiffFrontmatterDeletion:
    """A staged deletion of a `---` frontmatter delimiter MUST appear in
    `removed`, not be silently swallowed as a diff header."""

    def test_dashes_line_deletion_survives(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        original = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-21] ingest | first\n"
        )
        _write(repo, "log.md", original)
        _stage(repo, "log.md")
        _commit(repo, "initial: log")

        # Now delete the closing `---` delimiter line — exactly the
        # historical AGENTS002 failure case.
        broken = original.replace("---\n\n# Log", "\n# Log")
        _write(repo, "log.md", broken)
        _stage(repo, "log.md")

        diff = staged_diff(repo, "log.md")
        # In a unified diff, a deleted `---` content line is rendered
        # as `----` (one diff marker + three content chars); stripping
        # the marker yields `---` back. Pre-fix this line was eaten as
        # a `--- a/path` header — the regression we're guarding.
        assert "---" in diff.removed, (
            f"expected the deleted `---` line to survive header filtering; "
            f"got removed={diff.removed!r}"
        )

    def test_plus_plus_plus_content_line_addition_survives(
        self, tmp_path: Path,
    ) -> None:
        """Symmetric: adding a bare `+++` content line must not be
        eaten as a `+++ b/...` header."""
        repo = _init_repo(tmp_path)
        _write(repo, "note.md", "first line\n")
        _stage(repo, "note.md")
        _commit(repo, "initial: note")

        _write(repo, "note.md", "first line\n+++\nthird\n")
        _stage(repo, "note.md")

        diff = staged_diff(repo, "note.md")
        # `++++` → strip leading marker → `+++` content line, same shape
        # symmetry as the `---` case above.
        assert "+++" in diff.added, (
            f"expected the added `+++` line to appear in added; got "
            f"{diff.added!r}"
        )

    def test_normal_edit_unaffected(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _write(repo, "x.md", "a\nb\nc\n")
        _stage(repo, "x.md")
        _commit(repo, "initial")

        _write(repo, "x.md", "a\nB\nc\n")
        _stage(repo, "x.md")

        diff = staged_diff(repo, "x.md")
        assert "b" in diff.removed
        assert "B" in diff.added


class TestStagedDeletions:
    """`staged_deletions` carries (old_lineno, content) for every `-` line.
    Must respect the `---` frontmatter content-line invariant too."""

    def test_dashes_line_in_deletions(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        original = "---\nkey: val\n---\n# Body\n"
        _write(repo, "page.md", original)
        _stage(repo, "page.md")
        _commit(repo, "initial: page")

        # Replace the closing delimiter with a different content line.
        _write(repo, "page.md", "---\nkey: val\nNOT_A_DELIM\n# Body\n")
        _stage(repo, "page.md")

        deletions = staged_deletions(repo, "page.md")
        contents = [c for _ln, c in deletions]
        # `---` line deleted → diff marker stripped → `---` content
        # survives.
        assert "---" in contents
