---
type: concept
domain: research-papers
created: 2026-05-19
updated: 2026-05-19
sources: ["[[2024-anthropic-sparse-autoencoders-analysis]]"]
tags: [interpretability, sparse-autoencoders, dictionary-learning, technique]
aliases: ["SAE", "sparse autoencoder", "dictionary learning"]
status: active
compiled_against: 1
last_validated: 2026-05-19
first_appeared: 2023-10-01
also_known_as: ["dictionary learning (the classical signal-processing precursor)", "L1-sparse coding"]
---

# Sparse autoencoder (SAE)

A neural-network technique for **recovering an overcomplete sparse
basis** from dense, high-dimensional activations. In interpretability
work, an SAE is trained on a language model's residual stream (or
MLP output) to find directions ("atoms") that activate sparsely and
correspond to single concepts.

## Architecture (informal)

```
input activation ──► linear encoder ──► sparse latent ──► linear decoder ──► reconstructed activation
                                            │
                                            └── L1 penalty pushes the latent to be mostly zero
```

The decoder is typically frozen at unit-norm columns; the encoder is
trained to minimise reconstruction error plus L1 on the latent. The
**dictionary size** (number of latent dimensions) is usually
4× — 32× the input dimension; "overcomplete" means more atoms than
input directions, which is exactly what's needed if the input is in
[[superposition]].

## Why it works (current best guess)

If the true feature inventory is sparse — only a few features active
per token — the L1 prior aligns the learned dictionary with that
ground truth. Empirically this produces atoms that activate on
human-coherent concepts at higher rates than baselines (PCA, raw
neurons), as quantified in
[[2024-anthropic-sparse-autoencoders-analysis]].

## Known failure modes

- **Dead atoms.** A fraction of atoms never activate across training
  — wasted capacity.
- **Polysemantic atoms.** ~30% of atoms still activate on a mixture
  of unrelated concepts at any tested dictionary size.
- **Feature splitting.** As dictionary size grows, what looked like
  one atom can split into multiple narrower atoms — is this the true
  feature inventory emerging, or an artefact of the L1 prior?

## Relationship to other techniques

- **PCA** — linear, no sparsity prior. Baseline that SAEs beat by ~7×.
- **Activation patching** — orthogonal: SAEs find features, patching
  tests their causal role.
- **Circuits-level analysis** — composes atoms into multi-step
  computations. SAEs give the alphabet; circuits give the grammar.

## Appearances

| Date       | Page                                                          | Note                                                         |
| ---------- | ------------------------------------------------------------- | ------------------------------------------------------------ |
| 2026-05-19 | [[2024-anthropic-sparse-autoencoders-analysis]]               | First demonstration of SAE monosemanticity at frontier scale |
