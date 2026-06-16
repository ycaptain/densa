"""User intents — the closed alphabet the view-model reduces over.

Intents are payload-free: each one maps to exactly one pure transition
in :func:`densa.tui.model.reduce`. The curses driver
(:mod:`densa.tui.app_curses`) is responsible for translating raw
keypresses into intents and for any height-dependent behaviour (page
scrolling, viewport sizing) that cannot live in the height-agnostic
view-model.
"""

from __future__ import annotations

from enum import Enum, auto


class Intent(Enum):
    """A single user action. One intent → one :func:`reduce` transition."""

    NAV_UP = auto()
    NAV_DOWN = auto()
    TOP = auto()
    BOTTOM = auto()
    CYCLE_SEV = auto()
    CYCLE_RULE = auto()
    TOGGLE_MUTE = auto()
    OPEN_EXCERPT = auto()
    CLOSE_EXCERPT = auto()
    QUIT = auto()
