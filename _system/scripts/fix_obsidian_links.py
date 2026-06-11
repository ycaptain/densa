#!/usr/bin/env python3
"""Rewrite bucket-relative wikilinks into forms Obsidian can resolve.

The backlog-clearing companion to AGENTS013 (``obsidian-link-format``).
Historic vaults accumulated links like ``[[concepts/x]]`` because the
densa resolver's suffix index accepted them; Obsidian resolves any link
containing ``/`` from the vault root only, so each one renders as a
grey ghost node in the graph and 404s on click. This script retargets
them mechanically:

1. Every wikilink that :func:`densa.wikilink.obsidian_resolvable`
   rejects is resolved through the densa suffix index. A unique match
   (after the same same-domain preference :func:`densa.wikilink.resolve`
   applies) is rewritten.
2. The rewritten form follows AGENTS.md §"Naming and linking
   conventions": the bare ``[[slug]]`` when the basename is unique
   across everything Obsidian indexes (including nested checkouts the
   densa walk prunes), otherwise the full vault path with a display
   alias ``[[domains/<X>/wiki/concepts/x|x]]``. Anchors and existing
   aliases are preserved verbatim.
3. With ``--fuzzy``, links whose suffix has **no** match (typically a
   stale bucket prefix, e.g. ``[[skills/x]]`` for a page that lives in
   ``concepts/``) fall back to a unique-basename match. These rewrites
   are reported separately — review them in the diff.

Scope mirrors AGENTS013 (:func:`densa.paths.wikilinks_scoped`):
``raw/`` (immutable, AGENTS001), every ``log.md`` (append-only,
AGENTS002), ``outputs/``, ``_system/`` etc. are never touched.
Wikilinks inside fenced or inline code are skipped, mirroring
:func:`densa.wikilink.scan`.

Idempotent: a second run finds nothing Obsidian-unresolvable and
changes zero files. Not a schema migration — no ``migrations.log``
entry, no ``compiled_against`` change; run it by hand, review with
``git diff``, commit normally.

Usage::

    python _system/scripts/fix_obsidian_links.py --dry-run
    python _system/scripts/fix_obsidian_links.py --apply
    python _system/scripts/fix_obsidian_links.py --apply --fuzzy
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

# Invoked standalone from the repo root; resolve the densa package the
# same way the migration scripts do.
_HERE = Path(__file__).resolve()
_SYSTEM = _HERE.parent.parent
if str(_SYSTEM) not in sys.path:
    sys.path.insert(0, str(_SYSTEM))

from densa.fswalk import iter_markdown  # noqa: E402
from densa.paths import wikilinks_scoped  # noqa: E402
from densa.wikilink import (  # noqa: E402
    WIKILINK_RE,
    SlugIndex,
    build_index,
    obsidian_resolvable,
)

_INLINE_CODE_RE: Final[re.Pattern[str]] = re.compile(r"`[^`\n]*`")

# Directories Obsidian itself ignores when indexing a vault. Dot-dirs
# (.git, .obsidian, nested checkouts' .git, ...) are skipped wholesale;
# these two are common non-dot noise.
_OBSIDIAN_SKIP: Final[frozenset[str]] = frozenset({
    "node_modules",
    "__pycache__",
})


@dataclass
class Rewrite:
    """One performed (or planned) link rewrite, for the report."""

    path: str
    lineno: int
    old: str
    new: str
    fuzzy: bool = False


@dataclass
class Skip:
    """One link we could not fix, with the reason."""

    path: str
    lineno: int
    target: str
    reason: str  # "ambiguous" | "missing"
    candidates: tuple[str, ...] = ()


@dataclass
class Outcome:
    rewrites: list[Rewrite] = field(default_factory=list)
    skips: list[Skip] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    repo = _find_repo_root()
    if repo is None:
        _err("not inside a Densa vault (no AGENTS.md + _system/densa/ here)")
        return 2

    outcome = run_fix(repo, apply=args.apply, fuzzy=args.fuzzy)
    _print_report(outcome, applied=args.apply)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="fix_obsidian_links",
        description=(
            "rewrite bucket-relative wikilinks (AGENTS013 backlog) into "
            "Obsidian-resolvable form"
        ),
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--apply", action="store_true", help="write the rewrites to disk",
    )
    mode.add_argument(
        "--dry-run", action="store_true",
        help="print the plan; do not modify anything",
    )
    p.add_argument(
        "--fuzzy", action="store_true",
        help=(
            "also retarget links whose path suffix has no match but "
            "whose basename matches exactly one file (stale bucket "
            "prefixes); review these in the diff"
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


# --- core ------------------------------------------------------------------


def run_fix(repo: Path, *, apply: bool, fuzzy: bool) -> Outcome:
    """Scan the vault, plan every rewrite, optionally write them."""
    idx = build_index(repo)
    basenames = _obsidian_basename_counts(repo)
    outcome = Outcome()

    for rel in sorted(iter_markdown(repo)):
        rel_str = rel.as_posix()
        if not wikilinks_scoped(rel_str):
            continue
        md = repo / rel
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = _fix_text(
            text, rel_str, idx, basenames, fuzzy=fuzzy, outcome=outcome,
        )
        if new_text != text:
            outcome.changed_files.append(rel_str)
            if apply:
                md.write_text(new_text, encoding="utf-8")
    return outcome


def _obsidian_basename_counts(repo: Path) -> Counter[str]:
    """Count ``.md`` basenames across everything Obsidian indexes.

    Obsidian's resolver sees the whole vault directory — including
    nested git checkouts that :func:`densa.fswalk.iter_markdown`
    deliberately prunes — but ignores dot-directories. A bare
    ``[[slug]]`` is only safe when the stem is unique in *Obsidian's*
    view, so uniqueness is computed with this wider walk.
    """
    counts: Counter[str] = Counter()
    for _root, dirs, files in os.walk(repo):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in _OBSIDIAN_SKIP
        ]
        for f in files:
            if f.endswith(".md"):
                counts[f[:-3]] += 1
    return counts


def _fix_text(
    text: str,
    rel: str,
    idx: SlugIndex,
    basenames: Counter[str],
    *,
    fuzzy: bool,
    outcome: Outcome,
) -> str:
    """Rewrite one file's text, mirroring ``wikilink.scan`` masking."""
    out_lines: list[str] = []
    in_fence = False
    # splitlines/join would eat a trailing newline; split manually.
    lines = text.split("\n")
    for lineno, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        masked = _INLINE_CODE_RE.sub(
            lambda m: " " * len(m.group(0)), line,
        )
        new_line: list[str] = []
        cursor = 0
        for m in WIKILINK_RE.finditer(masked):
            body = line[m.start(1):m.end(1)]
            replacement = _fix_body(
                body, rel, lineno, idx, basenames,
                fuzzy=fuzzy, outcome=outcome,
            )
            if replacement is None:
                continue
            new_line.append(line[cursor:m.start(1)])
            new_line.append(replacement)
            cursor = m.end(1)
        new_line.append(line[cursor:])
        out_lines.append("".join(new_line))
    return "\n".join(out_lines)


