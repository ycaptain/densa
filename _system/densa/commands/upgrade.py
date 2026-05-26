"""``densa upgrade`` — pull upstream schema/validator changes safely.

The flow:

1. Verify we're inside a Densa vault (``AGENTS.md`` + ``_system/densa/``
   exist; ``upstream`` remote configured).
2. ``git fetch upstream``.
3. Show a short diff summary (commits ahead, files changed in
   ``AGENTS.md`` / ``_system/`` / ``docs/``) so the user can preview
   the upgrade before it lands.
4. ``git merge upstream/main`` (or ``--ref`` override).
5. Detect new ``_system/scripts/migrate_NN_*.py`` files introduced by
   the merge and prompt the user to run them.

This command **never touches** ``domains/**``; if the merge surfaces
a conflict there, that's a vault-content conflict and the user owns
it. The upstream contract is that ``domains/**`` belongs to the user
(per AGENTS.md §"Operation writes"), so genuine conflicts in that namespace should
be rare.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def add_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register ``densa upgrade`` with the top-level argparse parser."""
    p = subparsers.add_parser(
        "upgrade",
        help="pull upstream schema/validator changes (git fetch + merge)",
        description=(
            "Pull upstream Densa changes into this vault. Fetches "
            "upstream, shows a diff summary, merges, and surfaces any "
            "new migration scripts."
        ),
    )
    p.add_argument(
        "--ref",
        default="upstream/main",
        help="upstream ref to merge (default: upstream/main)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would change; do not merge",
    )
    p.add_argument(
        "--yes", "-y",
        action="store_true",
        help="merge without asking for confirmation",
    )


def run(args: argparse.Namespace) -> int:
    """Execute ``densa upgrade``. Returns the CLI exit code."""
    repo = _resolve_repo()
    if repo is None:
        _err("not inside a Densa vault (no AGENTS.md + _system/densa/ here)")
        return 2

    if not _has_remote(repo, "upstream"):
        _err(
            "no `upstream` remote configured. Run "
            "`git remote add upstream https://github.com/ycaptain/densa.git`"
        )
        return 2

    if _run_git(["fetch", "upstream"], cwd=repo) != 0:
        _err("git fetch upstream failed")
        return 1

    summary = _diff_summary(repo, args.ref)
    print(summary)
    if "0 commits ahead of HEAD" in summary:
        print("Already up to date.")
        return 0

    if args.dry_run:
        print("(dry run — not merging)")
        return 0

    if not args.yes:
        choice = input(f"Merge {args.ref} into HEAD? [y/N] ").strip().lower()
        if choice not in ("y", "yes"):
            print("Aborted.")
            return 0

    rc = _run_git(["merge", args.ref], cwd=repo)
    if rc != 0:
        _err(
            "merge failed. Resolve conflicts (likely in AGENTS.md or "
            "_system/**; never in domains/**), then `git commit`."
        )
        return rc

    _surface_migrations(repo)
    print("✓ Densa vault upgraded.")
    return 0


# --- internals --------------------------------------------------------------


def _resolve_repo() -> Path | None:
    """Walk up from cwd looking for a Densa vault root."""
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").is_file() and (
            candidate / "_system" / "densa"
        ).is_dir():
            return candidate
    return None


def _has_remote(repo: Path, name: str) -> bool:
    out = subprocess.run(
        ["git", "remote"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return name in out.split()


def _diff_summary(repo: Path, ref: str) -> str:
    """Produce a short, human-readable summary of HEAD..<ref>."""
    log = subprocess.run(
        ["git", "log", "--oneline", f"HEAD..{ref}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    if not log:
        return f"0 commits ahead of HEAD on {ref}."

    commits = log.splitlines()

    stat = subprocess.run(
        ["git", "diff", "--stat", f"HEAD..{ref}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    head = f"{len(commits)} commit(s) ahead of HEAD on {ref}:\n"
    body = "\n".join(f"  {c}" for c in commits[:8])
    if len(commits) > 8:
        body += f"\n  … and {len(commits) - 8} more"
    return f"{head}{body}\n\nDiff stat:\n{stat}\n"


def _surface_migrations(repo: Path) -> None:
    """If the merge introduced new ``_system/scripts/migrate_NN_*.py``
    files, tell the user about them."""
    scripts_dir = repo / "_system" / "scripts"
    if not scripts_dir.is_dir():
        return

    # Find migrate_*.py that appeared in the last merge (HEAD^..HEAD).
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD^..HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    new_scripts = [
        line for line in out.splitlines()
        if line.startswith("_system/scripts/migrate_") and line.endswith(".py")
    ]
    if not new_scripts:
        return

    print()
    print("This upgrade introduced new schema-migration scripts:")
    for s in new_scripts:
        print(f"  python {s}")
    print()
    print("Run each migration once, review the diff, then commit.")


def _run_git(argv: list[str], cwd: Path) -> int:
    return subprocess.run(["git", *argv], cwd=cwd, check=False).returncode


def _err(msg: str) -> None:
    print(f"densa upgrade: error: {msg}", file=sys.stderr)
