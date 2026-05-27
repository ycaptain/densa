---
type: overview
domain: psychology
created: 2026-05-26
updated: 2026-05-26
sources: []
tags: []
aliases: ["psychology home", "psychology overview"]
status: active
compiled_against: 2
---

# psychology — Overview

> [!important] If you're new here, this is the only page you need to
> start. Run `ingest` against any source under `raw/` and the agent
> will populate the buckets below.

## What this domain has (mindmap)

```mermaid
mindmap
  root((psychology))
    Summaries
      one per ingested source
    Entities
      people orgs and objects
    Concepts
      terms worth defining once
    Comparisons
      X vs Y
    Sub-area overviews
      birds-eye views
    Syntheses
      cross-source narratives
    Open questions
      long-arc trackers
```

## What page do I read when?

| Situation | Read |
|---|---|
| Elevator pitch | the mindmap above |
| One source's takeaways | a page in `summaries/` (~5 min each) |
| Look up a term | a page in `concepts/` |
| Track a person / org | a page in `entities/` |
| Compare two things | a page in `comparisons/` |
| Cross-source story | a page in `syntheses/` |
| Sub-area bird's-eye | a page in `overviews/` |
| What's still open | a page in `open-questions/` |

## Pages migrated mechanically (re-ingest when load-bearing)

```dataview
TABLE WITHOUT ID file.link AS "Page", type AS "Type", updated AS "Updated"
FROM "examples/showcases/psychology/wiki"
WHERE migration_history AND status = "active"
SORT updated DESC
```

## Summaries

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "examples/showcases/psychology/wiki/summaries"
WHERE type = "summary" AND status = "active"
SORT updated DESC
```

## Concepts

```dataview
TABLE WITHOUT ID file.link AS "Page", last_validated AS "Validated"
FROM "examples/showcases/psychology/wiki/concepts"
WHERE type = "concept" AND status = "active"
SORT last_validated DESC
```

## Entities

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "examples/showcases/psychology/wiki/entities"
WHERE type = "entity" AND status = "active"
SORT updated DESC
```

## Comparisons

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "examples/showcases/psychology/wiki/comparisons"
WHERE type = "comparison" AND status = "active"
SORT updated DESC
```

## Sub-area overviews

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "examples/showcases/psychology/wiki/overviews"
WHERE type = "overview" AND status = "active"
SORT updated DESC
```

## Syntheses

```dataview
TABLE WITHOUT ID file.link AS "Page", updated AS "Updated"
FROM "examples/showcases/psychology/wiki/syntheses"
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```

## Open questions

```dataview
TABLE WITHOUT ID file.link AS "Page", arc_status AS "Status", updated AS "Updated"
FROM "examples/showcases/psychology/wiki/open-questions"
WHERE type = "open-question"
SORT updated DESC
```

## Recent activity

```dataviewjs
const log = await dv.io.load("examples/showcases/psychology/log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(0, 10));
}
```
