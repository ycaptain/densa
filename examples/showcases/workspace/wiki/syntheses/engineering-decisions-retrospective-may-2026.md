---
type: synthesis
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-04-22-decision-microservices-split]]", "[[2026-05-13-meeting-api-style-decision]]", "[[2026-05-19-meeting-vector-db-selection]]", "[[engineering-decision-style]]", "[[decision-delay-from-skipped-stakeholder]]"]
tags: [synthesis, decision-process, cross-team, retrospective, may-2026, intern-onboarding]
aliases: ["May 2026 engineering decisions retrospective", "How this team makes engineering decisions"]
status: active
compiled_against: 1
---

# Engineering decisions retrospective — May 2026

Cross-team synthesis braiding three decision meetings across three
projects ([[q2-platform-migration]],
[[api-platform-evolution]], [[data-platform-vector-search]]) and
three lead authors ([[team-platform]],
[[stakeholder-marcus-api]], [[stakeholder-hiro-ml]]). Designed as
**intern-onboarding reading** — a newly-joined engineer should be
able to read this single page and walk away with a clear mental
model of how the team makes engineering decisions, what the
recurring patterns are, and which page to deepen on next.

## TL;DR

> [!important]
> Across May 2026, three engineering decisions hit the team's
> decision-making process — ADR-001 microservices split (decided
> 2026-04-22, but executed in May with one significant incident),
> ADR-002 API style for the new identity service (decided
> 2026-05-13), and ADR-003 vector DB for semantic search (decided
> 2026-05-19). All three exhibited most of the team's positive
> [[engineering-decision-style]] pattern. **The single defect in
> ADR-001 — residual risks named without owner + date — produced
> the 2026-05-04 incident.** ADR-002 and ADR-003 closed that defect
> by treating step 5 (exit triggers) and step 6 (owner + date on
> mitigations) as non-skippable. The retrospective's organising
> claim is that the team's *decision-making process* is healthy;
> the **workflow seam at the boundary between "decision documented"
> and "mitigation owned"** is where the bugs land.

## Why this page exists (for the intern)

Most retrospectives compare what went well against what went
wrong. This one compares the **shape** of three decisions that all
mostly worked, to surface the structural difference between the one
that produced an incident and the two that didn't. The hypothesis
underlying the synthesis is that **decision-making competence is a
team capability, not an individual one** — once you can see the
shape of a healthy decision in the team's wiki, you can recognise
when a new decision is missing a step.

Open this synthesis when:
- You are new to the team and want to understand how decisions are
  made here.
- You are convening your first engineering decision and want a
  template to match.
- You are reviewing an ADR draft and want to check the residual-
  risk-ownership step before sign-off.

## The three decisions at a glance

| Dimension                          | ADR-001 (Q2 migration)                                            | ADR-002 (API style)                                                | ADR-003 (Vector DB)                                                |
| ---------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| Project                            | [[q2-platform-migration]]                                         | [[api-platform-evolution]]                                         | [[data-platform-vector-search]]                                    |
| Convener                           | Maya Chen ([[team-platform]])                                     | [[stakeholder-marcus-api]] ([[team-api-platform]])                 | [[stakeholder-hiro-ml]] ([[team-ml-platform]])                     |
| Date decided                       | 2026-04-22                                                        | 2026-05-13                                                         | 2026-05-19                                                         |
| Decision shape                     | extract identity + webhooks, 4-phase rollout                      | option (D) hybrid: gRPC internal + REST gateway external           | pgvector IVFFlat v1, HNSW post-Q3-upgrade                          |
| Load-bearing external stakeholder  | [[stakeholder-alex-cs]] (enterprise SLA)                          | [[stakeholder-bram-partner]] (60+ partner integrations)            | enterprise pre-sales (via Devon)                                   |
| Reversibility                      | partial                                                           | partial                                                            | high                                                               |
| Engineering-decision-style step 1-4 (pre-read, priority, stress-test, constraint-owners) | all present                | all present                                                        | all present                                                        |
| Step 5 (exit triggers)             | weak — phase gates named but no "if X then revisit Y"             | strong — 3 named triggers (B-direction, C-direction, A-direction)  | strong — 5 named triggers                                          |
| Step 6 (owner+date on mitigations) | failed — cross-layer recon had no owner / no date                  | strong — every mitigation has owner + date                         | strong — every mitigation + per-tenant tuning has owner + date     |
| Downstream incident?               | yes — 2026-05-04 incident matched the deferred residual risk      | TBD — ADR-002 review 2026-05-22                                    | TBD — ADR-003 review 2026-05-28                                    |
| Pattern instance                   | [[decision-delay-from-skipped-stakeholder]] (negative, N=1)       | [[engineering-decision-style]] (positive, instance 1 of 2)         | [[engineering-decision-style]] (positive, instance 2 of 2)         |

## The Q2 arc — decision shape vs follow-through

Read the per-arc detail in [[q2-platform-arc-may]]. The short
version: ADR-001 was, by the standards of ADRs, **a good document**.
The 2026-04-08 planning meeting brought
[[stakeholder-alex-cs]] into the room early as a constraint-owner
(step 4); Marcus' pre-read covered options + trade-offs (step 1);
the meeting accepted shape-of-rollout constraints from Alex (step 3
stress-test working); named phase gates (partial step 5).

What ADR-001 didn't do is what
[[engineering-decision-style]]'s step 6 is for: the cross-layer
reconciliation mitigation was acknowledged in writing as a residual
risk and **filed as "phase-2 follow-up monitoring work" without an
owner and without a date**. Three weeks later the failure mode
landed. The
[[decision-delay-from-skipped-stakeholder]] pattern's central
observation is that **documenting a residual risk is not the same
as mitigating it**.

