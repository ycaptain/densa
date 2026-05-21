"""End-to-end runner tests against a hermetic mini-vault."""

from __future__ import annotations

from wikilint.config import Config
from wikilint.runner import lint_all

from .conftest import MiniVault, make_wiki_page


def test_lint_all_clean_vault(mini_vault: MiniVault) -> None:
    mini_vault.write(
        "domains/psychology/wiki/concepts/anxiety.md",
        make_wiki_page(),
    )
    mini_vault.write(
        "domains/psychology/wiki/concepts/depression.md",
        make_wiki_page(extra="see also [[anxiety]]\n"),
    )
    report = lint_all(mini_vault.root)
    assert not report.has_errors
    # 2 wiki pages + the AGENTS.md root marker the fixture writes
    assert report.files_checked == 3


def test_lint_all_finds_unresolved_link(mini_vault: MiniVault) -> None:
    mini_vault.write(
        "domains/psychology/wiki/concepts/x.md",
        make_wiki_page(extra="see also [[ghost]]\n"),
    )
    report = lint_all(mini_vault.root)
    assert report.has_errors
    assert any(d.rule_id == "AGENTS006" for d in report.diagnostics)


def test_lint_all_with_ignore_drops_rule(mini_vault: MiniVault) -> None:
    mini_vault.write(
        "domains/psychology/wiki/concepts/x.md",
        make_wiki_page(extra="see also [[ghost]]\n"),
    )
    config = Config(ignore=frozenset({"AGENTS006"}))
    report = lint_all(mini_vault.root, config)
    assert not report.has_errors


def test_lint_all_with_select_runs_only_one_rule(
    mini_vault: MiniVault,
) -> None:
    mini_vault.write(
        "domains/psychology/wiki/analyses/x-analysis.md",
        make_wiki_page(type_="analysis", sources=["[[a]]", "[[b]]"]),
    )
    config = Config(select=frozenset({"AGENTS005"}))
    report = lint_all(mini_vault.root, config)
    rule_ids = {d.rule_id for d in report.diagnostics}
    assert rule_ids == {"AGENTS005"}


def test_analysis_with_one_source_is_clean(mini_vault: MiniVault) -> None:
    mini_vault.write(
        "domains/psychology/raw/sessions/2026-01-01-session.md",
        "# raw transcript",
    )
    mini_vault.write(
        "domains/psychology/wiki/analyses/x-analysis.md",
        make_wiki_page(
            type_="analysis",
            sources="[[2026-01-01-session]]",
        ),
    )
    config = Config(select=frozenset({"AGENTS005"}))
    report = lint_all(mini_vault.root, config)
    assert not report.has_errors
