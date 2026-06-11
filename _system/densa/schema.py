"""Schema-as-data: the single source of truth for Densa's contracts.

Why this module exists
----------------------

Up through schema_version 1, the contracts lived in three places that drifted
silently:

- ``AGENTS.md`` prose described what each operation may write.
- ``_system/prompts/<op>.md`` re-stated the same in step-by-step form.
- ``_system/densa/config.py`` encoded the machine-enforced subset.

When a user asked an AI to "widen ingest's write scope", the AI usually
touched one of the three and left the others stale. The resulting drift
broke schema upgrades.

Schema_version 2 collapses the three into one Python module — this one.
Everything below is treated as data, not code-with-side-effects. Sister
modules (``config``, ``checks.prompt_schema_sync``, ``commands.migrate``)
read from here; markdown documentation (``docs/reference/karpathy-mapping.md``,
``AGENTS.md`` §"Frontmatter schema") mirrors it for humans and is checked for drift by
AGENTS011.

This file is **stdlib-only** at import time so it can be loaded by the
pre-commit hook without paying a YAML-parse cost.

Karpathy lineage
----------------

Every page-type name comes from Karpathy's original llm-wiki gist
(https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
The ``karpathy_term`` field records the original phrase verbatim; see
``docs/reference/karpathy-mapping.md`` for the side-by-side glossary.
"""

from __future__ import annotations

from typing import Final, NamedTuple

# --- Schema version -------------------------------------------------------

SCHEMA_VERSION: Final[int] = 2
"""Current L1 schema version.

Bumping this requires:

1. A new ``Migration`` entry below describing the upgrade path.
2. A migration script under ``_system/scripts/migrate_NN_<slug>.py``
   that idempotently brings v(N-1) vaults forward.
3. AGENTS010 (``schema-version-consistency``) will then surface pages
   still on the old version as errors — ``densa migrate`` is the
   sanctioned fix.
"""


# --- Page types -----------------------------------------------------------

class PageType(NamedTuple):
    """One row of the page-type registry.

    ``folder`` is ``None`` for types that don't live under
    ``domains/<X>/wiki/`` (``source`` lives under ``raw/``, ``report``
    under ``outputs/``).
    """

    name: str
    folder: str | None
    sources_min: int
    sources_max: int | None  # ``None`` means unbounded.
    sources_must_be: str | None  # ``None`` or ``"raw"``.
    description: str
    karpathy_term: str


PAGE_TYPES: Final[tuple[PageType, ...]] = (
    PageType(
        name="summary",
        folder="summaries",
        sources_min=1,
        sources_max=1,
        sources_must_be="raw",
        description=(
            "Reader-facing distillation of one raw source. "
            "1:1 with one raw file."
        ),
        karpathy_term="summary page",
    ),
    PageType(
        name="entity",
        folder="entities",
        sources_min=1,
        sources_max=None,
        sources_must_be=None,
        description=(
            "A person, organisation, or recurring object referenced "
            "across multiple summaries."
        ),
        karpathy_term="entity page",
    ),
    PageType(
        name="concept",
        folder="concepts",
        sources_min=0,
        sources_max=None,
        sources_must_be=None,
        description=(
            "A term or recurring idea worth defining once and citing "
            "from many places."
        ),
        karpathy_term="concept page",
    ),
    PageType(
        name="comparison",
        folder="comparisons",
        sources_min=2,
        sources_max=None,
        sources_must_be=None,
        description=(
            "X vs Y — table or prose contrasting two or more things."
        ),
        karpathy_term="comparison",
    ),
    PageType(
        name="overview",
        folder="overviews",
        sources_min=0,
        sources_max=None,
        sources_must_be=None,
        description=(
            "Bird's-eye view of a sub-area; the kind of page a "
            "newcomer reads first to orient."
        ),
        karpathy_term="overview",
    ),
    PageType(
        name="synthesis",
        folder="syntheses",
        sources_min=2,
        sources_max=None,
        sources_must_be=None,
        description=(
            "Braided narrative weaving two or more sources / "
            "summaries into one story."
        ),
        karpathy_term="synthesis",
    ),
    PageType(
        name="open-question",
        folder="open-questions",
        sources_min=0,
        sources_max=None,
        sources_must_be=None,
        description=(
            "Long-arc empirical question; accumulates an evidence "
            "ledger as new summaries arrive."
        ),
        karpathy_term="open question",
    ),
    PageType(
        name="source",
        folder=None,  # Lives under ``raw/``, not ``wiki/``.
        sources_min=0,
        sources_max=0,
        sources_must_be=None,
        description="Raw material. Immutable.",
        karpathy_term="raw source",
    ),
    PageType(
        name="report",
        folder=None,  # Lives under ``outputs/``, not ``wiki/``.
        sources_min=0,
        sources_max=None,
        sources_must_be=None,
        description=(
            "Operation artifact (lint report, Q&A archive). "
            "In git, but outside the wikilink graph."
        ),
        karpathy_term="(densa extension)",
    ),
)
"""The full type registry. Order is documentation-friendly (Karpathy
order first, densa extensions last)."""


