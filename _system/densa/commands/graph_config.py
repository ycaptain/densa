"""``densa graph-config`` — generate a readable Obsidian graph config.

A fresh Obsidian vault renders every markdown file as a node with no
colors and no filters; on a grown Densa vault that is a grey hairball:
scaffolding (``_system/``, ``attic/``, ``outputs/``), immutable raw
sources, and the append-only logs (a mature domain log carries
hundreds of outgoing links) drown the ~few-hundred wiki pages that
are the actual knowledge graph.

This command writes ``.obsidian/graph.json`` tuned for a Densa vault:

- **filter** — only the wiki graph: scaffolding, ``raw/``, every
  ``log.md``, and the schema docs are excluded. Extra exclusions
  (e.g. a vendored upstream checkout) via repeatable ``--exclude``.
- **color groups** — one color per ``domains/<X>/`` (stable palette,
  sorted domain order), plus landmark groups for ``index.md`` files
  and ``syntheses/`` pages. First matching group wins; tweak freely
  in Obsidian's graph settings panel afterwards.
- **display / forces** — tuned for a few-hundred-node graph: labels
  fade in earlier, unresolved ghosts hidden, tighter link distance.

Design notes:

- **Write-once by default.** ``graph.json`` is user config; an
  existing file is never overwritten without ``--force``.
- **Run with Obsidian closed.** Obsidian rewrites ``.obsidian/*.json``
  on exit, so edits made while it is running are silently lost.
- The **global graph is a domain map**, not a navigation tool — for
  daily use open the *local* graph (depth 2) on the page you are
  reading. See docs/setup.md §"Graph view".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Decimal RGB values (0xRRGGBB) for per-domain color groups, assigned
# to domains in sorted-name order and recycled when a vault has more
# domains than the palette has rows.
_DOMAIN_PALETTE: tuple[int, ...] = (
    0x9B59B6,  # purple
    0x3498DB,  # blue
    0x2ECC71,  # green
    0xE67E22,  # orange
    0x1ABC9C,  # teal
    0xE74C3C,  # red
    0x95A5A6,  # grey
)

_INDEX_COLOR = 0xF1C40F  # gold — navigation landmarks
_SYNTHESES_COLOR = 0xE91E63  # pink — highest-value compiled pages

_BASE_FILTER = (
    '-path:"_system/" -path:"attic/" -path:"inbox/" -path:"outputs/" '
    '-path:"/raw/" -file:"log.md" -file:"AGENTS.md" -file:"CLAUDE.md" '
    '-file:"GUIDE.md" -file:"README.md"'
)


def add_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register ``densa graph-config`` with the top-level parser."""
    p = subparsers.add_parser(
        "graph-config",
        help="generate .obsidian/graph.json tuned for a Densa vault",
        description=(
            "Write an Obsidian graph-view config that filters out "
            "scaffolding/raw/logs and colors nodes per domain, so the "
            "graph shows the wiki instead of a hairball. Never "
            "overwrites an existing graph.json without --force. Run "
            "while Obsidian is closed."
        ),
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "extra path to filter out of the graph (repeatable), e.g. "
            "--exclude share/ for a vendored upstream checkout"
        ),
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing .obsidian/graph.json",
    )
    p.add_argument(
        "--print",
        dest="print_only",
        action="store_true",
        help="print the generated JSON to stdout instead of writing",
    )


def run(args: argparse.Namespace) -> int:
    """Execute ``densa graph-config``. Returns the CLI exit code."""
    repo = _resolve_repo()
    if repo is None:
        _err("not inside a Densa vault (no AGENTS.md + _system/densa/ here)")
        return 2

    domains = discover_domains(repo)
    config = build_graph_config(domains, excludes=args.exclude)
    payload = json.dumps(config, indent=2, ensure_ascii=False) + "\n"

    if args.print_only:
        sys.stdout.write(payload)
        return 0

    target = repo / ".obsidian" / "graph.json"
    if target.exists() and not args.force:
        _err(
            f"{target.relative_to(repo)} already exists — re-run with "
            f"--force to overwrite (your current graph settings will "
            f"be replaced), or --print to inspect first"
        )
        return 2

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    print(f"wrote {target.relative_to(repo)}")
    print(f"  domains colored: {', '.join(domains) if domains else '(none)'}")
    if args.exclude:
        print(f"  extra exclusions: {', '.join(args.exclude)}")
    print()
    print("Notes:")
    print("  - run this while Obsidian is CLOSED (it rewrites "
          ".obsidian/*.json on exit)")
    print("  - the global graph is a domain map; for navigation open "
          "the LOCAL graph (depth 2) on any page")
    print("  - colors/filters are editable later in Obsidian's graph "
          "settings panel")
    return 0


# --- generation ---------------------------------------------------------------


def discover_domains(repo: Path) -> list[str]:
    """Sorted names of ``domains/<X>/`` dirs that have a ``wiki/``."""
    root = repo / "domains"
    if not root.is_dir():
        return []
    return sorted(
        child.name
        for child in root.iterdir()
        if child.is_dir() and (child / "wiki").is_dir()
    )


def build_graph_config(
    domains: list[str],
    excludes: list[str] | None = None,
) -> dict[str, object]:
    """Assemble the ``graph.json`` payload Obsidian expects.

    ``colorGroups`` entries are ``{"query": ..., "color": {"a": 1,
    "rgb": <decimal 0xRRGGBB>}}``; the first matching group wins, so
    domain groups come first and the landmark groups (index /
    syntheses) follow.
    """
    search = _BASE_FILTER
    for extra in excludes or []:
        search = f'-path:"{extra}" {search}'

    color_groups: list[dict[str, object]] = [
        {
            "query": f'path:"domains/{domain}/"',
            "color": {
                "a": 1,
                "rgb": _DOMAIN_PALETTE[i % len(_DOMAIN_PALETTE)],
            },
        }
        for i, domain in enumerate(domains)
    ]
    color_groups.append({
        "query": 'file:"index.md"',
        "color": {"a": 1, "rgb": _INDEX_COLOR},
    })
    color_groups.append({
        "query": 'path:"/syntheses/"',
        "color": {"a": 1, "rgb": _SYNTHESES_COLOR},
    })

    return {
        "collapse-filter": False,
        "search": search,
        "showTags": False,
        "showAttachments": False,
        "hideUnresolved": True,
        "showOrphans": False,
        "collapse-color-groups": False,
        "colorGroups": color_groups,
        "collapse-display": False,
        "showArrow": False,
        "textFadeMultiplier": -0.6,
        "nodeSizeMultiplier": 1.2,
        "lineSizeMultiplier": 1,
        "collapse-forces": False,
        "centerStrength": 0.45,
        "repelStrength": 13,
        "linkStrength": 0.9,
        "linkDistance": 110,
        "scale": 0.7,
        "close": False,
    }


def _resolve_repo() -> Path | None:
    """Walk up from cwd looking for a Densa vault root."""
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").is_file() and (
            candidate / "_system" / "densa"
        ).is_dir():
            return candidate
    return None


def _err(msg: str) -> None:
    print(f"densa graph-config: error: {msg}", file=sys.stderr)
