---
type: overview
domain: research-papers
created: 2026-05-19
updated: 2026-05-19
sources: ["[[2024-anthropic-sparse-autoencoders-summary]]"]
tags: [interpretability, framework, research-programme]
aliases: ["mech interp", "MI"]
status: active
compiled_against: 2
last_validated: 2026-05-19
programme_start: 2020-01-01
programme_status: active
migration_history:
  - from: 1
    to: 2
    on: 2026-05-24
    mode: in-place
    notes: 'type framework → overview'
---

# Mechanistic interpretability

A research programme that treats neural networks as **artefacts to
be reverse-engineered**, by analogy with reverse-engineering an
unfamiliar compiled binary. The goal is not "what does this model
do on average" (behavioural eval) but "what algorithm has it learned
and where in the weights is it stored".

## Core commitments

1. **Models are object-level, not black-box.** Their weights and
   activations contain the algorithm; we should be able to read it
   if we have the right vocabulary.
2. **Causal claims over correlational ones.** Activation patching,
   ablations, and steering experiments are preferred over probes
   that merely correlate.
3. **Bottom-up over top-down.** Identify atomic features and small
   circuits; compose upward. Top-down interpretation (e.g.
   "concept X must be in layer Y because tasks Z depend on it")
   risks confirmation bias.

## Sub-programmes (current state)

| Sub-programme              | What it does                                                          | Status                                                     |
| -------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| Dictionary learning / SAEs | Recover atomic features from activations in [[superposition]]         | Active; see [[2024-anthropic-sparse-autoencoders-summary]] |
| Circuits-level analysis    | Compose features into multi-step computations across layers           | Active; needs SAE-aligned vocabulary to scale              |
| Probing                    | Linear / non-linear classifiers on activations                        | Mature, but limited to features the probe can express      |
| Activation patching        | Surgically intervene on activations to test causal role               | Mature; standard tool                                      |

## Where this programme could fail

- **Features may not factor cleanly.** If real models compute in ways
  that resist any reasonable sparse basis (e.g. heavy use of
  positional context that's inherently non-local), SAEs and circuits
  may bottom out at "we can label 30-50% and that's it".
- **Scale brittleness.** Techniques developed on small models may
  not transfer. Cross-model transfer is an active question — see
  [[saes-cross-model-transfer]].
- **Safety gap.** Even if interpretability succeeds technically, it
  may not produce the kind of guarantees that alignment requires
  (verification of properties, not just description of mechanisms).

## Connected concepts

- [[superposition]] — the central obstacle this programme attacks.
- [[sparse-autoencoder]] — one of its most-used tools.

## Connected analyses

- [[2024-anthropic-sparse-autoencoders-summary]]

## Open programme-level questions

- [[saes-cross-model-transfer]] — do features transfer across model
  families?
