---
type: manual
scope: vault
updated: 2026-05-21
compiled_against: 1
---

# LLM Wiki — User Manual

> A second brain built on Andrej Karpathy's `llm-wiki` pattern,
> instantiated for an LLM agent (Cursor / Claude Code / Codex / etc.)
> operating over an Obsidian vault.
>
> **Authority split.**
> - [`/AGENTS.md`](../AGENTS.md) (L1) and `domains/<X>/AGENTS.md` (L2)
>   are **normative** — the machine-readable contracts the LLM obeys.
>   Any rule that affects an `ingest` / `query` / `lint` outcome lives
>   there.
> - This MANUAL is **explanatory** — it answers *why* the design looks
>   the way it does, walks through scenarios, and serves as a FAQ.
>
> When MANUAL and AGENTS disagree, **AGENTS wins**. Schema-shaped
> tables in §3 are mirrors of the canonical ones; they exist for human
> reading convenience but the canonical source is always AGENTS.md.

---

## 0. Cheat sheet

| Operation                | Command template                                  | Writes to                                  |
| ------------------------ | ------------------------------------------------- | ------------------------------------------ |
| Add a new source         | drop the file into `domains/<X>/raw/<bucket>/`    | `raw/` (you manually place it)             |
| Process a new source     | `ingest <path>`                                   | `wiki/analyses/` + several wiki nodes + log |
| Ask the wiki a question  | `query <natural-language question>`               | (read-only + optional file-back to `outputs/qa/<date>-<slug>.md`) |
| Maintain the wiki        | `lint [--domain <X>]`                             | `outputs/lint/<date>.md` + `outputs/snapshots/index-snapshot.md` |
| Triage unrouted material | `process-inbox`                                   | `git mv inbox/<file> → domains/<X>/raw/<bucket>/`; logs (no wiki edits — `ingest` is a separate step) |
| Upgrade a Q&A to wiki    | `promote outputs/qa/<file>.md [--as <type>]`      | `git mv` Q&A → `domains/<X>/wiki/<type>/<slug>.md` + logs |

| Page type     | 1:n     | Folder                                | `sources` length / target                          |
| ------------- | ------- | ------------------------------------- | -------------------------------------------------- |
| `source`      | n=1     | `raw/<bucket>/`                       | n/a (the file *is* the source)                     |
| `analysis`    | 1:1     | `wiki/analyses/`                      | **= 1**, points at raw (≠ 1 → promote to synthesis) |
| `synthesis`   | many:1  | `wiki/syntheses/`                     | ≥ 2, points at raw or wiki pages (incl. analyses)  |
| `entity`      | reused  | `wiki/entities/`                      | ≥ 1, points at raw or analyses (where it first appears) |
| `concept`     | reused  | `wiki/concepts/`                      | ≥ 0 (evergreen), ≥ 1 once cited                    |
| `pattern`     | reused  | `wiki/patterns/`                      | ≥ 2, points at raw or analyses (pattern instances) |
| `theme`       | reused  | `wiki/themes/`                        | ≥ 2, points at raw or analyses (multi-source arc)  |
| `framework`   | reused  | `wiki/frameworks/`                    | ≥ 1, points at the literature or canonical wiki    |

> See [`AGENTS.md`](../AGENTS.md) §3.1 for the full per-type schema —
> that table is the source of truth.

| Red line                                                | Guardian |
| ------------------------------------------------------- | -------- |
| `raw/` is immutable                                     | L1 §6 + `wikilint` (AGENTS001) |
| `log.md` is append-only                                 | L1 §6 + `wikilint` (AGENTS002) |
| Never delete wiki pages (deprecate instead)             | L1 §4    |
| `analysis.sources` length = 1                           | L1 §3.1 + `wikilint` (AGENTS005) |
| Each commit's writes stay within its operation's scope  | L1 §2.0 + `wikilint` (AGENTS007) |
| Ingest must plan first and wait for confirmation        | L1 §2.1  |

---

## 1. Mental model

### 1.1 One-sentence definition

> **Wiki is the codebase, Obsidian is the IDE, the LLM is the
> programmer.** You only do three things: select sources, ask
> questions, and review. Everything else happens as incremental edits
> the LLM applies to the wiki.

### 1.2 Three semantic layers

```
+-------------------------------------------------------+
|  AGENTS.md  <- rules (schema, operations, red lines)  |
+-------------------------------------------------------+
|  wiki/      <- hypotheses (LLM-owned, rewritten freely)|
+-------------------------------------------------------+
|  raw/       <- evidence (immutable, append-only)      |
+-------------------------------------------------------+
```

