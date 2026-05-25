# Vector database selection — semantic search v1

> **Note for readers of the template.** This file is a *synthesised
> stand-in* for a real meeting transcript. All people, teams, vendors,
> and numbers are fictional. It exists to demonstrate the `workspace`
> L2 ingest flow against a vendor-selection decision. Replace with
> your own raws when adopting.

**Date:** 2026-05-19, 10:00–11:15 PT
**Location:** Hybrid (Hiro, Priya in-room; Marcus, Devon remote)
**Scribe:** Hiro Tanaka
**Recording:** internal-only
**Agenda owner:** Hiro Tanaka (ML Platform)

## Attendees
- Hiro Tanaka — ML Platform lead
- Marcus Chen — API Platform lead (cross-team; owns the API surface
  that will expose the search endpoint)
- Priya Shah — Senior engineer, Platform (operational perspective)
- Devon Park — Product lead
- Yuki Nakamura — Senior ML engineer (ML Platform; ran the
  benchmarks; speaks once at 10:42)

## Pre-read
- Hiro's 6-page memo: "Vector DB v1 selection — pgvector vs Pinecone
  vs Weaviate, benchmark report + trade-off matrix."
- Benchmark dataset: 12M document embeddings, 1024-dim, real
  customer corpus snapshot from 2026-04-30.

## Agenda
1. Confirm problem statement and constraints (Hiro, 10 min).
2. Walk the three options and benchmark numbers (Hiro, 20 min).
3. Cross-team concerns: API surface (Marcus), ops (Priya), product
   (Devon) (25 min).
4. Decide (15 min).
5. Exit criteria + migration triggers (5 min).

---

**[10:01] Hiro:** Thanks for joining. Goal today is to lock the v1
vector DB so the search team can ship the public beta by end of Q2.
Pre-read covers the trade-off matrix and our benchmark report; I'd
like to use this time to pressure-test the decision, not re-derive it.

**[10:02] Hiro:** Problem statement: semantic search v1 over customer
documents. Index size at launch: ~12M vectors, 1024-dim (matches our
embedding model). Growth: +1M/quarter steady-state, with one
~30M-vector enterprise tenant in pre-sales. Query mix: 90% top-k
ANN, 10% filtered-ANN (metadata pre-filter then ANN). Target latency:
≤150ms p99 single-tenant.

**[10:04] Hiro:** Constraints, priority-ordered:

1. **Ship-by-Q2-end.** Hard deadline; product has commitments to
   the launch partners.
2. **Operability against our existing stack.** Whatever we pick has
   to fit our observability, deploy, and incident-response posture.
3. **Acquisition cost ≤ $50k/year for v1 scale.** Beyond v1 we
   re-evaluate.
4. **Reversibility.** v1 is a v1; we should not lock ourselves out
   of switching at v2 if our needs shift.
5. **Filtered-ANN quality.** The 10% of queries with metadata
   pre-filter matter disproportionately for enterprise tenants
   (compliance scoping).

**[10:07] Devon:** Push back on (3). $50k is tight if we have any
enterprise tenant by Q3. The 30M-vector enterprise in pre-sales is a
$1.2M ACV, and them seeing "we run on managed-cheap-tier" might be
a sales objection. I'd rather (3) be "≤$50k pending enterprise close,
re-budget on close".

**[10:08] Hiro:** Accepted. (3) becomes "v1 cost ≤$50k/year at launch
scale; revisit on enterprise close."

**[10:09] Hiro:** Options:

- **(A) pgvector** on our existing Postgres infrastructure. ANN via
  IVFFlat / HNSW indexes. Self-hosted; same Postgres cluster pattern
  we already run.
- **(B) Pinecone** (managed, vendor SaaS). API-only; no infra to run.
- **(C) Weaviate** (self-hosted open source). Schema-first, built-in
  filters, hybrid sparse + dense search.

**[10:11] Hiro:** Benchmark results — Yuki ran these against the
12M-vector corpus on EC2 c6i.4xlarge equivalents. Headlines:

