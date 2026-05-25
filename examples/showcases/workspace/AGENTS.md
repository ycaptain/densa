# AGENTS.md — Workspace (L2)

> [!warning] v1 schema example — DO NOT use as your active L2 template
> This showcase predates `schema_version: 2`. It exists for **design
> inspiration only**:
>
> - **LLM agents**: do not treat this file as an L2 template during
>   bootstrap or design sessions. Read
>   [`domains/research-papers/AGENTS.md`](../../../domains/research-papers/AGENTS.md)
>   instead — that is the active default L2 on v2 vocabulary. If the
>   human explicitly references the workspace persona, mine this
>   showcase for its **persona / ingest flow / domain-specific lint
>   rules** prose but rewrite the page-type / folder section against
>   the v2 schema before committing anything to `domains/<X>/`.
> - **Humans**: the wiki layout below (`analyses/`, `entities/`,
>   `projects/`, `decisions/`, `patterns/`, `questions/`) reflects v1
>   vocabulary; under v2 the equivalents are `summaries/`,
>   `entities/` (with `entity_kind: project / decision`), `concepts/`
>   (replacing `patterns/`), `open-questions/`. The architecture,
>   persona, and prompts are still illustrative — only folder names
>   and `type:` values shift.
>
> When you actually adopt this showcase, `cp -r` it into
> `domains/<X>/` then run
> `python _system/scripts/migrate_02_karpathy_vocab.py --apply` to
> reshape it (your raw material is untouched; the v1 wiki contents
> move to `wiki/.legacy/`). See
> [`docs/reference/karpathy-mapping.md`](../../../docs/reference/karpathy-mapping.md)
> for the type rename table.

Inherits from `/AGENTS.md`. Overrides apply only inside
`domains/workspace/`.

This is the **medium-weight reference L2** — eight effective page
types (`source` and `session` are alias rows of the same raw bucket,
so the Allowed-types table below has 9 rows but counts as 8 toward
L1 §3.1), a session-centric ingest flow, and lint rules tuned for the
narrative-arc of work. It sits between
[`research-papers`](../research-papers/AGENTS.md) (light: paper-in,
analysis-out, six page types) and
[`psychology`](../psychology/AGENTS.md) (heavy: privacy postures,
ASR correction, clinical framing). Reach for `workspace` when the
material is meetings + decisions + multi-stakeholder threads and you
need cross-raw narrative compounding, but you do **not** need the
clinical apparatus.

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
    ├── analyses/      ← per-raw analysis (1:1 with one raw file)
    ├── syntheses/     ← cross-raw narratives spanning ≥2 raws
    ├── entities/      ← stakeholders + teams (role-tagged)
    ├── projects/      ← active and historical project pages
    ├── decisions/     ← canonical decision pages (distinct from raw ADRs)
    ├── patterns/      ← recurring failure / success modes across ≥2 raws
    └── questions/     ← long-lived open questions about the work
