"""Tests for AGENTS002 — log.md is append-only.

The check fires on staged deletions inside any `log.md`, with two
narrow exemptions baked into the rule: the `---` frontmatter delimiter
(structural, not history) and a paired `updated: YYYY-MM-DD` bump
(allowed in lockstep with each new entry).

These tests are hermetic: each builds a tmp repo, commits an initial
`log.md`, then stages an edit and asks the rule to evaluate.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from wikilint.checks.log_append_only import LogAppendOnly
from wikilint.git_io import StagedEntry, staged_entries
from wikilint.report import Report

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


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


def _seed_log(repo: Path) -> str:
    body = (
        "---\n"
        "type: log\n"
        "scope: global\n"
        "updated: 2026-05-01\n"
        "---\n"
        "\n"
        "# Log\n"
        "\n"
        "## [2026-05-01] ingest | first\n"
        "- Source: [[a]]\n"
        "- One-line synthesis.\n"
    )
    _write(repo, "log.md", body)
    _stage(repo, "log.md")
    _commit(repo, "initial: log")
    return body


def _run(repo: Path) -> Report:
    report = Report()
    LogAppendOnly().apply(repo, staged_entries(repo), report)
    return report


class TestPureAppend:
    """The good case: prepend a new entry under the preamble; bump
    `updated:` in lockstep. Should produce zero diagnostics."""

    def test_clean_prepend_with_paired_updated_bump(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path)
        _seed_log(repo)
        new = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-21\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-21] ingest | second\n"
            "- Source: [[b]]\n"
            "- One-line synthesis.\n"
            "\n"
            "## [2026-05-01] ingest | first\n"
            "- Source: [[a]]\n"
            "- One-line synthesis.\n"
        )
        _write(repo, "log.md", new)
        _stage(repo, "log.md")
        assert _ids(_run(repo)) == []


class TestRejectedEdits:
    def test_delete_past_entry_is_error(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _seed_log(repo)
        # Removes the entire `## [2026-05-01]` entry.
        broken = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-01\n"
            "---\n"
            "\n"
            "# Log\n"
        )
        _write(repo, "log.md", broken)
        _stage(repo, "log.md")
        diags = _run(repo).diagnostics
        assert any(d.rule_id == "AGENTS002" for d in diags)

    def test_rewrite_past_entry_is_error(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _seed_log(repo)
        # Mutates a past entry's body — the canonical "rewrite history".
        broken = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-01\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-01] ingest | first (edited)\n"
            "- Source: [[a]]\n"
            "- One-line synthesis.\n"
        )
        _write(repo, "log.md", broken)
        _stage(repo, "log.md")
        assert "AGENTS002" in _ids(_run(repo))

    def test_unbalanced_updated_bump_is_error(self, tmp_path: Path) -> None:
        """Adding a second `updated:` line without removing the prior
        one breaks the paired-bump invariant."""
        repo = _init_repo(tmp_path)
        _seed_log(repo)
        broken = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-01\n"
            "updated: 2026-05-21\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-01] ingest | first\n"
            "- Source: [[a]]\n"
            "- One-line synthesis.\n"
        )
        _write(repo, "log.md", broken)
        _stage(repo, "log.md")
        assert "AGENTS002" in _ids(_run(repo))


class TestBypass:
    def test_reorder_bypass_with_audit_entry_is_clean(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path)
        # Seed two out-of-order entries (forward-chrono drift).
        body = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-21\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-01] ingest | first\n"
            "- One-line synthesis.\n"
            "\n"
            "## [2026-05-21] ingest | second\n"
            "- One-line synthesis.\n"
        )
        _write(repo, "log.md", body)
        _stage(repo, "log.md")
        _commit(repo, "initial: out-of-order log")

        # Reorder to newest-first AND add a maintenance entry on top.
        reordered = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-22\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-22] maintenance | reorder pass\n"
            "- Repaired chronological drift.\n"
            "\n"
            "## [2026-05-21] ingest | second\n"
            "- One-line synthesis.\n"
            "\n"
            "## [2026-05-01] ingest | first\n"
            "- One-line synthesis.\n"
        )
        _write(repo, "log.md", reordered)
        _stage(repo, "log.md")

        monkeypatch.setenv("WIKI_ALLOW_LOG_REORDER", "1")
        assert _ids(_run(repo)) == []

    def test_reorder_bypass_without_audit_entry_is_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Even with the bypass, a reorder must add a `maintenance`
        heading for audit. Skipping it should be rejected."""
        repo = _init_repo(tmp_path)
        body = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-21\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-01] ingest | first\n"
            "- a\n"
            "\n"
            "## [2026-05-21] ingest | second\n"
            "- b\n"
        )
        _write(repo, "log.md", body)
        _stage(repo, "log.md")
        _commit(repo, "initial: out-of-order log")

        reordered = (
            "---\n"
            "type: log\n"
            "scope: global\n"
            "updated: 2026-05-21\n"
            "---\n"
            "\n"
            "# Log\n"
            "\n"
            "## [2026-05-21] ingest | second\n"
            "- b\n"
            "\n"
            "## [2026-05-01] ingest | first\n"
            "- a\n"
        )
        _write(repo, "log.md", reordered)
        _stage(repo, "log.md")

        monkeypatch.setenv("WIKI_ALLOW_LOG_REORDER", "1")
        # The bypass accepted the permutation but the audit entry is
        # missing → still an AGENTS002 error.
        assert "AGENTS002" in _ids(_run(repo))


class TestNonLogPathsIgnored:
    def test_modifying_wiki_page_is_clean(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _write(repo, "domains/psy/wiki/p.md", "first\n")
        _stage(repo, "domains/psy/wiki/p.md")
        _commit(repo, "initial: page")

        _write(repo, "domains/psy/wiki/p.md", "edited\n")
        _stage(repo, "domains/psy/wiki/p.md")
        # AGENTS002 only fires on log.md edits.
        report = Report()
        LogAppendOnly().apply(
            repo,
            [StagedEntry("M", "domains/psy/wiki/p.md")],
            report,
        )
        assert _ids(report) == []
