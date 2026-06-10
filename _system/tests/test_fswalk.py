"""Tests for the shared vault walk (``densa.fswalk``).

Regression for the nested-git-repo flaw (found on a real vault that
keeps an upstream densa checkout inside itself, gitignored by the
vault): the slug index, ``densa --all`` file collection, and
``densa stats`` all descended into the nested checkout, producing
foreign-file AGENTS006 errors and slug-index pollution — a showcase
domain inside the nested repo shadowed the vault's own pages, so every
bare ``[[slug]]`` reported "ambiguous (2 matches)".

The contract under test: a subdirectory that carries its own ``.git``
entry (directory for ordinary clones, *file* for linked worktrees) is
pruned wholesale; the vault root's own ``.git`` never suppresses the
walk.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from densa.commands import stats as stats_cmd
from densa.fswalk import is_nested_repo_root, iter_markdown
from densa.runner import lint_all
from densa.wikilink import ResolutionStatus, build_index, resolve

from .conftest import make_wiki_page


def _make_vault_with_nested_repo(tmp_path: Path) -> Path:
    """A vault (own ``.git`` at the root) containing two nested repos.

    - ``vendor/upstream/`` — ordinary clone (``.git`` directory) with a
      duplicate-slug wiki page and an unresolvable wikilink.
    - ``vendor/worktree/`` — linked worktree (``.git`` *file*).
    """
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (tmp_path / "_system" / "densa").mkdir(parents=True)
    (tmp_path / ".git").mkdir()  # the vault root IS a repo — never pruned

    wiki = tmp_path / "domains" / "psychology" / "wiki" / "concepts"
    wiki.mkdir(parents=True)
    (wiki / "anxiety.md").write_text(
        make_wiki_page(extra="see [[anxiety]]\n"), encoding="utf-8",
    )

    nested = tmp_path / "vendor" / "upstream"
    nested_wiki = nested / "domains" / "psychology" / "wiki" / "concepts"
    nested_wiki.mkdir(parents=True)
    (nested / ".git").mkdir()
    # Same bare slug as the vault's own page → would make [[anxiety]]
    # ambiguous if the nested repo leaked into the slug index.
    (nested_wiki / "anxiety.md").write_text(
        make_wiki_page(), encoding="utf-8",
    )
    (nested_wiki / "foreign-only.md").write_text(
        make_wiki_page(extra="[[totally-unresolvable-placeholder]]\n"),
        encoding="utf-8",
    )

    worktree = tmp_path / "vendor" / "worktree"
    worktree.mkdir(parents=True)
    (worktree / ".git").write_text(
        "gitdir: /elsewhere/.git/worktrees/wt\n", encoding="utf-8",
    )
    (worktree / "page-in-worktree.md").write_text("x\n", encoding="utf-8")

    return tmp_path


# --- the predicate ----------------------------------------------------------


def test_is_nested_repo_root_git_dir(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    assert is_nested_repo_root(tmp_path)


def test_is_nested_repo_root_git_file(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
    assert is_nested_repo_root(tmp_path)


def test_is_nested_repo_root_plain_dir(tmp_path: Path) -> None:
    assert not is_nested_repo_root(tmp_path)


# --- the shared walk --------------------------------------------------------


def test_iter_markdown_prunes_nested_repos(tmp_path: Path) -> None:
    repo = _make_vault_with_nested_repo(tmp_path)
    rels = {str(rel).replace("\\", "/") for rel in iter_markdown(repo)}
    assert "domains/psychology/wiki/concepts/anxiety.md" in rels
    assert "AGENTS.md" in rels  # root's own .git does not suppress the walk
    assert not any(rel.startswith("vendor/") for rel in rels)


# --- slug index -------------------------------------------------------------


def test_slug_index_ignores_nested_repo(tmp_path: Path) -> None:
    repo = _make_vault_with_nested_repo(tmp_path)
    idx = build_index(repo)
    res = resolve("anxiety", idx)
    # One hit (the vault's own page), not ambiguous-with-the-nested-copy.
    assert res.status is ResolutionStatus.OK
    assert res.hits == ("domains/psychology/wiki/concepts/anxiety",)
    # A slug that exists only inside the nested repo is invisible.
    assert resolve("foreign-only", idx).status is ResolutionStatus.MISSING


# --- `densa --all` file collection ------------------------------------------


def test_lint_all_skips_nested_repo(tmp_path: Path) -> None:
    repo = _make_vault_with_nested_repo(tmp_path)
    report = lint_all(repo)
    checked_or_flagged = {d.path for d in report.diagnostics}
    assert not any(p.startswith("vendor/") for p in checked_or_flagged)
    # The unresolvable wikilink lives only in the nested repo → no
    # AGENTS006 anywhere.
    assert not any(d.rule_id == "AGENTS006" for d in report.diagnostics)


# --- stats ------------------------------------------------------------------


def test_stats_ignores_nested_repo(tmp_path: Path) -> None:
    repo = _make_vault_with_nested_repo(tmp_path)
    stats = stats_cmd.collect_stats(repo, today=date(2026, 6, 1))
    # Only the vault's own wiki page is counted — not the nested copy
    # or the nested foreign-only page.
    assert stats.total_pages == 1
    assert stats.by_domain == {"psychology": 1}
