"""Render-shape property + boundary tests for ``densa.tui.view``.

Spec §6.2: for any state and any (width>=20, height>=5) the renderer
returns exactly ``height`` rows, each at most ``width`` columns, and
never raises. Below-minimum dimensions degrade to a single notice.
PBT here is paired with explicit boundary generators (BVA) because
naive random sizes cluster away from the min-dimension edges that
actually break renderers.
"""

from __future__ import annotations

import random

from densa.report import Diagnostic, Report, Severity
from densa.tui.intents import Intent
from densa.tui.model import AppState, initial, reduce
from densa.tui.view import (
    MIN_HEIGHT,
    MIN_WIDTH,
    render,
    scroll_window,
    too_small,
)

_RULE_IDS = ("DENSA-IO", "AGENTS001", "AGENTS006", "AGENTS014")
_PATHS = (
    "domains/research-papers/wiki/concepts/superposition.md",
    "_system/densa/cli.py",
    "docs/maintainers/plan.md",  # noise
    ".backlog/tasks/t-1.md",  # noise
)


def _rand_state(rng: random.Random, n: int) -> AppState:
    report = Report()
    for _ in range(n):
        report.add(
            Diagnostic(
                rule_id=rng.choice(_RULE_IDS),
                severity=rng.choice((Severity.ERROR, Severity.WARNING)),
                path=rng.choice(_PATHS),
                line=rng.choice((0, 1, 7, 999)),
                message=rng.choice(("short", "a much longer message " * 4)),
            )
        )
    state = initial(report)
    # Randomly walk into varied filter/cursor/excerpt states.
    for _ in range(rng.randint(0, 15)):
        state = reduce(state, rng.choice(tuple(Intent)))
    return state


def _assert_shape(rows: list[str], width: int, height: int) -> None:
    assert len(rows) == height
    assert all(len(r) <= width for r in rows)


class TestScrollWindow:
    def test_window_contains_cursor_and_is_bounded(self) -> None:
        rng = random.Random(0)
        for _ in range(2000):
            total = rng.randint(1, 200)
            rows = rng.randint(1, 60)
            cursor = rng.randint(0, total - 1)
            start, end = scroll_window(cursor, total, rows)
            assert 0 <= start <= end <= total
            assert end - start <= rows
            assert start <= cursor < end  # cursor always visible

    def test_short_list_shows_all(self) -> None:
        assert scroll_window(0, 3, 10) == (0, 3)

    def test_empty(self) -> None:
        assert scroll_window(0, 0, 10) == (0, 0)


class TestRenderShape:
    """§6.2 — exact height, bounded width, never raises, across BVA dims."""

    def test_property_random_states_and_dims(self) -> None:
        rng = random.Random(42)
        # BVA: include the min edge, just-above, and a wide spread.
        widths = [MIN_WIDTH, MIN_WIDTH + 1, 40, 80, 200]
        heights = [MIN_HEIGHT, MIN_HEIGHT + 1, 10, 30, 60]
        for _ in range(40):
            state = _rand_state(rng, rng.randint(0, 50))
            for w in widths:
                for h in heights:
                    rows = render(state, w, h, excerpt_lines=["x" * 300] * 50)
                    _assert_shape(rows, w, h)

    def test_below_minimum_degrades(self) -> None:
        # BVA: min-1 on each axis must not raise and must fill exactly h.
        for w, h in [(MIN_WIDTH - 1, 10), (40, MIN_HEIGHT - 1), (1, 1), (0, 0)]:
            assert too_small(w, h)
            rows = render(initial(Report()), w, h)
            assert len(rows) == h
            assert all(len(r) <= w for r in rows)


def _sample_report() -> Report:
    report = Report()
    report.add(
        Diagnostic("AGENTS006", Severity.ERROR, "domains/x/a.md", 14, "broken link")
    )
    report.add(
        Diagnostic("AGENTS001", Severity.ERROR, "domains/x/raw/p.md", 0, "raw modified")
    )
    report.add(
        Diagnostic("AGENTS011", Severity.WARNING, "_system/prompts/ingest.md", 8, "drift")
    )
    return report


class TestGoldenScreens:
    """§4 state-enumeration goldens. Assert content, not just shape."""

    def test_empty(self) -> None:
        rows = render(initial(Report()), 40, 6)
        assert any("No findings" in r for r in rows)
        _assert_shape(rows, 40, 6)

    def test_single(self) -> None:
        report = Report()
        report.add(Diagnostic("AGENTS001", Severity.ERROR, "domains/x/a.md", 1, "msg"))
        rows = render(initial(report), 60, 8)
        assert any(">E AGENTS001" in r for r in rows)  # selected marker
        assert any("1/1" in r for r in rows)  # position
        _assert_shape(rows, 60, 8)

    def test_full_scrolls_and_marks_cursor(self) -> None:
        report = Report()
        for i in range(50):
            report.add(
                Diagnostic("AGENTS001", Severity.ERROR, f"domains/x/{i}.md", 1, "m")
            )
        state = initial(report)
        for _ in range(10):
            state = reduce(state, Intent.NAV_DOWN)
        rows = render(state, 60, 10)
        _assert_shape(rows, 60, 10)
        assert any(r.startswith(">") for r in rows)  # cursor row present
        assert any("11/50" in r for r in rows)  # scrolled position

    def test_too_small(self) -> None:
        # Height below MIN with a width wide enough to show the notice.
        rows = render(initial(_sample_report()), 40, MIN_HEIGHT - 1)
        assert any("too small" in r for r in rows)
        _assert_shape(rows, 40, MIN_HEIGHT - 1)

    def test_filtered_out_note(self) -> None:
        # Mute noise + filter to a rule with zero non-noise matches.
        report = Report()
        report.add(Diagnostic("AGENTS006", Severity.ERROR, "docs/maintainers/p.md", 1, "n"))
        state = AppState(all=tuple(report.diagnostics), mute_noise=True)
        rows = render(state, 50, 7)
        assert any("shown" in r for r in rows)  # "0 of N shown ..."
        _assert_shape(rows, 50, 7)

    def test_excerpt_pane(self) -> None:
        report = Report()
        report.add(Diagnostic("AGENTS006", Severity.ERROR, "domains/x/a.md", 2, "bad"))
        state = reduce(initial(report), Intent.OPEN_EXCERPT)
        assert state.excerpt_open
        rows = render(state, 60, 14, excerpt_lines=["line one", "line two", "line three"])
        _assert_shape(rows, 60, 14)
        assert any("domains/x/a.md:2" in r for r in rows)
        assert any("line two" in r for r in rows)

    def test_excerpt_open_at_min_height(self) -> None:
        # Closes the gap the adversarial review flagged: split-pane at the
        # smallest dims the renderer accepts (excerpt path must not under/
        # over-fill at height 5 and 6).
        report = Report()
        report.add(Diagnostic("AGENTS006", Severity.ERROR, "domains/x/a.md", 1, "bad"))
        state = reduce(initial(report), Intent.OPEN_EXCERPT)
        for h in (MIN_HEIGHT, MIN_HEIGHT + 1, MIN_HEIGHT + 2):
            rows = render(state, MIN_WIDTH, h, excerpt_lines=["only line"])
            _assert_shape(rows, MIN_WIDTH, h)