ALLOWED_TYPES: Final[frozenset[str]] = frozenset(pt.name for pt in PAGE_TYPES)
"""Quick set lookup used by AGENTS004."""


WIKI_FOLDERS: Final[tuple[str, ...]] = tuple(
    pt.folder for pt in PAGE_TYPES if pt.folder is not None
)
"""Recommended wiki sub-folder names (one per non-source, non-report type).

Note: folder layout is a *convention*, not a hard rule — the validator
checks ``type`` (frontmatter) and ignores folder names beyond the
``domains/<X>/wiki/`` prefix. L2s may regroup or merge folders as long
as ``type`` stays in :data:`ALLOWED_TYPES`.
"""


def page_type_by_name(name: str) -> PageType | None:
    """Look up a :class:`PageType` by its ``name`` field."""
    for pt in PAGE_TYPES:
        if pt.name == name:
            return pt
    return None


# --- Operations -----------------------------------------------------------

class WriteSpec(NamedTuple):
    """One row of an operation's write contract.

    ``path`` is a glob with ``<X>`` (domain slug) and ``<slug>`` (file
    slug) placeholders. ``when`` is a short human-readable trigger
    ("always", "touched", "new page", "cross-domain"). ``why`` is the
    one-line rationale that surfaces in prompts and lint output.
    """

    path: str
    when: str
    why: str


class OperationSpec(NamedTuple):
    """Per-operation write/read contract.

    Two parallel views of the same operation:

    - :attr:`writes` is the **human-readable promise**: prose-shaped
      paths with ``<X>`` / ``<slug>`` placeholders. Each row carries
      ``when`` (under what condition) and ``why`` (rationale). This is
      what appears in prompts, in ``docs/reference/karpathy-mapping.md``,
      and in lint ``Write contract`` tables. AGENTS011 checks
      prompt-tables against this list.

    - :attr:`scope_globs` is the **enforcement boundary**: the set of
      raw glob patterns AGENTS007 uses to allow / reject staged paths
      in a commit. These are intentionally wider than :attr:`writes`
      because an ingest/lint/promote pass legitimately touches the
      full wiki sub-tree of a domain in ways no static table can
      enumerate up front. Treat :attr:`writes` as a documented minimum
      and :attr:`scope_globs` as the validated maximum.
    """

    name: str
    writes: tuple[WriteSpec, ...]
    scope_globs: tuple[str, ...]
    reads: tuple[str, ...]
    forbids: tuple[str, ...]


