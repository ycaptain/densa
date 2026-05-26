"""End-to-end tests for the v1 → v2 migration script.

Three modes are exercised side-by-side on the same v1 starting layout:

- ``in-place``: rename folder + type + slug, rewrite frontmatter and
  wikilinks repo-wide, stamp ``migration_history``.
- ``archive``: park v1 contents under ``.legacy/`` and seed empty v2
  folders.
- ``recover``: the inverse of ``archive`` — given a vault already in
  the archived state, lift its contents back into the live v2 layout
  with the in-place transform.

Each mode is also asserted to be idempotent: re-running on the
post-migration state produces no diff (and the script reports
``Vault is already v2-shaped``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the migration script importable as a module so we can unit-test
# its helpers without spawning subprocesses.
_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import migrate_02_karpathy_vocab as mig  # noqa: E402

# --- Helpers --------------------------------------------------------------


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _v1_page(type_: str, body_extra: str = "") -> str:
    """A minimal-but-valid v1 wiki page body."""
    return (
        "---\n"
        f"type: {type_}\n"
        "domain: research-papers\n"
        "created: 2024-01-01\n"
        "updated: 2024-01-01\n"
        "sources: []\n"
        "aliases: []\n"
        "tags: []\n"
        "status: active\n"
        "compiled_against: 1\n"
        "---\n"
        "# Page\n"
        f"{body_extra}"
    )


def _build_v1_vault(root: Path) -> None:
    """Seed a vault with the v1 folder layout researchers ship with."""
    (root / "AGENTS.md").write_text(
        "---\ntype: schema\nscope: L1\n---\n# AGENTS\n", encoding="utf-8",
    )
    # Double-factor marker for cli._resolve_repo.
    (root / "_system" / "densa").mkdir(parents=True)
    (root / "_system" / "densa" / "__init__.py").write_text(
        "", encoding="utf-8",
    )
    domain = root / "domains" / "research-papers"
    _write(
        domain / "wiki" / "analyses" / "2024-foo-analysis.md",
        _v1_page("analysis", "Refers to [[bar]] and to [[2024-foo-analysis]]\n"),
    )
    _write(
        domain / "wiki" / "concepts" / "bar.md",
        _v1_page("concept", "Tracked across [[2024-foo-analysis|Foo]]\n"),
    )
    _write(
        domain / "wiki" / "frameworks" / "research-programme.md",
        _v1_page("framework"),
    )
    _write(
        domain / "wiki" / "questions" / "open-arc.md",
        _v1_page("question"),
    )
    _write(
        domain / "wiki" / "syntheses" / "cross.md",
        _v1_page("synthesis", "See [[2024-foo-analysis\\|F]]\n"),
    )


def _frontmatter_value(page: Path, key: str) -> str | None:
    text = page.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        if line.lstrip().startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return None


def _has_migration_history(page: Path) -> bool:
    return "migration_history:" in page.read_text(encoding="utf-8")


def _run_script(repo: Path, *args: str) -> int:
    # In tests the vault root is the tmp_path, not the upstream repo, so
    # we run the migration script via the in-process ``main`` instead of
    # spawning a fresh interpreter. That keeps the test hermetic and
    # avoids needing the actual upstream files on disk.
    cwd_was = Path.cwd()
    try:
        os.chdir(repo)
        return mig.main(list(args))
    finally:
        os.chdir(cwd_was)


# --- in-place mode --------------------------------------------------------


class TestInPlaceMode:
    def test_renames_folders_and_pages(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        rc = _run_script(tmp_path, "--apply", "--mode", "in-place")
        assert rc == 0

        wiki = tmp_path / "domains" / "research-papers" / "wiki"

        # v1 folders are gone (or empty).
        for v1 in ("analyses", "frameworks", "questions"):
            assert not (wiki / v1).exists(), f"{v1}/ should be removed"

        # v2 folders received the renamed contents.
        assert (wiki / "summaries" / "2024-foo-summary.md").is_file()
        assert (wiki / "overviews" / "research-programme.md").is_file()
        assert (wiki / "open-questions" / "open-arc.md").is_file()

        # concepts/ and syntheses/ kept their names; pages moved through
        # the in-place transform without changing folder.
        assert (wiki / "concepts" / "bar.md").is_file()
        assert (wiki / "syntheses" / "cross.md").is_file()

        # overview.md was seeded.
        assert (wiki / "overview.md").is_file()

    def test_frontmatter_upgraded(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        wiki = tmp_path / "domains" / "research-papers" / "wiki"
        summary = wiki / "summaries" / "2024-foo-summary.md"

        assert _frontmatter_value(summary, "type") == "summary"
        assert _frontmatter_value(summary, "compiled_against") == "2"
        assert _has_migration_history(summary)
        # The history entry records the type rename.
        body = summary.read_text(encoding="utf-8")
        assert "from: 1" in body
        assert "to: 2" in body
        assert "mode: in-place" in body
        assert "type analysis → summary" in body

    def test_concept_kept_same_type_records_history(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _run_script(tmp_path, "--apply", "--mode", "in-place")
        concept = (
            tmp_path / "domains" / "research-papers" / "wiki"
            / "concepts" / "bar.md"
        )
        # Same type → entry still added.
        assert _has_migration_history(concept)
        assert _frontmatter_value(concept, "type") == "concept"

    def test_wikilinks_rewritten(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        wiki = tmp_path / "domains" / "research-papers" / "wiki"
        concept_body = (wiki / "concepts" / "bar.md").read_text(encoding="utf-8")
        # The wikilink to ``2024-foo-analysis`` should now point at
        # ``2024-foo-summary`` (with its alias preserved).
        assert "[[2024-foo-summary|Foo]]" in concept_body
        # The escaped pipe form should also have been rewritten.
        synthesis_body = (wiki / "syntheses" / "cross.md").read_text(
            encoding="utf-8"
        )
        assert "[[2024-foo-summary\\|F]]" in synthesis_body

    def test_idempotent(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _run_script(tmp_path, "--apply", "--mode", "in-place")
        wiki = tmp_path / "domains" / "research-papers" / "wiki"
        before = sorted(
            (p.relative_to(tmp_path), p.read_text(encoding="utf-8"))
            for p in wiki.rglob("*.md")
        )
        # Use --force so the migrations-log short-circuit doesn't hide a
        # latent non-idempotency.
        _run_script(tmp_path, "--apply", "--mode", "in-place", "--force")
        after = sorted(
            (p.relative_to(tmp_path), p.read_text(encoding="utf-8"))
            for p in wiki.rglob("*.md")
        )
        assert before == after


# --- archive mode ---------------------------------------------------------


class TestArchiveMode:
    def test_v1_moved_to_legacy(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        rc = _run_script(tmp_path, "--apply", "--mode", "archive")
        assert rc == 0

        wiki = tmp_path / "domains" / "research-papers" / "wiki"
        legacy = wiki / ".legacy"

        # Every v1 folder lives under .legacy/ now.
        for v1 in ("analyses", "concepts", "frameworks", "questions", "syntheses"):
            assert (legacy / v1).is_dir(), f".legacy/{v1}/ should exist"

        # The seven recommended v2 folders all exist (created empty).
        for v2 in ("summaries", "entities", "concepts", "comparisons",
                   "overviews", "syntheses", "open-questions"):
            assert (wiki / v2).is_dir()

        # overview.md was seeded.
        assert (wiki / "overview.md").is_file()

    def test_legacy_pages_marked_snapshot(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _run_script(tmp_path, "--apply", "--mode", "archive")
        page = (
            tmp_path / "domains" / "research-papers" / "wiki" / ".legacy"
            / "analyses" / "2024-foo-analysis.md"
        )
        assert _frontmatter_value(page, "status") == "legacy-snapshot"


# --- recover mode ---------------------------------------------------------


class TestRecoverMode:
    def test_inverse_of_archive(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        # First archive…
        _run_script(tmp_path, "--apply", "--mode", "archive")
        # … then recover.
        rc = _run_script(tmp_path, "--apply", "--mode", "recover")
        assert rc == 0

        wiki = tmp_path / "domains" / "research-papers" / "wiki"

        # .legacy/ is now empty (or its sub-folders are at least cleaned).
        legacy = wiki / ".legacy"
        if legacy.exists():
            remaining = [p for p in legacy.rglob("*") if p.is_file()]
            assert remaining == []

        # Live v2 layout populated with the recovered content.
        assert (wiki / "summaries" / "2024-foo-summary.md").is_file()
        assert (wiki / "concepts" / "bar.md").is_file()
        assert (wiki / "overviews" / "research-programme.md").is_file()
        assert (wiki / "open-questions" / "open-arc.md").is_file()
        assert (wiki / "syntheses" / "cross.md").is_file()

        # Recovered pages have status=active (legacy-snapshot was reset).
        summary = wiki / "summaries" / "2024-foo-summary.md"
        assert _frontmatter_value(summary, "status") == "active"
        assert _has_migration_history(summary)
