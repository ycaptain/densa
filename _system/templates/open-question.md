---
type: open-question
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
tags: [open-question]
status: active
compiled_against: 2
arc_status: open
first_asked: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.file.title %>

<!-- Long-arc empirical question that accumulates evidence over time.
Per L1 §3 the page is a *ledger*: each new [[summary]] that bears on
the question appends an evidence row, never re-states the underlying
fact. The page itself stays declarative about the *question*, not the
answer. -->

State the question in one paragraph: what we'd need to observe to
consider it resolved, and what we don't yet observe.

## Why this matters

2–4 bullets on the downstream decisions / claims that hinge on this
question's resolution.

## Evidence ledger

| Date | Source | Direction | Strength | Note |
|------|--------|-----------|----------|------|
| YYYY-MM-DD | [[<summary-slug>]] | supports / undermines / orthogonal | weak / moderate / strong | one-line read |

## Adjacent questions

- [[<other-open-question-slug>]] — relation
- [[<concept-slug>]] — relation

## What would change my mind

<!-- 2–3 concrete observations that would shift `arc_status` to
`partial` or `answered`. Useful for the human reviewing the ledger
quarterly. -->

- …

## Sources

<!-- Optional pinned list when a specific summary is the question's
anchor; otherwise the evidence ledger above is the canonical source
list and this section can be omitted. -->

- [[<summary-slug>]] — the anchor that first surfaced this question
