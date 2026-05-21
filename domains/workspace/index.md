---
type: index
scope: workspace
domain: workspace
updated: 2026-05-20
compiled_against: 1
example_status: worked-example
---

# Workspace — Index

Domain-level index for meetings, decisions, projects, stakeholders,
and cross-raw narrative arcs. See [`AGENTS.md`](AGENTS.md) for the
L2 schema (persona, ontology, lint rules) before authoring any wiki
page in this domain.

## Projects

```dataview
TABLE WITHOUT ID
    file.link AS "Project",
    project_status AS "Status",
    start_date AS "Started",
    target_date AS "Target",
    lead AS "Lead"
FROM "domains/workspace/wiki/projects"
WHERE type = "project" AND status = "active"
SORT start_date DESC
```

## Decisions

```dataview
TABLE WITHOUT ID
    file.link AS "Decision",
    adr_id AS "ADR",
    decision_date AS "Date",
    reversibility AS "Reversibility"
FROM "domains/workspace/wiki/decisions"
WHERE type = "decision" AND status = "active"
SORT decision_date DESC
```

## Analyses

```dataview
TABLE WITHOUT ID
    file.link AS "Analysis",
    raw_type AS "Raw type",
    meeting_date AS "Date",
    updated AS "Updated"
FROM "domains/workspace/wiki/analyses"
WHERE type = "analysis" AND status = "active"
SORT meeting_date DESC
```

## Entities (stakeholders + teams)

```dataview
TABLE WITHOUT ID
    file.link AS "Entity",
    role AS "Role",
    team AS "Team",
    title AS "Title"
FROM "domains/workspace/wiki/entities"
WHERE type = "entity" AND status = "active"
SORT role ASC, file.name ASC
```

## Patterns

```dataview
TABLE WITHOUT ID
    file.link AS "Pattern",
    first_observed AS "First observed",
    instances_count AS "Instances"
FROM "domains/workspace/wiki/patterns"
WHERE type = "pattern" AND status = "active"
SORT instances_count DESC
```

## Open questions

```dataview
TABLE WITHOUT ID
    file.link AS "Question",
    arc_status AS "Status",
    first_asked AS "First asked",
    updated AS "Last update"
FROM "domains/workspace/wiki/questions"
WHERE type = "question" AND arc_status != "answered"
SORT updated DESC
```

## Syntheses

```dataview
TABLE WITHOUT ID
    file.link AS "Synthesis",
    updated AS "Updated"
FROM "domains/workspace/wiki/syntheses"
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```

## Recent domain activity

```dataviewjs
const log = await dv.io.load("domains/workspace/log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(0, 15));
}
```
