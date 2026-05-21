"""AGENTS001 — raw/ is immutable.

Staged modify/delete/rename of any path under a ``raw/`` directory is
rejected. See L1 §6.

Adds, copies into raw/, are permitted: that's how users intentionally
file new sources. The bypass for this rule is intentionally absent —
the red line has no sanctioned exception in user vaults. (Template
maintenance can use ``git commit --no-verify`` once per release; that
is an out-of-band escape, not a feature.)
"""

from __future__ import annotations

from pathlib import Path

from wikilint.git_io import StagedEntry
from wikilint.paths import is_raw
from wikilint.report import Diagnostic, Report, Severity

_RULE_ID = "AGENTS001"
_REJECTED_LETTERS = frozenset({"M", "D", "R"})


class RawImmutability:
    id: str = _RULE_ID

    def apply(
        self,
        repo: Path,
        entries: list[StagedEntry],
        report: Report,
    ) -> None:
        for entry in entries:
            if is_raw(entry.path) and entry.letter in _REJECTED_LETTERS:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.ERROR,
                    path=entry.path,
                    line=0,
                    message=(
                        f"raw/ is immutable; staged status={entry.letter}"
                    ),
                ))
