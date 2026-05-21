---
type: report
domain: <your-domain-or-vault>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
tags: [qa]
status: active
---

# <% tp.file.title %>

> Q&A artifact filed back from a `query` run. Lives under `outputs/qa/`,
> ignored by the wikilink resolver. Wiki pages MUST NOT cite this file.
> If this answer turns out to be evergreen, run
> [`promote outputs/qa/<this-file>.md`](../../_system/prompts/promote.md)
> to upgrade it into a wiki page.

## Question

State the question the human asked, verbatim or lightly normalised.

## Sub-claims

<!-- 2-4 numbered claims this answer commits to. Decomposing up front
keeps each downstream paragraph honest. -->

1.
2.

## Answer

<!-- Inline-cited prose. Every non-trivial claim carries a
`[[wiki-page]]` or `[[raw-source]]` link. -->

## Sources

<!-- Aggregated list of every wiki page and raw file read while
answering. The wikilink resolver ignores this file, but the inline
[[wikilinks]] above still point at real wiki pages — promote uses this
section + the inline citations to hoist into frontmatter `sources:`. -->

-

## Uncertainty

<!-- Where the wiki is silent, stale, or contradictory. Leave empty
when nothing meaningful is unknown — do not pad. -->

## Issues to surface at next lint

<!-- Spot-check flags ready for the next `lint` run to pick up
(quote-integrity failures, citation-depth violations, MANUAL/AGENTS
drift). Lint clears this section after ingesting it. -->
