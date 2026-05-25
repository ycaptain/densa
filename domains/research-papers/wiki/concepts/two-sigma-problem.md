---
type: concept
domain: research-papers
created: 2026-05-20
updated: 2026-05-21
sources: ["[[2024-vanzo-gpt4-homework-tutor-summary]]", "[[2025-kestin-ai-tutoring-active-learning-summary]]", "[[2024-bastani-generative-ai-guardrails-summary]]"]
tags: [education, learning-science, history, effect-size, motivating-problem]
aliases: ["2-sigma problem", "Bloom's 2 sigma", "Bloom 2-sigma", "two sigma problem"]
status: active
compiled_against: 2
last_validated: 2026-05-21
first_appeared: 1984-06-01
also_known_as: ["Bloom's two-sigma problem (Educational Researcher, 1984)"]
migration_history:
  - from: 1
    to: 2
    on: 2026-05-24
    mode: in-place
    notes: 'type stayed concept'
---

# Two-Sigma Problem (Bloom 1984)

The empirical finding, reported by Benjamin Bloom in 1984, that
**students taught with one-to-one (or one-to-few) mastery tutoring
perform roughly two standard deviations better** than students taught
in a conventional classroom on the same material. Bloom's framing
turns this from a curiosity into a *problem*: how to deliver that
effect size at population scale, when human one-on-one tutoring is
priced out of reach for most learners.

This is **the motivating problem** of essentially the entire
[[llm-tutoring-systems]] programme. If LLMs cannot at least
partially close this gap, the case for them in education collapses
to "engagement tool"; if they can close it cheaply, the implications
are large.

## The original finding (informal)

Bloom's review reported the following rough ordering on average
learning gains relative to a conventional lecture baseline (in
standard-deviation units, σ):

- Conventional classroom (lecture + summative test): **0σ baseline**.
- Lecture + graded homework with corrective feedback: **+0.8σ**.
- Lecture + mastery learning (Bloom's signature framework): **+1.0σ**.
- **One-to-one or one-to-few personal tutoring with mastery: +2σ.**

Bloom explicitly framed the gap between the +1σ scalable approaches
and the +2σ tutored approach as the **problem to solve** — finding
methods that could deliver tutoring-level effects without
tutoring-level cost.

## Why it matters for LLM tutoring research

Every paper in this domain's evidence arc gestures at Bloom:

- [[2024-vanzo-gpt4-homework-tutor-summary|Vanzo 2024]] opens with
  Bloom 1984 and explicitly positions the work as a partial attack
  on the homework-feedback end of the curve (the 0.3σ → 0.8σ gap).
- [[2025-kestin-ai-tutoring-active-learning-summary|Kestin 2025]]
  frames its physics-course RCT as the closest empirical move
  toward 2σ-style uplift via a pedagogy-aware AI tutor.
- [[2024-bastani-generative-ai-guardrails-summary|Bastani 2024]]
  is a counter-anchor: GPT Tutor only *matches* control on the exam.
  An LLM tutor that merely matches a no-AI baseline is **not** the
  2σ uplift Bloom was after.

The honest current summary across the three: **scalable LLM tutoring
can deliver short-term performance and engagement gains; whether it
can deliver Bloom's +2σ on actual retained skill is still empirically
open.** This tension is unpacked in
[[llm-tutoring-causal-evidence-2024-2025]].

## Common misreadings

- **"2σ means LLMs will replace teachers."** No. Bloom's effect was
  for *human* tutoring with mastery feedback. Whether *any* AI
  system reproduces it is still being measured. The Kestin 2025
  result is the strongest move so far in the LLM literature but
  remains single-site, single-domain, single-term.
- **"Effect sizes that small don't matter."** A consistent +1σ
  across millions of learners is enormous in practice — but only
  measurable when retention is tested. Most LLM-tutoring papers
  measure during-use performance, not retention; those numbers are
  not comparable to Bloom's.
- **"Bloom's 1984 numbers are gospel."** They are a review, not a
  meta-analysis. Replications since have yielded effect sizes more
  in the 0.4σ – 1.0σ range for human tutoring. Bloom himself
  acknowledged the original 2σ figure was a high-water mark.

## Relationship to other concepts

- [[intelligent-tutoring-system|ITS]] — the pre-LLM systematic
  attempt to deliver Bloom's effect at scale. Delivered roughly
  d ≈ 0.3 – 0.6, well short of 2σ.
- [[learning-guardrails]] — the prompt-level mechanism by which LLM
  tutors *try* to recover the mastery-feedback property Bloom
  identified as load-bearing.
- [[cognitive-offloading]] — the failure mode that prevents an LLM
  tutor from delivering Bloom's effect even when it appears to
  during use.

## Appearances

| Date       | Page                                                              | Note                                                                                            |
| ---------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 2026-05-20 | [[2024-vanzo-gpt4-homework-tutor-summary]]                        | Opens with Bloom 1984; positions GPT-4 homework tutoring as attacking the 0.3σ-feedback gap     |
| 2026-05-20 | [[2025-kestin-ai-tutoring-active-learning-summary]]               | Frames Harvard physics RCT as the closest 2σ-style move with an AI tutor to date                 |
| 2026-05-20 | [[2024-bastani-generative-ai-guardrails-summary]]                 | Counter-anchor: GPT Tutor matches control, not 2σ — clarifies what "skill acquisition" requires |
