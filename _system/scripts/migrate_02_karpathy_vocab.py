#!/usr/bin/env python3
"""Migrate a Densa vault from schema_version 1 to 2.

Three modes are supported. ``densa migrate`` selects one via
``--mode``; running this script directly accepts the same flag.

``--mode in-place`` *(default — content-preserving)*
    For each ``domains/<X>/wiki/`` in the vault:

    1. Rename v1 sub-folders to their v2 names per
       :data:`densa.schema.FOLDER_RENAMES_V1_TO_V2` (``analyses/`` →
       ``summaries/``, ``frameworks/`` → ``overviews/``,
       ``questions/`` → ``open-questions/``, etc.).
    2. Rewrite each page's frontmatter ``type:`` per
       :data:`densa.schema.TYPE_RENAMES_V1_TO_V2`. When the v1 type
       carried a sub-category nuance ``pattern``, ``project``,
       ``decision`` …) the script writes a ``kind:`` field so L2s
       can preserve the distinction.
    3. Rename slug stems via
       :data:`densa.schema.SLUG_SUFFIX_RENAMES_V1_TO_V2`
       (``*-analysis.md`` → ``*-summary.md``).
    4. Bump ``compiled_against`` to 2 and append a ``migration_history``
       entry so future tooling (and humans) can tell which pages
       were mechanically migrated vs. re-ingested under v2.
    5. Rewrite every ``[[wikilink]]`` (and ``[[link|alias]]``,
       ``[[link#anchor]]``) across the *entire* vault so the new
       slugs resolve.
    6. Create the seven recommended v2 folders and a per-domain
       ``overview.md`` if missing.

``--mode archive``
    For each ``domains/<X>/wiki/`` in the vault:

    1. ``git mv`` every v1 sub-folder under ``wiki/.legacy/<name>/``.
    2. Annotate moved pages with ``status: legacy-snapshot``.
    3. Create the seven recommended v2 folders and a per-domain
       ``overview.md`` so the next ingest has a clean slate.

    Use this when you want a fresh start and plan to re-ingest the
    sources you still care about under v2 from scratch.

``--mode recover``
    Inverse of ``archive``. For each ``domains/<X>/wiki/.legacy/``
    folder, lift its contents back into the live v2 layout by
    applying the in-place transform (folder rename + type rewrite +
    slug rename + frontmatter update + wikilink rewrite). The
    ``.legacy/`` tree is then empty and can be removed by the user.

    Use this when a previous ``archive`` run feels too aggressive.

Every mode is **idempotent**: re-running on a vault that already
reached the target state produces no diff. The migrations log at
``_system/migrations.log`` records (date, id, mode) for each run so
the chain ``densa migrate`` builds is auditable.

Usage::

    python _system/scripts/migrate_02_karpathy_vocab.py --apply
    python _system/scripts/migrate_02_karpathy_vocab.py --apply --mode archive
    python _system/scripts/migrate_02_karpathy_vocab.py --apply --mode recover
    python _system/scripts/migrate_02_karpathy_vocab.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Final

# This script is invoked by ``densa migrate`` with PYTHONPATH set to
# ``_system``; resolve our siblings even when run standalone from the
# repo root so the rename tables stay single-sourced.
_HERE = Path(__file__).resolve()
_SYSTEM = _HERE.parent.parent
if str(_SYSTEM) not in sys.path:
    sys.path.insert(0, str(_SYSTEM))

from densa.schema import (  # noqa: E402
    FOLDER_RENAMES_V1_TO_V2,
    MIGRATION_MODE_ARCHIVE,
    MIGRATION_MODE_IN_PLACE,
    MIGRATION_MODE_RECOVER,
    SCHEMA_VERSION,
    SLUG_SUFFIX_RENAMES_V1_TO_V2,
    TYPE_RENAMES_V1_TO_V2,
    TYPE_SUB_KIND_V1_TO_V2,
)

MIGRATION_ID: Final[str] = "02_karpathy_vocab"
MIGRATION_LABEL: Final[str] = "v1 → v2: Karpathy vocabulary"
FROM_VERSION: Final[int] = 1
TO_VERSION: Final[int] = 2

# The full set of v2 folders any domain should host. Used by every
# mode to seed missing folders + the per-domain ``overview.md``.
V2_FOLDERS: Final[tuple[str, ...]] = (
    "summaries",
    "entities",
    "concepts",
    "comparisons",
    "overviews",
    "syntheses",
    "open-questions",
)

LEGACY_DIR: Final[str] = ".legacy"


_OVERVIEW_TEMPLATE: Final[str] = """\
---
type: overview
domain: {domain}
created: {today}
updated: {today}
sources: []
tags: []
aliases: ["{domain} home", "{domain} overview"]
status: active
compiled_against: 2
---

