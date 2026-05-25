---
type: open-question
domain: research-papers
created: 2026-05-20
updated: 2026-05-23
sources: ["[[2024-bastani-generative-ai-guardrails-summary]]", "[[2024-vanzo-gpt4-homework-tutor-summary]]", "[[2025-kestin-ai-tutoring-active-learning-summary]]", "[[2025-kim-chatgpt-education-review-tkl-summary]]"]
tags: [open-question, llm-tutoring, cognitive-offload, retention, long-arc]
aliases: ["does AI tutoring cause skill displacement", "cognitive offload arc"]
status: active
compiled_against: 2
arc_status: partial
first_asked: 2024-09-01
migration_history:
  - from: 1
    to: 2
    on: 2026-05-24
    mode: in-place
    notes: 'type question → open-question'
---

# Does LLM tutoring cause measurable skill displacement at multi-term scale?

[[2024-bastani-generative-ai-guardrails-summary|Bastani et al. 2024]]
shows a clean **within-term**
[[cognitive-offloading|crutch effect]]
for unguarded GPT-4 access during math practice — students score
17% lower on the unassisted exam than the no-AI control.
**Is this a within-term blip or a stable long-horizon drift?** And
does the answer change for guardrailed tutors, where harm is locally
eliminated but no positive uplift is delivered (Bastani's GPT Tutor),
or for pedagogy-aware tutors (Kestin's design) where the active-
retrieval structure *should* protect against the failure mode but
has not been tested under withdrawal?

## Why this matters

Three reasons:

1. **Policy timing.** Schools are deciding *now* whether to deploy
   ChatGPT-style tools as homework helpers. The Bastani result
   makes the within-term harm clear; the multi-term answer
   determines whether the harm compounds or self-corrects.
2. **Programme viability.** If the [[llm-tutoring-systems]]
   programme cannot demonstrate **net positive learning at the
   horizon that matters (months, not minutes)**, its strongest claim
   collapses to "improves engagement and during-use productivity"
   — useful but not the [[two-sigma-problem|Bloom-scale]] win.
3. **Mitigation calibration.** If naive deployments cause
   compounding harm, the cost of [[learning-guardrails]] becomes
   not a luxury but a precondition — which inverts the affordability
   story for under-resourced schools (see
   [[llm-tutoring-equity-impact]]).

## Evidence so far

| Date       | Source                                                              | What it adds                                                                                                          |
| ---------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 2024-09    | [[2024-vanzo-gpt4-homework-tutor-summary]]                          | Within-term positive engagement and grammar gain; **no retention test** — does not constrain the long-arc question     |
| 2024-fall  | [[2024-bastani-generative-ai-guardrails-summary]]                   | **Pre-registered, large-N**: GPT Base −17% on unassisted exam vs. control. GPT Tutor neutralises the harm within term  |
| 2025       | [[2025-kestin-ai-tutoring-active-learning-summary]]                 | Within-term positive uplift with pedagogy-aware prompt; **no retention probe** — leaves multi-term question untested    |
| 2025-10    | [[2025-kim-chatgpt-education-review-tkl-summary]]                   | Systematic content-analysis review of 52 empirical ChatGPT-in-education studies (Jan 2023–Dec 2024): **none of the 52 use a Bastani-style withdrawal-exam design**; confirms the multi-term retention gap is *field-wide*, not specific to the RCTs we've already ingested |
| TODO       | LearnLM/Eedi UK RCT (Google DeepMind 2025; not yet ingested)         | Adds human-in-the-loop arm; near-term knowledge-transfer gain on subsequent topics; multi-term retention still untested |

**Status: `arc_status: partial`.** The *within-term* portion of the
question has a clean answer for the unguarded case (yes, harm) and
for the verification-guardrailed case (no, but no uplift). The
*multi-term* portion is open across all design tiers.

## What would settle it

- A multi-term RCT (1+ academic year) with **periodic withdrawal
  exams** and a no-AI control. Ideally pre-registered, multi-site.
- A natural experiment using schools that have already deployed
  Khanmigo / GPT-style tools school-wide, with matched non-deploying
  schools — even with confounding, this could constrain the
  long-arc effect direction.
- A failure case is equally valuable: if a year-long Kestin-style
  deployment shows *no* retention drift, the offload concern can be
  narrowed to the unguarded-tool case specifically.

## Related

- [[cognitive-offloading]] — the underlying mechanism.
- [[learning-guardrails]] — the design strategy that locally
  neutralises the harm.
- [[llm-tutoring-systems]] — the programme this is the central
  open question for.
- [[two-sigma-problem]] — without resolution here, claims about
  approaching Bloom's effect are unwarranted.
- [[llm-tutoring-causal-evidence-2024-2025]] — the synthesis in
  which this question is the dominant unresolved thread.
