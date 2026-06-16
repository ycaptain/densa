"""Merge-blocking guardrails for ``densa tui`` (spec §7).

The viewer is read-only and must stay cheap to import. Two invariants
protect that and one protects the CLI wiring:

1. **No writes.** The whole view read-path (lint + render + excerpt
   read) leaves the vault byte-for-byte identical.
2. **No curses on the lint path.** Importing the CLI and running a
   non-tui command must not transitively import ``curses`` — that is
   the lazy-import contract that keeps the pre-commit hook's import
   budget intact (mirrors the MCP server).
3. **The subcommand is registered** and accepts ``--diff``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from densa import cli

from .conftest import MiniVault, make_wiki_page


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


class _FakeScreen:
    """A headless stand-in for a curses window, replaying a key script.

    Lets the read-only test drive the real ``_loop`` (keymap dispatch,
    excerpt reads, re-run) without a TTY. Once the script is exhausted
    it returns ``q`` so the loop always terminates.
    """

    def __init__(self, keys: list[int], rows: int = 24, cols: int = 80) -> None:
        self._keys = iter(keys)
        self._rows = rows
        self._cols = cols

    def getmaxyx(self) -> tuple[int, int]:
        return (self._rows, self._cols)

    def getch(self) -> int:
        return next(self._keys, ord("q"))

    def keypad(self, _flag: bool) -> None:
        pass

    def erase(self) -> None:
        pass

    def addstr(self, _y: int, _x: int, _s: str) -> None:
        pass

    def refresh(self) -> None:
        pass


class TestReadOnly:
    def test_view_path_does_not_mutate_the_vault(self, mini_vault: MiniVault) -> None:
        pytest.importorskip("curses")
        from densa.runner import lint_all  # noqa: PLC0415
        from densa.tui import view  # noqa: PLC0415
        from densa.tui.app_curses import _read_excerpt  # noqa: PLC0415
        from densa.tui.model import initial  # noqa: PLC0415

        # A page with an unresolvable wikilink → at least one finding with
        # a real line number, so the excerpt reader is exercised too.
        mini_vault.write(
            "domains/d/wiki/concepts/a.md",
            make_wiki_page(extra="see [[totally-unresolvable-placeholder]]\n"),
        )
        before = _snapshot(mini_vault.root)

        report = lint_all(mini_vault.root)
        state = initial(report)
        cache: dict[str, list[str] | None] = {}
        for diag in report.diagnostics:
            _read_excerpt(mini_vault.root, diag.path, cache)
        for w in (20, 80):
            for h in (5, 20):
                view.render(state, w, h)

        assert _snapshot(mini_vault.root) == before

    def test_event_loop_does_not_mutate_the_vault(
        self, mini_vault: MiniVault
    ) -> None:
        # Drives the REAL _loop (not just the read primitives) so a write
        # introduced anywhere in the event loop — keymap handling, the `r`
        # re-run, excerpt caching — would flip this guardrail red.
        pytest.importorskip("curses")
        from densa.runner import lint_all  # noqa: PLC0415
        from densa.tui import app_curses  # noqa: PLC0415

        mini_vault.write(
            "domains/d/wiki/concepts/a.md",
            make_wiki_page(extra="see [[totally-unresolvable-placeholder]]\n"),
        )
        before = _snapshot(mini_vault.root)
        # nav down, open excerpt (reads file), close, re-run lint, quit.
        keys = [ord("j"), ord("\n"), 27, ord("r"), ord("q")]
        screen = _FakeScreen(keys)
        rc = app_curses._loop(screen, mini_vault.root, lint_all(mini_vault.root))

        assert rc == 0
        assert _snapshot(mini_vault.root) == before

    def test_read_excerpt_returns_none_for_missing_file(
        self, mini_vault: MiniVault
    ) -> None:
        pytest.importorskip("curses")
        from densa.tui.app_curses import _read_excerpt  # noqa: PLC0415

        assert _read_excerpt(mini_vault.root, "does/not/exist.md", {}) is None


class TestLazyCursesImport:
    def test_curses_absent_after_lint(self) -> None:
        # Fresh interpreter: import the CLI, run a non-tui command, assert
        # curses never entered sys.modules.
        code = (
            "import sys\n"
            "from densa import cli\n"
            "assert 'curses' not in sys.modules, 'curses at import time'\n"
            "cli.main(['version'])\n"
            "assert 'curses' not in sys.modules, 'curses after a lint-path cmd'\n"
            "print('ok')\n"
        )
        repo_root = Path(__file__).resolve().parents[1]  # _system/
        proc = subprocess.run(
            [sys.executable, "-c", code],
            env={"PYTHONPATH": str(repo_root)},
            capture_output=True,
            text=True,
            cwd=str(repo_root.parent),
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        assert "ok" in proc.stdout


class TestCliWiring:
    def test_tui_is_dispatchable(self) -> None:
        assert "tui" in cli._DISPATCH

    def test_tui_parses_diff_flag(self) -> None:
        parser = cli._build_parser()
        args = parser.parse_args(["tui", "--diff", "origin/main"])
        assert args.command == "tui"
        assert args.diff == "origin/main"

    def test_tui_diff_defaults_none(self) -> None:
        parser = cli._build_parser()
        args = parser.parse_args(["tui"])
        assert args.diff is None

    def test_non_curses_import_error_is_not_masked(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # A real import bug inside the tui package (not a missing curses)
        # must surface, not be reported as "unsupported platform".
        import densa.tui  # noqa: F401, PLC0415  (ensure parent is importable)

        monkeypatch.setitem(sys.modules, "densa.tui.app_curses", None)
        args = cli._build_parser().parse_args(["tui"])
        with pytest.raises(ImportError):
            cli._cmd_tui(args)
