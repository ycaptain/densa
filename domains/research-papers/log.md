---
type: log
scope: research-papers
domain: research-papers
updated: 2026-05-23
compiled_against: 1
---

# Research papers — Log

Append-only domain timeline. New entries go immediately below this
preamble (newest first); older entries scroll down. See
[`/AGENTS.md`](../../AGENTS.md) §6 for the append-only rule and §2.1
for entry format.

---

## [2026-05-23] ingest | Kim et al. 2025, "Unlocking the Future: A Comprehensive Review of ChatGPT in Education"
- Source: [[2025-kim-chatgpt-education-review-tkl]] (*Technology, Knowledge and Learning*, DOI 10.1007/s10758-025-09923-w; PDF-to-markdown extraction; full-text body of §§1–6 included, Figs. 1–5 + Appendix-A 52-row table partially summarised — see "Extraction scope" note in the raw)
- Pages touched: [[2025-kim-chatgpt-education-review-tkl-analysis]] (new), [[cognitive-offloading]] (Appearances row), [[llm-tutoring-systems]] (new "Connected reviews" subsection), [[llm-tutoring-cognitive-offload]] (Evidence-so-far row), [[llm-tutoring-equity-impact]] (Evidence-so-far row)
- One-line synthesis: a content-analysis review of 52 empirical ChatGPT-in-education studies (Jan 2023–Dec 2024) **quantifies the methodological gap** — only 1/52 explicit RCT and 25% geographically unspecified, with the three RCT anchors already in this wiki (Vanzo/Bastani/Kestin) sitting *outside* the corpus due to the "ChatGPT" keyword + 7-journal venue filters; **load-bearing limit**: position-paper layering in §5 means the four pedagogical recommendations are framework-informed syntheses, not derivations from §4 counts.

## [2026-05-21] maintenance | readability sweep + prompt-ingest reconciliation across worked examples
- Pages touched:
  [[2024-anthropic-sparse-autoencoders-analysis]] (rewritten to meet
  L2 §"Required analysis structure" — added 30-second TL;DR, How-to-
  read callout with §-anchor reading order, pipeline-flowchart
  Mermaid, Method × Headline × Baseline headline-numbers table, and
  the feature-splitting mechanism-level datum inside Evidence; added
  `mechanistic` methodology tag; promoted the demo-stand-in caveat to
  a proper `> [!note]` callout),
  [[2024-vanzo-gpt4-homework-tutor-analysis]] (added the previously
  missing **Headline numbers table** — a "Result × Anchor" shape
  appropriate for Vanzo's positional contribution, concentrating the
  §4.3.2 engagement-mediation OLS `coef = −0.446 p = 0.666`, the
  §4.3.1 weaker-students-benefit-more `R = −0.777, p < 0.001`, and
  the §4.3.3 hallucination-rate `4/1,549 ≈ 0.26%` numbers PhD readers
  most commonly miss; added `secondary-findings` tag),
  [[sparse-autoencoder]] (architecture sketch ASCII → Mermaid;
  Common-misreadings section added; failure-mode bullets cross-link
  to specific raw sections; `last_validated` bumped),
  [[superposition]] (mechanism Mermaid added; Common-misreadings
  section added; open questions tightened against current evidence;
  `last_validated` bumped).
- Sub-prompt
  [`_system/prompts/domains/research-papers-paper-analysis.md`](../../_system/prompts/domains/research-papers-paper-analysis.md)
  updated: the "Keep one diagram per analysis" Mermaid rule was
  refined to acknowledge the **double-Mermaid pattern Bastani's
  analysis already uses** (one structural before §Claim, one paper-
  specific mechanism diagram inside §Evidence when it carries
  paper-specific numerical content); the SAE worked-example listing
  in §"Worked examples to study" was updated to name the specific
  patterns it instantiates (pipeline flowchart + Method×Headline×
  Baseline table + rater/baseline/steering identification ladder).
- No `raw/` files touched (L1 §6 red-line preserved).
- Effect: a researcher landing on the L2 sub-prompt's
  "Worked examples to study" list now finds every referenced
  analysis fully compliant with the L2 lint rule (all four readability
  elements present before §Claim across all four worked examples);
  the interpretability lane is no longer a thinner-than-spec stub,
  the Vanzo headline-numbers table makes the engagement-mediation
  and weaker-students-benefit-more results impossible to miss, and
  the prompt language matches what the worked examples actually
  demonstrate.

## [2026-05-21] ingest | worked-example bundle (LLM-tutoring causal-evidence arc 2024–2025)
- Sources: [[2024-vanzo-gpt4-homework-tutor-eth]],
  [[2024-bastani-generative-ai-guardrails-pnas]],
  [[2025-kestin-ai-tutoring-active-learning-harvard]]
  (full primary articles extracted from arXiv 2409.15981v1,
  PNAS 10.1073/pnas.2422633122, Nature SR 10.1038/s41598-025-97652-6),
  plus [[2024-anthropic-sparse-autoencoders]] as an additional
  synthesised demo stand-in.
- Pages touched:
  [[2024-vanzo-gpt4-homework-tutor-analysis]],
  [[2024-bastani-generative-ai-guardrails-analysis]],
  [[2025-kestin-ai-tutoring-active-learning-analysis]],
  [[2024-anthropic-sparse-autoencoders-analysis]],
  [[two-sigma-problem]], [[learning-guardrails]],
  [[cognitive-offloading]], [[intelligent-tutoring-system]],
  [[sparse-autoencoder]], [[mechanistic-interpretability]],
  [[llm-tutoring-systems]],
  [[llm-tutoring-cognitive-offload]],
  [[llm-tutoring-equity-impact]],
  [[llm-tutoring-causal-evidence-2024-2025]],
  [[ai-education-2024-2025-researcher-guide]],
  [[how-to-read-this-domain]].
- Worked example demonstrating how the lightweight research-papers
  L2 ingests three primary RCTs into a coherent causal-evidence arc:
  per-paper analyses with 30-second TL;DRs + mechanism Mermaid
  diagrams + headline-numbers tables, four evergreen concept pages
  with appearance-tracking, one framework page, two long-running
  open questions, a cross-paper synthesis, a researcher guide with
  question-routed Mermaid decision tree, and a three-audience
  navigator. The fourth raw ([[2024-anthropic-sparse-autoencoders]])
  is an explicit synthesised demo stand-in — replace when adopting
  this template.
