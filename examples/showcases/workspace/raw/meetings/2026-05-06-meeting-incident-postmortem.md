# Postmortem — webhook delivery incident 2026-05-04

> **Note for readers of the template.** This file is a *synthesised
> stand-in* for an incident postmortem. All people, teams, services,
> and incident details are fictional. It exists to demonstrate the
> `workspace` L2 ingest flow against a multi-stakeholder
> postmortem. Replace with your own raws when adopting.

**Date:** 2026-05-06, 14:00–15:30 PT
**Location:** Hybrid
**Scribe:** Tom Becker
**Recording:** internal-only

## Attendees
- Maya Chen — Platform team lead
- Devon Park — Product lead
- Priya Shah — Senior engineer, Platform
- Tom Becker — SRE lead
- Alex Rivera — Customer Success
- Jordan Liu — On-call SRE during the incident
- Sam Okafor — Customer Success, account manager for two affected
  enterprise customers

## Incident summary

On 2026-05-04 between 09:14 UTC and 23:08 UTC (~14 hours),
approximately **3.2% of webhook delivery requests** received by the
new routing layer were acknowledged with 202 to the calling code
path but never enqueued for the worker pool. No delivery attempt
was made for those requests. Total estimated affected deliveries:
**~1.7M**, distributed across roughly 8% of customer endpoints; two
enterprise accounts under contractual SLA were impacted.

The incident occurred during phase 2 of the ADR-001 rollout (10%
traffic on new routing layer). Phase 2 had been live for 6 days
before the incident.

---

**[14:02] Tom:** Welcome. Standard blameless postmortem rules.
Timeline first, then root cause, then mitigations, then process
review. Jordan, walk us through the on-call sequence.

**[14:03] Jordan:** Page came in at 23:08 UTC on 2026-05-04 from
Sam — three customer complaint tickets in the same hour about
missing webhook deliveries. I checked the routing-layer dashboard:
queue-depth assertion was clean. Acknowledgement rate normal.
Worker pool delivery rate normal. Everything green.

**[14:05] Jordan:** I escalated to Priya around 23:30. We started
diffing customer-side delivery logs against our acknowledgement
logs. By 00:45 UTC on 2026-05-05 we'd confirmed: the routing layer
had `request_received` events for deliveries the worker pool had
no record of. The 202s were being sent, the enqueue was not
happening, and the queue-depth assertion was not firing.

**[14:08] Priya:** Right. So the assertion logic was: "if the
routing layer accepts a request and the local enqueue function
returns success, but the queue depth doesn't increase within 30
seconds, fire." The bug was in the second condition. The routing
layer talks to a sharded queue; the assertion was checking
*global* queue depth as a proxy, which is dominated by the 90% of
traffic still on the monolith's path. A 3% drop on the 10% new-
path traffic is well under the noise floor of global queue depth.
So the assertion never fired.

**[14:11] Maya:** The cross-layer reconciliation gap we flagged in
the ADR.

**[14:11] Alex:** Yeah. Sorry to be the one to say this, but
this is exactly the failure mode I described on 2026-04-08 and
that I flagged again in my partial sign-off on ADR-001. The
routing layer is acknowledging without enqueueing, and the local
assertion is structurally unable to see it because of the sharding.
The enterprise account I was worried about — Northbridge — is one
of the two affected.

**[14:13] Tom:** That's a fair statement and it's important for
the record. The ADR explicitly accepted "cross-layer
reconciliation" as a residual risk to be addressed in phase-2
follow-up monitoring. Phase 2 is exactly where we are. The
follow-up work was scheduled but not delivered before the
incident.

**[14:14] Devon:** Why wasn't it delivered?

**[14:14] Priya:** It was on the backlog under "phase-2
follow-up monitoring" but it didn't have an owner or a date.
When phase 2 went live, the assumption was that the routing-
layer-local assertion would catch the cases that mattered for the
first week of phase 2, and we'd build the cross-layer
reconciliation in parallel. The local assertion's blind spot
wasn't recognised until the incident.

**[14:17] Maya:** Owning that. It was my call to ship phase 2
without the cross-layer monitoring in place. I weighed it as low-
probability based on the shadow data, and I didn't fully
internalise that the shadow data couldn't tell us about this
specific failure mode either — because shadow mode also doesn't
exercise the actual customer endpoint, so a silent drop in shadow
looks identical to a success.

