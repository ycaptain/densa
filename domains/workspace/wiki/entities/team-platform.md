---
type: entity
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-04-08-meeting-q2-planning]]", "[[2026-04-22-decision-microservices-split]]", "[[2026-05-06-meeting-incident-postmortem]]"]
tags: [team, platform, engineering]
aliases: ["Platform team", "Platform engineering"]
status: active
compiled_against: 1
last_validated: 2026-05-20
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

## Cross-stakeholder interfaces

- **Product** ([Devon Park](#)) — accepts the no-customer-visible
  upside Q2 in exchange for Q3 deploy-frequency gains.
- **Customer Success** ([[stakeholder-alex-cs]]) — the
  load-bearing external interface for SLA-exposure risk. The Q2
  arc is the team's first sustained collaboration with CS on a
  platform-level decision, which is partly why the partial-sign-
  off process was under-defined.

## Open work items inherited from postmortem

- Cross-layer reconciliation between routing layer and worker
  pool (Priya, blocking phase 3).
- Joint review of partial-sign-off process with Alex (Maya).
- Coordination with SRE + Product on the "blocking vs deferrable
  risks" one-pager.

## Notes

The team's behaviour across the arc is **structurally good** —
they brought CS into the planning meeting early, accepted shape-
of-rollout constraints from outside the team, and ran a blameless
postmortem. The defect is at the workflow seam where documented
residual risks are tracked: they were named, not owned, not
dated. See [[decision-delay-from-skipped-stakeholder]] for the
pattern this generalises to.
