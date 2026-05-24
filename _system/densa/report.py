"""Structured diagnostics — the value type carried across every rule.

A :class:`Diagnostic` is the atomic finding: a file, a line, a rule that
fired, a human message, and a severity. A :class:`Report` is a bag of
diagnostics plus a tally of files actually inspected (used in the
summary line).

Diagnostics are deliberately pure data: rule implementations append
them to a report, and the formatter (text / JSON / GitHub) consumes
them. No formatting decision is made at construction time.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from enum import Enum


class Severity(str, Enum):
    """How seriously a finding should be treated.

    ``ERROR``-level diagnostics flip the runner exit code; ``WARNING``
    surfaces but does not fail. Severity is a property of the *finding*,
    not of the rule — the same rule can emit different severities for
    different inputs (e.g. ``WikilinkResolvable`` emits ERROR for a
    missing link and WARNING for an ambiguous one).
    """

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Diagnostic:
    """One finding from one rule against one file location.

    Attributes
    ----------
    rule_id :
        Stable identifier such as ``"AGENTS001"``. See
        :mod:`densa.config` for the canonical registry. Used by
        ``--select`` / ``--ignore``.
    severity :
        ``Severity.ERROR`` flips exit code; ``Severity.WARNING`` does not.
    path :
        Repo-relative path, forward slashes.
    line :
        1-indexed line number. ``0`` means "the whole file" — used for
        rules that cannot point at a specific line (e.g. frontmatter
        missing entirely).
    message :
        Human-readable finding. Should not include the path/line — the
        formatter adds those. Should be one line, ≤ 120 chars.
    """

    rule_id: str
    severity: Severity
    path: str
    line: int
    message: str

    def to_dict(self) -> dict[str, str | int]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


@dataclass
class Report:
    """Accumulates diagnostics and a checked-file count.

    A single ``Report`` is threaded through one lint run. ``add()`` and
    ``saw()`` mutate it in place; everything else is read-only.
    """

    diagnostics: list[Diagnostic] = field(default_factory=list)
    files_checked: int = 0

    def add(self, diagnostic: Diagnostic) -> None:
        self.diagnostics.append(diagnostic)

    def saw(self) -> None:
        """Called once per file actually inspected (not skipped)."""
        self.files_checked += 1

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.WARNING]

    @property
    def has_errors(self) -> bool:
        return any(d.severity is Severity.ERROR for d in self.diagnostics)

    def extend(self, items: Iterable[Diagnostic]) -> None:
        self.diagnostics.extend(items)
