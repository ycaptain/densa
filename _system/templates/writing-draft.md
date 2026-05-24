---
type: fleeting
domain: writing
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
tags: [writing, draft]
status: active
compiled_against: 1
publication_status: draft
target_venue: <blog | newsletter | substack | thread | …>
target_length_words: <approx>
---

# <% tp.file.title %>

> Lives under `writing/drafts/<slug>.md`. Not part of the wikilink
> contract: `writing/` is excluded from the L1 page-type schema
> enforcement. Frontmatter here is **advisory** — adapt as needed.
> When shipped, `git mv` the file into `writing/published/<slug>.md`
> and bump `publication_status: published` plus `published_on:`.

## Thesis

One sentence: what this piece claims.

## Audience & venue

- **Reader**: who is this for?
- **Venue**: where will it land?
- **Length target**: …

## Outline

1. …
2. …
3. …

## Draft

<!-- Compose freely. Cite wiki pages with [[wikilink]] when leaning
on compounded knowledge; the citations flow writing → wiki, never
the reverse. -->

## Wiki dependencies

- [[<concept-or-synthesis>]] — what this piece borrows from it
- …

## Open questions before publishing

- …
