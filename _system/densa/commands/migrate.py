"""``densa migrate`` — apply schema migrations to bring a vault to the
current ``SCHEMA_VERSION``.

The flow:

1. Locate the vault root (same heuristics as ``densa upgrade``).
2. Determine the vault's effective schema version by scanning
   ``compiled_against`` frontmatter across all wiki pages outside
   ``.legacy/``. The minimum value is the vault's current version.
3. Compute the chain of :data:`~densa.schema.MIGRATIONS` entries that
   bring that version forward to :data:`~densa.schema.SCHEMA_VERSION`.
4. For each migration in the chain, dispatch to its script
   (``_system/scripts/migrate_NN_<slug>.py``) by invoking it as a
   subprocess with ``--apply`` (or ``--dry-run`` when the user passed
   that flag). The migration scripts are themselves idempotent.

Migrations are intentionally **separate scripts** rather than imported
modules — each one is a one-shot transform that may go on to live
under ``attic/`` once every active vault has applied it. Keeping them
as scripts lets us delete them without breaking the runtime.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from densa.frontmatter import parse
from densa.paths import parts
from densa.schema import (
    ALL_MIGRATION_MODES,
    MIGRATION_MODE_IN_PLACE,
    MIGRATIONS,
    SCHEMA_VERSION,
    Migration,
)


def add_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register ``densa migrate`` with the top-level argparse parser."""
    p = subparsers.add_parser(
        "migrate",
        help="apply schema migrations to bring the vault to the current version",
        description=(
            "Bring this vault's wiki pages forward to the current "
            "SCHEMA_VERSION by running the migration scripts declared "
            "in densa.schema.MIGRATIONS. Each script is idempotent — "
            "re-running after a partial failure is safe."
        ),
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would change; do not apply",
    )
    p.add_argument(
        "--yes", "-y",
        action="store_true",
        help="apply migrations without asking for confirmation",
    )
    p.add_argument(
        "--from-version",
        type=int,
        default=None,
        help=(
            "override the auto-detected starting version; useful for "
            "re-running a specific migration on a vault that already "
            "claims a higher version"
        ),
    )
    p.add_argument(
        "--mode",
        choices=ALL_MIGRATION_MODES,
        default=None,
        help=(
            "migration strategy. `in-place` (default) renames "
            "folder/type/slug + rewrites wikilinks + stamps each page "
            "with `migration_history`, preserving content. `archive` "
            "moves v(N-1) wiki/ contents to wiki/.legacy/ and seeds "
            "empty vN folders for re-ingest. `recover` lifts a prior "
            "archive's .legacy/ contents back into the live layout "
            "with the in-place transform applied. When omitted, the "
            "default declared by each migration in the chain wins; "
            "currently that is `in-place`."
        ),
    )


def run(args: argparse.Namespace) -> int:
    """Execute ``densa migrate``. Returns the CLI exit code."""
    repo = _resolve_repo()
    if repo is None:
        _err("not inside a Densa vault (no AGENTS.md + _system/densa/ here)")
        return 2

    requested_mode: str | None = args.mode
    is_recover_run = requested_mode == "recover"

    if args.from_version is not None:
        current = args.from_version
    elif is_recover_run:
        # ``recover`` is meaningful even when the vault already claims
        # the current schema_version, because the .legacy/ snapshot
        # holds the previous version. Pin ``current`` to the migration
        # immediately below the latest one so the chain is non-empty.
        current = max((m.from_version for m in MIGRATIONS), default=SCHEMA_VERSION - 1)
    else:
        current = _detect_vault_version(repo)

    chain = _migration_chain(current, SCHEMA_VERSION)
    if not chain and not is_recover_run:
        print(
            f"Vault is already at SCHEMA_VERSION={SCHEMA_VERSION}. "
            f"Nothing to migrate."
        )
        return 0

    # Validate the requested mode against the chain.
    if requested_mode is not None:
        unsupported = [
            m for m in chain if requested_mode not in m.supported_modes
        ]
        if unsupported:
            _err(
                f"--mode={requested_mode!r} is not supported by these "
                f"migration(s): "
                + ", ".join(
                    f"v{m.from_version}->v{m.to_version}" for m in unsupported
                )
            )
            return 2

    if is_recover_run:
        print(
            f"Recover mode: targeting the v{current}->v{SCHEMA_VERSION} "
            f"migration regardless of the current schema_version "
            f"(SCHEMA_VERSION={SCHEMA_VERSION}). Looking for legacy "
            f"content under each domain's wiki/.legacy/."
        )
    else:
        print(
            f"Vault is on schema v{current}; current SCHEMA_VERSION="
            f"{SCHEMA_VERSION}."
        )
    print(f"Will apply {len(chain)} migration(s):")
    for m in chain:
        mode_for_step = requested_mode or m.default_mode
        marker = "(BREAKING)" if m.breaking else ""
        print(f"  v{m.from_version} -> v{m.to_version}  mode={mode_for_step}  {marker}")
        print(f"    {m.summary}")
        print(f"    script: {m.script}")

    if args.dry_run:
        print("\n(dry run — no scripts executed)")
        return 0

    if not args.yes:
        choice = input("\nApply these migrations now? [y/N] ").strip().lower()
        if choice not in ("y", "yes"):
            print("Aborted.")
            return 0

    print()
    for m in chain:
        mode_for_step = requested_mode or m.default_mode
        rc = _run_migration(repo, m, dry_run=False, mode=mode_for_step)
        if rc != 0:
            _err(
                f"migration v{m.from_version}->v{m.to_version} failed "
                f"(exit {rc}). Review the output above; the script is "
                f"idempotent, so you can re-run after fixing the issue."
            )
            return rc

    print()
    print("All migrations applied. Next steps:")
    print(f"  1. PYTHONPATH=_system python -m densa --all   (verify)")
    print(f"  2. git status                                 (review the diff)")
    if requested_mode == "archive":
        print(
            f"  3. Re-ingest the sources you still care about under "
            f"v{SCHEMA_VERSION}, then `git rm -r wiki/.legacy/` when "
            f"you no longer need the archive."
        )
    else:
        print(
            f"  3. Look for `migration_history` in frontmatter; pages "
            f"with that field were mechanically migrated and may still "
            f"reflect the v{SCHEMA_VERSION - 1} narrative shape."
        )
        print(
            f"     Pick any of them up later with `ingest` (re-process "
            f"the source) when the prose becomes load-bearing."
        )
    return 0


