# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/) for
the L1 schema version recorded in [`AGENTS.md`](AGENTS.md) frontmatter
(`schema_version`).

## [Unreleased]

### Added

- **`docs/reference/harness-memory-vs-llm-wiki.md`** — distinguishes
  Densa from the six other "knowledge-base-shaped" layers in the
  agent stack (AGENTS.md / Cline Memory Bank / Skills / session
  memory / RAG-MCP retrieval / Letta personal memory). Distilled from
  the 2026-05-27 ecosystem snapshot survey filed under
  `docs/maintainers/prior-art/`. Linked from `README.md` (new
  "Why not just `CLAUDE.md` / Memory Bank / Letta?" section) and
  `docs/reference/README.md`.
- **Optional `CLAUDE.md` / `GEMINI.md` shim guidance** in
  [`_system/templates/vault-readme.md`](_system/templates/vault-readme.md).
  Convenience aliases (one line each, pointing back at `AGENTS.md`)
  for users whose agent defaults to a non-AGENTS filename. Pattern
  borrowed from Tolaria; never copy the contract into the shim.
- **`Reasoning:` field** in the `ingest` log-entry template
  ([`_system/prompts/ingest.md`](_system/prompts/ingest.md);
  mirrored in [`AGENTS.md` §2.1](AGENTS.md#21-ingest-path) and the
  global [`log.md`](log.md) preamble). Encouraged, not required —
  the schema-friendly substitute for a runtime session trace (Densa
  stays at the schema layer; the explanation lives in the new
  reference doc above).

## [0.5.0] - 2026-05-26 — schema v2 (Karpathy vocab) + onboarding clarity sweep

### Template changes (affects forks)

> **Schema bump.** `schema_version: 1 → 2`. The L1 type vocabulary is
> realigned to Karpathy's gist
> ([`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md)):
> the 16 v1 page types collapse to nine v2 types
> (`source`, `summary`, `entity`, `concept`, `comparison`, `overview`,
> `synthesis`, `open-question`, `report`). The active default L2
> (`domains/research-papers/`) ships on v2 already; the two
> `examples/showcases/{workspace,psychology}/` references remain on
> v1 for now (banners on each AGENTS.md flag this). Fork upgrade
> runbook: `python -m densa migrate` (idempotent; preserves
> content; stamps `migration_history` on each page).

#### Added

- **`densa init <destination>` subcommand** — automates a fresh vault
  bootstrap: clones upstream, wires the pre-commit hook, walks
  example-domain disposition, and (optionally) injects
  `docs/bootstrap.md` into your AI agent (`--auto-inject
  cursor|claude-code|codex|auto`). Runnable today via
  `PYTHONPATH=_system python -m densa init my-vault` from any Densa
  clone (or `densa init my-vault` after `pip install -e .`). Documented
  in [`README.md` §"Alternative: scaffold without cloning by hand"](README.md#alternative-scaffold-without-cloning-by-hand).

#### Changed (BREAKING — schema vocabulary)

- **`_system/densa/schema.py`** is now the single source of truth
  for the L1 contract. AGENTS.md prose mirrors it; AGENTS011
  catches drift.
- **`_system/templates/`** reshaped to nine v2 templates
  (`summary.md`, `entity.md`, `concept.md`, `comparison.md`,
  `overview.md`, `synthesis.md`, `open-question.md`, `source.md`,
  `report.md`, plus the `qa.md` Q&A variant and the two
  advisory `writing-*` templates). The 15 v1 templates
  (`analysis.md`, `pattern.md`, `theme.md`, `framework.md`,
  `protocol.md`, `experiment.md`, `decision.md`, `stakeholder.md`,
  `project.md`, `fleeting.md`, `correction.md`, `question.md`,
  `session.md`, `psychology-analysis.md`, `psychiatry-analysis.md`)
  move to `attic/templates-v1/` with a README pointer.
- **`examples/hello-world/`** migrated to v2 buckets
  (`wiki/analyses/` → `wiki/summaries/`,
  `docstring-overview-analysis.md` → `docstring-overview-summary.md`).
- **AGENTS010** (`schema-version-consistency`) is now ERROR severity:
  pages with `compiled_against` lagging the current
  `SCHEMA_VERSION` block commits. AGENTS011
  (`prompt-schema-sync`) and AGENTS012
  (`migration-history-hygiene`) are WARN.
- **`_system/scripts/migrate_02_karpathy_vocab.py`** is the v1 → v2
  migration. Three modes: `in-place` (default; content-preserving),
  `archive` (parks v1 under `wiki/.legacy/`), `recover` (inverts a
  prior archive). Idempotent.

#### Migration from v1 (existing forks)

```bash
git fetch upstream && git merge upstream/main
python -m densa migrate            # apply all pending migrations (default mode: in-place)
PYTHONPATH=_system python -m densa --all   # confirm a clean baseline
```

`raw/` is never touched. The migration script stamps each rewritten
page with a `migration_history` frontmatter block (audited by
AGENTS012) so you can later see when a page moved from v1 to v2.

#### Changed (non-schema)

- **README** gains a *Pick your path* router (just-look / just-use /
  evaluate) before the 5-minute demo. The *Two names, one project*
  callout is demoted to a footnote at the end of Quickstart.
- **`index.md`** redirects new users to `README.md` instead of GUIDE
  (was confusing: index is a content map, not an onboarding entry).
- **`AGENTS.md §1.1`** opens with a callout clarifying that the
  four-file minimal set is the **LLM** onboarding contract, not for
  human readers (who enter at README).
- **`AGENTS.md` slimmed** (~437 lines, down from ~504):
  - Full vault tree moved to
    [`docs/reference/repository-layout.md`](docs/reference/repository-layout.md)
    (new).
  - Migration runbook (the `python -m densa migrate` modes + chain)
    moved into
    [`docs/reference/schema-versioning.md`](docs/reference/schema-versioning.md).
  - Workflow "natural language → action" table moved to
    [`GUIDE.md`](GUIDE.md) §"Mapping natural language to operations".
  - `§6.1` registry compressed; AGENTS010/011/012 details now in
    [`docs/reference/rules-registry.md`](docs/reference/rules-registry.md).
  - Canonical-fact callout removed from §3 (already documented in
    [`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md)).
- **`SETUP.md`** reorganised into three explicit segments:
  *Required (everyone) / Recommended (Obsidian users) / Privacy
  (sensitive material)*. Each opt-in segment has an applicability
  callout — a VSCode-only user can skip the Obsidian section
  cleanly. The rule table extended to AGENTS001-012.
- **`docs/reference/rules-registry.md`** extended to AGENTS010-012
  (was AGENTS001-009 only).
- **`docs/EXAMPLE-DOMAINS.md` content merged into
  [`docs/setup.md` §"Choosing or replacing the default domain"](docs/setup.md#choosing-or-replacing-the-default-domain)** —
  the decision tree lives alongside the install runbook so domain
  setup is one stop. Per-showcase descriptive content (the *what does
  it look like* tour) moved to the showcase README so each doc has a
  single role.
- **`docs/EXAMPLES.md` deleted** — its per-domain tour merged into
  [`examples/showcases/README.md`](examples/showcases/README.md);
  shipped showcases now self-document their structure in one place.
- **`domains/research-papers/wiki/overview.md`** now opens with a
  collapsed callout that empty Dataview sections (`entities/`,
  `comparisons/`, `overviews/`) mean *not yet triggered*, not
  *broken*. Avoids a fresh-fork first-impression that the wiki is
  half-empty.

#### Fork update procedure (no migration script needed)

```bash
# Resolve the two doc renames in your own references.
git grep -l 'docs/EXAMPLES\.md'        | xargs sed -i '' 's|docs/EXAMPLES\.md|examples/showcases/README.md|g'
git grep -l 'docs/EXAMPLE-DOMAINS\.md' | xargs sed -i '' 's|docs/EXAMPLE-DOMAINS\.md|docs/setup.md|g'
git fetch upstream && git merge upstream/main
PYTHONPATH=_system python -m densa --all
```

No `compiled_against` bump, no migration script needed.

### Planned

- **Publish `densa` to PyPI**. *Status as of 2026-05-25: not yet
  available; `pipx install densa` will fail. The supported install
  today is `git clone` + `git config core.hooksPath _system/hooks`
  (pure stdlib, no `pip install` needed), or `densa init` from an
  existing Densa install (see Added above).*
- `how-to-read-this-domain.md` synthesis page for `workspace` (matching
  the `research-papers` and `psychology` pattern).
- Structured "promotion candidates" output from `lint` (currently
  surfaced only as free-text in the report).

## [0.2.0] - 2026-05-24 — onboarding refactor (BREAKING repository layout)

Layout-only release. No schema changes; `compiled_against: 1` is
preserved. **This release breaks paths but not the contract.** Forks
of `0.1.0` need to either re-fork or run a small path-update sweep
(see "Migration" below).

> **Reading guide.** This release combines repository-layout work
> (affects every fork) with cosmetic fixes to the *shipped example
> L2* (the synthesised psychology / workspace content). Forks that
> have already replaced the shipped examples with their own content
> can skip the second subsection entirely.

### Template changes (affects forks)

#### Changed (breaking — file layout only)

- **`_system/MANUAL.md` → `GUIDE.md`** (root). The day-in-the-life
  guide was hiding under `_system/` (which reads as "private system
  files"); promoted to the root next to `README.md` / `AGENTS.md`.
- **`_system/SETUP.md` → `SETUP.md`** (root). Same rationale.
- **`docs/dogfood/` / `docs/prior-art/` / `docs/user-research/` /
  `docs/MASTER-PLAN-*.md` → `docs/maintainers/`**. Maintainer-only
  design archive consolidated into one path. The directory remains
  `.gitignore`d (it was already private); the move keeps disk layout
  consistent with intent.
- **`docs/reference/`** (new). The long tables that used to live
  inside `AGENTS.md` § 2.0 / § 3.1 / § 3.2 / § 3.3 / § 6.1 broken out
  into five companion docs (`operation-scopes.md`,
  `sources-cardinality.md`, `schema-versioning.md`,
  `rules-registry.md`, `red-lines.md`) plus an index.
- **`AGENTS.md` trimmed from 685 → ~370 lines.** Contract-only: the
  five red lines (one sentence each), the five operations (numbered
  steps), the universal frontmatter contract. All long tables and
  failure-mode rationale moved to `docs/reference/`. The minimal
  onboarding set (§ 1.1) is unchanged at four files.
- **`domains/workspace/` and `domains/psychology/` →
  `examples/showcases/`**. Default fork now ships **one** active
  example L2 (`research-papers/` — the light schema). The heavier
  showcases stay as reference material, opt-in by `cp -r
  examples/showcases/<X> domains/<X>`. The validator's wikilink
  resolver skips `examples/` so showcase internals don't pollute your
  active wiki graph.
- **`README.md`** rewritten from 393 → ~175 lines. Single
  Quickstart path (the `pipx install densa` preview block was
  dropped — it'll come back when PyPI publication actually ships).
  Adds an explicit *Densa (project) vs `densa` (CLI)* distinction in
  the lead, since they were silently colliding.

#### Added

- **`examples/hello-world/`** — a 5-minute walkthrough: one-page
  source + the wiki pages an ingest would produce + the log entry.
  Linked from the README's *5-minute demo* section. No agent
  required to consume.
- **`examples/` is a new validator-recognised top-level**
  (`WIKILINK_SKIP_TOP_LEVEL` includes it); `(no prefix)` commits may
  write `examples/**`.
- **Root-level docs are exempt from wikilink resolvability checks.**
  `GUIDE.md`, `SETUP.md`, `README.md`, `CHANGELOG.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` (in addition
  to `AGENTS.md` at any depth) contain `[[placeholder]]` examples
  and historical references by design.
- **`log.md` at any depth is exempt from wikilink resolvability
  checks.** The log is append-only audit history; past entries'
  wikilinks may legitimately point at deprecated / moved / renamed
  pages, and rewriting them would violate AGENTS002.
- **AGENTS.md §3.4** — `cross-domain` tagging contract.
- **`densa` rule `DENSA-IO`** registered in `config.RULES`
  with stable ID + summary + anchor.
- **`densa --diff <base_ref>`** subcommand so CI can apply the
  staged rules (AGENTS001 / AGENTS002 / AGENTS007) over a PR range.
  Before this, a local `git commit --no-verify` bypassed every
  staged rule and CI had no way to catch it. `.github/workflows/ci.yml`
  now runs both `--all` (file rules) and `--diff origin/<base>`
  (staged rules) on every PR.
- **11 new regression tests** covering each of the fixes below
  (index exclusion, explicit-path fallback, inbox→raw rename,
  raw-to-raw rename, source-aware fallback, analysis source must
  resolve to raw, raw source clean path, BOM frontmatter, CRLF
  frontmatter, diff-mode catches AGENTS001, diff-mode passes clean
  range).

#### Fixed (validator + first-week-adopter sharp edges)

- **AGENTS006 slot-index pollution**. `build_index()` indexed
  everything under `_system/templates/` (and `attic/` / `inbox/` /
  `outputs/`), so a typo like `[[concept]]` silently resolved to the
  template file rather than being flagged MISSING. Index now mirrors
  `wikilinks_scoped` exclusions; explicit-path wikilinks like
  `[[_system/templates/concept]]` still resolve via a separate
  full-repo index.
- **AGENTS001 inbox→raw rename false positive**. `StagedEntry` now
  carries the rename source path; the rule only forbids renames
  whose *source* sits under `raw/`. `git mv inbox/x.md
  domains/<X>/raw/<bucket>/y.md` (the canonical `process-inbox`
  action per L1 §2.4) is now permitted as designed.
- **AGENTS005 didn't require the source to be a raw file**. Per L1
  §3.1 `analysis.sources` MUST point at a raw file; the rule now
  resolves the wikilink and asserts the target lies under `raw/`.
- **`frontmatter.parse_stdlib`** silently lost BOM-prefixed and
  CRLF-terminated frontmatter, surfacing as false AGENTS003 errors
  on Windows-authored pages. Both are now normalised.

#### Docs / OSS polish

- Reconciled the "three vs five example L2 domains" drift across
  `README.md`, `docs/EXAMPLE-DOMAINS.md`, `docs/bootstrap-prompt.md`.
- `_system/MANUAL.md §0` cheat sheet now lists `process-inbox` (was
  missing) and no longer claims a "Capture a fleeting note"
  operation (which violated L1 §6's source-traceability rule).
- `_system/prompts/process-inbox.md` no longer calls itself the
  "fourth operation" (there are five).
- `setup_encryption.sh` defaults are commented out — `README.md`
  and `_system/SETUP.md` now say so explicitly instead of implying
  there is a default path list.
- `AGENTS.md` §3.4 formalises `cross-domain` as a first-class tag
  (the ingest/lint prompts already required it).
- `DENSA-IO` (meta diagnostic for unreadable files) is now in
  the rule registry, so `--ignore DENSA-IO` works.
- Dropped dead references to `pydantic` and
  `densa.checks.l2_extensions` from `__init__.py` / `config.py`.

#### Migration from 0.1.0

If you forked `0.1.0` and want to pull in the new layout, a single
sweep handles the path changes (no schema changes are needed):

```bash
# Resolve text-level references — relative paths inside wiki pages,
# index.md, and any L2-internal docs.
git grep -l '_system/MANUAL'  | xargs sed -i '' 's|_system/MANUAL|GUIDE|g'
git grep -l '_system/SETUP'   | xargs sed -i '' 's|_system/SETUP|SETUP|g'

# If you customised an L2, those L2s stay under domains/. The
# rename only affects the two shipped showcases; if you forked
# either of those into your own domain you don't need to do anything.

git fetch upstream && git merge upstream/main
PYTHONPATH=_system python -m densa --all  # confirm clean
```

The change is layout-only — no `compiled_against` bump, no
migration script needed.

### Shipped example data fixes (cosmetic, no fork action)

Cleanup applied to the bundled worked-example L2s. Forks that
replaced the shipped examples with their own content can ignore
this entire subsection — none of these changes alter the schema,
the validator, or any path your fork depends on.

- **`research-papers/AGENTS.md` opener** now correctly says six
  page types (was "three"); **`workspace/AGENTS.md` opener**
  documents the source/session synonym so the 8 vs 9 row count is
  unambiguous.
- **Three `index.md` files** were displaying recent activity
  backwards (`entries.slice(-15).reverse()` on a
  reverse-chronological log shows the *oldest* 15). All four
  `index.md` files now use `entries.slice(0, 15)`.
- **~170 broken Obsidian block-id anchors** under
  `domains/psychology/wiki/` rewritten from `[[file#^[HH:MM]]]`
  (which never resolved, because the raws use `**[HH:MM]**` not
  `^id`) to `[[file]] [HH:MM]`, matching the L2's own convention
  in `domains/psychology/AGENTS.md`.
- **Workspace `engineering-decision-style`** instance count
  reconciled between the pattern page (N=2-provisional), the
  2026-05-19 analysis prose, and the log entry.
- **`decision-delay-from-skipped-stakeholder.instances_count`**
  updated from `1` to `3` so the pattern no longer violates its
  own L2 `instances_count ≥ len(sources)` lint rule; the arc-level
  "N=1 provisional" claim is preserved in the prose.
- **`workspace/AGENTS.md` folder layout** marks `raw/threads/` as
  on-demand (the directory doesn't ship on disk); stakeholder /
  team / project `team:` / `lead:` fields explicitly accept a plain
  string when no entity page is yet warranted (matching what the
  shipped example pages actually do).

## [0.1.0] - 2026-05-21

### Added

- **L1 schema** ([`AGENTS.md`](AGENTS.md)) — universal contract for
  every domain: page-type enum, `sources` cardinality, red lines,
  routing rules, schema versioning, `last_validated` semantics.
- **Five canonical operations** under [`_system/prompts/`](_system/prompts/) —
  `ingest`, `query`, `lint`, `process-inbox`, `promote`.
- **Page templates** for every page type under
  [`_system/templates/`](_system/templates/), including
  domain-specialised variants and a Q&A template.
- **`densa` Python validator** ([`_system/densa/`](_system/densa/)) —
  pure-stdlib (~1k lines) schema + red-line enforcement; pre-commit
  hook under [`_system/hooks/`](_system/hooks/) and GitHub Action
  under [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
- **Three worked-example domains** under [`domains/`](domains/) covering
  light/medium/heavy schema density (`research-papers`, `workspace`,
  `psychology`).
- **Claude Code plugin** at [`integrations/claude-code/`](integrations/claude-code/) —
  thin slash-command shims wrapping all five operations.
