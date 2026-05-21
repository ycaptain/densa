"""Test wikilink scanning and resolution."""

from __future__ import annotations

from pathlib import Path

from wikilint.wikilink import (
    ResolutionStatus,
    WikilinkHit,
    build_index,
    resolve,
    scan,
)


def test_scan_finds_links_outside_code() -> None:
    text = (
        "see [[foo]] and [[bar|Bar]]\n"
        "but not `[[in-inline-code]]`\n"
        "```\n"
        "[[in-fenced-block]]\n"
        "```\n"
        "back to [[normal]]\n"
    )
    hits = list(scan(text))
    assert hits == [
        WikilinkHit(lineno=1, target="foo"),
        WikilinkHit(lineno=1, target="bar|Bar"),
        WikilinkHit(lineno=6, target="normal"),
    ]


def test_resolve_ok(tmp_path: Path) -> None:
    (tmp_path / "domains/psychology/wiki/concepts").mkdir(
        parents=True, exist_ok=True,
    )
    (tmp_path / "domains/psychology/wiki/concepts/anxiety.md").write_text(
        "x", encoding="utf-8",
    )
    idx = build_index(tmp_path)
    res = resolve("anxiety", idx)
    assert res.status is ResolutionStatus.OK


def test_resolve_missing(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("x", encoding="utf-8")
    idx = build_index(tmp_path)
    assert resolve("nothing-here", idx).status is ResolutionStatus.MISSING


def test_resolve_ambiguous(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a/dup.md").write_text("x", encoding="utf-8")
    (tmp_path / "b/dup.md").write_text("x", encoding="utf-8")
    idx = build_index(tmp_path)
    res = resolve("dup", idx)
    assert res.status is ResolutionStatus.AMBIGUOUS
    assert len(res.hits) == 2


def test_resolve_strips_anchor_and_display(tmp_path: Path) -> None:
    (tmp_path / "page.md").write_text("x", encoding="utf-8")
    idx = build_index(tmp_path)
    assert resolve("page#section", idx).status is ResolutionStatus.OK
    assert resolve("page|Display", idx).status is ResolutionStatus.OK
    assert resolve("page#section|Display", idx).status is ResolutionStatus.OK


def test_resolve_anchor_only(tmp_path: Path) -> None:
    idx = build_index(tmp_path)
    assert resolve("#self-anchor", idx).status is ResolutionStatus.ANCHOR_ONLY
