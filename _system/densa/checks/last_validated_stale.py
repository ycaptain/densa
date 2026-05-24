"""AGENTS008 — last_validated freshness.

Per L1 §3.3, every page with ``type`` in {concept, framework,
protocol, entity} declares a ``last_validated: YYYY-MM-DD`` timestamp
recording the last time the LLM (or human) re-read the cited sources
and confirmed the page still reflects them.

This rule warns (does **not** block commits) when ``last_validated``
is older than 180 days on those types. The warning surfaces drift
candidates so the human can re-validate; auto-bumping the timestamp
without re-reading sources would be a closed-epistemic-loop
violation (the LLM MUST NOT do that — see L1 §3.3).

Missing ``last_validated`` on the four types triggers AGENTS003
(``frontmatter-required-keys``) once the field is added to the
required-keys set; for now this rule treats missing as silent (it's
the templates' job to seed the field).
"""

from __future__ import annotations

from datetime import date, datetime

from densa.frontmatter import parse
from densa.paths import is_wiki
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex

_RULE_ID = "AGENTS008"
_REQUIRES_LAST_VALIDATED = frozenset({"concept", "framework", "protocol", "entity"})
_TTL_DAYS = 180


class LastValidatedFresh:
    id: str = _RULE_ID

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None:
        if not is_wiki(path):
            return
        fm = parse(text)
        if fm is None:
            return
        if fm.get("type") not in _REQUIRES_LAST_VALIDATED:
            return

        raw = fm.get("last_validated")
        if not raw:
            return  # AGENTS003 territory once the field is required
        stamp = _parse_iso_date(str(raw))
        if stamp is None:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    f"AGENTS008 last-validated-fresh: `last_validated: "
                    f"{raw}` is not a YYYY-MM-DD date"
                ),
            ))
            return

        age = (date.today() - stamp).days
        if age > _TTL_DAYS:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    f"AGENTS008 last-validated-fresh: last_validated "
                    f"({stamp.isoformat()}) is {age} days old (>{_TTL_DAYS}); "
                    f"re-read the cited sources and bump the timestamp, "
                    f"or accept that this page is stale"
                ),
            ))


def _parse_iso_date(raw: str) -> date | None:
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
