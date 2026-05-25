---
type: open-question
domain: research-papers
created: 2026-05-19
updated: 2026-05-19
sources: ["[[2024-anthropic-sparse-autoencoders-summary]]"]
tags: [interpretability, open-question, sparse-autoencoders]
aliases: []
status: active
compiled_against: 2
arc_status: open
first_asked: 2026-05-19
migration_history:
  - from: 1
    to: 2
    on: 2026-05-24
    mode: in-place
    notes: 'type question → open-question'
---

# Do SAE-recovered features transfer across model families?

If a sparse autoencoder trained on model A's residual stream recovers
a feature like "code that increments a counter", does the *same*
direction (or a learnable linear map of it) recover the same feature
in model B's residual stream?

## Why this matters

Three reasons:

1. **Generality of the feature inventory.** If features transfer, the
   model is converging on a near-universal concept basis that
   pre-exists training. If they don't, each model is constructing its
   own idiosyncratic vocabulary and "interpretability per model" is
   inherently per-model work.
2. **Cost amortisation.** SAE training is expensive. If atoms transfer
   even partially, interpretability infrastructure becomes a public
   good across model families.
3. **Safety verification.** Cross-model transfer would let auditors
   reuse a vetted SAE on a new model without retraining.

## Evidence so far

| Date       | Source                                                            | What it adds                                                                  |
| ---------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 2026-05-19 | [[2024-anthropic-sparse-autoencoders-summary]]                   | Single-model result only; cross-model transfer not tested in this paper.      |

## What would settle it

- An SAE trained on model A, applied to model B's activations, that
  recovers a non-trivial fraction (>5%? >20%?) of the model-B
  monosemantic features that an SAE trained on B would find.
- A failure case: the cross-model SAE recovers nothing above baseline.
  That result is equally valuable.

## Related

- [[sparse-autoencoder]]
- [[superposition]]
- [[mechanistic-interpretability]]
