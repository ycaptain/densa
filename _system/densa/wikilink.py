"""Wikilink scanning and resolution.

Obsidian uses ``[[shortest-unique-slug]]`` to link between pages. We
mirror the resolver's behaviour: a target resolves if there's exactly
one file in the repo whose path-without-extension *ends with* the
target's path components.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from densa.config import WIKILINK_SKIP_TOP_LEVEL
from densa.fswalk import iter_markdown

WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
"""Match ``[[anything-but-brackets-or-newline]]``. Greedy non-empty body."""

_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


class ResolutionStatus(str, Enum):
    """How a wikilink resolved against the index."""

    OK = "ok"
    AMBIGUOUS = "ambiguous"
    MISSING = "missing"
    ANCHOR_ONLY = "anchor-only"


@dataclass(frozen=True)
class Resolution:
    status: ResolutionStatus
    hits: tuple[str, ...] = ()


# --- Slug index -----------------------------------------------------------

SlugIndex = dict[str, list[str]]
"""Map ``"slug"`` / ``"sub/path/slug"`` → list of full repo-relative
paths-without-extension that end with that suffix.

The graph-relevant index (built by :func:`build_index`) excludes the
top-level directories listed in
:data:`~densa.config.WIKILINK_SKIP_TOP_LEVEL` so that a bare slug
like ``[[concept]]`` cannot silently resolve to a template / prompt /
artifact under those trees. A second, full-repo path-existence index
(:data:`SlugIndex` returned by :func:`build_index` carries it under
the ``__explicit_paths__`` key) lets explicit-path wikilinks like
``[[_system/templates/concept]]`` continue to resolve.
"""

_EXPLICIT_PATHS_KEY = "__explicit_paths__"


def _walk_markdown(
    repo: Path,
    include_skipped_top_level: bool = False,
) -> Iterator[Path]:
    """Yield markdown paths relative to *repo*.

    By default mirrors the exclusions in
    :func:`densa.paths.wikilinks_scoped`: ``_system/`` / ``attic/`` /
    ``inbox/`` / ``outputs/`` hold templates / prompts / artifacts that
    contain ``[[placeholder]]`` examples by design. Set
    ``include_skipped_top_level=True`` to walk the full repo, used to
    keep explicit-path wikilinks like ``[[_system/templates/concept]]``
    resolving.

    The underlying walk (:func:`densa.fswalk.iter_markdown`) already
    prunes :data:`~densa.config.SKIP_DIRS` and nested git checkouts,
    so foreign repos inside the vault never pollute the slug index.
    """
    for rel in iter_markdown(repo):
        if (
            not include_skipped_top_level
            and rel.parts
            and rel.parts[0] in WIKILINK_SKIP_TOP_LEVEL
        ):
            continue
        yield rel


def build_index(repo: Path) -> SlugIndex:
    """Build the slug → paths map for every markdown file under *repo*.

    Two layers:

    1. Suffix slots, populated only from wiki-graph-relevant files
       (see :func:`_walk_markdown`). A bare ``[[concept]]`` cannot
       resolve to ``_system/templates/concept.md`` this way.
    2. Full repo-relative path set under the internal
       ``__explicit_paths__`` key. Lets :func:`resolve` accept explicit
       paths like ``[[_system/templates/concept]]`` without re-introducing
       the false-resolution bug.
    """
    idx: SlugIndex = {}
    for rel in _walk_markdown(repo):
        no_ext = str(rel.with_suffix("")).replace("\\", "/")
        parts = no_ext.split("/")
        for i in range(len(parts)):
            suffix = "/".join(parts[i:])
            idx.setdefault(suffix, []).append(no_ext)
    explicit: list[str] = []
    for rel in _walk_markdown(repo, include_skipped_top_level=True):
        no_ext = str(rel.with_suffix("")).replace("\\", "/")
        explicit.append(no_ext)
    idx[_EXPLICIT_PATHS_KEY] = explicit
    return idx


# --- Resolution -----------------------------------------------------------

def _domain_prefix(path: str) -> str | None:
    """Return ``"domains/<X>/"`` for a path under a domain, else ``None``.

    Pure string classification of a repo-relative path; files outside
    any ``domains/<X>/`` tree (root ``log.md``, ``index.md``, ...) have
    no domain context.
    """
    p = path.replace("\\", "/").split("/")
    if len(p) > 2 and p[0] == "domains":
        return f"domains/{p[1]}/"
    return None


def resolve(
    target: str,
    idx: SlugIndex,
    source: str | None = None,
) -> Resolution:
    """Resolve a single wikilink body (everything between ``[[`` ``]]``).

    Strips display labels (``slug|Display``), section anchors
    (``slug#section`` or ``slug#^block-id``), and trailing ``.md``.
    Explicit paths (``[[_system/templates/concept]]``, ``[[domains/x/wiki/y]]``)
    are matched against the full repo-relative path set; bare slugs
    are matched against the wiki-graph-relevant suffix index only.

    *source* is the repo-relative path of the file containing the link.
    When a **bare slug** has multiple global matches and the source file
    lives under ``domains/<X>/``, candidates are first filtered to that
    domain (the L2-wins philosophy at the link-resolution layer):
    exactly one same-domain survivor resolves; multiple survivors stay
    ambiguous; zero survivors fall back to the global candidate set so
    cross-domain links keep working. ``source=None`` (or a source
    outside any domain) keeps the historical global-only behaviour.
    """
    target = target.replace("\\|", "|")
    main = target.split("|", 1)[0].split("#", 1)[0].strip()
    main = main[:-3] if main.endswith(".md") else main
    if not main:
        return Resolution(ResolutionStatus.ANCHOR_ONLY)
    hits = sorted(set(idx.get(main, [])))
    if hits:
        if len(hits) > 1 and "/" not in main and source is not None:
            domain = _domain_prefix(source)
            if domain is not None:
                same = [h for h in hits if h.startswith(domain)]
                if len(same) == 1:
                    return Resolution(ResolutionStatus.OK, tuple(same))
        if len(hits) > 1:
            return Resolution(ResolutionStatus.AMBIGUOUS, tuple(hits))
        return Resolution(ResolutionStatus.OK, tuple(hits))
    # Fallback: explicit-path wikilinks (containing "/" and matching a
    # real file in the repo, including templates / prompts / artifacts).
    if "/" in main:
        explicit = idx.get(_EXPLICIT_PATHS_KEY, [])
        if main in explicit:
            return Resolution(ResolutionStatus.OK, (main,))
    return Resolution(ResolutionStatus.MISSING)


# --- Scanning -------------------------------------------------------------

@dataclass(frozen=True)
class WikilinkHit:
    """A single ``[[…]]`` occurrence in a file, with location."""

    lineno: int
    target: str


def scan(text: str) -> Iterator[WikilinkHit]:
    """Yield every wikilink in *text*, skipping fenced and inline code.

    Lines starting with triple backticks or tildes toggle a fence flag;
    inline ``` `code` ``` regions on a line are masked out before
    wikilink matching, so a literal ``[[example]]`` inside backticks
    is not reported as a link.
    """
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        scan_line = _INLINE_CODE_RE.sub(
            lambda m: " " * len(m.group(0)),
            line,
        )
        for m in WIKILINK_RE.finditer(scan_line):
            yield WikilinkHit(lineno=lineno, target=m.group(1).strip())
