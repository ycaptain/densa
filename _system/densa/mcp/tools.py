"""The eight read-only MCP tools and their JSON-Schema declarations.

Each tool is a pure ``(repo, arguments) -> dict`` function. The server
(:mod:`densa.mcp.server`) is the only caller; it wraps the returned dict
as MCP ``content`` and handles transport. Keeping the tools transport-free
makes them unit-testable without a JSON-RPC loop.

The schemas in :data:`TOOL_SCHEMAS` are the runtime mirror of
``_system/densa/mcp/SPEC.md`` — the frozen pre-launch contract. When a
tool's input/output shape changes, update both this module and ``SPEC.md``
(and bump the version in ``SPEC.md`` if the change is post-launch).

This module is stdlib-only, like the rest of the import-time surface of
:mod:`densa`.
"""

from __future__ import annotations

import base64
import bisect
import datetime
import re
import secrets
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final, NamedTuple

from densa import paths
from densa.checks import STAGED_RULES
from densa.config import RULES, Config
from densa.frontmatter import parse as parse_frontmatter
from densa.fswalk import iter_markdown
from densa.report import Severity
from densa.runner import lint_all, lint_paths
from densa.wikilink import (
    ResolutionStatus,
    build_index,
    resolve,
)


class ToolError(Exception):
    """Raised by a tool for a client-visible failure (bad params, missing
    path). The server maps it to a JSON-RPC ``-32602`` error response.
    """

    def __init__(self, message: str, code: int = -32602) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# --- Page model -----------------------------------------------------------

class Page(NamedTuple):
    """One wiki page, with metadata pre-computed and its raw text retained
    for full-text search."""

    path: str
    title: str
    type: str
    domain: str
    updated: str | None
    preview_line: str
    text: str


_FRONTMATTER_RE: Final = re.compile(
    r"\A﻿?---\n.*?\n---[ \t]*(?:\n|\Z)", re.DOTALL,
)
_HEADING_RE: Final = re.compile(r"^#{1,6}\s+(.*)$")
_DATE_RE: Final = re.compile(r"^##\s+\[(\d{4}-\d{2}-\d{2})\]")
_SKIP_PREVIEW_PREFIXES: Final = ("```", "~~~", "---", "|", ">")


def _body_of(text: str) -> str:
    """Return *text* with a leading YAML frontmatter block stripped."""
    return _FRONTMATTER_RE.sub("", text, count=1)


def _first_heading(body: str) -> str | None:
    for line in body.splitlines():
        m = _HEADING_RE.match(line.strip())
        if m:
            return m.group(1).strip()
    return None


def _preview(body: str) -> str:
    """First prose line of *body*, max 120 chars.

    Skips blank lines, ATX headings, and block markers (fences, tables,
    rules, blockquotes) so the picker shows readable text, not syntax.
    Falls back to the first heading's text, then to the empty string.
    """
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith(_SKIP_PREVIEW_PREFIXES):
            continue
        return line[:120]
    heading = _first_heading(body)
    return (heading or "")[:120]


def _domain_of(rel: str, frontmatter: dict[str, Any]) -> str:
    fm_domain = frontmatter.get("domain")
    if isinstance(fm_domain, str) and fm_domain:
        return fm_domain
    parts = paths.parts(rel)
    return parts[1] if len(parts) > 1 and parts[0] == "domains" else ""


