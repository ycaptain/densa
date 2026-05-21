---
type: analysis
domain: research-papers
created: 2026-05-19
updated: 2026-05-19
sources: ["[[2024-anthropic-sparse-autoencoders]]"]
tags: [interpretability, sparse-autoencoders, superposition, dictionary-learning]
aliases: []
status: active
compiled_against: 1
paper: "[[2024-anthropic-sparse-autoencoders]]"
authors: [a-researcher, b-coauthor, c-lab]
evidence_quality: controlled
replicated: partial
---

# Scaling monosemanticity (analysis)

> **Demo analysis.** Generated from the synthesised stand-in raw under
> [[2024-anthropic-sparse-autoencoders]]. Shows the expected page
> structure for `type: analysis` in this L2.

## Claim

Sparse autoencoders (SAEs) trained on a frontier language model's
residual stream recover **interpretable, monosemantic features** at
scale — far more than naive baselines (PCA, raw neurons). This
demonstrates that [[superposition]] is reversible by dictionary-
learning, at least partially, even at the 9B-parameter scale.

## Method

L1-penalised SAE on layer-24 residual stream activations of a 9B
model. Dictionary 16× the activation dimension, trained on ~3B
tokens. Encoder learned; decoder frozen at unit norm. The output is
a sparse latent vector per token, with each dimension ("atom")
corresponding to a candidate feature direction.

The interpretability evaluation is **blind-labelled**: two human
raters independently assign a concept label to each atom from its
top-activating examples; agreement is measured by Cohen's kappa.

## Evidence

**Strongest result** (paper §3.1): ~14% of 16,384 atoms are
human-coherent under blind labelling, vs 2.1% (PCA) and 3.4% (raw
neurons). Inter-rater kappa = 0.71 supports the labels are
load-bearing, not noise.

**Causal corroboration** (§3.2): atom-level steering at decode time
predictably shifts model behaviour with dose-response. This moves
the claim past pure correlation: the atoms are not just *correlated
with* concepts, they are at least *partially functional* for them.

**Replication.** The general approach (SAEs on residual stream)
has been independently reported by at least two other groups in
nearby time, with broadly consistent monosemanticity-fraction
estimates in the same order of magnitude. Hence `replicated:
partial` — the *direction* is robust; the specific 14% number is
not yet cross-validated under identical conditions.

## Limits

- **Coverage ceiling.** ~30% of atoms remain polysemantic at any
  tested dictionary size. Some concept families (numeric ranges,
  positional / syntactic markers) appear to resist clean factoring.
  This is consistent with the [[superposition]] model needing more
  than just sparsity to disentangle.
- **Single-scale.** All experiments at 9B. Whether the
  interpretability fraction scales monotonically with model size
  is open — the paper notes this explicitly.
- **Influence ≠ necessity.** Steering shows the atom is *sufficient*
  to shift behaviour, not that the model *requires* this atom.
  Ablation studies would tighten this.

## Open questions (filed back)

- Cross-model transfer of SAE atoms (model A → model B) —
  see [[saes-cross-model-transfer]].
- Composing atoms into circuits — bridges with
  [[mechanistic-interpretability]] framework.
- Is feature splitting an artefact of the L1 prior or evidence of
  the true feature inventory emerging? — added to
  [[saes-cross-model-transfer]] tracking page.

## Wiki cross-references

- [[superposition]] — the obstacle this paper attacks.
- [[sparse-autoencoder]] — the technique used.
- [[mechanistic-interpretability]] — the broader programme this
  contributes to.

## Notes

The analysis is intentionally non-cheerleading: the paper shows real
progress on a real problem and is honest about its limits. The
"replicated: partial" tag is the most important field for future
queries — when synthesising across multiple SAE papers, weighting by
replication status matters more than weighting by venue.