def _fix_body(
    body: str,
    rel: str,
    lineno: int,
    idx: SlugIndex,
    basenames: Counter[str],
    *,
    fuzzy: bool,
    outcome: Outcome,
) -> str | None:
    """Compute the fixed body for one wikilink, or ``None`` to keep it."""
    if obsidian_resolvable(body, idx):
        return None

    main, anchor, alias = _split_body(body)
    target = _resolve_target(main, rel, idx)
    used_fuzzy = False
    if target is None and fuzzy:
        target = _resolve_basename(main, rel, idx)
        used_fuzzy = target is not None
    if target is None:
        outcome.skips.append(Skip(
            path=rel, lineno=lineno, target=main,
            reason=_skip_reason(main, idx),
            candidates=tuple(sorted(idx.get(main, []))),
        ))
        return None

    slug = target.rsplit("/", 1)[-1]
    if basenames.get(slug, 0) == 1:
        new_main = slug
        new_alias = alias
    else:
        new_main = target
        new_alias = alias or f"|{slug}"
    new_body = f"{new_main}{anchor}{new_alias}"
    outcome.rewrites.append(Rewrite(
        path=rel, lineno=lineno, old=body, new=new_body, fuzzy=used_fuzzy,
    ))
    return new_body


def _split_body(body: str) -> tuple[str, str, str]:
    """Split a wikilink body into ``(main, anchor_suffix, alias_suffix)``.

    The alias separator may be the markdown-table escape ``\\|``; both
    suffixes include their separator so the caller can paste them back
    verbatim.
    """
    slug_part, alias_suffix = body, ""
    i = 0
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            slug_part, alias_suffix = body[:i], body[i:]
            break
        if body[i] == "|":
            slug_part, alias_suffix = body[:i], body[i:]
            break
        i += 1
    if "#" in slug_part:
        main, anchor = slug_part.split("#", 1)
        anchor_suffix = f"#{anchor}"
    else:
        main, anchor_suffix = slug_part, ""
    main = main.strip()
    main = main[:-3] if main.endswith(".md") else main
    return main, anchor_suffix, alias_suffix


