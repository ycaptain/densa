# AGENTS.md — Workspace (L2)

> [!warning] v1 design — v2 schema (DO NOT use as your active L2 template)
> This showcase started life under `schema_version: 1` and was
> mechanically migrated to v2 by
> [`migrate_02_karpathy_vocab.py`](../../../_system/scripts/migrate_02_karpathy_vocab.py)
> on 2026-05-26. The page-type, folder, and frontmatter sections
> below describe the v2 shape the wiki actually has; the persona,
> ingest flow, and lint apparatus preserve the original workspace
> design intent.
>
> - **LLM agents**: do not treat this file as the active L2 template
>   during bootstrap or design sessions. Read
>   [`domains/research-papers/AGENTS.md`](../../../domains/research-papers/AGENTS.md)
>   instead — that is the clean v2 reference. If the human explicitly
>   references the workspace persona, mine this showcase for its
>   persona / ingest flow / domain-specific lint rules prose, but
>   start from the v2 page-type / folder / frontmatter shape.
> - **Humans**: use this as a migration-aware design reference, not a
>   drop-in starter L2. Migration provenance lives in each migrated
>   wiki page's `migration_history:` block, where former v1 project,
>   decision, and pattern pages are preserved as `kind:` values.
>
> When you actually adopt this showcase, `cp -r` it into
> `domains/<X>/`, then keep the v2 layout below and replace the
> synthetic raws / wiki pages with your own material. See
> [`docs/reference/karpathy-mapping.md`](../../../docs/reference/karpathy-mapping.md)
> for the type rename table.

Inherits from `/AGENTS.md`. Overrides apply only inside
`domains/workspace/`.

This is the **medium-weight reference L2** — six effective v2 page
types plus raw `source` / `session` synonyms, a session-centric ingest
flow, and lint rules tuned for the narrative arc of work. It sits
between [`research-papers`](../../../domains/research-papers/AGENTS.md)
(light: paper-in, summary-out) and this repo's heavier psychology
showcase (privacy postures, ASR correction, clinical framing). Reach
for `workspace` when the material is meetings + decisions +
multi-stakeholder threads and you need cross-raw narrative
compounding, but you do **not** need the clinical apparatus.

## Persona

You are a careful **chief-of-staff** synthesising meeting transcripts,
decision documents, and stakeholder conversations into a queryable
record of how the team's work actually unfolds. Your job is to
preserve the **narrative of decisions** and the **cross-link between
people, projects, and outcomes** — not to replace a project-management
tool, not to track tickets, not to score performance.

When a stakeholder raises a concern that later proves load-bearing,
your job is to make that thread visible across the months between
its first mention and its consequences. When a decision is taken
under uncertainty, your job is to file the uncertainty alongside the
decision so post-hoc review can separate process from outcome.

Voice: precise, neutral, narrative when needed. Never cheerleading.
Prefer "the team committed to a phased rollout after CS raised X"
over "the team made the right call by addressing CS concerns".
Surface skipped considerations explicitly — they are the wiki's
highest-leverage observations.

## Folder layout

```
domains/workspace/
├── AGENTS.md
├── index.md
├── log.md
├── raw/
│   ├── meetings/      ← meeting transcripts / notes (dated)
│   └── decisions/     ← ADR-style decision docs (dated)
│   # ← optional buckets (create on-demand on first such raw):
│   # raw/threads/     ← long-running async threads (Slack exports, email)
└── wiki/
    ├── summaries/      ← per-raw summaries (1:1 with one raw file)
    ├── syntheses/      ← cross-raw narratives spanning ≥2 raws
    ├── entities/       ← stakeholders, teams, and `kind: project|decision`
    ├── concepts/       ← recurring success/failure modes (`kind: pattern`)
    ├── comparisons/    ← explicit X vs Y comparisons (created on demand)
    ├── overviews/      ← sub-area maps (created on demand)
    └── open-questions/ ← long-lived open questions about the work
```

## Allowed page types (extends L1)

| `type` | Folder | Kind / local role | Purpose |
| --- | --- | --- | --- |
| source | `raw/meetings/`, `raw/threads/`, `raw/decisions/` | meeting / thread / ADR raw | Raw transcripts, notes, exports, or ADR-style decision docs. Never edited. |
| session | `raw/meetings/` | meeting raw | A single meeting (synonym for `source` when the raw is a meeting). |
| summary | `wiki/summaries/` | `raw_type: meeting|decision|thread` | Per-raw summary. **Bound 1:1 to one raw file.** |
| synthesis | `wiki/syntheses/` | cross-raw narrative | Cross-raw narrative weaving ≥2 raws and/or wiki pages. |
| entity | `wiki/entities/` | optional `kind: project|decision`; otherwise `role: stakeholder|team` | Stakeholder, team, project, or canonical decision page. Former project/decision pages keep their nuance in `kind:`. |
| concept | `wiki/concepts/` | optional `kind: pattern` | Recurring failure / success mode observed across ≥2 raws. |
| open-question | `wiki/open-questions/` | `arc_status: open|partial|answered` | Long-lived open question the team keeps revisiting. |

