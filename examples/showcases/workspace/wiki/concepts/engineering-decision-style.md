---
type: concept
kind: pattern
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-13-meeting-api-style-decision]]", "[[2026-05-19-meeting-vector-db-selection]]"]
tags: [pattern, decision-process, positive-pattern, cross-team]
aliases: ["healthy engineering-decision meeting", "decision-shape positive pattern"]
status: active
compiled_against: 2
first_observed: 2026-05-13
instances_count: 2
migration_history:
  - from: 1
    to: 2
    on: 2026-05-26
    mode: in-place
    notes: 'type pattern → concept'
---

# Engineering decision style (positive pattern)

> [!important]
> **This is a *positive* pattern.** Most workspace patterns track
> failure modes (e.g. [[decision-delay-from-skipped-stakeholder]]).
> This one tracks a workflow shape that is **working well** — what
> the team's healthy decision-making meetings look like, so the
> team can recognise and reproduce the shape on subsequent
> decisions. Positive patterns are first-class in this L2.

## Pattern description

A recurring six-step shape across the team's decision meetings,
observed across at least two domains (API design + ML
infrastructure) and two teams ([[team-api-platform]] +
[[team-ml-platform]]). The shape is:

1. **Pre-read with a fully-derived trade-off matrix.** The convener
   distributes a 6-8 page memo containing the problem statement, the
   options, and a multi-dimensional trade-off matrix populated with
   numbers (benchmarks, costs, eng-week estimates). The meeting
   starts from the matrix, not from a blank page.
2. **Constraints declared in priority order, with priority itself
   open to challenge.** The convener names 4-6 constraints and ranks
   them. The Product representative (or another non-engineering
   stakeholder) is invited to challenge the prioritisation at the
   start of the meeting before any option is discussed.
3. **Meeting time spent on stress-testing, not re-deriving.** The
   convener's job in the meeting is to defend the recommendation
   against load-bearing objections, not to re-walk the matrix. If
   the meeting spends >30% of its time on "let me explain option
   B...", something failed in the pre-read.
4. **Cross-team dependency owners in the room as constraint-owners,
   not as reviewers.** The other teams' representatives are present
   not to approve the decision but to bring their team's constraint
   into the decision. Their interventions are *constraint
   contributions*, not *vetoes*.
5. **Exit triggers / migration triggers named before the decision
   is signed.** The convener names ≥3 specific, measurable
   conditions that would cause the team to revisit. Each trigger
   has a direction (which option to consider on trigger) and a
   threshold (the measurable condition).
6. **Owner + due-date on every action item, including residual-
   risk mitigations.** No action item leaves the room without a
   named owner and a date; no residual risk leaves the room
   without being either accepted explicitly (in the at-a-glance
   "Residual risks accepted" row) or assigned a mitigation owner
   + date. This is the step whose absence
   [[decision-delay-from-skipped-stakeholder]] catches.

## Mechanism (why does this shape work?)

The shape collapses three failure modes other decision-meeting
styles routinely hit:

- **"We didn't have the numbers" loop.** Step 1's pre-read with
  benchmark numbers means nobody can derail the meeting with "but
  what about latency?" — the answer is in the matrix.
- **"Engineering decided in private" loop.** Step 2's constraint-
  prioritisation challenge at the start invites the non-engineering
  perspective before any technical advocacy has staked positions.
- **"The follow-up never landed" loop.** Steps 5 + 6 together close
  the workflow seam: residual risks become either accepted (and
  named on the record) or scheduled work (with owner + date).
  This is the step the
  [[decision-delay-from-skipped-stakeholder]] pattern's first
  instance specifically failed.

The shape's robustness comes from the **redundancy across steps**.
Even if step 5 (exit triggers) is weak, step 6 catches it; even if
step 2 (priority challenge) is skipped, step 4 (constraint-owners)
brings the missing perspective in.

## Instances

