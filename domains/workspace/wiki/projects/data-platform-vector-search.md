---
type: project
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-19-meeting-vector-db-selection]]"]
tags: [ml-platform, semantic-search, vector-db, q2-2026]
aliases: ["Semantic search v1", "Vector search platform"]
status: active
compiled_against: 1
last_validated: 2026-05-21
project_status: active
start_date: 2026-05-19
target_date: 2026-06-30
lead: "[[stakeholder-hiro-ml]]"
---

# Data Platform — vector search

Semantic search v1 over customer documents. Ships by end of Q2 with a
12M-vector index at launch (1024-dim embeddings) and a planned
+1M/quarter steady-state growth profile, plus one 30M-vector
enterprise pre-sales tenant in scope on close.

## Goal

- Ship the public beta of semantic search by end of Q2 2026.
- Pick a vector DB for v1 that meets the constraints (Q2 deadline,
  operability, ≤$50k v1 budget, reversibility, filtered-ANN
  quality).
- Establish the per-tenant tuning approach for varying corpus sizes
  and filter selectivity profiles.

## Scope

**In scope (Q2):**
- Vector DB v1 selection (pgvector with IVFFlat) — landed
  2026-05-19; see [[2026-05-19-meeting-vector-db-selection-analysis]].
- ADR-003 (formalising the choice) — Hiro, due 2026-05-26.
- Per-tenant Postgres replica isolation for the 30M-vector
  enterprise tenant (contingent on close).
- Per-tenant IVFFlat tuning profile — Yuki, due 2026-06-02.
- API surface design for the search endpoint — Marcus
  ([[team-api-platform]]), due 2026-06-09.

**Out of scope (Q2):**
- HNSW index migration — deferred to Q3, post Postgres 15 → 16
  upgrade.
- Migration to Weaviate or Pinecone — deferred pending exit-
  trigger thresholds.

## Status

- 2026-05-19 — Decision meeting; pgvector v1 selected with five
  named migration triggers.
- 2026-05-26 (target) — ADR-003 draft.
- 2026-05-28 (target) — ADR-003 review.
- 2026-06-02 (target) — Per-tenant tuning profile (Yuki).
- 2026-06-09 (target) — API surface design (Marcus).
- End-of-Q2 (target) — Public beta launch.
- Q3 — Postgres 15 → 16 upgrade (Priya); HNSW migration.

## Decisions

- **Vector DB v1**: pgvector with IVFFlat indexing for v1; HNSW
  migration deferred to Q3 post-Postgres-upgrade. Pending ADR-003
  formalisation. See
  [[2026-05-19-meeting-vector-db-selection-analysis]] for the
  decision's rationale.

## Sessions and source raws

| Date       | Raw                                                          | Role in arc                                                |
| ---------- | ------------------------------------------------------------ | ---------------------------------------------------------- |
| 2026-05-19 | [[2026-05-19-meeting-vector-db-selection]]                   | Decision meeting; pgvector v1 selected                     |

## Stakeholders

- [[team-ml-platform]] — owning team.
- [[stakeholder-hiro-ml]] — lead and decision owner.
- [[stakeholder-marcus-api]] — cross-team; API surface for search.
- [[team-platform]] — sibling; Postgres infrastructure owner.
- Yuki Nakamura (ML Platform) — benchmark owner; per-tenant tuning.
- Priya Shah ([[team-platform]]) — Postgres 15 → 16 upgrade
  dependency owner.
- Devon Park (Product) — enterprise pre-sales coordination.

## Open risks

- **Filtered-ANN headroom is thin** at 50% selective filters
  (p99 145ms vs 150ms budget). At 10% selective, p99 climbs to
  220ms — out of budget. Mitigation: per-tenant Postgres replica
  isolation for the 30M-vector enterprise tenant on close.
- **Postgres 15 → 16 upgrade timing.** If the Q3 upgrade slips,
  v1 stays on IVFFlat (recall 0.94 vs HNSW 0.96-0.97). Probably
  fine for v1; revisit if customer feedback suggests recall is
  the issue.
- **"Managed-cheap-tier" sales objection risk** on enterprise
  pre-sales. Framing-dependent; Hiro accepted routing enterprise
  technical questions to himself directly. Devon to coordinate
  with sales.

## Migration triggers (revisit conditions)

Five named triggers per the 2026-05-19 meeting (see analysis for
detail):
- Filtered-ANN p99 >150ms for >$500k tenant for 2 consecutive
  weeks after isolation → migrate to Weaviate.
- ≥3 new ML surfaces + per-surface pgvector ops cost > Pinecone
  monthly → migrate to Pinecone.
- Load profile shifts to mostly-unfiltered, small-per-tenant
  corpora → reconfirm pgvector is right.
- Budget cap lifts from $50k → reopen all options.
- API mix needs native hybrid graph + vector queries → reconsider
  (added by Marcus at ~10:40).

## Connections to other projects

- **[[api-platform-evolution]]** — the API Platform team will own
  the API surface fronting the search service. The reversibility-
  at-v2-horizon framing Marcus brought to the vector DB meeting
  is informed by his own API decision experience from
  2026-05-13.

## Cross-references

- [[2026-05-19-meeting-vector-db-selection-analysis]] — the
  analysis of the decision meeting.
- [[engineering-decision-style]] — positive pattern this project
  exemplifies.
- [[engineering-decisions-retrospective-may-2026]] — cross-decision
  synthesis braiding this project's decision with Q2 platform
  migration's ADR-001 and the API style decision.
