---
type: log
scope: workspace
domain: workspace
updated: 2026-05-26
compiled_against: 2
---

# Workspace — Log

Append-only domain timeline. New entries go immediately below this
preamble (newest first); older entries scroll down. See
[`/AGENTS.md`](../../AGENTS.md) §6 for the append-only rule and §2.1
for entry format.

Entry format:

```
## [YYYY-MM-DD] <operation> | <one-line summary>
- Source: [[<path>]]
- Pages touched: [[…]], [[…]]
- One-line synthesis.
```

---

## [2026-05-21] ingest | 2026-05-19 vector DB selection (pgvector v1 for semantic search)
- Source: [[2026-05-19-meeting-vector-db-selection]]
- Pages touched:
  [[2026-05-19-meeting-vector-db-selection-summary]],
  [[stakeholder-hiro-ml]], [[team-ml-platform]],
  [[data-platform-vector-search]],
  [[engineering-decision-style]] (+1 confirmed instance, N=1→N=2 provisional),
  [[engineering-decisions-retrospective-may-2026]],
  [[stakeholder-marcus-api]] (Appearances +1 — cross-team),
  [[team-platform]] (Appearances +1 — cross-team via Priya)
- Vector DB v1: pgvector with IVFFlat selected over Pinecone /
  Weaviate on operability + cost; HNSW deferred to Q3 post
  Postgres 15→16 upgrade; 5 named migration triggers. Decision
  is the second confirmed instance of
  [[engineering-decision-style]], lifting it to N=2-provisional
  (ADR-001 remains a partial near-miss; pattern stays provisional
  until a third independent confirmation).

## [2026-05-21] ingest | 2026-05-13 API style decision (gRPC + REST gateway hybrid)
- Source: [[2026-05-13-meeting-api-style-decision]]
- Pages touched:
  [[2026-05-13-meeting-api-style-decision-summary]],
  [[stakeholder-marcus-api]], [[stakeholder-inez-dx]],
  [[stakeholder-bram-partner]], [[team-api-platform]],
  [[api-platform-evolution]],
  [[engineering-decision-style]] (1st confirmed full instance),
  [[engineering-decisions-retrospective-may-2026]],
  [[team-platform]] (Appearances +1 — Maya cross-team)
- API style for the new identity service: option (D) hybrid
  (gRPC internal + hand-written REST gateway external) over
  REST-only / gRPC+grpc-gateway / GraphQL on partner-compat +
  internal-latency + SDK-quality trade-offs. 3 named exit
  triggers committed before signing. First full instance of the
  [[engineering-decision-style]] positive pattern; structural
  contrast to the [[decision-delay-from-skipped-stakeholder]]
  failure mode on ADR-001.

## [2026-05-21] maintenance | workspace example expanded — domain prompt + 2 new arcs + cross-decision synthesis
- Bypass used: WIKI_ALLOW_CROSS_SCOPE=1 (touches `_system/**` and `domains/workspace/**` in the same change set)
- New: `_system/prompts/domains/workspace-meeting-analysis.md` (v1
  workspace-specific ingest sub-prompt — encodes the four
  readability elements, six body sections, side-effects matrix,
  pattern detection rules, decision-page creation rule).
- New raws: [[2026-05-13-meeting-api-style-decision]],
  [[2026-05-19-meeting-vector-db-selection]].
- New wiki pages: 2 analyses, 4 stakeholders, 2 teams, 2 projects,
  1 positive pattern, 1 cross-decision synthesis.
- Retrofitted: the 3 existing Q2-arc analyses with the four
  readability elements (TL;DR + at-a-glance + Mermaid + cast-
  and-stake table) so the worked examples match the new prompt's
  output contract. Cross-links added bidirectionally.
- Why: prompt↔ingest correspondence was missing for workspace;
  the prior single-arc worked example covered the negative
  pattern only; intern-onboarding readability needed a positive
  pattern + cross-project synthesis. See
  [[engineering-decisions-retrospective-may-2026]] for the
  intern-facing entry point.

## [2026-05-21] ingest | worked-example bundle (Q2 platform-migration arc)
- Sources: [[2026-04-08-meeting-q2-planning]],
  [[2026-04-22-decision-microservices-split]],
  [[2026-05-06-meeting-incident-postmortem]]
- Pages touched:
  [[2026-04-08-meeting-q2-planning-summary]],
  [[2026-04-22-decision-microservices-split-summary]],
  [[2026-05-06-meeting-incident-postmortem-summary]],
  [[team-platform]], [[stakeholder-alex-cs]],
  [[q2-platform-migration]], [[microservices-split]],
  [[decision-delay-from-skipped-stakeholder]],
  [[q2-platform-arc-may]],
  [[should-we-revisit-cs-veto-power]]
- Worked example demonstrating how a workspace ingest produces
  three analyses, two entity pages, a canonical decision page
  (distinct from the raw ADR), the cross-raw `decision-delay-from-
  skipped-stakeholder` pattern, and a 6-week arc synthesis. Synthetic
  / fictional content — see [`docs/EXAMPLE-DOMAINS.md`](../../docs/EXAMPLE-DOMAINS.md)
  for the removal-or-adopt guide.
