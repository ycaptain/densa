"""AGENTS009 — compiled_against vs current SCHEMA_VERSION.

Per ``docs/reference/schema-versioning.md``, every wiki page declares ``compiled_against: <N>``
recording the L1 schema version it was authored under. When L1 bumps
to v2 (and so on), every existing page sits at ``compiled_against:
1`` until an explicit re-ingest migrates it forward.

This rule warns (does **not** block commits) when a page's
``compiled_against`` is below the current
:data:`~densa.config.SCHEMA_VERSION`. At v1 this is a no-op (the
intended steady state); the rule exists so v2 migrations have a
ready-made audit gate.

Missing ``compiled_against`` is left to AGENTS003 once that rule
includes it in the required-keys set; this rule treats missing as
silent so it doesn't double-report.
"""

from __future__ import annotations

from densa.config import SCHEMA_VERSION
from densa.frontmatter import parse
from densa.paths import is_wiki
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex

_RULE_ID = "AGENTS009"


class CompiledAgainstCurrent:
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

        raw = fm.get("compiled_against")
        if raw is None or raw == "":
            return  # AGENTS003 territory once the field is required
        try:
            version = int(str(raw).strip())
        except ValueError:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    f"AGENTS009 compiled-against-current: "
                    f"`compiled_against: {raw}` is not an integer"
                ),
            ))
            return

        if version < SCHEMA_VERSION:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    f"AGENTS009 compiled-against-current: page is "
                    f"compiled_against={version} but current "
                    f"SCHEMA_VERSION={SCHEMA_VERSION}; a re-ingest may "
                    f"be needed (see docs/reference/schema-versioning.md "
                    f"for the migration procedure)"
                ),
            ))
