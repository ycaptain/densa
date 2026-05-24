"""AGENTS003 / AGENTS004 — frontmatter required keys + allowed type.

Two separate rules because they have different cardinalities and one
might want to disable AGENTS004 alone (e.g. while shipping a migration
that introduces a new type).
"""

from __future__ import annotations

from densa.config import (
    ALLOWED_TYPES,
    PRESENCE_ONLY_FRONTMATTER_KEYS,
    REQUIRED_FRONTMATTER_KEYS,
)
from densa.frontmatter import parse
from densa.paths import is_output_artifact, is_wiki
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex


def _needs_frontmatter(path: str) -> bool:
    """Files subject to the universal frontmatter contract.

    Wiki pages under ``domains/<X>/wiki/`` and operation artifacts
    under ``outputs/<bucket>/`` (e.g. ``outputs/lint/<date>.md``) both
    carry the universal frontmatter. The bare ``outputs/README.md`` is
    exempt (see :func:`densa.paths.is_output_artifact`).
    """
    return is_wiki(path) or is_output_artifact(path)


class FrontmatterRequiredKeys:
    """Every wiki markdown file must declare the universal frontmatter."""

    id: str = "AGENTS003"

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None:
        if not _needs_frontmatter(path):
            return
        fm = parse(text)
        if fm is None:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=1,
                message="missing YAML frontmatter",
            ))
            return
        for key in REQUIRED_FRONTMATTER_KEYS:
            value = fm.get(key)
            if value is None or value == "" or value == []:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.ERROR,
                    path=path,
                    line=1,
                    message=f"missing required frontmatter key: {key}",
                ))
        for key in PRESENCE_ONLY_FRONTMATTER_KEYS:
            if key not in fm:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.ERROR,
                    path=path,
                    line=1,
                    message=(
                        f"missing universal frontmatter key: {key} "
                        f"(may be empty list, but key must be declared)"
                    ),
                ))


class FrontmatterTypeAllowed:
    """frontmatter ``type`` must be in :data:`ALLOWED_TYPES`."""

    id: str = "AGENTS004"

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None:
        if not _needs_frontmatter(path):
            return
        fm = parse(text)
        if fm is None:
            return
        t = fm.get("type")
        if isinstance(t, str) and t and t not in ALLOWED_TYPES:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=path,
                line=1,
                message=f"unknown type: {t}",
            ))