| Dimension | (A) pgvector | (B) Pinecone | (C) Weaviate |
| --- | --- | --- | --- |
| top-k ANN p99 @ k=20 | 82ms | 38ms | 65ms |
| Filtered-ANN p99 @ k=20 | 145ms | 71ms | 88ms |
| Recall@20 vs ground truth | 0.94 | 0.97 | 0.95 |
| Annual cost @ 12M vectors | ~$18k (existing Postgres incremental) | ~$42k | ~$28k (incl. EC2) |
| Annual cost @ 30M vectors | ~$38k | ~$98k | ~$58k |
| Operability against our stack | ✅ identical | new vendor + SaaS posture | new self-hosted system |
| Reversibility | ✅ high (SQL) | medium (proprietary API) | medium (open source but distinct shape) |
| Time-to-ship | 4 weeks | 2 weeks | 6 weeks |

**[10:14] Hiro:** Important caveat — pgvector's filtered-ANN p99 of
145ms is *barely* inside our 150ms budget, and it gets worse as the
filter selectivity drops. We benchmarked at 50% selective filters; at
10% selective the p99 climbs to 220ms. The 30M-vector pre-sale tenant
will hit harder filter cases.

**[10:16] Priya:** Operations side. (A) is the friendliest by a wide
margin. We already run the Postgres pattern, same backup, same
monitoring, same on-call runbook. (B) is a black box — when it
breaks, we file a ticket with Pinecone and wait. (C) is a new
self-hosted system we'd have to learn to operate; the second
Postgres-like database in our infra is the second-most-expensive
database from an ops perspective (the first being the first).

**[10:18] Priya:** That doesn't mean (B) or (C) are wrong, but the
ops cost of "another system to run" is real and easy to underweight
in a six-month horizon. SRE on-call is already at-budget. A new
self-hosted system without a 6-month onboarding plan is a phase-2
incident waiting to happen.

**[10:20] Marcus:** From the API surface side, I care about contract
stability. All three have reasonable client libraries, and the API
in our service will hide the choice from internal callers. So the
"reversibility" row matters more than the "client library quality"
row, because we *will* reconsider this in 12-18 months as the
enterprise tenant scaling profile clarifies.

**[10:21] Marcus:** (A)'s reversibility is the strongest — vectors
in Postgres are just rows. Migration to anything else is "dump,
re-embed if needed, load". (B) is medium — Pinecone's API is
proprietary but the vectors themselves are exportable; the indexing
config doesn't transfer. (C) is medium for similar reasons.

**[10:23] Devon:** Hiro, what's your recommendation in the pre-read?

**[10:23] Hiro:** (A) for v1, with explicit triggers to migrate to
(C) or (B) if specific things happen. Cost wins clearly inside v1;
operability wins; ship-by-Q2 wins. The filtered-ANN headroom is
thin, which is the load-bearing risk.

**[10:25] Devon:** What's the risk if filtered-ANN regresses past
the budget under the enterprise tenant?

**[10:25] Hiro:** Two failure modes. First, search-quality regression
visible to the enterprise tenant's users (slow queries time out at
the API layer; users see partial results). Second, if we push the
budget by tuning the IVF lists or HNSW parameters, recall drops
below 0.93 and tenant complains about quality.

**[10:26] Hiro:** Mitigation in (A): partition the 30M enterprise
tenant into its own Postgres replica with tuned indexes; isolate
their query load from the multi-tenant pool. Adds ~$8k/year per
isolated tenant in storage; acceptable for $1.2M ACV.

**[10:28] Yuki:** Coming in once. I ran the benchmarks; happy to
answer specifics. One concern not in the matrix — HNSW indexes in
pgvector require Postgres ≥16 with the extension at ≥0.7; our
production cluster is on Postgres 15 still. Either we upgrade
Postgres in parallel with this work (real risk, real cost), or we
use IVFFlat (lower recall ceiling, simpler).

**[10:30] Priya:** Postgres 15 → 16 upgrade has been on our backlog
for two quarters. It'll happen in Q3 either way. For v1 launch by
end of Q2 we use IVFFlat; we migrate the indexes to HNSW after the
Postgres upgrade.

**[10:31] Yuki:** Works. IVFFlat at the benchmarks I ran was 0.94
recall; HNSW would have been higher (~0.96-0.97). The v1 cost of
the indexing choice is real but small.

**[10:33] Devon:** What about the enterprise sales objection on
"managed-cheap-tier"? Does pgvector hurt us there?

**[10:34] Hiro:** Honest answer — it might, but the framing depends
on how we present it. "We index your embeddings in our managed
Postgres" reads differently than "we use pgvector". The technology
brand is engineering-facing; the customer-facing surface is "we
manage your search index". If you want, sales can route enterprise
questions to me directly.

