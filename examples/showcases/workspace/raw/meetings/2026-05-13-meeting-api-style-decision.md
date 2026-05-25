# API style decision — identity service public API

> **Note for readers of the template.** This file is a *synthesised
> stand-in* for a real meeting transcript. All people, teams, services,
> and trade-offs are fictional. It exists to demonstrate the
> `workspace` L2 ingest flow against a clean cross-team
> decision-making meeting. Replace with your own raws when adopting.

**Date:** 2026-05-13, 14:00–15:30 PT
**Location:** Hybrid (Maya, Marcus, Inez, Priya in-room; Bram, Devon, Tom remote)
**Scribe:** Priya Shah
**Recording:** internal-only, auto-transcribed + light human cleanup
**Agenda owner:** Marcus Chen (API Platform)

## Attendees
- Maya Chen — Platform team lead
- Marcus Chen — API Platform lead (no relation; gets mistaken on Slack constantly)
- Inez Park — Developer Experience lead (owns SDKs)
- Bram Müller — Partner Engineering lead (owns external integrations)
- Devon Park — Product lead
- Tom Becker — SRE lead
- Priya Shah — Senior engineer, Platform

## Pre-read
- ADR-001 ([[2026-04-22-decision-microservices-split]]) — Q2 identity +
  webhook service extraction. Phase 2 is currently rolled back (see
  [[2026-05-06-meeting-incident-postmortem]]); cross-layer
  reconciliation work due 2026-05-20.
- Marcus's pre-read doc: "Identity service public API — REST vs gRPC
  vs GraphQL, 8-page trade-off matrix."

## Agenda
1. Confirm problem statement and constraints (Marcus, 10 min).
2. Walk the four options and their trade-off matrix (Marcus, 20 min).
3. Cross-team concerns: DX (Inez), partners (Bram), ops (Tom) (30 min).
4. Decide (15 min).
5. Exit criteria + revisit triggers (15 min).

---

**[14:01] Marcus:** Thanks for making time. The identity service has
been on internal-stub APIs through phase 1. We need to commit to a
public API style before phase 2 resumes after cross-layer reconciliation
lands. The pre-read covers the trade-off matrix; today I want to use
the time to land a decision, not re-derive the matrix.

**[14:02] Marcus:** Problem statement, one paragraph: the new identity
service has two consumer classes — internal services (everything else
in our system that needs identity lookups, currently ~14 callers) and
external partners (the 60+ integrations that hit the monolith's
identity endpoints today, plus the SDK paths customers use directly).
The API style we pick has to serve both well; picking one style and
forcing the other to live with it is going to hurt the side we forced.

**[14:04] Marcus:** Constraints — five of them, in priority order:

1. **Backward compatibility for partner integrations.** The 60+
   existing partner integrations are REST-over-HTTPS today. Hard
   constraint: we cannot break them in phase 2.
2. **Internal call latency.** The 14 internal callers do roughly
   8000 RPS in aggregate at peak; current p99 is 22ms over the
   monolith. Soft target: ≤30ms p99 against the new service.
3. **Schema-first contracts.** Whatever style we pick must support
   generated types in our four supported SDK languages (Go, Python,
   TypeScript, Ruby).
4. **Observability parity with REST today.** Distributed tracing,
   per-route metrics, structured request logs. The SRE on-call
   playbook depends on it.
5. **Time-to-market.** We need to ship phase 2 by end-of-Q2; the API
   style decision can't be the gating factor.

**[14:07] Devon:** Confirming I see this list in the pre-read. The
ordering is mine to disagree with if I want — yes? OK. I'd put
backward compat as #1 too. Internal latency at #2 sounds engineering-
opinionated; I'd put time-to-market #2 and treat #2-#4 as engineering
budgets within that.

**[14:08] Marcus:** Fair. Let me reorder: (1) partner backward compat,
(2) time-to-market, (3) internal latency, (4) schema-first contracts,
(5) observability parity. The engineering items are budgets, not
priorities. Sound right?

**[14:09] Devon:** Yes. Continue.

**[14:09] Marcus:** Options on the table — four:

- **(A) REST-only.** Everything REST, internal + external, with
  OpenAPI 3 specs as the contract surface.
- **(B) gRPC-only.** Everything gRPC, internal + external, with a
  REST gateway via grpc-gateway for partner compat.
- **(C) GraphQL gateway.** Single GraphQL endpoint, federation
  internally, REST passthrough at the edge for partners who don't
  want GraphQL.
- **(D) Hybrid: gRPC internal + REST gateway external.** Native gRPC
  for the 14 internal callers, a hand-written REST gateway translating
  to gRPC for the 60+ partner integrations and the SDK surface.

**[14:11] Marcus:** The trade-off matrix is in the pre-read. I'll
summarise the load-bearing cells:

