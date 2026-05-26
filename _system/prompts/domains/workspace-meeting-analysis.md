# Sub-prompt: workspace meeting / decision analysis (v1)

Used by [`_system/prompts/ingest.md`](../ingest.md) whenever a new file under
`domains/workspace/raw/meetings/`, `domains/workspace/raw/decisions/`, or
`domains/workspace/raw/threads/` is being processed. Produces **exactly one**
`analysis` page per raw, plus the entity / project / decision / pattern /
synthesis side-effects mandated by the L2 ingest flow.

> Authority: this prompt is procedural; the schema is in
> [`/AGENTS.md`](../../../AGENTS.md) (L1) and
> [`domains/workspace/AGENTS.md`](../../../domains/workspace/AGENTS.md) (L2).
> When this prompt and AGENTS disagree, AGENTS wins.

This sub-prompt encodes the *concrete shape* every meeting / decision
analysis MUST take in this L2. It sits between the lighter
[`research-papers-paper-analysis.md`](research-papers-paper-analysis.md)
(single-source, single-arc, mechanism-focused) and the heavier
[`psychology-session-analysis.md`](psychology-session-analysis.md)
(three-stage, privacy-bounded, multi-lens). Workspace's failure mode is
distinct: the risk is **decision-rationale loss** — a wiki that records
*what* was decided but loses *why*, *what was traded off*, and *what was
deferred without an owner*.

The Q2-platform-migration arc (`2026-04-08` planning → `2026-04-22` ADR →
`2026-05-06` postmortem) demonstrated this failure mode concretely: a
well-written ADR named a residual risk, deferred its mitigation, and the
mitigation gap landed as the exact incident the stakeholder had warned
about. This prompt's job is to make sure ingest captures that kind of
multi-meeting causal chain even when no individual raw is dramatic.

---

## When invoked

A user dropped a new `<slug>.md` (or auto-transcribed file) into
`domains/workspace/raw/{meetings,decisions,threads}/`, or said
`ingest <path>` against such a file. Confirm the raw is a primary source
(meeting transcript, ADR, decision doc, async thread export) and not a
secondary summary before drafting. If the raw is a summary somebody else
wrote of a meeting you do not have the transcript for, file it under
`raw/threads/` and analyse it as a thread, not a meeting — the
provenance is one hop further from the room.

## Two-pass pipeline

Meeting ingest runs two passes in the **same LLM context**:

```
Pass 1   Plan & extract — read raw, draft frontmatter + the four
                          readability elements + the six required body
                          sections. NOT WRITTEN TO DISK.
Pass 2   Apply          — write the analysis + entity / project /
                          decision / pattern side-effects + (when
                          warranted) a synthesis + log entries.
```

A self-critique pass is unnecessary for typical meeting raws — the
participants and decisions are named in the raw and cross-checkable.
Spend the budget on **causal-chain extraction** instead (which earlier
raw does this one continue, which later raw does it forecast).

### Pass 1 — Plan & extract

1. **Read the full source.** Identify date, meeting type, attendees, and
   the **working subject** — what is the meeting / doc / thread *about*
   at the project level. For auto-transcribed files, state explicitly
   which speakers you have confidence in identifying vs which are
   `说话人 N` / `Speaker N` style placeholders.
2. **Load conditional context** (token budget):
   - Always: this sub-prompt + L1 + L2 + the snapshot at
     `outputs/snapshots/index-snapshot.md`.
   - Conditional: read the frontmatter (and only relevant section
     bodies) of any `wiki/{entities,projects,decisions,patterns,questions}/<slug>.md`
     the meeting plausibly touches. Use the slug index from the
     snapshot to find them; do not enumerate the folder by `ls`.
   - Just-in-time: prior analyses for the same project (when the
     meeting is the 2nd+ in an arc).
   - Target ≤30K tokens before drafting. Meeting raws are usually
     smaller than therapy transcripts but larger than papers; the
     conditional wiki context dominates the budget.
