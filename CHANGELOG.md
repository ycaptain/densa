# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/) for
the L1 schema version recorded in [`AGENTS.md`](AGENTS.md) frontmatter
(`schema_version`).

## [Unreleased]

## [0.6.0] - 2026-06-16 — interactive diagnostics TUI + Obsidian graph readability sweep

### Added

- **`densa tui` — interactive diagnostics viewer.** A read-only,
  stdlib-only (`curses`) terminal UI over `densa --all`: scroll and
  filter findings by severity or rule, mute the expected
  gitignored-tree noise band, and read the offending file excerpt with
  jump-to-line. Built on a pure, framework-agnostic view-model
  (`densa.tui.model`) and renderer (`densa.tui.view`) — the curses
  driver is the only impure shell and is lazy-imported behind the `tui`
  subcommand, so the lint / pre-commit path never pays the `curses`
  import (mirrors the MCP server). POSIX-only; a missing `curses`
  exits with a clear message. `--diff REF` scopes the view to
  `REF..HEAD`.
- **AGENTS013 `obsidian-link-format`.** Densa's suffix-matching
  resolver accepts bucket-relative wikilinks (`[[concepts/x]]`) that
  Obsidian cannot resolve — they lint clean but render as grey ghost
  nodes in the graph view and 404 on click. The new rule (warning;
  intended to become an error once active vaults are clean) flags any
  `/`-containing link that is not a vault-root path.
  `AGENTS.md` §"Naming and linking conventions" now forbids the form
  explicitly. (`densa.wikilink.obsidian_resolvable` is the shared
  predicate.)
- **`_system/scripts/fix_obsidian_links.py`** clears the AGENTS013
  backlog mechanically: bare `[[slug]]` when the basename is unique
  across everything Obsidian indexes (including nested checkouts the
  densa walk prunes), full vault path + display alias otherwise;
  `--fuzzy` retargets stale bucket prefixes via unique basename.
  `raw/` and `log.md` are never touched; dry-run default; idempotent.
- **`densa graph-config`** generates `.obsidian/graph.json` tuned for
  a Densa vault: filter excludes scaffolding / `raw/` / `log.md` /
  schema docs (repeatable `--exclude` for vendored checkouts),
  per-domain color groups plus index/syntheses landmarks, forces
  tuned for a few-hundred-node graph. Write-once unless `--force`.
  docs/setup.md gains a "Graph view" section with the
  local-graph-first navigation workflow.
- **`densa stats` graph-health metrics**: `obsidian_unresolvable_links`
  (the AGENTS013 backlog), the top ghost targets, and the top
  inbound/outbound hub pages — graph-readability regressions surface
  as numbers in the lint baseline.

### Changed

- **Appearances rows require a one-line annotation.** A bare
  date + link row stores nothing a backlink doesn't, but each row is
  an explicit graph edge — the biggest source of hub explosion in
  grown vaults. Pure chronological timelines on concept/entity pages
  now go through a rendered Dataview block (`LIST FROM [[]]`), which
  shows the same list with zero graph edges. Annotated rows keep
  explicit wikilinks; the canonical-fact rule is unchanged. Encoded in
  the AGENTS.md ingest contract, both templates, and the ingest
  prompt.

- **AGENTS006 bare-slug wikilinks prefer a same-domain match before
  reporting ambiguity.** When a bare `[[slug]]` has multiple global
  candidates, the resolver now filters them to the linking file's own
  `domains/<X>/` first: exactly one survivor resolves silently,
  multiple survivors stay ambiguous, zero survivors fall back to the
  global candidate set (cross-domain links keep working). Files
  outside any domain (root `log.md`, `index.md`) keep the historical
  behaviour. On a migrated real vault this silenced 561 of 575
  ambiguity warnings where two domains legitimately keep an entity of
  the same slug — the L2-wins philosophy at the link-resolution layer.
  (TK-0037)

### Fixed

