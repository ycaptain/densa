# Q2 platform planning — meeting notes

> **Note for readers of the template.** This file is a *synthesised
> stand-in* for a real meeting transcript. All people, teams,
> tickets, and decisions are fictional. It exists to demonstrate
> the `workspace` L2 ingest flow against a multi-stakeholder
> planning meeting. Replace with your own raws when adopting.

**Date:** 2026-04-08, 10:00–11:20 PT
**Location:** Hybrid (Maya, Devon, Priya in-room; Alex, Tom remote)
**Scribe:** Devon Park
**Recording:** internal-only, transcribed by ASR + light human cleanup

## Attendees
- Maya Chen — Platform team lead
- Devon Park — Product lead
- Priya Shah — Senior engineer, Platform
- Tom Becker — SRE lead
- Alex Rivera — Customer Success, accounts >$500k ARR

## Agenda
1. Platform team's Q2 proposal: monolith → microservices split
2. Risk surface review
3. Decide whether to formalise an ADR by 2026-04-22

---

**[10:02] Maya:** Thanks for making time. The deck I sent yesterday
covers the case for the split. Quick recap: the deploy queue is now
the bottleneck — we ship maybe twice a week because every change
ships everything. We've identified four bounded contexts —
identity, billing, content, and webhooks — that could live as
independent services. We want Q2 to be the carve-out of the first
two: identity and webhooks.

**[10:05] Devon:** What's the customer-visible upside?

**[10:05] Maya:** Honestly, none in Q2. Q2 is plumbing. Q3 is where
we start shipping faster — we estimate 2–3× deploy frequency by end
of Q3 if Q2 lands clean.

**[10:07] Tom:** From the SRE side I'm in favour. The current
deploy story is the single biggest source of weekend pages. The
risk I see is the dual-running period — while we're migrating, we
have both the monolith and the new services live at the same time.
That's a fragile window.

**[10:09] Priya:** We've prototyped the dual-write for identity. It
works on staging. Session state is the gnarly part — the monolith
holds it in a Redis cluster, the new service wants Postgres. We
have a migration plan that does dual-write for two weeks, reads
from new, falls back to old.

**[10:11] Devon:** Sounds like identity is well-scoped. What about
webhooks?

**[10:12] Maya:** Webhooks are simpler in code but trickier in
delivery semantics. We deliver about 40M webhooks a day to
customer endpoints. The split means a new routing layer in front
of the existing delivery worker pool.

**[10:14] Alex:** Can I jump in here? I want to flag something
specific about webhooks. Half my book of business — the enterprise
accounts — has SLAs around webhook delivery. Two of them have
contractual commitments to <0.1% delivery loss per month.

**[10:15] Maya:** Right, and the new routing layer doesn't change
delivery guarantees. The worker pool is the same.

**[10:16] Alex:** I hear that. My concern is the seam. During the
cutover, when traffic shifts from the monolith's webhook path to
the new routing layer's path, what happens to in-flight
deliveries? And specifically — and this is the one that keeps me
up at night — what happens if the routing layer accepts a
delivery request, returns 202 to the caller, and then fails to
hand it off to the worker pool? We've had two near-misses last
year where the monolith's internal queue spilled and we found out
from customer complaints, not from monitoring.

**[10:18] Tom:** The retry logic should catch that. The worker pool
retries with exponential backoff for 24 hours.

**[10:18] Alex:** Right, but retry-on-failure only works if the
request *fails*. My worry is the silent acceptance case. The
routing layer says "yes I have it" and then the request never
lands in a queue anyone is watching. There's no failure signal,
so there's no retry.

**[10:20] Maya:** That's a fair point. We have a generic
"in-flight" metric but it's not delivery-attempt-level. I think we
can build a queue-depth assertion at the routing layer that fires
if the layer accepts but doesn't enqueue within N seconds.

**[10:21] Alex:** I'd want to see that as a P0 in the design, not
a phase-2 follow-up. Even one hour of silent drops on a 40M/day
volume hits the SLA on two enterprise accounts.

**[10:22] Devon:** Maya, can you take that as an action item?

**[10:22] Maya:** Yeah, we'll come back with a phased rollout plan
that addresses the seam specifically. We were already planning
phased — what we need is to enumerate the failure modes during
each phase and what monitoring catches each.

**[10:25] Priya:** One option: shadow-mode the routing layer for
two weeks before any traffic shifts. We'd see exactly how often
the accept-without-enqueue case happens under real load, and we
can fix it before customer traffic touches the new path.

**[10:26] Alex:** That would help a lot. But I want to be clear
— if we get to cutover and the shadow data shows even one
silent-drop incident, we don't cut over, we fix it. I'm not
willing to accept "we'll watch it carefully" as the mitigation.

**[10:28] Tom:** I think that's reasonable. From the SRE side I'd
add: the rollback plan needs to be specific. "Roll back the
deploy" isn't enough if we've already started dual-writing
session state, because the data layer might have diverged.

**[10:30] Maya:** Agreed. We'll write the rollback as a runbook
with step-by-step state reconciliation, not just `kubectl
rollout undo`.

**[10:32] Devon:** Anything else from the room?

**[10:33] Priya:** Just timing. If we want to formalise by
2026-04-22 we need the design doc by 2026-04-18. That's tight but
doable.

**[10:34] Alex:** I'd like to be a reviewer on the ADR specifically
for the webhook section. Even if you put me on cc, I want my name
on the review.

**[10:35] Maya:** Yes, absolutely. I'll send the draft to you,
Tom, and Devon by EOD 2026-04-18.

## Decisions taken
- None yet. Decision to proceed with split deferred to ADR review
  on or before 2026-04-22.

## Action items
- **Maya** — Draft ADR-001 covering identity + webhook split, with
  phased rollout, failure-mode table, and step-by-step rollback
  runbook. Due 2026-04-18.
- **Maya** — Include shadow-mode for the webhook routing layer (≥2
  weeks) as a P0 line item.
- **Priya** — Validate session-state dual-write performance on
  staging at production-equivalent load. Due 2026-04-17.
- **Tom** — Define rollback runbook structure (state
  reconciliation, not just deploy rollback). Due 2026-04-18.
- **Alex** — Reviewer on ADR-001 webhook section. Sign-off
  required before cutover, not just before merge.

## Open threads
- Customer-success contractual SLA exposure during cutover — Alex
  flagged but no number quantified yet.
- Q3 follow-on (billing, content services) — out of scope for
  this meeting; revisit after Q2 lands.
