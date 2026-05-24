"""YAML frontmatter parsing.

Two backends are provided:

- ``parse_stdlib``  — pure stdlib regex parser. Handles the limited YAML
  subset used by template frontmatter: scalar values, inline lists
  (``[a, b]``), and block lists (``- foo`` on the next line). Does
  **not** support nested mappings, anchors, refs, or multi-line strings.
- ``parse_pyyaml``  — full YAML via the optional ``pyyaml`` dependency.
  Use this in ``--all`` / ``--ci`` modes and tests.

The default :func:`parse` is **stdlib-only** unless the user opts into
pyyaml explicitly by setting ``DENSA_STRICT=1`` in the environment.
This keeps validator behaviour deterministic across machines: a clone
with pyyaml on the global ``site-packages`` no longer silently parses
differently from a clone without it. Rules should call :func:`parse`
(or one of the explicit backends in tests).

The contract returned by all backends is identical:

    parse(text) -> dict[str, Any] | None

Returning ``None`` means "no leading ``---`` delimiter was found"
(i.e. the file has no frontmatter at all). An empty dict means "found
``---`` block but it parsed to no key/value pairs".
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable
from typing import Any, Final

_FRONTMATTER_DELIM_RE = re.compile(
    r"\A---\n(.*?)(?:\n)?---(?:\n|\Z)", re.DOTALL,
)
_KV_RE = re.compile(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$")
_LIST_ITEM_RE = re.compile(r"^\s+-\s+")


def _extract_block(text: str) -> str | None:
    """Return the inner YAML of the frontmatter block, or ``None``.

    Strips a leading UTF-8 BOM and normalises CRLF → LF before matching
    so that Windows-authored or BOM-prefixed wiki pages don't silently
    appear to have no frontmatter (which would then surface as a false
    AGENTS003 missing-keys error).
    """
    normalised = text.lstrip("\ufeff").replace("\r\n", "\n")
    m = _FRONTMATTER_DELIM_RE.match(normalised)
    return m.group(1) if m else None


def _strip_quotes(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    return v


def _split_inline_list(inner: str) -> list[str]:
    """Split ``a, "b, c", 'd'`` respecting quote-balanced commas."""
    out: list[str] = []
    buf = ""
    quote = ""
    for ch in inner:
        if quote:
            buf += ch
            if ch == quote:
                quote = ""
        elif ch in ('"', "'"):
            quote = ch
            buf += ch
        elif ch == ",":
            if buf.strip():
                out.append(_strip_quotes(buf))
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(_strip_quotes(buf))
    return out


def parse_stdlib(text: str) -> dict[str, Any] | None:
    """Pure-stdlib parser. See module docstring for the supported subset."""
    block = _extract_block(text)
    if block is None:
        return None

    lines = block.split("\n")
    fields: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        kv = _KV_RE.match(line)
        if not kv:
            i += 1
            continue
        key, rest = kv.group(1), kv.group(2).strip()
        if rest == "":
            items: list[str] = []
            j = i + 1
            while j < len(lines) and _LIST_ITEM_RE.match(lines[j]):
                items.append(_strip_quotes(_LIST_ITEM_RE.sub("", lines[j]).strip()))
                j += 1
            fields[key] = items if items else ""
            i = j
        elif rest.startswith("[") and rest.endswith("]"):
            fields[key] = _split_inline_list(rest[1:-1])
            i += 1
        else:
            fields[key] = _strip_quotes(rest)
            i += 1
    return fields


def parse_pyyaml(text: str) -> dict[str, Any] | None:
    """Full-YAML parser. Raises :class:`ImportError` if pyyaml absent."""
    import yaml  # noqa: PLC0415  (lazy import; optional dep)

    block = _extract_block(text)
    if block is None:
        return None
    loaded = yaml.safe_load(block)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(
            f"frontmatter root is {type(loaded).__name__}, expected mapping",
        )
    return loaded


_STRICT_ENV: Final[str] = "DENSA_STRICT"


def _pick_default_backend() -> Callable[[str], dict[str, Any] | None]:
    """Pick the default parser.

    Stdlib is the deterministic default. Users opt into pyyaml by
    setting ``DENSA_STRICT=1``; if pyyaml is missing in that case
    we emit a one-line stderr banner and fall back to stdlib (rather
    than crashing the validator at import time).
    """
    if os.environ.get(_STRICT_ENV) != "1":
        return parse_stdlib
    try:
        import yaml  # noqa: F401, PLC0415
    except ImportError:
        print(
            f"{_STRICT_ENV}=1 set but pyyaml is not installed; "
            f"falling back to stdlib parser. "
            f"Install with: pip install -e \".[strict]\"",
            file=sys.stderr,
        )
        return parse_stdlib
    return parse_pyyaml


parse: Callable[[str], dict[str, Any] | None] = _pick_default_backend()
"""Default parser, picked at import time.

Stdlib by default. ``DENSA_STRICT=1`` opts into pyyaml.
"""