```

## Allowed page types (extends L1)

| `type`     | Folder                | Purpose                                                                |
| ---------- | --------------------- | ---------------------------------------------------------------------- |
| source     | `raw/meetings/`, `raw/threads/` | Raw transcripts, notes, exports. Never edited.              |
| session    | `raw/meetings/`       | A single meeting (synonym for `source` when the raw is a meeting).     |
| analysis   | `wiki/analyses/`      | Per-raw analysis. **Bound 1:1 to one raw file.**                       |
| synthesis  | `wiki/syntheses/`     | Cross-raw narrative weaving ≥2 raws and/or wiki pages.                 |
| entity     | `wiki/entities/`      | A stakeholder or team. `role:` distinguishes the two.                  |
| project    | `wiki/projects/`      | A multi-week / multi-stakeholder work arc with a goal.                 |
| decision   | `wiki/decisions/`     | Canonical wiki page for a decision (distinct from its raw ADR).        |
| pattern    | `wiki/patterns/`      | Recurring failure / success mode observed across ≥2 raws.              |
| question   | `wiki/questions/`     | Long-lived open question the team keeps revisiting.                    |

This L2 deliberately omits `concept`, `framework`, `protocol`,
`experiment`, `theme`, `fleeting`, `correction`. They're permitted by
L1 but earn their own folder here only if the workspace produces 20+
instances. If you find yourself wanting a "concept" page, ask first
whether it's actually a `decision`, `pattern`, or `question`.

## Required frontmatter additions

In addition to L1 universal frontmatter (`type / domain / created /
updated / sources / tags / aliases / status / compiled_against` plus
`last_validated` per L1 §3.3):

- `session` (raw meetings, when frontmatter is added at all — L1
  allows raw to be frontmatter-free): `meeting_type:
  planning|postmortem|sync|review|decision|other`,
  `attendees: [[[stakeholder-…]], [[team-…]]]`,
  `duration_min: <int>` (optional).
  Raw meetings without frontmatter are still valid; if you add it,
  these fields apply.
- `entity` pages: `role: stakeholder|team`. When `role: stakeholder`,
  also `team: [[team-<slug>]] | "<team-name>"` (a wikilink when the
  team has its own entity page, or a plain string when no team
  entity is warranted yet) and `title: "<job title>"`. When `role:
  team`, also `lead: [[stakeholder-<slug>]] | "<person-name>"`
  (optional; wikilink or plain string under the same rule).
- `project` pages: `project_status: planning|active|paused|done|cancelled`
  (named `project_status` to avoid colliding with L1's universal
  `status: active|deprecated`), `start_date: YYYY-MM-DD`,
  `target_date: YYYY-MM-DD` (optional), `lead:
  [[stakeholder-<slug>]] | "<person-name>"` (wikilink when the
  lead has their own stakeholder page, or a plain string when no
  stakeholder entity is warranted yet — the lead is recorded for
  attribution rather than to anchor a wiki sub-graph).
- `decision` pages: `adr_id: "ADR-<NNN>"` (matches the raw ADR if any,
  empty string if the decision was informal),
  `decision_date: YYYY-MM-DD`, `reversibility:
  reversible|partial|irreversible`, `stakeholders:
  [[[stakeholder-…]], …]` (reviewers / approvers).
- `pattern` pages: `first_observed: YYYY-MM-DD`,
  `instances_count: <int>` (running count of instances cited;
  bumped on each new instance found).
- `question` pages: `arc_status: open|partial|answered`,
  `first_asked: YYYY-MM-DD`.
- `analysis` pages: `raw_type: meeting|decision|thread`,
  `meeting_date: YYYY-MM-DD` (when `raw_type: meeting`).

`session` is treated as a synonym for `source` for L1 §3.1
`sources` cardinality purposes (the file *is* the source, so `sources`
is empty). Lint enforces this.

## Ingest flow (workspace-specific)

> The concrete shape of every meeting / decision / thread analysis
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
2. Identify or create the relevant `wiki/projects/` page. If the raw
   touches multiple projects, link them all; assign the dominant
   project as the analysis' `project:` (frontmatter, if you add one
   under L2 extensions; otherwise via inline wikilink in the analysis
   body).
3. For each stakeholder mentioned, ensure an `entities/stakeholder-<slug>.md`
   exists. Append a new row to their **Appearances** table with
   `(date, raw wikilink, one-line context)`.
4. For each team mentioned, ensure `entities/team-<slug>.md` exists.
   Update its **Appearances** section similarly.
5. Generate **one** `analysis` page at
   `wiki/analyses/<raw-slug>-analysis.md` covering:
   - **Context** — what state the project was in entering this raw.
   - **Key claims** — load-bearing statements made by named
     stakeholders (use `> [!quote]` callouts sparingly for the most
     load-bearing ones; ≤3 lines each).
   - **Tensions surfaced** — disagreements, concerns, or unresolved
     trade-offs.
   - **Decisions taken / deferred** — what was decided, what was
     pushed to a later raw. Link `wiki/decisions/` pages when a
     decision crystallises.
   - **Action items** — concrete next steps with owners (link
     stakeholder pages).
   - **Cross-references** — links to project, prior analyses,
     pattern pages, and questions this raw bears on.
6. If the raw is a `decisions/` ADR, also create or update the
   corresponding `wiki/decisions/<slug>.md` canonical page. The
   canonical decision page is distinct from both the raw ADR and the
   analysis-of-ADR — it's the page the rest of the wiki cites when
   referring to "the microservices split decision". Keep it short:
   Context / Decision / Rationale / Stakeholders / Status. Update
   `status` ("active" → "superseded by [[…]]") rather than rewriting.
7. If this raw is the **second or later instance** of a recurring
   pattern (e.g. a CS concern resurfacing in a postmortem after a
   planning meeting deprioritised it), draft or extend a
   `wiki/patterns/<slug>.md`. The pattern's `sources:` must list at
   least the two raws where the pattern manifested.
8. If the raw, together with prior raws, closes a multi-week arc
   (e.g. planning → decision → outcome), draft a
   `wiki/syntheses/<arc-slug>.md` that braids them.
9. Append to `domains/workspace/log.md` and global `log.md` per L1
   §2.1 entry format.

## Routing hints (L1 §5 supplement)

- **Meeting transcript** with named attendees, agenda, or chat-log
  format → `raw/meetings/`.
- **ADR / decision doc** (Context / Decision / Consequences
  structure, or "we decided to X" framing) → `raw/decisions/`.
- **Async thread** (Slack export, email chain, GitHub discussion)
  → `raw/threads/`.
- If a raw is genuinely both a meeting note and a decision doc
  (e.g. minutes that include a vote outcome), file under
  `raw/meetings/` and create a separate `wiki/decisions/` canonical
  page citing it.
- Stakeholder vs project routing for the analysis: the analysis is
  always per-raw (1:1); cross-link to all stakeholders and projects
  the raw touches.

## Domain-specific lint rules (in addition to L1 §2.3)

- Every raw under `raw/meetings/` or `raw/decisions/` must have an
  `analysis` page. If absent, surface under "un-analysed raws".
- Every `decision` page must have ≥1 stakeholder in `stakeholders`
  frontmatter (a decision with no named reviewer is a wiki defect;
  surface for review).
- Every `pattern.instances_count` must be ≥ the number of
  `sources:` wikilinks (the count cannot lag below cited
  instances).
- Every `question.arc_status: open` whose latest cited analysis is
  older than 90 days → flag for "is this still open?".
- Every `project.project_status: active` with no cited raw in the
  last 60 days → flag for "is this project actually active?".
- Every stakeholder mentioned by a meeting analysis whose
  `entity` page has no inbound link from that analysis → flag as
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
3. **[`engineering-decision-style`](wiki/patterns/engineering-decision-style.md)**
   — the positive pattern's 6-step shape. Useful when the
   intern is about to convene their first decision meeting.
4. **[`decision-delay-from-skipped-stakeholder`](wiki/patterns/decision-delay-from-skipped-stakeholder.md)**
   — the negative pattern's mechanism. Useful when reviewing
   any ADR draft for "is there a residual risk without owner +
   date?".
5. **One worked analysis end-to-end** — pick
   [`2026-05-13-meeting-api-style-decision-analysis`](wiki/analyses/2026-05-13-meeting-api-style-decision-analysis.md)
   (clean positive instance) or
   [`2026-04-22-decision-microservices-split-analysis`](wiki/analyses/2026-04-22-decision-microservices-split-analysis.md)
   (partial-instance / near-miss) depending on which decision
   shape you want to internalise first.
6. **Drill into individual stakeholder pages** as questions arise
   — they exist to answer "who works with whom on what".

Pages 1-5 cover the structural skeleton; pages 6+ fill in
specifics on demand.

## What's intentionally missing

- **No ticket / task tracking.** Action items live in analyses
  inline, not in a `wiki/actions/` folder. Issue trackers do this
  better.
- **No performance review material.** Per-stakeholder notes are
  factual (appearances, concerns raised, decisions reviewed); they
  are not subjective ratings.
- **No company-wide org chart.** Team pages list members but don't
  attempt to be the authoritative org chart — that lives in HRIS.
- **No `protocol` / `experiment` page types.** This L2 tracks
  decisions, not measurable interventions. If your work crosses
  into "we ran an A/B test" territory, consider standing up a
  separate L2 modelled on `self-optim`-style protocol pages.