- **AGENTS007 no longer classifies commits one-behind under
  `git commit -m`.** The rule read `.git/COMMIT_EDITMSG` assuming it
  held the in-flight message, but git rewrites that file only _after_
  the pre-commit hook passes — so every commit was classified by the
  PREVIOUS commit's prefix, and a correctly prefixed operation commit
  following a maintenance commit always failed on first attempt. The
  prefix-scope rule now runs in a new `_system/hooks/commit-msg` hook,
  which receives the real message file as `$1` and hands it to the
  validator via `DENSA_COMMIT_MSG_FILE`; the pre-commit hook runs
  every other rule and skips AGENTS007 (`--ignore AGENTS007`).
  `_commit_subject()` prefers the env-provided file and never reads
  `COMMIT_EDITMSG` anymore (falling back to the `HEAD` subject for
  post-commit re-runs and CI `--diff`). The existing
  `core.hooksPath _system/hooks` wiring covers both hooks — no setup
  change needed. (TK-0038)

- **Vault walkers no longer descend into nested git checkouts.** A
  repo checked out inside the vault (e.g. an upstream densa working
  copy, gitignored by the vault) polluted the slug index — foreign
  showcase pages made every bare `[[slug]]` ambiguous — and raised
  AGENTS006 on foreign template placeholders. The new shared
  `densa.fswalk.iter_markdown` prunes any subdirectory carrying its
  own `.git` (directory or worktree-style file); the slug index,
  `densa --all` collection, `densa stats`, and `migrate_02`'s
  wikilink rewrite all walk through it. The same descent let a
  migration run rewrite files inside the nested upstream repo.
  (TK-0035)

- **`migrate_02` now seeds missing v2 universal frontmatter keys.**
  v1 pages predate `aliases` (and occasionally `sources`); the
  frontmatter rewrite pass now appends the missing presence-only keys
  as empty lists so a freshly migrated vault validates clean under
  AGENTS003. Found migrating a real ~600-file v1 vault, which surfaced
  254 post-migration `missing universal frontmatter key: aliases`
  errors. (TK-0030)
- **`migrate_02` rewrites folder path segments in wikilinks.** The
  rewriter previously only renamed bare-slug links; full-path links
  (`[[domains/<d>/wiki/analyses/...]]`) and wiki-relative
  folder-prefixed links (`[[questions/...]]`, `[[decisions/...]]`)
  kept their v1 folder segment, leaving ~1,600 AGENTS006 errors on the
  same real-vault migration. Folder renames (schema table + `--map`)
  now compose with slug renames in one pass; `raw/` is skipped per
  AGENTS001. (TK-0031)
- **Adopted v1 vaults migrate without manual `--force`.** Copying
  upstream `_system/` into a pre-existing v1 vault also copies densa's
  own `_system/migrations.log`, whose entries made the migration
  script refuse to run. `densa migrate` now passes `--force` to the
  scripts whenever its own `compiled_against` scan determined the
  migration is still pending — the scan is ground truth, the scripts
  are idempotent. Direct script invocation keeps the log guard.
  `docs/reference/schema-versioning.md` gains an "Adopting densa into
  a pre-existing vault" note. (TK-0032)

### Added

- **`migrate_02 --map OLDFOLDER=NEWFOLDER[:NEWTYPE]`** (repeatable) —
  fold custom v1 folders/types into the v2 vocabulary in the same
  migration run (folder rename + optional type rewrite + wikilink
  rewrite). Unknown target types fail fast against `ALLOWED_TYPES`.
  Dry-run plans annotate type rewrites; the `migrations.log` marker
  records the mapping. (TK-0033)
- **`WIKI_ALLOW_MIGRATION=1` — sanctioned AGENTS002 escape for
  migration commits.** `migrate_02` rewrites wikilinks inside past
  `log.md` entries by design, but AGENTS002 rejected every staged
  log deletion, making the migration's own output uncommittable.
  The new bypass skips AGENTS002 for one commit and is inert unless
  the same commit also stages an addition to
  `_system/migrations.log` (it only works inside a recorded
  migration). `WIKI_ALLOW_LOG_REORDER` semantics unchanged. Found
  preparing the actual v1→v2 migration commit on a real vault.
  (TK-0034)

### Changed