# --- internals -------------------------------------------------------------


def _resolve_repo() -> Path | None:
    """Walk up from cwd looking for a Densa vault root.

    Mirrors :func:`densa.commands.upgrade._resolve_repo`. We keep a
    local copy because the two share no other code and importing
    upgrade's helper would couple unrelated commands.
    """
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").is_file() and (
            candidate / "_system" / "densa"
        ).is_dir():
            return candidate
    return None


def _detect_vault_version(repo: Path) -> int:
    """Scan wiki pages and return the lowest ``compiled_against`` seen.

    ``.legacy/`` subtrees are skipped — those are intentionally frozen
    at an older version and should not drag the vault floor down.
    """
    lowest: int | None = None
    for md in repo.rglob("*.md"):
        rel_parts = parts(str(md.relative_to(repo)))
        if ".legacy" in rel_parts:
            continue
        # Only wiki pages declare compiled_against.
        if not (len(rel_parts) >= 4 and rel_parts[0] == "domains" and rel_parts[2] == "wiki"):
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = parse(text)
        if not fm:
            continue
        raw = fm.get("compiled_against")
        if raw in (None, ""):
            continue
        try:
            version = int(str(raw).strip())
        except ValueError:
            continue
        if lowest is None or version < lowest:
            lowest = version
    return lowest if lowest is not None else SCHEMA_VERSION


def _migration_chain(
    from_version: int,
    to_version: int,
) -> list[Migration]:
    """Return the ordered list of migrations from ``from_version`` to
    ``to_version``.

    Walks :data:`densa.schema.MIGRATIONS` looking for the connecting
    edges. Returns an empty list when ``from_version >= to_version``.
    Raises :class:`ValueError` when no chain exists.
    """
    if from_version >= to_version:
        return []
    chain: list[Migration] = []
    cursor = from_version
    while cursor < to_version:
        nxt: Migration | None = None
        for m in MIGRATIONS:
            if m.from_version == cursor:
                nxt = m
                break
        if nxt is None:
            raise ValueError(
                f"no migration registered for v{cursor} — cannot reach v{to_version}"
            )
        chain.append(nxt)
        cursor = nxt.to_version
    return chain


def _run_migration(
    repo: Path,
    migration: Migration,
    *,
    dry_run: bool,
    mode: str = MIGRATION_MODE_IN_PLACE,
) -> int:
    """Invoke ``python <migration.script> --apply --mode <mode>`` as a
    subprocess.

    We use a subprocess (rather than importing) so each migration can
    drift freely from the live ``densa.schema``: a future migration
    might need helpers that don't fit the current Python module
    structure, and subprocess isolation keeps that flexibility. The
    same mechanism makes it safe to retire old migration scripts to
    ``attic/`` once every active vault has applied them.
    """
    script_path = repo / migration.script
    if not script_path.is_file():
        _err(f"migration script not found: {migration.script}")
        return 2

    flag = "--dry-run" if dry_run else "--apply"
    argv = [sys.executable, str(script_path), flag, "--mode", mode]
    print(f"--- running {migration.script} {flag} --mode {mode} ---")
    rc = subprocess.run(argv, cwd=repo, check=False).returncode
    print(f"--- {migration.script} exit {rc} ---")
    return rc


def _err(msg: str) -> None:
    print(f"densa migrate: error: {msg}", file=sys.stderr)
