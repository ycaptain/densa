"""The curses driver — the viewer's only impure shell.

Everything stateful and decidable lives in the pure view-model
(:mod:`densa.tui.model`) and renderer (:mod:`densa.tui.view`); this
module does only the three things that genuinely need a terminal and a
filesystem:

1. translate raw keypresses into :class:`densa.tui.intents.Intent`,
2. read excerpt file content from disk (lazily, cached),
3. paint rows and pump the event loop under :func:`curses.wrapper`,
   which guarantees the terminal is restored on every exit path
   (normal quit, ``KeyboardInterrupt``, or an exception).

It imports ``curses`` at module top, so the CLI entry point
(:func:`densa.cli._cmd_tui`) imports *this module* lazily — keeping
``curses`` off the import path of the common lint / pre-commit run, and
letting the import fail cleanly on platforms without curses (Windows).
"""

from __future__ import annotations

import contextlib
import curses
from pathlib import Path

from densa.config import rule_by_id
from densa.report import Report
from densa.runner import lint_all
from densa.tui import view
from densa.tui.intents import Intent
from densa.tui.model import initial, reduce

# Raw key → intent. Arrow keys (curses KEY_*) and vim keys both map.
_KEYMAP: dict[int, Intent] = {
    ord("k"): Intent.NAV_UP,
    curses.KEY_UP: Intent.NAV_UP,
    ord("j"): Intent.NAV_DOWN,
    curses.KEY_DOWN: Intent.NAV_DOWN,
    ord("g"): Intent.TOP,
    ord("G"): Intent.BOTTOM,
    ord("s"): Intent.CYCLE_SEV,
    ord("f"): Intent.CYCLE_RULE,
    ord("m"): Intent.TOGGLE_MUTE,
    ord("\n"): Intent.OPEN_EXCERPT,
    curses.KEY_ENTER: Intent.OPEN_EXCERPT,
    27: Intent.CLOSE_EXCERPT,  # Esc
    ord("q"): Intent.QUIT,
}


def _read_excerpt(
    repo: Path, rel: str, cache: dict[str, list[str] | None]
) -> list[str] | None:
    """Read *rel*'s lines (cached). ``None`` when unreadable — the
    renderer turns that into an inline "(unreadable)" note."""
    if rel in cache:
        return cache[rel]
    try:
        lines = (repo / rel).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        lines = None
    cache[rel] = lines
    return lines


def _paint(stdscr: curses.window, rows: list[str], flash: str | None) -> None:
    height, width = stdscr.getmaxyx()
    stdscr.erase()
    for i, row in enumerate(rows):
        if i >= height:
            break
        # Trim to width-1 to dodge the classic bottom-right-cell error.
        with contextlib.suppress(curses.error):
            stdscr.addstr(i, 0, row[: max(0, width - 1)])
    if flash and height >= 1:
        with contextlib.suppress(curses.error):
            stdscr.addstr(height - 1, 0, flash[: max(0, width - 1)])
    stdscr.refresh()


def _loop(stdscr: curses.window, repo: Path, report: Report) -> int:
    with contextlib.suppress(curses.error):
        curses.curs_set(0)
    stdscr.keypad(True)

    state = initial(report)
    excerpt_cache: dict[str, list[str] | None] = {}
    flash: str | None = None

    while not state.quit:
        height, width = stdscr.getmaxyx()
        excerpt_lines: list[str] | None = None
        if state.excerpt_open:
            sel = state.selected()
            if sel is not None and sel.line > 0:
                excerpt_lines = _read_excerpt(repo, sel.path, excerpt_cache)
        rows = view.render(state, width, height, excerpt_lines)
        _paint(stdscr, rows, flash)
        flash = None

        ch = stdscr.getch()
        if ch == ord("r"):  # re-run: the only refresh; rebuild the snapshot
            report = lint_all(repo)
            state = initial(report)
            excerpt_cache.clear()
            flash = " re-ran densa --all"
            continue
        if ch == ord("e"):  # explain the selected rule (transient)
            sel = state.selected()
            if sel is not None:
                spec = rule_by_id(sel.rule_id)
                summary = spec.summary if spec is not None else "(unknown rule)"
                flash = f" {sel.rule_id}: {summary}"
            continue
        intent = _KEYMAP.get(ch)
        if intent is not None:
            state = reduce(state, intent)

    return 0


def run(repo: Path, report: Report) -> int:
    """Open the viewer over *report*. Returns 0 (a viewer's exit is not a
    lint verdict). ``curses.wrapper`` restores the terminal on every
    exit path, including exceptions and ``Ctrl-C``."""
    try:
        return int(curses.wrapper(_loop, repo, report))
    except KeyboardInterrupt:  # pragma: no cover - interactive
        return 0
