"""AGENTS013 — wikilinks must use a format Obsidian can resolve.

Densa's resolver (:func:`densa.wikilink.resolve`) accepts any unique
path *suffix*, so a bucket-relative link like ``[[concepts/x]]`` lints
clean when ``domains/<d>/wiki/concepts/x.md`` exists. Obsidian's own
resolver does not do suffix matching: a link body containing ``/`` is
resolved from the vault root only. The result is a link that passes
AGENTS006 yet renders as a grey "ghost" node in Obsidian's graph and
404s on click.

This rule flags exactly that gap: any wikilink containing ``/`` that
is not a vault-root-relative path to a real file. The fix is either
the bare slug (``[[x]]``, preferred per AGENTS.md §"Naming and linking
conventions") or the full path with a display alias
(``[[domains/<d>/wiki/concepts/x|x]]``) when the basename is not
unique.

Severity is WARNING while existing vaults migrate their backlog
(``_system/scripts/fix_obsidian_links.py`` rewrites mechanically);
it is intended to become an ERROR once active vaults lint clean.

Scope mirrors AGENTS006 (:func:`~densa.paths.wikilinks_scoped`).
"""

from __future__ import annotations

from densa.paths import wikilinks_scoped
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex, obsidian_resolvable, scan


class ObsidianLinkFormat:
    id: str = "AGENTS013"

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
            if obsidian_resolvable(hit.target, idx):
                continue
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=hit.lineno,
                message=(
                    f"Obsidian cannot resolve [[{hit.target}]] — links "
                    f"containing '/' resolve from the vault root only; "
                    f"use the bare slug or the full path"
                ),
            ))
