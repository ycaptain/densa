"""Per-rule unit tests.

Each rule gets a class with two kinds of tests:

- ``test_clean_*`` — happy-path inputs that should produce no diagnostics.
- ``test_dirty_*`` — inputs that should produce exactly the expected
  diagnostic IDs.

We assert on rule IDs rather than on message strings, so wording can
evolve without breaking tests.
"""

from __future__ import annotations

import pytest

from wikilint.checks.analysis_sources import AnalysisSourcesCardinality
from wikilint.checks.frontmatter_required import (
    FrontmatterRequiredKeys,
    FrontmatterTypeAllowed,
)
from wikilint.checks.wikilink_resolvable import WikilinkResolvable
from wikilint.config import ALLOWED_TYPES
from wikilint.report import Report, Severity
from wikilint.wikilink import build_index

from .conftest import MiniVault, make_wiki_page


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


class TestFrontmatterRequiredKeys:
    rule_id = "AGENTS003"

    def test_clean(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/concepts/x.md"
        mini_vault.write(path, make_wiki_page())
        report = Report()
        FrontmatterRequiredKeys().visit(
            path, make_wiki_page(), build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_missing_frontmatter_entirely(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/concepts/x.md"
        text = "# no frontmatter\n"
        report = Report()
        FrontmatterRequiredKeys().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == [self.rule_id]

    def test_missing_required_key(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/concepts/x.md"
        text = (
            "---\n"
            "type: concept\n"
            "domain: psychology\n"
            "created: 2026-01-01\n"
            "updated: 2026-01-01\n"
            "---\n"  # missing status
        )
        report = Report()
        FrontmatterRequiredKeys().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == [self.rule_id]


class TestFrontmatterTypeAllowed:
    rule_id = "AGENTS004"

    def test_clean(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(type_="concept")
        report = Report()
        FrontmatterTypeAllowed().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_unknown_type(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(type_="totally-made-up")
        report = Report()
        FrontmatterTypeAllowed().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == [self.rule_id]
        message = report.diagnostics[0].message
        assert "unknown type: totally-made-up" in message
        for type_ in ALLOWED_TYPES:
            assert type_ in message


class TestAnalysisSourcesCardinality:
    rule_id = "AGENTS005"

    def test_clean(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/analyses/x-analysis.md"
        text = make_wiki_page(type_="analysis", sources="[[the-raw]]")
        report = Report()
        AnalysisSourcesCardinality().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    @pytest.mark.parametrize("sources,expected_count", [
        ([], 0),
        (["[[a]]", "[[b]]"], 2),
    ])
    def test_wrong_cardinality(
        self,
        mini_vault: MiniVault,
        sources: list[str],
        expected_count: int,
    ) -> None:
        path = "domains/psychology/wiki/analyses/x-analysis.md"
        text = make_wiki_page(type_="analysis", sources=sources or None)
        report = Report()
        AnalysisSourcesCardinality().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == [self.rule_id]

    def test_non_wikilink(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/analyses/x-analysis.md"
        text = make_wiki_page(
            type_="analysis", sources="plain-string-not-a-wikilink",
        )
        report = Report()
        AnalysisSourcesCardinality().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == [self.rule_id]


class TestWikilinkResolvable:
    rule_id = "AGENTS006"

    def test_clean(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md",
            make_wiki_page(),
        )
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(extra="See [[anxiety]] for more.\n")
        mini_vault.write(path, text)
        report = Report()
        WikilinkResolvable().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_unresolved_link_is_error(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(extra="See [[nothing-here]] now.\n")
        mini_vault.write(path, text)
        report = Report()
        WikilinkResolvable().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert len(report.diagnostics) == 1
        diag = report.diagnostics[0]
        assert diag.rule_id == self.rule_id
        assert diag.severity is Severity.ERROR

    def test_ambiguous_link_is_warning(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/dup.md", make_wiki_page(),
        )
        mini_vault.write(
            "domains/research-papers/wiki/concepts/dup.md", make_wiki_page(),
        )
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(extra="See [[dup]] for more.\n")
        mini_vault.write(path, text)
        report = Report()
        WikilinkResolvable().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert len(report.diagnostics) == 1
        diag = report.diagnostics[0]
        assert diag.rule_id == self.rule_id
        assert diag.severity is Severity.WARNING
