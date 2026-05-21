---
type: concept
domain: research-papers
created: 2026-05-19
updated: 2026-05-19
sources: ["[[2024-anthropic-sparse-autoencoders-analysis]]"]
tags: [interpretability, superposition, mechanism]
aliases: ["feature superposition", "polysemanticity"]
status: active
compiled_against: 1
last_validated: 2026-05-19
first_appeared: 2022-09-01
also_known_as: ["polysemanticity (when discussed at the neuron level)"]
---

# Superposition

Large neural networks pack **more concepts than they have neurons**
by representing concepts as overlapping linear combinations of
neuron-direction vectors. The same neuron then fires on a mixture of
unrelated concepts ("polysemanticity"), which is why naive probes
return uninterpretable directions.

## Mechanism (informal)

If the model needs to represent K concepts in a D-dimensional space
where K > D, it can use **almost-orthogonal** directions (interfering
slightly with one another) and tolerate the noise. Sparsity in the
ground-truth feature firing rate makes this tradeoff favourable: most
concepts are off most of the time, so interference is rare.

## Why it matters

Superposition is the central obstacle to **mechanistic
interpretability**: you cannot read a neural network as if each
neuron were a feature, because most neurons are mixtures. Two
research lines try to undo it:

1. **Dictionary learning** — train a sparse overcomplete basis (e.g.
   [[sparse-autoencoder]]) so that ground-truth features become axis-
   aligned in the new basis. See
   [[2024-anthropic-sparse-autoencoders-analysis]] for one instance.
2. **Circuit-level analysis** — accept polysemantic neurons and
   reason about composed computations directly. See
   [[mechanistic-interpretability]].

## Open questions

- Is superposition *necessary* for the capabilities we see, or is it
  an artefact of architecture / training? Architectures that
  discourage it (e.g. wide MLPs, sparse routing) may behave
  differently.
- How does superposition interact with the *size* of the model? More
  parameters could relax the K > D pressure, or training dynamics
  could exploit superposition more aggressively.

## Appearances

| Date       | Page                                                          | Note                                                                   |
| ---------- | ------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 2026-05-19 | [[2024-anthropic-sparse-autoencoders-analysis]]               | Empirical evidence that ~14% of SAE atoms become monosemantic at scale |
