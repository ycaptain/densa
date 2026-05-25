---
type: entity
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-13-meeting-api-style-decision]]", "[[2026-05-19-meeting-vector-db-selection]]"]
tags: [team, api-platform, engineering]
aliases: ["API Platform team", "API Platform engineering"]
status: active
compiled_against: 1
last_validated: 2026-05-21
role: team
lead: "[[stakeholder-marcus-api]]"
---

# API Platform team

The API Platform team owns the public and internal API surface across
all products. Sibling team to [[team-platform]] — Platform builds
the underlying services (identity, webhooks, etc.); API Platform
designs and operates the API surface those services expose.

The team's load-bearing surface in Q2 2026 is the new
[[api-platform-evolution]] arc: deciding the API style for the
post-Q2-migration identity service, then progressively cleaning up
the older REST endpoints inherited from the monolith era.

## Members (Q2 2026)

| Name              | Role                                 | Appears in (raw)                                                                                                |
| ----------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Marcus Chen       | Team lead ([[stakeholder-marcus-api]]) | [[2026-05-13-meeting-api-style-decision]] (owner), [[2026-05-19-meeting-vector-db-selection]] (cross-team)      |

The team has additional members (4 engineers) who do not appear as
named speakers in the current raws; they are mentioned in passing in
the API style meeting's pre-read but do not earn individual
appearances under the workspace L2's stakeholder restraint.

## Appearances

- [[2026-05-13-meeting-api-style-decision]] — Marcus owns the
  meeting; lands option (D) hybrid (gRPC internal + REST gateway
  external).
- [[2026-05-19-meeting-vector-db-selection]] — Marcus attends
  cross-team; contributes the "reversibility matters at v2 horizon"
  framing and Trigger 5 (graph-shaped query mix).

## Cross-stakeholder interfaces

- **[[team-platform]]** — sibling team. Platform builds the
  identity and webhook services; API Platform owns the API contract
  those services expose. The 2026-05-13 meeting was the first
  cross-team decision the two teams co-resolved on the new
  identity service.
- **[[team-ml-platform]]** — sibling team. The API surface to
  the new semantic search lives in API Platform's scope, hiding
  the vector DB choice from internal callers (per
  [[data-platform-vector-search]] action items).
- **Developer Experience** ([[stakeholder-inez-dx]]) — joint
  SDK release cadence; coupled biweekly release.
- **Partner Engineering** ([[stakeholder-bram-partner]]) —
  partner-facing API contract; backward-compat constraint.
- **Product** (Devon Park) — feature-velocity vs API-quality
  trade-offs.

## Decisions in flight

- ADR-002 (API style for identity service) — owned by Marcus,
  draft due 2026-05-20, review 2026-05-22. See
  [[api-platform-evolution]].
- API surface design for semantic search — Marcus, due
  2026-06-09. See [[data-platform-vector-search]].

## Patterns observed

- [[engineering-decision-style]] — the team's 2026-05-13 decision
  meeting is one of the three pattern instances. The combination
  of pre-read trade-off matrix + meeting-as-stress-test + explicit
  exit triggers is the pattern's signature.

## Cross-references

- [[team-platform]] — sibling team across the identity surface.
- [[team-ml-platform]] — sibling team across the search API
  surface.
- [[stakeholder-marcus-api]] — team lead.
- [[api-platform-evolution]] — the team's primary Q2 project.
- [[engineering-decision-style]] — positive pattern this team
  instantiates.
- [[engineering-decisions-retrospective-may-2026]] — cross-team
  synthesis.
