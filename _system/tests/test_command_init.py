"""Tests for ``densa init`` (``densa.commands.init``).

We exercise the pure helpers directly. The end-to-end ``run()`` path
shells out to git and would either hit the network (real clone) or
need a fake-git PATH shim — both are out of scope for the unit tests.
We assert on the small, stable invariants instead.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from densa.commands import init as init_cmd

# --- _resolve_destination ---------------------------------------------------


def test_resolve_destination_yes_without_arg_errors(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--yes`` with no positional destination must be a clean error,
    not a silent ``./my-vault`` default — non-interactive mode shouldn't
    invent paths.
    """
    result = init_cmd._resolve_destination(None, yes=True)
    assert result is None
    err = capsys.readouterr().err
    assert "--yes requires an explicit destination" in err


def test_resolve_destination_explicit_empty_dir(tmp_path: Path) -> None:
    """An explicit empty directory resolves cleanly."""
    target = tmp_path / "vault"
    target.mkdir()
    result = init_cmd._resolve_destination(str(target), yes=True)
    assert result == target.resolve()


def test_resolve_destination_explicit_nonexistent(tmp_path: Path) -> None:
    """A non-existent path resolves cleanly — clone will create it."""
    target = tmp_path / "new-vault"
    result = init_cmd._resolve_destination(str(target), yes=True)
    assert result == target.resolve()


def test_resolve_destination_non_empty_dir_errors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A non-empty directory is rejected — clone would either fail or
    silently merge into an unrelated repo.
    """
    (tmp_path / "preexisting.txt").write_text("hi")
    result = init_cmd._resolve_destination(str(tmp_path), yes=True)
    assert result is None
    err = capsys.readouterr().err
    assert "not empty" in err


def test_resolve_destination_dot_alias(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``.`` resolves to cwd."""
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(empty)
    result = init_cmd._resolve_destination(".", yes=True)
    assert result == empty.resolve()


# --- _format_path -----------------------------------------------------------


def test_format_path_home_relative(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Paths under ``~`` render as ``~/...`` for readability."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))  # type: ignore[arg-type]
    nested = tmp_path / "vault"
    assert init_cmd._format_path(nested) == "~/vault"


def test_format_path_falls_back_to_absolute(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A path neither under ``~`` nor under cwd falls back to absolute."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))  # type: ignore[arg-type]
    monkeypatch.chdir(tmp_path)
    other_root = Path("/var/tmp/totally-elsewhere-densa-test")
    assert init_cmd._format_path(other_root) == str(other_root)


# --- add_parser smoke test --------------------------------------------------


def test_add_parser_registers_init_subcommand() -> None:
    """``add_parser`` wires the subcommand cleanly; the parser must
    accept ``init <destination>`` without raising."""
    parent = argparse.ArgumentParser()
    sub = parent.add_subparsers(dest="command")
    init_cmd.add_parser(sub)

    args = parent.parse_args(["init", "my-vault", "--yes"])
    assert args.command == "init"
    assert args.destination == "my-vault"
    assert args.yes is True
    assert args.auto_inject == "none"


def test_add_parser_auto_inject_choices() -> None:
    """The ``--auto-inject`` choice list must include every supported
    agent + ``auto`` + ``none``."""
    parent = argparse.ArgumentParser()
    sub = parent.add_subparsers(dest="command")
    init_cmd.add_parser(sub)

    for value in ("cursor", "claude-code", "codex", "auto", "none"):
        args = parent.parse_args(["init", ".", "--yes", f"--auto-inject={value}"])
        assert args.auto_inject == value

    with pytest.raises(SystemExit):
        parent.parse_args(["init", ".", "--yes", "--auto-inject=invalid"])


# --- run() with missing git --------------------------------------------------


def test_run_errors_when_git_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """If ``git`` isn't on PATH, ``densa init`` must report a clean
    error (exit code 2) rather than crash.
    """
    monkeypatch.setattr(init_cmd, "_git_available", lambda: False)
    args = argparse.Namespace(
        destination=".", upstream="x", yes=True,
        auto_inject="none", examples="keep-all",
    )
    assert init_cmd.run(args) == 2
    err = capsys.readouterr().err
    assert "git is not on PATH" in err
