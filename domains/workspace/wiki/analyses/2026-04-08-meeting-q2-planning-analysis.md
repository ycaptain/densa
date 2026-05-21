---
type: analysis
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-04-08-meeting-q2-planning]]"]
tags: [q2-platform-migration, planning, webhooks, identity-service]
aliases: []
status: active
compiled_against: 1
raw_type: meeting
meeting_date: 2026-04-08
---

# Q2 platform planning — analysis

## Context

First scoping meeting of the Q2 platform-migration arc (see
[[q2-platform-migration]]). The Platform team enters the room with
a fully formed proposal — extract `identity` and `webhooks` from
the monolith — and a target ADR date two weeks out. Product is
sympathetic; SRE is in favour; engineering has prototyped the
hardest part (session-state dual-write) on staging. The risk
surface from the platform side is well-mapped on entry.

The room contains exactly one stakeholder whose risk surface is
**not** captured by the platform side's prep: [[stakeholder-alex-cs]],
representing enterprise customers with contractual webhook
delivery SLAs. Alex's concern dominates the second half of the
meeting and reshapes the proposal from a 4-phase rollout into a
5-phase rollout with a shadow-mode prerequisite.

## Key claims

- **Maya** (Platform lead): the deploy queue is the single biggest
  source of friction; identity and webhooks are the two cleanest
  bounded contexts to extract first. Q3 deploy-frequency target
  2–3×.
- **Tom** (SRE lead): the dual-running migration window is the
  fragile surface; rollback must be a runbook with state
  reconciliation, not a deploy revert.
- **Alex** (Customer Success): two enterprise accounts carry
  contractual <0.1% delivery-loss SLAs; the load-bearing failure
  mode is *silent acceptance* — the routing layer returns 202 but
  never hands off to the worker pool. Retry logic does not catch
  this because no failure signal is emitted.

## Tensions surfaced

- **Tom vs Alex on retry-logic adequacy** (~10:18). Tom: "the
  retry logic should catch that." Alex: "retry-on-failure only
  works if the request *fails*." Resolution: Maya commits to
  adding a queue-depth assertion specifically for the silent-
  acceptance case.
- **Phase boundaries vs SLA exposure**. Alex pushes for shadow
  mode + zero-tolerance for silent-drop incidents as cutover
  prerequisites, not as monitoring goals. The team accepts.
- **Reviewer authority vs reviewer-as-cc**. Alex explicitly asks
  to be a named reviewer on the ADR's webhook section, not on
  cc. Maya accepts immediately; no pushback. This is recorded
  here because the postmortem six weeks later (see
  [[2026-05-06-meeting-incident-postmortem-analysis]]) revisits
  whether *named-reviewer* status was sufficient authority for
  the SLA-exposure risk Alex was representing.

## Decisions deferred

No final decision in this meeting. The decision to proceed with
the split is deferred to the ADR review on or before 2026-04-22
(see [[2026-04-22-decision-microservices-split-analysis]]). What
*was* decided here are the constraints the ADR must satisfy:

- Phased rollout, hard gates between phases.
- Shadow mode on the webhook routing layer ≥ 2 weeks before any
  traffic shift.
- Rollback plan as a runbook with state reconciliation.
- Queue-depth assertion at the routing layer for the silent-
  acceptance case.

## Action items

- Maya — Draft ADR-001 by 2026-04-18.
- Priya — Validate session-state dual-write on staging at
  production-equivalent load by 2026-04-17.
- Tom — Define rollback runbook structure by 2026-04-18.
- Alex — Reviewer on ADR-001 webhook section; sign-off required
  before cutover.

## Cross-references

- [[q2-platform-migration]] — the project this meeting opens.
- [[stakeholder-alex-cs]] — the stakeholder whose concern dominates
  the second half and shapes the rest of the arc.
- [[team-platform]] — the team proposing the split.
- [[microservices-split]] — the canonical decision page that
  ADR-001 will populate.
- [[2026-04-22-decision-microservices-split-analysis]] — next page
  in the causal arc.
- [[decision-delay-from-skipped-stakeholder]] — the pattern this
  meeting *almost* avoids by bringing CS into the room early, and
  that the postmortem will eventually re-validate as a near-miss
  (the structural mitigation surfaced here was the right one;
  the follow-through gap is what later breaks).

## Notes

This meeting is the **best-behaviour** anchor of the arc — the
stakeholder with the load-bearing concern is in the room, gets
floor time, gets named-reviewer status, and reshapes the
proposal. Six weeks later the postmortem will surface that
named-reviewer status was not actually sufficient authority for
the residual risk that broke. The lesson is not "Alex was right";
the lesson is that *being in the room and getting documented
agreement on a residual risk is not the same as that risk being
treated as blocking*.