OPERATIONS: Final[tuple[OperationSpec, ...]] = (
    OperationSpec(
        name="ingest",
        writes=(
            WriteSpec(
                "domains/<X>/wiki/summaries/<slug>.md",
                "always",
                "1:1 with the raw — one summary per ingest",
            ),
            WriteSpec(
                "domains/<X>/wiki/concepts/<slug>.md",
                "when touched",
                "append Appearances row when the concept is mentioned",
            ),
            WriteSpec(
                "domains/<X>/wiki/entities/<slug>.md",
                "when touched",
                "append Appearances row when the entity is mentioned",
            ),
            WriteSpec(
                "domains/<X>/wiki/open-questions/<slug>.md",
                "when touched",
                "append evidence row when the source bears on an open question",
            ),
            WriteSpec(
                "domains/<X>/wiki/overview.md",
                "when a new page is created",
                "add the new page to the overview mindmap and Dataview blocks",
            ),
            WriteSpec(
                "domains/<X>/log.md",
                "always",
                "audit trail (newest first per AGENTS002)",
            ),
            WriteSpec(
                "log.md",
                "only when cross-domain",
                "global timeline (newest first)",
            ),
        ),
        scope_globs=(
            "domains/*/wiki/**",
            "domains/*/log.md",
            "log.md",
        ),
        reads=(
            "domains/<X>/raw/**",
            "domains/<X>/wiki/**",
            "domains/<X>/AGENTS.md",
            "AGENTS.md",
            "_system/prompts/ingest.md",
        ),
        forbids=(
            "modifying domains/**/raw/**",
            "fetching the web mid-ingest without explicit human approval",
        ),
    ),
    OperationSpec(
        name="query",
        writes=(
            WriteSpec(
                "outputs/qa/<YYYY-MM-DD>-<slug>.md",
                "when the answer is substantive",
                "Q&A artifact; not a wiki page until `promote` runs",
            ),
            WriteSpec(
                "domains/<X>/log.md",
                "always",
                "audit trail",
            ),
            WriteSpec(
                "log.md",
                "only when the query spans ≥2 domains",
                "global timeline",
            ),
        ),
        scope_globs=(
            "outputs/qa/**",
            "domains/*/log.md",
            "log.md",
        ),
        reads=(
            "domains/**/wiki/**",
            "domains/**/AGENTS.md",
            "outputs/qa/**",
            "AGENTS.md",
            "_system/prompts/query.md",
        ),
        forbids=(
            "writing wiki pages directly — use `promote` if a Q&A "
            "earns wiki-grade status",
        ),
    ),
    OperationSpec(
        name="lint",
        writes=(
            WriteSpec(
                "outputs/lint/<YYYY-MM-DD>.md",
                "always",
                "the lint report itself",
            ),
            WriteSpec(
                "outputs/snapshots/index-snapshot.md",
                "always",
                "machine-readable index mirror (refreshed every lint)",
            ),
            WriteSpec(
                "domains/<X>/wiki/<page>.md",
                "additive auto-fix only",
                "missing cross-references / cross-domain tag / index entry",
            ),
            WriteSpec(
                "domains/<X>/log.md",
                "always",
                "audit trail",
            ),
            WriteSpec(
                "log.md",
                "always",
                "global lint timeline",
            ),
        ),
        scope_globs=(
            "outputs/**",
            "domains/*/wiki/**",
            "domains/*/log.md",
            "log.md",
        ),
        reads=(
            "**/*.md",
            "_system/prompts/lint.md",
        ),
        forbids=(
            "deleting wiki pages",
            "renaming wiki pages",
            "rewriting prose without human review",
        ),
    ),
    OperationSpec(
        name="process-inbox",
        writes=(
            WriteSpec(
                "domains/<X>/raw/<bucket>/<slug>",
                "always",
                "git mv from inbox/ into the correct raw bucket",
            ),
            WriteSpec(
                "domains/<X>/log.md",
                "always",
                "audit trail of the move",
            ),
            WriteSpec(
                "log.md",
                "always",
                "global timeline",
            ),
        ),
        scope_globs=(
            "domains/*/raw/**",
            "domains/*/log.md",
            "log.md",
        ),
        reads=(
            "inbox/**",
            "domains/**/AGENTS.md",
            "_system/prompts/process-inbox.md",
        ),
        forbids=(
            "ingesting in the same commit — that is a separate step",
            "modifying any wiki/** page",
        ),
    ),
    OperationSpec(
        name="promote",
        writes=(
            WriteSpec(
                "domains/<X>/wiki/<folder>/<slug>.md",
                "always (created via git mv from outputs/qa/)",
                "the promoted Q&A becomes a first-class wiki page",
            ),
            WriteSpec(
                "outputs/qa/<source>.md",
                "always (the source Q&A is moved away)",
                "git mv preserves history; `git log --follow` traces back",
            ),
            WriteSpec(
                "outputs/lint/<latest>.md",
                "when the latest lint report has a Human-review queue",
                "append residual issues from the promoted Q&A",
            ),
            WriteSpec(
                "domains/<X>/log.md",
                "always",
                "audit trail",
            ),
            WriteSpec(
                "log.md",
                "only when cross-domain",
                "global timeline",
            ),
        ),
        scope_globs=(
            "outputs/qa/**",
            "outputs/lint/**",
            "domains/*/wiki/**",
            "domains/*/log.md",
            "log.md",
        ),
        reads=(
            "outputs/qa/**",
            "outputs/lint/**",
            "domains/**/wiki/**",
            "_system/prompts/promote.md",
        ),
        forbids=(
            "promoting >1 Q&A in a single commit (1:1 granularity)",
            "rewriting the promoted Q&A's claims beyond the mechanical "
            "voice transform documented in the prompt",
        ),
    ),
    OperationSpec(
        name="visualize",
        writes=(
            WriteSpec(
                "domains/<X>/wiki/<folder>/<slug>.md",
                "chart blocks only, on pages whose trigger conditions pass",
                "embed/refresh a chart block (+ data-as-of line) compiled "
                "from the host page's own prose and frontmatter",
            ),
            WriteSpec(
                "domains/<X>/log.md",
                "always",
                "audit trail (newest first per AGENTS002)",
            ),
            WriteSpec(
                "log.md",
                "only when cross-domain",
                "global timeline (newest first)",
            ),
        ),
        scope_globs=(
            "domains/*/wiki/**",
            "domains/*/log.md",
            "index.md",
            "log.md",
        ),
        reads=(
            "domains/<X>/wiki/**",
            "domains/<X>/AGENTS.md",
            "AGENTS.md",
            "_system/prompts/visualize.md",
            "_system/templates/charts/**",
        ),
        forbids=(
            "introducing claims absent from the host page's prose "
            "(charts are compiled, never authored)",
            "charting crisis-card / SI / medication material",
            "reading raw/** except to verify an existing anchor",
        ),
    ),
)


