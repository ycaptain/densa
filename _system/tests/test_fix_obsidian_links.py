"""Tests for ``_system/scripts/fix_obsidian_links.py``.

The script clears the AGENTS013 backlog: bucket-relative wikilinks
(``[[concepts/x]]``) are retargeted to forms Obsidian can resolve —
the bare slug when unique, the full vault path with alias otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

from densa.checks.obsidian_link_format import ObsidianLinkFormat
from densa.report import Report
from densa.wikilink import build_index

from .conftest import MiniVault, make_wiki_page

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import fix_obsidian_links as fix  # noqa: E402


def _run(vault: MiniVault, *, apply: bool = True, fuzzy: bool = False):
    return fix.run_fix(vault.root, apply=apply, fuzzy=fuzzy)


class TestRewrites:
    def test_unique_basename_becomes_bare_slug(
        self, mini_vault: MiniVault,
    ) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/psychology/wiki/concepts/x.md",
            make_wiki_page(extra="See [[concepts/anxiety]].\n"),
        )
        out = _run(mini_vault)
        assert [r.new for r in out.rewrites] == ["anxiety"]
        assert "[[anxiety]]" in page.read_text(encoding="utf-8")

    def test_colliding_basename_becomes_full_path_with_alias(
        self, mini_vault: MiniVault,
    ) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/dup.md", make_wiki_page(),
        )
        mini_vault.write(
            "domains/career/wiki/concepts/dup.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/psychology/wiki/concepts/x.md",
            make_wiki_page(extra="See [[concepts/dup]].\n"),
        )
        _run(mini_vault)
        # Same-domain preference picks the psychology candidate; the
        # collision forces the full-path + alias form.
        assert (
            "[[domains/psychology/wiki/concepts/dup|dup]]"
            in page.read_text(encoding="utf-8")
        )

    def test_anchor_and_alias_are_preserved(
        self, mini_vault: MiniVault,
    ) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/psychology/wiki/concepts/x.md",
            make_wiki_page(extra="See [[concepts/anxiety#triggers|焦虑]].\n"),
        )
        _run(mini_vault)
        assert "[[anxiety#triggers|焦虑]]" in page.read_text(encoding="utf-8")

    def test_frontmatter_sources_are_rewritten(
        self, mini_vault: MiniVault,
    ) -> None:
        """`sources:` wikilinks live in frontmatter lines and are
        covered by the same text pass."""
        mini_vault.write(
            "domains/psychology/raw/sessions/2026-01-01-session.md",
            "# raw\n",
        )
        page = mini_vault.write(
            "domains/psychology/wiki/summaries/2026-01-01-session-summary.md",
            make_wiki_page(
                type_="summary", sources="[[sessions/2026-01-01-session]]",
            ),
        )
        _run(mini_vault)
        assert (
            'sources: ["[[2026-01-01-session]]"]'
            in page.read_text(encoding="utf-8")
        )

    def test_fuzzy_retargets_stale_bucket_prefix(
        self, mini_vault: MiniVault,
    ) -> None:
        """[[skills/x]] for a page living in concepts/ has no suffix
        match; only --fuzzy retargets it via the unique basename."""
        mini_vault.write(
            "domains/career/wiki/concepts/platform-eng.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/career/wiki/concepts/x.md",
            make_wiki_page(extra="See [[skills/platform-eng]].\n"),
        )
        out = _run(mini_vault, fuzzy=False)
        assert out.rewrites == []
        assert [s.reason for s in out.skips] == ["missing"]

        out = _run(mini_vault, fuzzy=True)
        assert [r.fuzzy for r in out.rewrites] == [True]
        assert "[[platform-eng]]" in page.read_text(encoding="utf-8")

    def test_ambiguous_suffix_is_skipped(self, mini_vault: MiniVault) -> None:
        """Two candidates in *other* domains: no same-domain tiebreak,
        so the link is reported, not guessed."""
        mini_vault.write(
            "domains/psychology/wiki/concepts/dup.md", make_wiki_page(),
        )
        mini_vault.write(
            "domains/career/wiki/concepts/dup.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/people/wiki/concepts/x.md",
            make_wiki_page(extra="See [[concepts/dup]].\n"),
        )
        before = page.read_text(encoding="utf-8")
        out = _run(mini_vault)
        assert [s.reason for s in out.skips] == ["ambiguous"]
        assert page.read_text(encoding="utf-8") == before


class TestScopeAndSafety:
    def test_raw_and_log_are_never_touched(
        self, mini_vault: MiniVault,
    ) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        raw = mini_vault.write(
            "domains/psychology/raw/sessions/2026-01-01-session.md",
            "See [[concepts/anxiety]].\n",
        )
        log = mini_vault.write(
            "domains/psychology/log.md",
            "## [2026-01-01] ingest | [[concepts/anxiety]]\n",
        )
        out = _run(mini_vault)
        assert out.changed_files == []
        assert "[[concepts/anxiety]]" in raw.read_text(encoding="utf-8")
        assert "[[concepts/anxiety]]" in log.read_text(encoding="utf-8")

    def test_code_fences_and_inline_code_are_skipped(
        self, mini_vault: MiniVault,
    ) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/psychology/wiki/concepts/x.md",
            make_wiki_page(extra=(
                "```\n[[concepts/anxiety]]\n```\n"
                "Inline `[[concepts/anxiety]]` stays.\n"
            )),
        )
        out = _run(mini_vault)
        assert out.rewrites == []
        text = page.read_text(encoding="utf-8")
        assert text.count("[[concepts/anxiety]]") == 2

    def test_dry_run_writes_nothing(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        page = mini_vault.write(
            "domains/psychology/wiki/concepts/x.md",
            make_wiki_page(extra="See [[concepts/anxiety]].\n"),
        )
        before = page.read_text(encoding="utf-8")
        out = _run(mini_vault, apply=False)
        assert len(out.rewrites) == 1
        assert page.read_text(encoding="utf-8") == before

    def test_idempotent(self, mini_vault: MiniVault) -> None:
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        mini_vault.write(
            "domains/psychology/wiki/concepts/x.md",
            make_wiki_page(extra="See [[concepts/anxiety]].\n"),
        )
        first = _run(mini_vault)
        assert len(first.rewrites) == 1
        second = _run(mini_vault)
        assert second.rewrites == []
        assert second.changed_files == []

    def test_fix_clears_agents013(self, mini_vault: MiniVault) -> None:
        """End-to-end contract: after --apply, the AGENTS013 rule is
        silent on the fixed page."""
        mini_vault.write(
            "domains/psychology/wiki/concepts/anxiety.md", make_wiki_page(),
        )
        page_rel = "domains/psychology/wiki/concepts/x.md"
        page = mini_vault.write(
            page_rel,
            make_wiki_page(extra="See [[concepts/anxiety]].\n"),
        )
        _run(mini_vault)
        report = Report()
        ObsidianLinkFormat().visit(
            page_rel,
            page.read_text(encoding="utf-8"),
            build_index(mini_vault.root),
            report,
        )
        assert report.diagnostics == []
