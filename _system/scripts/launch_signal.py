#!/usr/bin/env python3
"""launch_signal.py — append one adoption-signal row to the launch ledger.

MAINTAINER-ONLY. This script is deliberately **not** part of the
`_system/densa/` package: it shells out to the `gh` CLI, and dragging
that dependency into the otherwise stdlib-only, `cp -R`-able core would
break the differentiator that the whole project protects (see
`docs/maintainers/tracker/open/T016-adoption-signal-loop.md`).

It is pure stdlib here (subprocess + json + datetime) and assumes a
working, authenticated `gh` on PATH. No telemetry phone-home, no
third-party analytics — every number is a `gh api` *read* against the
public repo, appended to a human-readable markdown table.

Usage:
    python3 _system/scripts/launch_signal.py            # append today's row
    python3 _system/scripts/launch_signal.py --dry-run  # print the row, don't write
    python3 _system/scripts/launch_signal.py --note "pre-launch baseline"

The repo is auto-detected from the `origin` remote; override with
--repo owner/name. The ledger path defaults to
docs/maintainers/launch-signal.md; override with --ledger.

Degrades gracefully: any metric whose API read fails or is unavailable
on the host is recorded as `n/a` rather than failing the whole row, so
a row always lands (an absent row is a worse signal than a partial one).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LEADING_INDICATORS = (
    # Locked at T016 file-pickup (2026-05-31). Each validates one
    # high-cost launch bet; see the ledger preamble for the rationale.
    "mcp_mention_pct",  # % of open issues+discussions mentioning "MCP" — validates Phase E
    "helloworld_reactions",  # reactions on the hello-world "this is the loop" Discussion — validates the demo
    "fork_to_commit_pct",  # forks with >=1 commit ahead — validates the contributor on-ramp (T017)
)

# Markdown table header. Order is load-bearing: append_row() builds the
# row in this exact column order.
COLUMNS = (
    "date",
    "stars",
    "stars_7d",  # star velocity: stars gained in trailing 7 days (from this ledger's own history)
    "issues_open",
    "issues_closed",
    "prs_open",
    "prs_closed",
    "discussions",
    "installs",  # marketplace installs where a host API exposes them; else n/a
    "mcp_%",
    "hw_react",
    "fork_commit_%",
    "note",
)

NA = "n/a"


def run_gh(args: list[str]) -> str | None:
    """Run `gh <args>` and return stdout, or None on any failure.

    None is the caller's signal to record `n/a` for that metric.
    """
    try:
        proc = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def gh_json(args: list[str]):
    """Run a gh command expected to emit JSON; return the parsed value or None."""
    out = run_gh(args)
    if out is None:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def detect_repo() -> str | None:
    """owner/name from the `origin` remote, via gh."""
    data = gh_json(["repo", "view", "--json", "nameWithOwner"])
    if isinstance(data, dict):
        return data.get("nameWithOwner")
    return None


def fetch_core(repo: str) -> dict:
    """stars / forks / open-issue count / discussions-enabled in one call."""
    data = gh_json([
        "api",
        f"repos/{repo}",
        "--jq",
        "{stars: .stargazers_count, forks: .forks_count, "
        "open_issues_and_prs: .open_issues_count, "
        "has_discussions: .has_discussions}",
    ])
    return data if isinstance(data, dict) else {}


def fetch_issue_pr_counts(repo: str) -> dict:
    """Split issues vs PRs, open vs closed, via the search API (counts only)."""
    out: dict = {}
    queries = {
        "issues_open": f"repo:{repo} is:issue is:open",
        "issues_closed": f"repo:{repo} is:issue is:closed",
        "prs_open": f"repo:{repo} is:pr is:open",
        "prs_closed": f"repo:{repo} is:pr is:closed",
    }
    for key, q in queries.items():
        data = gh_json(["api", "-X", "GET", "search/issues", "-f", f"q={q}", "--jq", ".total_count"])
        out[key] = data if isinstance(data, int) else None
    return out


def fetch_discussions_count(repo: str) -> int | None:
    """Total Discussions via the GraphQL API. None if disabled/unavailable."""
    owner, _, name = repo.partition("/")
    query = (
        "query($owner:String!,$name:String!){"
        "repository(owner:$owner,name:$name){discussions{totalCount}}}"
    )
    data = gh_json([
        "api", "graphql",
        "-f", f"query={query}",
        "-F", f"owner={owner}",
        "-F", f"name={name}",
        "--jq", ".data.repository.discussions.totalCount",
    ])
    return data if isinstance(data, int) else None


def fetch_mcp_mention_pct(repo: str) -> int | None:
    """% of open issues+discussions whose title/body mentions 'MCP'.

    Issues are searchable; Discussions are not via the issues search
    endpoint, so this is an issues+PRs approximation — still the cheapest
    proxy for "are people asking about the MCP surface". Returns an int
    percentage, or None if there are no open items yet.
    """
    total = gh_json(["api", "-X", "GET", "search/issues", "-f",
                     f"q=repo:{repo} is:open", "--jq", ".total_count"])
    if not isinstance(total, int) or total == 0:
        return None
    mcp = gh_json(["api", "-X", "GET", "search/issues", "-f",
                   f"q=repo:{repo} is:open MCP in:title,body", "--jq", ".total_count"])
    if not isinstance(mcp, int):
        return None
    return round(100 * mcp / total)


def fetch_fork_to_commit_pct(repo: str) -> int | None:
    """% of forks that are >=1 commit ahead of the parent default branch.

    Reads up to 100 forks (one page); for a pre-launch repo that ceiling
    is irrelevant, and the row's `note` should flag if forks ever exceed
    it. Returns an int percentage, or None if there are no forks.
    """
    forks = gh_json(["api", f"repos/{repo}/forks", "--paginate",
                     "--jq", "[.[] | {full: .full_name, default: .default_branch}]"])
    if not isinstance(forks, list) or len(forks) == 0:
        return None
    ahead = 0
    measured = 0
    for fork in forks[:100]:
        fork_full = fork.get("full")
        fork_owner = fork_full.partition("/")[0] if fork_full else None
        branch = fork.get("default") or "main"
        if not fork_owner:
            continue
        # compare base...head — `ahead_by` > 0 means the fork has new commits
        cmp = gh_json([
            "api",
            f"repos/{repo}/compare/main...{fork_owner}:{branch}",
            "--jq", ".ahead_by",
        ])
        measured += 1
        if isinstance(cmp, int) and cmp > 0:
            ahead += 1
    if measured == 0:
        return None
    return round(100 * ahead / measured)


def fetch_helloworld_reactions(repo: str) -> int | str:
    """Reactions on the hello-world 'this is the loop' Discussion.

    There is no stable ID for that Discussion pre-launch, so this is a
    best-effort: it sums reactions across all Discussions whose title
    contains 'hello-world' or 'this is the loop'. Returns an int, or NA
    if Discussions are disabled / none match.
    """
    owner, _, name = repo.partition("/")
    query = (
        "query($owner:String!,$name:String!){repository(owner:$owner,name:$name){"
        "discussions(first:50){nodes{title reactions{totalCount}}}}}"
    )
    data = gh_json([
        "api", "graphql",
        "-f", f"query={query}",
        "-F", f"owner={owner}",
        "-F", f"name={name}",
        "--jq",
        ".data.repository.discussions.nodes",
    ])
    if not isinstance(data, list):
        return NA
    total = 0
    matched = False
    for node in data:
        title = (node.get("title") or "").lower()
        if "hello-world" in title or "this is the loop" in title:
            matched = True
            rc = node.get("reactions", {}).get("totalCount")
            if isinstance(rc, int):
                total += rc
    return total if matched else NA


def read_prior_stars(ledger: Path, cutoff: date) -> int | None:
    """Earliest recorded star count on/before `cutoff`, for 7d velocity.

    Parses this ledger's own rows. Returns None if no usable prior row.
    """
    if not ledger.exists():
        return None
    best_date: date | None = None
    best_stars: int | None = None
    for raw_line in ledger.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("| 20"):  # data rows start "| 2026-..."
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        try:
            row_date = datetime.strptime(cells[0], "%Y-%m-%d").date()
            row_stars = int(cells[1])
        except (ValueError, IndexError):
            continue
        # take the row closest to (but not after) the cutoff
        if row_date <= cutoff and (best_date is None or row_date > best_date):
            best_date, best_stars = row_date, row_stars
    return best_stars


def fmt(value) -> str:
    """Render a metric cell: None -> n/a, everything else -> str."""
    if value is None:
        return NA
    return str(value)


def build_row(repo: str, ledger: Path, today: date, note: str) -> dict:
    core = fetch_core(repo)
    counts = fetch_issue_pr_counts(repo)
    discussions = fetch_discussions_count(repo)
    stars = core.get("stars")

    prior = read_prior_stars(ledger, today - timedelta(days=7))
    stars_7d = (stars - prior) if (isinstance(stars, int) and isinstance(prior, int)) else None

    return {
        "date": today.isoformat(),
        "stars": stars,
        "stars_7d": stars_7d,
        "issues_open": counts.get("issues_open"),
        "issues_closed": counts.get("issues_closed"),
        "prs_open": counts.get("prs_open"),
        "prs_closed": counts.get("prs_closed"),
        "discussions": discussions,
        "installs": None,  # no host marketplace API exposes this yet; revisit per-host
        "mcp_%": fetch_mcp_mention_pct(repo),
        "hw_react": fetch_helloworld_reactions(repo),
        "fork_commit_%": fetch_fork_to_commit_pct(repo),
        "note": note or "",
    }


def row_to_md(row: dict) -> str:
    cells = [
        row["date"],
        fmt(row["stars"]),
        fmt(row["stars_7d"]),
        fmt(row["issues_open"]),
        fmt(row["issues_closed"]),
        fmt(row["prs_open"]),
        fmt(row["prs_closed"]),
        fmt(row["discussions"]),
        fmt(row["installs"]),
        fmt(row["mcp_%"]),
        fmt(row["hw_react"]),
        fmt(row["fork_commit_%"]),
        row["note"].replace("|", "\\|"),
    ]
    return "| " + " | ".join(cells) + " |"


LEDGER_HEADING = "## Ledger"


def append_row(ledger: Path, md_row: str) -> None:
    """Append a row immediately below the Ledger table's divider line.

    Mirrors log.md discipline (append-only); newest rows sit at the top
    of the table body, just under the `|---|` divider. The divider is
    located *after* the `## Ledger` heading so the Column-key table
    earlier in the document is never targeted by accident.
    """
    text = ledger.read_text(encoding="utf-8")
    lines = text.splitlines()

    heading_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == LEDGER_HEADING),
        None,
    )
    if heading_idx is None:
        raise SystemExit(
            f"could not find the '{LEDGER_HEADING}' heading in {ledger}; "
            "is the ledger preamble intact?"
        )

    divider_idx = None
    for i in range(heading_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("|") and set(stripped) <= set("|-: "):
            divider_idx = i
            break
    if divider_idx is None:
        raise SystemExit(
            f"could not find the Ledger table divider after '{LEDGER_HEADING}' "
            f"in {ledger}; is the table intact?"
        )

    lines.insert(divider_idx + 1, md_row)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--repo", help="owner/name (default: from origin via gh)")
    parser.add_argument(
        "--ledger",
        default="docs/maintainers/launch-signal.md",
        help="path to the ledger markdown file",
    )
    parser.add_argument("--note", default="", help="free-text note for this row")
    parser.add_argument(
        "--date",
        help="ISO date for the row (default: today UTC). Set for deterministic testing.",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the row; do not write")
    args = parser.parse_args(argv)

    if run_gh(["--version"]) is None:
        print("error: `gh` CLI not found or not working on PATH.", file=sys.stderr)
        print("Install from https://cli.github.com and run `gh auth login`.", file=sys.stderr)
        return 2

    repo = args.repo or detect_repo()
    if not repo:
        print("error: could not detect repo; pass --repo owner/name.", file=sys.stderr)
        return 2

    today = (
        datetime.strptime(args.date, "%Y-%m-%d").date()
        if args.date
        else datetime.now(timezone.utc).date()
    )

    ledger = Path(args.ledger)
    row = build_row(repo, ledger, today, args.note)
    md_row = row_to_md(row)

    if args.dry_run:
        print(f"repo: {repo}")
        print(md_row)
        return 0

    if not ledger.exists():
        print(
            f"error: ledger {ledger} does not exist. Create it first "
            "(see docs/maintainers/launch-signal.md template) — this script "
            "only appends rows.",
            file=sys.stderr,
        )
        return 2

    append_row(ledger, md_row)
    print(f"appended row for {today.isoformat()} to {ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
