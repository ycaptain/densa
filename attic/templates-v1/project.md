---
type: project
domain: <your-domain>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
sources: []
aliases: []
project: <slug>
status: active
project_status: discovery     # L2-defined: discovery | active | paused | shipped | abandoned
owners: [self]
started: <% tp.date.now("YYYY-MM-DD") %>
target:
priority: P1
tags: []
compiled_against: 1
---

# <% tp.file.title %>

One-paragraph project framing: what's being built, for whom, why now.

## Scope

- **In**: …
- **Out**: …

## Stakeholders

- [[<stakeholder>]] — role on this project

## Recent activity

<!-- Append-only. Each entry: date, source link, one-line gist. -->

- YYYY-MM-DD — [[<raw>]] — what happened

## Open questions / risks

- …

## Decisions

```dataview
TABLE WITHOUT ID
    file.link AS "Decision",
    decided_on AS "Date",
    status AS "Status"
FROM "domains/<your-domain>/wiki/decisions"
WHERE type = "decision" AND project = this.project
SORT decided_on DESC
```

## Milestones

| Date       | Milestone | Status |
| ---------- | --------- | ------ |
| YYYY-MM-DD | …         | …      |
