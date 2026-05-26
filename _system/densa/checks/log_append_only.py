"""AGENTS002 — log.md is append-only.

Rejects staged ``-`` (deletion) lines in any ``log.md``, with two
narrow exceptions:

1. The ``---`` frontmatter delimiter line — allowed to bounce because
   it's structural noise, not history.
2. A paired ``updated: YYYY-MM-DD`` frontmatter bump (one removed line
   ↔ one added line) — the human-curated timestamp on top of the
   frontmatter is allowed to roll forward in lockstep with each new
   entry.

A one-shot reorder sweep (when an old log drifted into forward-chrono
order and needs a clean re-permutation) is permitted via the
``WIKI_ALLOW_LOG_REORDER=1`` environment variable. The diff must then
be a *pure permutation* — every removed line reappears verbatim on the
added side — plus a fresh ``## [YYYY-MM-DD] maintenance | …`` heading
recording the reorder for audit.
"""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

from densa.config import LOG_REORDER_BYPASS_ENV
from densa.git_io import StagedDiff, StagedEntry, staged_deletions, staged_diff
from densa.paths import is_log
from densa.report import Diagnostic, Report, Severity

_RULE_ID = "AGENTS002"

_UPDATED_FIELD_RE = re.compile(r"^\s*updated:\s*\d{4}-\d{2}-\d{2}\s*$")
_MAINTENANCE_HEADING_RE = re.compile(
    r"^##\s*\[\d{4}-\d{2}-\d{2}\]\s*maintenance\s*\|",
)


class LogAppendOnly:
    id: str = _RULE_ID

    def apply(
        self,
        repo: Path,
        entries: list[StagedEntry],
        report: Report,
    ) -> None:
        bypass = os.environ.get(LOG_REORDER_BYPASS_ENV) == "1"
        for entry in entries:
            if not is_log(entry.path) or entry.letter == "A":
                continue
            self._check_one(repo, entry.path, bypass, report)

    def _check_one(
        self,
        repo: Path,
        path: str,
        bypass: bool,
        report: Report,
    ) -> None:
        diff = staged_diff(repo, path)
        removed_updated = sum(
            1 for line in diff.removed if _UPDATED_FIELD_RE.match(line)
        )
        added_updated = sum(
            1 for line in diff.added if _UPDATED_FIELD_RE.match(line)
        )
        updated_paired = removed_updated == added_updated

        if not updated_paired:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=0,
                message=(
                    "unbalanced `updated:` frontmatter bump "
                    f"(removed={removed_updated}, added={added_updated})"
                ),
            ))

        deletions = [
            (lineno, content)
            for lineno, content in staged_deletions(repo, path)
            if content.strip() != "---"
            and not (
                updated_paired and _UPDATED_FIELD_RE.match(content)
            )
        ]

        if not deletions:
            return

        if bypass:
            self._check_bypass(path, diff, report)
        else:
            for lineno, content in deletions:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.ERROR,
                    path=path,
                    line=lineno,
                    message=(
                        "AGENTS002 log-append-only: staged deletion of "
                        f"{content.rstrip()!r}. Logs are append-only and "
                        "reverse-chronological (AGENTS.md §\"Red lines\"); new entries go above "
                        "older ones. For a one-shot reorder sweep, set "
                        f"`{LOG_REORDER_BYPASS_ENV}=1` and include a "
                        "`## [YYYY-MM-DD] maintenance | ...` audit entry."
                    ),
                ))

    def _check_bypass(
        self,
        path: str,
        diff: StagedDiff,
        report: Report,
    ) -> None:
        ok, reason = self._is_pure_reorder(diff.removed, diff.added)
        if not ok:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=0,
                message=(
                    f"log edit rejected under {LOG_REORDER_BYPASS_ENV}: "
                    f"{reason}"
                ),
            ))
            return
        if not self._has_maintenance_entry(diff.added):
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=0,
                message=(
                    f"{LOG_REORDER_BYPASS_ENV}=1 requires a new "
                    "`## [YYYY-MM-DD] maintenance | ` heading recording "
                    "the reorder for audit trail"
                ),
            ))

    @staticmethod
    def _is_pure_reorder(
        removed: list[str],
        added: list[str],
    ) -> tuple[bool, str]:
        rem = list(removed)
        add = list(added)
        rem_upd = [i for i, ln in enumerate(rem) if _UPDATED_FIELD_RE.match(ln)]
        add_upd = [i for i, ln in enumerate(add) if _UPDATED_FIELD_RE.match(ln)]
        if len(rem_upd) != len(add_upd):
            return False, "unbalanced `updated:` frontmatter bump"
        for i in reversed(rem_upd):
            del rem[i]
        for i in reversed(add_upd):
            del add[i]
        missing = Counter(rem) - Counter(add)
        if missing:
            sample = next(iter(missing))
            return False, (
                "removed line not matched verbatim on the added side: "
                f"{sample!r} (reorder must be a pure permutation)"
            )
        return True, ""

    @staticmethod
    def _has_maintenance_entry(added_lines: list[str]) -> bool:
        return any(
            _MAINTENANCE_HEADING_RE.match(line) for line in added_lines
        )
