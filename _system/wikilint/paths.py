"""Pure path classifiers — predicates over repo-relative paths.

Everything here takes a repo-relative path string (forward slashes) and
returns ``bool``. No filesystem I/O; no git; no string parsing of the
file's contents. Keeping these pure makes them trivially unit-testable
and reusable across rules.
"""

from __future__ import annotations

from typing import Final

from wikilint.config import WIKILINK_SKIP_TOP_LEVEL


def normalise(path: str) -> str:
    """Convert backslashes to forward slashes. Idempotent."""
    return path.replace("\\", "/")


def parts(path: str) -> list[str]:
    """Split a repo-relative path into segments (forward-slash normalised)."""
    return normalise(path).split("/")


def is_raw(path: str) -> bool:
    """True iff *path* lies under any ``raw/`` directory.

    Matches any ``.../raw/<something>`` pattern. Does **not** treat the
    bare ``raw/`` directory itself as raw — only its contents.
    """
    p = parts(path)
    return "raw" in p and p.index("raw") < len(p) - 1


def is_log(path: str) -> bool:
    """True iff *path* is a ``log.md`` at any depth (global or per-domain)."""
    p = normalise(path)
    return p == "log.md" or p.endswith("/log.md")


_DOMAIN: Final[str] = "domains"
_WIKI: Final[str] = "wiki"
_LEGACY: Final[str] = ".legacy"


def is_wiki(path: str) -> bool:
    """True iff *path* is a wiki markdown file subject to frontmatter checks.

    Layout: ``domains/<X>/wiki/<bucket>/<file>.md``. The ``.legacy/``
    subtree is excluded because legacy snapshots are deliberate
    pre-redo material that may not match the current schema.
    """
    p = parts(path)
    if len(p) < 4:
        return False
    if p[0] != _DOMAIN or p[2] != _WIKI:
        return False
    if not p[-1].endswith(".md"):
        return False
    return _LEGACY not in p


def is_outputs(path: str) -> bool:
    """True iff *path* is under ``outputs/``.

    ``outputs/`` is in git but deliberately excluded from the wikilink
    graph: lint reports cite wiki pages, never the other way around.
    The bare ``outputs`` directory itself is not classified as an
    output artifact.
    """
    p = parts(path)
    return len(p) > 1 and p[0] == "outputs"


def is_output_artifact(path: str) -> bool:
    """True iff *path* is an ``outputs/`` artifact subject to frontmatter checks.

    Layout: ``outputs/<bucket>/<file>.md`` (e.g. ``outputs/lint/<date>.md``,
    ``outputs/snapshots/index-snapshot.md``). The bare ``outputs/README.md``
    is exempt — it is human-readable explanation, not an operation
    artifact.
    """
    p = parts(path)
    return (
        len(p) >= 3
        and p[0] == "outputs"
        and p[-1].endswith(".md")
    )


def wikilinks_scoped(path: str) -> bool:
    """True iff wikilink resolvability is enforced for *path*.

    Excluded:
      - Anything under ``raw/`` (immutable, may legitimately reference
        external material).
      - Anything under ``outputs/`` (operation artifacts; reports may
        reference wiki pages but their own outbound wikilinks are not
        graph-relevant and the directory is excluded by design).
      - Anything under ``_system/`` / ``attic/`` / ``inbox/`` (templates,
        prompts, AGENTS docs — all of which contain ``[[<placeholder>]]``
        examples by design).
      - Any ``AGENTS.md`` file (L1 or L2), for the same reason.
      - Non-markdown files.
    """
    if not normalise(path).endswith(".md") or is_raw(path):
        return False
    if is_outputs(path):
        return False
    p = parts(path)
    if p[0] in WIKILINK_SKIP_TOP_LEVEL:
        return False
    return p[-1] != "AGENTS.md"
