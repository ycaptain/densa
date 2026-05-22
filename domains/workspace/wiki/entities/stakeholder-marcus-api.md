---
type: entity
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-13-meeting-api-style-decision]]", "[[2026-05-19-meeting-vector-db-selection]]"]
tags: [stakeholder, api-platform, engineering]
aliases: ["Marcus Chen", "Marcus from API"]
status: active
compiled_against: 1
last_validated: 2026-05-21
role: stakeholder
team: "[[team-api-platform]]"
title: "API Platform lead"
---

# Marcus Chen (API Platform)

API Platform lead. Owns the public + internal API surface across all
of the team's products, including the new identity service post Q2
migration. Convener of the 2026-05-13 API style decision meeting.

> [!important]
> **Disambiguation.** Marcus Chen (API Platform) is **not** the same
> person as Maya Chen ([[team-platform]] lead). They share a surname,
> which causes routine Slack confusion. When citing this stakeholder
> in a wiki page, always wikilink `[[stakeholder-marcus-api]]` rather
> than using bare "Marcus" — the disambiguation matters for the
> intern reading the wiki cold.

## Role and authority

- **Decision authority**: API style and contract decisions for
  services in the API Platform team's scope.
- **Reviewer authority**: named reviewer on any ADR that touches a
  public API surface; secondary reviewer when the surface is
  internal-only.

## Appearances

| Date       | Raw                                                          | One-line context                                                                                              |
| ---------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| 2026-05-13 | [[2026-05-13-meeting-api-style-decision]]                    | Owns the API style decision; proposes and lands option (D) hybrid (gRPC internal + REST gateway external)     |
| 2026-05-19 | [[2026-05-19-meeting-vector-db-selection]]                   | Cross-team attendee; advocates for reversibility as the decision dimension that matters at v2 horizon         |

## Decisions led

- **API style for the new identity service** (2026-05-13) → option
  (D) hybrid: gRPC internal + hand-written REST gateway external,
  with three named exit triggers. To be formalised as ADR-002 by
  2026-05-20. See [[api-platform-evolution]].

## Concerns raised

1. **Two-surface contract drift** (2026-05-13, ~14:22). With (D)
   hybrid, the team maintains both OpenAPI (partner-facing) and
   proto (internal) contracts. If they drift, partners see weirdness.
   Mitigation: biweekly coupled SDK release (slip both if either
   slips); committed jointly with [[stakeholder-inez-dx]].
2. **API surface needs hybrid graph + vector queries** (2026-05-19,
   ~10:40). Added Trigger 5 to the vector DB decision: if the API
   request mix shifts to needing graph-shaped queries against
   search results, pgvector starts looking weak vs specialised
   vector DBs.

## Decision style

Marcus' decision-meeting shape (observed across the API style meeting
and his cross-team contributions to the vector DB meeting) is one of
the three instances of the [[engineering-decision-style]] positive
pattern: pre-read with a fully-derived trade-off matrix, meeting
spent on stress-testing rather than re-deriving, explicit exit
triggers named before the decision is signed.

## Cross-references

- [[team-api-platform]] — Marcus' team.
- [[team-platform]] — sibling Platform team; works closely with on
  the identity service (the surface API Platform exposes is what
  Platform's identity work produces).
- [[stakeholder-inez-dx]] — DX lead; joint SDK release cadence.
- [[stakeholder-bram-partner]] — Partner Engineering lead; advocates
  for partner backward-compat which constrained the API style
  decision.
- [[api-platform-evolution]] — the project Marcus owns at the
  API-style level.
- [[data-platform-vector-search]] — the cross-team project Marcus
  feeds API constraints into.
- [[engineering-decision-style]] — positive pattern; Marcus is one
  of the three pattern instances.
- [[engineering-decisions-retrospective-may-2026]] — cross-decision
  synthesis.
