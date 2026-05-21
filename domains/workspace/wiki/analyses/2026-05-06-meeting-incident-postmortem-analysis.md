---
type: analysis
domain: workspace
created: 2026-05-20
updated: 2026-05-20
sources: ["[[2026-05-06-meeting-incident-postmortem]]"]
tags: [q2-platform-migration, postmortem, webhooks, sla, customer-success]
aliases: []
status: active
compiled_against: 1
raw_type: meeting
meeting_date: 2026-05-06
---

# Webhook delivery incident postmortem — analysis

## Context

Phase 2 of ADR-001 (see [[microservices-split]]) had been live for
six days when the 2026-05-04 incident occurred. Roughly 3.2% of
deliveries routed to the new layer were silently dropped over a
14-hour window. The exact failure mode is the one Alex Rivera
described on 2026-04-08 (see
[[2026-04-08-meeting-q2-planning-analysis]]) and on which Alex
issued a partial sign-off in ADR-001 (see
[[2026-04-22-decision-microservices-split-analysis]]).

This postmortem is the **closing beat** of the Q2-platform-
migration causal arc covered in [[q2-platform-arc-may]].

## Key claims

- **Root cause.** The routing-layer-local queue-depth assertion
  was structurally unable to detect silent acceptance-without-
  enqueue under sharded traffic at <10% rollout. A 3% drop on
  10% of traffic is below the noise floor of global queue depth,
  which is what the assertion was inspecting.
- **The cross-layer reconciliation gap deferred in ADR-001 was
  exactly the gap that broke.** This is stated explicitly by
  Maya on the record at ~14:11.
- **Phased rollout limited blast radius.** Two enterprise
  accounts impacted instead of the entire customer base; one
  triggered a contractual service credit, one stayed below the
  contractual threshold.
- **Rollback worked.** Mean time to remediate after root cause
  confirmed: 18 minutes.

## Tensions surfaced

- **"Alex was right" framing risk** (~14:20). Alex explicitly
  declines this framing on the record: "I don't want this to
  become 'Alex was right.' That's not useful." Recording this
  because it would have been easy for the postmortem to land on
  the wrong takeaway. Alex's reframe — "what would have made the
  team treat it as P0 instead of P1?" — is the load-bearing
  question and reshapes the action items.
- **CS sign-off authority** (~14:32). The Riverdale account
  manager (Sam) reports that one of the impacted enterprise
  customers is asking for a formal CS veto on phase progression,
  not just review. Alex confirms reconsidering whether the
  partial-sign-off on ADR-001 was the right call.
- **Documented residual risk vs blocking mitigation.** Maya's
  on-record statement at ~14:17 — "I weighed it as low-
  probability ... and I didn't fully internalise that the shadow
  data couldn't tell us about this specific failure mode either"
  — names the cognitive shape of the failure: shadow mode
  satisfied a different question than the one Alex was asking.

## Decisions taken

- **Phase 2 rolled back to 0% on new routing layer.** Confirmed
  18 minutes after root cause; phase 2 will not resume until
  the cross-layer reconciliation work lands.
- **Cross-layer reconciliation is now blocking phase 3.** Owner:
  Priya. Due 2026-05-20. (This is the action item that, six
  weeks earlier, the ADR deferred without owner or date.)

## Decisions deferred

- **CS sign-off authority — partial vs blocking.** Parked for a
  separate meeting per Devon's request (~14:37). The open
  question is filed as [[should-we-revisit-cs-veto-power]].
- **Customer-facing communication to Riverdale.** Sam to schedule
  follow-up; conditions for resuming phase 3 not yet committed.

## Action items

- Tom & Devon — "Blocking risks vs deferrable risks" one-pager
  for CS-flagged SLA exposures. Due 2026-05-13.
- Priya — Cross-layer reconciliation. **Blocking phase 3.** Due
  2026-05-20.
- Maya — Send postmortem to Northbridge and Riverdale by
  2026-05-08.
- Sam — Schedule follow-up with Riverdale on phase-3 conditions.
- Tom — Schedule meeting on CS sign-off authority.
- Maya & Alex — Joint review of ADR-001 partial-sign-off
  process; recommend a future-state convention for ADR-002+.
  Due 2026-05-15.

## Cross-references

- [[2026-04-08-meeting-q2-planning-analysis]] — where the concern
  was first surfaced.
- [[2026-04-22-decision-microservices-split-analysis]] — where the
  concern was acknowledged but the mitigation was deferred.
- [[microservices-split]] — the canonical decision page; status
  to be updated to reflect phase-2 rollback.
- [[q2-platform-migration]] — the project arc.
- [[stakeholder-alex-cs]] — the stakeholder whose concern was
  load-bearing across all three raws.
- [[team-platform]] — the team owning the rollout.
- [[decision-delay-from-skipped-stakeholder]] — the pattern this
  postmortem confirms; an instance of the broader failure mode
  of *under-empowering* a stakeholder rather than skipping them.
- [[q2-platform-arc-may]] — the cross-raw synthesis.
- [[should-we-revisit-cs-veto-power]] — the open question this
  postmortem opens.

## Notes

The interesting structural observation in this postmortem is
that the standard "did we listen to the stakeholder?" question
has the wrong shape. The team **did** listen: Alex was in the
planning meeting, got floor time, got named-reviewer status on
the ADR, got the silent-acceptance failure mode documented in
both the ADR and the partial-sign-off, and got the local
assertion as the immediate mitigation. The team listened, and
the failure mode still happened.

The right question is the one Alex asks at ~14:20: what level
of authority would have caused the team to treat the residual
risk as blocking rather than deferrable? This question generalises
beyond this one stakeholder and beyond this one ADR — it is what
[[decision-delay-from-skipped-stakeholder]] tries to capture as a
recurring pattern, and what [[should-we-revisit-cs-veto-power]]
tracks as an open process question.