def _as_page(repo: Path, rel: str) -> Page | None:
    try:
        text = (repo / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    frontmatter = parse_frontmatter(text) or {}
    body = _body_of(text)
    fm_title = frontmatter.get("title")
    title = (
        fm_title
        if isinstance(fm_title, str) and fm_title
        else (_first_heading(body) or Path(rel).stem)
    )
    fm_type = frontmatter.get("type")
    fm_updated = frontmatter.get("updated")
    return Page(
        path=rel,
        title=title,
        type=fm_type if isinstance(fm_type, str) else "",
        domain=_domain_of(rel, frontmatter),
        updated=fm_updated if isinstance(fm_updated, str) and fm_updated else None,
        preview_line=_preview(body),
        text=text,
    )


def collect_pages(repo: Path) -> list[Page]:
    """Every wiki page (``domains/<X>/wiki/**.md``), sorted by path.

    Uses the shared :func:`~densa.fswalk.iter_markdown` walk, so the same
    exclusions (``SKIP_DIRS``, nested git checkouts) apply as for lint.
    """
    out: list[Page] = []
    for rel_path in iter_markdown(repo):
        rel = str(rel_path).replace("\\", "/")
        if not paths.is_wiki(rel):
            continue
        if (repo / rel).is_symlink():
            # A wiki page is a real file. A symlink could alias raw/ content
            # into the wiki namespace and leak it unfenced — exclude it.
            # (A hardlink shares an inode and is NOT caught here; that is a
            # documented v1 limitation — see mcp/SPEC.md "read_page".)
            continue
        page = _as_page(repo, rel)
        if page is not None:
            out.append(page)
    out.sort(key=lambda p: p.path)
    return out


# --- Cursor (opaque base64, last-path keyed for stability) ----------------

def _encode_cursor(after_path: str) -> str:
    """Encode the last-returned path as an opaque pagination cursor.

    Path-keyed, **not** offset-keyed: resumption is by sort key, so
    inserting or deleting a page between paginated calls never skips or
    duplicates a row (an offset cursor would shift every later row). Both
    paginated tools return path-sorted, path-unique rows, so the last
    path is a stable, total resume key.
    """
    return base64.urlsafe_b64encode(after_path.encode("utf-8")).decode("ascii")


def _decode_cursor(cursor: str | None) -> str | None:
    """Decode an opaque cursor to the path to resume *after*, or ``None``
    for the first page. A malformed cursor is a client error (-32602)."""
    if not cursor:
        return None
    try:
        return base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise ToolError(f"invalid cursor: {cursor!r}") from exc


def _page_window(
    keys: list[str], after: str | None, limit: int
) -> tuple[int, bool]:
    """Resume offset + has-more flag for a path-sorted key list.

    ``after`` is the last path the client already saw; ``bisect_right``
    gives the first index strictly past it (so a since-deleted ``after``
    still resumes at the right place without re-emitting or skipping).
    """
    start = 0 if after is None else bisect.bisect_right(keys, after)
    take = min(limit, max(0, len(keys) - start))
    has_more = start + take < len(keys)
    return start, has_more


def _clamp_limit(value: Any, default: int, maximum: int) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise ToolError(f"limit must be an integer, got {type(value).__name__}")
    if value < 1:
        raise ToolError("limit must be >= 1")
    return min(value, maximum)


# --- Untrusted fence (D+B protocol, AGENTS.md §4.5) -----------------------

def make_salt() -> str:
    """A fresh 4-character hex salt for one ``<untrusted>`` fence."""
    return secrets.token_hex(2)


def untrusted_fence(source: str, content: str, salt: str) -> str:
    """Wrap *content* in an ``<untrusted>`` fence per AGENTS.md §4.5.

    Pre-escape (B): every literal ``</untrusted`` becomes ``&lt;/untrusted``
    so a premature-close attack is structurally impossible.
    Salt-on-close (D): the open and close tags both carry *salt*; a close
    tag whose salt differs is literal source content, not a boundary.
    """
    escaped = content.replace("</untrusted", "&lt;/untrusted")
    return (
        f'<untrusted source="{source}" salt="{salt}">\n'
        f"{escaped}\n"
        f'</untrusted salt="{salt}">'
    )


# --- Domains --------------------------------------------------------------

def _domain_dirs(repo: Path) -> list[str]:
    base = repo / "domains"
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir())


