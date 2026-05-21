"""L1 schema constants + stable rule registry.

This file is the **single source of truth** for the schema enforced by
the validator. The human-readable mirror lives in `AGENTS.md` §3 / §6 of
the repo; keep the two in sync via the procedure in
``docs/DESIGN.md`` §"Engineering hooks".

Rule IDs follow a stable convention: ``AGENTS``-prefix + zero-padded
three-digit number, where the number is monotonically allocated and
**never reused**. Re-numbering a rule is a breaking change for users
who pin ``# noqa: AGENTS003`` in their pages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

SCHEMA_VERSION: Final[int] = 1
"""Mirrors the ``schema_version`` in /AGENTS.md frontmatter.

Bumping this here without shipping a migration script under
``_system/scripts/migrate_NN_<slug>.py`` is a contract violation. See
the L1 §3.2 procedure.
"""


# --- Allowed wiki page types ----------------------------------------------

ALLOWED_TYPES: Final[frozenset[str]] = frozenset({
    "source",
    "entity",
    "concept",
    "pattern",
    "session",
    "analysis",
    "synthesis",
    "protocol",
    "experiment",
    "project",
    "stakeholder",
    "decision",
    "theme",
    "framework",
    "question",
    "fleeting",
    "correction",
    "report",
})
"""See AGENTS.md §3 frontmatter schema."""


REQUIRED_FRONTMATTER_KEYS: Final[tuple[str, ...]] = (
    "type",
    "domain",
    "created",
    "updated",
    "status",
)
"""Universal frontmatter contract. L2 schemas add more keys; lint
delegates those to :func:`wikilint.checks.l2_extensions.check`.
"""


# --- Bypass env vars ------------------------------------------------------

LOG_REORDER_BYPASS_ENV: Final[str] = "WIKI_ALLOW_LOG_REORDER"
"""Sanctioned narrow exception to log append-only — see L1 §6 and
:class:`wikilint.checks.log_append_only.LogAppendOnly`.
"""


CROSS_SCOPE_BYPASS_ENV: Final[str] = "WIKI_ALLOW_CROSS_SCOPE"
"""Sanctioned narrow exception to AGENTS007 — see L1 §2.0 and
:class:`wikilint.checks.operation_writes_scope.OperationWritesScope`.
"""


# --- Path classifiers (string-set constants) ------------------------------

SKIP_DIRS: Final[frozenset[str]] = frozenset({
    ".git",
    ".obsidian",
    ".cursor",
    "node_modules",
    "__pycache__",
})
"""Directories never walked when building the slug index."""


WIKILINK_SKIP_TOP_LEVEL: Final[frozenset[str]] = frozenset({
    "_system",
    "attic",
    "inbox",
    "outputs",
})
"""Top-level directories whose markdown files contain ``[[placeholder]]``
examples by design — wikilink resolvability is not enforced there.

``outputs/`` is included here for symmetry with
:func:`wikilint.paths.is_outputs`; the canonical exclusion happens in
``wikilinks_scoped``.
"""


# --- Operation writes (AGENTS007) -----------------------------------------

OPERATION_WRITES: Final[dict[str, frozenset[str]]] = {
    "ingest": frozenset({
        "domains/*/wiki/**",
        "domains/*/log.md",
        "log.md",
    }),
    "query": frozenset({
        "outputs/qa/**",
        "domains/*/log.md",
        "log.md",
    }),
    "lint": frozenset({
        "outputs/**",
        "domains/*/log.md",
        "log.md",
    }),
    "process-inbox": frozenset({
        "domains/*/raw/**",
        "domains/*/log.md",
        "log.md",
    }),
    "promote": frozenset({
        "outputs/qa/**",
        "domains/*/wiki/**",
        "domains/*/log.md",
        "log.md",
    }),
    "": frozenset({
        "_system/**",
        "docs/**",
        "integrations/**",
        "outputs/**",
        "projects/**",
        "writing/**",
        "AGENTS.md",
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
        ".gitignore",
        ".gitattributes",
        ".gitattributes.example",
        ".editorconfig",
        ".pre-commit-hooks.yaml",
        "pyproject.toml",
        "index.md",
        "*.md",
    }),
}
"""Per-operation write-scope whitelist enforced by AGENTS007.

