"""Tests for AGENTS008 — last_validated freshness.

The rule warns (does not error) when `last_validated` on a
concept/framework/protocol/entity page is older than 180 days. Missing
or non-applicable types are silent. Malformed dates surface a separate
warning.
"""

from __future__ import annotations

from datetime import date, timedelta

from densa.checks.last_validated_stale import LastValidatedFresh
from densa.report import Report, Severity

_EMPTY_INDEX: dict[str, list[str]] = {}


def _page(page_type: str, last_validated: str) -> str:
    return (
        "---\n"
        f"type: {page_type}\n"
        "domain: x\n"
        "created: 2026-01-01\n"
        "updated: 2026-01-01\n"
        "status: active\n"
        f"last_validated: {last_validated}\n"
        "---\n# t\n"
    )


def _ids(report: Report) -> list[tuple[str, Severity]]:
    return [(d.rule_id, d.severity) for d in report.diagnostics]


class TestLastValidatedFresh:
    def test_skips_non_wiki_path(self) -> None:
        report = Report()
        LastValidatedFresh().visit(
            "_system/templates/concept.md",
            _page("concept", "2020-01-01"),
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []

    def test_skips_other_types(self) -> None:
        old = (date.today() - timedelta(days=400)).isoformat()
        report = Report()
        LastValidatedFresh().visit(
            "domains/x/wiki/syntheses/foo.md",
            _page("synthesis", old),
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []

    def test_recent_passes(self) -> None:
        recent = (date.today() - timedelta(days=10)).isoformat()
        report = Report()
        LastValidatedFresh().visit(
            "domains/x/wiki/concepts/foo.md",
            _page("concept", recent),
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []

    def test_stale_warns(self) -> None:
        stale = (date.today() - timedelta(days=200)).isoformat()
        report = Report()
        LastValidatedFresh().visit(
            "domains/x/wiki/concepts/foo.md",
            _page("concept", stale),
            _EMPTY_INDEX,
            report,
        )
        assert _ids(report) == [("AGENTS008", Severity.WARNING)]

    def test_malformed_date_warns(self) -> None:
        report = Report()
        LastValidatedFresh().visit(
            "domains/x/wiki/concepts/foo.md",
            _page("concept", "yesterday"),
            _EMPTY_INDEX,
            report,
        )
        assert _ids(report) == [("AGENTS008", Severity.WARNING)]

    def test_missing_silent(self) -> None:
        body = (
            "---\n"
            "type: concept\n"
            "domain: x\n"
            "created: 2026-01-01\n"
            "updated: 2026-01-01\n"
            "status: active\n"
            "---\n# t\n"
        )
        report = Report()
        LastValidatedFresh().visit(
            "domains/x/wiki/concepts/foo.md",
            body,
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []  # AGENTS003 territory once required