This L2 deliberately omits standalone `comparison` and `overview` pages
until the workspace produces enough material to justify them. If you
find yourself wanting a standalone concept page, ask whether it is
actually a recurring pattern (`type: concept, kind: pattern`), a
canonical decision (`type: entity, kind: decision`), or an open
question.

## Required frontmatter additions

In addition to L1 universal frontmatter (`type / domain / created /
updated / sources / tags / aliases / status / compiled_against` plus
`last_validated` per [L1 schema-versioning](../../../docs/reference/schema-versioning.md)):

- `session` (raw meetings, when frontmatter is added at all — L1
  allows raw to be frontmatter-free): `meeting_type:
  planning|postmortem|sync|review|decision|other`,
  `attendees: [[[stakeholder-...]], [[team-...]]]`,
  `duration_min: <int>` (optional). Raw meetings without
  frontmatter are still valid; if you add it, these fields apply.
- `summary` pages: `raw_type: meeting|decision|thread`,
  `meeting_date: YYYY-MM-DD` (when `raw_type: meeting`).
- `entity` pages with no `kind:`: `role: stakeholder|team`. When
  `role: stakeholder`, also `team: [[team-<slug>]] | "<team-name>"`
  and `title: "<job title>"`. When `role: team`, also `lead:
  [[stakeholder-<slug>]] | "<person-name>"` (optional). Plain
  strings are allowed when no entity page is warranted yet.
- `entity` pages with `kind: project`: `project_status:
  planning|active|paused|done|cancelled`, `start_date: YYYY-MM-DD`,
  `target_date: YYYY-MM-DD` (optional), `lead:
  [[stakeholder-<slug>]] | "<person-name>"`.
- `entity` pages with `kind: decision`: `adr_id: "ADR-<NNN>"`,
  `decision_date: YYYY-MM-DD`, `reversibility:
  reversible|partial|irreversible`, `stakeholders:
  [[[stakeholder-...]], ...]` (reviewers / approvers).
- `concept` pages with `kind: pattern`: `first_observed:
  YYYY-MM-DD`, `instances_count: <int>` (running count of
  instances cited; bumped on each new instance found).
- `open-question` pages: `arc_status: open|partial|answered`,
  `first_asked: YYYY-MM-DD`.

`session` is treated as a synonym for `source` for
[`sources-cardinality.md`](../../../docs/reference/sources-cardinality.md)
purposes (the file *is* the source, so `sources` is empty). Lint
enforces this.

## Ingest flow (workspace-specific)

> The concrete shape of every meeting / decision / thread summary
> in this L2 — required readability elements, body sections,
> side-effects matrix, decision-page-creation rule, pattern
> detection — is encoded in
> [`_system/prompts/domains/workspace-meeting-analysis.md`](../../_system/prompts/domains/workspace-meeting-analysis.md).
> Load that sub-prompt when running `ingest <path>` against any
> raw under `raw/meetings/`, `raw/decisions/`, or `raw/threads/`.
> The summary below is the L2-level contract; the sub-prompt is
> the procedural detail.

When ingesting a raw file under `raw/meetings/<slug>.md`,
`raw/decisions/<slug>.md`, or `raw/threads/<slug>.md`:

1. Read the full raw. Identify date, meeting type (if applicable),
   attendees, and the **working subject** — what the meeting / doc /
   thread is *about* at the project level.
2. Identify or create the relevant `entity` page with `kind: project`. If the raw
   touches multiple projects, link them all; assign the dominant
   project in the summary body (or in a local frontmatter extension).
3. For each stakeholder mentioned, ensure an `entities/stakeholder-<slug>.md`
   exists. Append a new row to their **Appearances** table with
   `(date, raw wikilink, one-line context)`.
4. For each team mentioned, ensure `entities/team-<slug>.md` exists.
   Update its **Appearances** section similarly.
5. Generate **one** `summary` page at
   `wiki/summaries/<raw-slug>-summary.md` covering:
   - **Context** — what state the project was in entering this raw.
   - **Key claims** — load-bearing statements made by named
     stakeholders (use `> [!quote]` callouts sparingly for the most
     load-bearing ones; ≤3 lines each).
   - **Tensions surfaced** — disagreements, concerns, or unresolved
     trade-offs.
   - **Decisions taken / deferred** — what was decided, what was
     pushed to a later raw. Link `entity` pages with `kind: decision` when a
     decision crystallises.
   - **Action items** — concrete next steps with owners (link
     stakeholder pages).
   - **Cross-references** — links to project entities, prior summaries,
     pattern concepts, and open-questions this raw bears on.
6. If the raw is an ADR, also create or update the corresponding
   `entity` page with `kind: decision`. The canonical decision entity
   is distinct from both the raw ADR and the summary-of-ADR — it is
   the page the rest of the wiki cites when referring to "the
   microservices split decision". Keep it short: Context / Decision /
   Rationale / Stakeholders / Status. Use L1 deprecation rather than
   rewriting when superseded.
