"""AGENTS010 — schema-version-consistency.

Companion to AGENTS009 (``compiled_against_lag``). Where AGENTS009
emits a *warning* when a wiki page lags the current schema version,
AGENTS010 escalates to an *error* when the lagging page is **not**
under a ``.legacy/`` snapshot directory. The rationale: a v2 vault may
intentionally retain v1 pages under ``wiki/.legacy/<bucket>/`` as a
read-only archive (the migration script puts them there), but pages
that still live at the canonical ``wiki/<bucket>/<slug>.md`` path under
v2 must declare ``compiled_against: <SCHEMA_VERSION>`` or higher —
otherwise they're stale and visible to the graph.

Fix path:

  1. ``densa migrate`` runs the canonical migration script that moves
     unmigrated v1 contents to ``wiki/.legacy/``.
  2. Or, for a single page, manually re-ingest it under the current
     schema (drop the file under ``wiki/.legacy/<bucket>/<slug>.md``
     first to preserve the snapshot, per L1 §6 ``.legacy/`` rule).

Missing ``compiled_against`` is left to AGENTS003 (required-keys).
This rule treats missing as silent so it doesn't double-report.
"""

from __future__ import annotations

from densa.config import SCHEMA_VERSION
from densa.frontmatter import parse
from densa.paths import is_wiki, parts
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex

_RULE_ID = "AGENTS010"
_LEGACY = ".legacy"


class SchemaVersionConsistency:
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
        # ``is_wiki`` already excludes the .legacy/ subtree, so any
        # path that reaches us here is a "live" wiki page subject to
        # the current schema. Defensive double-check in case
        # ``is_wiki`` evolves later.
        if _LEGACY in parts(path):
            return

        fm = parse(text)
        if fm is None:
            return

        raw = fm.get("compiled_against")
        if raw is None or raw == "":
            return  # AGENTS003 territory once the field is required
        try:
            version = int(str(raw).strip())
        except ValueError:
            # AGENTS009 already emits a warning about non-integer
            # values; don't double-report here.
            return

        if version >= SCHEMA_VERSION:
            return

        report.add(Diagnostic(
            rule_id=self.id,
            severity=Severity.ERROR,
            path=path,
            line=1,
            message=(
                f"AGENTS010 schema-version-consistency: page is "
                f"compiled_against={version} but current "
                f"SCHEMA_VERSION={SCHEMA_VERSION}. Run "
                f"`python -m densa migrate` to fold v{version} "
                f"contents under wiki/.legacy/, or move this page "
                f"there by hand and re-ingest its source under "
                f"the v{SCHEMA_VERSION} schema. See L1 §3.2."
            ),
        ))
