"""The commit-msg hook and git's real hook ordering (TK-0038).

Git hook timing during ``git commit -m``:

1. **pre-commit** runs first. ``.git/COMMIT_EDITMSG`` still holds the
   PREVIOUS commit's message — git rewrites it only after this hook
   passes. The in-flight message is fundamentally unavailable, so the
   shipped ``_system/hooks/pre-commit`` skips AGENTS007
   (``--ignore AGENTS007``).
2. **commit-msg** runs next and receives the real message file as
   ``$1``. The shipped ``_system/hooks/commit-msg`` exports it via
   ``DENSA_COMMIT_MSG_FILE`` and re-runs only AGENTS007
   (``--staged --select AGENTS007``).

Two test groups:

- Static checks of the commit-msg script (mirrors
  ``test_hook_script.py`` for pre-commit).
- End-to-end regression: a throwaway vault repo with
  ``core.hooksPath`` pointed at the *shipped* hooks, driven by real
  ``git commit`` so git itself sequences the hooks. The stale
  ``COMMIT_EDITMSG`` is primed explicitly so the one-commit-behind
  trap is deterministic regardless of git version.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

_SYSTEM = Path(__file__).resolve().parents[1]
_HOOKS = _SYSTEM / "hooks"
_HOOK = _HOOKS / "commit-msg"


class TestCommitMsgHookScript:
    """Static checks — same posture as the pre-commit hook tests."""

    def test_hook_exists(self) -> None:
        assert _HOOK.is_file()

    def test_hook_is_executable(self) -> None:
        mode = _HOOK.stat().st_mode
        assert mode & stat.S_IXUSR, (
            "_system/hooks/commit-msg is not executable; "
            "run `chmod +x _system/hooks/commit-msg`"
        )

    def test_hook_uses_bash_shebang(self) -> None:
        first = _HOOK.read_text(encoding="utf-8").splitlines()[0]
        assert first == "#!/usr/bin/env bash"

    def test_hook_has_pipefail_safety(self) -> None:
        assert "set -euo pipefail" in _HOOK.read_text(encoding="utf-8")

    def test_hook_exports_message_file_from_dollar_one(self) -> None:
        """The whole point of the commit-msg stage: $1 is the real
        message file; the hook must hand it to the validator."""
        body = _HOOK.read_text(encoding="utf-8")
        assert 'MSG_FILE="$1"' in body
        assert 'export DENSA_COMMIT_MSG_FILE="$MSG_FILE"' in body

    def test_hook_runs_only_agents007(self) -> None:
        body = _HOOK.read_text(encoding="utf-8")
        assert "python3 -m densa --staged --select AGENTS007" in body
        assert "python -m densa --staged --select AGENTS007" in body

    def test_hook_exports_pythonpath(self) -> None:
        body = _HOOK.read_text(encoding="utf-8")
        assert "PYTHONPATH=" in body and "_system" in body

    def test_hook_resolves_repo_via_git(self) -> None:
        assert "git rev-parse --show-toplevel" in _HOOK.read_text(
            encoding="utf-8",
        )

    def test_hook_gracefully_handles_missing_python(self) -> None:
        body = _HOOK.read_text(encoding="utf-8")
        assert "command -v python3" in body
        assert "exit 1" in body
        assert "no-verify" in body or "core.hooksPath" in body

    def test_pre_commit_sibling_skips_agents007(self) -> None:
        """The two hooks are one mechanism: pre-commit MUST skip the
        rule it cannot classify, commit-msg MUST re-run it."""
        body = (_HOOKS / "pre-commit").read_text(encoding="utf-8")
        assert "--ignore AGENTS007" in body


@pytest.mark.skipif(
    shutil.which("git") is None, reason="git CLI not on PATH",
)
class TestGitHookOrdering:
    """Regression for the one-commit-behind misclassification.

    Real ``git commit`` drives the shipped hooks in git's actual
    order. Acceptance criteria covered:

    1. a correctly prefixed operation commit passes on FIRST attempt
       regardless of the previous commit's prefix;
    2. misprefixed commits are still rejected — at the commit-msg
       stage, classified by the REAL subject;
    3. the simulation reproduces git's hook ordering (stale
       COMMIT_EDITMSG at pre-commit time, ``$1`` at commit-msg time).
    """

    @staticmethod
    def _git(repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True,
        )

    def _init_vault_repo(self, tmp_path: Path) -> Path:
        """Throwaway vault wired to the SHIPPED hooks.

        The repo carries the `_is_wiki_root` double-factor markers
        (AGENTS.md + an empty `_system/densa/` directory — deliberately
        **without** `__init__.py`, so the hook's PYTHONPATH prepend
        leaves it a mere namespace portion and the real densa package
        still wins the import).
        """
        repo = tmp_path / "vault"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.email", "test@example.com")
        self._git(repo, "config", "user.name", "Test")
        (repo / "AGENTS.md").write_text(
            "---\ntype: schema\nscope: L1\n---\n# AGENTS\n",
            encoding="utf-8",
        )
        (repo / "_system" / "densa").mkdir(parents=True)
        (repo / "README.md").write_text("# vault\n", encoding="utf-8")
        # Baseline commit lands BEFORE the hooks are wired — an
        # unprefixed maintenance subject, the trap case for AGENTS007.
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "chore: scaffold vault")
        self._git(repo, "config", "core.hooksPath", str(_HOOKS))
        return repo

    @staticmethod
    def _prime_stale_editmsg(repo: Path, previous_subject: str) -> None:
        """Pin the state pre-commit really sees mid-commit: a
        COMMIT_EDITMSG still holding the previous commit's message."""
        (repo / ".git" / "COMMIT_EDITMSG").write_text(
            previous_subject + "\n", encoding="utf-8",
        )

    @staticmethod
    def _commit(
        repo: Path, message: str,
    ) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env.pop("DENSA_COMMIT_MSG_FILE", None)
        env.pop("WIKI_ALLOW_CROSS_SCOPE", None)
        env["PYTHONPATH"] = str(_SYSTEM)
        return subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo,
            env=env,
            check=False,  # rejection is the behaviour under test
            capture_output=True,
            text=True,
        )

    @staticmethod
    def _head_subject(repo: Path) -> str:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%s"], cwd=repo, text=True,
        ).strip()

    def _stage_domain_file(self, repo: Path, name: str) -> None:
        # A non-markdown payload keeps the file-level frontmatter rules
        # out of the picture — this test isolates AGENTS007 staging.
        page = repo / "domains" / "psy" / "wiki" / "concepts" / name
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("payload\n", encoding="utf-8")
        self._git(repo, "add", str(page))

    def test_prefixed_commit_passes_first_attempt(
        self, tmp_path: Path,
    ) -> None:
        """AC1: previous commit unprefixed, in-flight commit correctly
        prefixed — must pass on the first attempt. Under the old
        COMMIT_EDITMSG read, pre-commit classified this as
        `(no prefix)` and rejected it."""
        repo = self._init_vault_repo(tmp_path)
        self._prime_stale_editmsg(repo, "chore: scaffold vault")
        self._stage_domain_file(repo, "x.txt")
        result = self._commit(repo, "ingest(psy): add page")
        assert result.returncode == 0, (
            f"first-attempt commit rejected:\n{result.stdout}{result.stderr}"
        )
        assert self._head_subject(repo) == "ingest(psy): add page"

    def test_misprefixed_commit_rejected_with_real_subject(
        self, tmp_path: Path,
    ) -> None:
        """AC2: the stale COMMIT_EDITMSG carries a prefix that WOULD
        allow the staged path; the real subject does not. The commit
        must be rejected (at commit-msg time) and classified
        `(no prefix)` — proof the real subject was read, not the
        stale file at either stage."""
        repo = self._init_vault_repo(tmp_path)
        self._prime_stale_editmsg(repo, "ingest(psy): previous commit")
        self._stage_domain_file(repo, "y.txt")
        result = self._commit(repo, "fix: stray edit")
        output = result.stdout + result.stderr
        assert result.returncode != 0
        assert "AGENTS007" in output
        assert "(no prefix)" in output
        assert self._head_subject(repo) == "chore: scaffold vault"
        # Same staged set, correct prefix → goes through: the
        # rejection above was message-shaped, not path-shaped.
        retry = self._commit(repo, "ingest(psy): take two")
        assert retry.returncode == 0, (
            f"retry rejected:\n{retry.stdout}{retry.stderr}"
        )

    def test_unprefixed_maintenance_commit_passes(
        self, tmp_path: Path,
    ) -> None:
        """Sanity: maintenance commits outside domains/** stay green
        through both hook stages."""
        repo = self._init_vault_repo(tmp_path)
        self._prime_stale_editmsg(repo, "ingest(psy): previous commit")
        (repo / "docs").mkdir()
        (repo / "docs" / "note.md").write_text(
            "# note\n", encoding="utf-8",
        )
        self._git(repo, "add", "docs/note.md")
        result = self._commit(repo, "docs: add note")
        assert result.returncode == 0, (
            f"maintenance commit rejected:\n{result.stdout}{result.stderr}"
        )
