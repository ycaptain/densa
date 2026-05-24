---
type: protocol
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
# `area:` is optional and L2-defined. Add it here only if your L2's
# AGENTS.md declares an `area` enum (e.g. an L2 that organises
# protocols by topical bucket); otherwise leave it out.
status: active
protocol_status: considering  # L2-defined: considering | trialing | adopted | retired
started: <% tp.date.now("YYYY-MM-DD") %>
last_revised: <% tp.date.now("YYYY-MM-DD") %>
evidence: anecdote
tags: []
compiled_against: 1
last_validated: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.file.title %>

One-paragraph description: what the routine is, what it claims to do,
and what would falsify it.

## Routine

Concrete steps, dosages, frequencies. Be specific enough that a future
me can replicate without guessing.

## Claimed effect

What it should change, on what time horizon, by what mechanism.

## Evidence

Use the evidence ladder — `mechanism | observational | rct | anecdote` —
per claim, not just for the protocol overall.

| Claim | Evidence    | Source              |
| ----- | ----------- | ------------------- |
| …     | mechanism   | [[<concept>]]       |
| …     | rct         | [[<article>]]       |

## Linked experiments

- [[<experiment-id>]] — N-of-1 trial of this protocol

## Revision log

<!-- Append-only. -->

- YYYY-MM-DD — what changed and why
