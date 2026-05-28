---
type: index
scope: workspace
domain: workspace
updated: 2026-05-28
compiled_against: 2
example_status: worked-example
---

# Workspace — Index

Domain-level index for meetings, decisions, projects, stakeholders,
and cross-raw narrative arcs. See [`AGENTS.md`](AGENTS.md) for the
L2 schema (persona, ontology, lint rules) before authoring any wiki
page in this domain.

## Summaries (1:1 per raw)

```dataview
TABLE WITHOUT ID
    file.link AS "Summary",
    raw_type AS "Raw type",
    meeting_date AS "Date",
    updated AS "Updated"
FROM "examples/showcases/workspace/wiki/summaries"
WHERE type = "summary" AND status = "active"
SORT meeting_date DESC
```

## Entities (stakeholders + teams + v1 projects/decisions via `kind:`)

```dataview
TABLE WITHOUT ID
    file.link AS "Entity",
    kind AS "Kind",
    role AS "Role",
    team AS "Team",
    title AS "Title"
FROM "examples/showcases/workspace/wiki/entities"
WHERE type = "entity" AND status = "active"
SORT role ASC, file.name ASC
```

## Concepts (incl. v1 patterns via `kind:`)

```dataview
TABLE WITHOUT ID
    file.link AS "Concept",
    kind AS "Kind",
    first_observed AS "First observed",
    instances_count AS "Instances"
FROM "examples/showcases/workspace/wiki/concepts"
WHERE type = "concept" AND status = "active"
SORT instances_count DESC
```

## Open questions

```dataview
TABLE WITHOUT ID
    file.link AS "Question",
    arc_status AS "Status",
    first_asked AS "First asked",
    updated AS "Last update"
FROM "examples/showcases/workspace/wiki/open-questions"
WHERE type = "open-question" AND arc_status != "answered"
SORT updated DESC
```

## Syntheses

```dataview
TABLE WITHOUT ID
    file.link AS "Synthesis",
    updated AS "Updated"
FROM "examples/showcases/workspace/wiki/syntheses"
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```

## Recent domain activity

```dataviewjs
const log = await dv.io.load("examples/showcases/workspace/log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(0, 15));
}
```
