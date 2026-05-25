---
type: project
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-13-meeting-api-style-decision]]"]
tags: [api-platform, public-api, sdk, q2-2026]
aliases: ["API Platform evolution", "API style refresh"]
status: active
compiled_against: 1
last_validated: 2026-05-21
project_status: active
start_date: 2026-05-13
target_date: 2026-09-30
lead: "[[stakeholder-marcus-api]]"
---

# API Platform evolution

Multi-quarter arc to modernise the public + internal API surface.
First milestone (Q2): pick the API style for the post-migration
identity service. Subsequent milestones (Q3-Q4): progressively
clean up the older REST endpoints inherited from the monolith era;
revisit GraphQL gateway for analytics queries.

## Goal

- Land a defensible API style (REST + gRPC hybrid) for the new
  identity service that survives the next 18-24 months of internal
  callers + partner integrations.
- Re-shape the SDK release cadence so the two surfaces (internal
  proto-generated, external REST) stay coupled.
- Build the operational posture (per-surface SLOs, REST↔gRPC trace
  correlation) before partner traffic touches the gateway.

## Scope

**In scope (Q2):**
- API style decision (option (D) hybrid) — see
  [[2026-05-13-meeting-api-style-decision-analysis]].
- ADR-002 (formalising the decision) — Marcus, due 2026-05-20.
- REST gateway implementation (3 engineering-weeks within the 7-week
  total).
- REST↔gRPC trace correlation as phase-1 deliverable.
- Coupled biweekly SDK release.

**Out of scope (Q2):**
- GraphQL gateway for analytics surface — deferred to Q4
  (see exit Trigger 2 in [[2026-05-13-meeting-api-style-decision-analysis]]).
- Older monolith REST endpoint cleanup — Q3 effort.

## Status

- 2026-05-13 — Decision meeting; option (D) selected.
- 2026-05-20 (target) — ADR-002 draft.
- 2026-05-22 (target) — ADR-002 review and acceptance.
- 2026-05-22 (target) — Partner notifications sent (Bram, due
  2026-05-20).
- 2026-05-25 (target) — Operational dual-surface monitoring posture
  (Tom).
- End-of-Q2 (target) — Phase-1 deliverable: gRPC native for internal
  callers + REST gateway live for partners.

## Decisions

- **API style for identity service**: option (D) hybrid (gRPC
  internal + hand-written REST gateway external). Pending ADR-002
  formalisation. Will populate a canonical decision page once the
  ADR lands; see [[2026-05-13-meeting-api-style-decision-analysis]]
  for the decision's rationale.

## Sessions and source raws

| Date       | Raw                                                          | Role in arc                                                |
| ---------- | ------------------------------------------------------------ | ---------------------------------------------------------- |
| 2026-05-13 | [[2026-05-13-meeting-api-style-decision]]                    | Decision meeting; option (D) hybrid selected               |

## Stakeholders

- [[team-api-platform]] — owning team.
- [[stakeholder-marcus-api]] — lead and decision owner.
- [[stakeholder-inez-dx]] — DX, joint SDK release cadence.
- [[stakeholder-bram-partner]] — Partner Engineering, partner-compat
  blocking constraint.
- [[team-platform]] — sibling team; identity service implementation.
- Tom Becker (SRE) — operational dual-surface posture.
- Devon Park (Product) — feature-velocity oversight.

## Open risks

- **Two-surface contract drift.** OpenAPI (partner) + proto
  (internal) contracts can diverge if release discipline slips.
  Mitigation: biweekly coupled release commitment.
- **REST↔gRPC trace correlation as phase-1 must-have.** If shipped
  under time pressure without it, incident debugging will be 2x
  harder (Tom flagged at ~14:24 on 2026-05-13).
- **Partner sign-off process for ADR-002.** Same partial-sign-off
  question raised in [[should-we-revisit-cs-veto-power]] applies
  to Bram's review of ADR-002. Tom and Devon's "blocking vs
  deferrable risks" one-pager (due 2026-05-13, may already be
  drafted) becomes relevant here.

## Connections to other projects

- **[[q2-platform-migration]]** — the identity service this project
  designs the API for. ADR-002 (this project) follows ADR-001
  (Q2 migration) in the same naming series.
- **[[data-platform-vector-search]]** — the search service that
  will also live behind an API Platform–owned surface; the
  reversibility-at-v2-horizon framing Marcus brought to the vector
  DB meeting (2026-05-19) is informed by his own API decision
  experience from 2026-05-13.

## Cross-references

- [[2026-05-13-meeting-api-style-decision-analysis]] — the analysis
  of the decision meeting.
- [[engineering-decision-style]] — positive pattern this project
  exemplifies.
- [[engineering-decisions-retrospective-may-2026]] — cross-decision
  synthesis braiding this project's decision with Q2 platform
  migration's ADR-001 and the vector DB selection.