- **`raw/` is fact.** Clipped articles, transcribed sessions, recorded
  meetings. The LLM never edits them. Their purpose is to let you
  return three years from now and verify the source of any wiki claim.
- **`wiki/` is the current best model.** It is rewritten repeatedly.
  Its purpose is to compress information in `raw/` into queryable,
  reasonable, presentable structured knowledge.
- **`AGENTS.md` is the contract.** It tells the LLM which material
  goes into which bucket, which pages each `ingest` should touch, and
  what `lint` should check. Editing AGENTS.md = editing the language
  the LLM and you share.

### 1.3 Why this is not RAG

| Dimension       | RAG                                       | LLM Wiki (this design)                  |
| --------------- | ----------------------------------------- | --------------------------------------- |
| At query time   | retrieve raw chunks → stitch an answer    | read the already-compiled wiki → answer |
| Compounding     | none (each query starts from zero)        | monotonic (every ingest densifies wiki) |
| Backlinks       | not explicit                              | enforced (`sources:` frontmatter)       |
| Readability     | opaque (vector index)                     | wiki is markdown for humans             |
| Maintenance     | almost none (also barely maintainable)    | LLM does the work, human reviews        |
| Best scale      | millions of chunks, low query frequency   | hundreds of sources, high synthesis frequency |

If your wiki grows past ~300 pages and the `index.md` routing layer
starts to miss, layer Smart Connections (embedding search) on top as
a fallback. At smaller scales you don't need it.

---

## 2. Physical layout

### 2.1 Annotated directory tree

```
<vault>/
├── AGENTS.md                   ← L1 schema: operations, routing, frontmatter, red lines
├── index.md                    ← global index: links to each domain + global log + cross-domain syntheses
├── log.md                      ← global timeline, cross-domain events
├── .gitignore
│
├── _system/                    ← system layer, not wiki content
│   ├── MANUAL.md               ← this file
│   ├── SETUP.md                ← one-time install steps (plugins, Web Clipper, git-crypt)
│   ├── prompts/
│   │   ├── ingest.md           ← canonical procedure for `ingest`
│   │   ├── query.md            ← canonical procedure for `query`
│   │   ├── lint.md             ← canonical procedure for `lint`
│   │   ├── process-inbox.md    ← canonical procedure for `process-inbox`
│   │   ├── promote.md          ← canonical procedure for `promote`
│   │   └── domains/            ← domain-specific sub-prompts (optional)
│   ├── templates/              ← Templater page templates (one per page type)
│   ├── wikilint/               ← red-line enforcement package (called by pre-commit)
│   ├── scripts/
│   │   └── setup_encryption.sh ← one-time git-crypt bootstrap (opt-in)
│   └── hooks/
│       └── pre-commit          ← runs `python -m wikilint --staged` on every commit
│
├── domains/
│   ├── research-papers/        ← light L2 (6 page types) — 4-paper LLM-tutoring arc
│   │   ├── AGENTS.md
│   │   ├── index.md
│   │   ├── log.md
│   │   ├── raw/                ← 4 papers + clipped abstracts (synthesised stand-ins)
│   │   └── wiki/               ← analyses, concepts, frameworks, syntheses, questions
│   ├── workspace/              ← medium L2 — meetings / decisions / stakeholders
│   │   ├── AGENTS.md
│   │   ├── index.md
│   │   ├── log.md
│   │   ├── raw/                ← Q2 platform-migration meeting transcripts
│   │   └── wiki/               ← analyses, decisions, stakeholders, teams, projects
│   ├── psychology/             ← heavy L2 — 6-week father-grief worked arc
│   │   ├── AGENTS.md           ← thorough L2 schema; privacy-posture callout
│   │   ├── index.md
│   │   ├── log.md
│   │   ├── raw/                ← 3 therapy + 1 psychiatry session (synthesised)
│   │   └── wiki/               ← ~25 pages: analyses, themes, patterns, syntheses, …
│   └── <your-domain>/          ← add as many L2s as you need
│
├── outputs/                    ← operation artifacts (in git, outside wikilink graph)
│   ├── lint/<YYYY-MM-DD>.md    ← lint reports (type: report)
│   ├── qa/<YYYY-MM-DD>-*.md    ← query Q&A archives (type: report)
│   └── snapshots/              ← machine-readable index mirror (§1.1)
│
├── docs/                       ← project meta documentation (DESIGN, EXAMPLES, …)
├── integrations/               ← (optional) agent-specific UX add-ons (claude-code)
├── inbox/                      ← optional: un-routed material (see L1 §2.4)
└── attic/                      ← deprecated / quarantined files
```