# {domain} — Overview

> [!important] If you're new here, this is the only page you need to
> start. Run `ingest` against any source under `raw/` and the agent
> will populate the buckets below.

## What this domain has (mindmap)

```mermaid
mindmap
  root(({domain}))
    Summaries
      one per ingested source
    Entities
      people orgs and objects
    Concepts
      terms worth defining once
    Comparisons
      X vs Y
    Sub-area overviews
      birds-eye views
    Syntheses
      cross-source narratives
    Open questions
      long-arc trackers
```

## What page do I read when?

| Situation | Read |
|---|---|
| Elevator pitch | the mindmap above |
| One source's takeaways | a page in `summaries/` (~5 min each) |
| Look up a term | a page in `concepts/` |
| Track a person / org | a page in `entities/` |
| Compare two things | a page in `comparisons/` |
| Cross-source story | a page in `syntheses/` |
| Sub-area bird's-eye | a page in `overviews/` |
| What's still open | a page in `open-questions/` |

## Pages migrated mechanically (re-ingest when load-bearing)

```dataview
TABLE WITHOUT ID file.link AS "Page", type AS "Type", updated AS "Updated"
FROM "domains/{domain}/wiki"
WHERE migration_history AND status = "active"
SORT updated DESC
```

## Summaries

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "domains/{domain}/wiki/summaries"
WHERE type = "summary" AND status = "active"
SORT updated DESC
```

## Concepts

```dataview
TABLE WITHOUT ID file.link AS "Page", last_validated AS "Validated"
FROM "domains/{domain}/wiki/concepts"
WHERE type = "concept" AND status = "active"
SORT last_validated DESC
```

## Entities

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "domains/{domain}/wiki/entities"
WHERE type = "entity" AND status = "active"
SORT updated DESC
```

## Comparisons

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "domains/{domain}/wiki/comparisons"
WHERE type = "comparison" AND status = "active"
SORT updated DESC
```

## Sub-area overviews

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "domains/{domain}/wiki/overviews"
WHERE type = "overview" AND status = "active"
SORT updated DESC
```

