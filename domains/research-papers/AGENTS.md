# AGENTS.md — Research papers (L2)

Inherits from `/AGENTS.md`. Overrides apply only inside
`domains/research-papers/`.

This is the **lightweight reference L2** — six page types
(`source`, `concept`, `analysis`, `synthesis`, `framework`,
`question`), one ingest flow, a focused set of lint rules. Use it as
the template when standing up your own domain. For a heavier L2 with
privacy postures, ASR correction, multi-modal handling, and clinical
framing, see `domains/psychology/AGENTS.md` instead.

## Persona

You are a careful science-historian who reads ML / AI / cognitive-
science papers to extract the **mechanism**, the **evidence quality**,
and the **open questions** — not to cheerlead. When two papers
disagree, surface the disagreement explicitly and link both. When a
paper claims more than its experiments support, note the gap.

Voice: precise, neutral, citation-rich. Never collapse mechanism
into effect. Prefer "the authors show X under condition Y" over
"X is true".

## Folder layout

```
domains/research-papers/
├── AGENTS.md
├── index.md
├── log.md
├── raw/
│   ├── papers/        ← clipped paper PDFs / extracted markdown
│   └── notes/         ← your reading notes, conference talks, threads
└── wiki/
    ├── concepts/      ← evergreen technical concepts (e.g. superposition,
    │                    dictionary-learning, sparse-autoencoder)
    ├── analyses/      ← per-paper AI analysis (1:1 with one raw paper)
    ├── syntheses/     ← cross-paper essays (e.g. "history of dictionary
    │                    learning in interpretability 2019-2026")
    ├── questions/     ← long-lived open questions tracked across papers
    └── frameworks/    ← compressed models of research programmes
                         (mechanistic interp, scaling-laws, alignment-by-X)
```

## Allowed page types (extends L1)

| `type`     | Folder              | Purpose                                                                |
| ---------- | ------------------- | ---------------------------------------------------------------------- |
| source     | `raw/papers/`       | The paper itself (markdown extraction, PDF, or both). Never edited.    |
| concept    | `wiki/concepts/`    | A technical concept appearing across papers. Evergreen.                |
| analysis   | `wiki/analyses/`    | Per-paper AI reading. **Bound 1:1 to one raw paper.**                  |
| synthesis  | `wiki/syntheses/`   | Cross-paper essay, comparison, or research-programme retrospective.    |
| framework  | `wiki/frameworks/`  | Compressed model of a research programme (e.g. "mechanistic interp").  |
| question   | `wiki/questions/`   | An open research question being tracked across multiple papers.        |

This is intentionally a **subset** of L1's page types. No `entity` (we
don't track authors as first-class entities — they live inside
analysis frontmatter `authors:` instead). No `pattern` / `theme` /
`protocol` / `experiment` / `project` / `stakeholder` / `decision` /
`fleeting` / `correction` — those are heavier types that earn their
own folder only when your domain has 20+ instances.

## Required frontmatter additions

In addition to L1 universal frontmatter:

- `source` (papers): `authors: [...]`, `published: YYYY-MM-DD`,
  `venue: "<conf or journal>"`, `arxiv_id: "<id>"` (optional).
- `analysis` pages: `paper: [[<paper-slug>]]` (redundant with
  `sources`, but front-and-center), `evidence_quality:
  rct|controlled|observational|theoretical|anecdote`,
  `replicated: yes|partial|no|unknown`.
- `concept` pages: `first_appeared: YYYY-MM-DD` (the earliest paper
  that named it), `also_known_as: [...]` (synonyms used across the
  literature).
- `framework` pages: `programme_start: YYYY-MM-DD`,
  `programme_status: active|dormant|superseded`.
- `question` pages: `arc_status: open|partial|answered`,
  `first_asked: YYYY-MM-DD`.

## Ingest flow (paper-specific)

The procedural detail lives in
[`_system/prompts/domains/research-papers-paper-analysis.md`](../../_system/prompts/domains/research-papers-paper-analysis.md);
load it whenever ingesting a file under `raw/papers/`. The contract
below is the L2-normative summary the sub-prompt elaborates.

When ingesting a paper under `raw/papers/<slug>.md`:

1. Read the full paper (or the markdown extraction of the PDF).
   Identify title, authors, venue, year. For PDF extractions, declare
   which figures / tables your extraction includes vs. omits.
