"""``densa stats`` — vault health at a glance.

A cheap, read-only subcommand that prints how a vault is doing:

- total wiki pages, broken down per domain;
- distribution by ``type:`` (the closed page-type enum);
- average ``updated:`` age per type, in days;
- orphan-page count (wiki pages with no inbound wikilink);
- cross-domain page count (pages tagged ``cross-domain``);
- log staleness (days since each domain's ``log.md`` last grew);
- graph health: wikilinks Obsidian cannot resolve (AGENTS013 backlog),
  the most-referenced ghost targets, and the highest-degree hub pages
  (inbound / outbound) — the numbers that decide whether the Obsidian
  graph view is readable or a hairball.

It is the "my vault is growing" artifact — a dopamine signal for the
maintainer and a README-badge candidate (``densa stats --format json``
feeds shields.io).

Design notes:

- **Stdlib-only**, like the rest of ``_system/densa/``. ``--format
  json`` uses the stdlib ``json``; dates use ``datetime``.
- **Counts the wiki, not the scaffolding.** Only ``domains/<X>/wiki/``
  pages are counted (via :func:`densa.paths.is_wiki`), which already
  excludes ``raw/``, ``outputs/``, ``attic/``, ``.legacy/`` etc. — so
  the numbers are about compiled knowledge, not bytes on disk.
- **Read-only.** No writes, no git mutation; safe to run anywhere,
  anytime, in any vault state.

The function ``run(args)`` is the entry point the CLI dispatcher calls.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from densa import paths
from densa.frontmatter import parse
from densa.fswalk import iter_markdown
from densa.paths import wikilinks_scoped
from densa.schema import ALLOWED_TYPES
from densa.wikilink import (
    ResolutionStatus,
    build_index,
    obsidian_resolvable,
    resolve,
    scan,
)


@dataclass
class _PageInfo:
    """Per-page facts gathered in a single walk."""

    rel: str
    domain: str
    type: str | None
    updated: date | None
    cross_domain: bool


@dataclass
class VaultStats:
    """The full stats payload — shaped to serialise cleanly to JSON."""

    total_pages: int = 0
    by_domain: dict[str, int] = field(default_factory=dict)
    by_type: dict[str, int] = field(default_factory=dict)
    avg_age_days_by_type: dict[str, float | None] = field(default_factory=dict)
    orphan_count: int = 0
    cross_domain_count: int = 0
    log_staleness_days: dict[str, int | None] = field(default_factory=dict)
    obsidian_unresolvable_links: int = 0
    ghost_targets: dict[str, int] = field(default_factory=dict)
    top_inbound_pages: dict[str, int] = field(default_factory=dict)
    top_outbound_pages: dict[str, int] = field(default_factory=dict)


_TOP_N = 10
"""How many entries the ghost-target / hub-page leaderboards keep."""


def add_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register ``densa stats`` with the top-level argparse parser."""
    p = subparsers.add_parser(
        "stats",
        help="print vault health stats (page counts, types, orphans, staleness)",
        description=(
            "Read-only vault health report: wiki-page counts per domain, "
            "distribution by type, average page age per type, orphan and "
            "cross-domain counts, and per-domain log staleness. "
            "`--format json` feeds badges and CI."
        ),
    )
    p.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )


def run(args: argparse.Namespace) -> int:
    """Execute ``densa stats``. Always returns 0 (reporting, not gating)."""
    repo = _resolve_repo()
    stats = collect_stats(repo, today=date.today())

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        _emit_json(stats)
    else:
        _emit_text(stats)
    return 0


# --- collection -------------------------------------------------------------


def collect_stats(repo: Path, today: date) -> VaultStats:
    """Walk the vault once and compute every stat.

    ``today`` is injected (not read from the clock inside) so tests are
    deterministic and the age math has a single, explicit reference.
    """
    pages = _collect_pages(repo)
    stats = VaultStats(total_pages=len(pages))

    # Per-domain and per-type counts.
    by_domain: dict[str, int] = defaultdict(int)
    by_type: dict[str, int] = defaultdict(int)
    ages_by_type: dict[str, list[int]] = defaultdict(list)
    for pg in pages:
        by_domain[pg.domain] += 1
        type_key = pg.type if pg.type in ALLOWED_TYPES else "(unknown)"
        by_type[type_key] += 1
        if pg.updated is not None:
            ages_by_type[type_key].append((today - pg.updated).days)
        if pg.cross_domain:
            stats.cross_domain_count += 1

    stats.by_domain = dict(sorted(by_domain.items()))
    stats.by_type = dict(sorted(by_type.items()))
    stats.avg_age_days_by_type = {
        t: (round(sum(ages) / len(ages), 1) if ages else None)
        for t, ages in sorted(ages_by_type.items())
    }
    # Types present but with no dated pages still deserve a row.
    for t in stats.by_type:
        stats.avg_age_days_by_type.setdefault(t, None)

    _collect_link_health(repo, pages, stats)
    stats.log_staleness_days = _log_staleness(repo, today)
    return stats


