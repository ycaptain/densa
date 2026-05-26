# Sub-prompt: psychology session / psychiatry analysis (v3)

Used by [`_system/prompts/ingest.md`](../ingest.md) whenever a new file under
`domains/psychology/raw/sessions/` is being processed. Produces
**exactly one** `analysis` page per raw, in single-file v3 layout.

> Replaces v2's lens-A / lens-B dual-file design. Per Persons / Eells case
> formulation literature + DAP/SOAP industry practice, per-session notes
> should reference the living formulation rather than re-derive it. The
> living formulation in this wiki is the union of `wiki/patterns/` +
> `wiki/themes/` + `wiki/entities/` + `wiki/concepts/` + `wiki/frameworks/`.

> Authority: this prompt is procedural; the schema is in
> [`/AGENTS.md`](../../../AGENTS.md) (L1) and
> [`domains/psychology/AGENTS.md`](../../../domains/psychology/AGENTS.md) (L2).
> When this prompt and AGENTS disagree, AGENTS wins.

---

## When invoked

A user dropped a new raw file or said `ingest <path>`. The path resolves
under `domains/psychology/raw/sessions/`. Determine `session_kind` and
clinician slug from the filename pattern (see §"Routing" below); if
ambiguous, ask once before drafting.

## Three-stage pipeline

Every ingest runs three stages in sequence within the **same LLM context**
(no subagent overhead — the critique self-review is cheaper as a
contiguous reasoning pass).

```
Stage 1 Draft       — read raw + load conditional wiki pages, draft analysis. NOT WRITTEN TO DISK.
Stage 2 Critique    — self-review the draft against the raw + wiki invariants. Output an issue list.
Stage 3 Revise      — apply critique fixes, write the file + all wiki side-effects.
```

The three stages compose; do NOT shortcut to a single pass.

### Stage 1 — Draft

1. **Resolve routing** (§"Routing" below). Determine `session_kind`,
   `participants`, `clinician-slug`. If unsure, ask once.
2. **Load conditional context** (token budget):
   - Always: this sub-prompt + L1 + L2 + `outputs/snapshots/index-snapshot.md`
   - Conditional: read frontmatter (and only the relevant section bodies)
     of any `wiki/{entities,patterns,themes,concepts,frameworks}/<slug>.md`
     that the routing step suggests will be touched.
   - Just-in-time: the full raw transcript.
   - Target ≤40K tokens before drafting.