def _resolve_target(main: str, rel: str, idx: SlugIndex) -> str | None:
    """Unique suffix match for *main*, with same-domain preference.

    Mirrors the candidate filtering in :func:`densa.wikilink.resolve`:
    when multiple files share the suffix and the linking file lives
    under ``domains/<X>/``, a single same-domain candidate wins.
    """
    hits = sorted(set(idx.get(main, [])))
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        domain = _domain_prefix(rel)
        if domain is not None:
            same = [h for h in hits if h.startswith(domain)]
            if len(same) == 1:
                return same[0]
    return None


def _resolve_basename(main: str, rel: str, idx: SlugIndex) -> str | None:
    """Fallback for ``--fuzzy``: unique match on the final segment."""
    stem = main.rsplit("/", 1)[-1]
    if stem == main:
        return None
    return _resolve_target(stem, rel, idx)


def _domain_prefix(path: str) -> str | None:
    p = path.split("/")
    if len(p) > 2 and p[0] == "domains":
        return f"domains/{p[1]}/"
    return None


def _skip_reason(main: str, idx: SlugIndex) -> str:
    return "ambiguous" if idx.get(main) else "missing"


# --- report ------------------------------------------------------------------


def _print_report(outcome: Outcome, *, applied: bool) -> None:
    exact = [r for r in outcome.rewrites if not r.fuzzy]
    fuzzy = [r for r in outcome.rewrites if r.fuzzy]

    verb = "rewrote" if applied else "would rewrite"
    print(f"fix_obsidian_links: {verb} {len(outcome.rewrites)} link(s) "
          f"in {len(outcome.changed_files)} file(s)")
    if exact:
        print(f"\n  exact suffix matches ({len(exact)}):")
        for r in exact:
            print(f"    {r.path}:{r.lineno}  [[{r.old}]] -> [[{r.new}]]")
    if fuzzy:
        print(f"\n  fuzzy basename matches ({len(fuzzy)}) — review these:")
        for r in fuzzy:
            print(f"    {r.path}:{r.lineno}  [[{r.old}]] -> [[{r.new}]]")
    if outcome.skips:
        print(f"\n  left untouched ({len(outcome.skips)}):")
        for s in outcome.skips:
            extra = (
                f" candidates: {', '.join(s.candidates)}"
                if s.candidates else ""
            )
            print(f"    {s.path}:{s.lineno}  [[{s.target}]] "
                  f"({s.reason}){extra}")
    if not applied and outcome.rewrites:
        print("\n(dry run — re-run with --apply to write)")
    if applied and outcome.changed_files:
        print("\nNext: review `git diff`, then run "
              "`PYTHONPATH=_system python -m densa --all`.")


def _err(msg: str) -> None:
    print(f"fix_obsidian_links: error: {msg}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
