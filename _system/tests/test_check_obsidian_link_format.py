"""AGENTS013 — obsidian-link-format.

The rule flags wikilinks that densa's suffix-matching resolver accepts
but Obsidian's vault-root-only resolver cannot: bucket-relative forms
like ``[[concepts/x]]``. Bare slugs and full vault paths are clean.
"""

from __future__ import annotations

from densa.checks.obsidian_link_format import ObsidianLinkFormat
from densa.report import Report, Severity
from densa.wikilink import build_index, obsidian_resolvable

from .conftest import MiniVault, make_wiki_page


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


class TestObsidianLinkFormat:
    rule_id = "AGENTS013"

    def test_bare_slug_is_clean(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(extra="See [[anxiety]].\n")
        mini_vault.write(path, text)
        report = Report()
        ObsidianLinkFormat().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_full_vault_path_is_clean(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(
            extra="See [[domains/psychology/wiki/concepts/anxiety|anxiety]].\n",
        )
        mini_vault.write(path, text)
        report = Report()
        ObsidianLinkFormat().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_bucket_relative_link_is_warning(
        self, mini_vault: MiniVault,
    ) -> None:
        """The hairball case: [[concepts/x]] resolves for densa (unique
        suffix) but not for Obsidian (no vault-root file concepts/x.md)."""
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(extra="See [[concepts/anxiety]].\n")
        mini_vault.write(path, text)
        report = Report()
        ObsidianLinkFormat().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert len(report.diagnostics) == 1
        diag = report.diagnostics[0]
        assert diag.rule_id == self.rule_id
        assert diag.severity is Severity.WARNING

    def test_alias_and_anchor_are_stripped(
        self, mini_vault: MiniVault,
    ) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(
            extra="See [[concepts/anxiety#triggers|the triggers]].\n",
        )
        mini_vault.write(path, text)
        report = Report()
        ObsidianLinkFormat().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == [self.rule_id]

    def test_missing_bare_slug_is_not_this_rules_problem(
        self, mini_vault: MiniVault,
    ) -> None:
        """A bare slug pointing nowhere is AGENTS006's diagnostic; the
        format rule stays silent (no '/' → Obsidian-compatible format)."""
        path = "domains/psychology/wiki/concepts/x.md"
        text = make_wiki_page(extra="See [[nothing-here]].\n")
        mini_vault.write(path, text)
        report = Report()
        ObsidianLinkFormat().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []

    def test_out_of_scope_file_is_skipped(self, mini_vault: MiniVault) -> None:
        path = "domains/psychology/raw/sessions/2026-01-01-session.md"
        text = "See [[concepts/anything]].\n"
        mini_vault.write(path, text)
        report = Report()
        ObsidianLinkFormat().visit(
            path, text, build_index(mini_vault.root), report,
        )
        assert _ids(report) == []


class TestObsidianResolvable:
    """Unit coverage for the predicate the rule (and the fix script)
    share."""

    def test_explicit_path_into_skipped_top_level(
        self, mini_vault: MiniVault,
    ) -> None:
        """[[_system/templates/concept]] resolves in Obsidian (real
        vault-root path) even though the suffix index skips _system/."""
        mini_vault.write("_system/templates/concept.md", "# template\n")
        idx = build_index(mini_vault.root)
        assert obsidian_resolvable("_system/templates/concept", idx)

    def test_md_extension_is_normalised(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        idx = build_index(mini_vault.root)
        assert obsidian_resolvable(
            "domains/psychology/wiki/concepts/anxiety.md", idx,
        )
        assert not obsidian_resolvable("concepts/anxiety.md", idx)

    def test_escaped_alias_separator(self, mini_vault: MiniVault) -> None:
        """Markdown-table escape ``\\|`` is treated as the alias cut."""
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        idx = build_index(mini_vault.root)
        assert not obsidian_resolvable("concepts/anxiety\\|焦虑", idx)
        assert obsidian_resolvable(
            "domains/psychology/wiki/concepts/anxiety\\|焦虑", idx,
        )