**[14:20] Alex:** I want to be careful here because I don't want
this to become "Alex was right." That's not useful. The useful
question is: at the planning stage, when I raised the concern,
what would have made the team treat it as P0 instead of as P1?
Because I did flag it specifically, I did get the local assertion
out of the ADR, and the cross-layer gap was acknowledged in
writing — and it still happened.

**[14:22] Devon:** I'll take that one. I think the answer is:
when CS flags an SLA-exposure failure mode, the default should be
that mitigations are blocking, not deferrable. The ADR did the
right thing by writing it down, and the wrong thing by not
turning it into a phase-1 prerequisite.

**[14:25] Tom:** Action item — Devon, you and I draft a one-pager
on "when CS-flagged risks block a phase gate" before the next
ADR cycle.

**[14:26] Maya:** I want to add: the rollback plan worked, which
is the one thing that went right. We rolled phase 2 back to 0%
new-routing-layer traffic in 18 minutes from when we confirmed
root cause. The session-state dual-write was unaffected because
the incident was webhook-only.

**[14:28] Alex:** Confirmed from CS side — Sam, you want to take
this?

**[14:28] Sam:** Yes. Both Northbridge and the other enterprise
account, Riverdale, have been notified. Northbridge is asking
for a written postmortem; we're sending the customer-facing
version by 2026-05-08. Their SLA includes a service credit
clause that triggers automatically at >0.5% monthly delivery loss
— they're at 0.71% for May so far, so credits will issue.
Riverdale is at 0.18% and is below the contractual trigger but
above their internal threshold; they want assurances about
phase-3 rollout before we proceed.

**[14:32] Devon:** What's Riverdale specifically asking for?

**[14:32] Sam:** A formal sign-off process where CS has veto power
on phase progression, not just review power. They've been clear
that "we flagged it and got documented agreement that we were
flagging it" is not adequate from their side.

**[14:34] Alex:** This connects to the question I had on the
ADR — whether CS sign-off should be partial-approve-able or
blocking. I partial-approved ADR-001 because I didn't want to
block a decision the rest of the room had aligned on. I'm
revisiting whether that was the right call.

**[14:36] Maya:** That's the conversation we need to have but
maybe not in this room today. We have a postmortem to finish.

**[14:37] Devon:** Agreed, parking. Tom, take the action item to
schedule a follow-up specifically on CS sign-off authority.

## Root cause

The routing layer's queue-depth assertion was structurally unable
to detect silent acceptance-without-enqueue under sharded traffic
at <10% rollout. The cross-layer reconciliation that would have
caught it was acknowledged as a residual risk in ADR-001 but
deferred to phase-2 follow-up work which was not delivered before
phase 2 went live.

The concern was raised explicitly at the 2026-04-08 planning
meeting by Alex Rivera, addressed partially in ADR-001 via the
local assertion, and the unaddressed portion was the one that
broke.

## Action items
- **Tom & Devon** — Draft "blocking risks vs deferrable risks"
  one-pager for CS-flagged SLA exposures. Due 2026-05-13.
- **Priya** — Implement cross-layer reconciliation between
  routing-layer acknowledgements and worker-pool delivery
  attempts. **Blocking phase 3.** Due 2026-05-20.
- **Maya** — Send postmortem to Northbridge and Riverdale by
  2026-05-08.
- **Sam** — Schedule follow-up with Riverdale on phase-3
  conditions.
- **Tom** — Schedule meeting on CS sign-off authority (separate
  agenda). Due 2026-05-11.
- **Maya & Alex** — Joint review of ADR-001 partial-sign-off
  process; produce a recommendation for ADR-002 and beyond. Due
  2026-05-15.

## Process review

The team did three things right:
- Phased rollout meant 10% traffic, not 100%. The blast radius
  was bounded.
- Rollback plan worked exactly as written; mean time to
  remediate was 18 minutes after root cause.
- The shadow-mode period correctly validated what it could
  validate. Its limits were not the team's fault; its limits
  were the design's.

The team did one thing wrong: it treated "acknowledged residual
risk" as adequate process when the residual risk was load-bearing.
The ADR's documentation discipline was good. The follow-through on
the documented gap was not.