3. **Read the full raw**. State explicitly which modalities you can/cannot
   process if the raw includes images, audio, or non-text data (per
   [AGENTS.md §"Red lines"](../../../AGENTS.md#6-red-lines-non-negotiable)
   multi-modal red line).
4. **Draft** the appropriate template:
   - therapy → [`attic/templates-v1/psychology-analysis.md`](../../../attic/templates-v1/psychology-analysis.md) (legacy v1 template; under v2 these become `type: summary` pages — see [`_system/templates/summary.md`](../../templates/summary.md))
   - psychiatry → [`attic/templates-v1/psychiatry-analysis.md`](../../../attic/templates-v1/psychiatry-analysis.md) (legacy v1 template; same v2 note as above)
5. **Do not write to disk yet.** Hold the draft in working memory.

### Stage 2 — Critique

Run a clinical-supervisor self-review pass against the Stage-1 draft.
Output an issue list (do NOT modify the draft). Use this prompt body:

```
以临床督导身份审 Stage-1 草稿，对照 raw + 当前 wiki，逐条列出问题:

(a) 草稿里有任何引证不到 raw 文本的论断（hallucination 风险）
(b) 用了某 lens 但 frontmatter `analysis_lens` 没声明（或反之）
(c) 提到的 pattern / entity / theme / concept 没回链 wiki/<bucket>/<slug>
(d) 引文超过 raw 原文（捏造引文）
(e) Working formulation 章节里复述了 [[frameworks/X]] 的定义（应只引不展）
(f) `diagnostic_signals` 列了某诊断但本文找不到对应的 raw 锚点（诊断越界）
(g) 决策瘫痪 / 逃避场景没跑 alone-test（独处时是否也出现？）— 漏判神经发育成分
(h) 跨临床归属错乱（精神科 raw 里出现了应该在 therapy session 里处理的 process 材料）
(i) `Wiki side-effects` 清单与正文实际触动的页不一致
(j) Privacy: 第三方姓名 / 联系方式 / 地址被引入而本来不必要

输出格式：每条 `[一致性 | 失实 | 越界 | 漏改 | 隐私] line<n>: <问题> → <建议修复>`
不修改草稿，只输出 issue 清单。
```

If the issue list is empty, write a one-line confirmation
`Stage 2 critique: clean.` and proceed. If non-empty, the issues feed
Stage 3.

### Stage 3 — Revise

1. Apply each Stage-2 issue's suggested fix.
2. Verify `diagnostic_signals` only contain items with raw anchors.
3. Verify `analysis_lens` matches the `(<lens> lens)` paragraphs in the
   body (each lens declared has a paragraph; each paragraph has a declared lens).
4. Write the file to `domains/psychology/wiki/analyses/<raw-stem>-analysis.md`
   (per L2 §"Slug recognition rules" naming convention).
5. Apply all `Wiki side-effects` listed in the body:
   - **Append** instances to `wiki/patterns/<slug>.md`'s "Instances" / "实例"
   - **Append** timeline entries to `wiki/themes/<slug>.md`'s timeline
   - **Append** appearances to `wiki/entities/<slug>.md`'s "Appearances"
   - **Append** instances to `wiki/concepts/<slug>.md`'s "在我的材料里如何出现"
   - For psychiatry: **append** a row to `wiki/protocols/medication-arc.md`'s
     timeline (always, even when nothing changed).
6. Prepend to `domains/psychology/log.md` (top-of-file under frontmatter, per
   [AGENTS.md §"Red lines"](../../../AGENTS.md#6-red-lines-non-negotiable))
   using the [AGENTS.md §"ingest"](../../../AGENTS.md#21-ingest-path)
   entry format.
7. Output the **"Pages NOT touched but should be (carry-over)"** section in
   the analysis file with anything you discovered but didn't update.

---

## Routing — filename → session_kind + clinician slug

Deterministic mapping (per L2 §"Slug recognition rules"):

| Raw filename pattern | session_kind | clinician slug |
| --- | --- | --- |
| `<date>-session-<therapist-slug>.md` | `therapy` | `<therapist-slug>` |
| `<date>-session.md` (default therapist, no slug suffix) | `therapy` | `<your default therapist slug>` |
| `<date>-psychiatry-<dr-slug>.md` | `psychiatry` | `<dr-slug>` |

The exact slug mapping for your therapists and psychiatrists lives in
[`domains/psychology/AGENTS.md`](../../../domains/psychology/AGENTS.md)
§"Slug recognition rules". Edit the table there as you stabilise your
clinician set.

### Self-name recognition

Add the human's real name (or its romanisation) to the L2 AGENTS.md
§"Slug recognition rules" so the LLM treats every occurrence of that
name in raw transcripts as **self**, never as a counterpart entity.
This rule is the single most useful safeguard for ASR-transcribed
therapy material where the counterpart calls the user by name.

### Speaker-label disambiguation

Auto-transcribed files use generic labels (`说话人 1 / 2 / 3 ...`).
Determine which speaker is self by content patterns:
- Self typically: speaks in long paragraphs, recounts events, expresses
  emotions in first person, references "前任" / 工作 / 关系
- Counterpart typically: asks short questions, offers reflective summaries,
  uses second person ("你...")
- When ambiguous, ask once before drafting.

---

## Lens menu (11 + 4 conditional)

Pick the lenses that genuinely apply to the material at hand. Drop the
rest from `analysis_lens` and the body. Don't pad.

**Core 11** (declare freely when applicable):

| Lens | Code in `analysis_lens` | When it applies | Framework page |
| --- | --- | --- | --- |
| Cognitive Behavioural | `cbt` | Identifiable automatic thought / cognitive distortion / behavioural test | [[cbt]] |
| Internal Family Systems | `ifs` | ≥2 distinct parts surface; can describe Self-energy state | [[ifs]] |
| Emotion-Focused | `eft` | Affect itself shifts in-session; emotion schemes visible | [[eft]] |
| Attachment | `attachment-theory` | Relational anxiety / avoidance pattern with caregivers / partners / therapist | [[attachment-theory]] |
| Narrative | `narrative` | Identity story being authored / re-authored | [[narrative-therapy]] |
| Existential / Humanistic | `existential` | Meaning-level, freedom-and-responsibility material | [[existential-humanistic]] |
| Schema Therapy | `schema` | Long-standing maladaptive pattern with mode polarity (Vulnerable Child ↔ Punitive Parent ↔ Healthy Adult) | [[schema-therapy]] |
| Acceptance & Commitment | `act` | Decision-paralysis / experiential avoidance; values-action gap | [[act]] |
| Compassion-Focused | `cft` | Shame / self-attack system; threat vs soothing system imbalance | [[cft]] |
| **Biopsychosocial 4P** | `biopsychosocial-4P` | Multi-causal layering: predisposing / precipitating / perpetuating / protective | (no single framework page; cross-cutting) |
| **Diagnostic-differential** | `diagnostic-differential` | Material plausibly attributable to ADHD / ASD / MDD / GAD; alone-test relevant | [[adhd]] / [[asd]] / [[depression]] / [[anxiety]] |

**Conditional 4** (only when material warrants):

- `psychodynamic` — unconscious dynamics, defence mechanisms, drive material
- `transference` — therapist-client field is itself the data
- `somatic` — body data appears (breathing, tension, posture)
- `developmental` — life-stage / Erikson tasks centred

---

## session_kind branches

### `therapy`

Use [`psychology-analysis.md`](../../templates/psychology-analysis.md) template.

- Body length: 1500-2500 字
- Lenses: typically 2-4 from the core 11
- Wiki side-effects: usually 3-7 pages updated (entity + 1-2 patterns + maybe theme + concept if new)

### `psychiatry`

Use [`psychiatry-analysis.md`](../../templates/psychiatry-analysis.md) template.

- Body length: 1000-2000 字 (briefer than therapy)
- Lenses: `biopsychosocial-4P` and `diagnostic-differential` always; CBT optionally if cognitive material surfaced
- **Wiki side-effects MUST include `medication-arc` timeline +1 entry** (even on "no change" sessions)
- Pattern / theme work is **NOT done here**. Process material surfacing in psychiatry sessions is logged under "Open threads" for next therapy session.

---

## Biopsychosocial 4P — when to apply

Per L2 §"Biopsychosocial 4P framing", every analysis MUST consider whether
the session surfaces material from each of the four causal layers, and
when used, label `analysis_lens: [..., biopsychosocial-4P]`.

The 4P labels:
- **Predisposing**: trait-level factors present long before the trigger
  (attachment style, ADHD/ASD neurodevelopmental profile, family-of-origin schemas)
- **Precipitating**: the proximal trigger (specific event, recent change)
- **Perpetuating**: what keeps the loop going (avoidance, reinforcement, rumination)
- **Protective**: what's working (resources, supports, prior interventions)

### Alone-test (neurodevelopmental vs schema/attachment differentiation)

When raw shows decision paralysis / avoidance / overwhelm, before assigning
`diagnostic_signals` ask:

- Does the same phenomenon appear when **alone with no possible audience**? → favour neurodevelopmental ([[adhd]] / [[possible-asd-features]])
- Does it appear **only when others may evaluate**? → favour schema/attachment ([[evaluation-fear]] / [[inner-critic]])
- Both? → mark `diagnostic_signals` to include both axes; do **not** force a single attribution

### Diagnostic conservatism

- Use `[[possible-asd-features]]` rather than `[[asd]]` (user is in evaluation, not formally diagnosed)
- Every `diagnostic_signals` entry MUST have a raw anchor (timestamp / paragraph) in the body
- No diagnostic flag is added without observable evidence in this specific raw

---

## Privacy posture

Follow the posture declared in the L2 AGENTS.md §"Privacy posture"
section. Two postures are supported:

- **Default (public-shareable)** — paraphrase + raw-anchor link;
  ≤3 lines per verbatim quote; first-name + role only; encrypt
  `raw/` with `git-crypt` before any remote push.
- **Private-repo (only if the repo will never leave your own
  machines + a single encrypted backup remote)** — verbatim quotes
  in `analyses/` allowed without strict line cap; first names and
  full personal context allowed; user's real name in raw is
  recognised as `self`; `syntheses/` retains the ≤3-line soft cap;
  third parties not directly involved still use first-name + role.

---

## Quality bar (final pass before commit)

A correct ingest produces:

1. **Exactly one** `analysis` file per raw, named `<raw-stem>-analysis.md`
2. `frontmatter.session_kind` matches the raw bucket / filename pattern
3. `frontmatter.analysis_lens` exactly mirrors the `(<lens> lens)` body paragraphs
4. `frontmatter.diagnostic_signals` contains only entries with raw anchors in body
5. `frontmatter.sources` is a list of length **exactly 1**, the raw wikilink
6. **Bidirectional wikilinks**: every entity / pattern / theme / concept named in the analysis body has been updated in its own page (Appearances / Instances / timeline)
7. For psychiatry: `[[medication-arc]]` has a new timeline entry **(non-negotiable)**
8. `log.md` appended per [AGENTS.md §"ingest"](../../../AGENTS.md#21-ingest-path)
9. `Pages NOT touched but should be` section is non-empty if Stage 2 surfaced any carry-over (or explicitly states "none")

If any of (1)-(8) is missing, the ingest is incomplete — do not output a "done" message.
