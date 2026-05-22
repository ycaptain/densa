---
type: entity
domain: workspace
created: 2026-05-20
updated: 2026-05-21
sources: ["[[2026-04-08-meeting-q2-planning]]", "[[2026-04-22-decision-microservices-split]]", "[[2026-05-06-meeting-incident-postmortem]]", "[[2026-05-13-meeting-api-style-decision]]", "[[2026-05-19-meeting-vector-db-selection]]"]
tags: [team, platform, engineering]
aliases: ["Platform team", "Platform engineering"]
status: active
compiled_against: 1
last_validated: 2026-05-21
role: team
lead: "Maya Chen"
---

# Platform team

The Platform team owns the deploy queue, the monolith's bounded
contexts, and the in-flight Q2 service-extraction work (see
[[q2-platform-migration]] and [[microservices-split]]). The team
sits between Product (downstream consumer of feature velocity)
and SRE (downstream consumer of operability).

> [!important]
> The `lead` frontmatter field stores Maya Chen as plain text
> rather than a `[[stakeholder-…]]` wikilink. Per this L2,
> stakeholders earn their own page only when their behaviour
> becomes the working subject of a synthesis or pattern. Maya
> appears across all three raws but is not yet such a subject;
> if that changes (e.g. a synthesis on platform-lead decision-
> making style), promote her to a full stakeholder page and
> backfill the wikilink.

## Members (Q2 2026)

| Name        | Role                          | Appears in (raw)                                                                                 |
| ----------- | ----------------------------- | ------------------------------------------------------------------------------------------------ |
| Maya Chen   | Team lead, decision authority | [[2026-04-08-meeting-q2-planning]], [[2026-04-22-decision-microservices-split]], [[2026-05-06-meeting-incident-postmortem]] |
| Priya Shah  | Senior engineer               | [[2026-04-08-meeting-q2-planning]], [[2026-05-06-meeting-incident-postmortem]]                   |
| Tom Becker  | SRE lead (matrixed)           | All three raws                                                                                   |
| Jordan Liu  | On-call SRE (matrixed)        | [[2026-05-06-meeting-incident-postmortem]]                                                       |

SRE is matrixed in for the Q2 arc; not a permanent member of
the Platform team's reporting line.

## Appearances

- [[2026-04-08-meeting-q2-planning]] — proposes the identity +
  webhook split; commits to phased rollout with shadow mode.
- [[2026-04-22-decision-microservices-split]] — authors ADR-001
  (Maya); rollback runbook (Tom); staging dual-write validation
  (Priya).
- [[2026-05-06-meeting-incident-postmortem]] — runs the
  blameless postmortem; owns cross-layer reconciliation work
  going forward.
- [[2026-05-13-meeting-api-style-decision]] — cross-team
  appearance (Maya). Confirms identity team can start (D) hybrid
  work in parallel with cross-layer reconciliation; identity
  service consumer team for the API Platform decision.
- [[2026-05-19-meeting-vector-db-selection]] — cross-team
  appearance (Priya). Operations perspective decisive ("second-
  most-expensive-database" argument at ~10:18); Postgres 15 → 16
  Q3 upgrade is the dependency owner for the HNSW migration path.

## Cross-stakeholder interfaces

- **Product** ([Devon Park](#)) — accepts the no-customer-visible
  upside Q2 in exchange for Q3 deploy-frequency gains.
- **Customer Success** ([[stakeholder-alex-cs]]) — the
  load-bearing external interface for SLA-exposure risk. The Q2
  arc is the team's first sustained collaboration with CS on a
  platform-level decision, which is partly why the partial-sign-
  off process was under-defined.
- **[[team-api-platform]]** ([[stakeholder-marcus-api]]) — sibling
  team. Platform builds the underlying identity + webhook
  services; API Platform designs the API contract those services
  expose. First sustained cross-team collaboration on the
  2026-05-13 API style decision; Platform's identity work
  produces the surface API Platform exposes.
- **[[team-ml-platform]]** ([[stakeholder-hiro-ml]]) — sibling
  team. Platform owns the Postgres infrastructure that the new
  semantic-search pgvector stack runs on; the Q3 Postgres 15 → 16
  upgrade is a Platform-owned dependency for ML Platform's HNSW
  migration path.

## Open work items inherited from postmortem

- Cross-layer reconciliation between routing layer and worker
  pool (Priya, blocking phase 3).
- Joint review of partial-sign-off process with Alex (Maya).
- Coordination with SRE + Product on the "blocking vs deferrable
  risks" one-pager.

## Patterns observed

- [[decision-delay-from-skipped-stakeholder]] — the Q2 ADR-001
  arc is the negative pattern's N=1 instance. The defect is
  workflow-seam, not interpersonal.
- [[engineering-decision-style]] — the team's behaviour across
  the Q2 arc exhibits steps 1-4 of the positive pattern; the
  failure point is steps 5-6. Cf. the team's downstream
  collaboration with [[team-api-platform]] and
  [[team-ml-platform]] in May, where the team contributes to
  full-instance executions of the pattern.

## Notes

The team's behaviour across the arc is **structurally good** —
they brought CS into the planning meeting early, accepted shape-
of-rollout constraints from outside the team, and ran a blameless
postmortem. The defect is at the workflow seam where documented
residual risks are tracked: they were named, not owned, not
dated. See [[decision-delay-from-skipped-stakeholder]] for the
pattern this generalises to, and
[[engineering-decisions-retrospective-may-2026]] for how the May
decisions (in which Maya and Priya cross-team-attended) closed
this exact workflow seam.
