---
type: summary
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: ["[[<raw-source-wikilink>]]"]
aliases: []
tags: []
status: active
compiled_against: 2
---

# <% tp.file.title %>

<!-- Reader-facing distillation of exactly ONE raw source. Per docs/reference/sources-cardinality.md
a `summary` page MUST cite exactly one raw file in `sources`. If you
find yourself wanting to cite a second raw or a prior summary, you are
writing a `synthesis` — change `type:` and move under `wiki/syntheses/`.

L2 schemas may add required frontmatter fields (e.g. `research-papers`
requires `paper`, `authors`, `evidence_quality`, `replicated`;
psychology adds session-specific fields). Copy those in from the L2-
specific template when applicable. Section layout below is a generic
skeleton — drop sections that don't apply; add L2-specific sub-headers
when the L2 prescribes them. -->

## TL;DR

1–3 sentences. What delta does this source bring to the wiki — which
page strengthened, which thread advanced, what new structure surfaced.

## Key moments

<!-- 3–6 bullets, each anchored to a raw locator (timestamp / section /
paragraph ID) + the entity / concept / open question it activates. -->

- <locator> — short description; touches [[<wiki-page>]]

## Body

<!-- 400–800 words of analytical prose. Inline-link [[wiki-page]]
freely; do NOT re-derive content that already lives in those pages —
point readers at them. For papers / articles: name claim + method +
evidence + limits + open-question. For meetings / decisions: name
context + tensions surfaced + decisions taken / deferred + action
items. -->

…

## Wiki side-effects

<!-- Append-only checklist of what this ingest updated. Machine-readable. -->

- Concept: [[<slug>]] — Appearances +1
- Entity: [[<slug>]] — Appearances +1
- Open question: [[<slug>]] — evidence row added (when applicable)
- Proposed new page: [[<slug>]] — reason (when applicable; do NOT auto-create)

## Open threads

<!-- 2–3 bullets. Hypotheses to track, follow-ups, candidates worth
promoting to `wiki/open-questions/`. -->

- …

## Pages NOT touched but should be (carry-over)

<!-- Pages this source referenced but didn't update this pass. The
next ingest of related material should fill these in first. Empty if
none. -->

- …