| Date         | Project                              | Raw                                                                     | Manifestation                                                                                                                       |
| ------------ | ------------------------------------ | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 2026-05-13   | [[api-platform-evolution]]           | [[2026-05-13-meeting-api-style-decision]]                               | API style for the new identity service (4 options, 60+ partner stakes). All six steps present; particularly clean step 5 (3 named triggers) and step 4 (Inez + Bram in the room as constraint-owners, not approvers) |
| 2026-05-19   | [[data-platform-vector-search]]      | [[2026-05-19-meeting-vector-db-selection]]                              | Vector DB v1 selection (3 options, 12M-vector launch corpus). All six steps present; particularly clean step 6 (owner + date on every action item, including per-tenant tuning ownership for Yuki) |

## Predictors (when does the pattern reproduce?)

(Tentative until a third independent instance corroborates beyond
the API + Vector DB pair.)

- **The decision involves a vendor / framework / architecture
  choice with non-trivial reversibility cost.** Trivial decisions
  don't warrant the pre-read effort; deeply load-bearing decisions
  trigger the discipline.
- **At least one external-contractual stakeholder is implicated.**
  Bram for API, Devon's enterprise-sales lens for Vector DB. The
  external surface seems to be what triggers the step 2 priority
  challenge.
- **A previous failure in the team's recent memory.** The 2026-05-04
  incident was 9-15 days before both decision meetings; multiple
  speakers in the vector DB meeting referenced "phase 2 incident"
  explicitly when arguing for ops simplicity. The recent failure
  appears to lower the threshold for steps 5-6 discipline.

## Counter-instances / near-misses

- **[[2026-04-22-decision-microservices-split]] (ADR-001)** is a
  **partial-instance / near-miss**. Steps 1-4 are present in
  exemplary form: pre-read, priority-ordered constraints, Alex
  ([[stakeholder-alex-cs]]) in the room as constraint-owner for
  enterprise SLA exposure, meeting spent on stress-testing. Step 5
  (exit triggers) was weak — the ADR named phase gates but did
  not name explicit "if X then revisit option Y" triggers. Step 6
  failed on the residual cross-layer-reconciliation risk: the
  risk was acknowledged in writing but lacked owner + date. The
  resulting incident is documented in
  [[2026-05-06-meeting-incident-postmortem-summary]] and the
  pattern catching the failure is
  [[decision-delay-from-skipped-stakeholder]].

  The contrast between ADR-001 and the two full-instance decisions
  is the central teaching observation of
  [[engineering-decisions-retrospective-may-2026]].

- **Hyper-local sync decisions** ("we'll rename this variable in
  the next sprint") do not exhibit the pattern and should not be
  forced into it. The pattern's overhead is well-suited to
  decisions with ≥4-week downstream consequences; smaller decisions
  benefit from looser process.

## What might un-do the pattern

(Speculative; logged as input to ongoing process design rather than
as predictions.)

- **Time pressure that collapses pre-read effort.** If the convener
  doesn't have the calendar slack to write the trade-off matrix
  before the meeting, the meeting becomes "let's whiteboard the
  options", which routinely lands without steps 5-6.
- **Single-team decisions without cross-team constraint-owners
  present.** Without step 4, step 2's priority challenge loses
  texture; the convener's priorities go un-stressed.
- **Tooling regression on action-item tracking.** Steps 5-6's
  effectiveness depends on action items being trackable post-
  meeting. If the team's action-item tooling becomes unreliable,
  step 6 silently regresses.

## Cross-references

- [[2026-05-13-meeting-api-style-decision-summary]],
  [[2026-05-19-meeting-vector-db-selection-summary]] — the two
  full-instance analyses.
- [[2026-04-22-decision-microservices-split-summary]] — the
  partial-instance / near-miss analysis.
- [[decision-delay-from-skipped-stakeholder]] — the negative
  pattern whose failure mode this pattern's step 6 specifically
  prevents.
- [[engineering-decisions-retrospective-may-2026]] — synthesis
  braiding all three decision instances.
- [[team-api-platform]], [[team-ml-platform]] — the two teams that
  produced the full instances.
- [[stakeholder-marcus-api]], [[stakeholder-hiro-ml]] — the two
  decision owners who exhibited the pattern.
