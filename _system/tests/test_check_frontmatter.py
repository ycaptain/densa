"""Focused tests for AGENTS003 / AGENTS004 frontmatter rules.

`test_rules.py` already covers the happy path + a missing-key case
shared with other rules. This file adds the edge cases that get hit in
real-world use: malformed YAML, non-wiki paths the rule should skip,
output artifacts that ARE in scope, and the presence-only vs
required-with-value split introduced in T3.2.
"""

from __future__ import annotations

import pytest

from densa.checks.frontmatter_required import (
    FrontmatterRequiredKeys,
    FrontmatterTypeAllowed,
)
from densa.config import ALLOWED_TYPES
from densa.report import Report

from .conftest import MiniVault, make_wiki_page


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


_EMPTY_INDEX: dict[str, list[str]] = {}


class TestFrontmatterRequiredKeysScope:
    """The rule fires only for paths under domains/<X>/wiki/ or
    outputs/<bucket>/. Other markdown (raw, schema docs, prompts) is
    out of scope by design."""

    @pytest.mark.parametrize("path", [
        "domains/x/raw/sessions/2026-01-01.md",
        "_system/templates/concept.md",
        "_system/prompts/ingest.md",
        "AGENTS.md",
        "docs/setup.md",
        "inbox/dropped.md",
        "attic/legacy.md",
        "outputs/README.md",  # explicitly exempt
        "writing/drafts/foo.md",
    ])
    def test_out_of_scope_paths_skipped(
        self, mini_vault: MiniVault, path: str,
    ) -> None:
        text = "# no frontmatter at all\n"
        report = Report()
        FrontmatterRequiredKeys().visit(path, text, _EMPTY_INDEX, report)
        assert _ids(report) == [], (
            f"AGENTS003 fired on out-of-scope path: {path}"
        )

    @pytest.mark.parametrize("path", [
        "domains/x/wiki/concepts/foo.md",
        "outputs/lint/2026-05-19.md",
        "outputs/snapshots/index-snapshot.md",
        "outputs/qa/2026-05-19-foo.md",
    ])
    def test_in_scope_paths_required(
        self, mini_vault: MiniVault, path: str,
    ) -> None:
        text = "# no frontmatter at all\n"
        report = Report()
        FrontmatterRequiredKeys().visit(path, text, _EMPTY_INDEX, report)
        assert _ids(report) == ["AGENTS003"], (
            f"AGENTS003 did not fire on in-scope path: {path}"
        )


class TestFrontmatterRequiredKeysEdgeCases:
    path = "domains/x/wiki/concepts/foo.md"

    def test_legacy_path_is_exempt(self, mini_vault: MiniVault) -> None:
        """Files under wiki/.legacy/ are pre-redo snapshots that may
        legitimately violate the current schema."""
        legacy = "domains/x/wiki/.legacy/old-page.md"
        report = Report()
        FrontmatterRequiredKeys().visit(
            legacy, "# no frontmatter\n", _EMPTY_INDEX, report,
        )
        assert _ids(report) == []

    def test_no_frontmatter_block_errors(
        self, mini_vault: MiniVault,
    ) -> None:
        """A page lacking the leading ``---`` block at all surfaces a
        single "missing YAML frontmatter" diagnostic, not nine missing-key
        diagnostics."""
        text = "# just a heading, no frontmatter\nbody\n"
        report = Report()
        FrontmatterRequiredKeys().visit(
            self.path, text, _EMPTY_INDEX, report,
        )
        assert _ids(report) == ["AGENTS003"]
        assert "missing YAML frontmatter" in report.diagnostics[0].message

    def test_all_nine_keys_clean(self, mini_vault: MiniVault) -> None:
        report = Report()
        FrontmatterRequiredKeys().visit(
            self.path, make_wiki_page(), _EMPTY_INDEX, report,
        )
        assert _ids(report) == []

    def test_missing_compiled_against_errors(
        self, mini_vault: MiniVault,
    ) -> None:
        text = (
            "---\n"
            "type: concept\n"
            "domain: x\n"
            "created: 2026-01-01\n"
            "updated: 2026-01-01\n"
            "sources: []\n"
            "aliases: []\n"
            "tags: []\n"
            "status: active\n"
            "---\n# t\n"
        )
        report = Report()
        FrontmatterRequiredKeys().visit(
            self.path, text, _EMPTY_INDEX, report,
        )
        assert _ids(report) == ["AGENTS003"]


class TestFrontmatterTypeAllowedEdgeCases:
    path = "domains/x/wiki/concepts/foo.md"

    def test_all_l1_types_allowed(self, mini_vault: MiniVault) -> None:
        """Every type listed in AGENTS.md's "Frontmatter schema" must pass AGENTS004."""
        for t in ALLOWED_TYPES:
            text = make_wiki_page(type_=t)
            report = Report()
            FrontmatterTypeAllowed().visit(
                self.path, text, _EMPTY_INDEX, report,
            )
            assert _ids(report) == [], f"AGENTS004 rejected allowed type {t!r}"

    def test_missing_type_is_silent_here(
        self, mini_vault: MiniVault,
    ) -> None:
        """A page missing the `type:` key triggers AGENTS003, not
        AGENTS004 — the two rules don't double-report the same issue."""
        text = (
            "---\n"
            "domain: x\n"
            "created: 2026-01-01\n"
            "updated: 2026-01-01\n"
            "sources: []\n"
            "aliases: []\n"
            "tags: []\n"
            "status: active\n"
            "compiled_against: 1\n"
            "---\n# t\n"
        )
        report = Report()
        FrontmatterTypeAllowed().visit(
            self.path, text, _EMPTY_INDEX, report,
        )
        assert _ids(report) == []

    def test_unknown_type_message_names_type(
        self, mini_vault: MiniVault,
    ) -> None:
        text = make_wiki_page(type_="bogus-type-name")
        report = Report()
        FrontmatterTypeAllowed().visit(
            self.path, text, _EMPTY_INDEX, report,
        )
        assert len(report.diagnostics) == 1
        assert "bogus-type-name" in report.diagnostics[0].message
