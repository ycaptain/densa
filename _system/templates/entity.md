---
type: entity
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
role:
first_seen: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
tags: []
status: active
compiled_against: 2
last_validated: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.file.title %>

One-paragraph who-they-are: relationship to me, why they matter, what they
represent in the wiki.

## Profile

- **Role**:
- **Context**:
- **Communication style** (if relevant):

## Appearances

<!-- Append-only timeline. Each row MUST carry a one-line context note —
that annotation is the information the page stores. A bare date + link
row says nothing a backlink doesn't, and each explicit link is one more
edge in the graph view; if you find yourself appending unannotated
rows, delete the tail and let the Dataview block below surface them. -->

- YYYY-MM-DD — [[<source>]] — short note

<!-- Optional: replaces unannotated enumeration. `FROM [[]]` lists the
pages that link here; a rendered query creates no graph edges. -->

```dataview
LIST FROM [[]] WHERE type = "summary" SORT file.name DESC
```

## Recurring threads they participate in

<!-- Wikilinks to [[concept-…]] / [[synthesis-…]] / [[overview-…]]
pages this entity recurs in. -->

## Open questions

<!-- Things I still don't understand about this entity. -->