3. **Draft frontmatter** per L2 §"Required frontmatter additions":
   - `raw_type: meeting | decision | thread`
   - `meeting_date: YYYY-MM-DD` (when `raw_type: meeting`)
   - `sources: ["[[<raw-slug>]]"]` — exactly one element, per
     [`sources-cardinality.md`](../../../docs/reference/sources-cardinality.md)
   - `tags:` — include the dominant project slug, the meeting type
     (`planning`, `postmortem`, `sync`, `review`, `decision-doc`), and
     any cross-cutting topical tag (`api-design`, `sla-exposure`,
     `vendor-selection`, ...).
4. **Draft the four required readability elements** (see §"Required
   analysis structure" below). These four are non-optional in this L2 —
   every meeting analysis carries them, in this order, at the top of
   the file. They are what makes a teammate landing on this page able
   to decide in **30 seconds** whether to read further.
5. **Draft the six required body sections**: Context / Key claims /
   Tensions surfaced / Decisions (taken + deferred — see §"`##
   Decisions taken` / `## Decisions deferred`") / Action items /
   Cross-references. These mirror L2 §"Ingest flow" step 5. An
   optional `## Notes` section may follow Cross-references when the
   analysis surfaces a pattern-promotion observation worth recording
   (see existing worked examples).
6. **Plan side-effects.** Output a short plan before writing:
   ```
   Plan:
   - create: [[<raw-slug>-analysis]]
   - update: [[stakeholder-<name>]] — Appearances row + (optional) Concerns raised
   - update: [[team-<slug>]] — Appearances row
   - update: [[<project-slug>]] — Sessions row + (optional) status change
   - create: [[<decision-slug>]]   ← only if a new canonical decision crystallises
   - update: [[<pattern-slug>]] — append instance (when this raw is the 2nd+ instance)
   - create: [[<new-pattern>]]     ← only when ≥2 instances are now citable
   - defer/create: [[<question>]]  ← see "Question-page deferral" below
   - create: [[<synthesis>]]       ← only when the synthesis trigger fires (§"Synthesis trigger")
   - update: [[index]]              ← only if a new wiki page was created
   - prepend: domains/workspace/log.md
   - prepend: log.md (global, only if cross-domain)
   ```
   Wait for the human's go-ahead unless they pre-approved a batch.

### Pass 2 — Apply

1. Write the analysis file to
   `domains/workspace/wiki/analyses/<raw-stem>-analysis.md`.
2. Update / create each side-effect page in the plan. For entity and
   project pages, **append** to the Appearances / Sessions tables;
   never overwrite. For pattern pages, **append** to the Instances
   table and bump `instances_count`.
3. Update `domains/workspace/index.md` **only** if a new wiki page was
   created (Dataview blocks pick up updated frontmatter automatically).
4. Prepend to `domains/workspace/log.md` per
   [AGENTS.md §"Red lines"](../../../AGENTS.md#6-red-lines-non-negotiable) entry insertion
   point (immediately after preamble separator):
   ```
   ## [YYYY-MM-DD] ingest | <one-line meeting title>
   - Source: [[<raw-slug>]]
   - Pages touched: [[<analysis>]], [[<entity-A>]], ...
   - One-line synthesis — the decision the meeting produced + the load-bearing trade-off.
   ```
5. If this ingest's plan declared `cross-domain` in step 6.5 of the
   parent ingest prompt (rare for workspace; typical when a meeting
   touches material that crosses into `psychology` or `self-optim`),
   also prepend to the global `log.md`.

---

## Required analysis structure (the four readability elements)

Every meeting / decision / thread analysis in this L2 opens with these
four blocks before the `## Context` section. They are what makes a
teammate (or onboarding intern) able to decide in **30 seconds**
whether they need to read further or already know enough.

### 1. 30-second TL;DR — `> [!important]` callout

3-5 sentences. State:
- The **decision the meeting produced** (or did not produce —
  "deferred to <next raw>" is a valid TL;DR).
- The **load-bearing trade-off** — the one constraint or value the
  decision had to weigh.
- The **single most important deferral** — what was acknowledged but
  not committed; this is the field most likely to bite later.

**Voice rule.** Match the L2 chief-of-staff persona: precise, neutral,
narrative when needed; never cheerleading. Prefer "the team committed
to phased rollout after CS raised SLA concerns" over "the team made
the right call". A reader who only reads this callout should walk away
with the same understanding you hold after reading the full transcript
— no inflation, no hedge inflation.

### 2. At-a-glance decision table

A markdown table with these columns (skip rows that don't apply):

| Field | Content |
| --- | --- |
| **Working subject** | one-line — what is this meeting about at the project level |
| **Meeting type** | planning / decision-doc / review / postmortem / sync / other |
| **Attendees** | comma-separated wikilinks `[[stakeholder-…]]` |
| **Decision produced** | one-line, or "deferred to YYYY-MM-DD" |
| **Reversibility** | reversible / partial / irreversible (skip when no decision was produced) |
| **Load-bearing constraint** | the one constraint that drove the trade-off |
| **Residual risks accepted** | bullets — what was acknowledged but not mitigated |
| **Owners assigned** | bullets — `[[stakeholder]]` → action, with due date if named |

The "Residual risks accepted" row is the single highest-leverage field
in this table. If the raw acknowledges a risk that has no owner and no
date in the action items, surface it here explicitly. The Q2
postmortem exists precisely because this field was implicit, not
explicit, in the 2026-04-22 ADR.

### 3. Cross-meeting causal-chain diagram — Mermaid

Exactly one Mermaid diagram showing **where this raw sits in its arc**.
Pick the diagram type from this decision table:

| Meeting kind | Diagram type | What it shows |
| --- | --- | --- |
| Planning meeting (1st in an arc) | `flowchart LR` | Constraints in → proposal out → next-raw target date |
| Decision doc / ADR | `flowchart LR` with `Constraints` and `Trade-offs` subgraphs | Inputs from prior raws → decision crystallised → phases / gates out |
| Postmortem | `timeline` | Planning raw → Decision raw → Incident → Postmortem; mark the load-bearing risk's progression |
| Review meeting | `flowchart TD` | Prior decision → review evidence → adjusted decision |
| Sync / standalone | (omit) | A truly standalone sync doesn't need a diagram; one-off syncs are usually low-information per L2 lint anyway |

**Mermaid robustness rules** (bake these in to avoid validator
failures):

- Use `<br/>` (not `\n`) for line breaks inside node labels.
- Quote node labels containing spaces or punctuation:
  `A["Planning meeting<br/>(constraints set)"]`.
- For `timeline` diagrams, dates as the section header and one-line
  events as items: `2026-04-08 : Planning : CS raises silent-drop risk`.
- Avoid colons inside `quadrantChart` point labels.

The diagram's purpose is **arc legibility for the intern** — a reader
new to the project should see how this meeting connects to neighbours
without first reading prose. Do NOT add a diagram that merely restates
the at-a-glance table with shapes.

### 4. Cast-and-stake table

A markdown table with one row per stakeholder who spoke
substantively (≥2 turns or one load-bearing claim). Columns:

| Stakeholder | Stake | Position | Outcome |
| --- | --- | --- | --- |
| `[[stakeholder-…]]` | what they own / represent | what they argued for | what the meeting decided relative to their position |

This is the single most useful artifact for an intern trying to
understand **who cares about what**. A 6-month-tenured engineer can
read this table in 20 seconds and know which stakeholder to talk to
about which surface. Skip stakeholders who only attended in listening
mode.

---

## Six required body sections

After the four readability elements, every analysis carries these six
sections in order. Section names are fixed (do not rename them per
ingest — the wiki is grep-able):

### `## Context`

3-6 sentences. What state was the project in entering this raw. What
prior decisions are this meeting's input. Which stakeholders' concerns
came pre-loaded vs surfaced fresh in the room. Link prior analyses
inline.

### `## Key claims`

3-8 bullets. Each bullet:
- Names the stakeholder.
- States their load-bearing claim in their voice (paraphrase, not
  verbatim — but preserve their framing).
- Anchors to a raw locator (timestamp `[10:14]` or paragraph anchor
  `^P12`) when the raw provides one.

Use `> [!quote]` callouts **sparingly** for the most load-bearing 1-2
claims per analysis, with the timestamp as the citation. ≤3 lines per
quote. Do not quote routine procedural turns.

### `## Tensions surfaced`

The disagreements, unresolved trade-offs, and structural concerns the
meeting brought into the open — even when the decision moved past
them. For each tension: who-vs-who, what the resolution was (or "no
resolution; carried to <next raw>"), and which residual risk if any
the tension's resolution implies.

Tensions surfaced are usually the **most predictive** part of the
analysis for what will land in the next raw. Be generous here.

### `## Decisions taken` / `## Decisions deferred`

Either format is acceptable, pick what fits the raw:

- **Single section** `## Decisions taken & deferred` with two `###`
  subsections (use when one bucket is small — e.g. a postmortem with
  many decisions taken but few deferred, or a planning meeting where
  everything is deferred to the ADR).
- **Two sibling H2 sections** `## Decisions taken` and
  `## Decisions deferred` (use when both buckets have body weight; this
  is the style of the existing Q2-arc analyses and is the default).

**Decisions taken** — bullets. Each bullet:
- States the decision concretely (a teammate who didn't attend should
  know exactly what was committed).
- Names the decision's reversibility (`reversible` / `partial` /
  `irreversible`).
- Links the canonical `[[<decision-slug>]]` page when one crystallises;
  see §"Decision-page creation" below for when to create one.

**Decisions deferred** — bullets. Each bullet:
- States the open question.
- Identifies what would be needed to close it (a follow-up meeting?
  data? a process change?).
- Names the target raw / date if scheduled.

> [!important]
> **A deferred decision without an owner and a date is a residual
> risk**, not a deferral. If the raw contains such an item, surface
> it here AND in the at-a-glance "Residual risks accepted" row. The
> Q2-platform-arc lesson is that "filed as follow-up work" is *not*
> equivalent to a deferral with shape.

### `## Action items`

The committed next steps. Each bullet:
- `[[stakeholder-…]]` — concrete action — due `YYYY-MM-DD` (or
  "no date set" — flag this).
- Link to the surface the action delivers on (a project, a decision,
  a question page).

This section is **action items, not aspirations**. An item the room
discussed but did not assign goes under "Decisions deferred", not here.

### `## Cross-references`

A bullet list linking:
- The dominant project page.
- All stakeholder entity pages whose concerns appeared in the meeting.
- The team entity pages whose work is touched.
- Prior analyses in the same arc (when this is the 2nd+ raw).
- The canonical decision page (when applicable).
- Pattern pages this raw extends instances of.
- Question pages this raw bears on.
- The synthesis braiding the arc (when one exists).

The "Cross-references" section is the wiki's **navigation gift to
future readers** — for an intern landing on this analysis cold, this
section is the on-ramp to the rest of the wiki.

---

## Decision-page creation

A canonical `wiki/decisions/<slug>.md` page is **distinct** from both
the raw ADR doc and the analysis-of-ADR. Its job is to be the page
the rest of the wiki cites when referring to "the X decision" without
needing to know which raw the decision originated in.

Create a canonical decision page when **all** of the following hold:

1. The raw is an ADR / decision doc / meeting-with-decision-outcome.
2. The decision is **referenced** (by name or by anchor) from at least
   one other page outside its own analysis — i.e. it's not purely
   internal to one raw.
3. The decision has a stable identifier the team uses in conversation
   ("ADR-001", "the microservices split", "the vector-DB selection").

If only (1) holds but the decision is hyper-local to one meeting and
nobody references it elsewhere, **skip the canonical page**; the
analysis itself is sufficient. Examples of decisions that warrant a
canonical page: ADR-001 microservices split. Examples that don't: a
sprint-internal "we'll change the variable name" agreement recorded
in a sync meeting.

Canonical decision page structure: Context / Decision / Rationale /
Stakeholders / Status. Keep it short — the rationale's evidence lives
in the analysis, not here; the canonical page points to the analysis.

---

## Pattern detection (when to create or extend a pattern)

A `wiki/patterns/<slug>.md` page lives at the workspace's
**second-order signal** layer: a recurring failure or success mode
that shows up across ≥2 raws.

Rules for ingest:

1. **Pattern creation requires N=2.** Do not mint a new pattern page
   on first observation. Hold the candidate-pattern observation in
   the analysis's "Notes" section; promote when a second independent
   raw demonstrates the same shape.
2. **Pattern extension is mandatory on N=2+.** If the current raw is
   the 2nd, 3rd, ... instance of an existing pattern, you MUST
   append a row to that pattern's Instances table and bump
   `instances_count`. The L2's lint rule "every
   `pattern.instances_count` must be ≥ the number of `sources:`
   wikilinks" enforces this.
3. **Negative patterns vs positive patterns.** Both are first-class.
   `decision-delay-from-skipped-stakeholder` is a negative pattern.
   `engineering-decision-style` (problem → constraints → options →
   trade-off matrix → decision → exit criteria) is a positive
   pattern. Workspace tracks both; positive patterns are how a team
   sees its own competence shape and reproduces it.
4. **N=1 patterns are flagged provisional.** If a pattern lands at
   `instances_count: 1` (e.g. mid-arc, only one instance currently
   cited), open the body with a `> [!important]` callout naming the
   N=1 status. Lint surfaces N=1 patterns that have not advanced to
   N=2 within 60 days as candidates for either promotion or
   demotion-to-note.

---

## Question-page deferral

Default behaviour: do **not** create new `wiki/questions/` pages on
first ingest. Open questions in the meeting itself go in the
analysis's "Decisions deferred" subsection.

Promote to a question page when:

1. The same open question recurs across ≥2 raws (it has stopped being
   a one-meeting deferral and is becoming an arc-level process
   question). The Q2 arc's `should-we-revisit-cs-veto-power` is the
   worked example.
2. The human explicitly asks for the question to be tracked.
3. An existing question page already lists this thread — append a row
   to its "Evidence so far" table.

Question pages are long-lived; the lint rule for `arc_status: open`
without recent citation (>90 days) catches stagnation.

---

## Synthesis trigger

`wiki/syntheses/<slug>.md` is reserved for **deliberate cross-raw
narrative** — not for every ingest. Trigger a synthesis when:

1. The current raw, together with ≥1 prior raw in the same arc,
   closes a multi-week narrative loop (planning → decision →
   outcome). The Q2 arc's `q2-platform-arc-may` is the worked
   example.
2. ≥3 decisions across different projects exhibit the same shape and
   teaching them as a set has higher leverage than teaching each
   separately. The `engineering-decisions-retrospective-may-2026`
   synthesis is the worked example.
3. The human asks for a comparison or retrospective.

Synthesis structure follows the same TL;DR-first principle as
analysis. The TL;DR names the thread; the body braids the raws with
inline wikilinks rather than re-summarising them. A synthesis that
re-states each raw's analysis is a **synthesis defect** — the
analyses are not duplicated, they are *referenced*.

---

## Cross-team meetings — entity bookkeeping

When a meeting attendees list spans ≥2 teams (e.g. Platform +
Customer Success + Product), the ingest MUST:

1. Ensure each team has its own `team-<slug>.md` page.
2. Ensure each speaking stakeholder has their own
   `stakeholder-<slug>.md` page.
3. In each stakeholder page, the "Appearances" table row for this raw
   names the cross-team context ("attended Platform planning;
   represented CS contractual exposure").
4. In each team page, the "Cross-stakeholder interfaces" section
   notes which other teams' representatives this meeting put the team
   in contact with.

This is the single most useful bookkeeping for the intern's question
"who works with whom on what". Underdoing it produces a wiki where
the org chart is implicit and unreadable.

---

## Stakeholder appearance restraint

A stakeholder earns a full `stakeholder-<slug>.md` page when **either**:

- They are a **named reviewer** on a decision doc.
- They have spoken substantively (≥2 turns or one load-bearing claim)
  in ≥1 raw.
- They are explicitly named in a pattern's instances (under-empowered,
  load-bearing-concern-raiser, etc.).

Until they earn the page, store their participation under the team
page's Members table with raw-link appearances. Promote to a full
stakeholder page when the criterion above is met; backfill the
wikilink in prior analyses.

The `team-platform.md` page demonstrates this restraint with Devon
Park (Product) and Maya Chen (Platform lead) as plain-text members
who appear in multiple raws but are not yet the *working subject* of
a pattern or synthesis — and Alex Rivera (`stakeholder-alex-cs`) as
the contrast: the load-bearing reviewer who earns the dedicated page
because his behaviour *is* the working subject of the
`decision-delay-from-skipped-stakeholder` pattern.

---

## Quality bar (final pass before commit)

A correct workspace ingest produces:

1. **Exactly one** `analysis` file per raw, named
   `<raw-stem>-analysis.md`, with `sources: ["[[<raw-slug>]]"]` of
   length 1 (sources-cardinality.md hard constraint).
2. The **four readability elements** (TL;DR + at-a-glance table +
   Mermaid + cast-and-stake table) are present, in order, before
   `## Context`.
3. The **six body sections** are present, in order: Context / Key
   claims / Tensions surfaced / Decisions (one H2 `## Decisions taken
   & deferred` with two subsections, OR two sibling H2s `## Decisions
   taken` and `## Decisions deferred`) / Action items /
   Cross-references. An optional `## Notes` section may follow
   Cross-references for pattern-promotion observations.
4. **Every stakeholder named in the cast-and-stake table has been
   updated in their own wiki page** (Appearances row + Concerns
   raised entry when applicable). Stakeholders below the appearance
   threshold are noted in the relevant `team-*.md` page's Members
   table instead.
5. **Every team named** has been updated similarly.
6. **The project page is updated** with a new row in the Sessions /
   raws table.
7. **Pattern pages are extended** when the raw is the 2nd+ instance.
   `instances_count` is bumped; the new row in Instances table cites
   the new raw + analysis.
8. A canonical decision page is created **only** when the
   §"Decision-page creation" criteria are met.
9. `wiki/questions/` is not touched on first ingest unless an existing
   stub justifies it; deferrals live in the analysis's "Decisions
   deferred" subsection.
10. A synthesis is created **only** when the §"Synthesis trigger"
    criteria are met.
11. `index.md` is refreshed only if a new wiki page was created.
12. `log.md` prepended per
    [AGENTS.md §"Red lines"](../../../AGENTS.md#6-red-lines-non-negotiable)
    with a one-line synthesis that names
    the **decision produced + the load-bearing trade-off**, not just
    the title.
13. No verbatim quoting >3 lines from the raw transcript in any wiki
    page; paraphrase + timestamp / paragraph anchor instead, except
    for sparing `> [!quote]` callouts on the 1-2 most load-bearing
    claims per analysis.

If any of (1)-(13) is missing, the ingest is incomplete — do not
output a "done" message.

---

## Worked examples to study

When in doubt about depth or voice, open one of these analyses and
copy the structural shape:

- [[2026-04-08-meeting-q2-planning-analysis]] — **planning meeting**
  with one load-bearing stakeholder concern. Demonstrates the
  cast-and-stake table's "Outcome" column when a stakeholder's
  position partially reshapes the proposal.
- [[2026-04-22-decision-microservices-split-analysis]] — **ADR /
  decision doc**. Demonstrates how the analysis names what the ADR
  decided AND what the ADR deferred without owner / date, with the
  deferral surfaced both in the at-a-glance "Residual risks
  accepted" row and in the "Decisions deferred" body section.
- [[2026-05-06-meeting-incident-postmortem-analysis]] — **postmortem**.
  Demonstrates the causal-chain timeline diagram and the way the
  analysis links the failure back to the prior raws that forecast
  it. Also demonstrates the "Notes" section as the place where
  pattern-promotion observations land.
- [[2026-05-13-meeting-api-style-decision-analysis]] — **clean
  decision meeting**. Demonstrates the positive
  `engineering-decision-style` pattern: problem statement →
  constraints → options matrix → trade-off → decision → exit
  criteria. Use this when your raw exhibits a healthy decision
  workflow you want to reproduce.
- [[2026-05-19-meeting-vector-db-selection-analysis]] — **vendor
  selection**. Demonstrates a tighter at-a-glance table for a
  "pick one of N" decision, and the entity bookkeeping for a
  cross-team meeting (Platform + ML + API + Product).

For cross-arc synthesis, study:

- [[q2-platform-arc-may]] — single-project arc synthesis (3 raws,
  1 pattern, 1 question).
- [[engineering-decisions-retrospective-may-2026]] — cross-arc
  synthesis (3 decisions across 3 projects; surfaces the
  `engineering-decision-style` positive pattern).