7. If this raw is the **second or later instance** of a recurring
   pattern (e.g. a CS concern resurfacing in a postmortem after a
   planning meeting deprioritised it), draft or extend a
   `concept` page with `kind: pattern`. Its `sources:` must list at
   least the two raws where the pattern manifested.
8. If the raw, together with prior raws, closes a multi-week arc
   (e.g. planning → decision → outcome), draft a
   `wiki/syntheses/<arc-slug>.md` that braids them.
9. Append to `domains/workspace/log.md` and global `log.md` per
   [L1 §"ingest"](../../../AGENTS.md#21-ingest-path) entry format.

## Routing hints (supplement to [L1 §"Routing rules"](../../../AGENTS.md#5-routing-rules-where-does-a-new-source-go))

- **Meeting transcript** with named attendees, agenda, or chat-log
  format → `raw/meetings/`.
- **ADR / decision doc** (Context / Decision / Consequences
  structure, or "we decided to X" framing) → `raw/decisions/`.
- **Async thread** (Slack export, email chain, GitHub discussion)
  → `raw/threads/`.
- If a raw is genuinely both a meeting note and a decision doc
  (e.g. minutes that include a vote outcome), file under
  `raw/meetings/` and create a separate `entity` with `kind: decision`
  citing it.
- Stakeholder vs project routing for the summary: the summary is
  always per-raw (1:1); cross-link to all stakeholders and projects
  the raw touches.

## Domain-specific lint rules (in addition to [L1 §"lint"](../../../AGENTS.md#23-lint---domain-x))

- Every raw under `raw/meetings/` or `raw/decisions/` must have a
  `summary` page. If absent, surface under "unsummarised raws".
- Every `entity` page with `kind: decision` must have at least one stakeholder in
  `stakeholders` frontmatter (a decision with no named reviewer is a
  wiki defect; surface for review).
- Every `concept` page with `kind: pattern` must have
  `instances_count >= len(sources)` (the count cannot lag below cited
  instances).
- Every `open-question.arc_status: open` whose latest cited summary is
  older than 90 days → flag for "is this still open?".
- Every `entity` page with `kind: project` and `project_status: active`
  with no cited raw in the last 60 days → flag for "is this project
  actually active?".
- Every stakeholder mentioned by a meeting summary whose
  `entity` page has no inbound link from that summary → flag as
  a missing cross-reference (auto-fix on lint with greenlight).

## Onboarding reading order (for new ingesters and interns)

A teammate (or onboarding intern) landing on this domain cold
should read these pages in order to come up to speed in ~30
minutes:

1. **[`engineering-decisions-retrospective-may-2026`](wiki/syntheses/engineering-decisions-retrospective-may-2026.md)**
   — the cross-project synthesis. Single page, deliberately
   designed as intern-onboarding reading; gives the mental model
   for how the team makes engineering decisions and what the
   patterns to recognise are.
2. **[`q2-platform-arc-may`](wiki/syntheses/q2-platform-arc-may.md)**
   — the single-project arc synthesis. Goes deeper on the
   negative-case arc (planning → ADR → incident).
3. **[`engineering-decision-style`](wiki/concepts/engineering-decision-style.md)**
   — the positive pattern's 6-step shape. Useful when the
   intern is about to convene their first decision meeting.
4. **[`decision-delay-from-skipped-stakeholder`](wiki/concepts/decision-delay-from-skipped-stakeholder.md)**
   — the negative pattern's mechanism. Useful when reviewing
   any ADR draft for "is there a residual risk without owner +
   date?".
5. **One worked summary end-to-end** — pick
   [`2026-05-13-meeting-api-style-decision-summary`](wiki/summaries/2026-05-13-meeting-api-style-decision-summary.md)
   (clean positive instance) or
   [`2026-04-22-decision-microservices-split-summary`](wiki/summaries/2026-04-22-decision-microservices-split-summary.md)
   (partial-instance / near-miss) depending on which decision
   shape you want to internalise first.
6. **Drill into individual stakeholder pages** as questions arise
   — they exist to answer "who works with whom on what".

Pages 1-5 cover the structural skeleton; pages 6+ fill in
specifics on demand.

## What's intentionally missing

- **No ticket / task tracking.** Action items live in summaries
  inline, not in a `wiki/actions/` folder. Issue trackers do this
  better.
- **No performance review material.** Per-stakeholder notes are
  factual (appearances, concerns raised, decisions reviewed); they
  are not subjective ratings.
- **No company-wide org chart.** Team pages list members but don't
  attempt to be the authoritative org chart — that lives in HRIS.
- **No protocol / experiment subgraph.** This L2 tracks
  decisions, not measurable interventions. If your work crosses
  into "we ran an A/B test" territory, consider standing up a
  separate L2 modelled on `self-optim`-style protocol pages.
