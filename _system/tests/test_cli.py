"""CLI surface tests.

Cover the argparse plumbing in :mod:`densa.cli` — specifically that
every advertised subcommand is registered and dispatches without
raising. The actual linting behaviour is covered by ``test_runner``;
this file only protects against the regression where a subcommand is
named in the docstring but never `sub.add_parser`-ed.
"""

from __future__ import annotations

import io
import shutil
import subprocess
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from densa import cli


def _run(argv: list[str]) -> int:
    """Invoke ``cli.main`` with ``argv`` and return its exit code,
    swallowing stdout."""
    with redirect_stdout(io.StringIO()):
        return cli.main(argv)


class TestSubcommandRegistration:
    """Both `densa <flag>` and `densa lint <flag>` MUST work.

    The legacy form (bare `--staged` / `--all`) keeps `attic/scripts/
    validate.py` and the pre-commit hook unbroken; the explicit
    `lint` subcommand is the canonical form going forward and is
    advertised in the CLI docstring.
    """

    def test_version_subcommand(self) -> None:
        assert _run(["version"]) == 0

    def test_rules_subcommand_text(self) -> None:
        assert _run(["rules"]) == 0

    def test_rules_subcommand_json(self) -> None:
        assert _run(["rules", "--format", "json"]) == 0

    def test_lint_subcommand_help_does_not_crash(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """`densa lint --help` must exit 0 (argparse SystemExit(0))."""
        with pytest.raises(SystemExit) as exc:
            cli.main(["lint", "--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "--staged" in out
        assert "--all" in out

    def test_bare_lint_without_args_fails_cleanly(self) -> None:
        """No flags + no paths → exit 2, not a traceback."""
        assert _run(["lint"]) == 2

    def test_top_level_lint_without_args_fails_cleanly(self) -> None:
        """Legacy form: bare `densa` with no flags → exit 2."""
        assert _run([]) == 2


class TestLintAgainstRealRepo:
    """End-to-end smoke: `lint --all` runs over a minimal repo."""

    def test_lint_all_clean_repo(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (tmp_path / "AGENTS.md").write_text(
            "---\ntype: schema\nscope: L1\n---\n", encoding="utf-8",
        )
        # _is_wiki_root double-factor marker.
        (tmp_path / "_system" / "densa").mkdir(parents=True)
        (tmp_path / "_system" / "densa" / "__init__.py").write_text(
            "", encoding="utf-8",
        )
        (tmp_path / "log.md").write_text(
            "---\ntype: log\nscope: global\nupdated: 2026-05-21\n"
            "---\n# Log\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        # Both forms — bare and `lint` subcommand — should behave the same.
        assert _run(["--all"]) == 0
        assert _run(["lint", "--all"]) == 0


@pytest.mark.skipif(
    shutil.which("git") is None, reason="git CLI not on PATH",
)
class TestDiffMode:
    """`--diff <base>` exercises the staged rules over a git range.

    Regression for: prior to the `lint_diff` entry point, CI had no
    way to enforce AGENTS001/002/007 — they only ran on the local
    pre-commit hook, which can be bypassed with `--no-verify`.
    """

    @staticmethod
    def _git(repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            capture_output=True,
        )

    def _init_repo_with_baseline(self, repo: Path) -> None:
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.email", "test@example.com")
        self._git(repo, "config", "user.name", "Test")
        (repo / "AGENTS.md").write_text(
            "---\ntype: schema\nscope: L1\n---\n", encoding="utf-8",
        )
        # _is_wiki_root double-factor check: needs both AGENTS.md and
        # the in-repo _system/densa/ marker directory.
        (repo / "_system" / "densa").mkdir(parents=True)
        (repo / "_system" / "densa" / "__init__.py").write_text(
            "", encoding="utf-8",
        )
        (repo / "domains/x/raw/sessions").mkdir(parents=True)
        (repo / "domains/x/raw/sessions/baseline.md").write_text(
            "# baseline raw\n", encoding="utf-8",
        )
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "ingest(x): baseline")

    def test_diff_mode_catches_raw_modification(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A commit that modifies a raw/ file (AGENTS001 violation)
        must be flagged when `--diff` runs over the range."""
        self._init_repo_with_baseline(tmp_path)
        # Make a violating commit: edit the existing raw file.
        (tmp_path / "domains/x/raw/sessions/baseline.md").write_text(
            "# baseline raw EDITED\n", encoding="utf-8",
        )
        self._git(tmp_path, "add", "-A")
        self._git(tmp_path, "commit", "-q", "-m", "bad: edit raw")
        monkeypatch.chdir(tmp_path)
        # Exit code 1 = there were errors (AGENTS001 fires).
        assert _run(["--diff", "HEAD^"]) == 1

    def test_diff_mode_passes_for_clean_range(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A commit that only adds a new wiki page (no raw edits, no
        log changes) passes a `--diff HEAD^` check."""
        self._init_repo_with_baseline(tmp_path)
        (tmp_path / "domains/x/wiki/concepts").mkdir(parents=True)
        (tmp_path / "domains/x/wiki/concepts/foo.md").write_text(
            "---\n"
            "type: concept\n"
            "domain: x\n"
            "created: 2026-05-21\n"
            "updated: 2026-05-21\n"
            "sources: []\n"
            "aliases: []\n"
            "tags: []\n"
            "status: active\n"
            "compiled_against: 1\n"
            "---\n# Foo\n",
            encoding="utf-8",
        )
        self._git(tmp_path, "add", "-A")
        self._git(tmp_path, "commit", "-q", "-m", "ingest(x): add foo")
        monkeypatch.chdir(tmp_path)
        assert _run(["--diff", "HEAD^"]) == 0
