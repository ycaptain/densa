---
type: experiment
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
experiment_id: <area>-<NNN>
hypothesis: ""
started: <% tp.date.now("YYYY-MM-DD") %>
ends:
status: planned
outcome: tbd
metric_links: []
tags: []
compiled_against: 1
---

# <% tp.file.title %>

## Hypothesis

One sentence. Should be falsifiable with the metrics you plan to track.

## Protocol

Exactly what you'll do. If this references an existing protocol page, link
[[…]] and only note the deviations here.

## Metrics

What you'll measure, how often, and from where the data comes
(`raw/metrics/…`).

| Metric | Frequency | Source                |
| ------ | --------- | --------------------- |
| …      | …         | [[<raw-metric>]]      |

## Decision criteria

How the result will translate into a next action — adopt as protocol,
extend, drop, or replace.

## Confounds

Things that could explain a positive or null result without the
hypothesis being right.

## Check-ins

<!-- Append-only weekly notes during `status: running`. -->

- YYYY-MM-DD — observation

## Outcome

(Filled in when `status: done`.) Effect size, confidence, recommended
next action.
