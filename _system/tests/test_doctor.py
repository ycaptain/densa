"""Tests for ``densa doctor`` (``densa.commands.doctor``).

The command is a checklist over a vault's *setup* (hook wiring, Python
version, importability, active domain). We build throwaway vaults on
disk — healthy, missing-hook, malformed-domain — and assert on the
individual :class:`CheckResult` rows plus the overall exit code.

We avoid the real vault under ``share/`` so the tests are hermetic.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

from densa.commands import doctor as doctor_cmd


def _make_vault(root: Path, *, with_hook: bool = True) -> Path:
    """Build a minimal vault that ``_is_wiki_root`` accepts.

    A real vault root has both ``AGENTS.md`` and an in-repo
    ``_system/densa/`` package directory. We stub the package dir (its
    contents don't matter to ``doctor``'s repo discovery) and, when
    ``with_hook``, drop a ``.git/hooks/pre-commit`` so the hook check
    passes without needing a configured ``core.hooksPath``.
    """
    (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (root / "_system" / "densa").mkdir(parents=True)
    if with_hook:
        hooks = root / ".git" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    return root


def _results(repo: Path | None) -> dict[str, doctor_cmd.CheckResult]:
    return {c.label: c for c in doctor_cmd._run_checks(repo)}


# --- repo discovery ---------------------------------------------------------


def test_find_repo_none_outside_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Outside any vault, ``_find_repo`` returns None — "you're not in a
    vault" is a diagnosis, not something to paper over with a fallback."""
    monkeypatch.chdir(tmp_path)
    assert doctor_cmd._find_repo() is None


def test_find_repo_walks_up_to_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``_find_repo`` finds the vault root from a nested cwd."""
    _make_vault(tmp_path)
    nested = tmp_path / "domains" / "x" / "wiki"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert doctor_cmd._find_repo() == tmp_path.resolve()


def test_repo_not_found_is_a_failed_check() -> None:
    """A None repo yields a single ✗ 'vault root' row with a fix."""
    results = _results(None)
    assert results["vault root"].ok is False
    assert "densa init" in results["vault root"].fix


# --- healthy vault ----------------------------------------------------------


def test_healthy_vault_all_pass(tmp_path: Path) -> None:
    """A well-formed vault with a wired hook passes every check."""
    repo = _make_vault(tmp_path)
    results = _results(repo)
    assert all(c.ok for c in results.values()), {
        k: v.detail for k, v in results.items() if not v.ok
    }
    assert results["pre-commit hook"].ok is True


def test_run_returns_zero_on_healthy_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _make_vault(tmp_path)
    monkeypatch.chdir(repo)
    rc = doctor_cmd.run(argparse.Namespace(format="text"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "all checks passed" in out


# --- missing hook -----------------------------------------------------------


def test_missing_hook_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No hook and no configured ``core.hooksPath`` → ✗ with the exact
    ``git config`` fix command."""
    repo = _make_vault(tmp_path, with_hook=False)
    # Force the git-config probe to report "unset" regardless of the
    # ambient environment.
    monkeypatch.setattr(doctor_cmd, "_git_config", lambda r, k: None)
    results = _results(repo)
    hook = results["pre-commit hook"]
    assert hook.ok is False
    assert hook.fix == "git config core.hooksPath _system/hooks"


def test_run_returns_one_when_a_check_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _make_vault(tmp_path, with_hook=False)
    monkeypatch.setattr(doctor_cmd, "_git_config", lambda r, k: None)
    monkeypatch.chdir(repo)
    rc = doctor_cmd.run(argparse.Namespace(format="text"))
    assert rc == 1
    out = capsys.readouterr().out
    assert "failed" in out


def test_configured_hooks_path_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``core.hooksPath = _system/hooks`` with the hook present passes,
    even without a ``.git/hooks/pre-commit``."""
    repo = _make_vault(tmp_path, with_hook=False)
    managed = repo / "_system" / "hooks"
    managed.mkdir(parents=True)
    (managed / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(
        doctor_cmd, "_git_config", lambda r, k: "_system/hooks",
    )
    assert _results(repo)["pre-commit hook"].ok is True


# --- active domain ----------------------------------------------------------


def test_domain_without_frontmatter_is_ok(tmp_path: Path) -> None:
    """An L2 ``AGENTS.md`` that is prose-only (no frontmatter) is valid —
    most L2 overrides are. It must not be flagged as broken."""
    repo = _make_vault(tmp_path)
    agents = repo / "domains" / "research" / "AGENTS.md"
    agents.parent.mkdir(parents=True)
    agents.write_text("# AGENTS — research (L2)\nprose only\n", encoding="utf-8")
    assert _results(repo)["active domain"].ok is True


def test_empty_vault_domain_check_passes(tmp_path: Path) -> None:
    """No ``domains/`` directory yet → the active-domain check passes
    (an empty vault is a valid starting state)."""
    repo = _make_vault(tmp_path)
    assert _results(repo)["active domain"].ok is True


def test_unreadable_domain_agents_is_flagged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An L2 ``AGENTS.md`` that raises on parse is reported broken."""
    repo = _make_vault(tmp_path)
    agents = repo / "domains" / "broken" / "AGENTS.md"
    agents.parent.mkdir(parents=True)
    agents.write_text("---\nbad\n", encoding="utf-8")

    def _raise(_text: str) -> dict[str, object] | None:
        raise ValueError("malformed frontmatter")

    monkeypatch.setattr("densa.frontmatter.parse", _raise)
    result = _results(repo)["active domain"]
    assert result.ok is False
    assert "broken" in result.detail


# --- python version ---------------------------------------------------------


def test_python_version_check_reads_current() -> None:
    """The python-version check passes on any interpreter that can run
    the test suite (≥ 3.10 per pyproject)."""
    result = doctor_cmd._check_python_version()
    assert result.ok is True
    assert "need ≥" in result.detail


# --- json output ------------------------------------------------------------


def test_json_format_is_machine_readable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _make_vault(tmp_path)
    monkeypatch.chdir(repo)
    rc = doctor_cmd.run(argparse.Namespace(format="json"))
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert {"label", "ok", "detail", "fix"} <= set(payload["checks"][0])


# --- internal robustness ----------------------------------------------------


def test_guard_converts_exception_to_failed_check() -> None:
    """A probe that raises degrades to a ✗ row, never a crash."""
    def boom() -> doctor_cmd.CheckResult:
        raise RuntimeError("kaboom")

    result = doctor_cmd._guard(boom)
    assert result.ok is False
    assert "kaboom" in result.detail


def test_git_config_handles_missing_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If ``git`` isn't on PATH, ``_git_config`` returns None, not a
    traceback."""
    def _no_git(*_a: object, **_k: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", _no_git)
    assert doctor_cmd._git_config(tmp_path, "core.hooksPath") is None
