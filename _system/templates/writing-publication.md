---
type: fleeting
domain: writing
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
tags: [writing, published]
status: active
compiled_against: 1
publication_status: published
published_on: <% tp.date.now("YYYY-MM-DD") %>
published_url: <https://…>
target_venue: <blog | newsletter | substack | thread | …>
canonical_length_words: <final>
---

# <% tp.file.title %>

> Lives under `writing/published/<slug>.md`. Treat as a snapshot of
> what shipped: per-L2 lint rules MAY enforce immutability, but
> `share/` v0.x does not ship one. Frontmatter here is **advisory**.

## Published version

<!-- Paste the canonical text that went out. Keep this section
identical to the publication; corrections go in §Errata below
rather than rewriting the body. -->

## Wiki dependencies

- [[<concept-or-synthesis>]] — what this piece relied on
- …

## Promotion candidates

<!-- After publishing, any reusable claim that earned reader
engagement may be worth promoting into a wiki page. Note them here;
the next `lint` will surface them for human review. -->

- …

## Errata

<!-- Post-publication corrections. Each entry: date + one-line
description + link to revised venue if applicable. -->

- …
