"""Runtime view of the contract; raw definitions live in :mod:`densa.schema`.

L1 schema constants + stable rule registry. The data lives in
:mod:`densa.schema`; this file re-exports the bits each check needs in
the shape AGENTS007 / AGENTS009 / AGENTS010 expect, plus the rule
registry.

Why the split? :mod:`densa.schema` is pure data (page types, operations,
migrations, Karpathy mapping); :mod:`densa.config` is the validator's
runtime knobs (rule IDs, bypass env vars, the assembled write-scope
glob table). When the schema changes, you edit ``schema.py``; this file
follows automatically.

Rule IDs follow a stable convention: ``AGENTS``-prefix + zero-padded
three-digit number, where the number is monotonically allocated and
**never reused**. Re-numbering a rule is a breaking change for users
who pin ``# noqa: AGENTS003`` in their pages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from densa.schema import (
    ALLOWED_TYPES as _SCHEMA_ALLOWED_TYPES,
)
from densa.schema import (
    SCHEMA_VERSION as _SCHEMA_VERSION,
)
from densa.schema import (
    operation_writes_globs as _operation_writes_globs,
)

SCHEMA_VERSION: Final[int] = _SCHEMA_VERSION
"""Mirrors the ``schema_version`` in /AGENTS.md frontmatter.

Bumping this requires shipping a migration script under
``_system/scripts/migrate_NN_<slug>.py`` and adding a :class:`Migration`
entry to :data:`densa.schema.MIGRATIONS`. See
``docs/reference/schema-versioning.md`` for the procedure.
"""


# --- Allowed wiki page types ----------------------------------------------

ALLOWED_TYPES: Final[frozenset[str]] = _SCHEMA_ALLOWED_TYPES
"""Derived from :data:`densa.schema.PAGE_TYPES`. See AGENTS.md's
"Frontmatter schema" section."""


REQUIRED_FRONTMATTER_KEYS: Final[tuple[str, ...]] = (
    "type",
    "domain",
    "created",
    "updated",
    "status",
    "compiled_against",
)
"""Universal frontmatter keys whose value MUST be present and non-empty.

AGENTS.md's "Frontmatter schema" section lists nine universal keys;
this tuple covers the six that MUST carry a meaningful value. The
remaining three (``sources``, ``tags``, ``aliases``) are also
universal but **may be empty lists** — see
:data:`PRESENCE_ONLY_FRONTMATTER_KEYS`. The split lets AGENTS003 fire
when a value is missing without inflating false-positives on legitimate
empty lists (e.g. an evergreen concept with ``sources: []``).

L2 schemas add their own required keys (e.g. `last_validated` for
`concept`); those are enforced by AGENTS008 plus the L2's own lint
pass per the L2 AGENTS.md.
"""


PRESENCE_ONLY_FRONTMATTER_KEYS: Final[tuple[str, ...]] = (
    "sources",
    "tags",
    "aliases",
)
"""Universal frontmatter keys that MUST be present but MAY be empty.

AGENTS003 errors when these keys are missing entirely; an empty list
or empty scalar is allowed (e.g. ``sources: []`` for evergreen
concepts). See ``docs/reference/sources-cardinality.md`` for the
per-page-type contract.
"""


# --- Bypass env vars ------------------------------------------------------

LOG_REORDER_BYPASS_ENV: Final[str] = "WIKI_ALLOW_LOG_REORDER"
"""Sanctioned narrow exception to log append-only — see AGENTS.md's
"Red lines" section and
:class:`densa.checks.log_append_only.LogAppendOnly`.
"""


CROSS_SCOPE_BYPASS_ENV: Final[str] = "WIKI_ALLOW_CROSS_SCOPE"
"""Sanctioned narrow exception to AGENTS007 — see AGENTS.md's
"Operation writes" section and
:class:`densa.checks.operation_writes_scope.OperationWritesScope`.
"""


MIGRATION_BYPASS_ENV: Final[str] = "WIKI_ALLOW_MIGRATION"
"""Sanctioned narrow exception to log append-only for migration
commits — see AGENTS.md's "Red lines" section and
:class:`densa.checks.log_append_only.LogAppendOnly`. Inert unless the
same commit stages an addition to ``_system/migrations.log``.
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
    "writing",
    "projects",
    "examples",
    ".github",
})
"""Top-level directories whose markdown files contain ``[[placeholder]]``
examples by design — wikilink resolvability is not enforced there.

``outputs/`` is included here for symmetry with
:func:`densa.paths.is_outputs`; the canonical exclusion happens in
``wikilinks_scoped``.

``writing/`` and ``projects/`` are opt-in workspaces (see
``docs/design/design-rationale.md`` "Optional layers" section):
they may cite wiki pages with ``[[wikilink]]`` but the reverse is
forbidden and their frontmatter is advisory.

``examples/`` holds opt-in showcase domains (e.g.
``examples/showcases/workspace/``) plus the ``hello-world`` demo.
These are reference material, not part of the wikilink graph; their
internal cross-links are pre-validated when shipped and re-validated
in a dedicated CI job, not the main ``densa --all`` pass.

``.github/`` holds GitHub community-health files (``CONTRIBUTING.md`` /
``SECURITY.md`` / ``CODE_OF_CONDUCT.md``) and issue / PR templates.
These are project-process docs, not wiki pages, and reference each
other by relative path — never by ``[[wikilink]]`` — so resolvability
is not enforced there.
"""