def _log_staleness_days(repo: Path, domain: str) -> int | None:
    log = repo / "domains" / domain / "log.md"
    if not log.is_file():
        return None
    try:
        text = log.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines():
        m = _DATE_RE.match(line)
        if m:
            try:
                when = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                return None
            return (datetime.date.today() - when).days
    return None


# --- Tool: vault_status ---------------------------------------------------

def tool_vault_status(repo: Path, _arguments: dict[str, Any]) -> dict[str, Any]:
    from densa import __version__  # noqa: PLC0415 (lazy: avoids import cycle)

    pages = collect_pages(repo)
    counts_by_domain: dict[str, dict[str, int]] = {}
    for page in pages:
        bucket = counts_by_domain.setdefault(page.domain, {})
        key = page.type or "(untyped)"
        bucket[key] = bucket.get(key, 0) + 1

    domains: list[dict[str, Any]] = []
    for name in _domain_dirs(repo):
        domains.append({
            "name": name,
            "path": f"domains/{name}",
            "page_counts": counts_by_domain.get(name, {}),
            "log_staleness_days": _log_staleness_days(repo, name),
        })
    return {
        "domains": domains,
        "total_pages": len(pages),
        "densa_version": __version__,
    }


# --- Tool: list_domains ---------------------------------------------------

def tool_list_domains(repo: Path, _arguments: dict[str, Any]) -> dict[str, Any]:
    domains: list[dict[str, Any]] = []
    for name in _domain_dirs(repo):
        base = repo / "domains" / name
        domains.append({
            "name": name,
            "path": f"domains/{name}",
            "has_l2": (base / "AGENTS.md").is_file(),
            "has_wiki": (base / "wiki").is_dir(),
            "has_raw": (base / "raw").is_dir(),
        })
    return {"domains": domains}


# --- Tool: list_pages -----------------------------------------------------

def _page_row(page: Page) -> dict[str, Any]:
    return {
        "path": page.path,
        "title": page.title,
        "type": page.type,
        "domain": page.domain,
        "updated": page.updated,
        "preview_line": page.preview_line,
    }


