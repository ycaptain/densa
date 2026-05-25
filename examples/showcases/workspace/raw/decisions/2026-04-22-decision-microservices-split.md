# ADR-001: Q2 identity + webhook service extraction

> **Note for readers of the template.** This file is a *synthesised
> stand-in* for an Architecture Decision Record. All people, teams,
> services, and trade-offs are fictional. It exists to demonstrate
> the `workspace` L2 ingest flow against a canonical ADR. Replace
> with your own raws when adopting.

**Status:** Accepted
**Date:** 2026-04-22
**Authors:** Maya Chen (Platform)
**Reviewers:** Devon Park (Product), Tom Becker (SRE), Alex Rivera
(Customer Success — webhook section only)
**Supersedes:** none
**Related:** Q2 planning meeting on 2026-04-08

## Context

The monolith's coupled deploy story is the single largest source of
delivery friction for the platform team: shipping changes to any
bounded context requires shipping all of them. The Q2 planning
discussion on 2026-04-08 confirmed broad alignment on extracting
**identity** and **webhooks** as the first two bounded contexts to
move out, with phase-1 cutover targeted for early May 2026.

The discussion surfaced two load-bearing risk areas that this ADR
must address before cutover:

1. **Session-state migration** (Priya, Tom): the monolith stores
   session state in Redis; the new identity service uses Postgres.
   Dual-write window must preserve consistency.
2. **Webhook delivery semantics during cutover** (Alex): the new
   routing layer must not accept delivery requests it cannot
   guarantee to enqueue. Enterprise SLA exposure is non-trivial.

## Decision

Extract `identity` and `webhooks` as independent services behind a
shared ingress, with a phased rollout per the table below.

| Phase | Identity                                | Webhooks                                   | Gate                        |
| ----- | --------------------------------------- | ------------------------------------------ | --------------------------- |
| 0     | Dual-write Redis ↔ Postgres on staging  | Routing layer in shadow mode               | Staging soak ≥7 days clean  |
| 1     | Dual-write live, reads still from Redis | Routing layer shadow on production traffic | ≥14 days, zero silent drops |
| 2     | Reads cut over to Postgres              | 10% traffic to new routing layer           | 7 days, error rate ≤ baseline |
| 3     | Redis decommissioned                    | 100% traffic to new routing layer          | 7-day burn-in               |

Cutover gates are **hard gates**: failure of any gate reverts to the
prior phase and blocks promotion until the failure mode is
remediated.

## Rationale

**Why phased, not big-bang.** The 2026-04-08 discussion converged on
phased as the only acceptable rollout shape given enterprise SLA
exposure. Big-bang was never seriously considered after Alex
quantified the contractual loss-rate cap (<0.1% delivery loss for
two enterprise accounts).

**Why shadow mode before any traffic shift.** Priya proposed it on
2026-04-08; this ADR formalises it as a P0 line item per Maya's
commitment. Shadow exercises the routing layer under real load
without customer exposure.

**Session-state dual-write window.** Priya's staging validation
(2026-04-17) showed dual-write adds 4ms p99 to identity writes,
within budget. The 14-day window is conservative; it can be
shortened if the production dual-write metrics agree with staging
within the first 7 days.

**Webhook silent-drop monitoring.** A queue-depth assertion at the
routing layer fires if the layer acknowledges a delivery request
but does not enqueue within 30 seconds. This is the explicit
mitigation for Alex's concern. **Note:** the assertion runs on the
routing layer's local view; cross-layer reconciliation between
"requests acknowledged" and "deliveries actually attempted by the
worker pool" is deferred to phase-2 follow-up monitoring work. The
working assumption is that the routing layer's local assertion plus
the worker pool's existing retry logic together cover the failure
surface. See Consequences for the residual risk we accept.

## Consequences

**Positive.**
- Deploy frequency target: 2–3× by end of Q3.
- Independent scaling of webhook delivery, which has been the
  monolith's hottest subsystem during peak hours.
- Cleaner bounded-context API for the Q3 follow-on (billing,
  content).

**Negative / residual risks.**
- **Cutover window risk.** Even with phased rollout, the dual-
  running period is the highest-risk surface area in any service
  extraction. SRE on-call rotation is doubled for phases 1–3.
- **Cross-layer reconciliation gap.** As noted above, the
  routing-layer-local assertion does not catch failure modes where
  the routing layer believes it has enqueued and the worker pool
  disagrees. The team's judgement is that the worker pool's retry
  logic plus the local assertion are sufficient for phase 1. Alex's
  original concern (silent-acceptance without enqueue at the
  routing layer) is directly addressed by the local assertion; the
  broader cross-layer reconciliation question is acknowledged as a
  residual gap and scheduled as a phase-2 follow-up.
- **Rollback complexity.** See Rollback plan; the data-layer
  divergence during dual-write means rollback is no longer
  `kubectl rollout undo`.

## Rollback plan

A rollback runbook (Tom, due 2026-04-21) defines the procedure for
each phase:

- **Phase 0–1:** No customer-facing rollback needed; revert the
  feature flag that promotes the new layer's reads, leave the
  dual-write running.
- **Phase 2:** Shift traffic back to 0% on the new routing layer
  (single feature flag flip); session-state reads remain on
  Postgres. SRE re-runs reconciliation script against Redis.
- **Phase 3:** Significantly more involved. Redis has been
  decommissioned by this point. Rollback requires standing Redis
  back up from the most recent snapshot, then running the
  reconciliation script in reverse. **Estimated time to rollback at
  phase 3: 90 minutes minimum.** Tom flagged this as
  uncomfortable; the team accepted the trade-off because the
  burn-in period at phase 3 is intended to be the steady state, not
  a high-risk window.

## Reviewer sign-off

- Devon Park: approved 2026-04-21.
- Tom Becker: approved 2026-04-21, conditional on rollback runbook
  being signed off by SRE on-call lead (which it was, same day).
- Alex Rivera: **partial sign-off on webhook section.** Approved
  the routing-layer-local assertion as the mitigation for the
  acceptance-without-enqueue case; did **not** sign off on the
  decision to defer cross-layer reconciliation to phase-2, but
  did not block the ADR over it. Alex's written comment:
  "Recording this for the postmortem record in case we need it.
  The local assertion is the right mitigation. The cross-layer
  gap is the one I'd push to close before phase 3, not after."

## Next steps

- Phase 0 begins 2026-04-23 (staging).
- Phase 1 (production shadow) targeted for 2026-04-29 pending
  staging soak.
- ADR review revisited if any gate fails or if shadow data shows
  silent-drop incidents.