- **`docs/reference/` split: design essays moved to `docs/design/`.**
  The two "why" essays (`design-rationale.md` +
  `harness-memory-vs-llm-wiki.md`) moved out of `docs/reference/` into a
  new published `docs/design/`, leaving `docs/reference/` as pure
  contract lookup tables ("what" vs "why"). Inbound links across README
  / ROADMAP / GUIDE / setup / bootstrap / the ingest prompt / issue
  template updated; `AGENTS.md` unaffected (it only links the contract
  specs).
- **`lint` now emits structured `## Promotion candidates`**
  ([`_system/prompts/lint.md`](_system/prompts/lint.md) §6.6 + the
  report skeleton). Each Q&A meeting ≥2 of the existing heuristics
  (`inbound_refs` / `citation_breadth` / `age`) is now written as a
  fenced YAML record with `qa / suggested_type / suggested_slug /
criteria_met / reason`, replacing the prior free-text rows.
  Zero-candidate runs MUST emit `_No candidates this run._` so
  `promote` and other downstream tooling can distinguish "section
  absent" (LLM forgot) from "section present, nothing qualified"
  (clean run). No code change in `_system/densa/`; the schema
  contract (`densa.schema.OPERATIONS['lint'].writes`) is unchanged.
  ROADMAP medium-term entry struck in lockstep.
