"""Densa's interactive diagnostics viewer (``densa tui``).

A thin, read-only curses surface over a :class:`densa.report.Report`.
The package is split so that all *logic* lives in importable, pure
modules (:mod:`densa.tui.model`, :mod:`densa.tui.intents`,
:mod:`densa.tui.noise`) and only :mod:`densa.tui.app_curses` imports
``curses``. The CLI entry point (`densa tui`) lazy-imports the driver
so the common lint / pre-commit path never pays the ``curses`` import
cost — mirroring :func:`densa.cli._cmd_mcp`.

Scope is deliberately narrow (see
``.workflow/active/WFS-densa-tui/.brainstorming/spec-diagnostics-viewer.md``):
scroll/filter/mute findings and read the offending excerpt. It is not
a page browser and not an operation runner.
"""

from __future__ import annotations
