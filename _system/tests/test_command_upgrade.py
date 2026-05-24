"""Tests for ``densa upgrade`` (``densa.commands.upgrade``).

We exercise the pure helpers and the error paths. The merge flow
itself shells out to git and is integration-tested manually; here we
make sure the wrappers behave when run outside a vault, when
``upstream`` is missing, etc.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pytest

from densa.commands import upgrade as upgrade_cmd


def test_resolve_repo_finds_vault_root(tmp_path: Path) -> None:
    """``_resolve_repo`` walks up from cwd looking for AGENTS.md + the
    densa package directory."""
    (tmp_path / "AGENTS.md").write_text("---\ntype: schema\n---\n")
    (tmp_path / "_system" / "densa").mkdir(parents=True)
    nested = tmp_path / "domains" / "x" / "wiki"
    nested.mkdir(parents=True)

    cwd = os.getcwd()
    try:
        os.chdir(nested)
        assert upgrade_cmd._resolve_repo() == tmp_path.resolve()
    finally:
        os.chdir(cwd)


def test_resolve_repo_returns_none_outside_vault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Outside a vault, ``_resolve_repo`` returns None and ``run``
    surfaces a clean error."""
    monkeypatch.chdir(tmp_path)
    assert upgrade_cmd._resolve_repo() is None


def test_run_errors_when_outside_vault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    args = argparse.Namespace(ref="upstream/main", dry_run=False, yes=False)
    assert upgrade_cmd.run(args) == 2
    err = capsys.readouterr().err
    assert "not inside a Densa vault" in err


def test_run_errors_when_no_upstream_remote(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A vault without `upstream` remote configured must surface a
    next-step error, not crash."""
    (tmp_path / "AGENTS.md").write_text("---\ntype: schema\n---\n")
    (tmp_path / "_system" / "densa").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(upgrade_cmd, "_resolve_repo", lambda: tmp_path)
    monkeypatch.setattr(upgrade_cmd, "_has_remote", lambda *_a, **_kw: False)

    args = argparse.Namespace(ref="upstream/main", dry_run=False, yes=False)
    assert upgrade_cmd.run(args) == 2
    err = capsys.readouterr().err
    assert "no `upstream` remote" in err


def test_add_parser_registers_upgrade_subcommand() -> None:
    parent = argparse.ArgumentParser()
    sub = parent.add_subparsers(dest="command")
    upgrade_cmd.add_parser(sub)

    args = parent.parse_args(["upgrade", "--dry-run"])
    assert args.command == "upgrade"
    assert args.dry_run is True
    assert args.ref == "upstream/main"

    args = parent.parse_args(["upgrade", "--ref", "upstream/v2"])
    assert args.ref == "upstream/v2"
