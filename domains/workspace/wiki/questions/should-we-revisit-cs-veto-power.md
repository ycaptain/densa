---
type: question
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-05-06-meeting-incident-postmortem]]", "[[2026-04-22-decision-microservices-split]]"]
tags: [process, customer-success, sign-off-authority, sla-exposure]
aliases: ["CS veto power", "partial sign-off authority"]
status: active
compiled_against: 1
arc_status: open
first_asked: 2026-05-06
---

# Should Customer Success hold blocking veto on SLA-exposing decisions?

## Question statement

When a Customer Success representative reviews a decision
document for a surface that touches a contractual customer SLA,
should their sign-off authority be:

- **(a)** advisory (current de facto state),
- **(b)** named reviewer with documented partial-approval rights
  (current de jure state per ADR-001), or
- **(c)** blocking veto on phase progression for the specific
  SLA-exposing surface?

The question generalises beyond CS to "stakeholders representing
external-contractual exposure" but originates in CS — see
[[stakeholder-alex-cs]] and [[microservices-split]].

## Why this is open

The 2026-05-04 incident demonstrated that named-reviewer status
with partial-approval rights was sufficient to *document* a
load-bearing residual risk but insufficient to *block* the
rollout phase where the risk landed. See
[[2026-05-06-meeting-incident-postmortem-analysis]] (~14:32 and
~14:34 on the raw) and the [[decision-delay-from-skipped-stakeholder]]
pattern for the structural argument.

The Riverdale enterprise customer is, as of 2026-05-06,
explicitly asking the team to adopt option (c) for phase-3
progression on the current rollout. The team has not yet formed
a position.

## Evidence so far

| Date       | Source                                                          | Bearing                                                                                                                          |
| ---------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 2026-04-08 | [[2026-04-08-meeting-q2-planning-analysis]]                     | First instance of the question's surface — Alex requests named-reviewer status, not blocking authority, and is granted it       |
| 2026-04-22 | [[2026-04-22-decision-microservices-split-analysis]]            | Partial sign-off exercised but undefined process semantics noted in the analysis                                                 |
| 2026-05-06 | [[2026-05-06-meeting-incident-postmortem-analysis]]             | Alex revisits whether partial sign-off was the right call; Riverdale formally asks for option (c)                                |

## Open sub-questions

- **Sub-question 1: Generalisation.** Does the proposed authority
  shift apply only to CS, or to any stakeholder representing
  external-contractual exposure? Argument for narrow: CS owns the
  contractual surface; nobody else does. Argument for broad: the
  pattern in [[decision-delay-from-skipped-stakeholder]] is not
  about CS specifically — it is about external-contractual
  stakeholders generally, and Security / Legal could land in the
  same shape.
- **Sub-question 2: Surface scoping.** If option (c) is adopted,
  on which surfaces? Argument for broad (any SLA-exposing
  surface): incidents tend to land precisely on the surfaces the
  representing stakeholder warned about. Argument for narrow
  (surfaces above a contractual loss threshold): broader scoping
  risks veto fatigue.
- **Sub-question 3: Process design.** If option (c) is adopted,
  what is the appeal process when the proposing team disagrees
  with a veto? Argument for an appeal layer: a CS veto on
  every platform decision would grind throughput to a halt.
  Argument against: appeals re-introduce the failure mode the
  veto was supposed to prevent.
- **Sub-question 4: Trade-off with delivery velocity.** What is
  the steady-state cost of option (c) in terms of phase-gate
  latency? Tom and Devon's "blocking risks vs deferrable risks"
  one-pager (due 2026-05-13) is partly intended to address this.

## What would resolve this question

- **At least one independent instance** of the
  [[decision-delay-from-skipped-stakeholder]] pattern in a
  different domain (e.g. Security, Legal) would harden the
  argument for the broader version of option (c).
- The Tom & Devon one-pager (due 2026-05-13) is the first
  process artifact that could move this question from open to
  partial.
- Empirical: if phase 3 of [[q2-platform-migration]] proceeds
  under the *new* arrangement (whatever it ends up being) and
  ships without an SLA incident, that's weak evidence the
  arrangement is adequate.

## Cross-references

- [[stakeholder-alex-cs]] — the stakeholder whose process
  experience opens the question.
- [[microservices-split]] — the decision whose partial-sign-off
  exposed the gap.
- [[decision-delay-from-skipped-stakeholder]] — the pattern the
  question feeds back into.
- [[q2-platform-arc-may]] — narrative context.
- [[team-platform]] — the team on the other side of the
  question.
