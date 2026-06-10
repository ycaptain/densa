# Schema versioning + `last_validated` semantics

Reference companion to
[`AGENTS.md` §"Frontmatter schema"](../../AGENTS.md#3-frontmatter-schema-universal)
(covers `compiled_against` schema versioning and `last_validated`
semantics).

## Schema versioning

The L1 schema carries a single integer version, exposed in two places:

- The frontmatter of [`AGENTS.md`](../../AGENTS.md) (`schema_version`).
- The Python constant
  [`_system/densa/schema.py`](../../_system/densa/schema.py)
  `SCHEMA_VERSION` (re-exported via `_system/densa/config.py` for
  runtime use).

Every wiki page MUST set `compiled_against: <N>` in frontmatter to
record the schema version it was authored under. New pages set it to
the current version; migrations bump it.

### When to bump

Breaking changes only. Examples that warrant a bump:
- A new required frontmatter key.
- A change to the `sources` cardinality contract (see
  [`sources-cardinality.md`](sources-cardinality.md)).
- A `type` enum value removed (additions are non-breaking; the new
  type just won't validate on old pages but old pages stay valid).

### Migration procedure

1. Bump `schema_version` in [`AGENTS.md`](../../AGENTS.md) frontmatter
   and `SCHEMA_VERSION` in `_system/densa/schema.py` (the two must
   stay in lockstep).
2. Ship `_system/scripts/migrate_<NN>_<slug>.py` that idempotently
   brings existing pages forward (re-running it on already-migrated
   pages is a no-op).
3. Append a one-liner to `_system/migrations.log` recording the
   migration: schema version, date, what it does, how to re-run.
4. Document the breaking change in [`CHANGELOG.md`](../../CHANGELOG.md)
   under `## [Unreleased]`.

### What lint does

AGENTS009 surfaces pages whose `compiled_against` lags the current
schema version as `human-review` (warning, not error). A re-ingest
may be needed; pages may still be correct under newer rules but the
audit cannot prove it without an explicit re-validation.

## `last_validated` semantics

Long-lived pages drift silently when their underlying sources evolve.
The `last_validated` field is a self-declared "this page still
reflects what the cited sources say" timestamp.

| `type` | `last_validated` requirement |
| --- | --- |
| concept, framework, protocol, entity | required; bump on any edit that re-checks the cited sources |
| pattern, theme | optional; an L2 may make it equivalent to its own `last_observed` field |
| analysis, synthesis, source, session, question, fleeting | not applicable; these have explicit dates from `created` / `updated` |
| correction, experiment, project, stakeholder, decision | not applicable; freshness is tracked via type-specific fields (`last_observed`, `ends`, `decided_on`, `Appearances`) |
| report | not applicable; operation artifacts have a fixed date in the filename |

AGENTS008 flags pages whose `last_validated` is older than **180
days** as `human-review`.

### Don't auto-stamp

**Auto-applying a fresh stamp without re-reading the cited sources is
a closed-epistemic-loop violation — never do that.** The whole point
of the field is to attest that a human (or the agent on the human's
behalf, mid-ingest) actually re-checked. A stamp without re-checking
makes the entire wiki's freshness signal worthless.

## Migration runbook

When upstream ships a breaking schema change (a bump to
`schema_version`), pull the changes and run the migration:

```bash
python -m densa upgrade          # git fetch + merge upstream
python -m densa migrate          # apply all pending migrations
python -m densa --all            # confirm a clean baseline
```

Each migration script under `_system/scripts/migrate_NN_<slug>.py` is
**idempotent** and supports **three modes** for handling existing
content. `densa migrate` picks each migration's declared default
unless `--mode` overrides:

| `--mode`     | What it does                                                                                         | Use when                                              |
|--------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| `in-place`   | **(default)** Rename folders, types, and slugs in-place. Rewrite frontmatter (`compiled_against` ← new version) and append a `migration_history` entry per page. Rewrite every `[[wikilink]]` across the vault so renamed slugs still resolve. **Content is preserved.** | The common case. Cheap, fast, no re-ingest needed. |
| `archive`    | `git mv` v(N-1) wiki contents to `wiki/.legacy/<bucket>/` and seed empty vN folders. Stamp each parked page with `status: legacy-snapshot`. | You want a clean restart and plan to re-ingest the sources you still care about. |
| `recover`    | Inverse of `archive`. Lift `.legacy/` contents back into the live vN layout with the in-place transform applied. | You ran `archive` and changed your mind. |

The shape of the v1→v2 transform is documented in
[`karpathy-mapping.md` §"Schema_version 1 → 2"](karpathy-mapping.md#schema_version-1--2-what-changed-and-why);
the per-page audit trail (`migration_history`) is documented in
[`karpathy-mapping.md` §"Upgrade modes"](karpathy-mapping.md#upgrade-modes-and-what-migration_history-records).

Pages migrated `in-place` carry their `migration_history` forward —
that audit trail tells you (and future tooling) **which pages were
mechanically renamed but never re-read by the LLM under the new
schema**. The shipped `overview.md` template surfaces them via a
Dataview block; pick them up one at a time with `ingest` when the
prose becomes load-bearing. **AGENTS012** warns when
`migration_history` is malformed or contradicts `compiled_against`.

For multi-version jumps (v1 → v3 / v4 / …), `densa migrate` walks
the declared `MIGRATIONS` chain and applies each step in order. The
chain is read from `densa.schema.MIGRATIONS`; each migration declares
its `from_version`, `to_version`, and supported modes. Future
migrations can opt out of `archive`/`recover` modes (e.g. when the
transform is purely additive and there's no destructive option) by
narrowing their `supported_modes` tuple — `densa migrate --mode X`
errors cleanly if `X` isn't supported by every step in the chain.

Your raw material is never touched by any migration.

### Adopting densa into a pre-existing vault

If you adopted densa by copying upstream `_system/` over an existing
(pre-densa or older-schema) vault, the copy brings along upstream's
`_system/migrations.log` — which already records migrations that ran
against the showcase content, **not** against your vault. That stale
log does not block you: `densa migrate` trusts its own
`compiled_against` scan as ground truth and passes `--force` to each
migration script it dispatches, so a pending migration always runs.
Only when you invoke a migration script **by hand** does its
log-based guard apply — add `--force` yourself in that case.

If your vault has custom v1 wiki folders outside the standard rename
table, fold them into the v2 vocabulary in the same run with the
script's repeatable `--map OLDFOLDER=NEWFOLDER[:NEWTYPE]` flag, e.g.
`python _system/scripts/migrate_02_karpathy_vocab.py --apply --force
--map skills=concepts:concept`. The folder is renamed, moved pages get
`type: NEWTYPE`, and wikilinks are rewritten accordingly.
