---
type: project
domain: workspace
created: 2026-05-20
updated: 2026-05-21
sources: ["[[2026-04-08-meeting-q2-planning]]", "[[2026-04-22-decision-microservices-split]]", "[[2026-05-06-meeting-incident-postmortem]]"]
tags: [platform, microservices, migration, q2-2026]
aliases: ["Q2 platform migration", "identity-webhook split"]
status: active
compiled_against: 1
last_validated: 2026-05-20
project_status: paused
start_date: 2026-04-01
target_date: 2026-06-30
lead: "Maya Chen"
---

# Q2 platform migration

Extraction of two bounded contexts — **identity** and **webhooks**
— from the monolith into independent services. First step of a
multi-quarter platform-modernisation programme intended to lift
deploy frequency 2–3× by end of Q3 2026.

## Goal

- Lift the monolith's deploy-queue bottleneck by isolating
  independently-deployable bounded contexts.
- Deliver phase 3 (full cutover, monolith decommissioned for
  identity + webhooks) by end of Q2.
- Lay a clean bounded-context contract that the Q3 follow-on
  (billing, content) can reuse.

## Scope

**In scope:** identity service extraction (session-state migration
Redis → Postgres, dual-write window); webhook service extraction
(new routing layer, shadow mode, phased traffic shift); rollback
runbook with state reconciliation; cross-layer monitoring upgrade
(added post-incident).

**Out of scope (Q2):** billing and content service extraction
(deferred to Q3); CS veto-power process change (parked as
[[should-we-revisit-cs-veto-power]]).

## Status

- Phase 0 (staging soak): complete (2026-04-23 → 2026-04-28).
- Phase 1 (production shadow on webhooks): complete (2026-04-29 →
  2026-05-03); zero silent drops observed in shadow data.
- Phase 2 (10% traffic on new routing layer): rolled back on
  2026-05-04 following the incident captured in
  [[2026-05-06-meeting-incident-postmortem-analysis]].
- Phase 3: blocked pending cross-layer reconciliation work
  (Priya, due 2026-05-20).

Project status is **paused** at the project-management level even
though [[microservices-split]] remains the active canonical
decision. The pause is operational, not strategic — the team
expects to resume phase 2 after cross-layer reconciliation lands.

## Decisions

- [[microservices-split]] — canonical ADR-001 decision, currently
  active with phase-2 rollback in effect.

## Sessions and source raws

| Date       | Raw                                                          | Role in arc                                                |
| ---------- | ------------------------------------------------------------ | ---------------------------------------------------------- |
| 2026-04-08 | [[2026-04-08-meeting-q2-planning]]                           | Scoping meeting; CS concern raised                         |
| 2026-04-22 | [[2026-04-22-decision-microservices-split]]                  | ADR-001 finalised; concern partially mitigated, partially deferred |
| 2026-05-06 | [[2026-05-06-meeting-incident-postmortem]]                   | Postmortem of incident matching the deferred residual risk |

## Stakeholders

- [[team-platform]] — owning team.
- [[stakeholder-alex-cs]] — load-bearing external reviewer for
  SLA-exposing surfaces.
- Devon Park (Product) — accountable for trade-offs between
  customer-visible work and platform investment.
- Tom Becker (SRE) — operational owner of cutover and rollback.

## Open risks

- **Cross-layer reconciliation work** (Priya, blocking phase 3).
  Currently in flight.
- **Phase 3 rollback complexity.** Once Redis is decommissioned,
  rollback requires snapshot restore (~90 minutes minimum).
  Riverdale account specifically asking for additional assurances
  about phase-3 conditions.
- **Process risk: CS sign-off authority.** Parked as
  [[should-we-revisit-cs-veto-power]]; could resurface in any
  future SLA-exposing ADR.

## Cross-references

- [[microservices-split]] — the canonical decision page.
- [[2026-04-08-meeting-q2-planning-analysis]],
  [[2026-04-22-decision-microservices-split-analysis]],
  [[2026-05-06-meeting-incident-postmortem-analysis]] — the three
  analyses covering the arc.
- [[q2-platform-arc-may]] — narrative synthesis across the arc.
- [[decision-delay-from-skipped-stakeholder]] — the pattern this
  project provides an instance of.
- [[api-platform-evolution]] — downstream project: API style for
  the new identity service produced by this migration.
- [[engineering-decision-style]] — positive pattern; ADR-001 is
  the partial-instance / near-miss the May decisions improve on.
- [[engineering-decisions-retrospective-may-2026]] — cross-decision
  synthesis braiding this project's ADR-001 with the May
  decisions.
