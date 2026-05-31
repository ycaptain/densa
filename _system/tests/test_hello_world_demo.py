"""T018 — Demo reproducibility guard for ``examples/hello-world/``.

The hello-world demo is the first thing a stranger reads, and the
README + storyboard SVG make hard structural promises about it:

    one 1-page source  →  1 summary + 2 concept pages + 1 log entry
    ("touch 4 pages", "concept (x2)")

Nothing erodes a trending repo's credibility faster than "I followed
the demo and got a different result." But the example lives under
``examples/`` — which is in :data:`densa.config.WIKILINK_SKIP_TOP_LEVEL`,
so ``densa --all`` walks the files yet **does not** enforce wiki schema
or wikilink resolvability on them (verified: ``paths.is_wiki`` is False
for every ``expected-wiki/`` path). This test is therefore the *only*
guard that the demo stays internally consistent and matches the counts
the README / SVG advertise.

Since Densa makes no LLM calls, "replay" is a deterministic proxy
(per T018's decision): the expected-wiki must be schema-valid,
internally cross-linked both directions, and structurally match what
the README and storyboard claim. The proxy catches every drift a
viewer would notice; we cannot re-run the agent in CI.

The assertions reuse densa's own library (``schema``, ``frontmatter``,
``wikilink``) so the guard tracks the contract rather than freezing a
private copy of it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from densa import frontmatter, wikilink
from densa.config import (
    PRESENCE_ONLY_FRONTMATTER_KEYS,
    REQUIRED_FRONTMATTER_KEYS,
)
from densa.schema import ALLOWED_TYPES, SCHEMA_VERSION

# --- The demo contract (mirror of the README + storyboard promises) -------

REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO = REPO_ROOT / "examples" / "hello-world"
WIKI = DEMO / "expected-wiki"

# One source page distils into exactly these wiki pages. The README's
# "Why these four pages" section and the SVG's "+ concept (x2)" both
# encode this shape; if it changes, both must change with it.
SUMMARY_SLUG = "docstring-overview-summary"
CONCEPT_SLUGS = ("docstring", "docstring-style")
SOURCE_SLUG = "source"

EXPECTED_TYPE_COUNTS = {"summary": 1, "concept": 2}
# "touch 4 pages": 1 summary + 2 concepts + 1 log entry.
EXPECTED_TOTAL_WRITES = 4


def _wiki_pages() -> list[Path]:
    """Every real wiki page under ``expected-wiki/``.

    Excludes ``log-entry.md`` — it is a *log* excerpt (an HTML-comment
    header says so), not a wiki page, and carries no frontmatter.
    """
    return sorted(
        p
        for p in WIKI.rglob("*.md")
        if p.name != "log-entry.md"
    )


def _fm(path: Path) -> dict:
    data = frontmatter.parse_stdlib(path.read_text(encoding="utf-8"))
    assert data is not None, f"{path.relative_to(REPO_ROOT)} has no frontmatter"
    return data


def _links(path: Path) -> list[str]:
    """Bare wikilink targets in *path* (display labels + anchors stripped)."""
    out = []
    for hit in wikilink.scan(path.read_text(encoding="utf-8")):
        main = hit.target.split("|", 1)[0].split("#", 1)[0].strip()
        if main.endswith(".md"):
            main = main[:-3]
        if main:
            out.append(main.rsplit("/", 1)[-1])
    return out


def _sources_slugs(fm: dict) -> list[str]:
    """Slugs cited in a page's ``sources:`` frontmatter list."""
    raw = fm.get("sources") or []
    if isinstance(raw, str):
        raw = [raw]
    slugs = []
    for entry in raw:
        s = str(entry).strip().lstrip("[").rstrip("]").strip()
        if s:
            slugs.append(s.rsplit("/", 1)[-1])
    return slugs


# --- Layout + counts ------------------------------------------------------


def test_demo_dir_exists() -> None:
    assert DEMO.is_dir(), f"missing demo dir {DEMO}"
    assert (DEMO / "source.md").is_file()
    assert (DEMO / "README.md").is_file()
    assert (WIKI / "log-entry.md").is_file()


def test_wiki_page_layout_matches_storyboard() -> None:
    """Exactly 1 summary + 2 concepts — no page snuck in or vanished."""
    pages = _wiki_pages()
    rels = {str(p.relative_to(WIKI)) for p in pages}
    assert rels == {
        f"summaries/{SUMMARY_SLUG}.md",
        f"concepts/{CONCEPT_SLUGS[0]}.md",
        f"concepts/{CONCEPT_SLUGS[1]}.md",
    }, (
        "expected-wiki/ no longer matches the demo's '1 source -> "
        "1 summary + 2 concepts' promise; update README + SVG if "
        "this is intentional"
    )


