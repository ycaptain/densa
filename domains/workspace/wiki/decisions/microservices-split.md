---
type: decision
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-04-22-decision-microservices-split]]", "[[2026-04-08-meeting-q2-planning]]", "[[2026-05-06-meeting-incident-postmortem]]"]
tags: [adr, platform, microservices, webhooks, identity-service]
aliases: ["ADR-001", "identity-webhook split"]
status: active
compiled_against: 1
last_validated: 2026-05-20
adr_id: "ADR-001"
decision_date: 2026-04-22
reversibility: partial
stakeholders: ["[[stakeholder-alex-cs]]", "[[team-platform]]"]
---

# Microservices split (ADR-001)

Canonical wiki page for the Platform team's decision to extract
**identity** and **webhooks** as independent services. Distinct
from the raw ADR document
([[2026-04-22-decision-microservices-split]]) and from the
analysis of that ADR
([[2026-04-22-decision-microservices-split-analysis]]) — this is
the page the rest of the wiki cites when referring to "the
microservices split decision".

## Context

Q2 2026. The monolith's coupled deploy story is the single
largest bottleneck on the Platform team's throughput. Two bounded
contexts (identity, webhooks) are clean candidates for extraction.
Two enterprise accounts hold contractual webhook delivery SLAs;
their exposure is the load-bearing constraint on rollout shape.

For the planning context that produced this decision, see
[[2026-04-08-meeting-q2-planning-analysis]].

## Decision

Extract `identity` and `webhooks` as independent services using a
**4-phase rollout** with hard gates between phases. Shadow mode
on the webhook routing layer for ≥14 days before any production
traffic shift. Rollback as a runbook with state reconciliation,
not a deploy revert.

## Rationale

- Phased rollout (vs big-bang) is the only shape compatible with
  the enterprise SLA exposure profile.
- Shadow mode validates the routing layer under real load
  without customer exposure.
- Session-state dual-write window contains the consistency risk
  during the identity extraction.

## Stakeholders

- **Maya Chen** ([[team-platform]] lead) — author.
- **Devon Park** (Product) — approver.
- **Tom Becker** (SRE) — approver, conditional on rollback
  runbook sign-off (resolved same day).
- **[[stakeholder-alex-cs]]** — reviewer of webhook section.
  **Partial sign-off.** Approved the routing-layer-local
  assertion; did not sign off on the deferral of cross-layer
  reconciliation. The cross-layer gap subsequently broke during
  phase 2; see [[2026-05-06-meeting-incident-postmortem-analysis]].

## Date

- Decided: 2026-04-22.
- First execution (phase 0): 2026-04-23.
- Phase-2 rollback: 2026-05-04.

## Status

**Active, with phase-2 in rollback.** The decision itself is not
superseded; the rollout is paused pending cross-layer
reconciliation work scheduled to complete on or around
2026-05-20. The status will tick back to "active, phase 2
resumed" if and when phase 2 re-promotes successfully.

If a future ADR meaningfully revises the rollout shape (e.g.
adopts a different routing-layer architecture, or formalises CS
veto-power per [[should-we-revisit-cs-veto-power]]), update this
page's `status` to `deprecated` and prepend a
`> Superseded by [[…]]` line.

## Cross-references

- [[2026-04-22-decision-microservices-split]] — the raw ADR doc.
- [[2026-04-22-decision-microservices-split-analysis]] — analysis
  of the ADR.
- [[2026-05-06-meeting-incident-postmortem-analysis]] — analysis
  of the phase-2 incident; demonstrates the decision's residual
  risk landing.
- [[q2-platform-migration]] — the project this decision moves
  forward.
- [[q2-platform-arc-may]] — narrative synthesis across the arc.
- [[decision-delay-from-skipped-stakeholder]] — the pattern this
  decision exemplifies on the under-empowered-stakeholder axis.
