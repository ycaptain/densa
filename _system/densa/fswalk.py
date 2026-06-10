"""Shared vault walk — the one place that decides what "in the vault" means.

Every consumer that enumerates markdown files on disk (the slug index
in :mod:`densa.wikilink`, ``densa --all`` file collection in
:mod:`densa.runner`, and ``densa stats``) goes through
:func:`iter_markdown` so the exclusion rules cannot drift apart:

- :data:`densa.config.SKIP_DIRS` (``.git``, ``.obsidian``, caches…)
  are pruned wholesale.
- Any subdirectory that is its own git checkout is pruned wholesale.
  A nested repo (e.g. an upstream densa working copy kept inside the
  vault, gitignored by the vault) is by definition not part of this
  vault: walking into it pollutes the slug index with foreign pages
  and raises AGENTS006 on its template placeholders. The vault root
  itself is exempt — only *children* of walked directories are tested,
  so the root's own ``.git`` never suppresses the walk.

Unlike :mod:`densa.paths` (pure string predicates, no I/O by
contract), this module deliberately does filesystem I/O — pruning a
nested repo requires a ``.git`` existence check.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from densa.config import SKIP_DIRS


def is_nested_repo_root(directory: Path) -> bool:
    """True iff *directory* carries its own ``.git`` entry.

    Both forms count: a ``.git`` *directory* (ordinary clone) and a
    ``.git`` *file* (linked worktree / submodule gitlink).
    """
    return (directory / ".git").exists()


def iter_markdown(repo: Path) -> Iterator[Path]:
    """Yield repo-relative paths of every markdown file in the vault.

    Walks *repo* top-down, pruning :data:`~densa.config.SKIP_DIRS`
    and nested git checkouts (see module docstring). Directories and
    files are visited in sorted order so the walk is deterministic
    across platforms.
    """
    for dirpath, dirnames, filenames in os.walk(repo):
        here = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in SKIP_DIRS and not is_nested_repo_root(here / d)
        )
        for name in sorted(filenames):
            if name.endswith(".md"):
                yield (here / name).relative_to(repo)
