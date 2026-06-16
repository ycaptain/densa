"""The pure view-model for ``densa tui``.

All navigation, filtering and selection state lives here as a frozen
:class:`AppState`; every transition is a pure function
(:func:`reduce`) that returns a *new* state. No ``curses`` import, no
I/O, no height awareness — which is exactly what makes the bulk of the
viewer unit-testable without a terminal (see the property tests in
``_system/tests/test_tui_model.py``).

Invariants maintained by every :func:`reduce` call:

* ``0 <= cursor < len(visible)`` when ``visible`` is non-empty;
  ``cursor == 0`` when it is empty.
* ``visible`` is ``all`` filtered by (mute, severity, rule), order-stable.
* ``excerpt_open`` implies a valid selection (``visible`` non-empty).
* ``muted_count`` depends only on ``all`` (constant across toggles).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from densa.report import Diagnostic, Report, Severity
from densa.tui.intents import Intent
from densa.tui.noise import is_known_noise


class SeverityFilter(Enum):
    """Which severities the list shows."""

    ALL = "all"
    ERRORS_ONLY = "errors"
    WARN_ONLY = "warnings"

    def accepts(self, severity: Severity) -> bool:
        if self is SeverityFilter.ALL:
            return True
        if self is SeverityFilter.ERRORS_ONLY:
            return severity is Severity.ERROR
        return severity is Severity.WARNING


# Cycle order for the ``s`` key.
_SEV_CYCLE: tuple[SeverityFilter, ...] = (
    SeverityFilter.ALL,
    SeverityFilter.ERRORS_ONLY,
    SeverityFilter.WARN_ONLY,
)


@dataclass(frozen=True)
class AppState:
    """Immutable snapshot of the viewer's state.

    ``all`` is the full, frozen set of findings from one lint run; the
    viewer never re-reads it implicitly (staleness is resolved only by
    an explicit re-run, handled in the driver).
    """

    all: tuple[Diagnostic, ...]
    severity_filter: SeverityFilter = SeverityFilter.ALL
    rule_filter: str | None = None
    mute_noise: bool = True
    cursor: int = 0
    excerpt_open: bool = False
    quit: bool = False

    # --- derived views (pure) --------------------------------------

    def visible(self) -> tuple[Diagnostic, ...]:
        """``all`` filtered by mute + severity + rule, order-stable."""
        out: list[Diagnostic] = []
        for d in self.all:
            if self.mute_noise and is_known_noise(d.path):
                continue
            if not self.severity_filter.accepts(d.severity):
                continue
            if self.rule_filter is not None and d.rule_id != self.rule_filter:
                continue
            out.append(d)
        return tuple(out)

    @property
    def muted_count(self) -> int:
        """How many findings live in a known-noise tree (constant)."""
        return sum(1 for d in self.all if is_known_noise(d.path))

    def present_rule_ids(self) -> tuple[str, ...]:
        """Sorted unique rule IDs across ``all`` (filter-cycle order)."""
        return tuple(sorted({d.rule_id for d in self.all}))

    def selected(self) -> Diagnostic | None:
        """The finding under the cursor, or ``None`` when empty."""
        vis = self.visible()
        if not vis:
            return None
        return vis[self.cursor]


def initial(report: Report) -> AppState:
    """Build the starting state from a lint :class:`Report`."""
    return _reclamp(AppState(all=tuple(report.diagnostics)))


def _clamp_cursor(cursor: int, n: int) -> int:
    if n <= 0:
        return 0
    return min(max(cursor, 0), n - 1)


def _reclamp(state: AppState) -> AppState:
    """Re-clamp cursor to the current ``visible`` length and close any
    now-invalid excerpt. Called after every filter/mute change."""
    n = len(state.visible())
    cursor = _clamp_cursor(state.cursor, n)
    excerpt_open = state.excerpt_open and n > 0
    if cursor == state.cursor and excerpt_open == state.excerpt_open:
        return state
    return replace(state, cursor=cursor, excerpt_open=excerpt_open)


def _cycle(seq: tuple[object, ...], current: object) -> object:
    """Next element after *current* in *seq*, wrapping around."""
    idx = seq.index(current) if current in seq else -1
    return seq[(idx + 1) % len(seq)]


def reduce(state: AppState, intent: Intent) -> AppState:
    """Return a new :class:`AppState` for *intent*. Pure; never mutates
    *state*. Exactly one transition per call."""
    n = len(state.visible())

    if intent is Intent.NAV_UP:
        return replace(state, cursor=_clamp_cursor(state.cursor - 1, n))
    if intent is Intent.NAV_DOWN:
        return replace(state, cursor=_clamp_cursor(state.cursor + 1, n))
    if intent is Intent.TOP:
        return replace(state, cursor=0)
    if intent is Intent.BOTTOM:
        return replace(state, cursor=_clamp_cursor(n - 1, n))

    if intent is Intent.CYCLE_SEV:
        nxt = _cycle(_SEV_CYCLE, state.severity_filter)
        assert isinstance(nxt, SeverityFilter)  # narrow for mypy
        return _reclamp(replace(state, severity_filter=nxt))
    if intent is Intent.CYCLE_RULE:
        ring: tuple[str | None, ...] = (None, *state.present_rule_ids())
        nxt_rule = _cycle(ring, state.rule_filter)
        assert nxt_rule is None or isinstance(nxt_rule, str)
        return _reclamp(replace(state, rule_filter=nxt_rule))
    if intent is Intent.TOGGLE_MUTE:
        return _reclamp(replace(state, mute_noise=not state.mute_noise))

    if intent is Intent.OPEN_EXCERPT:
        return replace(state, excerpt_open=n > 0)
    if intent is Intent.CLOSE_EXCERPT:
        return replace(state, excerpt_open=False)
    if intent is Intent.QUIT:
        return replace(state, quit=True)

    # Exhaustive over Intent; unreachable.
    raise AssertionError(f"unhandled intent: {intent!r}")  # pragma: no cover
