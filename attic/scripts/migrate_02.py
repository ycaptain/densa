#!/usr/bin/env python3
"""One-shot migration: relocate lint reports + index snapshot to outputs/.

Moves the following legacy paths under the new ``outputs/`` layer
introduced in v0.2.0:

  wiki/syntheses/lint-YYYY-MM-DD.md               -> outputs/lint/<date>.md
  domains/<X>/wiki/syntheses/lint-YYYY-MM-DD.md   -> outputs/lint/<date>.md
  _system/cache/index-snapshot.md                 -> outputs/snapshots/index-snapshot.md

Rewrites frontmatter ``type: synthesis`` -> ``type: report`` (and
``type: cache`` -> ``type: report``) on each moved file.

Idempotent: subsequent runs detect that the legacy paths no longer
exist and exit with 0 work performed.

Usage:
  python _system/scripts/migrate_02.py            # dry-run (default)
  python _system/scripts/migrate_02.py --apply    # execute git mv + rewrite
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_LINT_FILENAME_RE = re.compile(r"lint-(\d{4}-\d{2}-\d{2})\.md$")
_SYNTHESIS_PATH_RE = re.compile(
    r"^(?:domains/[^/]+/)?wiki/syntheses/lint-\d{4}-\d{2}-\d{2}\.md$",
)
_TYPE_LINE_RE = re.compile(r"^type:\s*(synthesis|cache)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Move:
    src: Path
    dest: Path


def _repo_root(start: Path) -> Path:
    out = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        text=True,
    )
    return Path(out.strip())


def _collect_moves(repo: Path) -> list[Move]:
    moves: list[Move] = []
    for rel in sorted(_iter_legacy_lint_files(repo)):
        m = _LINT_FILENAME_RE.search(rel.name)
        if not m:
            continue
        dest = repo / "outputs" / "lint" / f"{m.group(1)}.md"
        moves.append(Move(src=repo / rel, dest=dest))
    cache_snap = repo / "_system" / "cache" / "index-snapshot.md"
    if cache_snap.is_file():
        moves.append(Move(
            src=cache_snap,
            dest=repo / "outputs" / "snapshots" / "index-snapshot.md",
        ))
    return moves


def _iter_legacy_lint_files(repo: Path) -> Iterator[Path]:
    syntheses_dirs = [repo / "wiki" / "syntheses"]
    domains_root = repo / "domains"
    if domains_root.is_dir():
        for child in sorted(domains_root.iterdir()):
            if child.is_dir():
                syntheses_dirs.append(child / "wiki" / "syntheses")
    for d in syntheses_dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("lint-*.md")):
            rel = f.relative_to(repo).as_posix()
            if _SYNTHESIS_PATH_RE.match(rel):
                yield f.relative_to(repo)


def _git_mv(repo: Path, src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        ["git", "mv", str(src.relative_to(repo)), str(dest.relative_to(repo))],
        cwd=repo,
    )


def _rewrite_type(dest: Path) -> bool:
    text = dest.read_text(encoding="utf-8")
    new_text, count = _TYPE_LINE_RE.subn("type: report", text, count=1)
    if count:
        dest.write_text(new_text, encoding="utf-8")
        return True
    return False


def _append_migration_log(repo: Path, moved: int) -> None:
    log_path = repo / "_system" / "migrations.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = f"{date.today().isoformat()} migrate_02 | outputs/ layer adopted; {moved} file(s) moved\n"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(entry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="execute the migration; default is dry-run",
    )
    args = parser.parse_args(argv)

    repo = _repo_root(Path.cwd())
    moves = _collect_moves(repo)

    if not moves:
        print("migrate_02: nothing to do (legacy paths already migrated)")
        return 0

    print("migrate_02: action plan" + ("" if args.apply else " (dry-run)"))
    for m in moves:
        src_rel = m.src.relative_to(repo).as_posix()
        dest_rel = m.dest.relative_to(repo).as_posix()
        print(f"  git mv {src_rel} -> {dest_rel}")

    if not args.apply:
        print()
        print("rerun with --apply to execute. On failure roll back with:")
        print("  git restore --staged --worktree .")
        return 0

    for m in moves:
        try:
            _git_mv(repo, m.src, m.dest)
        except subprocess.CalledProcessError as exc:
            print(
                f"migrate_02: git mv failed for "
                f"{m.src.relative_to(repo)}: {exc}",
                file=sys.stderr,
            )
            print(
                "roll back with: git restore --staged --worktree .",
                file=sys.stderr,
            )
            return 1
        if _rewrite_type(m.dest):
            subprocess.check_call(
                ["git", "add", str(m.dest.relative_to(repo))],
                cwd=repo,
            )

    _append_migration_log(repo, len(moves))
    print(f"migrate_02: moved {len(moves)} file(s); migrations.log updated")
    print("review the staged diff (`git diff --cached`) before committing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
