---
type: entity
domain: workspace
created: 2026-05-21
updated: 2026-05-21
sources: ["[[2026-05-13-meeting-api-style-decision]]"]
tags: [stakeholder, developer-experience, sdk-ownership]
aliases: ["Inez Park", "Inez from DX"]
status: active
compiled_against: 2
last_validated: 2026-05-21
role: stakeholder
team: "Developer Experience"
title: "Developer Experience lead (SDK ownership)"
migration_history:
  - from: 1
    to: 2
    on: 2026-05-26
    mode: in-place
    notes: 'type stayed entity'
---

# Inez Park (Developer Experience)

Developer Experience lead. Owns the four supported SDK languages (Go,
Python, TypeScript, Ruby), the SDK release cadence, and the
developer-facing documentation for both internal and partner
audiences.

> [!important]
> **Disambiguation.** Inez Park (DX) shares a surname with Devon Park
> (Product). They are colleagues, not related; the wiki disambiguates
> them by role and team, not by name alone. Cite as
> `[[stakeholder-inez-dx]]` to keep the resolver unambiguous.

> [!important]
> The `team` frontmatter field stores the team name as plain text;
> Developer Experience does not yet have its own team page in this
> wiki. Per the workspace L2's stakeholder-appearance restraint, the
> team earns a page when its behaviour becomes the working subject
> of a pattern or synthesis. As of 2026-05-21, DX is represented
> through Inez's stakeholder page only.

## Role and authority

- **Reviewer authority**: named reviewer on any decision that
  touches SDK shape, SDK release cadence, or developer-facing
  documentation.
- **Decision authority**: SDK release cadence, SDK versioning
  policy, SDK code-generation toolchain choices.

## Appearances

| Date       | Raw                                                          | One-line context                                                                                                            |
| ---------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| 2026-05-13 | [[2026-05-13-meeting-api-style-decision]]                    | Advocates against option (B) gRPC-only on SDK-quality grounds (Ruby grpc gem cadence; long-tail partner languages); lands the biweekly coupled-release commitment |

## Concerns raised

1. **gRPC + grpc-gateway hurts long-tail partner SDKs**
   (2026-05-13, ~14:17). 60+ partner integrations across 7+
   languages — gRPC client maturity is uneven outside the four
   internal-supported languages. A grpc-gateway in front of gRPC
   leaks gRPC concepts into the REST surface when the gateway is
   not aggressively maintained. Resolution: option (D) hybrid
   chosen with a **hand-written REST gateway** instead of
   grpc-gateway specifically to avoid this failure mode.
2. **Two-surface SDK drift risk** (2026-05-13, ~14:43). Solution:
   biweekly coupled SDK release; if either internal proto-generated
   SDK or external REST SDK slips, both slip. Committed jointly
   with [[stakeholder-marcus-api]].

## Decision style

Inez argues from concrete language-level observations (Ruby grpc
gem release cadence; PHP / .NET / Java GraphQL client maturity)
rather than from positions. This pulls the API decision toward
the option that produces the **best partner-side experience
across the long-tail language distribution**, which is exactly
the constraint a public-API decision should be most attentive to.

## Cross-references

- [[stakeholder-marcus-api]] — API Platform lead; joint SDK
  release cadence commitment.
- [[stakeholder-bram-partner]] — Partner Engineering; shares the
  "long-tail partner languages matter" framing.
- [[api-platform-evolution]] — the project this stakeholder
  influences.
- [[engineering-decision-style]] — positive pattern; Inez's
  language-level constraint argument is part of why the API
  decision exhibits the pattern.