def test_type_distribution_matches_claim() -> None:
    counts: dict[str, int] = {}
    for page in _wiki_pages():
        t = str(_fm(page).get("type", ""))
        assert t in ALLOWED_TYPES, f"{page.name}: bad type {t!r}"
        counts[t] = counts.get(t, 0) + 1
    assert counts == EXPECTED_TYPE_COUNTS

    # "touch 4 pages" = the 3 wiki pages above + the single log entry.
    total = sum(counts.values()) + 1
    assert total == EXPECTED_TOTAL_WRITES


# --- Schema validity (examples/ is exempt from densa's wiki rules) --------


@pytest.mark.parametrize("page", _wiki_pages(), ids=lambda p: p.name)
def test_wiki_page_schema_valid(page: Path) -> None:
    fm = _fm(page)
    for key in REQUIRED_FRONTMATTER_KEYS:
        assert fm.get(key) not in (None, "", []), (
            f"{page.name}: required key {key!r} missing/empty"
        )
    for key in PRESENCE_ONLY_FRONTMATTER_KEYS:
        assert key in fm, f"{page.name}: universal key {key!r} absent"
    # compiled_against tracks SCHEMA_VERSION: if the schema is bumped,
    # the demo must be recompiled (exactly the drift T018 guards).
    assert int(fm["compiled_against"]) == SCHEMA_VERSION, (
        f"{page.name}: compiled_against={fm['compiled_against']} but "
        f"SCHEMA_VERSION={SCHEMA_VERSION}; recompile the demo"
    )


# --- Cross-links resolve both directions ----------------------------------


def test_summary_cites_source_and_links_both_concepts() -> None:
    fm = _fm(WIKI / "summaries" / f"{SUMMARY_SLUG}.md")
    assert _sources_slugs(fm) == [SOURCE_SLUG], (
        "summary must cite the source 1:1 in its sources: frontmatter"
    )
    body_links = set(_links(WIKI / "summaries" / f"{SUMMARY_SLUG}.md"))
    for slug in CONCEPT_SLUGS:
        assert slug in body_links, (
            f"summary body must link forward to [[{slug}]]"
        )


@pytest.mark.parametrize("slug", CONCEPT_SLUGS)
def test_concept_links_back_to_summary_and_sibling(slug: str) -> None:
    page = WIKI / "concepts" / f"{slug}.md"
    fm = _fm(page)
    # back-link via sources: each concept derives from the summary
    assert _sources_slugs(fm) == [SUMMARY_SLUG], (
        f"{slug}: sources: must cite [[{SUMMARY_SLUG}]]"
    )
    links = _links(page)
    # Appearances table cites the summary (the back-edge a viewer sees)
    assert SUMMARY_SLUG in links, (
        f"{slug}: Appearances must cite [[{SUMMARY_SLUG}]]"
    )
    # "See also" cross-links the sibling concept
    sibling = next(s for s in CONCEPT_SLUGS if s != slug)
    assert sibling in links, f"{slug}: must cross-link sibling [[{sibling}]]"


def test_no_dangling_wikilinks_in_demo() -> None:
    """Every [[link]] in the demo resolves to a demo file (hermetic)."""
    # Hermetic stem index — examples/ is skipped by the repo-wide index,
    # so we build a local one over just the demo's files.
    known = {SOURCE_SLUG, SUMMARY_SLUG, "log-entry", *CONCEPT_SLUGS}
    pages = [*_wiki_pages(), WIKI / "log-entry.md"]
    for page in pages:
        for target in _links(page):
            assert target in known, (
                f"{page.name}: dangling wikilink [[{target}]] "
                f"(known demo slugs: {sorted(known)})"
            )


# --- Log entry honesty ----------------------------------------------------


def test_log_entry_records_the_three_created_pages() -> None:
    text = (WIKI / "log-entry.md").read_text(encoding="utf-8")
    assert "[[source]]" in text, "log entry must cite the source"
    # The 'Wrote:' block names exactly the 3 created wiki pages.
    created = {SUMMARY_SLUG, *CONCEPT_SLUGS}
    for slug in created:
        assert f"{slug}.md" in text, (
            f"log entry omits created page {slug}.md"
        )


# --- Storyboard / README counts stay honest -------------------------------


def test_readme_advertises_the_real_counts() -> None:
    readme = (DEMO / "README.md").read_text(encoding="utf-8")
    assert "touch 4 pages" in readme, (
        "README headline count drifted from '4 pages'"
    )
    assert "One `summary`" in readme
    assert "Two `concept` pages" in readme


def test_storyboard_svg_counts_stay_honest() -> None:
    svg_files = list(DEMO.glob("*.svg"))
    if not svg_files:
        pytest.skip("no storyboard SVG present")
    svg = svg_files[0].read_text(encoding="utf-8")
    # The SVG encodes "touch 4 pages" and "concept (x2)"; keep them
    # numerically in step with the actual page counts.
    assert "4 pages" in svg, "SVG '4 pages' count drifted"
    assert "(x2)" in svg, "SVG concept '(x2)' count drifted"
    # And the numbers it shows must equal the real structure.
    assert EXPECTED_TYPE_COUNTS["concept"] == 2
    assert EXPECTED_TOTAL_WRITES == 4
