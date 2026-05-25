"""AGENTS011 — prompt-schema-sync.

Each operation prompt under ``_system/prompts/<op>.md`` (e.g. ``ingest.md``,
``query.md``, ``lint.md``, ``process-inbox.md``, ``promote.md``) must
carry a top-of-file ``## What this command will write`` section whose
markdown table mirrors :data:`densa.schema.OperationSpec.writes`. The
table's first column is the canonical ``WriteSpec.path`` (with
``<X>`` / ``<slug>`` placeholders, surrounded by backticks).

When the prompt table drifts from the schema (the AI added a new
write target to one but not the other, or the schema added an entry
the prompt hasn't reflected yet), this rule warns. The prompt is
treated as a human view of the schema; the schema is the source of
truth.

WARNING (not ERROR) by design: prompt prose is loose-ish, and a stale
prompt won't *break* the validator. But every prompt-vs-schema drift
is a "the AI changed the rules and forgot a file" signal — the exact
failure mode this rule defends against.
"""

from __future__ import annotations

import re

from densa.paths import normalise, parts
from densa.report import Diagnostic, Report, Severity
from densa.schema import operation_by_name
from densa.wikilink import SlugIndex

_RULE_ID = "AGENTS011"
_PROMPTS_DIR = "_system/prompts"


# Match the first `## What this command will write` heading and capture
# everything up until the next `##` or end-of-file. The heading title
# may carry trailing text (e.g. `(schema contract)`); we anchor on the
# leading phrase only.
_SECTION_RE = re.compile(
    r"^##\s+What this command will write[^\n]*\n(.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)


class PromptSchemaSync:
    id: str = _RULE_ID

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None:
        op_name = _classify(path)
        if op_name is None:
            return
        op = operation_by_name(op_name)
        if op is None:
            return  # Not an operation prompt (e.g. README in prompts/).

        m = _SECTION_RE.search(text)
        if m is None:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    f"AGENTS011 prompt-schema-sync: missing "
                    f"`## What this command will write` section. "
                    f"This prompt must mirror "
                    f"densa.schema.OPERATIONS['{op_name}'].writes; "
                    f"add a table near the top of the file with the "
                    f"columns Path | When | Why."
                ),
            ))
            return

        rows = _parse_table_rows(m.group(1))
        if not rows:
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    f"AGENTS011 prompt-schema-sync: section "
                    f"`What this command will write` has no table rows. "
                    f"Populate from "
                    f"densa.schema.OPERATIONS['{op_name}'].writes."
                ),
            ))
            return

        expected = [w.path for w in op.writes]
        observed = [_strip_path_cell(row[0]) for row in rows]

        missing = [p for p in expected if p not in observed]
        extra = [p for p in observed if p not in expected]
        if not missing and not extra:
            return

        details: list[str] = []
        if missing:
            details.append(
                "missing rows: " + ", ".join(f"`{p}`" for p in missing)
            )
        if extra:
            details.append(
                "unexpected rows: " + ", ".join(f"`{p}`" for p in extra)
            )
        report.add(Diagnostic(
            rule_id=self.id,
            severity=Severity.WARNING,
            path=path,
            line=1,
            message=(
                f"AGENTS011 prompt-schema-sync: prompt Write-contract "
                f"table drifts from "
                f"densa.schema.OPERATIONS['{op_name}'].writes. "
                f"{'; '.join(details)}. Update either the prompt "
                f"table or schema.py to reconverge."
            ),
        ))


def _classify(path: str) -> str | None:
    """Return the operation name for an op-level prompt, else ``None``.

    Matches ``_system/prompts/<op>.md`` where ``<op>`` is one of the
    operation names. Sub-prompts under ``_system/prompts/domains/`` are
    excluded because they extend an op rather than re-declare its
    write contract.
    """
    p = parts(normalise(path))
    if len(p) != 3:
        return None
    if p[0] != "_system" or p[1] != "prompts":
        return None
    if not p[2].endswith(".md"):
        return None
    return p[2][: -len(".md")]


def _parse_table_rows(block: str) -> list[tuple[str, ...]]:
    """Parse the body rows of the first markdown table in ``block``.

    Returns a list of cell-tuples (header and separator rows excluded).
    Stops at the first non-table line after the table has started, so
    prose interleaved with the table is tolerated.
    """
    rows: list[tuple[str, ...]] = []
    saw_separator = False
    in_table = False
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        in_table = True
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if _is_separator_row(cells):
            saw_separator = True
            continue
        if saw_separator:
            rows.append(tuple(cells))
    return rows


def _is_separator_row(cells: list[str]) -> bool:
    """Detect a markdown table separator like ``| --- | :---: | ---: |``."""
    if not cells:
        return False
    for c in cells:
        if not c:
            return False
        # Only `-`, `:`, and whitespace allowed.
        if any(ch not in "-: " for ch in c):
            return False
        # Must contain at least one dash.
        if "-" not in c:
            return False
    return True


def _strip_path_cell(cell: str) -> str:
    """Strip backticks, surrounding whitespace, and stray markdown."""
    s = cell.strip()
    if s.startswith("`") and s.endswith("`") and len(s) >= 2:
        s = s[1:-1]
    return s.strip()
