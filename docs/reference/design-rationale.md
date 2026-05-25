# Design rationale — why the LLM wiki looks this way

> Companion to [`README.md`](../../README.md). The README shows you how
> to use the template; this file explains *why* each load-bearing
> decision exists and how to extend the schema to your own domains.
> Long page (~680 lines); meant for *evaluating the design*, not for
> first-time onboarding. Skim the ToC and jump to the section you need.
> Sections that duplicated companion reference files (`red-lines.md`,
> `operation-scopes.md`, `sources-cardinality.md`,
> [AGENTS.md §"Routing rules"](../../AGENTS.md#5-routing-rules-where-does-a-new-source-go))
> now stub-to-pointer to avoid drift; load those for the long tables.

> [!faq]- Table of contents (click to expand)
> - [Why this exists](#why-this-exists)
> - [How it compares](#how-it-compares)
> - [Who this is not for](#who-this-is-not-for)
> - [The core invariant](#the-core-invariant)
> - [Why L1 / L2 schema layering](#why-l1--l2-schema-layering)
> - [The frontmatter contract](#the-frontmatter-contract) — pointer to [`sources-cardinality.md`](sources-cardinality.md)
> - [`outputs/`: where operations write](#outputs-where-operations-write)
> - [Q&A as operation artifact, not compiled knowledge](#qa-as-operation-artifact)
> - [The promote operation: how Q&A becomes wiki knowledge](#the-promote-operation)
> - [Red lines (and why each one is non-negotiable)](#red-lines) — pointer to [`red-lines.md`](red-lines.md)
> - [Operation writes red line (AGENTS007)](#operation-writes-red-line-agents007) — pointer to [`operation-scopes.md`](operation-scopes.md)
> - [Routing: where does a new source go?](#routing-where-does-a-new-source-go) — pointer to [AGENTS.md §"Routing rules"](../../AGENTS.md#5-routing-rules-where-does-a-new-source-go)
> - [Engineering hooks: turning soft norms into hard rules](#engineering-hooks)
> - [How to design your own L2](#how-to-design-your-own-l2)
> - [Optional layers: `projects/` and `writing/`](#optional-layers-projects-and-writing)
> - [Anti-patterns to avoid](#anti-patterns-to-avoid)

---

## Why this exists

A vector-DB-backed RAG layer is great for "look up something I half
remember in a haystack". It's the wrong tool for the question I
actually want my second brain to answer:

> *Given everything you've read for me over the past two years,
> what's the most accurate model of X right now?*

That question needs a model that **compounds** — every new source
should make the structure denser, not just the haystack bigger. So
the LLM doesn't search your notes at query time; it incrementally
*compiles* them, page by page, into a queryable wiki you can read
like a textbook.

> The wiki is the codebase. Obsidian is the IDE. The LLM is the programmer.

---

## How it compares

| Tool                                       | Storage              | Compounds?         | Open / portable?  | Cites sources by default? | Local-first? |
| ------------------------------------------ | -------------------- | ------------------ | ----------------- | ------------------------- | ------------ |
| **Densa** (this repo)                    | plain markdown + git | yes                | yes               | enforced by validator     | yes          |
| Vector RAG (LlamaIndex, LangChain, etc.)   | vector DB            | no                 | partially         | optional                  | varies       |
| Notion AI                                  | proprietary DB       | partially          | no                | sometimes                 | no           |
| mem.ai                                     | proprietary DB       | partially          | no                | sometimes                 | no           |
| Reflect / Tana / Logseq AI                 | proprietary / md     | partially          | partially         | no                        | varies       |
| Obsidian + Smart Connections               | markdown + index     | no (retrieve-only) | yes               | no                        | yes          |
| Cursor `@docs` / Claude Projects           | session-local        | no                 | no                | sometimes                 | no           |

The pattern composes: at ~500+ pages, layer embedding search (Smart
Connections, Obsidian Bases, even a small vector index) on top of the
wiki as a fallback. The wiki gives you compounded structure; embedding
search gives you fuzzy fallback. Both, not either.

---

## Who this is not for

**This template is not designed for narrative long-form writers,
journalists, or memoirists.** If you write essays, articles, or books
that need to preserve voice, branch drafts, and stay in dialogue with
editors — this tool's compiler-style "raw → wiki" structure will work
against you. Try Scrivener, Ulysses, or Obsidian + Longform instead.
**Creative writing workflows are intentional out-of-scope; we will
not be adding support for them.**

And a few more things this is *not*:

- **Not a RAG replacement** at millions-of-chunks scale. Sweet spot
  is hundreds of curated sources with high synthesis frequency.
- **Not a SaaS or hosted product.** Markdown + git, run locally with
  the LLM agent of your choice.
- **Not an autopilot.** Every ingest plans first and waits for your
  confirmation; every lint report is a dashboard, not an auto-apply.
- **Not coupled to one model vendor.** The schema and prompts are
  agent-agnostic; switch Cursor ↔ Claude Code ↔ Codex freely.
- **Not novel research.** It's a careful systematisation of Andrej
  Karpathy's [llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  gist into a working template — credit where it's due.

---

## The core invariant

Everything else in this design follows from one structural commitment:

> **`raw/` is fact (immutable, append-only).
> `wiki/` is the current best model (LLM-owned, rewritten freely).
> `AGENTS.md` is the contract between the two.**

This three-layer split is borrowed from how compiled programming
languages separate source code, compiled artifacts, and the language
specification:

| Layer       | Analogue in a compiled language |
| ----------- | ------------------------------- |
| `raw/`      | source files (you write them once and check them in) |
| `wiki/`     | compiled binary (regenerated from source) |
| `AGENTS.md` | language spec (defines what's well-formed) |

Two consequences fall out:

1. **Three-year-back integrity.** If a wiki claim turns out to be
   wrong, you can walk the wikilinks back to the raw file and see
   exactly what was said, by whom, when. The LLM can't quietly rewrite
   history because history lives in `raw/` and `raw/` is immutable.
2. **Compounding instead of replay.** Each ingest densifies the wiki.
   The next query reads a denser model, not the same raw chunks. The
   second brain compounds with use, the way a textbook does — not the
   way a search index does.

---

## Why L1 / L2 schema layering

The schema is split deliberately:

- **L1** (`/AGENTS.md`) — universal contract every domain inherits:
  - Required frontmatter (`type`, `domain`, `created`, `updated`,
    `status`).
  - The closed set of nine page types (`source`, `summary`, `entity`,
    `concept`, `comparison`, `overview`, `synthesis`,
    `open-question`, `report`) — all named verbatim from
    [Karpathy's `llm-wiki` gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f);
    full glossary at
    [`karpathy-mapping.md`](karpathy-mapping.md).
  - Sources cardinality per type (e.g. `summary.sources` must be
    exactly 1; `synthesis.sources` must be ≥ 2). Detail:
    [`sources-cardinality.md`](sources-cardinality.md).
  - The red lines (raw immutable, log append-only, no wiki deletion,
    bulk renames require human consent).
  - The five operations and their procedures.

- **L2** (`domains/<X>/AGENTS.md`) — domain-specific override:
  - Persona (what voice should the LLM adopt for this domain).
  - Folder layout under `raw/` and `wiki/`.
  - Which page types this domain uses (subset of L1's nine).
  - Additional required frontmatter per type (e.g. a psychology L2
    might require `session_kind` on session sources; a research-
    papers L2 requires `evidence_quality` on summary pages). L2s
    sub-categorise within a v2 type via L2-specific fields rather
    than inventing new top-level `type:` values — `type` is closed
    at L1.
  - Domain-specific routing hints, lint rules, privacy posture.

Why this split?

1. **L2s evolve independently.** Adding a new L2 (say, a research
   tracking domain) doesn't require touching L1 or any other L2.
2. **L1 stays stable.** The universal invariants don't drift as you
   experiment with new domains; the red lines are the same everywhere.
3. **A fresh LLM session can onboard fast.** Read four files (L1, the
   L2 in scope, the prompt for the current operation, the cache index
   snapshot) and you're operating correctly. See
   [L1 §"Minimal onboarding set"](../../AGENTS.md#11-minimal-onboarding-set-for-a-fresh-llm-session)
   for the minimal onboarding set.

---

## The frontmatter contract

The universal frontmatter shape and the per-type `sources` cardinality
table live at [`sources-cardinality.md`](sources-cardinality.md) (the
canonical reference) and
[`_system/densa/schema.py::PAGE_TYPES`](../../_system/densa/schema.py)
(the machine-enforced source of truth). The two load-bearing
distinctions worth remembering when reading the rest of this file:

- **`summary.sources` length must be exactly 1.** Mixing sources at
  the summary layer turns the page into a synthesis; change `type` and
  move under `wiki/syntheses/`. AGENTS005 enforces this.
- **Wiki-to-wiki citations are first-class** for second-order pages
  (`concept` / `overview` / `synthesis` / `comparison` /
  `open-question`). The chain `concept → summary → raw` still
  terminates at raw, just one hop further out; lint flags chains
  longer than 2 hops because by then the abstraction has likely
  drifted from evidence.

---

## `outputs/`: where operations write

A fourth top-level directory completes the compiler analogy:

| Layer       | Analogue in a compiled language          | Purpose                          |
| ----------- | ---------------------------------------- | -------------------------------- |
| `raw/`      | source files                             | evidence, immutable              |
| `wiki/`     | compiled binary                          | hypotheses, LLM-owned            |
| `AGENTS.md` | language spec                            | the contract                     |
| `outputs/`  | build artifacts (`target/`, `dist/`)     | runtime products, in git but ignored by the wikilink graph |

`outputs/` is in git so the audit trail of every `lint` run is intact
across machines and clones, but the wikilink resolver deliberately
ignores it. Two consequences:

- **Wiki pages MUST NOT cite `outputs/`.** Reports point at wiki
  pages; the reverse direction is forbidden by design. This keeps the
  link graph clean — lint hubs / orphans / rings are wiki properties,
  not runtime noise.
- **Stale reports are safe to delete.** When `outputs/lint/` grows
  large enough to be noisy, `git rm outputs/lint/<old>.md` removes
  them with zero downstream impact. There is no auto-rotation; user
  manages retention.

Current `outputs/` buckets:

- `outputs/lint/<YYYY-MM-DD>.md` — one lint report per run, `type: report`.
- `outputs/snapshots/index-snapshot.md` — machine-readable mirror of
  every `index.md` Dataview block. Regenerated by every `lint` run and
  consumed by fresh LLM sessions as part of the four-file onboarding set
  ([AGENTS.md §"Minimal onboarding set"](../../AGENTS.md#11-minimal-onboarding-set-for-a-fresh-llm-session)).
- `outputs/qa/<YYYY-MM-DD>-<slug>.md` — Q&A archives filed back from
  substantive `query` runs, `type: report`. See the next section for
  why these live here and not in `wiki/syntheses/`.

Validator enforcement:

- `paths.is_outputs(path)` classifies any path under `outputs/`.
- `paths.is_output_artifact(path)` is the subset subject to the
  universal frontmatter contract (`outputs/<bucket>/<file>.md`,
  excluding the bare `outputs/README.md`).
- AGENTS003 / AGENTS004 visit those artifacts. AGENTS005 (summary
  source cardinality) skips them (reports cannot be summaries).
- AGENTS006 (wikilink resolvable) skips `outputs/` entirely.

---

## Q&A as operation artifact

<a id="qa-as-operation-artifact"></a>

The `query` operation files non-trivial answers as `type: report` Q&A
files under `outputs/qa/` rather than `wiki/syntheses/`. The trade-off
is deliberate and worth explaining.

**The problem with the older layout.** Until v0.5.0 `query` filed back
to `wiki/syntheses/<date>-<slug>.md`. Three symptoms accumulated:

1. **Schema impedance.** A Q&A is a snapshot of one conversation;
   `synthesis` requires `sources: ≥ 2` and is meant to braid multiple
   sources into a stable claim. Most Q&A files squeezed into the
   contract awkwardly — either inflating `sources` to satisfy the
   validator or silently violating it.
2. **Graph pollution.** Every Q&A page became a node in the wikilink
   graph; lint's orphan / hub / ring detectors started reporting
   transient query products as if they were structural anomalies.
3. **Retention pressure.**
   [L1 §"Naming and linking conventions"](../../AGENTS.md#4-naming-and-linking-conventions)
   forbids deleting wiki pages, so old
   "what did the wiki say about X back in March?" archives never
   cleaned up.

**The fix.** Move Q&A out of `wiki/` entirely. `outputs/qa/<date>-<slug>.md`
gets the same artifact semantics as `outputs/lint/`: in git for the
audit trail, excluded from the wikilink graph, `sources` may be empty,
safe to `git rm` when stale. `wiki/syntheses/` returns to its narrow
purpose — explicit cross-source narratives deliberately produced
during `ingest` or promoted from a Q&A.

**The cost.** Future wiki pages cannot back-reference an old Q&A
directly (the resolver ignores `outputs/`). If a particular Q&A proves
durable — evergreen, frequently revisited, makes a stable claim that
deserves wikilink-graph membership — the path forward is `promote`
(next section), which lifts it into the wiki with a controlled
information-shape transform. The vast majority of Q&A are written
once, consumed once, and aged out; only the handful with lasting
value pay the promote cost.

The pattern echoes Yanhua's
["Karpathy knowledge base methodology" essay](https://www.yanhua.dev/blog/karpathy-knowledge-base),
which placed `outputs/qa/` next to `outputs/health/` (our lint
reports) — both runtime products of operations over the wiki, neither
part of the wiki itself. The compiler analogy in
[§"`outputs/`: where operations write"](#outputs-where-operations-write)
applies cleanly: Q&A is to a run-time log what `wiki/syntheses/`
is to a compiled binary.

---

## The promote operation

<a id="the-promote-operation"></a>

`promote <qa-path>` is the fifth and newest canonical operation. It
upgrades a `query`-produced Q&A artifact into a first-class wiki page,
performing a *controlled information-shape transform* rather than a
bare file move.

```mermaid
flowchart TB
    QA["outputs/qa/&lt;date&gt;-&lt;slug&gt;.md<br/>type: report"]
    PRE{{"Pre-flight checks<br/>(reject early)"}}
    A1["1. Voice transform<br/>Q→declarative"]
    A2["2. Citation hoist<br/>inline [[…]] → frontmatter sources:"]
    A3["3. L2 fill-in<br/>type-specific required fields"]
    A4["4. Section restructure<br/>apply target template"]
    DST["domains/&lt;X&gt;/wiki/&lt;folder&gt;/&lt;new-slug&gt;.md<br/>type: summary | concept | comparison | overview | synthesis | open-question | entity"]
    LINT["outputs/lint/&lt;date&gt;.md<br/>Human-review queue"]
    QA --> PRE
    PRE -->|"all pass"| A1
    PRE -.->|"any fail"| ABORT["abort with specific remediation"]
    A1 --> A2 --> A3 --> A4 --> DST
    QA -. "Issues to surface" section .-> LINT
    QA -. "git mv preserves history" .-> DST
```

Five design choices worth flagging:

### 1. Pre-flight rejects, never partially applies

The LLM runs every pre-flight check before touching the worktree. If
any fails (source not in `outputs/qa/`, target type not in L2's
allowed set, slug+aliases collision with existing wiki page, `sources`
cardinality below the
[`sources-cardinality.md`](sources-cardinality.md) contract,
missing L2 type-specific fields), it surfaces
the specific blocker with a remediation suggestion and aborts. A
half-promoted page is worse than no promote at all: it pollutes the
wiki link graph with malformed metadata that lint subsequently has to
flag as `human-review`.

### 2. `git mv`, not new-write + delete

The implementation is a single `git mv outputs/qa/<file>.md
domains/<X>/wiki/<folder>/<new-slug>.md` followed by a rewrite of
the moved file. The alternative — write a new file and `git rm` the
source — would lose the file's history. `git log --follow` against the
promoted page traces all the way back to the original Q&A creation,
which is invaluable when reconstructing why a wiki claim looks the
way it does months later.

### 3. Information-shape transform, not text copy

A Q&A's "Question / Sub-claims / Answer" structure doesn't match how
wiki pages are read. Voice transforms the prose into declarative
knowledge; citation hoist promotes inline `[[wikilinks]]` to
frontmatter `sources:` for graph-level traceability; L2 fill-in adds
type-specific required fields (`concept.first_appeared`,
`overview.programme_status`, etc.); section restructure reorders the
body to match the target type's template. Promote produces a page
that a fresh-session LLM cannot tell apart from one written during
ingest.

### 4. 1:1 granularity by design

One Q&A becomes one wiki page per `promote` invocation. The
alternatives — 1:N split (one Q&A → multiple wiki pages) or N:1 merge
(multiple Q&A → one wiki page) — both invite the LLM to silently
restructure content the human hasn't reviewed. 1:N is achieved by
repeated `promote` calls with distinct `--slug`s; N:1 starts with
one `promote` and treats subsequent Q&A as `ingest`s touching the
new page.

### 5. lint suggests, never executes

`lint` surfaces "Promotion candidates" — Q&A files meeting heuristic
thresholds (referenced ≥ 3 times by other Q&A, sources cover ≥ 3 raw
files, > 30 days old without modification) — but it never invokes
`promote` itself. The decision to commit Q&A content into the
wiki-link graph is a human judgment call.

The full canonical procedure lives in
[`_system/prompts/promote.md`](../../_system/prompts/promote.md); the
contract is pinned by
[`_system/tests/test_promote_preflight.py`](../../_system/tests/test_promote_preflight.py).

---

## Red lines

The eight non-negotiable rules — `raw/` immutable, `log.md`
append-only, no wiki page deletion, no bulk renames, every claim
traces to ≥1 source, bulk re-ingest preserves `.legacy/`, no silent
web fetches, multi-modal sources require explicit read-bound
declarations — each carry a load-bearing failure-mode rationale and a
sanctioned escape hatch (where one exists). Full table:
[`red-lines.md`](red-lines.md). The contract is one sentence per
rule at [`AGENTS.md` §"Red lines"](../../AGENTS.md#6-red-lines-non-negotiable).

---

## Operation writes red line (AGENTS007)

Each commit declares an *operation* via its commit-message prefix; the
validator rejects writes outside that operation's declared scope.
Without this rule, the LLM can silently bundle "small fixes" into an
ingest commit, and the audit trail loses the property that *one
operation = one bounded blast radius*. AGENTS007 keeps every commit's
scope matched to its operation.

Full per-prefix scope table + bypass usage:
[`operation-scopes.md`](operation-scopes.md). Machine-readable source:
[`_system/densa/schema.py`](../../_system/densa/schema.py) `OPERATIONS`
(assembled into globs by
[`_system/densa/config.py::OPERATION_WRITES`](../../_system/densa/config.py)).

---

## Routing: where does a new source go?

The decision tree lives in
[`AGENTS.md` §"Routing rules"](../../AGENTS.md#5-routing-rules-where-does-a-new-source-go)
— five ordered rules, terminating in *"ask one short clarifying
question"* when ambiguous. The two load-bearing disambiguators worth
pinning:

- **"Dominant working subject"** — which L2's persona is best-fit for
  what the raw is *about*. A therapy session that mentions a project
  decision is dominantly therapy, not projects.
- **"Stricter privacy posture"** — when two L2s could legitimately
  host the same raw, prefer the L2 with tighter privacy rules.
  Forward migration (strict → loose) is easy; reverse is not.

The `inbox/` folder is a deliberate escape hatch — see
[L1 §"process-inbox"](../../AGENTS.md#24-process-inbox-optional-opt-in)
for the triage flow. The LLM must not silently guess a domain for an
inbox file.

---

## Engineering hooks

The red lines above are easy to *describe* and hard to *uphold*
without enforcement. The [`densa`](../../_system/densa/) package
turns the soft norms into hard rules.

### Rule registry

Each rule has a stable ID (`AGENTS00N`) so users can target it with
`--select` / `--ignore` and reference it in `# noqa` comments without
fearing renumbering. The canonical table lives in
[`AGENTS.md` §"Machine-enforced rule registry"](../../AGENTS.md#61-machine-enforced-rule-registry)
— see that section for the ID → rule → anchor mapping. At runtime,
`python -m densa rules`
prints the table direct from the code (the rule registry is assembled
in [`_system/densa/config.py::RULES`](../../_system/densa/config.py);
the underlying schema data lives in
[`_system/densa/schema.py`](../../_system/densa/schema.py));
both the AGENTS.md mirror and this section are documentation.

### Architecture

```
_system/densa/
├── __init__.py     — public API: lint_staged / lint_all / lint_paths / Diagnostic
├── __main__.py     — `python -m densa`
├── cli.py          — argparse: lint / rules / version subcommands
├── runner.py       — orchestration: source → rules → Report
├── config.py       — schema constants + RuleSpec registry
├── paths.py        — pure-function path classifiers
├── frontmatter.py  — YAML parsing: stdlib (default) + pyyaml (extras)
├── wikilink.py     — scan() + resolve() against a built slug index
├── git_io.py       — typed wrappers around `git diff --cached`
├── report.py       — Diagnostic, Severity, Report dataclasses
├── formatters.py   — text / JSON / GitHub Actions output
└── checks/         — one Rule class per stable ID
    ├── base.py     — FileRule / StagedRule protocols
    ├── raw_immutability.py
    ├── log_append_only.py
    ├── frontmatter_required.py
    ├── analysis_sources.py
    ├── wikilink_resolvable.py
    └── operation_writes_scope.py
```

Two rule protocols, on purpose: a `FileRule` is asked "is this *one
file* invalid?"; a `StagedRule` is asked "is this *change set* shape
invalid?". Mixing both into a single `check(...)` signature was the
hottest spot of glue code in the predecessor.

### Dependency tiers

The pre-commit hook (`_system/hooks/pre-commit`) is the path that runs
on every `git commit`, and so is **pure stdlib**: no `pip install`
required before adopting the template. The hook just sets
`PYTHONPATH` and invokes `python -m densa --staged` from the in-repo
package.

CI and local `--all` runs can opt into the `[strict]` extra
(`pip install -e ".[strict]"`) which pulls in **pyyaml** for full
YAML parsing (nested maps, anchors, multi-line strings). The default
frontmatter parser is stdlib-only and handles the subset templates
actually use.

### Tests

The `_system/tests/` suite exercises every rule with a hermetic
mini-vault fixture, plus parser, formatter, and runner integration
tests. CI runs `pytest`, `ruff`, and `mypy --strict` on every PR
touching `_system/densa/`. Bypass exists (`git commit --no-verify`)
but is a deliberate emergency exit, not a routine.

---

## How to design your own L2

When you stand up a new domain, you're answering four questions:

### 1. Persona — what voice should the LLM adopt for this domain?

Examples:

- *"You are a careful, integrative psychotherapy companion. You hold
  multiple frameworks (psychodynamic, CBT, attachment, IFS) without
  collapsing one into the other."*
- *"You are a sharp PM/architect/strategist hybrid. You compress
  meetings and decisions into a queryable graph keyed on projects,
  stakeholders, and ADRs."*
- *"You are a careful evidence-curator and N-of-1 experiment designer.
  You weigh mechanism vs effect size vs evidence quality
  (RCT > meta-analysis cohort > mechanism > anecdote)."*

The persona shapes every synthesis the LLM produces in this domain.
Spend real time getting it right — it's the most leverage-y two
paragraphs in the whole L2.

### 2. Folder layout under `raw/` and `wiki/`

What kinds of source material will you drop in (sessions? meetings?
articles? lessons? metric exports? voice memos?), and what kinds of
wiki pages will the LLM produce (entities? concepts? patterns? themes?
analyses? syntheses? protocols? experiments? decisions?)? Each
deserves its own bucket.

Start small. You can always add a bucket later by editing the L2
schema and running `lint` to surface any pages that should move.

### 3. Page types + per-type frontmatter additions

Take the L1 nine-type set as a menu, pick the ones this domain needs,
and add domain-specific required fields. Sub-categorise within a v2
type via L2-specific `kind:` / `session_kind:` / similar — never
invent a new top-level `type:` value. Examples:

- A psychology L2: `source` pages tagged `session_kind: therapy`
  must carry `date`, `participants`, `mode`; recurring behavioural
  patterns live as `concept` pages with L2 fields `triggers`,
  `first_observed`, `last_observed`, `severity`.
- A projects L2: project entities (`type: entity` +
  `entity_kind: project`) must have `project_status`, `owners`,
  `priority`; decisions (`type: entity` + `entity_kind: decision`)
  must have `decision_id`, `decided_on`, `supersedes`,
  `superseded_by`.
- A self-optimisation L2: training-protocol concepts (`type: concept`
  + `concept_kind: protocol`) must carry `area`, `evidence`
  (mechanism / observational / rct / anecdote), `last_revised`;
  experimental-run summaries (`type: summary` +
  `summary_kind: experiment`) must have `experiment_id`,
  `hypothesis`, `outcome`, `metric_links`.

### 4. Domain-specific lint rules

What signals "this domain's wiki is drifting"? Examples:

- *"Every `concept` tagged `concept_kind: pattern` must cite ≥ 2
  distinct summaries, else it's premature abstraction → flag for
  inline-merge into the single existing summary."*
- *"Every project entity with `project_status: active` must have a
  decision entity logged in the last 30 days, else flag as stale."*
- *"`concept_kind: protocol` pages cited in ≥ 3 summaries but
  evidence still tagged `anecdote` → flag for evidence-upgrade hunt."*

Wire these into the L2 AGENTS.md's "Domain-specific lint rules"
section. The `lint` operation reads them automatically.

### Three example domain seeds (to open the space)

| Domain idea            | Persona seed                                                   | Page types you'd want                                                        |
| ---------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Research-paper reading | careful science-historian, evidence-ladder discipline          | `source`, `summary`, `concept`, `overview`, `synthesis`, `open-question`     |
| Family / relationships | warm, observant relationship-tracker; not a therapy stand-in   | `source`, `summary`, `entity`, `concept`, `open-question`, `synthesis`       |
| Language learning      | structured pedagogy + spaced-repetition mindset                | `source`, `summary` (per lesson), `concept`, `comparison` (target vs native) |

The shipped active default `domains/research-papers/` follows the
first row almost verbatim. A lighter L2 with three page types and
one lint rule is perfectly fine, and is often what you want for
your first try.

---

## Optional layers: `projects/` and `writing/`

Two top-level directories are **opt-in scaffolding** — the bootstrap
prompt asks whether you need them, and skips both by default. Neither
is wired into the lint contract; they are pure directory conventions
plus templates.

### `projects/<slug>/`

Multi-week research / experiment workspaces that don't yet belong
in any L2's `wiki/`. Each `<slug>/` subdir is free-form:

```text
projects/<slug>/
├── README.md          ← one-paragraph thesis + status
├── hypotheses/        ← what you expect to find
├── experiments/       ← experiment write-ups (one per run)
├── notes/             ← scratch thinking, meeting summaries
└── raw/               ← project-local raw material (still immutable)
```

When a project concludes, `git mv` its conclusions into the relevant
domain's `wiki/syntheses/` (or wherever the conclusion fits). The
workspace itself can stay in `projects/<slug>/` as a historical record
or migrate to `attic/projects/<slug>/`.

Enable when: you regularly run multi-week investigations that
generate hypothesis-test cycles. Skip when: your work is single-shot
ingest / query / lint loops over already-curated raw.

### `writing/{drafts,published}/`

Output layer for blog posts, newsletters, public threads that
*consume* wiki knowledge. Drafts live in `writing/drafts/<slug>.md`
and graduate to `writing/published/<slug>.md` once shipped. Templates:
[`_system/templates/writing-draft.md`](../../_system/templates/writing-draft.md),
[`_system/templates/writing-publication.md`](../../_system/templates/writing-publication.md).

Frontmatter is **advisory**, not enforced — `writing/` is in
`densa.config.WIKILINK_SKIP_TOP_LEVEL`, so its pages are fully outside
the AGENTS003-006 scope. The shipped draft/publication templates carry
historical `type: fleeting` placeholders; rewrite them however suits
your publishing workflow (the validator never visits these paths).
If you want post-publication immutability, add a per-L2 lint rule for
it; the template ships none.

Enable when: you actively publish externally and want your drafts in
the same repo as the wiki they cite. Skip when: you compose in a
separate tool (Notion, Bear, Drafts.app, etc.).

### Why these are not first-class

- **No new page types.** Both layers reuse existing L1 types
  (`entity` for projects / decisions, `summary` for individual
  experiments, free-form frontmatter for drafts). Adding bespoke
  types here would inflate the L1 schema for a feature most vaults
  skip.
- **No new lint rules.** `projects/` and `writing/` are in the
  no-prefix write-scope allow-list (AGENTS007), so maintenance
  commits can touch them, but no AGENTS rule enforces structure.
- **No automation for project conclusion / publication moves.**
  These are deliberate human-in-the-loop decisions; a script would
  encourage premature compression of in-progress work into the wiki.

---

## Anti-patterns to avoid

| Anti-pattern                                                       | Why it hurts                                                            | Fix                                                                  |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Auto-ingesting on file drop                                        | Surprise edits across many wiki pages, no human approval gate           | Always plan first, get OK, then apply ([L1 §"ingest"](../../AGENTS.md#21-ingest-path)) |
| Editing `raw/` to "fix" a wiki claim                               | Closed epistemic loop; wiki ends up citing its own corrections          | Fix the wiki page; leave raw alone                                   |
| Letting `summary.sources` grow to length 2+                        | Confuses 1:1 summary with cross-source synthesis                        | Promote to `synthesis`; move under `wiki/syntheses/`                 |
| Letting a `concept` page with `concept_kind: pattern` stay with 1 instance | Premature abstraction; the "pattern" is really a single-summary note | Inline it back into the relevant summary until a 2nd instance appears |
| Skipping `last_validated` bumps on `concept` / `entity` pages      | Pages drift silently as cited sources evolve                            | When you re-check sources, bump the timestamp (don't bump if you didn't) |
| Cloning the psychology showcase wholesale because it's there        | You inherit ~280 lines of complexity you don't need; it's still v1      | Design your L2 from the four questions above; copy *patterns*, not files |
| Using `wiki/syntheses/` as a dumping ground for second-order pages  | `concept`, `overview`, `comparison`, `open-question` all have homes    | If a page recurs and has stable structure, file it under the matching type |
| Inventing a new top-level `type:` value not in L1's nine             | Breaks AGENTS004; the schema is closed at L1                            | Sub-categorise within an existing type via an L2 `kind:` field instead |

---

## Where to go next

- Try the
  [bootstrap prompt](../bootstrap.md) flow once
  you've instantiated the template into a new directory (via GitHub
  fork or `degit`).
- Read the L1 schema in full: [`AGENTS.md`](../../AGENTS.md).
- Read the active default L2 (v2 schema) to see how the contract
  lands in practice:
  [`domains/research-papers/AGENTS.md`](../../domains/research-papers/AGENTS.md).
  The two v1 showcases under `examples/showcases/{workspace,psychology}/`
  are heavier reference material — useful for design inspiration,
  but they predate `schema_version: 2`.
- Read the five canonical operation prompts under
  [`_system/prompts/`](../../_system/prompts/) — they're the contracts
  the LLM actually executes against.
