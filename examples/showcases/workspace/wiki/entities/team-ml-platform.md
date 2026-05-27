---
type: entity
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-19-meeting-vector-db-selection]]"]
tags: [team, ml-platform, engineering]
aliases: ["ML Platform team", "ML Platform engineering"]
status: active
compiled_against: 2
last_validated: 2026-05-21
role: team
lead: "[[stakeholder-hiro-ml]]"
migration_history:
  - from: 1
    to: 2
    on: 2026-05-26
    mode: in-place
    notes: 'type stayed entity'
---

# ML Platform team

The ML Platform team owns the ML infrastructure stack: embedding
models, vector databases, training pipelines, inference platforms,
and the semantic-search service. Sibling team to [[team-platform]]
(general infrastructure) and [[team-api-platform]] (API surface).

The team's load-bearing surface in Q2 2026 is the new
[[data-platform-vector-search]] project: shipping semantic search
v1 by end of Q2 with the right vector DB choice for v1 scale.

## Members (Q2 2026)

| Name              | Role                                  | Appears in (raw)                                  |
| ----------------- | ------------------------------------- | ------------------------------------------------- |
| Hiro Tanaka       | Team lead ([[stakeholder-hiro-ml]])   | [[2026-05-19-meeting-vector-db-selection]] (owner)  |
| Yuki Nakamura     | Senior ML engineer                    | [[2026-05-19-meeting-vector-db-selection]] (ran benchmarks; speaks once at ~10:28) |

Yuki appears in the vector DB meeting raw as a named speaker on a
load-bearing point (the Postgres 15 → 16 upgrade dependency for HNSW).
Per the workspace L2's stakeholder-appearance threshold (≥2 turns
*or* one load-bearing claim), Yuki is at the edge — promoted to
appearance here on the team page; will earn a dedicated
`stakeholder-yuki-ml.md` page if a second appearance materialises.

## Appearances

- [[2026-05-19-meeting-vector-db-selection]] — Hiro owns the
  meeting; lands pgvector v1 with five named migration triggers.
  Yuki contributes the IVFFlat vs HNSW + Postgres-version
  observation.

## Cross-stakeholder interfaces

- **[[team-platform]]** — Platform owns the Postgres infrastructure
  that pgvector v1 will run on; the Postgres 15 → 16 upgrade in Q3
  (Priya owns; see [[team-platform]]) is a dependency for the
  HNSW migration path.
- **[[team-api-platform]]** — API Platform owns the public API
  surface for the new semantic search endpoint; the vector DB
  choice is hidden from internal callers behind that API.
- **Product** (Devon Park) — feature-velocity vs ML-stack
  investment trade-offs; enterprise pre-sales sensitivity to
  "managed-cheap-tier" branding (Devon raised this 2026-05-19).

## Decisions in flight

- ADR-003 (vector DB v1) — owned by Hiro, draft due 2026-05-26,
  review 2026-05-28. See [[data-platform-vector-search]].

## Patterns observed

- [[engineering-decision-style]] — the team's 2026-05-19 decision
  meeting is one of the three pattern instances. Same signature
  as the API Platform meeting: pre-read benchmark memo, meeting
  spent on stress-testing recommendation, five explicit exit
  triggers, per-tenant tuning approach documented for downstream
  ownership.

## Cross-references

- [[team-platform]] — sibling infrastructure team; Postgres
  ownership dependency.
- [[team-api-platform]] — sibling API team; owns the API surface
  fronting the search service.
- [[stakeholder-hiro-ml]] — team lead.
- [[data-platform-vector-search]] — the team's primary Q2
  project.
- [[engineering-decision-style]] — positive pattern this team
  instantiates.
- [[engineering-decisions-retrospective-may-2026]] — cross-team
  synthesis.