### 2.2 Who writes where

| Path                    | You write   | LLM writes      | Tracked by git |
| ----------------------- | ----------- | --------------- | -------------- |
| `raw/`                  | yes (once)  | **never**       | yes            |
| `wiki/`                 | discouraged | yes             | yes            |
| `*/log.md`              | rare notes  | primary author  | yes            |
| `*/index.md`            | rare        | small manual additions | yes      |
| `AGENTS.md` / templates / scripts | co-authored with LLM, you approve | proposes changes | yes |
| `attic/`                | as needed   | does not write proactively | yes |

---

## 3. Operations at a glance

The five operations are the **only** verbs the human uses on the
vault. Their canonical procedures live in `_system/prompts/`; the
LLM reads the relevant prompt before acting.

- **`ingest <path>`** — file a new raw source into the wiki. The LLM
  reads the source, drafts a plan listing every page it intends to
  touch, waits for your confirmation, then applies the edits. See
  [`_system/prompts/ingest.md`](prompts/ingest.md) and L1 §2.1.

- **`query <question>`** — ask the wiki a question. The LLM walks
  `index.md` → relevant per-domain `index.md` → candidate pages →
  inline-cited answer. Non-trivial answers default to being filed
  back as a new `synthesis`. See [`prompts/query.md`](prompts/query.md)
  and L1 §2.2.

- **`lint [--domain <X>]`** — health-check the wiki. The LLM produces
  a markdown report under `outputs/lint/<date>.md` (`type: report`)
  listing orphan pages, broken wikilinks, contradictions, stale claims,
  missing cross-references, etc., plus a refreshed
  `outputs/snapshots/index-snapshot.md` for the next fresh LLM session.
  Auto-applies only additive low-risk fixes; everything else waits for
  your review. See [`prompts/lint.md`](prompts/lint.md) and L1 §2.3.

- **`process-inbox`** — triage un-routed material that has been
  dropped into `/inbox/`. The LLM proposes a domain + bucket + slug
  for each file and `git mv`s them after your confirmation. It does
  **not** ingest; that is a deliberate next step. See
  [`prompts/process-inbox.md`](prompts/process-inbox.md) and L1 §2.4.

- **`promote <qa-path>`** — lift a Q&A artifact under
  [`outputs/qa/`](../outputs/) into a first-class wiki page (e.g.
  `synthesis`, `concept`, `framework`). The LLM runs pre-flight
  checks (target type allowed; slug+aliases dedup; `sources`
  cardinality), then performs a four-stage information-shape
  transform: voice (Q→declarative), citation hoist (inline
  `[[wikilinks]]` → frontmatter `sources:`), L2 fill-in
  (type-specific required fields), section restructure (apply target
  template). One commit, `git mv` preserves history. See
  [`prompts/promote.md`](prompts/promote.md) and L1 §2.5.

---

## 3.1 When a Q&A deserves to be promoted

`promote` is not the default lifecycle for Q&A artifacts. Most Q&A
write once, consume once, and age out — that's healthy. Reach for
`promote` only when **all three** of the following hold:

| Signal                        | Translation                                                          |
| ----------------------------- | -------------------------------------------------------------------- |
| **Evergreen claim**           | The answer doesn't depend on a specific timestamp (concept beats event). |
| **≥ 2 distinct sources** in body | Inline `[[wikilinks]]` already satisfy the target type's §3.1 cardinality. |
| **Repeated visits**           | You catch yourself re-reading this Q&A across separate sessions; or `lint` flags it under "Promotion candidates". |

Anti-signals (skip promote, let the Q&A age out under `outputs/qa/`):

- The question is "what did I say about X last week?" — the answer is
  inherently time-bound; promoting would freeze a snapshot the wiki
  doesn't need.
- The Q&A's "Sub-claims" are themselves tentative and the
  load-bearing prose is "I'm not sure, but…" — promote requires
  declarative voice; an unresolved question belongs in `wiki/questions/`
  via `--as question`, not in `wiki/syntheses/`.
- The Q&A cites only 1 raw file. Either enrich it inline (re-run a
  follow-up `query` to add citations) or promote `--as concept`
  (which allows `sources ≥ 0`) — never inflate fake citations to
  pass pre-flight.