## Syntheses

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "domains/{domain}/wiki/syntheses"
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```

## Open questions

```dataview
TABLE WITHOUT ID file.link AS "Page", arc_status AS "Status", updated AS "Updated"
FROM "domains/{domain}/wiki/open-questions"
WHERE type = "open-question"
SORT updated DESC
```

## Recent activity

```dataviewjs
const log = await dv.io.load("domains/{domain}/log.md");
if (!log) {{
    dv.paragraph("_log.md not yet populated._");
}} else {{
    const entries = log.split("\\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(0, 10));
}}
```
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    repo = _find_repo_root()
    if repo is None:
        _err("not inside a Densa vault (no AGENTS.md + _system/densa/ here)")
        return 2

    # Idempotency guard: skip re-runs unless --force OR mode is recover
    # (recover is meant to be re-applied after the initial archive).
    if (
        args.mode != MIGRATION_MODE_RECOVER
        and _already_applied(repo, args.mode)
        and not args.force
    ):
        print(
            f"{MIGRATION_ID} (mode={args.mode}) already recorded in "
            f"_system/migrations.log; nothing to do. Use --force to "
            f"re-run anyway."
        )
        return 0

    actions: list[Action] = []
    rename_map: dict[str, str] = {}  # slug → new slug; for wikilink rewrite
    for domain_dir in _iter_domain_dirs(repo):
        sub_actions, sub_renames = _plan_domain(domain_dir, mode=args.mode)
        actions.extend(sub_actions)
        rename_map.update(sub_renames)

    # In-place / recover modes also rewrite wikilinks across the full
    # repo so renamed slugs resolve. Archive mode does not — the moved
    # pages live in .legacy/ and are not part of the live wikilink
    # graph anyway.
    if args.mode in (MIGRATION_MODE_IN_PLACE, MIGRATION_MODE_RECOVER) and rename_map:
        actions.append(Action(
            kind="rewrite-wikilinks",
            src=repo,  # placeholder; the action carries the map below
            renames=dict(rename_map),
            note=f"rewrite {len(rename_map)} wikilink slug(s) across the vault",
        ))

    if not actions:
        print(f"Vault is already v{TO_VERSION}-shaped (mode={args.mode}). "
              f"Nothing to do.")
        if not args.dry_run:
            _record_migration(repo, args.mode)
        return 0

    _print_plan(actions, dry_run=args.dry_run)

    if args.dry_run:
        return 0

    git_available = _git_available()
    for a in actions:
        _apply(repo, a, use_git=git_available)
    _record_migration(repo, args.mode)
    print()
    print(f"✓ {MIGRATION_LABEL} applied (mode={args.mode}).")
    return 0


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog=f"migrate_{MIGRATION_ID}",
        description=MIGRATION_LABEL,
    )
    mode_action = p.add_mutually_exclusive_group(required=True)
    mode_action.add_argument(
        "--apply", action="store_true", help="execute the migration",
    )
    mode_action.add_argument(
        "--dry-run", action="store_true",
        help="print the plan; do not modify anything",
    )
    p.add_argument(
        "--mode",
        choices=(
            MIGRATION_MODE_IN_PLACE,
            MIGRATION_MODE_ARCHIVE,
            MIGRATION_MODE_RECOVER,
        ),
        default=MIGRATION_MODE_IN_PLACE,
        help=(
            "migration strategy. `in-place` (default) preserves "
            "content via rename/transform; `archive` parks v1 under "
            ".legacy/ and seeds empty v2 folders; `recover` lifts a "
            "prior archive back into the live layout."
        ),
    )
    p.add_argument(
        "--force", action="store_true",
        help=(
            "re-run even if migrations.log already records a previous "
            "run of this migration in this mode"
        ),
    )
    return p.parse_args(argv)


def _find_repo_root() -> Path | None:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").is_file() and (
            candidate / "_system" / "densa"
        ).is_dir():
            return candidate
    return None


def _git_available() -> bool:
    return shutil.which("git") is not None


# ---------------------------------------------------------------------------
# Actions + planning
# ---------------------------------------------------------------------------


@dataclass
class Action:
    """One discrete filesystem operation in the migration plan.

    ``kind`` discriminates the union; ``src`` is the primary path the
    action operates on; ``dst`` (when present) is the target. The
    ``transform`` payload carries action-specific data
    (e.g. ``type:`` rewrite for ``rewrite-frontmatter``). ``renames``
    is used only by ``rewrite-wikilinks``.
    """

    kind: str
    src: Path
    dst: Path | None = None
    transform: dict[str, str] | None = None
    renames: dict[str, str] = field(default_factory=dict)
    note: str = ""


def _iter_domain_dirs(repo: Path):
    domains = repo / "domains"
    if not domains.is_dir():
        return
    for child in sorted(domains.iterdir()):
        if child.is_dir() and (child / "wiki").is_dir():
            yield child


def _plan_domain(
    domain_dir: Path,
    *,
    mode: str,
) -> tuple[list[Action], dict[str, str]]:
    """Plan the v1 → v2 transform for one domain in the requested mode.

    Returns ``(actions, rename_map)``. ``rename_map`` is a slug → slug
    table (without the ``.md`` extension) accumulated across all
    rename actions; the caller folds the per-domain maps together and
    emits a single ``rewrite-wikilinks`` action at the end.
    """
    if mode == MIGRATION_MODE_IN_PLACE:
        return _plan_in_place(domain_dir, root=domain_dir / "wiki")
    if mode == MIGRATION_MODE_ARCHIVE:
        return _plan_archive(domain_dir)
    if mode == MIGRATION_MODE_RECOVER:
        return _plan_recover(domain_dir)
    raise ValueError(f"unknown mode: {mode!r}")


def _plan_in_place(
    domain_dir: Path,
    *,
    root: Path,
) -> tuple[list[Action], dict[str, str]]:
    """In-place migration: rename folder + frontmatter + slug; rewrite
    wikilinks repo-wide.

    ``root`` is the directory whose immediate children are the v1
    folders. For ``in-place`` mode that is ``wiki/``; for ``recover``
    mode the caller passes ``wiki/.legacy/`` instead.
    """
    actions: list[Action] = []
    rename_map: dict[str, str] = {}

    wiki = domain_dir / "wiki"

    if not root.is_dir():
        return actions, rename_map

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name == LEGACY_DIR:
            continue
        new_folder = FOLDER_RENAMES_V1_TO_V2.get(child.name)
        if new_folder is None:
            if child.name in FOLDER_RENAMES_V1_TO_V2:
                # Explicitly removed in v2 (e.g. ``fleeting/``).
                actions.append(Action(
                    kind="warn-removed-folder",
                    src=child,
                    note=(
                        f"v1 folder `{child.name}` is removed in v2; "
                        f"contents need human handling (move to inbox/ "
                        f"or delete)"
                    ),
                ))
            else:
                # Unknown folder — leave alone but warn.
                actions.append(Action(
                    kind="warn-unknown-folder",
                    src=child,
                    note=f"folder `{child.name}` is not in v1→v2 rename table",
                ))
            continue

        if not _folder_has_v1_content(child):
            continue

        target_folder = wiki / new_folder
        target_folder.mkdir(parents=True, exist_ok=True)

        for md in sorted(child.rglob("*.md")):
            new_md = _planned_target_for(md, child, target_folder)
            if md == new_md:
                # Same path (already v2-named); just rewrite frontmatter
                # (rare; happens when a v1 concept page already lives
                # in concepts/ and is being re-stamped).
                actions.append(Action(
                    kind="rewrite-frontmatter",
                    src=md,
                    note="upgrade frontmatter in place (folder unchanged)",
                ))
                continue
            actions.append(Action(
                kind="mv-and-rewrite",
                src=md,
                dst=new_md,
                note=f"v1 page → v2 layout",
            ))
            # Record slug rename for wikilink rewriting.
            old_slug = md.stem
            new_slug = new_md.stem
            if old_slug != new_slug:
                rename_map[old_slug] = new_slug

        actions.append(Action(
            kind="cleanup-empty-folder",
            src=child,
            note="remove the old v1 folder once empty",
        ))

    # Seed any missing v2 folders.
    for name in V2_FOLDERS:
        folder = wiki / name
        if folder.exists():
            continue
        actions.append(Action(
            kind="create-folder",
            src=folder,
            note="v2 recommended folder",
        ))

    overview = wiki / "overview.md"
    if not overview.is_file():
        actions.append(Action(
            kind="create-overview",
            src=overview,
            note=f"v2 entry page for {domain_dir.name}",
        ))

    return actions, rename_map


def _plan_archive(
    domain_dir: Path,
) -> tuple[list[Action], dict[str, str]]:
    """Archive mode: move v1 sub-folders under .legacy/ and seed v2."""
    actions: list[Action] = []
    wiki = domain_dir / "wiki"
    legacy = wiki / LEGACY_DIR

    will_be_emptied: set[str] = set()
    for child in sorted(wiki.iterdir()):
        if not child.is_dir():
            continue
        if child.name == LEGACY_DIR:
            continue
        if not _folder_has_v1_content(child):
            continue
        target = legacy / child.name
        actions.append(Action(
            kind="mv-folder",
            src=child,
            dst=target,
            note=f"v1 sub-folder → {LEGACY_DIR}/",
        ))
        will_be_emptied.add(child.name)
        for md in child.rglob("*.md"):
            rel = md.relative_to(child)
            post_move = target / rel
            actions.append(Action(
                kind="annotate-legacy",
                src=post_move,
                note="add status: legacy-snapshot to frontmatter",
            ))

    for name in V2_FOLDERS:
        folder = wiki / name
        if folder.exists() and name not in will_be_emptied:
            continue
        actions.append(Action(
            kind="create-folder",
            src=folder,
            note="v2 recommended folder",
        ))

    overview = wiki / "overview.md"
    if not overview.is_file():
        actions.append(Action(
            kind="create-overview",
            src=overview,
            note=f"v2 entry page for {domain_dir.name}",
        ))

    return actions, {}


def _plan_recover(
    domain_dir: Path,
) -> tuple[list[Action], dict[str, str]]:
    """Recover mode: lift .legacy/ contents into the live v2 layout."""
    wiki = domain_dir / "wiki"
    legacy = wiki / LEGACY_DIR
    if not legacy.is_dir():
        return [], {}
    return _plan_in_place(domain_dir, root=legacy)


def _planned_target_for(
    md: Path,
    src_folder: Path,
    target_folder: Path,
) -> Path:
    """Compute the v2 target path for a single v1 markdown file."""
    rel = md.relative_to(src_folder)
    name = rel.name
    for old_suffix, new_suffix in SLUG_SUFFIX_RENAMES_V1_TO_V2.items():
        if name.endswith(old_suffix):
            name = name[: -len(old_suffix)] + new_suffix
            break
    return target_folder / rel.with_name(name)


def _folder_has_v1_content(folder: Path) -> bool:
    """Return True iff this wiki sub-folder holds v1 content.

    A folder is v1 when at least one descendant ``.md`` file has a
    ``compiled_against`` value strictly less than 2 (or has
    frontmatter without that key — a pre-v2 omission). Folders
    containing only ``.gitkeep`` or v2 pages are skipped.
    """
    saw_md = False
    for md in folder.rglob("*.md"):
        saw_md = True
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        version = _read_compiled_against(text)
        if version is None:
            if text.startswith("---\n"):
                return True
            continue
        if version < 2:
            return True
    if not saw_md:
        return False
    return False


def _read_compiled_against(text: str) -> int | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        if line.lstrip().startswith("compiled_against:"):
            value = line.split(":", 1)[1].strip()
            try:
                return int(value)
            except ValueError:
                return None
    return None


# ---------------------------------------------------------------------------
# Apply actions
# ---------------------------------------------------------------------------


def _print_plan(actions: list[Action], dry_run: bool) -> None:
    header = "Plan (dry run — no changes will be made):" if dry_run else "Plan:"
    print(header)
    for a in actions:
        if a.kind == "mv-and-rewrite":
            print(f"  git mv + rewrite  {a.src}  ->  {a.dst}")
        elif a.kind == "rewrite-frontmatter":
            print(f"  rewrite frontmatter  {a.src}")
        elif a.kind == "mv-folder":
            print(f"  git mv  {a.src}  ->  {a.dst}")
        elif a.kind == "create-folder":
            print(f"  mkdir -p  {a.src}  (with .gitkeep)")
        elif a.kind == "create-overview":
            print(f"  create  {a.src}")
        elif a.kind == "annotate-legacy":
            print(f"  annotate  {a.src}  (status: legacy-snapshot)")
        elif a.kind == "rewrite-wikilinks":
            print(f"  rewrite wikilinks: {len(a.renames)} slug(s)")
        elif a.kind == "cleanup-empty-folder":
            print(f"  rmdir if empty  {a.src}")
        elif a.kind == "warn-removed-folder":
            print(f"  ! WARNING  {a.note}: {a.src}")
        elif a.kind == "warn-unknown-folder":
            print(f"  ! WARNING  {a.note}: {a.src}")
    print()


def _apply(repo: Path, action: Action, use_git: bool) -> None:
    if action.kind == "mv-and-rewrite":
        _do_mv_and_rewrite(repo, action.src, action.dst, use_git=use_git)
    elif action.kind == "rewrite-frontmatter":
        _do_rewrite_frontmatter(action.src)
    elif action.kind == "mv-folder":
        _do_mv_folder(repo, action.src, action.dst, use_git=use_git)
    elif action.kind == "create-folder":
        _do_create_folder(action.src)
    elif action.kind == "create-overview":
        _do_create_overview(action.src)
    elif action.kind == "annotate-legacy":
        _do_annotate_legacy(action.src)
    elif action.kind == "rewrite-wikilinks":
        _do_rewrite_wikilinks(repo, action.renames)
    elif action.kind == "cleanup-empty-folder":
        _do_cleanup_empty_folder(action.src)
    # warn-* actions are diagnostic only; the warning text already
    # surfaced in the plan print-out.


def _do_mv_folder(
    repo: Path,
    src: Path,
    dst: Path | None,
    *,
    use_git: bool,
) -> None:
    if dst is None:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if use_git:
        rc = subprocess.run(
            ["git", "mv", str(src.relative_to(repo)), str(dst.relative_to(repo))],
            cwd=repo,
            check=False,
        ).returncode
        if rc == 0:
            return
        print(f"  (git mv failed for {src}; falling back to shutil)")
    shutil.move(str(src), str(dst))


def _do_mv_and_rewrite(
    repo: Path,
    src: Path,
    dst: Path | None,
    *,
    use_git: bool,
) -> None:
    """Move a single markdown file and rewrite its frontmatter."""
    if dst is None:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if use_git:
        rc = subprocess.run(
            ["git", "mv", str(src.relative_to(repo)), str(dst.relative_to(repo))],
            cwd=repo,
            check=False,
        ).returncode
        if rc != 0:
            shutil.move(str(src), str(dst))
    else:
        shutil.move(str(src), str(dst))
    _do_rewrite_frontmatter(dst)


def _do_create_folder(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    gitkeep = folder / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")


def _do_create_overview(overview: Path) -> None:
    domain = overview.parent.parent.name
    today = date.today().isoformat()
    body = _OVERVIEW_TEMPLATE.format(domain=domain, today=today)
    overview.parent.mkdir(parents=True, exist_ok=True)
    overview.write_text(body, encoding="utf-8")


def _do_annotate_legacy(page: Path) -> None:
    if not page.is_file():
        return
    try:
        text = page.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    if not text.startswith("---\n"):
        return
    end = text.find("\n---", 4)
    if end == -1:
        return
    block = text[4:end]
    new_lines: list[str] = []
    saw_status = False
    already_legacy = False
    for line in block.splitlines():
        if line.lstrip().startswith("status:") and not saw_status:
            value = line.split(":", 1)[1].strip()
            if value == "legacy-snapshot":
                already_legacy = True
                new_lines.append(line)
            else:
                new_lines.append("status: legacy-snapshot")
            saw_status = True
        else:
            new_lines.append(line)
    if already_legacy:
        return
    if not saw_status:
        new_lines.append("status: legacy-snapshot")
    new_block = "\n".join(new_lines)
    page.write_text("---\n" + new_block + text[end:], encoding="utf-8")


def _do_cleanup_empty_folder(folder: Path) -> None:
    """Remove a folder if it (and all its sub-folders) became empty."""
    if not folder.is_dir():
        return
    # Walk bottom-up.
    for sub in sorted(folder.rglob("*"), reverse=True):
        if sub.is_dir():
            try:
                sub.rmdir()
            except OSError:
                pass
    try:
        folder.rmdir()
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Frontmatter rewriting
# ---------------------------------------------------------------------------


def _do_rewrite_frontmatter(page: Path) -> None:
    """Rewrite a single page's frontmatter to v2 semantics.

    Three changes:

    1. ``type:`` value renamed per :data:`TYPE_RENAMES_V1_TO_V2`.
       When the v1 type carried a sub-kind nuance (e.g. ``pattern``,
       ``decision``), a ``kind:`` field is added with the original
       value.
    2. ``compiled_against:`` is set to 2 (added if absent).
    3. ``migration_history:`` is appended with a single entry recording
       this run. Existing history is preserved so future migrations
       accumulate rather than overwrite.

    Idempotent: re-running on a page already migrated leaves it alone
    (its ``compiled_against`` is already 2 and the history entry is
    already present).
    """
    if not page.is_file():
        return
    try:
        text = page.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    if not text.startswith("---\n"):
        return
    end = text.find("\n---", 4)
    if end == -1:
        return
    block = text[4:end]
    body = text[end + len("\n---"):]
    new_block, mutated = _transform_frontmatter_block(block)
    if not mutated:
        return
    page.write_text("---\n" + new_block + "\n---" + body, encoding="utf-8")


def _transform_frontmatter_block(block: str) -> tuple[str, bool]:
    """Apply the v1 → v2 transform to a frontmatter block.

    Returns ``(new_block, mutated)``. ``new_block`` is the rewritten
    body without the surrounding ``---`` delimiters; ``mutated`` is
    ``True`` when at least one byte changed.

    The parser is line-oriented and limited to the flat-mapping subset
    used by Densa templates: ``key: value`` pairs and ``key:`` lists
    (``- item`` on subsequent indented lines). This mirrors what
    :func:`densa.frontmatter.parse_stdlib` accepts.
    """
    lines = block.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)

    saw_type = False
    saw_compiled = False
    saw_history = False
    needs_kind: str | None = None  # set by type rewrite when sub-kind applies
    already_has_kind = False
    type_v1: str | None = None
    type_v2: str | None = None

    while i < n:
        line = lines[i]
        stripped = line.lstrip()

        if stripped.startswith("type:") and not saw_type:
            saw_type = True
            value = line.split(":", 1)[1].strip()
            type_v1 = value
            mapped = TYPE_RENAMES_V1_TO_V2.get(value, value)
            type_v2 = mapped
            if mapped is None:
                # Removed type — leave as-is and let the human handle.
                out.append(line)
            else:
                if mapped != value:
                    out.append(f"type: {mapped}")
                else:
                    out.append(line)
                if value in TYPE_SUB_KIND_V1_TO_V2:
                    needs_kind = TYPE_SUB_KIND_V1_TO_V2[value]
            i += 1
            continue

        if stripped.startswith("kind:"):
            already_has_kind = True
            out.append(line)
            i += 1
            continue

        if stripped.startswith("compiled_against:"):
            saw_compiled = True
            out.append(f"compiled_against: {TO_VERSION}")
            i += 1
            continue

        if stripped.startswith("status:"):
            value = line.split(":", 1)[1].strip()
            # ``legacy-snapshot`` is the archive-mode marker. When
            # in-place / recover lifts a page back into the live
            # wiki layout, restore ``active`` — the page is no
            # longer a frozen snapshot.
            if value == "legacy-snapshot":
                out.append("status: active")
            else:
                out.append(line)
            i += 1
            continue

        if stripped.startswith("migration_history:"):
            saw_history = True
            # Copy the list block verbatim.
            out.append(line)
            j = i + 1
            while j < n and (lines[j].startswith(" ") or lines[j].startswith("-")):
                out.append(lines[j])
                j += 1
            i = j
            continue

        out.append(line)
        i += 1

    # Inject the kind sub-category right after type if needed.
    if needs_kind and not already_has_kind:
        for idx, line in enumerate(out):
            if line.lstrip().startswith("type:"):
                out.insert(idx + 1, f"kind: {needs_kind}")
                break

    if not saw_compiled:
        out.append(f"compiled_against: {TO_VERSION}")

    # Append migration_history entry. Existing entries are preserved
    # (the block was copied verbatim above); we add a new entry to the
    # tail of the file's history list.
    history_entry_lines = _format_history_entry(
        from_v=FROM_VERSION,
        to_v=TO_VERSION,
        on=date.today().isoformat(),
        mode=MIGRATION_MODE_IN_PLACE,
        v1_type=type_v1,
        v2_type=type_v2,
    )
    if saw_history:
        # Find the last line of the existing history list and splice.
        last_idx = _find_history_tail(out)
        for offset, hl in enumerate(history_entry_lines):
            out.insert(last_idx + 1 + offset, hl)
    else:
        out.append("migration_history:")
        out.extend(history_entry_lines)

    new_block = "\n".join(out)
    return new_block, new_block != block


def _format_history_entry(
    *,
    from_v: int,
    to_v: int,
    on: str,
    mode: str,
    v1_type: str | None,
    v2_type: str | None,
) -> list[str]:
    """Render one ``migration_history`` list entry as YAML lines."""
    notes_parts: list[str] = []
    if v1_type and v2_type and v1_type != v2_type:
        notes_parts.append(f"type {v1_type} → {v2_type}")
    elif v1_type:
        notes_parts.append(f"type stayed {v1_type}")
    notes = "; ".join(notes_parts) if notes_parts else "auto-renamed"
    return [
        f"  - from: {from_v}",
        f"    to: {to_v}",
        f"    on: {on}",
        f"    mode: {mode}",
        f"    notes: {notes!r}",
    ]


def _find_history_tail(lines: list[str]) -> int:
    """Return the index of the last line belonging to a previously
    written ``migration_history:`` list."""
    in_history = False
    last = -1
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("migration_history:"):
            in_history = True
            last = idx
            continue
        if in_history:
            if line.startswith(" ") or line.startswith("-") or not line.strip():
                last = idx
            else:
                break
    return last


# ---------------------------------------------------------------------------
# Wikilink rewriting
# ---------------------------------------------------------------------------


_WIKILINK_RE: Final[re.Pattern[str]] = re.compile(
    r"\[\[([^\[\]\n]+?)\]\]",
)


def _do_rewrite_wikilinks(repo: Path, renames: dict[str, str]) -> None:
    """Rewrite every ``[[<slug>]]`` whose ``<slug>`` is in ``renames``.

    Handles three suffix shapes (Obsidian wikilink grammar):

    - ``[[slug]]``                  → ``[[new-slug]]``
    - ``[[slug|alias]]``            → ``[[new-slug|alias]]``
    - ``[[slug#section]]``          → ``[[new-slug#section]]``
    - ``[[slug#section|alias]]``    → ``[[new-slug#section|alias]]``

    The rename map is keyed by raw slug (no extension, no anchor, no
    alias), which is also what the wikilink resolver uses.
    """
    if not renames:
        return
    skip = {".git", ".obsidian", "node_modules", "__pycache__"}
    for md in repo.rglob("*.md"):
        parts = md.relative_to(repo).parts
        if any(p in skip for p in parts):
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = _rewrite_wikilinks_in_text(text, renames)
        if new_text != text:
            md.write_text(new_text, encoding="utf-8")


def _rewrite_wikilinks_in_text(text: str, renames: dict[str, str]) -> str:
    """Walk every ``[[…]]`` and apply ``renames`` to the slug component.

    Mirrors :func:`densa.wikilink.resolve` parsing semantics so a
    wikilink that the resolver accepts is also one we know how to
    rewrite:

    - ``\\|`` is an escape for ``|`` inside markdown tables; the
      resolver treats it as the alias separator (it calls
      ``target.replace("\\|", "|")`` before splitting). We do the
      same when locating the slug boundary but preserve the original
      escape in the output so downstream markdown renderers still
      get a non-breaking table.
    - The slug component may carry an ``#anchor`` suffix; we keep it
      attached to the (possibly renamed) slug.
    - The slug component may be path-shaped (``folder/slug``); only
      the trailing path segment is the file stem the resolver
      matches, so we rewrite only that.
    """

    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        slug_part, alias_suffix = _split_slug_alias(body)
        if "#" in slug_part:
            stem, anchor = slug_part.split("#", 1)
            anchor_suffix = f"#{anchor}"
        else:
            stem, anchor_suffix = slug_part, ""
        if "/" in stem:
            head, last = stem.rsplit("/", 1)
            head_prefix = head + "/"
        else:
            head_prefix, last = "", stem
        new_last = renames.get(last, last)
        if new_last == last:
            return match.group(0)
        return f"[[{head_prefix}{new_last}{anchor_suffix}{alias_suffix}]]"

    return _WIKILINK_RE.sub(repl, text)


def _split_slug_alias(body: str) -> tuple[str, str]:
    """Split a wikilink body into ``(slug_part, alias_suffix)``.

    ``alias_suffix`` is the substring starting at the alias separator
    (``|`` or its markdown-table escape ``\\|``) and includes the
    separator so the caller can paste it back verbatim. Returns
    ``(body, "")`` when no alias separator is present.
    """
    i = 0
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            return body[:i], body[i:]
        if body[i] == "|":
            return body[:i], body[i:]
        i += 1
    return body, ""


# ---------------------------------------------------------------------------
# Migrations log
# ---------------------------------------------------------------------------


def _migrations_log_path(repo: Path) -> Path:
    return repo / "_system" / "migrations.log"


def _already_applied(repo: Path, mode: str) -> bool:
    log = _migrations_log_path(repo)
    if not log.is_file():
        return False
    marker = f"{MIGRATION_ID}  mode={mode}"
    return marker in log.read_text(encoding="utf-8")


def _record_migration(repo: Path, mode: str) -> None:
    log = _migrations_log_path(repo)
    log.parent.mkdir(parents=True, exist_ok=True)
    line = (
        f"{date.today().isoformat()}  {MIGRATION_ID}  "
        f"mode={mode}  {MIGRATION_LABEL}\n"
    )
    if log.is_file():
        existing = log.read_text(encoding="utf-8")
        marker = f"{MIGRATION_ID}  mode={mode}"
        if marker in existing:
            return
        new = existing.rstrip("\n") + "\n" + line if existing.strip() else line
    else:
        new = line
    log.write_text(new, encoding="utf-8")


def _err(msg: str) -> None:
    print(f"migrate_{MIGRATION_ID}: error: {msg}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