def tool_list_pages(repo: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    pages = collect_pages(repo)
    want_type = arguments.get("type")
    want_domain = arguments.get("domain")
    if want_type:
        pages = [p for p in pages if p.type == want_type]
    if want_domain:
        pages = [p for p in pages if p.domain == want_domain]

    limit = _clamp_limit(arguments.get("limit"), default=50, maximum=200)
    after = _decode_cursor(arguments.get("cursor"))
    start, has_more = _page_window([p.path for p in pages], after, limit)
    window = pages[start : start + limit]
    next_cursor = _encode_cursor(window[-1].path) if window and has_more else None
    return {
        "pages": [_page_row(p) for p in window],
        "next_cursor": next_cursor,
    }


# --- Tool: read_page ------------------------------------------------------

def _resolve_in_repo(repo: Path, rel: str) -> Path:
    target = (repo / rel).resolve()
    repo_resolved = repo.resolve()
    if repo_resolved != target and repo_resolved not in target.parents:
        raise ToolError(f"path escapes the vault: {rel!r}")
    return target


def tool_read_page(repo: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    rel_raw = arguments.get("path")
    if not isinstance(rel_raw, str) or not rel_raw:
        raise ToolError("read_page requires a non-empty 'path' string")
    rel = paths.normalise(rel_raw).lstrip("/")
    target = _resolve_in_repo(repo, rel)
    if not target.is_file():
        raise ToolError(f"path not found: {rel}")
    # Classify raw-ness from the *physical* location of the bytes, not the
    # request path: a symlink under wiki/ that points into raw/ must still
    # be fenced. The untrusted-egress invariant is about content provenance,
    # not the name it was requested under.
    real_rel = paths.normalise(str(target.relative_to(repo.resolve())))
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ToolError(f"cannot read {rel}: {exc}", code=-32603) from exc

    if paths.is_raw(real_rel):
        salt = make_salt()
        return {
            "path": rel,
            "is_raw": True,
            "frontmatter": None,
            "body": untrusted_fence(rel, text, salt),
            "salt": salt,
        }
    frontmatter = parse_frontmatter(text)
    return {
        "path": rel,
        "is_raw": False,
        "frontmatter": frontmatter,
        "body": _body_of(text),
        "salt": None,
    }


# --- Tool: search_wiki ----------------------------------------------------

def tool_search_wiki(repo: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    query = arguments.get("query")
    if not isinstance(query, str) or not query:
        raise ToolError("search_wiki requires a non-empty 'query' string")
    pages = collect_pages(repo)
    want_type = arguments.get("type")
    want_domain = arguments.get("domain")
    if want_type:
        pages = [p for p in pages if p.type == want_type]
    if want_domain:
        pages = [p for p in pages if p.domain == want_domain]

    prefix = bool(arguments.get("prefix", False))
    needle = query.lower()
    rows: list[dict[str, Any]] = []
    if prefix:
        for page in pages:
            if page.title.lower().startswith(needle):
                rows.append({
                    "path": page.path,
                    "title": page.title,
                    "type": page.type,
                    "domain": page.domain,
                    "preview_line": page.preview_line,
                    "line": None,
                })
    else:
        for page in pages:
            for lineno, line in enumerate(page.text.splitlines(), start=1):
                if needle in line.lower():
                    rows.append({
                        "path": page.path,
                        "title": page.title,
                        "type": page.type,
                        "domain": page.domain,
                        "preview_line": line.strip()[:120],
                        "line": lineno,
                    })
                    break

    limit = _clamp_limit(arguments.get("limit"), default=20, maximum=100)
    after = _decode_cursor(arguments.get("cursor"))
    start, has_more = _page_window([r["path"] for r in rows], after, limit)
    window = rows[start : start + limit]
    next_cursor = (
        _encode_cursor(window[-1]["path"]) if window and has_more else None
    )
    return {"results": window, "next_cursor": next_cursor}


# --- Tool: resolve_wikilink -----------------------------------------------

def tool_resolve_wikilink(repo: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    slug = arguments.get("slug")
    if not isinstance(slug, str) or not slug:
        raise ToolError("resolve_wikilink requires a non-empty 'slug' string")
    idx = build_index(repo)
    hint = arguments.get("domain")
    source = (
        f"domains/{hint}/wiki/__picker__.md"
        if isinstance(hint, str) and hint
        else None
    )
    resolution = resolve(slug, idx, source=source)
    if resolution.status is ResolutionStatus.OK:
        return {
            "slug": slug,
            "resolved_path": f"{resolution.hits[0]}.md",
            "ambiguous": False,
            "candidates": [],
        }
    if resolution.status is ResolutionStatus.AMBIGUOUS:
        return {
            "slug": slug,
            "resolved_path": None,
            "ambiguous": True,
            "candidates": [f"{h}.md" for h in resolution.hits],
        }
    return {
        "slug": slug,
        "resolved_path": None,
        "ambiguous": False,
        "candidates": [],
    }


# --- Tool: run_lint -------------------------------------------------------

def _rule_severity(summary: str) -> str:
    return "warning" if summary.lower().lstrip().startswith("warn") else "error"


def _tracked_markdown(repo: Path) -> set[str] | None:
    """Git-tracked markdown paths, or ``None`` if git is unavailable."""
    import subprocess  # noqa: PLC0415 (lazy: keep subprocess off the import path)

    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "ls-files", "*.md", "**/*.md"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return {line.strip() for line in out.splitlines() if line.strip()}


def tool_run_lint(repo: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    select_raw = arguments.get("select")
    select: frozenset[str] = frozenset()
    if select_raw is not None:
        if not isinstance(select_raw, list):
            raise ToolError("'select' must be an array of rule IDs")
        select = frozenset(str(r) for r in select_raw)
    config = Config(select=select)
    include_all = bool(arguments.get("all", False))
    domain = arguments.get("domain")

    if domain is None and include_all:
        report = lint_all(repo, config)
    else:
        candidates = [
            str(rel).replace("\\", "/") for rel in iter_markdown(repo)
        ]
        if domain:
            prefix = f"domains/{domain}/"
            candidates = [p for p in candidates if p.startswith(prefix)]
        if not include_all:
            tracked = _tracked_markdown(repo)
            if tracked is not None:
                candidates = [p for p in candidates if p in tracked]
        report = lint_paths(repo, candidates, config)

    diagnostics = [
        {
            "path": d.path,
            "line": d.line if d.line else None,
            "rule_id": d.rule_id,
            "severity": d.severity.value,
            "message": d.message,
        }
        for d in report.diagnostics
    ]
    errors = sum(1 for d in report.diagnostics if d.severity is Severity.ERROR)
    warnings = sum(1 for d in report.diagnostics if d.severity is Severity.WARNING)
    return {
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "files_checked": report.files_checked,
        },
        "diagnostics": diagnostics,
    }


# --- Tool: list_rules -----------------------------------------------------

def tool_list_rules(_repo: Path, _arguments: dict[str, Any]) -> dict[str, Any]:
    staged_ids = {r.id for r in STAGED_RULES}
    rules = [
        {
            "id": spec.id,
            "name": spec.name,
            "description": spec.summary,
            "severity": _rule_severity(spec.summary),
            "staged_only": spec.id in staged_ids,
        }
        for spec in RULES
        if spec.id.startswith("AGENTS")
    ]
    return {"rules": rules}


# --- Dispatch + schemas ---------------------------------------------------

ToolFn = Callable[[Path, dict[str, Any]], dict[str, Any]]

TOOLS: Final[dict[str, ToolFn]] = {
    "vault_status": tool_vault_status,
    "list_domains": tool_list_domains,
    "list_pages": tool_list_pages,
    "read_page": tool_read_page,
    "search_wiki": tool_search_wiki,
    "resolve_wikilink": tool_resolve_wikilink,
    "run_lint": tool_run_lint,
    "list_rules": tool_list_rules,
}


def call_tool(repo: Path, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    fn = TOOLS.get(name)
    if fn is None:
        raise ToolError(f"unknown tool: {name!r}", code=-32602)
    return fn(repo, arguments)


TOOL_SCHEMAS: Final[list[dict[str, Any]]] = [
    {
        "name": "vault_status",
        "description": (
            "Summary of mounted domains, page counts by type, and log staleness."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_domains",
        "description": "List all mounted domains detected under domains/.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_pages",
        "description": (
            "List wiki pages with optional type/domain filtering and cursor "
            "pagination. Returns title + preview_line + type per page for "
            "@-mention picker rendering."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "domain": {"type": "string"},
                "cursor": {"type": "string"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                },
            },
        },
    },
    {
        "name": "read_page",
        "description": (
            "Read a single page (wiki page or raw source). raw/ paths are "
            "wrapped in an <untrusted> fence (salt-on-close + pre-escape)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "search_wiki",
        "description": (
            "Full-text search over wiki pages (grep). Set prefix=true for "
            "title type-ahead used by the @-mention picker."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "type": {"type": "string"},
                "domain": {"type": "string"},
                "prefix": {"type": "boolean", "default": False},
                "cursor": {"type": "string"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "resolve_wikilink",
        "description": "Resolve a [[slug]] to its canonical repo-relative path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "domain": {"type": "string"},
            },
            "required": ["slug"],
        },
    },
    {
        "name": "run_lint",
        "description": (
            "Run the Densa validator and return structured diagnostics. Lint "
            "violations are returned in the diagnostics array, not as errors."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "select": {"type": "array", "items": {"type": "string"}},
                "all": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "list_rules",
        "description": "List the live AGENTS001-AGENTS0NN rule registry.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]
