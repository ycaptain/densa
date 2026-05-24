"""Base protocols for rules.

The runner sorts rules into two buckets by interface:

- :class:`FileRule` is asked, for each markdown file in scope,
  "does this file violate you?". Implementations append to the
  :class:`~densa.report.Report`.
- :class:`StagedRule` is asked once per lint run, holding the staged
  entries and a callback for fetching diffs. Used for rules that look
  at the *shape* of staged changes rather than file contents.

Keeping the two protocols separate avoids the common ``check_file()``
god-function pattern where every rule signature had to grow whenever
a new rule needed a new piece of context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from densa.git_io import StagedEntry
from densa.report import Report
from densa.wikilink import SlugIndex


class FileRule(Protocol):
    """A rule applied to one file's text at a time."""

    id: str

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None: ...


class StagedRule(Protocol):
    """A rule applied to the staged change set as a whole.

    The repo path is passed so the rule can fetch diffs lazily via
    :mod:`densa.git_io`.
    """

    id: str

    def apply(
        self,
        repo: Path,
        entries: list[StagedEntry],
        report: Report,
    ) -> None: ...
