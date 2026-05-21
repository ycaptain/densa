"""Tests for the new ``type: report`` page type and its frontmatter contract.

Reports live under ``outputs/<bucket>/`` (e.g. ``outputs/lint/<date>.md``)
and:

- Must declare the universal frontmatter keys (AGENTS003).
- Must use ``type: report`` (AGENTS004 rejects unknown types).
- May leave ``sources`` empty (§3.1).
- The bare ``outputs/README.md`` is exempt from both rules — it is
  human explanatory content, not an operation artifact.
"""

from __future__ import annotations

import pytest

from wikilint.checks.frontmatter_required import (
    FrontmatterRequiredKeys,
    FrontmatterTypeAllowed,
)
from wikilint.report import Report
from wikilint.wikilink import build_index

from .conftest import MiniVault


def _report_page(type_: str = "report", omit_status: bool = False) -> str:
    body = (
        "---\n"
        f"type: {type_}\n"
        "domain: vault\n"
        "created: 2026-05-19\n"
        "updated: 2026-05-19\n"
        "tags: [lint]\n"
    )
    if not omit_status:
        body += "status: active\n"
    body += "---\n# Lint report\n"
    return body


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


class TestReportFrontmatter:
    path = "outputs/lint/2026-05-19.md"

    def test_clean_report(self, mini_vault: MiniVault) -> None:
        mini_vault.write(self.path, _report_page())
        text = _report_page()
        report = Report()
        FrontmatterRequiredKeys().visit(
            self.path, text, build_index(mini_vault.root), report,
        )
        FrontmatterTypeAllowed().visit(
            self.path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_missing_status_is_error(self, mini_vault: MiniVault) -> None:
        text = _report_page(omit_status=True)
        mini_vault.write(self.path, text)
        report = Report()
        FrontmatterRequiredKeys().visit(
            self.path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == ["AGENTS003"]

    def test_unknown_type_is_error(self, mini_vault: MiniVault) -> None:
        text = _report_page(type_="bogus")
        mini_vault.write(self.path, text)
        report = Report()
        FrontmatterTypeAllowed().visit(
            self.path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == ["AGENTS004"]

    @pytest.mark.parametrize("path", [
        "outputs/snapshots/index-snapshot.md",
    ])
    def test_other_buckets_under_outputs_are_checked(
        self,
        mini_vault: MiniVault,
        path: str,
    ) -> None:
        text = _report_page()
        mini_vault.write(path, text)
        report = Report()
        FrontmatterRequiredKeys().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_outputs_readme_is_exempt(self, mini_vault: MiniVault) -> None:
        text = "# outputs/\n\nplain explanation, no frontmatter\n"
        mini_vault.write("outputs/README.md", text)
        report = Report()
        FrontmatterRequiredKeys().visit(
            "outputs/README.md",
            text,
            build_index(mini_vault.root),
            report,
        )
        FrontmatterTypeAllowed().visit(
            "outputs/README.md",
            text,
            build_index(mini_vault.root),
            report,
        )
        assert _ids(report) == []


def _qa_page() -> str:
    """A Q&A page under outputs/qa/ — same type/contract as lint reports
    but with `tags: [qa]` and a Q&A-specific body structure."""
    return (
        "---\n"
        "type: report\n"
        "domain: psy\n"
        "created: 2026-05-20\n"
        "updated: 2026-05-20\n"
        "sources: []\n"
        "tags: [qa]\n"
        "status: active\n"
        "---\n"
        "# Karpathy vs Yanhua on outputs/\n"
        "\n## Question\n\n…\n\n## Answer\n\n…\n"
    )


class TestQaFrontmatter:
    """`outputs/qa/` Q&A artifacts share the report contract."""

    path = "outputs/qa/2026-05-20-karpathy-vs-yanhua.md"

    def test_clean_qa_page(self, mini_vault: MiniVault) -> None:
        text = _qa_page()
        mini_vault.write(self.path, text)
        report = Report()
        FrontmatterRequiredKeys().visit(
            self.path, text, build_index(mini_vault.root), report,
        )
        FrontmatterTypeAllowed().visit(
            self.path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []
