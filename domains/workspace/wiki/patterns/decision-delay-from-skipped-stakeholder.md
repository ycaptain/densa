---
type: pattern
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-04-08-meeting-q2-planning]]", "[[2026-05-06-meeting-incident-postmortem]]", "[[2026-04-22-decision-microservices-split]]"]
tags: [pattern, stakeholder-process, sla-exposure, residual-risk]
aliases: ["under-empowered stakeholder", "documented-but-deferred risk"]
status: active
compiled_against: 1
first_observed: 2026-05-06
instances_count: 1
---

# Decision delay from a skipped stakeholder

> [!important]
> This pattern is N=1 at first observation (the Q2 platform
> migration arc) and should be treated as **provisional** until
> at least one independent instance is filed. The `instances_count: 1`
> reflects the single arc currently cited. Predictors and counter-
> instances are tentative until corroborated by a second case.

## Pattern description

A stakeholder with **load-bearing domain knowledge about a
specific failure mode** is *present in the room*, raises the
concern, gets it documented, and gets named-reviewer status on
the resulting decision document — but does **not** get the
authority to make their concern's mitigation a phase-blocking
prerequisite. The decision document acknowledges the concern as
a residual risk, defers the structural mitigation to follow-up
work, and ships. The deferred mitigation does not get an owner
or a date. The failure mode subsequently manifests.

This is **not** a "stakeholder was skipped" pattern in the naive
sense (the stakeholder was in the room). It is a "stakeholder
was structurally under-empowered" pattern — the process gave
them voice without giving them blocking authority on the
specific surface where their domain knowledge was load-bearing.

## Mechanism (hypothesised)

1. A subject-matter stakeholder identifies a failure mode based
   on their direct experience of the affected surface.
2. The proposing team — usually a technical owner — proposes a
   mitigation that addresses the *most legible* form of the
   failure mode.
3. The stakeholder accepts the legible mitigation but flags the
   residual gap. The flag is documented.
4. Because the residual gap is documented, both sides
   experience the workflow as having handled the concern — the
   stakeholder feels heard, the team feels diligent.
5. The documented gap is filed as "follow-up work" without an
   owner or a date. In the gap between "filed" and "delivered",
   the rollout proceeds.
6. The failure mode lands during the gap.

The pattern's force comes from step 4: the **documentation of a
residual risk is mistaken for the mitigation of it**.

## Instances

| Date         | Project                       | Raw                                                                            | Manifestation                                                                                                                  |
| ------------ | ----------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| 2026-04-08   | [[q2-platform-migration]]     | [[2026-04-08-meeting-q2-planning]] (raising)                                   | [[stakeholder-alex-cs]] raises silent-acceptance webhook failure; team accepts shadow mode + local assertion as mitigations    |
| 2026-04-22   | [[q2-platform-migration]]     | [[2026-04-22-decision-microservices-split]] (deferring)                        | ADR-001 documents cross-layer reconciliation as residual risk; partial sign-off; no owner, no date for the follow-up           |
| 2026-05-04   | [[q2-platform-migration]]     | [[2026-05-06-meeting-incident-postmortem]] (landing)                           | Phase-2 incident matches the exact failure mode flagged 26 days earlier; 14h silent-drop window, ~1.7M deliveries affected     |

Treat the three rows above as **one instance of the pattern**,
not three. The pattern's unit is the raising → deferring →
landing arc, which spans three raws.

## Predictors

(Tentative until a second instance corroborates.)

- Stakeholder representing **external-contractual** exposure (vs
  internal trade-offs) — their incentive is to block; the
  proposing team's incentive is to proceed.
- **Asymmetric domain knowledge.** The stakeholder knows the
  failure surface in detail; the team has higher-level confidence
  in adjacent mitigations that don't quite cover the named
  failure.
- The mitigation discussed at the planning stage has a name and
  a delivery shape (here: shadow mode, local assertion); the
  residual gap does not.
- **Partial sign-off accepted without defined semantics.** A
  partial sign-off becomes documentation rather than a process
  state.

## Counter-instances

- **The session-state dual-write surface** in the same ADR did
  *not* exhibit this pattern. Reasons: Priya owned both the
  technical risk and the operational risk; staging validation
  was a phase-0 gate; rollback was specific. No residual gap
  was deferred. Outcome: no incident on the session-state
  surface during phases 0–2.
- This counter-instance suggests the pattern is gated on
  **stakeholder-owner separation** (the stakeholder identifying
  the risk is not the implementer of the mitigation). Where
  identification and implementation collapse into one person,
  the pattern does not manifest.

## What might counter the pattern

(Speculative; logged as input to
[[should-we-revisit-cs-veto-power]] rather than as conclusions.)

- Define partial sign-off semantics explicitly in the ADR
  template — what does partial approval entitle the partial
  signer to?
- Make documented residual risks first-class scheduled work
  (owner + date + phase-gate label) at the moment of
  documentation, not later.
- Promote stakeholders with external-contractual exposure to
  blocking-reviewer authority on the specific surfaces they
  represent, *or* explicitly downgrade them to advisory and
  accept the trade-off on the record.

## Cross-references

- [[stakeholder-alex-cs]] — the instance stakeholder.
- [[microservices-split]] — the instance decision.
- [[q2-platform-arc-may]] — the synthesis narrating the arc.
- [[should-we-revisit-cs-veto-power]] — the open question this
  pattern's mitigation candidates feed into.
