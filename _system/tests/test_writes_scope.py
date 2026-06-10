"""Tests for AGENTS007 — operation writes within scope.

The rule classifies each commit by its leading commit-message prefix
(``ingest(<domain>):``, ``query:``, ``lint:``, ``process-inbox:``,
``promote:``) and asserts every staged path matches the allow-list
for that operation. Commits without a recognised prefix fall back to
the schema/docs/integrations maintenance allow-list.

The subject is sourced from ``DENSA_COMMIT_MSG_FILE`` (set by the
``commit-msg`` hook, which receives the real message file as ``$1``);
``.git/COMMIT_EDITMSG`` is never trusted because at pre-commit time it
still holds the *previous* commit's message (TK-0038). The fixture
helper therefore wires subjects through the env var, mirroring the
hook.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from densa.checks.operation_writes_scope import (
    COMMIT_MSG_FILE_ENV,
    OperationWritesScope,
    _commit_subject,
    _glob_match,
)
from densa.git_io import StagedEntry
from densa.report import Report


def _init_repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    subject: str = "",
) -> Path:
    """Throwaway git repo with *subject* wired the way the commit-msg
    hook does it: a message file handed over via DENSA_COMMIT_MSG_FILE.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.check_call(
        ["git", "init", "--quiet", "-b", "main", str(repo)],
    )
    monkeypatch.delenv(COMMIT_MSG_FILE_ENV, raising=False)
    if subject:
        msg_file = tmp_path / "commit-msg-file"
        msg_file.write_text(subject + "\n", encoding="utf-8")
        monkeypatch.setenv(COMMIT_MSG_FILE_ENV, str(msg_file))
    return repo


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


def _entries(*paths: str) -> list[StagedEntry]:
    return [StagedEntry("A", p) for p in paths]


class TestIngestScope:
    def test_clean(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "ingest(psy): foo")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "ingest(psy): foo")
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
    def test_lint_writes_to_outputs_is_clean(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "lint: 2026-05-19")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "query: foo")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "query: foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("domains/psy/wiki/syntheses/2026-05-20-foo.md"),
            report,
        )
        assert _ids(report) == ["AGENTS007"]

    def test_query_writing_to_lint_outputs_is_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """`query` may write outputs/qa/ but never outputs/lint/."""
        repo = _init_repo(tmp_path, monkeypatch, "query: foo")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "promote: foo ← 2026-05-20-qa-foo")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "promote: foo ← 2026-05-20-qa-foo")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A real `git mv` reports as letter ``R``, destination path."""
        repo = _init_repo(tmp_path, monkeypatch, "promote: foo ← 2026-05-20-qa-foo")
        report = Report()
        OperationWritesScope().apply(
            repo,
            [StagedEntry("R", "domains/psy/wiki/syntheses/foo.md")],
            report,
        )
        assert _ids(report) == []

    def test_promote_appending_to_lint_report_is_clean(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """`promote` Stage 4 appends 'Issues to surface' to today's lint report."""
        repo = _init_repo(tmp_path, monkeypatch, "promote: foo ← 2026-05-20-qa-foo")
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
    def test_template_edit_is_clean(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "chore: tidy templates")
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
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "fix: stray edit")
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
        repo = _init_repo(tmp_path, monkeypatch, "fix: stray edit")
        monkeypatch.setenv("WIKI_ALLOW_CROSS_SCOPE", "1")
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("domains/psy/wiki/concepts/x.md"),
            report,
        )
        assert _ids(report) == []


class TestCommitSubjectSources:
    """`_commit_subject` source order (TK-0038).

    Git hook timing: COMMIT_EDITMSG is rewritten only *after* the
    pre-commit hook passes, so mid-commit it holds the previous
    commit's message. The function must therefore (1) trust the
    commit-msg hook's DENSA_COMMIT_MSG_FILE env var first, (2) never
    read COMMIT_EDITMSG, (3) fall back to the HEAD subject for
    post-commit re-runs (``densa --diff`` in CI, manual ``--staged``).
    """

    @staticmethod
    def _git(repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True,
        )

    def _commit_baseline(self, repo: Path, subject: str) -> None:
        self._git(repo, "config", "user.email", "test@example.com")
        self._git(repo, "config", "user.name", "Test")
        (repo / "README.md").write_text("# baseline\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", subject)

    def test_env_file_wins_over_everything(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch, "ingest(psy): real")
        self._commit_baseline(repo, "chore: previous commit")
        (repo / ".git" / "COMMIT_EDITMSG").write_text(
            "lint: stale leftover\n", encoding="utf-8",
        )
        assert _commit_subject(repo) == "ingest(psy): real"

    def test_relative_env_path_resolves_against_repo(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """git hands `$1` as `.git/COMMIT_EDITMSG` relative to the
        worktree; the belt-and-braces resolution must anchor at repo."""
        repo = _init_repo(tmp_path, monkeypatch)
        (repo / ".git" / "MSG").write_text(
            "promote: foo\n", encoding="utf-8",
        )
        monkeypatch.setenv(COMMIT_MSG_FILE_ENV, ".git/MSG")
        assert _commit_subject(repo) == "promote: foo"

    def test_stale_commit_editmsg_is_ignored(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Regression: a COMMIT_EDITMSG left over from the previous
        commit must not classify the in-flight one (env unset, no HEAD
        → empty subject → `(no prefix)` scope)."""
        repo = _init_repo(tmp_path, monkeypatch)
        (repo / ".git" / "COMMIT_EDITMSG").write_text(
            "ingest(psy): previous commit\n", encoding="utf-8",
        )
        assert _commit_subject(repo) == ""
        report = Report()
        OperationWritesScope().apply(
            repo,
            _entries("domains/psy/wiki/concepts/x.md"),
            report,
        )
        assert _ids(report) == ["AGENTS007"]

    def test_falls_back_to_head_subject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Post-commit re-runs (CI `--diff`, manual `--staged`) keep
        classifying by the HEAD subject when no message file is given."""
        repo = _init_repo(tmp_path, monkeypatch)
        self._commit_baseline(repo, "ingest(psy): landed")
        assert _commit_subject(repo) == "ingest(psy): landed"

    def test_unreadable_env_file_falls_back(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _init_repo(tmp_path, monkeypatch)
        self._commit_baseline(repo, "query: head subject")
        monkeypatch.setenv(
            COMMIT_MSG_FILE_ENV, str(tmp_path / "does-not-exist"),
        )
        assert _commit_subject(repo) == "query: head subject"


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
