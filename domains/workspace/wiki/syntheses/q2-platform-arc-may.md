---
type: synthesis
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-04-08-meeting-q2-planning]]", "[[2026-04-22-decision-microservices-split]]", "[[2026-05-06-meeting-incident-postmortem]]", "[[decision-delay-from-skipped-stakeholder]]"]
tags: [synthesis, q2-platform-migration, narrative-arc, residual-risk]
aliases: ["Q2 platform arc — May 2026 view"]
status: active
compiled_against: 1
---

# Q2 platform migration — arc through May 2026

Six-week narrative spanning the [[q2-platform-migration]] project
from initial planning to phase-2 rollback. Pulls together three
raws and the [[decision-delay-from-skipped-stakeholder]] pattern.
Written 2026-05-20, with phase 2 still rolled back and
cross-layer reconciliation in flight.

## Weeks 1–2: a textbook-good planning meeting

The 2026-04-08 planning meeting is the **structurally healthy
anchor** of this arc. The Platform team enters with a fully-formed
proposal but no fixed rollout shape. [[stakeholder-alex-cs]] is in
the room — not on cc, not as an FYI — and gets sustained floor
time in the second half. The exchange between ~10:14 and ~10:26
is where the rollout actually gets designed: shadow mode, queue-
depth assertion, rollback as a runbook with state reconciliation,
named-reviewer status on the ADR. The Platform team accepts all
of these as constraints from outside the team without pushback.

If the arc had ended here, this would be a worked example of
cross-functional planning done right.

See [[2026-04-08-meeting-q2-planning-analysis]] for the per-raw
detail.

## Weeks 2–3: a textbook-good ADR

The 2026-04-22 ADR (canonical decision page:
[[microservices-split]]) reflects everything the planning meeting
asked for. Phased rollout with hard gates. Shadow mode as a P0
line item. Failure-mode table. Rollback as a phase-specific
runbook with explicit estimated time-to-rollback at each phase.
Named reviewers. Partial sign-off recorded on the record with
Alex's exact written comment preserved.

By the standards of architecture decision records, ADR-001 is a
**good document**. It names its residual risks. It dates its
phase gates. It records its reviewers' partial concerns. The
documentation discipline is not the failure mode.

The failure mode — and this is the load-bearing observation of
the entire arc — is a workflow seam that is **invisible inside
the ADR template**: the ADR can document a residual risk and
defer its mitigation, but the ADR template does not require the
deferred mitigation to have an owner, a date, or a phase-gate
label. The "cross-layer reconciliation" gap is named in the ADR,
acknowledged in Alex's partial sign-off, and then filed as
"phase-2 follow-up monitoring work" without any of those three
attachments.

See [[2026-04-22-decision-microservices-split-analysis]].

## Weeks 4–5: shadow mode, then phase 2

Phase 0 (staging soak) and phase 1 (production shadow) ran
clean. Zero silent drops observed in shadow data over 5 days of
shadow on 100% of production traffic. The team's confidence
going into phase 2 was justified *by the shadow data*. The
problem is that the shadow data could not have answered the
question being deferred to phase-2 follow-up monitoring —
shadow mode does not exercise customer endpoints, so a silent
drop in shadow looks like a success. Maya names this on the
record at ~14:17 of the postmortem: "I didn't fully internalise
that the shadow data couldn't tell us about this specific
failure mode either."

This is the cognitive shape of the failure: a robust validation
(shadow mode) satisfies a real question (does the routing layer
work under real load?) that is *adjacent to but distinct from*
the question Alex was asking (will silent acceptance-without-
enqueue be caught?). The team did not lose sight of the question
Alex asked; the team conflated the two questions.

## Week 6: the incident

The 2026-05-04 incident is six days into phase 2. The exact
failure mode Alex described on 2026-04-08 manifests:
acknowledgement-without-enqueue, no failure signal, retry logic
inactive, queue-depth assertion blind because a 3% drop on 10%
of traffic is below the noise floor of global queue depth.
~14 hours, ~1.7M deliveries affected, two enterprise accounts
hit (one triggers a contractual service credit, one below the
contractual threshold but above its internal threshold).

The postmortem is **blameless and good**. Alex declines the
"Alex was right" framing on the record (~14:20) and reframes
the question to: at the planning stage, what would have made
the team treat the residual risk as P0 instead of P1? Maya
takes the call on shipping phase 2 without cross-layer
reconciliation in place. Tom and Devon take the action item to
draft a "blocking risks vs deferrable risks" one-pager before
the next ADR cycle.

See [[2026-05-06-meeting-incident-postmortem-analysis]].

## What this arc demonstrates

The pattern [[decision-delay-from-skipped-stakeholder]] is the
load-bearing generalisation. The arc is the pattern's first
filed instance. The key observation — and the reason this
synthesis exists as a wiki page rather than a meeting note — is
that the standard remedies *for the naive form* of the pattern
do not apply here. The team **did** bring the stakeholder into
the room. They **did** give floor time, named-reviewer status,
and documented sign-off (partial). The remedies that would have
prevented this — partial-sign-off semantics, residual-risk-as-
owned-work, phase-gate authority — operate at a layer below the
"who's in the room?" layer.

## What this arc does not demonstrate

- It does not demonstrate that the microservices split was the
  wrong decision; the structural argument for the split is
  unchanged.
- It does not demonstrate that phased rollout was inadequate;
  phased rollout is exactly what bounded the blast radius from
  100% to 10%.
- It does not demonstrate that the team listened poorly; by
  every observable behaviour the team listened well. The defect
  is in process design, not in interpersonal conduct.

## Open questions

- [[should-we-revisit-cs-veto-power]] — the question of CS
  authority on SLA-exposing surfaces.
- Whether the "blocking risks vs deferrable risks" one-pager
  (Tom & Devon, due 2026-05-13) operationalises a generalisable
  process or only handles the CS-specific surface.
- Whether the [[decision-delay-from-skipped-stakeholder]] pattern
  acquires a second independent instance — which would harden
  the pattern from N=1 (currently flagged as provisional) to
  N=2.

## Cross-references

- [[q2-platform-migration]] — the project.
- [[microservices-split]] — the canonical decision.
- [[team-platform]] — the team.
- [[stakeholder-alex-cs]] — the load-bearing external reviewer.
- [[decision-delay-from-skipped-stakeholder]] — the pattern.
- [[should-we-revisit-cs-veto-power]] — the live process
  question.
