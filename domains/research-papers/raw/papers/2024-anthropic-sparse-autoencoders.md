# Scaling monosemanticity: extracting interpretable features from large language models with sparse autoencoders

> **Note for readers of the template.** This file is a *synthesised
> stand-in* for a real research paper. It paraphrases the public
> outline of work by Anthropic and others on dictionary-learning
> approaches to interpretability circa 2023-2024. It is included
> purely to demonstrate the ingest flow; **do not cite this file as
> the real paper**. Replace it with the actual paper's PDF or
> markdown extraction when you adopt this template.

**Authors.** A. Researcher, B. Coauthor, C. Lab.
**Venue.** Preprint, 2024.
**arXiv.** placeholder/2401.xxxxx

## Abstract

Large language models compute in superposition: more directions in
their residual stream than they have dimensions. Naive probes find
features that activate on a mixture of unrelated concepts. We train
sparse autoencoders (SAEs) on the residual stream of a production-
scale language model. The learned dictionary atoms are substantially
more monosemantic than neurons: a single atom often corresponds to a
single human-interpretable concept (e.g. "the Golden Gate Bridge",
"DNA-sequence-like text", "code that increments a counter"). We
characterise the scale-dependence of feature interpretability and
identify three failure modes (dead atoms, polysemantic atoms,
feature splitting under widening).

## 1. Background

Mechanistic interpretability seeks to reverse-engineer the
algorithms a neural network has learned. A central obstacle is
**superposition**: the model packs more concepts than neurons by
using overlapping linear combinations of neuron directions.
Dictionary learning offers a candidate solution — find an
overcomplete basis in which features are sparse.

## 2. Method

We train SAEs with an L1 sparsity penalty on the residual stream
activations of a 9B-parameter language model at layer 24. The
dictionary size is 16x the activation dimension. We train on ~3B
tokens of pretraining data. Decoder weights are frozen at norm 1;
the encoder is trained to minimise reconstruction MSE plus L1 on
the latent.

## 3. Evidence

### 3.1 Atom interpretability

Of 16,384 atoms, ~14% activate on a human-coherent concept under
blind labelling (Cohen's kappa = 0.71 between two raters).
Comparable baselines (PCA components, raw neurons) score 2.1% and
3.4% respectively.

### 3.2 Feature steering

Intervening on a single SAE atom at decode time predictably shifts
model behaviour. Boosting the "code-comment" atom causes the model
to insert comments in code completions; suppressing the
"first-person" atom causes shifts from "I think" to "the model
thinks" style. Effect sizes are dose-dependent.

### 3.3 Feature splitting

When the dictionary size grows from 4x to 32x activation
dimension, ~30% of "compound" atoms split into multiple narrower
atoms (e.g. "Golden Gate Bridge" splits into "Golden Gate Bridge —
photograph", "Golden Gate Bridge — driving directions",
"Golden Gate Bridge — historical context"). This is consistent
with the dictionary becoming better-resolved at higher capacity.

## 4. Limits

- **Coverage.** ~30% of atoms remain polysemantic at any
  dictionary size we tested; some concepts (numeric ranges, syntactic
  positions) appear to resist clean factoring.
- **Scale extrapolation.** All experiments are at a single model
  scale. Whether the interpretability fraction monotonically
  improves with model size is open.
- **Causality.** Steering experiments show influence, not necessity
  — we have not shown the model *requires* a given atom to express
  a behaviour.

## 5. Open questions

- Does SAE-atom interpretability transfer across model families
  (e.g. atoms trained on model A predicting structure in model B)?
- Is feature splitting evidence of the *true* feature inventory
  emerging, or an artefact of the L1 sparsity prior?
- How does this approach interact with circuits-level analysis
  (composing atoms into multi-step computations)?
