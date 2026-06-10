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
from typing import ClassVar

import pytest

from densa.checks.frontmatter_required import FrontmatterRequiredKeys
from densa.report import Report

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


# --- presence-only key seeding (TK-0030) ----------------------------------


class TestSeedsPresenceOnlyKeys:
    """v1 pages routinely lack ``aliases`` (and sometimes ``sources`` /
    ``tags``); the migration must seed them as empty lists so the
    migrated vault passes AGENTS003."""

    @staticmethod
    def _v1_page_missing_presence_keys() -> str:
        # No aliases/sources/tags at all — the common v1 shape.
        return (
            "---\n"
            "type: analysis\n"
            "domain: research-papers\n"
            "created: 2024-01-01\n"
            "updated: 2024-01-01\n"
            "status: active\n"
            "compiled_against: 1\n"
            "---\n"
            "# Page\n"
        )

    def test_missing_keys_seeded_as_empty_lists(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        _write(
            domain / "wiki" / "analyses" / "2024-bare-analysis.md",
            self._v1_page_missing_presence_keys(),
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        page = domain / "wiki" / "summaries" / "2024-bare-summary.md"
        assert page.is_file()
        assert _frontmatter_value(page, "aliases") == "[]"
        assert _frontmatter_value(page, "sources") == "[]"
        assert _frontmatter_value(page, "tags") == "[]"

    def test_existing_keys_not_duplicated(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _run_script(tmp_path, "--apply", "--mode", "in-place")
        page = (
            tmp_path / "domains" / "research-papers" / "wiki"
            / "summaries" / "2024-foo-summary.md"
        )
        body = page.read_text(encoding="utf-8")
        # _v1_page already carries all three keys; no second copy.
        for key in ("aliases", "sources", "tags"):
            assert body.count(f"{key}:") == 1

    def test_migrated_page_passes_agents003(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        _write(
            domain / "wiki" / "analyses" / "2024-bare-analysis.md",
            self._v1_page_missing_presence_keys(),
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        report = Report()
        for md in (domain / "wiki").rglob("*.md"):
            rel = md.relative_to(tmp_path).as_posix()
            FrontmatterRequiredKeys().visit(
                rel, md.read_text(encoding="utf-8"), {}, report,
            )
        assert [d.rule_id for d in report.diagnostics] == []


# --- folder path segments in wikilinks (TK-0031) ---------------------------


class TestRewriteWikilinksInText:
    """Unit coverage for the folder-segment + slug rename composition."""

    FOLDERS: ClassVar[dict[str, str]] = {
        "questions": "open-questions",
        "analyses": "summaries",
    }
    SLUGS: ClassVar[dict[str, str]] = {
        "2024-foo-analysis": "2024-foo-summary",
    }

    @pytest.mark.parametrize("src,expected", [
        # Wiki-relative folder-prefixed links.
        ("[[questions/open-arc]]", "[[open-questions/open-arc]]"),
        ("[[questions/open-arc|the arc]]", "[[open-questions/open-arc|the arc]]"),
        ("[[questions/sub/open-arc]]", "[[open-questions/sub/open-arc]]"),
        # Full-path links: folder segment is the one right after wiki/.
        (
            "[[domains/psych/wiki/questions/open-arc]]",
            "[[domains/psych/wiki/open-questions/open-arc]]",
        ),
        # Folder rename + slug rename compose in one pass.
        (
            "[[domains/psych/wiki/analyses/2024-foo-analysis]]",
            "[[domains/psych/wiki/summaries/2024-foo-summary]]",
        ),
        ("[[analyses/2024-foo-analysis]]", "[[summaries/2024-foo-summary]]"),
        # Anchor + alias label preserved verbatim.
        (
            "[[analyses/2024-foo-analysis#sec|Foo]]",
            "[[summaries/2024-foo-summary#sec|Foo]]",
        ),
        # Bare slugs keep working (no folder segment at all).
        ("[[2024-foo-analysis]]", "[[2024-foo-summary]]"),
        # Unknown folder segment: left alone.
        ("[[customs/whatever]]", "[[customs/whatever]]"),
        # Candidate folder is the final segment → it is a slug, not a
        # folder; left to the slug map (which has no entry here).
        ("[[domains/psych/wiki/questions]]", "[[domains/psych/wiki/questions]]"),
    ])
    def test_rewrite(self, src: str, expected: str) -> None:
        assert mig._rewrite_wikilinks_in_text(src, self.SLUGS, self.FOLDERS) == expected


class TestFolderSegmentWikilinksEndToEnd:
    def test_wiki_relative_folder_links_rewritten(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        _write(
            domain / "wiki" / "syntheses" / "linker.md",
            _v1_page(
                "synthesis",
                "Track [[questions/open-arc]] and [[questions/open-arc|the arc]]\n",
            ),
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        body = (domain / "wiki" / "syntheses" / "linker.md").read_text(
            encoding="utf-8"
        )
        assert "[[open-questions/open-arc]]" in body
        assert "[[open-questions/open-arc|the arc]]" in body
        assert "[[questions/" not in body

    def test_full_path_links_folder_and_slug_compose(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        _write(
            domain / "wiki" / "syntheses" / "linker.md",
            _v1_page(
                "synthesis",
                "See [[domains/research-papers/wiki/analyses/2024-foo-analysis]]\n"
                "and [[domains/research-papers/wiki/questions/open-arc|Arc]]\n",
            ),
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        body = (domain / "wiki" / "syntheses" / "linker.md").read_text(
            encoding="utf-8"
        )
        assert (
            "[[domains/research-papers/wiki/summaries/2024-foo-summary]]" in body
        )
        assert (
            "[[domains/research-papers/wiki/open-questions/open-arc|Arc]]" in body
        )

    def test_log_md_links_rewritten(self, tmp_path: Path) -> None:
        """log.md follows the existing slug-rename precedent: a
        sanctioned migration retargets its links so they keep
        resolving."""
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        _write(
            domain / "log.md",
            "# Log\n\n"
            "## [2024-01-02] ingest | wrote "
            "[[domains/research-papers/wiki/analyses/2024-foo-analysis]]\n",
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place")

        body = (domain / "log.md").read_text(encoding="utf-8")
        assert (
            "[[domains/research-papers/wiki/summaries/2024-foo-summary]]" in body
        )

    def test_raw_files_never_rewritten(self, tmp_path: Path) -> None:
        """AGENTS001: raw/ sources are immutable, even for a migration."""
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        raw = domain / "raw" / "sessions" / "2024-01-01-foo.md"
        original = (
            "Mentions [[questions/open-arc]] and [[2024-foo-analysis]]\n"
        )
        _write(raw, original)
        _run_script(tmp_path, "--apply", "--mode", "in-place")
        assert raw.read_text(encoding="utf-8") == original

    def test_idempotent_with_folder_renames(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        domain = tmp_path / "domains" / "research-papers"
        _write(
            domain / "wiki" / "syntheses" / "linker.md",
            _v1_page("synthesis", "Track [[questions/open-arc]]\n"),
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place")
        before = sorted(
            (p.relative_to(tmp_path), p.read_text(encoding="utf-8"))
            for p in tmp_path.rglob("*.md")
        )
        _run_script(tmp_path, "--apply", "--mode", "in-place", "--force")
        after = sorted(
            (p.relative_to(tmp_path), p.read_text(encoding="utf-8"))
            for p in tmp_path.rglob("*.md")
        )
        assert before == after


# --- user-supplied --map (TK-0033) ------------------------------------------


def _build_custom_folder_vault(root: Path) -> Path:
    """v1 vault plus a custom ``skills/`` folder outside the rename
    table, with a page linking into it. Returns the domain dir."""
    _build_v1_vault(root)
    domain = root / "domains" / "research-papers"
    _write(
        domain / "wiki" / "skills" / "negotiation.md",
        _v1_page("skill"),
    )
    _write(
        domain / "wiki" / "syntheses" / "skill-linker.md",
        _v1_page("synthesis", "Builds on [[skills/negotiation]]\n"),
    )
    return domain


class TestMapOption:
    def test_map_moves_folder_and_rewrites_type(self, tmp_path: Path) -> None:
        domain = _build_custom_folder_vault(tmp_path)
        rc = _run_script(
            tmp_path, "--apply", "--mode", "in-place",
            "--map", "skills=concepts:concept",
        )
        assert rc == 0
        assert not (domain / "wiki" / "skills").exists()
        page = domain / "wiki" / "concepts" / "negotiation.md"
        assert page.is_file()
        assert _frontmatter_value(page, "type") == "concept"
        assert _frontmatter_value(page, "compiled_against") == "2"
        assert "type skill → concept" in page.read_text(encoding="utf-8")

    def test_map_rewrites_wikilinks(self, tmp_path: Path) -> None:
        domain = _build_custom_folder_vault(tmp_path)
        _run_script(
            tmp_path, "--apply", "--mode", "in-place",
            "--map", "skills=concepts:concept",
        )
        body = (domain / "wiki" / "syntheses" / "skill-linker.md").read_text(
            encoding="utf-8"
        )
        assert "[[concepts/negotiation]]" in body
        assert "[[skills/" not in body

    def test_map_without_type_keeps_type(self, tmp_path: Path) -> None:
        domain = _build_custom_folder_vault(tmp_path)
        _run_script(
            tmp_path, "--apply", "--mode", "in-place",
            "--map", "skills=concepts",
        )
        page = domain / "wiki" / "concepts" / "negotiation.md"
        assert page.is_file()
        # No :NEWTYPE → the (unknown) v1 type is left for the human.
        assert _frontmatter_value(page, "type") == "skill"

    def test_map_dry_run_shows_mapping(self, tmp_path: Path, capsys) -> None:
        domain = _build_custom_folder_vault(tmp_path)
        rc = _run_script(
            tmp_path, "--dry-run", "--mode", "in-place",
            "--map", "skills=concepts:concept",
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "(type -> concept)" in out
        assert "folder segment(s)" in out
        # Dry run: nothing moved.
        assert (domain / "wiki" / "skills" / "negotiation.md").is_file()

    @pytest.mark.parametrize("spec", [
        "skills",                  # no '='
        "=concepts",               # empty old folder
        "skills=",                 # empty new folder
        "skills=concepts:wizard",  # not a v2 page type
    ])
    def test_map_invalid_spec_exits_2(self, tmp_path: Path, spec: str) -> None:
        _build_custom_folder_vault(tmp_path)
        rc = _run_script(
            tmp_path, "--apply", "--mode", "in-place", "--map", spec,
        )
        assert rc == 2

    def test_map_recorded_in_log_marker(self, tmp_path: Path) -> None:
        _build_custom_folder_vault(tmp_path)
        _run_script(
            tmp_path, "--apply", "--mode", "in-place",
            "--map", "skills=concepts:concept",
        )
        log = tmp_path / "_system" / "migrations.log"
        body = log.read_text(encoding="utf-8")
        # A --map run must not be confused with a plain run (and vice
        # versa) by the idempotency guard.
        assert "map=skills=concepts:concept" in body


# --- migrations.log guard on direct invocation (TK-0032 counterpart) -------


class TestMigrationsLogGuard:
    def test_direct_run_honours_recorded_log(
        self, tmp_path: Path, capsys,
    ) -> None:
        """Hand-run scripts keep the log-based guard; only ``densa
        migrate`` (whose compiled_against scan is ground truth)
        bypasses it with --force."""
        _build_v1_vault(tmp_path)
        log = tmp_path / "_system" / "migrations.log"
        log.write_text(
            "2026-01-01  02_karpathy_vocab  mode=in-place  "
            "v1 → v2: Karpathy vocabulary\n",
            encoding="utf-8",
        )
        rc = _run_script(tmp_path, "--apply", "--mode", "in-place")
        assert rc == 0
        assert "nothing to do" in capsys.readouterr().out
        # Vault untouched: still v1-shaped.
        wiki = tmp_path / "domains" / "research-papers" / "wiki"
        assert (wiki / "analyses" / "2024-foo-analysis.md").is_file()


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


# --- _iter_domain_dirs --extra-roots --------------------------------------


def _build_showcase_v1(root: Path, name: str = "psychology") -> Path:
    """Seed an ``examples/showcases/<name>/`` directory with the same v1
    shape ``_build_v1_vault`` uses inside ``domains/<X>/``. Returns the
    showcase directory.
    """
    showcase = root / "examples" / "showcases" / name
    _write(
        showcase / "wiki" / "analyses" / "2024-session.md",
        _v1_page("analysis", "Refers to [[2024-session]]\n"),
    )
    _write(
        showcase / "wiki" / "patterns" / "automaton-mode.md",
        _v1_page("pattern"),
    )
    return showcase


class TestIterDomainDirsExtraRoots:
    def test_default_only_yields_domains(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _build_showcase_v1(tmp_path)
        yielded = list(mig._iter_domain_dirs(tmp_path))
        names = [d.name for d in yielded]
        # examples/showcases/ MUST NOT be yielded without --extra-roots.
        assert names == ["research-papers"]

    def test_extra_roots_yields_showcase_dirs(self, tmp_path: Path) -> None:
        _build_v1_vault(tmp_path)
        _build_showcase_v1(tmp_path, name="psychology")
        _build_showcase_v1(tmp_path, name="workspace")
        yielded = list(
            mig._iter_domain_dirs(tmp_path, ["examples/showcases"])
        )
        names = [d.name for d in yielded]
        # Sorted by enumerate order: domains/ first (research-papers),
        # then examples/showcases/ children in alphabetical order.
        assert names == ["research-papers", "psychology", "workspace"]

    def test_extra_roots_nonexistent_path_is_silently_skipped(
        self, tmp_path: Path,
    ) -> None:
        _build_v1_vault(tmp_path)
        # Pointing extra-roots at a non-existent path should not raise;
        # it should just be a no-op.
        yielded = list(
            mig._iter_domain_dirs(tmp_path, ["examples/nope"])
        )
        names = [d.name for d in yielded]
        assert names == ["research-papers"]

    def test_extra_roots_migrates_showcase_in_place(
        self, tmp_path: Path,
    ) -> None:
        _build_v1_vault(tmp_path)
        showcase = _build_showcase_v1(tmp_path, name="psychology")
        rc = _run_script(
            tmp_path,
            "--apply", "--mode", "in-place",
            "--extra-roots", "examples/showcases",
        )
        assert rc == 0

        # The showcase wiki was migrated: analyses/ -> summaries/ +
        # *-analysis -> *-summary rename + compiled_against bumped.
        sc_wiki = showcase / "wiki"
        assert not (sc_wiki / "analyses").exists()
        assert (sc_wiki / "summaries" / "2024-session.md").is_file()

        page = sc_wiki / "summaries" / "2024-session.md"
        assert _frontmatter_value(page, "type") == "summary"
        assert _frontmatter_value(page, "compiled_against") == "2"
        assert _has_migration_history(page)

    def test_extra_roots_records_distinct_log_marker(
        self, tmp_path: Path,
    ) -> None:
        _build_v1_vault(tmp_path)
        _build_showcase_v1(tmp_path, name="psychology")
        _run_script(
            tmp_path,
            "--apply", "--mode", "in-place",
            "--extra-roots", "examples/showcases",
        )
        log = tmp_path / "_system" / "migrations.log"
        assert log.is_file()
        body = log.read_text(encoding="utf-8")
        # The marker for an extra-roots run must include the roots so a
        # subsequent default run is not falsely short-circuited.
        assert "mode=in-place  extra-roots=examples/showcases" in body

    def test_extra_roots_overview_dataview_from_uses_correct_root(
        self, tmp_path: Path,
    ) -> None:
        """Regression: when a showcase domain is migrated via
        ``--extra-roots``, the seeded ``overview.md`` must reference
        the showcase root (``examples/showcases/<x>/...``), not the
        default ``domains/<x>/...``. Without this fix Obsidian
        Dataview blocks would silently render empty in showcase
        domains.
        """
        _build_v1_vault(tmp_path)
        _build_showcase_v1(tmp_path, name="psychology")
        _run_script(
            tmp_path,
            "--apply", "--mode", "in-place",
            "--extra-roots", "examples/showcases",
        )

        # The domains/ overview should still point at domains/<x>/...
        domains_overview = (
            tmp_path / "domains" / "research-papers" / "wiki" / "overview.md"
        )
        assert domains_overview.is_file()
        domains_body = domains_overview.read_text(encoding="utf-8")
        assert 'FROM "domains/research-papers/wiki' in domains_body
        assert 'FROM "examples/showcases/research-papers' not in domains_body

        # The showcase overview must point at examples/showcases/<x>/...
        showcase_overview = (
            tmp_path / "examples" / "showcases" / "psychology"
            / "wiki" / "overview.md"
        )
        assert showcase_overview.is_file()
        body = showcase_overview.read_text(encoding="utf-8")
        assert 'FROM "examples/showcases/psychology/wiki' in body
        assert 'FROM "domains/psychology' not in body
        # dataviewjs log.md load should also use the showcase root.
        assert 'dv.io.load("examples/showcases/psychology/log.md"' in body