| Dimension | (A) REST | (B) gRPC + gateway | (C) GraphQL | (D) Hybrid |
| --- | --- | --- | --- | --- |
| Partner backward compat | ✅ no change | ⚠️ via gateway | ⚠️ via passthrough | ✅ no change |
| Internal p99 (estimated) | 35-45ms | 8-12ms | 25-35ms | 8-12ms |
| Schema-first SDKs | ✅ OpenAPI | ✅ proto | ✅ SDL | ✅ both |
| SDK code-gen quality | medium | high (Go, TS); lower (Ruby) | medium (TS strong, Ruby weak) | high internal, medium external |
| Observability | ✅ mature | needs work | partial | ✅ on REST surface, needs work on gRPC |
| Engineering-weeks to ship | 3 | 6 (gateway is the cost) | 8 (federation novelty) | 7 (two surfaces) |
| Decision reversibility | high (smaller change) | medium | low (lock-in) | medium |

**[14:14] Maya:** Internal p99 jumping from 22ms to 35-45ms under (A)
— is that real? That's a phase-2-gate failure if so.

**[14:14] Marcus:** It's directional. Our internal calls have a lot
of small payloads; REST's overhead per call costs us. We benchmarked
identity-lookup at production-equivalent shape on the gRPC prototype:
9.2ms p99. Same shape on REST-Native: 38ms p99. Phase-2 gate was ≤30ms
p99 per the ADR's table.

**[14:15] Maya:** So (A) violates the phase-2 latency gate by itself.
That removes (A) from contention before we get to DX or partners.

**[14:16] Marcus:** That's my read too. (A) is on the table for
completeness but its own constraint kicks it out.

**[14:16] Inez:** Want to come in on SDK quality. From DX side, (B)'s
gRPC + grpc-gateway hurts the partner SDKs in a way that's hard to
recover from. We've shipped Python and TypeScript proto-generated
SDKs internally — they're great. Ruby is rough; the maintained
grpc-ruby gem is on a slower release cadence and integration with
common Ruby frameworks isn't first-class.

**[14:17] Inez:** The partner SDK story is the load-bearing one,
though. 60+ partner integrations means 60+ different stacks. They're
running PHP, .NET, Java, Go, Python, Ruby, Node, plus a long tail.
Asking them to switch to gRPC-native clients is a non-starter for
the long tail. They'll stay on the gateway, which means the REST
surface is what their experience is — and a hand-written REST gateway
on top of gRPC tends to leak gRPC concepts (status codes, deadline
metadata) into the REST surface unless we invest serious gateway
discipline.

**[14:19] Bram:** Echoing Inez from the partner side. Two of the
biggest integrations — Northbridge and one I won't name on the
recording because their procurement team will read it — explicitly
told me last quarter that "gRPC" was a red flag because their
security team wasn't familiar with HTTP/2 trailers and proto wire
formats. They'd live with grpc-gateway if it presents as plain REST,
but if they see *any* gRPC concept leak through (Trailer headers,
proto field types as strings, exotic status codes) they'll escalate.

**[14:21] Marcus:** That's option (D)'s pitch — the partner-facing
surface is intentionally a hand-written REST gateway, **not**
grpc-gateway. It's gRPC internally, and the gateway is a thin
hand-coded service that takes REST in, validates inputs against the
REST OpenAPI spec, calls the internal gRPC service, and maps
responses. Partners never see gRPC. Internal services get the latency
win.

**[14:22] Marcus:** Cost: 7 engineering-weeks, ~3 of which are the
gateway. We have to maintain two contracts (OpenAPI for partners,
proto for internal). If they drift, partners see weirdness.

**[14:23] Tom:** SRE concerns on (D). Two surfaces means two sets of
SLOs, two dashboards, two on-call runbooks. Not impossible, but it's
not free. Operationally the worst case is when a problem on the gRPC
side manifests through the gateway as something REST-shaped and we
debug the wrong half for an hour.

**[14:24] Tom:** Manageable if we instrument the gateway with
explicit "REST request <→> internal gRPC call" trace correlation.
But if we cut that corner under time pressure we'll regret it. I'd
make it part of the gate.

**[14:25] Devon:** What about (C)?

**[14:26] Marcus:** (C) GraphQL gateway is the highest-ceiling option
— a single endpoint, partners pick what they want, federation
internally as we add more services. But the engineering cost (8
weeks, novelty risk, federation in production for the first time) and
the partner SDK story (Ruby and PHP GraphQL clients are uneven)
together make it the wrong call for Q2. I think GraphQL is worth
revisiting in Q4 for the analytics surface specifically; not for
identity in Q2.

**[14:28] Devon:** OK. So we're between (B) and (D), realistically.

**[14:28] Bram:** Strongly preferring (D). The hand-written REST
gateway is more work for us, but partners only see REST. With (B),
even with grpc-gateway, the partner SDK quality on the long-tail
languages is going to bleed back into integration tickets that
my team has to resolve.

**[14:29] Inez:** DX side — also (D). The hybrid lets us ship clean
gRPC-native SDKs for the four internal-supported languages (Go,
Python, TypeScript, Ruby — internal Ruby is fine because the few
internal Ruby callers can use our internal proto tooling) and clean
hand-curated REST SDKs (or just leave partners on their own REST
clients) for the external surface. Two surfaces is more work, but
each surface is better than (B)'s gateway-leaking approach.

