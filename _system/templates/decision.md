---
type: decision
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
decision_id: <project>-<NNN>
decided_on: <% tp.date.now("YYYY-MM-DD") %>
status: proposed
project: <project-slug>
supersedes: []
superseded_by: []
tags: []
---

# <% tp.file.title %>

<!-- ADR-lite. Once `status: accepted`, this page is IMMUTABLE except
for typo fixes and link repair. New information → new decision page that
`supersedes:` this one. See your domain's L2 AGENTS.md §"Decision pages". -->

## Context

What changed in the world that forced this decision. State the problem
in present tense; do not pre-justify the conclusion.

## Decision

What we decided. One paragraph, declarative.

## Alternatives considered

- **A** — pros / cons / why rejected
- **B** — pros / cons / why rejected

## Consequences

Expected impact, what we're now committed to, what we're betting against.
List both upside and downside; an honest decision page names what it
gives up.

## Links

- Source meeting / thread: [[<raw>]]
- Project: [[<project>]]
- Supersedes: [[<prior decision>]] (if any)
- Superseded by: [[<later decision>]] (filled in if/when superseded)