def operation_by_name(name: str) -> OperationSpec | None:
    """Look up an :class:`OperationSpec` by its ``name`` field."""
    for op in OPERATIONS:
        if op.name == name:
            return op
    return None


def operation_writes_globs() -> dict[str, frozenset[str]]:
    """Derive the AGENTS007 ``OPERATION_WRITES`` table from
    :data:`OPERATIONS`.

    Returns a dict keyed by the operation's commit-message prefix
    (e.g. ``"ingest"``) whose value is the frozenset of
    :attr:`OperationSpec.scope_globs` patterns. The ``""`` (no-prefix)
    fallback is **not** included here — it lives in
    :data:`densa.config.OPERATION_WRITES` together with the
    schema/docs/integrations maintenance allow-list.

    The narrower :attr:`OperationSpec.writes` table (which uses
    ``<X>`` / ``<slug>`` placeholders) is for prompts and documentation;
    only ``scope_globs`` is suitable for AGENTS007's runtime matcher.
    """
    return {
        op.name: frozenset(op.scope_globs) for op in OPERATIONS
    }


# --- Canonical-fact rules (used by prompts; not enforced mechanically) ----

CANONICAL_FACTS: Final[tuple[str, ...]] = (
    "Numbers, dates, and verbatim quotes live ONLY in summaries/<slug>.md "
    "with a raw anchor (timestamp or section reference).",
    "concepts/entities/open-questions store wikilinks to summaries, never "
    "restate the underlying fact.",
    "overviews/comparisons/syntheses cite [[summary#section]] anchors, not "
    "the raw directly.",
    "When the same fact would appear in two wiki pages, pick the deepest "
    "page (the one closest to raw) as canonical and have the other link in.",
)
"""Prose rules for preventing data duplication across wiki pages.

Embedded in prompts (so the LLM sees them on every operation) and in
``docs/reference/karpathy-mapping.md`` (so humans see them too). Not
mechanically enforceable in v2 — see ``docs/reference/schema-v2.md``
"Fact duplication checks" for the heuristic ideas tracked for v3.
"""