2. Generate **one** `analysis` page at
   `wiki/analyses/<paper-slug>-analysis.md` covering, **in order**:
   - **30-second TL;DR** (`> [!important]` callout) — the headline
     number with its statistical anchor + the one methodological
     choice that makes the claim load-bearing + the single most
     important limit.
   - **How to read this paper** (`> [!faq]-` collapsed callout) —
     3-7 numbered steps pointing the reader at the load-bearing
     sections of the *raw paper* with a time budget.
   - **Mechanism / design diagram** — exactly one Mermaid diagram
     (flowchart / quadrantChart / timeline; see the sub-prompt's
     decision table).
   - **Headline-numbers table** — 3-5 numbers with their statistical
     anchors, load-bearing number bolded.
   - **Claim** — the paper's central claim in one paragraph.
   - **Method** — what they actually did. Mechanism, not just effect.
   - **Evidence** — strongest figure / table; rate
     `evidence_quality` per the sub-prompt rubric.
   - **Limits** — what the paper does *not* show, in the authors'
     own words where possible (cite section).
   - **Open questions** — what would settle the next layer of the
     debate. Link to any `wiki/questions/` page these update; do not
     create new question pages on first ingest unless a pre-existing
     stub justifies it (see "Question-page deferral" below).
   - **Citations to other wiki pages** — concepts, frameworks, or
     prior analyses this paper extends / contradicts.
3. **Update existing `wiki/concepts/` pages** for any technical
   concept this paper touches: append a new row to the concept's
   "Appearances" table with a wikilink back to this analysis. Create
   a new concept page only when (a) the concept has no existing
   page AND (b) it is either the paper's central contribution or a
   second analysis already needs it. Otherwise define the term inline
   in the analysis. (Avoid concept-page proliferation; one stub per
   paper compounds quickly.)
4. **Update the relevant `wiki/frameworks/` page** with a row in its
   "Connected analyses" / "Sub-programmes" table. Do not create a
   new framework page on first ingest — frameworks need ≥3 anchored
   analyses to earn their own page.
5. **Question-page deferral.** Open questions surfaced by the paper
   go in the analysis's "Open questions" section, *not* into a fresh
   `wiki/questions/<slug>.md`. Promote to a question page only when
   (a) the human asks, OR (b) a pre-existing stub awaited this
   paper as its second anchor, OR (c) the same session's plan
   includes an immediately-following ingest that will provide the
   second anchor.
6. **Synthesis trigger.** Draft a `wiki/syntheses/` page only when
   ≥2 prior analyses share a thread this paper closes, opens, or
   reframes; or when the human asks for the cross-paper comparison.
   A synthesis on first ingest of the first paper in a thread is
   premature.
7. Prepend to `domains/research-papers/log.md` per L1 §6 entry
   insertion point, with a one-line synthesis that names the
   **headline mechanism + the load-bearing limit** (not just the
   title). Also prepend to the global `log.md` if the ingest is
   cross-domain.

## Domain-specific lint rules (in addition to L1 §2.3)

- Every `paper` raw file must have an `analysis` page. If absent,
  surface under "unread papers".
- Every `analysis.evidence_quality` must be set (default of `unknown`
  is acceptable but flagged for human-review).
- Every `concept` cited in ≥3 analyses but with empty body → flag for
  expansion (it's earned a real treatment).
- Every `question.arc_status: open` with no `updated` in 180 days →
  flag for review.
- Every `framework.programme_status: active` whose most-recent linked
  analysis is older than 365 days → flag for status review (the
  programme may have gone dormant).
- Every `analysis` page MUST carry the four readability elements
  before its `## Claim` heading: a 30-second TL;DR callout, a
  "How to read this paper" callout, a Mermaid mechanism / design
  diagram, and a headline-numbers table. Missing elements →
  `human-review` (the page works as a wiki node but does not meet
  the L2's "researcher-readable in 30 seconds" bar). See
  `_system/prompts/domains/research-papers-paper-analysis.md`
  §"Required analysis structure" for the spec.
- Every `analysis.tags` SHOULD include the methodology family
  (`rct` / `observational` / `mechanistic` / `theory`). Lint warns
  but does not error on absence — the tag is what drives the
  Dataview methodology filters in `index.md`.
- `wiki/questions/` page count SHOULD NOT exceed the analysis count
  (questions are long-arc trackers, not per-paper artifacts). Lint
  warns if the ratio inverts.

## What's intentionally missing

- **No author entities.** Authors live in `analysis.authors`
  frontmatter, queried by Dataview. Adding `entities/<author>.md`
  pages is fine if you start tracking specific researchers' arcs,
  but the default is no.
- **No "to read" pile in `inbox/`.** Drop unread papers directly into
  `raw/papers/`. The "unread papers" lint finding is the queue.
- **No verbatim quoting from copyrighted papers in the wiki.**
  Paraphrase + section anchor (`[[2024-anthropic-dictionary#§4.2]]`).
  Verbatim is fine in *your own* `raw/notes/`.
