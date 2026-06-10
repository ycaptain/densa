"""AGENTS005 — analysis sources cardinality.

A wiki page with ``type: analysis`` must list **exactly one** wikilink
under ``sources``, and that wikilink must resolve to a file under some
``raw/`` directory. The schema rationale (see
``docs/reference/sources-cardinality.md``): an analysis is a
1:1 contract between a raw source and its first-order LLM reading.
Anything multi-source is a synthesis and lives in ``wiki/syntheses/``;
anything that cites another wiki page (not raw) is also not an
analysis.
"""

from __future__ import annotations

from densa.frontmatter import parse
from densa.paths import is_raw, is_wiki
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import (
    WIKILINK_RE,
    ResolutionStatus,
    SlugIndex,
    resolve,
)


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

        match = WIKILINK_RE.search(items[0])
        if not match:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=1,
                message=(
                    f"analysis sources entry is not a wikilink: {items[0]}"
                ),
            ))
            return

        # Per docs/reference/sources-cardinality.md: analysis.sources
        # MUST point at a raw/ file.
        target = match.group(1)
        resolution = resolve(target, idx, source=path)
        if resolution.status != ResolutionStatus.OK:
            # AGENTS006 (wikilink-resolvable) already complains about
            # MISSING / AMBIGUOUS; don't double-report here.
            return
        if not any(is_raw(hit + ".md") for hit in resolution.hits):
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=1,
                message=(
                    f"analysis sources entry does not point to a raw/ file: "
                    f"{items[0]} -> {resolution.hits[0]}"
                ),
            ))
