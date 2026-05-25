---
type: entity
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-19-meeting-vector-db-selection]]"]
tags: [stakeholder, ml-platform, vector-search]
aliases: ["Hiro Tanaka", "Hiro from ML"]
status: active
compiled_against: 1
last_validated: 2026-05-21
role: stakeholder
team: "[[team-ml-platform]]"
title: "ML Platform lead"
---

# Hiro Tanaka (ML Platform)

ML Platform lead. Owns the ML infrastructure stack including the new
semantic-search service the team is shipping in Q2; convener of the
2026-05-19 vector DB selection meeting.

## Role and authority

- **Decision authority**: ML infrastructure stack including
  embedding models, vector databases, training pipelines, and
  inference platforms.
- **Reviewer authority**: named reviewer on any decision that
  touches an ML surface or its supporting infrastructure.

## Appearances

| Date       | Raw                                                          | One-line context                                                                                                          |
| ---------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| 2026-05-19 | [[2026-05-19-meeting-vector-db-selection]]                   | Owns the vector DB selection; lands pgvector (IVFFlat v1, HNSW post-Postgres-16) with five named migration triggers       |

## Decisions led

- **Vector DB v1 for semantic search** (2026-05-19) → pgvector
  with IVFFlat for v1, with explicit migration triggers to
  Weaviate (filtered-ANN p99 regression) or Pinecone (multi-
  surface ops cost). To be formalised as ADR-003 by 2026-05-26.
  See [[data-platform-vector-search]].

## Concerns raised

1. **Filtered-ANN headroom is thin under pgvector**
   (2026-05-19, ~10:14). At 50% selective filters, pgvector p99
   was 145ms — barely inside the 150ms budget. At 10% selective,
   it climbs to 220ms. The 30M-vector enterprise pre-sales tenant
   will hit harder filter cases.
   Mitigation accepted: per-tenant Postgres replica isolation
   ($8k/year per isolated tenant; acceptable for $1.2M ACV).
2. **Postgres 15 → 16 upgrade as a dependency for HNSW**
   (2026-05-19, via Yuki at ~10:28). Decided to ship v1 on IVFFlat
   (recall 0.94) and migrate to HNSW (recall ~0.96-0.97) after the
   Q3 Postgres upgrade. Recall difference is real but small for
   v1.
3. **Customer-facing branding of "pgvector" vs "managed Postgres"**
   (2026-05-19, ~10:33). The enterprise sales objection risk is
   real but framing-dependent. Hiro accepted routing enterprise
   technical questions to himself directly.

## Decision style

Hiro's decision-meeting shape on 2026-05-19 is one of the three
instances of the [[engineering-decision-style]] positive pattern:
6-page pre-read memo with benchmark results, meeting spent on
stress-testing the recommendation rather than re-deriving the
matrix, explicit migration triggers named before the decision is
signed, per-tenant tuning approach documented for downstream
ownership.

## Cross-references

- [[team-ml-platform]] — Hiro's team.
- [[stakeholder-marcus-api]] — API Platform lead; cross-team
  attendee on the vector DB decision; will own the API surface
  that hides the vector DB choice from internal callers.
- [[data-platform-vector-search]] — the project Hiro owns.
- [[engineering-decision-style]] — positive pattern; Hiro is one
  of the three pattern instances.
- [[engineering-decisions-retrospective-may-2026]] — cross-decision
  synthesis.
