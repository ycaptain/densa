---
type: synthesis
domain: psychology
created: 2026-05-21
updated: 2026-05-21
sources: [
  "[[2026-04-02-session-reyes-summary]]",
  "[[2026-04-16-session-reyes-summary]]",
  "[[2026-04-23-psychiatry-han-summary]]",
  "[[2026-05-14-session-reyes-summary]]",
  "[[2026-05-14-six-week-retrospective]]",
  "[[how-to-read-psychology-domain]]"
]
scope: capability-demo
tags: [meta, capability-demo, evaluator, schema-demonstration, ten-capabilities, demo-claims]
aliases: ["what this domain demonstrates", "psychology capability demo", "ten capabilities"]
status: active
compiled_against: 2
migration_history:
  - from: 1
    to: 2
    on: 2026-05-26
    mode: in-place
    notes: 'type stayed synthesis'
---

# What this domain demonstrates — ten capabilities, with proof anchors

> [!important] For the open-source evaluator
> This page is the **claim sheet** the worked example pays out.
> It lists, with anchor-style proof, **ten specific schema
> capabilities** the four-ingest father-grief arc exercises.
> Each capability points at the exact wiki / raw location where
> the capability is visible, so the evaluator can verify in
> under 60 seconds per claim. This is the page to quote in your
> own evaluation report.

> [!faq]- For the clinician (orienting note)
> This synthesis is written for an *open-source evaluator*
> audience — engineers / clinician-developers / PKM hobbyists
> sizing up whether to adopt the LLM-wiki pattern. The clinical
> entry point is [[2026-05-14-six-week-retrospective]]. If you
> are arriving here from the L2 onboarding navigator
> ([[how-to-read-psychology-domain|psychology reading guide]])
> and you want the doctor-to-doctor
> view, switch to the retrospective.

> [!faq]- For the client (orienting note)
> This page is meta — it explains what the wiki pattern is
> *for*, not what your case is *about*. Your case lives at
> [[father-grief-arc]] (theme) and across the four session
> analyses. Skip this page unless you're curious about why
> the wiki is shaped the way it is.

## The ten capabilities

### 1. Time-evolution tracking across sessions

The same pattern is visible across multiple session ingests
with a real instance-ledger.
[[somatic-grief-containment]] has 4 distinct instance rows
spanning 2026-04-02 → 2026-05-14, each anchored to a different
raw [HH:MM] reference, each showing a different state of the
pattern. [[avoidant-mother-contact]] has 4 instance rows
showing the trajectory from voicemail-default (04-02) → first
partial breach (04-16) → indexed by PCL-5 (04-23) →
transformed by client-initiated 70-min call (05-14). Pattern
pages are **not** static definitions; they are growing
evidence ledgers.

