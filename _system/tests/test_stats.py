"""Tests for ``densa stats`` (``densa.commands.stats``).

``stats`` walks a vault once and reports page counts, type
distribution, per-type average age, orphan count, cross-domain count,
and log staleness. We build empty / single-domain / multi-domain
vaults on disk and assert on the :class:`VaultStats` payload.

``collect_stats`` takes an injected ``today`` so the age math is
deterministic — no clock reads in the assertions.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pytest

from densa.commands import stats as stats_cmd

from .conftest import make_wiki_page

TODAY = date(2026, 6, 1)


def _vault(tmp_path: Path) -> Path:
    """A vault root ``stats`` will accept as the repo (AGENTS.md +
    in-repo package dir)."""
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (tmp_path / "_system" / "densa").mkdir(parents=True)
    return tmp_path


def _page(
    type_: str = "concept",
    *,
    updated: str = "2026-05-01",
    extra: str = "",
    cross_domain: bool = False,
) -> str:
    """Wrap ``make_wiki_page`` with the knobs stats cares about."""
    body = make_wiki_page(type_=type_, extra=extra)
    body = body.replace("updated: 2026-01-01", f"updated: {updated}")
    if cross_domain:
        body = body.replace("tags: []", "tags: [cross-domain]")
    return body


# --- empty vault ------------------------------------------------------------


def test_empty_vault_reports_zero(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.total_pages == 0
    assert stats.by_domain == {}
    assert stats.orphan_count == 0


def test_empty_vault_text_output_is_graceful(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _vault(tmp_path)
    monkeypatch.chdir(repo)
    rc = stats_cmd.run(argparse.Namespace(format="text"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "total wiki pages: 0" in out
    assert "no wiki pages yet" in out


# --- single domain ----------------------------------------------------------


def test_single_domain_counts(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    base = repo / "domains" / "research" / "wiki"
    (base / "concepts").mkdir(parents=True)
    (base / "summaries").mkdir(parents=True)
    (base / "concepts" / "a.md").write_text(_page("concept"), encoding="utf-8")
    (base / "concepts" / "b.md").write_text(_page("concept"), encoding="utf-8")
    (base / "summaries" / "s.md").write_text(_page("summary"), encoding="utf-8")

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.total_pages == 3
    assert stats.by_domain == {"research": 3}
    assert stats.by_type == {"concept": 2, "summary": 1}


def test_avg_age_per_type(tmp_path: Path) -> None:
    """Average age is computed from ``updated:`` against the injected
    ``today``, per type."""
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    # 2026-05-01 → 31 days before 2026-06-01; 2026-05-31 → 1 day.
    (base / "old.md").write_text(_page("concept", updated="2026-05-01"), encoding="utf-8")
    (base / "new.md").write_text(_page("concept", updated="2026-05-31"), encoding="utf-8")

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.avg_age_days_by_type["concept"] == 16.0  # (31 + 1) / 2


def test_cross_domain_count(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    (base / "x.md").write_text(_page("concept", cross_domain=True), encoding="utf-8")
    (base / "y.md").write_text(_page("concept", cross_domain=False), encoding="utf-8")

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.cross_domain_count == 1


# --- orphans ----------------------------------------------------------------


def test_orphan_detection(tmp_path: Path) -> None:
    """A page nobody links to is an orphan; a linked page is not."""
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    # `hub` links to `target`; `lonely` is linked by no one.
    (base / "hub.md").write_text(
        _page("concept", extra="See [[target]].\n"), encoding="utf-8",
    )
    (base / "target.md").write_text(_page("concept"), encoding="utf-8")
    (base / "lonely.md").write_text(_page("concept"), encoding="utf-8")

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    # hub (no inbound) and lonely (no inbound) are orphans; target is not.
    assert stats.orphan_count == 2


def test_self_link_does_not_rescue_from_orphan(tmp_path: Path) -> None:
    """A page that links only to itself is still an orphan."""
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    (base / "narciss.md").write_text(
        _page("concept", extra="See [[narciss]].\n"), encoding="utf-8",
    )
    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.orphan_count == 1


# --- multi domain -----------------------------------------------------------


def test_multi_domain_breakdown(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    for dom, n in (("alpha", 2), ("beta", 1)):
        base = repo / "domains" / dom / "wiki" / "concepts"
        base.mkdir(parents=True)
        for i in range(n):
            (base / f"p{i}.md").write_text(_page("concept"), encoding="utf-8")

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.total_pages == 3
    assert stats.by_domain == {"alpha": 2, "beta": 1}


def test_legacy_and_outputs_excluded(tmp_path: Path) -> None:
    """``.legacy/`` snapshots and ``outputs/`` artifacts are not wiki
    pages and must not inflate the counts."""
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki"
    (base / "concepts").mkdir(parents=True)
    (base / "concepts" / "live.md").write_text(_page("concept"), encoding="utf-8")
    # A .legacy snapshot under wiki/ — excluded by paths.is_wiki.
    legacy = base / ".legacy" / "concepts"
    legacy.mkdir(parents=True)
    (legacy / "old.md").write_text(_page("concept"), encoding="utf-8")
    # An outputs artifact — not under domains/<X>/wiki/ at all.
    out = repo / "outputs" / "lint"
    out.mkdir(parents=True)
    (out / "2026-06-01.md").write_text(_page("report"), encoding="utf-8")

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.total_pages == 1


# --- log staleness ----------------------------------------------------------


def test_log_staleness_none_when_absent(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    (repo / "domains" / "r" / "wiki" / "concepts").mkdir(parents=True)
    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.log_staleness_days == {"r": None}


def test_log_staleness_present(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    dom = repo / "domains" / "r"
    (dom / "wiki" / "concepts").mkdir(parents=True)
    (dom / "log.md").write_text("# log\n", encoding="utf-8")
    stats = stats_cmd.collect_stats(repo, today=TODAY)
    # mtime is "now" in the test run, so staleness is a small int ≥ 0.
    assert isinstance(stats.log_staleness_days["r"], int)


# --- json output ------------------------------------------------------------


def test_json_output_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    (base / "a.md").write_text(_page("concept"), encoding="utf-8")
    monkeypatch.chdir(repo)

    rc = stats_cmd.run(argparse.Namespace(format="json"))
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["total_pages"] == 1
    assert payload["by_type"] == {"concept": 1}
    assert "orphan_count" in payload


# --- parser smoke -----------------------------------------------------------


def test_add_parser_registers_stats() -> None:
    parent = argparse.ArgumentParser()
    sub = parent.add_subparsers(dest="command")
    stats_cmd.add_parser(sub)
    args = parent.parse_args(["stats", "--format", "json"])
    assert args.command == "stats"
    assert args.format == "json"


# --- graph health -----------------------------------------------------------


def test_obsidian_unresolvable_and_ghost_targets(tmp_path: Path) -> None:
    """A bucket-relative link counts toward the AGENTS013 backlog and
    its target shows up on the ghost leaderboard; a densa-missing bare
    slug is a ghost too but not format-unresolvable."""
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    (base / "anxiety.md").write_text(_page("concept"), encoding="utf-8")
    (base / "x.md").write_text(
        _page("concept", extra=(
            "See [[concepts/anxiety]] and [[nothing-here]].\n"
        )),
        encoding="utf-8",
    )

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.obsidian_unresolvable_links == 1
    assert stats.ghost_targets == {
        "concepts/anxiety": 1,
        "nothing-here": 1,
    }


def test_hub_degree_leaderboards(tmp_path: Path) -> None:
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    (base / "hub.md").write_text(_page("concept"), encoding="utf-8")
    for i in range(3):
        (base / f"fan{i}.md").write_text(
            _page("concept", extra="See [[hub]].\n"), encoding="utf-8",
        )

    stats = stats_cmd.collect_stats(repo, today=TODAY)
    assert stats.top_inbound_pages == {
        "domains/r/wiki/concepts/hub.md": 3,
    }
    assert all(
        n == 1 for n in stats.top_outbound_pages.values()
    )
    assert len(stats.top_outbound_pages) == 3


def test_graph_health_in_json_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _vault(tmp_path)
    base = repo / "domains" / "r" / "wiki" / "concepts"
    base.mkdir(parents=True)
    (base / "a.md").write_text(_page("concept"), encoding="utf-8")
    monkeypatch.chdir(repo)

    rc = stats_cmd.run(argparse.Namespace(format="json"))
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["obsidian_unresolvable_links"] == 0
    assert payload["ghost_targets"] == {}
    assert "top_inbound_pages" in payload
    assert "top_outbound_pages" in payload