- **`examples/showcases/{psychology,workspace}/AGENTS.md` banners
  rewritten to match the actual on-disk shape.** The two showcases
  were mechanically migrated to v2 frontmatter / folder layout on
  2026-05-26 via
  `python -m densa migrate --mode in-place --extra-roots examples/showcases`
  (recorded in [`_system/migrations.log`](_system/migrations.log)),
  but the AGENTS.md prose still described them as "v1 schema
  example, run the migration to upgrade". Both banners now read
  "v1 design — v2 schema" and point readers at
  [`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md)
  - the active default L2. ROADMAP "Short term: examples/showcases
    v1→v2 migration" struck in lockstep.

### Added

- **`densa doctor`** — a preflight that diagnoses a local setup before
  it fails confusingly: checks the pre-commit hook is wired, the Python
  meets `requires-python`, `densa` is importable, every active L2
  `domains/<X>/AGENTS.md` parses, and the linter can walk the vault.
  Prints a ✓/✗ checklist with the exact fix command per failure; exits
  non-zero if any check fails (CI/script usable). `--format json` for
  tooling. Stdlib-only (`_system/densa/commands/doctor.py`), so the
  core stays `cp -R`-able. Wired into the README Quickstart ("stuck?")
  and CONTRIBUTING §"Your first 30 minutes".
- **`densa stats`** — a read-only vault-health report: total wiki pages,
  per-domain and per-`type:` breakdown, average page age per type,
  orphan-page count (no inbound wikilinks), cross-domain count, and
  per-domain log staleness. `--format json` feeds shields.io badges and
  CI. Stdlib-only (`_system/densa/commands/stats.py`); counts only
  `domains/<X>/wiki/` pages (so `raw/`, `outputs/`, `.legacy/` never
  inflate the numbers).
- **`examples/showcases/workspace/wiki/syntheses/how-to-read-this-domain.md`**
  — four time-budgeted reading paths (5 min / 30 min / 2 h /
  half-day) over the workspace showcase, mirroring the
  `domains/research-papers/wiki/syntheses/how-to-read-this-domain.md`
  and `examples/showcases/psychology/wiki/syntheses/how-to-read-psychology-domain.md`
  navigators. Includes a Mermaid map of the five raws → five
  summaries → two patterns → two syntheses graph, the three-decision
  headline table, and a "How to extend this wiki with your own
  meetings" hand-off to the workspace sub-prompt. Linked from
  `examples/showcases/workspace/wiki/overview.md` (new-teammate
  callout + mindmap node) and the L2
  `examples/showcases/workspace/AGENTS.md`'s "Onboarding reading
  order" section, which now defers to the navigator as the
  canonical entry.
- **`docs/design/harness-memory-vs-llm-wiki.md`** — distinguishes
  Densa from the six other "knowledge-base-shaped" layers in the
  agent stack (AGENTS.md / Cline Memory Bank / Skills / session
  memory / RAG-MCP retrieval / Letta personal memory). Distilled
  from the maintainers' 2026-05-27 ecosystem snapshot survey.
  Linked from `README.md` (new
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

- **`<untrusted>` fenced ingest** — raw-source content is wrapped in
  an `<untrusted>` data fence during `ingest`, with nested-tag and
  premature-close escape handling (the D+B protocol,
  [`AGENTS.md` §4.5](AGENTS.md)). Regression fixtures under
  `_system/tests/fixtures/`.
- **Trust-tier protocol** (`AGENTS.md` §4.5) — formalizes the trust
  vocabulary (contract / wiki / raw / external) the operations and
  the MCP surface share.
- **Two-pass ingest** — `_system/prompts/ingest.md` split into
  Pass 1 (analysis) and Pass 2 (generation), converging with the
  quality pattern independently adopted by two upstreams in the
  prior-art set.
- **MCP tool-surface spec** — [`_system/densa/mcp/SPEC.md`](_system/densa/mcp/SPEC.md)
  freezes the 8-tool read/navigate/lint surface (plus the @-mention
  picker design in [`integrations/README.md`](integrations/README.md))
  ahead of the stdlib JSON-RPC server implementation.
- **Op-prompt progressive disclosure** — each `_system/prompts/<op>.md`
  is split into a small header + an on-demand body, cutting the
  per-operation context cost.

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

- **README** gains a _Pick your path_ router (just-look / just-use /
  evaluate) before the 5-minute demo. The _Two names, one project_
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
  _Required (everyone) / Recommended (Obsidian users) / Privacy
  (sensitive material)_. Each opt-in segment has an applicability
  callout — a VSCode-only user can skip the Obsidian section
  cleanly. The rule table extended to AGENTS001-012.
- **`docs/reference/rules-registry.md`** extended to AGENTS010-012
  (was AGENTS001-009 only).
- **`docs/EXAMPLE-DOMAINS.md` content merged into
  [`docs/setup.md` §"Choosing or replacing the default domain"](docs/setup.md#choosing-or-replacing-the-default-domain)** —
  the decision tree lives alongside the install runbook so domain
  setup is one stop. Per-showcase descriptive content (the _what does
  it look like_ tour) moved to the showcase README so each doc has a
  single role.
- **`docs/EXAMPLES.md` deleted** — its per-domain tour merged into
  [`examples/showcases/README.md`](examples/showcases/README.md);
  shipped showcases now self-document their structure in one place.
- **`domains/research-papers/wiki/overview.md`** now opens with a
  collapsed callout that empty Dataview sections (`entities/`,
  `comparisons/`, `overviews/`) mean _not yet triggered_, not
  _broken_. Avoids a fresh-fork first-impression that the wiki is
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

- **Publish `densa` to PyPI**. _Status as of 2026-05-25: not yet
  available; `pipx install densa` will fail. The supported install
  today is `git clone` + `git config core.hooksPath _system/hooks`
  (pure stdlib, no `pip install` needed), or `densa init` from an
  existing Densa install (see Added above)._

## [0.2.0] - 2026-05-24 — onboarding refactor (BREAKING repository layout)

Layout-only release. No schema changes; `compiled_against: 1` is
preserved. **This release breaks paths but not the contract.** Forks
of `0.1.0` need to either re-fork or run a small path-update sweep
(see "Migration" below).

> **Reading guide.** This release combines repository-layout work
> (affects every fork) with cosmetic fixes to the _shipped example
> L2_ (the synthesised psychology / workspace content). Forks that
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
  Adds an explicit _Densa (project) vs `densa` (CLI)_ distinction in
  the lead, since they were silently colliding.

#### Added

- **`examples/hello-world/`** — a 5-minute walkthrough: one-page
  source + the wiki pages an ingest would produce + the log entry.
  Linked from the README's _5-minute demo_ section. No agent
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
  whose _source_ sits under `raw/`. `git mv inbox/x.md
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
  reverse-chronological log shows the _oldest_ 15). All four
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
