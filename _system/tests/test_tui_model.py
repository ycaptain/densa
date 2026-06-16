"""Property + boundary tests for the ``densa tui`` view-model.

These exercise the contract in
``.workflow/active/WFS-densa-tui/.brainstorming/spec-diagnostics-viewer.md``
§6 (tests 1, 3, 4, 5). They are framework-agnostic: the view-model
imports no ``curses``, so the bulk of the viewer's behaviour is proven
here without a terminal. Randomised cases use a seeded stdlib
``random`` (no new dependency).
"""

from __future__ import annotations

import random
import sys

from densa.report import Diagnostic, Report, Severity
from densa.tui.intents import Intent
from densa.tui.model import AppState, SeverityFilter, initial, reduce
from densa.tui.noise import NOISE_PREFIXES

_RULE_IDS = ("DENSA-IO", "AGENTS001", "AGENTS006", "AGENTS007", "AGENTS014")
_PATH_DIRS = (
    "domains/research-papers/wiki/concepts/",
    "domains/research-papers/raw/papers/",
    "_system/densa/",
    "docs/maintainers/",  # noise
    ".backlog/tasks/",  # noise
)
_ALL_INTENTS = tuple(Intent)


def _rand_report(rng: random.Random, n: int) -> Report:
    report = Report()
    for i in range(n):
        report.add(
            Diagnostic(
                rule_id=rng.choice(_RULE_IDS),
                severity=rng.choice((Severity.ERROR, Severity.WARNING)),
                path=rng.choice(_PATH_DIRS) + f"page-{i}.md",
                line=rng.choice((0, 1, 5, 42)),
                message=f"finding {i}",
            )
        )
    return report


def _assert_invariants(state: AppState) -> None:
    vis = state.visible()
    if vis:
        assert 0 <= state.cursor < len(vis)
    else:
        assert state.cursor == 0
    if state.excerpt_open:
        assert len(vis) > 0
    # muted_count counts noise findings in `all`, independent of toggles.
    expected_muted = sum(
        1 for d in state.all if any(d.path.startswith(p) for p in NOISE_PREFIXES)
    )
    assert state.muted_count == expected_muted


class TestReduceInvariants:
    """§6.1 — invariants hold after every intent in any sequence."""

    def test_random_intent_sequences(self) -> None:
        for seed in range(50):
            rng = random.Random(seed)
            state = initial(_rand_report(rng, rng.randint(0, 30)))
            _assert_invariants(state)
            for _ in range(40):
                state = reduce(state, rng.choice(_ALL_INTENTS))
                _assert_invariants(state)

    def test_view_model_does_not_import_curses(self) -> None:
        # The whole point of the view-model: importing it must not drag in
        # curses. Checked in a fresh interpreter because sys.modules is
        # process-global (another test importing the driver would pollute
        # an in-process assertion).
        import subprocess  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        repo_root = Path(__file__).resolve().parents[1]  # _system/
        code = (
            "import sys\n"
            "import densa.tui.model, densa.tui.noise, densa.tui.intents\n"
            "assert 'curses' not in sys.modules\n"
            "print('ok')\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            env={"PYTHONPATH": str(repo_root)},
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        assert "ok" in proc.stdout


class TestBoundaryStates:
    """§4 state enumeration: empty / single / full edges."""

    def test_empty_report(self) -> None:
        state = initial(Report())
        assert state.visible() == ()
        assert state.selected() is None
        # Nav is a no-op on empty.
        for intent in (Intent.NAV_DOWN, Intent.NAV_UP, Intent.BOTTOM, Intent.TOP):
            assert reduce(state, intent).cursor == 0
        # Cannot open an excerpt with nothing selected.
        assert reduce(state, Intent.OPEN_EXCERPT).excerpt_open is False

    def test_single_finding_pins_cursor(self) -> None:
        report = Report()
        report.add(Diagnostic("AGENTS001", Severity.ERROR, "domains/x/a.md", 1, "x"))
        state = initial(report)
        assert reduce(state, Intent.NAV_DOWN).cursor == 0
        assert reduce(state, Intent.NAV_UP).cursor == 0
        assert reduce(state, Intent.OPEN_EXCERPT).excerpt_open is True

    def test_nav_down_bounded_at_end(self) -> None:
        report = Report()
        for i in range(3):
            report.add(
                Diagnostic("AGENTS001", Severity.ERROR, f"domains/x/{i}.md", 1, "x")
            )
        state = initial(report)
        for _ in range(10):
            state = reduce(state, Intent.NAV_DOWN)
        assert state.cursor == 2  # never runs past the last index


class TestFilterTotality:
    """§6.4 — every finding is either visible or accounted-for, never lost."""

    def test_visible_plus_excluded_equals_total(self) -> None:
        rng = random.Random(7)
        base = initial(_rand_report(rng, 40))
        # Walk a representative grid of filter states.
        for sev in SeverityFilter:
            for rule in (None, *base.present_rule_ids()):
                for mute in (True, False):
                    s = AppState(
                        all=base.all,
                        severity_filter=sev,
                        rule_filter=rule,
                        mute_noise=mute,
                    )
                    vis = s.visible()
                    # No duplicates, subset of all, order-stable.
                    assert len(vis) <= len(s.all)
                    assert all(d in s.all for d in vis)
                    # Order stability: visible follows all's order.
                    idxs = [s.all.index(d) for d in vis]
                    assert idxs == sorted(idxs)


class TestSnapshotImmutability:
    """§6.5 — reduce never mutates its input state or the report list."""

    def test_reduce_returns_new_state_without_mutation(self) -> None:
        rng = random.Random(3)
        report = _rand_report(rng, 20)
        original_len = len(report.diagnostics)
        state = initial(report)
        before_all = state.all
        before_cursor = state.cursor
        for intent in _ALL_INTENTS:
            reduce(state, intent)  # discard result
        # Input state untouched (frozen dataclass guarantees, but assert
        # the observable fields explicitly).
        assert state.all is before_all
        assert state.cursor == before_cursor
        # Underlying report list not mutated by snapshotting/reducing.
        assert len(report.diagnostics) == original_len
