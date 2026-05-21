"""AGENTS005 — analysis sources cardinality.

A wiki page with ``type: analysis`` must list **exactly one** wikilink
under ``sources``. The schema rationale (L1 §3.1): an analysis is a
1:1 contract between a raw source and its first-order LLM reading.
Anything multi-source is a synthesis and lives in ``wiki/syntheses/``.
"""

from __future__ import annotations

from wikilint.frontmatter import parse
from wikilint.paths import is_wiki
from wikilint.report import Diagnostic, Report, Severity
from wikilint.wikilink import WIKILINK_RE, SlugIndex


class AnalysisSourcesCardinality:
    id: str = "AGENTS005"

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
        if fm.get("type") != "analysis":
            return

        srcs = fm.get("sources")
        items: list[str]
        if isinstance(srcs, list):
            items = [str(item) for item in srcs]
        elif isinstance(srcs, str) and srcs:
            items = [srcs]
        else:
            items = []

        if len(items) != 1:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=1,
                message=(
                    f"type=analysis but sources has {len(items)} entries "
                    "(must be exactly 1)"
                ),
            ))
            return

        if not WIKILINK_RE.search(items[0]):
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=1,
                message=(
                    f"analysis sources entry is not a wikilink: {items[0]}"
                ),
            ))