**[10:36] Devon:** Acceptable. Let's go with (A) pgvector, IVFFlat
v1, HNSW after Postgres 16 upgrade. Document the migration triggers
explicitly so we don't drift past them.

**[10:37] Hiro:** Triggers, four:

- **Trigger 1 (migrate to (C) Weaviate):** If filtered-ANN p99 stays
  above 150ms for the >$500k ACV tenant for two consecutive weeks
  after the per-tenant isolation mitigation, the filtered-ANN
  headroom we accepted is gone.
- **Trigger 2 (migrate to (B) Pinecone):** If we add ≥3 more ML
  surfaces (recommendations, document Q&A, semantic alerting) and
  the ops cost of running per-surface pgvector clusters exceeds
  what we'd pay Pinecone per-month. Likely Q4-2026 at earliest.
- **Trigger 3 (stay on (A) and tune):** If the load profile evolves
  to be more "top-k unfiltered + small corpus per tenant" (i.e.
  filtered-ANN drops below 5%), the case for managed weakens.
- **Trigger 4 (revisit budget):** If the $50k cap is no longer the
  constraint (enterprise close lifts it to $200k), all three options
  become live again.

**[10:40] Marcus:** Adding to triggers — if the API surface starts
needing graph-shaped queries against the search results (e.g.
"documents semantically similar to X, written by author Y, in
tenant Z, after date D"), pgvector starts looking weak compared to
specialised vector DBs that do hybrid queries natively. Watch the
API request mix.

**[10:42] Hiro:** Good. Including as Trigger 5.

**[10:42] Yuki:** Last thing — Recall@20 on the benchmark was 0.94
for IVFFlat with `lists=100`. If we raise lists to 200, recall
climbs to 0.96 but latency goes up ~25%. We should tune lists per
deployment; not a one-size-fits-all.

**[10:43] Hiro:** Per-tenant tuning, noted. Yuki owns the tuning
profile per tenant.

**[10:44] Devon:** Let's wrap. Decision: (A) pgvector with IVFFlat
for v1; ADR-003 documents the choice, the migration triggers, and
the per-tenant tuning approach. Migration to HNSW post-Postgres-16
upgrade in Q3.

**[10:45] Hiro:** ADR-003 draft by 2026-05-26, review 2026-05-28.

## Decisions taken
- **pgvector with IVFFlat** selected for v1 semantic search.
- **HNSW migration deferred** to post-Postgres-16 upgrade in Q3.
- **Per-tenant tuning approach** (lists/m parameters) committed;
  Yuki owns the per-tenant profile.

## Action items
- **Hiro** — Draft ADR-003 covering pgvector decision + migration
  triggers + per-tenant tuning. Due 2026-05-26.
- **Hiro** — Stand up per-tenant Postgres replica for the
  30M-vector enterprise pre-sales account, contingent on close.
- **Yuki** — Per-tenant IVFFlat tuning profile (lists, probes,
  index build parameters) documented. Due 2026-06-02.
- **Priya** — Coordinate Postgres 15 → 16 upgrade for Q3; ensure
  HNSW indexes are part of the upgrade validation. Due Q3 start.
- **Marcus** — API surface design for search endpoint; ensure the
  service-internal API hides the vector DB choice from internal
  callers. Due 2026-06-09.
- **Devon** — Communicate the decision posture to sales for the
  enterprise pre-sales account.

## Exit criteria / migration triggers
Five triggers (see 10:37, 10:40, 10:42) for migrating off pgvector or
re-tuning:
- Filtered-ANN p99 >150ms for >$500k tenant for 2 consecutive weeks
  after isolation mitigation → migrate to Weaviate.
- ≥3 new ML surfaces + per-surface pgvector ops cost > Pinecone
  monthly → migrate to Pinecone.
- Load profile shifts to mostly-unfiltered, small-per-tenant →
  reconfirm pgvector is right.
- Budget cap lifts from $50k → reopen all options.
- API mix needs native hybrid graph + vector queries → reconsider.

## Open threads
- Postgres 15 → 16 upgrade timing (Priya, Q3) is a dependency for
  HNSW. If the upgrade slips, the recall@20 ceiling stays at IVFFlat
  levels (~0.94). Probably fine for v1; revisit if customer
  feedback suggests recall is the issue.
- The "managed-cheap-tier sales objection" risk (Devon's 10:33) is
  unresolved; flagged for sales coordination.