## The May decisions — step 6 as the closing safety net

Both ADR-002 (API style) and ADR-003 (Vector DB) had the
opportunity to make the same kind of mistake and **didn't**. In
ADR-002, the partial-language partner concerns ([[stakeholder-inez-dx]]
on Ruby/PHP SDK quality; [[stakeholder-bram-partner]] on
procurement-security gRPC red flags) could plausibly have been
treated as residual risks deferred to phase-2 SDK quality work —
the same shape as ADR-001's cross-layer reconciliation deferral.
Instead, both concerns were **structurally mitigated as part of
the decision itself**: option (D)'s hand-written REST gateway
adopted *because* of Bram's procurement-security concern; biweekly
coupled SDK release committed *because* of Inez's drift concern.
Step 6 was passed at decision time, not deferred to follow-up.

In ADR-003, the equivalent moment is Priya's "second-most-expensive-
database" framing at ~10:18 — an operability concern that could
have been waved off ("we'll figure out ops") and instead became
the **decisive** input that picked pgvector over Weaviate. Step 6
was passed by accepting an operability constraint as a decision
input, not as a follow-up commitment.

## What changed between ADR-001 and ADR-002/003

The mechanical change is that step 6 stopped being optional. The
**reason** it stopped being optional — to the extent the wiki can
trace this — is a combination of two factors:

1. **The 2026-05-04 incident was recent and visible.** Multiple
   speakers in the May meetings referenced the incident explicitly
   when arguing for tightening process. Priya's "phase-2 incident
   waiting to happen" framing in the vector DB meeting (~10:18)
   is the most legible instance.
2. **Tom and Devon's "blocking risks vs deferrable risks" one-pager**
   was scheduled at the postmortem (due 2026-05-13). The wiki does
   not yet have a copy of this one-pager (it may not exist yet —
   the action item was due *on the day* of the API decision
   meeting). But Marcus and Hiro both treated step 6 as
   non-negotiable in their May meetings, which is the kind of
   downstream effect a well-circulated process artifact produces.

Either way, the shift between ADR-001 and ADR-002/003 is the
single most-teachable transition in the wiki right now. It is the
kind of process-evolution observation that the wiki's
narrative-arc orientation is built to surface.

## What's still open

- **The "blocking vs deferrable risks" one-pager itself** —
  formally due 2026-05-13, may exist as a Slack message or doc not
  yet ingested. If it materialises as a written artifact, ingest
  it (will produce its own analysis page + may promote
  [[engineering-decision-style]] step 6 into a documented team
  norm).
- **CS sign-off authority** is still tracked as
  [[should-we-revisit-cs-veto-power]]. The May decisions did not
  resolve it; they sidestepped it by structurally mitigating the
  concerns at decision time. The question may stay open until the
  next decision that *cannot* sidestep it lands.
- **The [[engineering-decision-style]] pattern is currently N=2.**
  A third independent instance from a fourth team would harden it
  from "two examples" to "team norm". Watch the next quarter's
  major decisions for the shape.

## What this synthesis does NOT claim

- It does not claim Maya, Marcus, or Hiro is a "better" decision-
  maker than the others. The Q2 ADR-001 case demonstrates that
  Maya's decision-making *process* was largely the same shape as
  Marcus' and Hiro's; the difference is in workflow follow-through
  on the residual-risk-ownership step. The team's competence is
  collective, not individual.
- It does not claim that ADR-002 and ADR-003 will not produce
  incidents. They might — for entirely different reasons (the API
  contract drift risk; the filtered-ANN headroom risk). The claim
  is narrower: they will not produce **this particular failure
  mode** because the residual-risk-ownership step caught it.
- It does not claim that step 5 + 6 are the only safety nets that
  matter. Step 4 (cross-team constraint-owners in the room) was
  also present in all three decisions and was load-bearing in
  different ways. The synthesis singles out steps 5-6 because
  they're the ones that distinguished the failing case from the
  succeeding ones.

## Reading order for the intern

1. **Start here** (this page) — get the overall map.
2. **[[q2-platform-arc-may]]** — read the Q2 migration arc in
   detail to see the negative case.
3. **[[engineering-decision-style]]** — read the positive pattern
   page to internalise the six-step shape.
4. **[[2026-05-13-meeting-api-style-decision-analysis]]** —
   open a worked example of the positive pattern and study the
   "Cast and stakes" + "Tensions surfaced" sections in particular.
5. **[[decision-delay-from-skipped-stakeholder]]** — read the
   negative pattern to understand what step 6 prevents.
6. Then drill into individual stakeholder pages
   ([[stakeholder-alex-cs]], [[stakeholder-bram-partner]],
   [[stakeholder-marcus-api]], [[stakeholder-hiro-ml]],
   [[stakeholder-inez-dx]]) and team pages
   ([[team-platform]], [[team-api-platform]],
   [[team-ml-platform]]) to see how individual contributors fit
   into the team's decision-making fabric.

## Cross-references

- [[q2-platform-arc-may]] — the prior single-project arc synthesis
  this cross-arc synthesis builds on.
- [[engineering-decision-style]] — the positive pattern.
- [[decision-delay-from-skipped-stakeholder]] — the negative
  pattern.
- [[should-we-revisit-cs-veto-power]] — the open process
  question that May's decisions sidestepped without closing.
- [[q2-platform-migration]], [[api-platform-evolution]],
  [[data-platform-vector-search]] — the three projects covered.
- All three analyses: [[2026-04-22-decision-microservices-split-analysis]],
  [[2026-05-13-meeting-api-style-decision-analysis]],
  [[2026-05-19-meeting-vector-db-selection-analysis]].