# --- Migrations -----------------------------------------------------------

# Each migration script may support multiple modes. The default mode
# ``in-place`` is content-preserving (folder rename + type rewrite +
# slug rename + wikilink update + frontmatter ``migration_history``
# stamp), so users do not pay re-ingest costs on every schema bump.
# ``archive`` parks v(N-1) contents under ``wiki/.legacy/`` and seeds
# an empty vN skeleton — useful when the user wants a clean restart.
# ``recover`` undoes a previous archive by lifting ``.legacy/`` contents
# back into the live vN layout with the in-place transform applied.

MIGRATION_MODE_IN_PLACE: Final[str] = "in-place"
MIGRATION_MODE_ARCHIVE: Final[str] = "archive"
MIGRATION_MODE_RECOVER: Final[str] = "recover"

ALL_MIGRATION_MODES: Final[tuple[str, ...]] = (
    MIGRATION_MODE_IN_PLACE,
    MIGRATION_MODE_ARCHIVE,
    MIGRATION_MODE_RECOVER,
)


class Migration(NamedTuple):
    """One entry in the migration ledger.

    ``script`` is a repo-relative path to the migration script.  Each
    script is idempotent (re-running is a noop) so users can re-run
    after a partial failure without fear.  ``supported_modes`` declares
    which of :data:`ALL_MIGRATION_MODES` the script accepts; ``densa
    migrate --mode X`` errors when ``X`` is not in the union of
    supported modes across the chain.

    ``default_mode`` is what ``densa migrate`` uses when the user
    omits ``--mode``. We default to ``in-place`` because content-
    preserving migrations are cheaper for users; ``archive`` is opt-in
    via ``--mode archive`` when a clean restart is wanted.
    """

    from_version: int
    to_version: int
    breaking: bool
    summary: str
    script: str
    supported_modes: tuple[str, ...] = (
        MIGRATION_MODE_IN_PLACE,
        MIGRATION_MODE_ARCHIVE,
        MIGRATION_MODE_RECOVER,
    )
    default_mode: str = MIGRATION_MODE_IN_PLACE


MIGRATIONS: Final[tuple[Migration, ...]] = (
    Migration(
        from_version=1,
        to_version=2,
        breaking=True,
        summary=(
            "Folder rename + type consolidation to Karpathy vocabulary "
            "(`analyses/` → `summaries/`, `frameworks/` → `overviews/`, "
            "`questions/` → `open-questions/`, etc.). The `in-place` "
            "mode (default) preserves all content and stamps each page "
            "with `migration_history`; `archive` mode parks v1 under "
            "`wiki/.legacy/` and seeds empty v2 folders for re-ingest; "
            "`recover` mode reverses a prior `archive` run."
        ),
        script="_system/scripts/migrate_02_karpathy_vocab.py",
    ),
)