**Anchor**: [[somatic-grief-containment#Instances]],
[[avoidant-mother-contact#Instances]].

### 2. Cross-session pattern recognition with instance ledgers

The LLM identifies recurring loops *across* sessions rather
than within a single session. The "automaton work-mode"
pattern, for example, surfaces in session 1's two-of-me
phenomenology, in session 2's kitchen-table 4:30-a.m. moment,
in session 4's Sunday-and-Monday-bad framing, and is indexed
by Han's anhedonia naming in psychiatry. None of these
instances would constitute a *pattern* alone; the wiki's
pattern-page makes the cross-session recurrence machine-
queryable.

**Anchor**: [[automaton-work-mode#Instances]] (4 rows, 4
distinct sessions, 4 distinct raw [HH:MM] anchors).

### 3. Cross-clinical boundary (therapy ↔ psychiatry separation)

The psychiatry analysis ([[2026-04-23-psychiatry-han-summary]])
uses the **psychiatry-analysis template** with sections
specific to psychiatry (`症状评估`, `量表`, `用药记录`,
`医生 plan`) and **does not update** pattern / theme /
IFS-Manager-part pages. The therapy analyses use the
**psychology-analysis template** with `## Working
formulation` lens blocks and *do* update those pages. The
[[medication-arc]] protocol is updated *only* from psychiatry
ingests. The separation is **architectural** — the templates
enforce different page structures, the wiki side-effects
diverge by session_kind, and the v3 prompt
([_system/prompts/domains/psychology-session-analysis.md](../../../_system/prompts/domains/psychology-session-analysis.md))
§"psychiatry branch" explicitly forbids pattern updates from
psychiatry ingests.

**Anchor**: compare §"Wiki side-effects" lists in
[[2026-04-23-psychiatry-han-summary#wiki-side-effects]] (4
items: protocol +1 row, 2 concept instances, 1 entity
created) vs [[2026-04-16-session-reyes-summary#wiki-side-effects]]
(11 items including pattern, theme, framework, entity,
concept). The psychiatry analysis's side-effect set is
deliberately smaller and contains no pattern-page edits.

### 4. Diagnostic conservatism with raw-anchored signals

Every `diagnostic_signals` entry has a raw [HH:MM] anchor in
the body of the analysis. The frontmatter
`diagnostic_signals: [depression, complicated-grief]` on
all four analyses contains only items that the in-room
material *anchors*. ASD / ADHD / PTSD / panic / primary
anxiety are **not** flagged despite surface features (the
executive-task professional context might naively suggest
ADHD; the chest tightness might naively suggest panic; the
PCL-5 = 28 avoidance cluster might naively suggest PTSD).
None are added because raw evidence specifically arguing
for them is absent or sub-threshold.

The L2 schema's rule that `[[possible-asd-features]]` is
preferred over `[[asd]]` (because the user / client is in
evaluation, not formally diagnosed) is exercised in the
schema even though this specific case does not surface ASD
features.

**Anchor**: [[2026-04-23-psychiatry-han-summary#stage-2-critique-applied]]
item (f) — the explicit critique-and-fix where Stage 1 draft
included `anxiety` based on GAD-7 = 9 and Stage 2 removed
it as over-claiming.

### 5. Privacy posture switching (architecturally declared)

The L2 AGENTS.md §"Privacy posture" supports two postures:
**conservative** (paraphrase + ≤3 lines per quote +
first-name + role + git-crypt) and **private-repo (relaxed)**
(verbatim allowed in analyses; first name + full personal
context allowed; user's real name treated as self). This
worked example **declares** the private-repo posture in
§"Privacy posture" preamble and exercises it: the analyses
contain ~4-line verbatim quotes from the raw sessions; the
syntheses retain the ≤3-line cap even under the relaxed
posture. The declaration is mechanically queryable; an
adopter switching postures only edits one section of
AGENTS.md.

**Anchor**: see [`domains/psychology/AGENTS.md`](../../AGENTS.md)
§"Privacy posture" §"This worked example uses the private-
repo (relaxed) posture". Note the explicit cap in
syntheses — this synthesis (you are reading it) quotes raw
material at most 1-2 lines per anchor.

### 6. ASR transcription correction table workflow

Real auto-transcribed sessions contain consistent ASR garbles
(homophones, acronyms mis-rendered, code-switched English in
Chinese transcripts). The L2 AGENTS.md §"Known transcription
corrections" table is **append-only** — corrections are
silently applied to wiki output and the table records the
mapping. The worked example's raws include 2-3 ASR-style
errors per session as demonstration material; the L2's
correction table is populated with worked rows from this
demo.

**Anchor**: see [`domains/psychology/AGENTS.md`](../../AGENTS.md)
§"Known transcription corrections" table; specifically the
worked rows for `"P.H. cue"` → `"PHQ"` (raw session 1 line
[12:08]) and similar.

### 7. Multi-lens orchestration without forcing a single school

Each therapy analysis declares 2-4 lenses from the menu of
11 + 4 (per
[_system/prompts/domains/psychology-session-analysis.md](../../../_system/prompts/domains/psychology-session-analysis.md)
§"Lens menu"). The lenses are chosen to match what the
in-room material actually warrants, not chosen to fit a
predetermined modality.

| Analysis | Lenses declared |
| --- | --- |
| [[2026-04-02-session-reyes-summary]] | `biopsychosocial-4P, attachment-theory, existential` |
| [[2026-04-16-session-reyes-summary]] | `ifs, somatic, eft, biopsychosocial-4P` |
| [[2026-04-23-psychiatry-han-summary]] | `biopsychosocial-4P, diagnostic-differential, cbt` |
| [[2026-05-14-session-reyes-summary]] | `narrative, attachment-theory, eft, biopsychosocial-4P` |

The lens set evolves with the in-room material: IFS is
absent from session 1 (no parts-language yet); IFS dominates
session 2 (frame introduced); narrative / meaning-
reconstruction enters at session 4 (only after partial
unburdening). The schema does **not** force any single
framework allegiance; the [[integrative-grief-therapy]]
framework page makes the multi-school braid explicit.

**Anchor**: frontmatter `analysis_lens` fields across the
four analyses. Each declared lens has a corresponding
`(<lens> lens)` paragraph in the body (per v3 prompt §"Quality
bar" item 3, machine-checkable).

### 8. Biopsychosocial 4P framing applied to every analysis

Every analysis (both therapy and psychiatry) carries a
`biopsychosocial-4P` declaration and a 4P-labelled body
paragraph or section. The 4P layers (predisposing,
precipitating, perpetuating, protective) are **populated
unevenly** across sessions — session 1 populates predisposing
+ precipitating densely; session 4 documents *which 4P layer
has changed* (a delta-view rather than a re-statement).

**Anchor**: [[2026-04-02-session-reyes-summary#working-formulation]]
*(biopsychosocial-4P lens)* paragraph;
[[2026-04-23-psychiatry-han-summary#biopsychosocial-4p-psychiatry-framing]]
4P table; [[2026-05-14-session-reyes-summary#working-formulation]]
*(biopsychosocial-4P lens)* with delta language ("structurally
unchanged but now *consciously transmissible*" — capturing
the intergenerational modification at the predisposing layer).

### 9. Alone-test for neurodevelopmental vs schema/attachment differentiation

The L2 AGENTS.md §"Alone-test" rule requires explicit
application of the alone-test whenever decision paralysis /
avoidance / overwhelm material surfaces: does the same
phenomenon appear when the user is *alone with no possible
audience* (→ neurodevelopmental) or only *when others may
evaluate* (→ schema/attachment)? Session 1's avoidance
behaviour (the maternal-call avoidance) is explicitly
alone-tested: avoidance is context-bound, not present in
solitary tasks → attachment/schema attribution → ASD/ADHD
**not** flagged in `diagnostic_signals`.

**Anchor**: [[2026-04-02-session-reyes-summary#working-formulation]]
*(biopsychosocial-4P lens)* paragraph: *"Mark's avoidance is
specifically context-bound — it does not appear when he is
alone doing solitary tasks, only when interpersonal contact
requires affect co-regulation he does not feel he has
bandwidth for. This favours attachment / schema attribution
rather than neurodevelopmental executive dysfunction;
ADHD / possible-ASD-features are not flagged in
`diagnostic_signals` despite the surface appearance of 'task
not getting done.'"*

### 10. v3 three-stage pipeline (Draft → Critique → Revise) — audit trail visible

Every analysis closes with a `## Stage 2 critique applied`
section listing 2-3 real critique items that the Stage 2
supervisor self-review surfaced against the Stage 1 draft,
and the specific fixes applied in Stage 3. The audit trail
makes the prompt↔output correspondence machine-readable —
a reader can confirm that the Stage 2 critique categories
((a) through (j) in
[_system/prompts/domains/psychology-session-analysis.md](../../../_system/prompts/domains/psychology-session-analysis.md)
§"Stage 2 — Critique") were actually applied.

**Anchor**: each analysis's terminal section:
- [[2026-04-02-session-reyes-summary#stage-2-critique-applied]]
  — 3 items: lens-declaration mismatch (b), wikilink discipline
  (c), diagnostic boundary (f).
- [[2026-04-16-session-reyes-summary#stage-2-critique-applied]]
  — 3 items: hallucinated content (a), alone-test omission (g),
  side-effects ↔ body consistency (i).
- [[2026-04-23-psychiatry-han-summary#stage-2-critique-applied]]
  — 3 items: diagnostic boundary (f), cross-clinical boundary
  (h), framework theory repetition (e).
- [[2026-05-14-session-reyes-summary#stage-2-critique-applied]]
  — 3 items: verbatim quote handling (d), framework theory
  expansion (e), side-effects ↔ body consistency (i).

Across the four analyses, **8 distinct Stage-2 critique items
(a-j) are exercised at least once** — i.e. the critique
categories are not theoretical.

## What this does *not* demonstrate

For epistemic clarity, the worked example is **not** evidence
for any of:

- **The LLM-wiki pattern as therapy itself.** The wiki is the
  bookkeeper of patterns across clinician-led sessions. The
  clinical work happens in clinician relationships.
- **A specific clinical modality's superiority** (IFS over
  CBT, integrative-grief-therapy over manualised CGT). The
  modalities are chosen by the (fictional) clinicians in the
  worked example because they fit the (fictional) case
  presentation; the schema is modality-agnostic and an
  adopter using purely CBT or purely psychoanalytic frames
  would see the same structural capabilities exercised
  through different lens declarations.
- **Diagnostic capability.** The schema's
  `diagnostic_signals` field surfaces dimensions; formal
  diagnosis stays with the licensed clinician. The worked
  example deliberately *does not* produce a DSM-5-TR coding;
  it produces a working dx (Han at psychiatry: "bereavement-
  related depressive episode with complicated-grief features
  and sub-threshold PTSD avoidance cluster") that explicitly
  defers coding.
- **Generalisable clinical claims.** The worked example is
  one (fictional) case. Each row of the protocols /
  pattern-instance ledgers is **one clinician's
  reasoning** at one moment on one patient. Reading the
  [[medication-arc]] as generalised SSRI-deferral guidance,
  or the [[avoidant-mother-contact]] page as a clinical
  description of all bereavement avoidance, would be a
  category error.

## What this would look like in your repo with your own L2

Three adoption patterns we anticipate, in increasing
investment order:

1. **Adopt the L2 schema as-is, replace the worked example
   with your own raws.** Delete the four raw files under
   `domains/psychology/raw/sessions/`, regenerate the wiki
   from your own ingests. The schema (AGENTS.md), the v3
   prompt, the templates, the validator carry over
   unchanged. The honest-disclosure callout on the L2
   AGENTS.md is the doorway you walk through here.
2. **Fork the L2 to a different clinical domain.** The
   schema generalises to most relationship-tracking
   domains. *Coaching* / *physical therapy* / *speech
   therapy* / *occupational therapy* — all map onto the
   same `session` → `analysis` → `pattern` / `theme` /
   `protocol` shape. The biopsychosocial 4P framing and
   the cross-clinical-boundary architecture are the parts
   most likely to need adaptation.
3. **Treat the worked example as a benchmark.** Use it as
   the reference output an LLM should be able to produce on
   a comparable raw input. The ten capabilities above are
   the explicit specification; the analyses are the
   reference implementation. An adopter can A/B their own
   ingest output against the worked example's structure
   to identify where their own prompts are under-specified.

## Cross-references

- [[2026-05-14-six-week-retrospective]] — the clinician-grade
  arc-level entry point this synthesis points to under
  Capability 2 / 7 / 8.
- [[how-to-read-psychology-domain|psychology reading guide]]
  — the three-audience navigator;
  the *process-indexed* counterpart to this *capability-
  indexed* synthesis.
- [`domains/psychology/AGENTS.md`](../../AGENTS.md) — the
  L2 schema being exercised.
- [`_system/prompts/domains/psychology-session-analysis.md`](../../../_system/prompts/domains/psychology-session-analysis.md)
  — the v3 ingest prompt operationalising the schema.
- [`GUIDE.md`](../../../../../GUIDE.md) §"Choosing or replacing the default domain"
  — the broader template-evaluation guide; psychology is the
  "heavy (worked example)" entry in the table.