def _collect_pages(repo: Path) -> list[_PageInfo]:
    """Gather a :class:`_PageInfo` for every wiki page in the vault."""
    out: list[_PageInfo] = []
    for rel in iter_markdown(repo):
        rel_str = str(rel).replace("\\", "/")
        if not paths.is_wiki(rel_str):
            continue
        abs_path = repo / rel
        try:
            fm = parse(abs_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            fm = None
        fm = fm or {}
        out.append(
            _PageInfo(
                rel=rel_str,
                domain=rel_str.split("/")[1],  # domains/<X>/wiki/...
                type=_as_str(fm.get("type")),
                updated=_parse_iso_date(_as_str(fm.get("updated"))),
                cross_domain=_has_cross_domain_tag(fm),
            )
        )
    return out


def _collect_link_health(
    repo: Path,
    pages: list[_PageInfo],
    stats: VaultStats,
) -> None:
    """One pass over the wikilink graph: orphans, ghosts, hub degrees.

    Orphan semantics are unchanged from the original orphan counter: a
    wiki page is an orphan when no *other* wiki page links to it
    (self-links don't rescue). On top of that walk we now also gather:

    - ``obsidian_unresolvable_links`` — links AGENTS013 would flag
      (bucket-relative forms Obsidian renders as ghost nodes), counted
      over every :func:`~densa.paths.wikilinks_scoped` file;
    - ``ghost_targets`` — the most-referenced targets that do not
      resolve to a real file in Obsidian's eyes (densa-missing or
      Obsidian-unresolvable), i.e. the grey nodes in the graph view;
    - ``top_inbound_pages`` / ``top_outbound_pages`` — the wiki pages
      with the highest link degree; the graph view's hub candidates.
    """
    idx = build_index(repo)
    page_rels = {pg.rel for pg in pages}
    inbound: Counter[str] = Counter()
    outbound: Counter[str] = Counter()
    ghosts: Counter[str] = Counter()
    linked: set[str] = set()

    for rel in iter_markdown(repo):
        rel_str = str(rel).replace("\\", "/")
        if not wikilinks_scoped(rel_str):
            continue
        try:
            text = (repo / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        is_wiki_source = rel_str in page_rels
        src_no_ext = rel_str[:-3] if rel_str.endswith(".md") else rel_str
        for hit in scan(text):
            unresolvable = not obsidian_resolvable(hit.target, idx)
            if unresolvable:
                stats.obsidian_unresolvable_links += 1
            res = resolve(hit.target, idx, source=rel_str)
            if unresolvable or res.status is ResolutionStatus.MISSING:
                # One ghost node per offending link, whether the file
                # is genuinely missing or just Obsidian-unresolvable.
                ghosts[_link_main(hit.target)] += 1
            if not is_wiki_source:
                # Only wiki pages participate in the orphan / degree
                # math — same semantics as the original orphan counter.
                continue
            for target_no_ext in res.hits:
                target_rel = f"{target_no_ext}.md"
                if target_rel == rel_str or target_no_ext == src_no_ext:
                    continue  # self-link doesn't count
                if target_rel in page_rels:
                    linked.add(target_rel)
                    inbound[target_rel] += 1
                    outbound[rel_str] += 1

    stats.orphan_count = sum(1 for pg in pages if pg.rel not in linked)
    stats.ghost_targets = dict(ghosts.most_common(_TOP_N))
    stats.top_inbound_pages = dict(inbound.most_common(_TOP_N))
    stats.top_outbound_pages = dict(outbound.most_common(_TOP_N))


def _link_main(target: str) -> str:
    """Normalise a wikilink body to its target key (strip alias/anchor)."""
    target = target.replace("\\|", "|")
    main = target.split("|", 1)[0].split("#", 1)[0].strip()
    return main[:-3] if main.endswith(".md") else main


def _log_staleness(repo: Path, today: date) -> dict[str, int | None]:
    """Days since each domain's ``log.md`` was last touched on disk.

    ``None`` means the domain has no ``log.md`` yet. We use the file's
    mtime rather than parsing the newest entry's date: it's cheap,
    stdlib-only, and "the log file changed" is the signal we want.
    """
    domains_dir = repo / "domains"
    if not domains_dir.is_dir():
        return {}
    out: dict[str, int | None] = {}
    for d in sorted(domains_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        log = d / "log.md"
        if not log.is_file():
            out[d.name] = None
            continue
        mtime = datetime.fromtimestamp(log.stat().st_mtime).date()
        out[d.name] = (today - mtime).days
    return out


# --- helpers ----------------------------------------------------------------


def _as_str(value: object) -> str | None:
    """Coerce a frontmatter value to a stripped string, or ``None``."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return str(value)


def _parse_iso_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _has_cross_domain_tag(fm: dict[str, object]) -> bool:
    """A page is cross-domain when ``cross-domain`` appears in ``tags``."""
    tags = fm.get("tags")
    if isinstance(tags, list):
        return any(str(t).strip() == "cross-domain" for t in tags)
    if isinstance(tags, str):
        return "cross-domain" in tags
    return False


def _resolve_repo() -> Path:
    """Discover the vault root (mirrors ``cli._resolve_repo`` minus the
    git fast-path — stats has no reason to shell out)."""
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").is_file() and (
            candidate / "_system" / "densa"
        ).is_dir():
            return candidate
    return Path(__file__).resolve().parents[2]


# --- output -----------------------------------------------------------------


def _emit_text(stats: VaultStats) -> None:
    print("densa stats — vault health")
    print()
    print(f"  total wiki pages: {stats.total_pages}")
    if stats.total_pages == 0:
        print()
        print("  (no wiki pages yet — ingest a source to get started)")
        return

    print(f"  orphan pages:     {stats.orphan_count} "
          f"({_pct(stats.orphan_count, stats.total_pages)})")
    print(f"  cross-domain:     {stats.cross_domain_count}")
    print()

    print("  by domain:")
    for domain, n in stats.by_domain.items():
        print(f"    {domain:<24} {n}")
    print()

    print("  by type (avg age):")
    for type_name, n in stats.by_type.items():
        age = stats.avg_age_days_by_type.get(type_name)
        age_str = f"{age}d avg" if age is not None else "—"
        print(f"    {type_name:<24} {n:>4}   {age_str}")
    print()

    if stats.log_staleness_days:
        print("  log staleness (days since last touched):")
        for domain, days in stats.log_staleness_days.items():
            days_str = f"{days}d" if days is not None else "no log.md"
            print(f"    {domain:<24} {days_str}")
        print()

    print("  graph health:")
    print(f"    obsidian-unresolvable links: "
          f"{stats.obsidian_unresolvable_links} "
          f"(AGENTS013 backlog — ghost nodes in the graph view)")
    if stats.ghost_targets:
        print("    top ghost targets (refs):")
        for target, n in stats.ghost_targets.items():
            print(f"      {target:<40} {n}")
    if stats.top_inbound_pages:
        print("    top hub pages (inbound links):")
        for rel, n in stats.top_inbound_pages.items():
            print(f"      {rel:<56} {n}")
    if stats.top_outbound_pages:
        print("    top fan-out pages (outgoing links):")
        for rel, n in stats.top_outbound_pages.items():
            print(f"      {rel:<56} {n}")


def _emit_json(stats: VaultStats) -> None:
    import json  # noqa: PLC0415

    payload = {
        "total_pages": stats.total_pages,
        "orphan_count": stats.orphan_count,
        "cross_domain_count": stats.cross_domain_count,
        "by_domain": stats.by_domain,
        "by_type": stats.by_type,
        "avg_age_days_by_type": stats.avg_age_days_by_type,
        "log_staleness_days": stats.log_staleness_days,
        "obsidian_unresolvable_links": stats.obsidian_unresolvable_links,
        "ghost_targets": stats.ghost_targets,
        "top_inbound_pages": stats.top_inbound_pages,
        "top_outbound_pages": stats.top_outbound_pages,
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _pct(part: int, whole: int) -> str:
    if whole == 0:
        return "0%"
    return f"{round(100 * part / whole)}%"
