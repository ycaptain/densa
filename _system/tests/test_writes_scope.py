"""Tests for AGENTS007 — operation writes within scope.

The rule classifies each commit by its leading commit-message prefix
(``ingest(<domain>):``, ``query:``, ``lint:``, ``process-inbox:``,
``promote:``) and asserts every staged path matches the allow-list
for that operation. Commits without a recognised prefix fall back to
the schema/docs/integrations maintenance allow-list.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from densa.checks.operation_writes_scope import (
    OperationWritesScope,
    _glob_match,
)
from densa.git_io import StagedEntry
from densa.report import Report


def _init_repo(tmp_path: Path, subject: str = "") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.check_call(
        ["git", "init", "--quiet", "-b", "main", str(repo)],
    )
    if subject:
        (repo / ".git" / "COMMIT_EDITMSG").write_text(
            subject + "\n", encoding="utf-8",
        )
    return repo


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


def _entries(*paths: str) -> list[StagedEntry]:
    return [StagedEntry("A", p) for p in paths]


class TestIngestScope:
    def test_clean(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path, "ingest(psy): foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries(
                "domains/psy/wiki/concepts/x.md",
                "domains/psy/log.md",
                "log.md",
            ),
            report,
        )
        assert _ids(report) == []

    def test_ingest_writing_to_system_is_error(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path, "ingest(psy): foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries(
                "domains/psy/wiki/concepts/x.md",
                "_system/scripts/foo.py",
            ),
            report,
        )
        assert _ids(report) == ["AGENTS007"]


class TestLintScope:
    def test_lint_writes_to_outputs_is_clean(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path, "lint: 2026-05-19")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries(
                "outputs/lint/2026-05-19.md",
                "outputs/snapshots/index-snapshot.md",
                "log.md",
            ),
            report,
        )
        assert _ids(report) == []


class TestQueryScope:
    """`query` files Q&A back to outputs/qa/ — not wiki/syntheses/ anymore."""

    def test_query_writes_to_outputs_qa_is_clean(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path, "query: foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries(
                "outputs/qa/2026-05-20-foo.md",
                "domains/psy/log.md",
                "log.md",
            ),
            report,
        )
        assert _ids(report) == []

    def test_query_writing_to_old_syntheses_path_is_error(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path, "query: foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("domains/psy/wiki/syntheses/2026-05-20-foo.md"),
            report,
        )
        assert _ids(report) == ["AGENTS007"]

    def test_query_writing_to_lint_outputs_is_error(
        self, tmp_path: Path,
    ) -> None:
        """`query` may write outputs/qa/ but never outputs/lint/."""
        repo = _init_repo(tmp_path, "query: foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("outputs/lint/2026-05-19.md"),
            report,
        )
        assert _ids(report) == ["AGENTS007"]


class TestPromoteScope:
    """`promote` performs git mv outputs/qa/ → domains/<X>/wiki/ in one commit."""

    def test_promote_mv_and_log_entries_is_clean(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path, "promote: foo ← 2026-05-20-qa-foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            [
                StagedEntry("D", "outputs/qa/2026-05-20-qa-foo.md"),
                StagedEntry("A", "domains/psy/wiki/syntheses/foo.md"),
                StagedEntry("M", "domains/psy/log.md"),
                StagedEntry("M", "log.md"),
            ],
            report,
        )
        assert _ids(report) == []

    def test_promote_writing_to_system_is_error(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path, "promote: foo ← 2026-05-20-qa-foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries(
                "domains/psy/wiki/concepts/x.md",
                "_system/scripts/foo.py",
            ),
            report,
        )
        assert _ids(report) == ["AGENTS007"]

    def test_promote_rename_directly_is_clean(
        self, tmp_path: Path,
    ) -> None:
        """A real `git mv` reports as letter ``R``, destination path."""
        repo = _init_repo(tmp_path, "promote: foo ← 2026-05-20-qa-foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            [StagedEntry("R", "domains/psy/wiki/syntheses/foo.md")],
            report,
        )
        assert _ids(report) == []

    def test_promote_appending_to_lint_report_is_clean(
        self, tmp_path: Path,
    ) -> None:
        """`promote` Stage 4 appends 'Issues to surface' to today's lint report."""
        repo = _init_repo(tmp_path, "promote: foo ← 2026-05-20-qa-foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            [
                StagedEntry("D", "outputs/qa/2026-05-20-qa-foo.md"),
                StagedEntry("A", "domains/psy/wiki/syntheses/foo.md"),
                StagedEntry("M", "outputs/lint/2026-05-20.md"),
                StagedEntry("M", "domains/psy/log.md"),
                StagedEntry("M", "log.md"),
            ],
            report,
        )
        assert _ids(report) == []


class TestNoPrefixScope:
    def test_template_edit_is_clean(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path, "chore: tidy templates")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries(
                "_system/templates/report.md",
                "AGENTS.md",
            ),
            report,
        )
        assert _ids(report) == []

    def test_no_prefix_writing_domains_is_error(
        self, tmp_path: Path,
    ) -> None:
        repo = _init_repo(tmp_path, "fix: stray edit")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("domains/psy/wiki/concepts/x.md"),
            report,
        )
        assert _ids(report) == ["AGENTS007"]


class TestBypass:
    def test_env_bypass_skips_rule(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, "fix: stray edit")
        monkeypatch.setenv("WIKI_ALLOW_CROSS_SCOPE", "1")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("domains/psy/wiki/concepts/x.md"),
            report,
        )
        assert _ids(report) == []


class TestGlobMatcher:
    """Spot-check the ``**``-aware matcher in the rule module."""

    @pytest.mark.parametrize("path,pattern,expected", [
        ("domains/x/wiki/concepts/a.md", "domains/*/wiki/**", True),
        ("domains/x/wiki/syntheses/a.md", "domains/*/wiki/syntheses/**", True),
        ("domains/x/raw/sessions/a.md", "domains/*/wiki/**", False),
        ("log.md", "log.md", True),
        ("domains/x/log.md", "domains/*/log.md", True),
        ("AGENTS.md", "AGENTS.md", True),
        ("docs/setup.md", "docs/**", True),
        ("outputs/lint/2026-01-01.md", "outputs/**", True),
        ("README.md", "*.md", True),
        # ``*`` should not span path separators
        ("a/b.md", "*.md", False),
    ])
    def test_glob_match(
        self, path: str, pattern: str, expected: bool,
    ) -> None:
        assert _glob_match(path, pattern) is expected
