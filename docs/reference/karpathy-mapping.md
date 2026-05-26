---
type: overview
domain: meta
created: 2026-05-24
updated: 2026-05-24
sources: []
tags: [karpathy, glossary, schema-v2]
aliases: ["karpathy mapping", "llm-wiki glossary"]
status: active
compiled_against: 2
---

# Karpathy llm-wiki ↔ Densa mapping

> This project is a full, executable implementation of Andrej Karpathy's
> [llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
> Karpathy described the idea in ~1500 words; Densa gives you the
> schema, the validator, the prompts, and three worked example
> domains so you can run the idea tomorrow.

This page is the bilingual glossary between Karpathy's prose and
Densa's machine-enforced contracts. **Every vocabulary item Densa
uses comes from Karpathy's gist** — if you wanted "is this thing
familiar from llm-wiki?" the answer in v2 is always yes.

## The five-second pitch (in Karpathy's own words)

> Most people's experience with LLMs and documents looks like RAG …
> the LLM is rediscovering knowledge from scratch on every question.
> There's no accumulation. The idea here is different. Instead of
> just retrieving from raw documents at query time, **the LLM
> incrementally builds and maintains a persistent wiki** … The
> knowledge is compiled once and then *kept current*, not re-derived
> on every query.
>
> — [llm-wiki gist, "The core idea"](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Vocabulary side-by-side

The table below mirrors `densa.schema.PAGE_TYPES`. The
**Karpathy term** column quotes the phrase verbatim from the gist;
**Densa name** is what you use in frontmatter `type:`; **Folder**
is the recommended sub-folder under `domains/<X>/wiki/` (L2s may
regroup as long as `type:` stays canonical).

| Karpathy term | Densa name      | Folder              | Lives under                 |
|---------------|-----------------|---------------------|-----------------------------|
| raw source    | `source`        | (none)              | `domains/<X>/raw/`          |
| summary page  | `summary`       | `summaries/`        | `domains/<X>/wiki/summaries/` |
| entity page   | `entity`        | `entities/`         | `domains/<X>/wiki/entities/`  |
| concept page  | `concept`       | `concepts/`         | `domains/<X>/wiki/concepts/`  |
| comparison    | `comparison`    | `comparisons/`      | `domains/<X>/wiki/comparisons/` |
| overview      | `overview`      | `overviews/`        | `domains/<X>/wiki/overview.md` (per-domain entry) + `domains/<X>/wiki/overviews/` (sub-area views) |
| synthesis     | `synthesis`     | `syntheses/`        | `domains/<X>/wiki/syntheses/` |
| open question | `open-question` | `open-questions/`   | `domains/<X>/wiki/open-questions/` |

Three operation names also come straight from the gist:

| Karpathy term | Densa operation | Procedure                              |
|---------------|-----------------|----------------------------------------|
| ingest        | `ingest`        | `_system/prompts/ingest.md`            |
| query         | `query`         | `_system/prompts/query.md`             |
| lint          | `lint`          | `_system/prompts/lint.md`              |

Plus two operations Densa added to round out the workflow:

| Densa operation  | What it does                                                                  | Why it isn't in the gist                                  |
|------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------|
| `process-inbox`  | Triage un-routed material in `/inbox/` into `domains/<X>/raw/<bucket>/` via `git mv`. | The gist assumes you already know which raw bucket a source belongs in. In practice, mobile-clipped material often doesn't, and a separate triage step keeps `ingest` honest. |
| `promote`        | Lift an evergreen Q&A from `outputs/qa/` into a first-class wiki page.        | The gist mentions filing query answers back into the wiki; `promote` is the controlled transform that does that without losing provenance. |

## What Densa added on top of the gist

The gist is intentionally abstract ("This document describes the
idea, not a specific implementation"). Densa fills in the
load-bearing engineering choices:

- **Multiple `domains/<X>/`.** A single vault can host distinct life
  areas (research papers, work meetings, therapy notes) each with
  its own schema, persona, and ingest flow. Karpathy's gist
  assumes one wiki; in practice a serious user always has more.
- **L1 + L2 schema layering.** `AGENTS.md` at the repo root is the
  universal contract; each `domains/<X>/AGENTS.md` extends or
  overrides it. Lets a vault carry both light L2s (e.g.
  `research-papers/`, 7 page types) and heavy ones (the optional
  `psychology/` showcase, 10+) without conflict.
- **A stdlib-only Python validator (`densa`).** Enforces the schema
  on every commit and in CI. Without mechanical checks, the LLM
  would drift away from any schema you describe in prose.
- **Operation write contracts.** Each of the five verbs declares
  what paths it may touch (`densa.schema.OPERATIONS['<op>'].writes`).
  AGENTS007 enforces this at commit time; AGENTS011 makes sure the
  prompts and schema don't drift apart silently. This is the
  guard rail that lets you ask the AI to extend a contract without
  fearing it changes one place and forgets four others.
- **`outputs/` directory.** Lint reports and Q&A archives are *operation
  artifacts*, not wiki content. Keeping them outside the wikilink
  graph (and outside the `wiki/` immutability rules) means you can
  `git rm outputs/lint/<old>.md` safely. The gist hints at this
  ("good answers can be filed back into the wiki as new pages") but
  doesn't formalise the artifact vs. wiki distinction.
- **Schema versioning + migration scripts.** `densa.schema.SCHEMA_VERSION`
  and the `MIGRATIONS` ledger let `python -m densa migrate` carry an
  existing vault forward when upstream ships a breaking schema
  change. Without this, every schema bump becomes a manual
  carrying-forward chore.

## Upgrade modes (and what `migration_history` records)

A schema bump is **a rename + frontmatter rewrite + wikilink fix-up**,
not a content rewrite. Densa's migration script supports three modes;
`densa migrate --mode <X>` picks one:

| Mode         | Cost                                             | What you keep                                                                    | What you lose                                          |
|--------------|--------------------------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------|
| `in-place`   | **lowest** (no re-ingest)                        | All content. Each page gets a `migration_history` entry recording the rename.    | The prose still reflects the v(N-1) narrative shape — re-ingest only when the content becomes load-bearing. |
| `archive`    | high (you'll re-ingest later)                    | The v(N-1) snapshot in `wiki/.legacy/`.                                          | The live wiki starts empty.                            |
| `recover`    | low (undoes a prior `archive`)                   | Everything from `.legacy/`, lifted back into the vN layout with in-place rules.  | Nothing.                                               |

The default is `in-place`. Pick `archive` when you actively want a
clean slate; pick `recover` when a previous `archive` run feels too
aggressive.

Every page touched by an `in-place` or `recover` migration grows a
`migration_history` list in its frontmatter:

```yaml
migration_history:
  - from: 1
    to: 2
    on: 2026-05-24
    mode: in-place
    notes: 'type analysis → summary'
```

Multi-version jumps accumulate entries (v1 → v2 → v3 each adds a row).
The per-domain `overview.md` template's *"Pages migrated mechanically"*
Dataview block lets you query for pages with this field so you can
decide which ones deserve a fresh ingest later. **AGENTS012** keeps
the field honest by warning on malformed entries.

## Schema_version 1 → 2: what changed and why

v1 was Densa's first attempt and accumulated 18 page types — many
of them workflow-specific (`pattern`, `theme`, `framework`,
`protocol`, `decision`, `correction`) that Karpathy never named.
v2 collapses the type registry back to **the 7 names in the gist
plus `source` and `report`**:

| v1 type        | v2 type         | Why the rename                                                  |
|----------------|-----------------|-----------------------------------------------------------------|
| `analysis`     | `summary`       | Karpathy used "summary page"; "analysis" was too generic.       |
| `framework`    | `overview`      | Engineers read "framework" as React-style; "overview" is the gist's word. |
| `pattern`      | `concept`       | A recurring behavioural pattern is a kind of concept.           |
| `theme`        | `overview`      | A multi-source story arc is best modelled as a sub-area overview. |
| `protocol`     | `concept`       | Clinical / training protocols are concepts with strict rules.   |
| `experiment`   | `summary`       | One experimental run is a kind of source summary.               |
| `project`      | `entity`        | A project is an entity with a lifecycle.                        |
| `stakeholder`  | `entity`        | A stakeholder is a person — the default kind of entity.         |
| `decision`     | `entity`        | A decision is a long-lived entity with an ADR id.               |
| `session`      | `source`        | A therapy / meeting session is a raw source.                    |
| `question`     | `open-question` | Renamed for clarity: the page is always for *open* questions.   |
| `fleeting`     | (removed)       | Short-lived thoughts belong in `inbox/` or `outputs/qa/`, not in the wiki. |
| `correction`   | `synthesis`     | A failure-mode tracker is a multi-source synthesis with a `correction` tag. |
| `synthesis`    | `synthesis`     | Same name.                                                      |
| `concept`      | `concept`       | Same name.                                                      |
| `entity`       | `entity`        | Same name.                                                      |
| `comparison`   | `comparison`    | (new in v2) promoted from a synthesis sub-flavour.              |
| `overview`     | `overview`      | (new in v2) promoted from an implicit pattern.                  |

The 7-type set you carry in your head now: **summary, entity,
concept, comparison, overview, synthesis, open-question**. Every
one of them appears verbatim in the Karpathy gist; non-technical
readers can guess what each does without reading another doc.

The full machine-readable mapping lives in
`densa.schema.KARPATHY_MAPPING`.

## Canonical-fact rules (don't duplicate the underlying claim)

A wiki page graph naturally tends toward duplication — the same
number/quote shows up in the summary that introduced it, the
concept that aggregates it, the open-question whose evidence row
it provides. To keep upgrade-paths cheap and the wiki
non-self-contradictory, v2 prescribes:

1. **Numbers, dates, and verbatim quotes live ONLY in
   `summaries/<slug>.md`** with a raw anchor (timestamp or section).
2. **`concepts/`, `entities/`, `open-questions/`** store wikilinks
   to summaries, never restate the underlying fact.
3. **`overviews/`, `comparisons/`, `syntheses/`** cite
   `[[summary#section]]` anchors, not the raw directly.
4. When the same fact would appear in two wiki pages, pick the
   deepest page (the one closest to raw) as canonical and have the
   other link in.

These rules ship in `densa.schema.CANONICAL_FACTS` and are
referenced from each operation prompt. They are not mechanically
enforced in v2 (fact-duplication heuristics tracked for v3); the
prompts treat them as hard rules and lint includes
spot-checks for verbatim duplication during the citation-depth
pass.

## Why "wiki is the codebase"

Karpathy:

> Obsidian is the IDE; the LLM is the programmer; the wiki is the
> codebase.

Densa operationalises this with three artefacts that act like a
compiler toolchain:

- **`raw/`** is the **source code** — immutable evidence.
- **`wiki/`** is the **compiled output** — LLM-owned, fully
  regenerable by re-ingesting, organised by `type` for queryability.
- **`AGENTS.md` + `_system/densa/`** is the **compiler** — the
  schema that turns raw into wiki, with mechanical checks to keep
  the build reproducible.

When you ask "can I trust this wiki claim?", the answer is "follow
the wikilink chain to a `raw/` file and read the source." That
chain is finite (≤2 hops per [L1 §"Red lines"](../../AGENTS.md#6-red-lines-non-negotiable))
and machine-checkable
(AGENTS006 + lint's citation-depth pass).
