# Sub-prompt: projects client call / meeting analysis (v1)

Used by [`_system/prompts/ingest.md`](../ingest.md) whenever a new file
under `domains/projects/raw/meetings/` (or another projects raw bucket
the L2 routes here) is being processed — client calls, internal syncs,
maintenance/status docs for client-facing project work.

> **This prompt is a deliberate derivation of
> [`workspace-meeting-analysis.md`](workspace-meeting-analysis.md).**
> Load BOTH files at ingest time: everything not restated below —
> the two-pass pipeline, the four readability elements, the six
> required body sections, the Mermaid robustness rules, decision-page
> creation, pattern detection, question-page deferral, the synthesis
> trigger, and the quality bar — **inherits verbatim** from the
> workspace prompt. This file carries only the client-projects deltas.
> (Referenced, not forked: when the workspace prompt improves, this
> domain inherits the improvement for free.)

> Authority: this prompt is procedural; the schema is in
> [`/AGENTS.md`](../../../AGENTS.md) (L1) and
> `domains/projects/AGENTS.md` (L2). When this prompt and AGENTS
> disagree, AGENTS wins.

The workspace prompt's failure mode (decision-rationale loss) applies
here too, but a client-facing solo/small operator has a sharper one:
**commitment loss** — telling a client "we'll have it by Friday" on a
call and having no system that remembers. Delta 3 below exists for
that.

---

## Delta 1 — Routing: filename → client slug + project slug

| Raw filename pattern | raw kind |
| --- | --- |
| `<YYYY-MM-DD>(-<HHMM>)?-<client-slug>-<topic>.md` (a call with the client on it) | `client call` |
| `<YYYY-MM-DD>(-<HHMM>)?-<topic-slug>.md` (no client present) | `internal sync` |
| `<topic-or-project-slug>.md` (undated; a living status/maintenance doc snapshot) | `maintenance doc` |

Resolve the **client slug** and the **project slug** before drafting
(one client can have several projects); both become tags and the
project page gets the Sessions row. Exact slug tables live in the L2.
If the raw kind is ambiguous (a doc that quotes a call), ask once.

## Delta 2 — At-a-glance table gains a `Commercial frame` row

Insert into the inherited at-a-glance decision table, directly after
the **Working subject** row:

| Field | Content |
| --- | --- |
| **Commercial frame** | scope / money / deadline — what of the three moved or was touched this raw; "untouched" is a valid and useful value |

Scope creep, price talk, and deadline movement are the three levers a
client conversation can silently pull; this row forces the check every
ingest.

## Delta 3 — New REQUIRED body section: `## Commitments made to the client`

Inserted between the inherited `## Decisions taken / deferred` and
`## Action items`. **For a solo operator this is the highest-risk
field — above even residual-risks.** One bullet per commitment that
crossed your lips (or keyboard) toward the client:

- the commitment, concrete enough that a reader knows what "done"
  looks like — **owner** — **date** (or "no date given — flag, and
  close the date on the next touchpoint")
- anchored to the raw locator where it was made

Rules:

- A commitment the client *believes* was made (their summary, their
  recap email quoted in the raw) is recorded here too, marked
  `[client-perceived]` — perception gaps are exactly what this
  section exists to surface.
- Internal action items that don't face the client stay in
  `## Action items`; this section is client-facing promises only.
- Empty is allowed but explicit: `None made this raw.`

## Delta 4 — Person-page ownership: humans live in the people domain

When the vault has a people/relationship domain, **stakeholder humans
get NO entity pages in projects**: client contacts and collaborators
live in the people domain's `wiki/entities/`, and projects pages
**wikilink to them — never duplicate**. The inherited cross-team
entity bookkeeping is satisfied by linking. Pages that DO live here:
project entities, decision entities, org/company entities when the L2
defines them. (Vaults without a people domain fall back to the
inherited workspace stakeholder-page rules.)

## Delta 5 — Maintenance-doc variant: table-only opening

When the raw kind is `maintenance doc` (status snapshots, runbooks,
living project docs — no room, no dialogue):

- Human layer = the **at-a-glance table only** (with the Commercial
  frame row). No 30-second TL;DR callout, no Mermaid, no
  cast-and-stake.
- Inherited body sections shrink to what applies: Context /
  Key claims / Decisions (if the doc records any) /
  Commitments made to the client (often the whole point of a status
  doc) / Cross-references.
- A maintenance doc that turns out to contain a decision with a
  trade-off is really a `decision` raw mislabelled — re-route before
  drafting.

---

## Everything else: inherited

Pipeline, the four readability elements and their voice rules, the six
body sections, quote discipline, Mermaid rules, decision-page
creation criteria, pattern N=2 rules, question-page deferral,
synthesis trigger, quality bar — all per
[`workspace-meeting-analysis.md`](workspace-meeting-analysis.md),
with three mechanical substitutions:

- `domains/workspace/` → `domains/projects/`
- summary filenames per the L2 (`<raw-stem>-summary.md` under
  `wiki/summaries/`)
- quality-bar addition: **(2b)** the Commercial frame row is present,
  **(5b)** `## Commitments made to the client` is present (possibly
  explicitly empty) and every dated commitment has an owner —
  a commitment with no date is flagged in the at-a-glance
  residual-risks row, same logic as the inherited deferral rule.