When in doubt, leave the Q&A in `outputs/qa/`. Promote is reversible
via `git revert`, but the wiki page it produces will accumulate
inbound wikilinks once visible; the reverse migration is harder once
the link graph adopts it.

---

## 4. FAQ

### Why is `raw/` immutable?

Because the wiki's epistemic integrity depends on being able to walk
any claim back to a verifiable source. If raw is editable, the LLM's
own past synthesis errors can silently propagate into the evidence
base, and the wiki becomes a closed epistemic loop (it cites itself,
not the world). The pre-commit hook enforces this; the only sanctioned
exception is a transcription-correction sweep documented per-L2 (see
e.g. the psychology L2's "Known transcription corrections" section).

### Why is `log.md` append-only and reverse-chronological?

Append-only because the log is the audit trail of every ingest /
query / lint; rewriting it would erase the LLM-vs-human collaboration
history. Reverse-chronological because the human reads top-down and
the most recent state is what matters. When position drift happens,
the `WIKI_ALLOW_LOG_REORDER=1` bypass permits a single-shot reorder
sweep — but the diff must be a pure permutation plus a maintenance
audit entry.

### Why don't we delete wiki pages?

Wikilinks propagate. Deleting `[[xyz]]` silently breaks every page
that referenced it; renaming is a cascade you must own consciously.
The deprecation pattern (set `status: deprecated`, add a `>
Superseded by [[new-page]]` redirect line at the top, remove from
the index) keeps the link graph intact while the page becomes a
gravestone pointing at its successor.

### How big can the wiki get before it stops scaling?

Empirically, the `index.md` Dataview routing layer suffices to about
~500 wiki pages. Past that, two early-warning signals: any single
Dataview block exceeds ~50 rendered rows, or `index.md` rendering
becomes noticeably slow. Either fires → migrate to Obsidian Bases
(`.base` files) or layer Smart Connections (embedding search) on
top. Until then Dataview is more diff-friendly in git and the LLM
operates on its source markdown more naturally.

### How do I know when a claim has drifted?

`lint` will flag:
- pages whose `last_validated` is older than 180 days (concept /
  framework / protocol / entity types) — re-read the cited sources,
  bump the timestamp.
- citation chains that take more than 2 hops to reach a `raw/` file
  — claims that float without recent evidence anchor.
- patterns / themes whose latest instance is older than the L2's
  configured staleness threshold.
- contradictions where two pages make opposite claims about the same
  entity / concept.

Treat `lint` reports as work-in-progress dashboards, not pass/fail
gates. The goal is a "boring" lint report: each subsequent run mostly
reports "no new findings since last lint", with the human-review
queue draining gradually as you walk down it.

### My vault is mostly in Chinese — anything special I need to know?

Yes; see [`../docs/CJK-WORKFLOW.md`](../docs/CJK-WORKFLOW.md). The
schema is language-neutral, but the recommended conventions for
slugs, aliases, commit messages, and lint-report language are
documented separately so a CJK-first vault stays internally
consistent.

### What is this, in one sentence?

A schema + LLM prompt set + tiny validator that lets you and a
coding-agent LLM (Cursor / Claude Code / Codex / similar) jointly
maintain a personal Obsidian wiki, where the LLM does the bookkeeping
and you curate sources and ask questions.

### Do I need Obsidian?

No — the wiki is plain markdown with YAML frontmatter and
`[[wikilink]]` syntax. Any editor works. Obsidian adds three things
this template benefits from:

- **Dataview** plugin: the dynamic blocks in every `index.md` rely on
  it. Without Dataview the indices fall back to static markdown —
  still readable, just no auto-refresh.
- **Templater** plugin: bound to `_system/templates/` so "New note"
  buttons drop the right frontmatter for each page type.
- **Graph view**: makes the entity / pattern / concept link
  structure visible at a glance.

If you prefer VSCode or Neovim, point an Obsidian-compatible markdown
parser at the same folder; the LLM agent doesn't care about the
editor.

### Why aren't lint reports under `wiki/`?

Lint reports are *operation artifacts*, not compiled knowledge.
Three problems with the older "drop them in `wiki/syntheses/`" layout:

- Reports accumulate as noise but L1 §4 forbids deleting wiki pages,
  so old reports cannot be cleaned up cleanly.
- `type: synthesis` requires `sources: ≥ 2`; a lint report doesn't
  fit that contract.
- `query` would occasionally cite a lint report as if it were
  knowledge, polluting answers.

The fix is a separate top-level `outputs/` directory: in git for the
audit trail, but excluded from the wikilink graph and the wiki's
schema contracts. Reports point at wiki pages; wiki never points back.

### What does `outputs/` contain?

Three buckets today:

- `outputs/lint/<YYYY-MM-DD>.md` — one report per lint run.
  Frontmatter is `type: report`; `sources` may be empty.
- `outputs/snapshots/index-snapshot.md` — the machine-readable mirror
  of every `index.md` Dataview block. Regenerated by every `lint` run
  and consumed by fresh LLM sessions as part of the four-file
  onboarding set ([AGENTS.md §1.1](../AGENTS.md) step 4).
- `outputs/qa/<YYYY-MM-DD>-<slug>.md` — Q&A archives from non-trivial
  `query` runs (same `type: report` artifact contract as lint reports).

Retention is user-managed: there is no auto-rotation. When `outputs/`
grows noisy, `git rm outputs/{lint,qa}/<old>.md` deletes safely (no
wiki page can link there, by design).

### Where do Q&A answers go, and why not `wiki/syntheses/`?

Substantive `query` answers are filed as `type: report` Q&A artifacts
under `outputs/qa/<YYYY-MM-DD>-<slug>.md` — alongside `outputs/lint/`
and `outputs/snapshots/`, not inside `wiki/`. The reasoning matches
why lint reports moved out: a Q&A is a snapshot of one conversation,
not a stable cross-source synthesis. Three concrete benefits:

1. **No fake `sources`.** Reports allow `sources: []`; a Q&A doesn't
   have to inflate its citations to satisfy `synthesis.sources ≥ 2`.
2. **Wikilink graph stays clean.** Lint's orphan / hub / ring
   detectors only see real wiki structure, not transient query
   products.
3. **Retention is simple.** `git rm outputs/qa/<old>.md` removes
   noise without breaking any wiki link, because the resolver doesn't
   look at `outputs/`.

If a particular answer turns out to be evergreen and worth
wikilink-graph membership, the path forward is `promote` (see §3.1).

### Can I run this with a non-Cursor agent?

Yes. The prompts and schema are agent-agnostic. The template is
tested with Cursor and Claude Code, but anything that can read
`AGENTS.md`, follow markdown templates, and run shell commands works.
The required file-system tools per operation are read / write / `git
mv` / `git diff` — no exotic capabilities.

### Do I have to use the example domains?

No. The three domains under `domains/` are all worked examples (see
[`../docs/EXAMPLE-DOMAINS.md`](../docs/EXAMPLE-DOMAINS.md)) covering
the **light → medium → heavy** schema-density spectrum:

- `domains/research-papers/` — **light** (6 page types), a 4-paper
  LLM-tutoring causal-evidence arc.
- `domains/workspace/` — **medium** (meetings / decisions /
  stakeholders), a Q2 platform-migration arc.
- `domains/psychology/` — **heavy** (~25 wiki pages from 4 sources),
  a 6-week father-grief therapy + psychiatry worked arc.

You can:

- Rename one and adapt its L2 (`git mv domains/<example>
  domains/<your-name>`), or
- Delete the whole example directory and design your L2(s) from
  scratch using the four design questions in
  [`../docs/DESIGN.md`](../docs/DESIGN.md) §"How to design your own
  L2", or
- Move an example under `domains/.legacy-example-<name>/` to keep it
  as a browsable reference without treating it as live (the bootstrap
  prompt's default recommendation; see
  [`../docs/EXAMPLE-DOMAINS.md`](../docs/EXAMPLE-DOMAINS.md) Option B).

The bootstrap prompt walks you through this decision; see
[`../docs/bootstrap-prompt.md`](../docs/bootstrap-prompt.md) Step 4.

### Will this work with private / sensitive material?

Yes, with care. See [`../SECURITY.md`](../SECURITY.md) for the
hardening checklist (git-crypt, cold backup remote, hardware-token
GPG keys). The template ships `setup_encryption.sh` and a
`.gitattributes.example` to make encrypted `raw/` trees a one-command
setup, and the psychology L2 demonstrates the two privacy postures
(public-shareable vs private-repo) in §"Privacy posture".

### What does CI run?

A single GitHub Actions workflow
(`.github/workflows/validate.yml`) that runs `python -m wikilint
--all` on every push and pull request. It enforces the L1 red lines
and frontmatter contract. No third-party dependencies are required.
