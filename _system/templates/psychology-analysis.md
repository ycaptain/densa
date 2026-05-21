---
type: analysis
domain: psychology
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: ["[[<raw-source-wikilink>]]"]
session_kind: therapy
participants: [self, <clinician-slug>]
analysis_lens: []
diagnostic_signals: []
tags: []
status: active
compiled_against: 1
---

# <% tp.file.title %>

<!-- Single-file v3 analysis of exactly ONE raw therapy session.
For psychiatry use _system/templates/psychiatry-analysis.md.
See domains/psychology/AGENTS.md §"Slug recognition rules" for filename → clinician slug mapping. -->

## TL;DR

1-3 sentences. What delta did this session bring to the wiki — which pattern strengthened, which theme advanced, what new structure surfaced.

## Key moments

<!-- 3-6 bullets, each anchored to a timestamp + the entity / pattern / theme / concept it activated. Quote ≤3 lines per anchor. -->

- [HH:MM] short description — touches [[<entity-or-pattern>]]

## Narrative reconstruction

<!-- 400-600 字, first-person experiential. Inline-link [[frameworks/X]] but do NOT expand framework theory here — point readers at the framework page. -->

…

## Working formulation

<!-- 2-4 paragraphs, EACH labelled with the lens it draws on, ≤150 字 each.
Only lenses that THIS session genuinely advances; don't re-derive what already lives in [[frameworks/X]]. Bias toward lenses applicable to the actual material — drop the rest. -->

*(<lens> lens)*
…

*(<lens> lens)*
…

## Wiki side-effects

<!-- Append-only checklist of what this ingest updated. Machine-readable. -->

- Pattern: [[<slug>]] +1 instance ([HH:MM])
- Theme: [[<slug>]] timeline +1
- Entity: [[<slug>]] Appearances +1
- Concept: [[<slug>]] +1 instance (if a DSM-5 dimension activated, list it here)
- Proposed new page: [[<slug>]] — reason (if applicable; do NOT auto-create)

## Open threads

<!-- 2-3 bullets. Things to test, hypotheses to track, fleeting ideas worth promoting to wiki/questions/. -->

- …

## Pages NOT touched but should be (carry-over)

<!-- Stage-3 revise output: pages this session referenced but didn't update.
Next ingest of related material should fill these in first. Empty if none. -->

- …
