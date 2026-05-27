---
type: entity
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-13-meeting-api-style-decision]]"]
tags: [stakeholder, partner-engineering, external-integrations, backward-compat]
aliases: ["Bram Müller", "Bram from Partner Eng"]
status: active
compiled_against: 2
last_validated: 2026-05-21
role: stakeholder
team: "Partner Engineering"
title: "Partner Engineering lead (external integrations)"
migration_history:
  - from: 1
    to: 2
    on: 2026-05-26
    mode: in-place
    notes: 'type stayed entity'
---

# Bram Müller (Partner Engineering)

Partner Engineering lead. Owns the 60+ external partner integrations
that consume the public API, including procurement-sensitive
enterprise integrations where partner security teams have
non-negotiable opinions about wire protocols.

> [!important]
> The `team` frontmatter field stores the team name as plain text.
> Partner Engineering does not yet have its own team page in this
> wiki; the team earns a page when its behaviour as a unit becomes
> the working subject of an analysis. As of 2026-05-21, Partner
> Engineering is represented through Bram's stakeholder page only.

## Role and authority

- **Reviewer authority**: named reviewer on any decision affecting
  the public API or partner-visible behaviour. Equivalent role for
  the partner ecosystem to what
  [[stakeholder-alex-cs]] holds for the enterprise customer SLA
  surface.
- **Decision authority**: partner-communication timing and depth on
  any API change; backward-compatibility cutover windows.

## Appearances

| Date       | Raw                                                          | One-line context                                                                                                                  |
| ---------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| 2026-05-13 | [[2026-05-13-meeting-api-style-decision]]                    | Advocates for partner-facing REST as a hard constraint; reports that two named partners explicitly flagged gRPC as a procurement-security red flag |

## Concerns raised

1. **gRPC concepts leaking to partners trigger procurement
   escalations** (2026-05-13, ~14:19). Two enterprise partners
   (Northbridge — also affected in the [[2026-05-06-meeting-incident-postmortem]]
   — and one not named on the recording) told Bram in Q1 that
   their security teams treat HTTP/2 trailers and proto wire
   formats as red flags. They will accept a grpc-gateway *only if*
   it presents as plain REST with no observable gRPC concepts.
   Resolution: option (D) hybrid with a **hand-written REST
   gateway** (not grpc-gateway) precisely to avoid leakage.
2. **Partner notification timing** (2026-05-13 action item). Bram
   committed to notifying the two named partners about the
   upcoming API style before ADR-002 review (2026-05-22), to
   collect any blocking objections before the ADR commits.

## Concerns shape

Bram represents the **external-contractual surface** of the
business — analogous to [[stakeholder-alex-cs]] on the SLA side. His
concerns inherit the same risk profile that
[[decision-delay-from-skipped-stakeholder]] identifies: external-
contractual stakeholders are the ones whose risk signal must be
treated as load-bearing because their incentive is to block whereas
the proposing team's incentive is to proceed.

The 2026-05-13 meeting handled Bram's concern *with* blocking
authority — the hand-written REST gateway (not grpc-gateway) was
adopted as the structural mitigation, not deferred to follow-up
work. This is a positive contrast to the ADR-001 pattern where
Alex's analogous concern was acknowledged but its mitigation was
deferred.

## Cross-references

- [[stakeholder-alex-cs]] — analogous role on the enterprise-SLA
  surface; the 2026-05-13 meeting's handling of Bram's concern is
  the structural improvement over the 2026-04-22 ADR-001 handling
  of Alex's.
- [[stakeholder-marcus-api]] — API Platform lead; designs around
  the partner-compat constraint.
- [[stakeholder-inez-dx]] — DX lead; shares the long-tail
  partner-language framing.
- [[api-platform-evolution]] — project this stakeholder
  constrains.
- [[engineering-decision-style]] — positive pattern; Bram's
  blocking-mitigation reception is one of the pattern's
  identifying features.
- [[decision-delay-from-skipped-stakeholder]] — the negative
  pattern this stakeholder's experience is a *counter-example*
  for (concern raised → blocking mitigation, not deferred).
