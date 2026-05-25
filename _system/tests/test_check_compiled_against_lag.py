"""Tests for AGENTS009 — compiled_against vs SCHEMA_VERSION.

AGENTS009 (this rule) warns when a page lags the current
SCHEMA_VERSION; AGENTS010 (``schema_version_consistency``) escalates
to error when the lagging page lives outside ``.legacy/``. Tests pin
the contract independently of the current SCHEMA_VERSION value so
schema bumps don't require touching them.
"""

from __future__ import annotations

from densa.checks.compiled_against_lag import CompiledAgainstCurrent
from densa.config import SCHEMA_VERSION
from densa.report import Report, Severity

_EMPTY_INDEX: dict[str, list[str]] = {}


def _page(compiled_against: object) -> str:
    return (
        "---\n"
        "type: concept\n"
        "domain: x\n"
        "created: 2026-01-01\n"
        "updated: 2026-01-01\n"
        "status: active\n"
        f"compiled_against: {compiled_against}\n"
        "---\n# t\n"
    )


def _ids(report: Report) -> list[tuple[str, Severity]]:
    return [(d.rule_id, d.severity) for d in report.diagnostics]


class TestCompiledAgainstCurrent:
    def test_current_passes(self) -> None:
        report = Report()
        CompiledAgainstCurrent().visit(
            "domains/x/wiki/concepts/foo.md",
            _page(SCHEMA_VERSION),
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []

    def test_lagged_warns(self) -> None:
        report = Report()
        CompiledAgainstCurrent().visit(
            "domains/x/wiki/concepts/foo.md",
            _page(SCHEMA_VERSION - 1),
            _EMPTY_INDEX,
            report,
        )
        assert _ids(report) == [("AGENTS009", Severity.WARNING)]

    def test_non_integer_warns(self) -> None:
        report = Report()
        CompiledAgainstCurrent().visit(
            "domains/x/wiki/concepts/foo.md",
            _page("not-a-number"),
            _EMPTY_INDEX,
            report,
        )
        assert _ids(report) == [("AGENTS009", Severity.WARNING)]

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
        CompiledAgainstCurrent().visit(
            "domains/x/wiki/concepts/foo.md",
            body,
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []

    def test_non_wiki_skipped(self) -> None:
        report = Report()
        CompiledAgainstCurrent().visit(
            "_system/templates/concept.md",
            _page(0),
            _EMPTY_INDEX,
            report,
        )
        assert report.diagnostics == []
