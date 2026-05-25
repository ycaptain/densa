---
type: pattern
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
triggers: []
first_observed: <% tp.date.now("YYYY-MM-DD") %>
last_observed: <% tp.date.now("YYYY-MM-DD") %>
# `severity:` is optional and L2-defined (e.g. psychology declares an
# enum); leave it out unless your L2's AGENTS.md prescribes it.
tags: []
status: active
compiled_against: 1
---

# <% tp.file.title %>

One-sentence definition: what triggers it, what the loop looks like, what
it costs.

## Mechanism

The internal logic. Why does the loop self-perpetuate?

## Triggers

- …

## Instances

<!-- Append-only timeline. ≥2 distinct sources required for a pattern to
stay active (else lint downgrades to a session-level note). -->

- YYYY-MM-DD — [[<analysis-or-raw>]] — short paraphrase, ≤2 lines

## Interventions tried

| Date       | Intervention | Outcome              | Source     |
| ---------- | ------------ | -------------------- | ---------- |
| YYYY-MM-DD | …            | successful / partial | [[…]]      |

## Related

- Concepts: [[…]]
- Themes:   [[…]]
- Patterns it co-occurs with: [[…]]