# --- Operation writes (AGENTS007) -----------------------------------------

def _build_operation_writes() -> dict[str, frozenset[str]]:
    """Assemble the AGENTS007 write-scope table.

    Per-operation rows come from :data:`densa.schema.OPERATIONS` (so
    edits to operation contracts live in one place). The ``""``
    (no-prefix) row stays hand-maintained here — it covers
    schema/docs/integrations maintenance, which is repo-shaped rather
    than vault-shaped.

    Each operation row is widened with two universal append-only
    targets (``domains/<X>/log.md`` and ``log.md``) when its writes
    already cover narrower paths under those files; without this the
    glob ``domains/<X>/wiki/<slug>.md`` would force every log
    bookkeeping write to also live in the operation's narrow paths.
    """
    table: dict[str, frozenset[str]] = {}
    for op_name, globs in _operation_writes_globs().items():
        # ``op_name`` mirrors the commit-message prefix.
        table[op_name] = frozenset(globs)

    table[""] = frozenset({
        "_system/**",
        "docs/**",
        "examples/**",
        "integrations/**",
        "outputs/**",
        "projects/**",
        "writing/**",
        ".github/**",
        "AGENTS.md",
        "GUIDE.md",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".pre-commit-hooks.yaml",
        "pyproject.toml",
        "noxfile.py",
        "index.md",
        "*.md",
    })
    return table


OPERATION_WRITES: Final[dict[str, frozenset[str]]] = _build_operation_writes()
"""Per-operation write-scope whitelist enforced by AGENTS007.

Keys mirror commit-message prefixes (``ingest``, ``query``, ``lint``,
``process-inbox``, ``promote``). The empty string ``""`` key is the
``(no prefix)`` fallback: schema/docs/integrations maintenance. Each
value is a frozenset of *glob patterns* relative to the repo root.

The per-operation rows are derived from
:data:`densa.schema.OPERATIONS`; edit there to change a contract. The
no-prefix row is maintained inline because it is repo-maintenance
boilerplate, not part of the vault's wiki contract.

AGENTS.md's "Operation writes" section is the human-readable mirror
of this table.
"""


# --- Rule registry --------------------------------------------------------

@dataclass(frozen=True)
class RuleSpec:
    """Metadata for one rule, independent of its implementation.

    The implementation lives in :mod:`densa.checks`; this class only
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
        id="DENSA-IO",
        name="io-failure",
        summary="meta diagnostic: the validator could not read a file",
        agents_anchor="(meta)",
    ),
    RuleSpec(
        id="AGENTS001",
        name="raw-immutability",
        summary="raw/ files cannot be modified, deleted, or renamed",
        agents_anchor='AGENTS.md §"Red lines"',
    ),
    RuleSpec(
        id="AGENTS002",
        name="log-append-only",
        summary="log.md is append-only; past entries cannot be rewritten",
        agents_anchor='AGENTS.md §"Red lines"',
    ),
    RuleSpec(
        id="AGENTS003",
        name="frontmatter-required-keys",
        summary="wiki pages must declare type/domain/created/updated/status",
        agents_anchor='AGENTS.md §"Frontmatter schema"',
    ),
    RuleSpec(
        id="AGENTS004",
        name="frontmatter-type-allowed",
        summary="frontmatter `type` must be in the allowed set",
        agents_anchor='AGENTS.md §"Frontmatter schema"',
    ),
    RuleSpec(
        id="AGENTS005",
        name="analysis-sources-cardinality",
        summary="`type: analysis` pages must list exactly one source wikilink",
        agents_anchor="docs/reference/sources-cardinality.md",
    ),
    RuleSpec(
        id="AGENTS006",
        name="wikilink-resolvable",
        summary="every `[[wikilink]]` must resolve to some file in the repo",
        agents_anchor='AGENTS.md §"Naming and linking conventions"',
    ),
    RuleSpec(
        id="AGENTS007",
        name="operation-writes-within-scope",
        summary=(
            "each commit's staged paths must lie within the write scope "
            "declared for its commit-message prefix"
        ),
        agents_anchor='AGENTS.md §"Operation writes"',
    ),
    RuleSpec(
        id="AGENTS008",
        name="last-validated-fresh",
        summary=(
            "warn when `last_validated` on concept/framework/protocol/entity "
            "is older than 180 days"
        ),
        agents_anchor="docs/reference/schema-versioning.md",
    ),
    RuleSpec(
        id="AGENTS009",
        name="compiled-against-current",
        summary=(
            "warn when a page's `compiled_against` lags the current "
            "schema_version"
        ),
        agents_anchor="docs/reference/schema-versioning.md",
    ),
    RuleSpec(
        id="AGENTS010",
        name="schema-version-consistency",
        summary=(
            "error when wiki pages outside .legacy/ still declare an "
            "older compiled_against — run `densa migrate` to fix"
        ),
        agents_anchor="docs/reference/schema-versioning.md",
    ),
    RuleSpec(
        id="AGENTS011",
        name="prompt-schema-sync",
        summary=(
            "warn when a prompt's Write-contract table drifts from "
            "densa.schema.OPERATIONS"
        ),
        agents_anchor='AGENTS.md §"Operation writes"',
    ),
    RuleSpec(
        id="AGENTS012",
        name="migration-history-hygiene",
        summary=(
            "warn when `migration_history` frontmatter is malformed or "
            "contradicts `compiled_against`"
        ),
        agents_anchor='AGENTS.md §"Upgrading an existing vault"',
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
