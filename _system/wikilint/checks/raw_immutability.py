"""AGENTS001 — raw/ is immutable.

Staged modify/delete of any path under a ``raw/`` directory, or rename
*from* a ``raw/`` path, is rejected. See L1 §6.

Adds and rename-*into* ``raw/`` from outside (e.g. the
``git mv inbox/x domains/<X>/raw/<bucket>/y`` move that
``process-inbox`` performs per L1 §2.4) are permitted: that's how
users intentionally file new sources. The bypass for this rule is
intentionally absent — the red line has no sanctioned exception in
user vaults. (Template maintenance can use ``git commit --no-verify``
once per release; that is an out-of-band escape, not a feature.)
"""

from __future__ import annotations

from pathlib import Path

from wikilint.git_io import StagedEntry
from wikilint.paths import is_raw
from wikilint.report import Diagnostic, Report, Severity

_RULE_ID = "AGENTS001"
_IN_PLACE_LETTERS = frozenset({"M", "D"})


class RawImmutability:
    id: str = _RULE_ID

    def apply(
        self,
        repo: Path,
        entries: list[StagedEntry],
        report: Report,
    ) -> None:
        for entry in entries:
            blocked = False
            if entry.letter in _IN_PLACE_LETTERS:
                blocked = is_raw(entry.path)
            elif entry.letter == "R":
                # Only forbid renames whose SOURCE is in raw/. Renaming
                # inbox/foo → domains/<X>/raw/<bucket>/foo is the
                # canonical `process-inbox` action and must be allowed.
                # If we have no src (legacy callers, or pre-`--diff`
                # tooling), fall back to dest to stay conservative.
                src = entry.src or entry.path
                blocked = is_raw(src)
            # `C` (copy) leaves the source intact; the destination is a
            # new file — treat it like `A` and let the user file new
            # raw material that way.
            if blocked:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.ERROR,
                    path=entry.path,
                    line=0,
                    message=(
                        f"raw/ is immutable; staged status={entry.letter}"
                    ),
                ))