**[14:31] Maya:** I want to be careful about the cost. 7 weeks is
real. Are we sure (D) hits end-of-Q2?

**[14:32] Marcus:** Tight but doable. The 7 weeks assumes the
cross-layer reconciliation work Priya is doing for webhooks doesn't
bleed into identity engineering — and Priya, you've been on the
critical path of both. What's your read?

**[14:33] Priya:** Cross-layer reconciliation is a 2-week piece of
work, currently at week 1. It's webhook-side, not identity. The
identity team can start on (D) in parallel; the API style decision
isn't blocked on phase-2 resumption.

**[14:35] Devon:** Then let's pick (D). Phased rollout follows the
existing pattern from ADR-001 — internal callers cut over first to
gRPC; the REST gateway then goes live for partners as a flag; once
partner integrations are validated, the monolith's identity
endpoints can decommission.

**[14:36] Maya:** Agreed. Marcus, write this up as ADR-002, similar
shape to ADR-001 — context, decision, rationale, consequences,
rollback. Phase gates with explicit exit criteria.

**[14:37] Marcus:** Will do. Targeting 2026-05-20 for the ADR draft;
review by 2026-05-22.

**[14:38] Tom:** Adding to the gate criteria — the REST↔gRPC trace
correlation I mentioned at 14:24. If that's not built when partners
start hitting the gateway, we will end up with the wrong half of an
incident getting debugged. Make it a phase-1 deliverable.

**[14:39] Marcus:** Adding to the action items.

**[14:40] Devon:** Exit criteria and revisit triggers — what
specifically would make us revisit (D) and consider going back to
(B) or forward to (C)?

**[14:41] Marcus:** Three triggers:

- **Trigger 1 (revisit back toward B):** If maintaining the
  hand-written REST gateway costs >2 engineering-weeks/quarter in
  drift-fixing for two consecutive quarters, the cost of two contracts
  has exceeded our budget. We'd evaluate moving the gateway to
  grpc-gateway with a written acceptance that partners see some
  leakage.
- **Trigger 2 (revisit forward toward C):** If the analytics team's
  Q4 GraphQL gateway lands cleanly and we see ≥3 internal callers
  asking for graph-shaped queries against identity, that's the signal
  to consider federating identity under GraphQL.
- **Trigger 3 (revisit back toward A):** If internal p99 budget is
  not the constraint we thought it was — e.g. the upstream callers
  get aggressively batched and per-call latency stops mattering —
  the case for gRPC weakens. Unlikely but worth naming.

**[14:43] Devon:** Good. Anything else?

**[14:43] Inez:** One small ask — SDK release cadence. With two
surfaces, please commit to releasing internal proto-generated SDK and
external REST SDK on the same cadence so we don't drift. Suggest
biweekly.

**[14:44] Marcus:** Accepted. Biweekly release; if either side
slips, we slip both.

**[14:45] Devon:** Let's wrap. Marcus owns ADR-002, draft by
2026-05-20, review by 2026-05-22. Decision recorded as (D) hybrid:
gRPC internal + hand-written REST gateway external.

## Decisions taken
- **Option (D) hybrid** selected: gRPC native for internal service-
  to-service identity calls; hand-written REST gateway (not
  grpc-gateway) for partner integrations and SDK surfaces.
- **GraphQL deferred to Q4.** Not for identity; revisit for the
  analytics surface where graph-shaped queries are native.

## Action items
- **Marcus** — Draft ADR-002 covering option (D) with phase gates
  and exit criteria. Due 2026-05-20.
- **Marcus** — Spec the REST↔gRPC trace correlation as a phase-1
  deliverable per Tom's 14:24 ask. Include in ADR.
- **Marcus + Inez** — Biweekly SDK release cadence commitment;
  coupled releases (slip both if either slips).
- **Tom** — Define operational dual-surface monitoring posture
  (per-surface SLOs, trace correlation, on-call runbook split).
  Due 2026-05-25.
- **Bram** — Notify the two named partners about the upcoming API
  style; collect any blocking objections before ADR-002 review. Due
  2026-05-20.

## Exit criteria / revisit triggers
Three named triggers (see 14:41) for revisiting the decision:
- gateway maintenance cost > 2 eng-weeks/quarter for two consecutive
  quarters → consider grpc-gateway with acceptance of leakage.
- Q4 GraphQL gateway lands cleanly + ≥3 internal callers want
  graph-shaped queries → consider federating identity under GraphQL.
- Internal p99 budget proves non-binding (aggressive batching changes
  the picture) → reconsider REST-native.

## Open threads
- ADR-002 review (2026-05-22) — needs partner sign-off equivalent to
  Alex's ADR-001 webhook-section sign-off. The partial-sign-off
  process question raised in [[2026-05-06-meeting-incident-postmortem]]
  applies here too; need to land a position before the next ADR
  cycle. Tom's "blocking vs deferrable risks" one-pager (due
  2026-05-13) becomes relevant here.
