"""AGENTS006 — every wikilink must resolve.

A missing target is an ERROR; an ambiguous target (multiple files
share the same shortest-unique slug) is a WARNING — Obsidian will pick
one of them at render time so the link still works, but the
ambiguity is a maintenance smell worth surfacing.

The set of files this rule examines is :func:`~densa.paths.wikilinks_scoped`:
canonical markdown content (domains, root index/log), excluding
schema docs (AGENTS, templates, prompts) and ``raw/``.
"""

from __future__ import annotations

from densa.paths import wikilinks_scoped
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import ResolutionStatus, SlugIndex, resolve, scan


class WikilinkResolvable:
    id: str = "AGENTS006"

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None:
        if not wikilinks_scoped(path):
            return
        for hit in scan(text):
            resolution = resolve(hit.target, idx)
            if resolution.status is ResolutionStatus.MISSING:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.ERROR,
                    path=path,
                    line=hit.lineno,
                    message=f"unresolved wikilink: [[{hit.target}]]",
                ))
            elif resolution.status is ResolutionStatus.AMBIGUOUS:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.WARNING,
                    path=path,
                    line=hit.lineno,
                    message=(
                        f"ambiguous wikilink [[{hit.target}]] "
                        f"({len(resolution.hits)} matches)"
                    ),
                ))
