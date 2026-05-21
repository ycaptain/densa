---
type: correction
domain: <your-domain>
# `area:` is optional and L2-defined. Add it here only if your L2's
# AGENTS.md declares an `area` enum (e.g. an L2 that tracks failures
# by sub-skill or sub-area); otherwise leave it out.
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: ["[[<analysis-or-raw-wikilink>]]"]
severity: <% tp.system.suggester(["low", "medium", "high"], ["low", "medium", "high"], false, "Severity") %>
first_observed: <% tp.date.now("YYYY-MM-DD") %>
last_observed: <% tp.date.now("YYYY-MM-DD") %>
status: open
linked_concept: "[[<concept-slug>]]"
linked_protocol: "[[<protocol-slug>]]"
tags: []
compiled_against: 1
---

# <% tp.file.title %>

<!-- A persistent failure mode that recurs across attempts / lessons /
sessions. One page per failure mode. Body is prescriptive: it tells the
user *where the problem is* and *what to do next*. Each new ingest that
re-observes the failure updates this page's recurrence log + last_observed
+ (if applicable) severity.

This template is **domain-neutral**. L2s tracking embodied / motor /
perceptual practice (music, sport, language, drawing) may want to fork
this template into a specialised variant under
`_system/templates/<l2>-correction.md` that adds embodied-specific
sections like "self-check in 5 seconds", "target geometry", "this
week's drills", and a falsification window — those add value for motor
work but distract from non-embodied corrections (coding defects,
reasoning fallacies, communication patterns). -->


## TL;DR

One sentence: what the failure mode is, in observable terms.
One sentence: the corrective stance you want next time.

## How to recognise it

<!-- Concrete signals that this failure mode is present. Each should be
verifiable in-the-moment, not after the fact. -->

1. **<signal 1>** — …
2. **<signal 2>** — …
3. **<signal 3>** — …

## Why it happens

Mechanism — what underlying constraint / habit / belief produces this
failure. Link [[concept-slug]] for any concept that explains the
mechanism (do not re-derive the concept here).

## What to do instead

<!-- Up to 5 prioritised, actionable steps. Granularity should be "user
can act on this without re-interpreting it." Abstract advice ("be more
careful") does not belong here. -->

1. **Highest priority**: …
2. …
3. …

## Falsification

- **Improvement signal**: by <N days/weeks> of applying §"What to do
  instead", expect to observe …
- **No-improvement signal**: if after <N days/weeks> we still see …,
  the mechanism in §"Why it happens" may be wrong; revisit.
- **Escalate severity** when: <condition>.

## Recurrence log

<!-- Append-only timeline. One row per occurrence of the failure mode
(or its resolution) — link the source (analysis, session, raw moment). -->

- YYYY-MM-DD — <one-line context, locator link, observation>

## Linked pages

- Concept: [[<concept-slug>]]
- Protocol: [[<protocol-slug>]]
- Related questions: [[<question-slug>]]
- Adjacent corrections: [[<other-correction-slug>]] — one-line relation