Keys mirror commit-message prefixes (``ingest``, ``query``, ``lint``,
``process-inbox``, ``promote``). The empty string ``""`` key is the
``(no prefix)`` fallback: schema/docs/integrations maintenance. Each
value is a frozenset of *glob patterns* relative to the repo root.

L1 §2.0 is the human-readable mirror of this table.
"""


# --- Rule registry --------------------------------------------------------

@dataclass(frozen=True)
class RuleSpec:
    """Metadata for one rule, independent of its implementation.

    The implementation lives in :mod:`wikilint.checks`; this class only
    carries the things humans look up: the stable ID, a short name for
    error messages, a one-line description, and the anchor in
    ``AGENTS.md`` it enforces.
    """

    id: str
    name: str
    summary: str
    agents_anchor: str
    default_enabled: bool = True

    @property
    def slug(self) -> str:
        """Lowercase-kebab alias for the rule (matches Python class name
        in kebab case)."""
        return self.name.lower().replace("_", "-")


RULES: Final[tuple[RuleSpec, ...]] = (
    RuleSpec(
        id="AGENTS001",
        name="raw-immutability",
        summary="raw/ files cannot be modified, deleted, or renamed",
        agents_anchor="AGENTS.md §6",
    ),
    RuleSpec(
        id="AGENTS002",
        name="log-append-only",
        summary="log.md is append-only; past entries cannot be rewritten",
        agents_anchor="AGENTS.md §6",
    ),
    RuleSpec(
        id="AGENTS003",
        name="frontmatter-required-keys",
        summary="wiki pages must declare type/domain/created/updated/status",
        agents_anchor="AGENTS.md §3",
    ),
    RuleSpec(
        id="AGENTS004",
        name="frontmatter-type-allowed",
        summary="frontmatter `type` must be in the allowed set",
        agents_anchor="AGENTS.md §3",
    ),
    RuleSpec(
        id="AGENTS005",
        name="analysis-sources-cardinality",
        summary="`type: analysis` pages must list exactly one source wikilink",
        agents_anchor="AGENTS.md §3.1",
    ),
    RuleSpec(
        id="AGENTS006",
        name="wikilink-resolvable",
        summary="every `[[wikilink]]` must resolve to some file in the repo",
        agents_anchor="AGENTS.md §4",
    ),
    RuleSpec(
        id="AGENTS007",
        name="operation-writes-within-scope",
        summary=(
            "each commit's staged paths must lie within the write scope "
            "declared for its commit-message prefix"
        ),
        agents_anchor="AGENTS.md §2.0",
    ),
)


@dataclass(frozen=True)
class Config:
    """Runtime configuration for one lint run.

    Built by ``cli.py`` from command-line arguments. The runner reads
    this and passes the relevant bits down to each rule.
    """

    select: frozenset[str] = field(default_factory=frozenset)
    """If non-empty, only rules whose ``id`` is in this set run."""

    ignore: frozenset[str] = field(default_factory=frozenset)
    """Rules in this set are skipped, even if they would otherwise run."""

    no_warnings: bool = False
    """Drop ``Severity.WARNING`` diagnostics from output (does not affect
    exit code, which already ignores warnings)."""

    def is_enabled(self, rule_id: str) -> bool:
        if self.select:
            return rule_id in self.select and rule_id not in self.ignore
        return rule_id not in self.ignore


def rule_by_id(rule_id: str) -> RuleSpec | None:
    for spec in RULES:
        if spec.id == rule_id:
            return spec
    return None


def rule_by_name(name: str) -> RuleSpec | None:
    for spec in RULES:
        if spec.name == name:
            return spec
    return None
