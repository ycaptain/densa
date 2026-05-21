---
type: analysis
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: ["[[<raw-source-wikilink>]]"]
tags: []
status: active
compiled_against: 1
---

# <% tp.file.title %>

<!-- Domain-neutral analysis of exactly ONE raw source.
Per L1 §3.1, an `analysis` page MUST cite exactly one raw file in `sources`.
If you find yourself wanting to cite a second raw or a prior analysis, you
are writing a `synthesis` — change the type and move the file to
wiki/syntheses/. L2 schemas may add required frontmatter fields
(e.g. psychology requires `session_kind`, `analysis_lens`,
`diagnostic_signals`; research-papers requires `evidence_quality`,
`replicated`). When such fields apply, copy them in from the L2-specific
template (e.g. `_system/templates/psychology-analysis.md`).

Section layout below is a generic skeleton. Drop sections that don't apply;
add L2-specific sections (e.g. psychology's `症状评估` / `用药记录`) by
copying from the matching L2 template. -->

## TL;DR

1-3 sentences. What delta does this source bring to the wiki — which page
strengthened, which thread advanced, what new structure surfaced.

## Key moments

<!-- 3-6 bullets, each anchored to a raw locator (timestamp / section /
paragraph ID) + the entity / concept / pattern it activates. -->

- <locator> short description — touches [[<wiki-page>]]

## Body

<!-- 400-800 words of analytical prose. Inline-link [[wiki-page]] freely;
do NOT re-derive what already lives in those pages — point readers at them.
For papers / articles: name claim + method + evidence + limits +
open-question. For meetings / decisions: name context + tensions surfaced +
decisions taken / deferred + action items. Use L2-specific sub-headers when
the L2 prescribes them. -->

…

## Wiki side-effects

<!-- Append-only checklist of what this ingest updated. Machine-readable. -->

- Concept: [[<slug>]] +1 instance
- Entity: [[<slug>]] Appearances +1
- Pattern: [[<slug>]] +1 instance (when applicable)
- Proposed new page: [[<slug>]] — reason (if applicable; do NOT auto-create)

## Open threads

<!-- 2-3 bullets. Hypotheses to track, follow-ups, questions worth
promoting to wiki/questions/. -->

- …

## Pages NOT touched but should be (carry-over)

<!-- Pages this source referenced but didn't update this pass. The next
ingest of related material should fill these in first. Empty if none. -->

- …