def get_migration(from_version: int, to_version: int) -> Migration | None:
    """Look up a :class:`Migration` by its (from, to) version pair."""
    for m in MIGRATIONS:
        if m.from_version == from_version and m.to_version == to_version:
            return m
    return None


# --- v1 → v2 rename tables (consumed by the migration script) -------------

TYPE_RENAMES_V1_TO_V2: Final[dict[str, str | None]] = {
    # Karpathy-vocab realignments
    "analysis": "summary",
    "framework": "overview",
    "pattern": "concept",
    "theme": "overview",
    "protocol": "concept",
    "experiment": "summary",
    "project": "entity",
    "stakeholder": "entity",
    "decision": "entity",
    "session": "source",
    "question": "open-question",
    "correction": "synthesis",
    "fleeting": None,  # removed in v2; flagged for human handling
    # unchanged
    "synthesis": "synthesis",
    "concept": "concept",
    "entity": "entity",
    "comparison": "comparison",
    "overview": "overview",
    "summary": "summary",
    "open-question": "open-question",
    "source": "source",
    "report": "report",
}
"""Maps v1 ``type:`` values to v2 ``type:`` values.

``None`` means the type is removed in v2; the migration script flags
those pages for human handling (typically a ``git mv`` to
``inbox/`` or ``outputs/qa/``) and does not rewrite them
automatically. Type values not in this table are left untouched (a
defence against future L2-specific types).
"""


TYPE_SUB_KIND_V1_TO_V2: Final[dict[str, str]] = {
    # When a v1 type collapses into a more-general v2 type, the
    # original distinction can be preserved as a ``kind:`` field on
    # the migrated page. The migration script writes this kind hint
    # into frontmatter; v2 lint does not enforce it (kinds are L2
    # business), but L2 schemas can pick it up to drive their own
    # Dataview filters.
    "pattern": "pattern",
    "theme": "theme",
    "protocol": "protocol",
    "experiment": "experiment",
    "project": "project",
    "stakeholder": "stakeholder",
    "decision": "decision",
    "correction": "correction",
}


FOLDER_RENAMES_V1_TO_V2: Final[dict[str, str | None]] = {
    "analyses": "summaries",
    "frameworks": "overviews",
    "questions": "open-questions",
    "patterns": "concepts",
    "themes": "overviews",
    "protocols": "concepts",
    "experiments": "summaries",
    "projects": "entities",
    "stakeholders": "entities",
    "decisions": "entities",
    "corrections": "syntheses",
    "fleeting": None,  # removed; pages move to inbox/ on human review
    # unchanged
    "syntheses": "syntheses",
    "concepts": "concepts",
    "entities": "entities",
    "comparisons": "comparisons",
    "overviews": "overviews",
    "summaries": "summaries",
    "open-questions": "open-questions",
}
"""Maps v1 wiki sub-folder names to v2 folder names.

``None`` means the folder is removed in v2 (pages need human
relocation). Folder names not in this table are left untouched and
flagged for human review (a defence against L2-specific folders).
"""


SLUG_SUFFIX_RENAMES_V1_TO_V2: Final[dict[str, str]] = {
    "-analysis.md": "-summary.md",
    "-analyses.md": "-summaries.md",
}
"""Stem-suffix rewrites for slug renames during in-place migration.

Most wiki pages don't encode their type into the filename; these two
are exceptions because v1 ``-analysis.md`` is the most common
type-flavoured slug pattern. The migration script applies these
substitutions whose corresponding wikilinks are then updated repo-
wide.
"""


# --- Karpathy mapping (renamed types from v1 → v2) ------------------------

class KarpathyMapping(NamedTuple):
    """One row of the v1 → v2 type-rename table.

    ``v1_type`` is the old ``type:`` value; ``v2_type`` is the new one
    (or ``None`` if the type is removed in v2 and contents should be
    folded into another type). ``note`` explains the rationale.
    """

    v1_type: str
    v2_type: str | None
    note: str


KARPATHY_MAPPING: Final[tuple[KarpathyMapping, ...]] = (
    KarpathyMapping(
        v1_type="analysis",
        v2_type="summary",
        note="Karpathy used 'summary page'; 'analysis' is too generic.",
    ),
    KarpathyMapping(
        v1_type="synthesis",
        v2_type="synthesis",
        note="Same name — Karpathy used 'synthesis' verbatim.",
    ),
    KarpathyMapping(
        v1_type="concept",
        v2_type="concept",
        note="Same name — Karpathy used 'concept page'.",
    ),
    KarpathyMapping(
        v1_type="entity",
        v2_type="entity",
        note="Same name — Karpathy used 'entity page'.",
    ),
    KarpathyMapping(
        v1_type="framework",
        v2_type="overview",
        note=(
            "'Framework' read as a code framework (React-style). "
            "Most v1 framework pages were sub-area overviews; "
            "fold into overview/ unless the page is truly a single "
            "concept (then -> concept/)."
        ),
    ),
    KarpathyMapping(
        v1_type="pattern",
        v2_type="concept",
        note=(
            "A recurring behavioural pattern is a kind of concept. "
            "Keep the 'recurring' nuance in the body, not in the type."
        ),
    ),
    KarpathyMapping(
        v1_type="theme",
        v2_type="overview",
        note=(
            "A multi-source story arc is best modelled as an "
            "overview of a sub-area, with the story in prose."
        ),
    ),
    KarpathyMapping(
        v1_type="protocol",
        v2_type="concept",
        note=(
            "Clinical / training protocols are concepts with strict "
            "rules; document the rules in the body."
        ),
    ),
    KarpathyMapping(
        v1_type="experiment",
        v2_type="summary",
        note="One experimental run is a kind of source summary.",
    ),
    KarpathyMapping(
        v1_type="project",
        v2_type="entity",
        note="A project is an entity with a lifecycle; track in entity fields.",
    ),
    KarpathyMapping(
        v1_type="stakeholder",
        v2_type="entity",
        note="A stakeholder is a person — the default kind of entity.",
    ),
    KarpathyMapping(
        v1_type="decision",
        v2_type="entity",
        note=(
            "A decision is a long-lived entity with an ADR id and "
            "stakeholder list."
        ),
    ),
    KarpathyMapping(
        v1_type="session",
        v2_type="source",
        note="A therapy / meeting session is a kind of raw source.",
    ),
    KarpathyMapping(
        v1_type="question",
        v2_type="open-question",
        note=(
            "Renamed for clarity: the page is always for *open* "
            "questions that accumulate evidence over time."
        ),
    ),
    KarpathyMapping(
        v1_type="fleeting",
        v2_type=None,
        note=(
            "Short-lived between-session thoughts don't belong in the "
            "wiki — drop them in inbox/ or outputs/qa/ instead."
        ),
    ),
    KarpathyMapping(
        v1_type="correction",
        v2_type="synthesis",
        note=(
            "A failure-mode tracker is a synthesis across multiple "
            "incidents; document in syntheses/ with a 'correction' "
            "tag."
        ),
    ),
    KarpathyMapping(
        v1_type="report",
        v2_type="report",
        note="Same name — operation artifact under outputs/.",
    ),
    KarpathyMapping(
        v1_type="source",
        v2_type="source",
        note="Same name — Karpathy used 'raw source'.",
    ),
    KarpathyMapping(
        v1_type="comparison",  # introduced in v2; v1 collapsed under synthesis
        v2_type="comparison",
        note=(
            "Promoted from a synthesis sub-flavour to a first-class "
            "type because comparisons are the most common reader "
            "request."
        ),
    ),
    KarpathyMapping(
        v1_type="overview",  # introduced in v2 as the per-domain entry
        v2_type="overview",
        note=(
            "Promoted from an implicit pattern (index.md plus a few "
            "framework pages) to a first-class type."
        ),
    ),
)
