# Sub-prompt: research-papers paper analysis (v1)

Used by [`_system/prompts/ingest.md`](../ingest.md) whenever a new file
under `domains/research-papers/raw/papers/` is being processed.
Produces **exactly one** `analysis` page per raw, plus the concept /
framework / question / synthesis side-effects mandated by the L2 ingest
flow.

> Authority: this prompt is procedural; the schema is in
> [`/AGENTS.md`](../../../AGENTS.md) (L1) and
> [`domains/research-papers/AGENTS.md`](../../../domains/research-papers/AGENTS.md) (L2).
> When this prompt and AGENTS disagree, AGENTS wins.

This sub-prompt encodes the *concrete shape* every paper analysis MUST
take in this L2 — derived from the 2026-05-20 readability pass over
the Vanzo / Bastani / Kestin / SAE worked examples. It is intentionally
lighter than the psychology sub-prompt (no critique stage, no privacy
posture, no lens menu) because the failure modes are different: paper
ingest's risk is *under-extraction* (a wiki page that looks like a
summary instead of a reusable structured object), not hallucination or
privacy leakage.

---

## When invoked

A user dropped a new `<slug>.md` (or PDF extraction) into
`domains/research-papers/raw/papers/`, or said `ingest <path>` against
such a file. Confirm the raw is a primary source (peer-reviewed paper,
arXiv preprint, or technical report) before drafting. Conference talks,
blog posts, and threads belong under `raw/notes/` and produce notes-
style ingest instead.

## Two-pass pipeline

Paper ingest runs two passes in the **same LLM context**:

```
Pass 1   Plan & extract — read raw, draft frontmatter + headline numbers
                          + structural sections. NOT WRITTEN TO DISK.
Pass 2   Apply          — write the analysis + concept side-effects +
                          framework update + (deferred) question check +
                          log entries.
```

A self-critique pass is unnecessary for papers — claims trace to the
single raw and the L2's lint rules (`evidence_quality` + `replicated` +
sources cardinality) already provide post-hoc correction. Spend the
budget on **mechanism extraction** instead.

### Pass 1 — Plan & extract

1. **Read the full source.** Identify title, authors, venue / year /
   DOI or arXiv id. For PDF-extracted markdown, also state which
   figures / tables your extraction includes vs. omits (per L1 §6
   multi-modal red line).
2. **Load conditional context** (token budget):
   - Always: this sub-prompt + L1 + L2 + the snapshot at
     `outputs/snapshots/index-snapshot.md`.
   - Conditional: read the frontmatter (and only relevant section
     bodies) of any `wiki/{concepts,frameworks,questions}/<slug>.md`
     this paper plausibly touches. Use the slug index from the snapshot
     to find them; do not enumerate the folder by `ls`.
   - Just-in-time: the full raw.
   - Target ≤30K tokens before drafting. Papers are smaller than
     therapy transcripts, so the budget is tighter and you can afford
     to read more wiki context.
3. **Draft frontmatter** per L2 §"Required frontmatter additions":
   - `paper: [[<raw-slug>]]`
   - `authors: [author-1-slug, author-2-slug, ...]` (kebab-case)
   - `evidence_quality:` — see rubric below.
   - `replicated:` — see rubric below.
   - `tags:` — include the methodology family (`rct`, `observational`,
     `mechanistic`, `theory`), the domain area (`k12`, `higher-ed`,
     `interpretability`, ...), and any cross-cutting tag.
4. **Draft the four required structural elements** (see §"Required
   analysis structure" below). These four are non-optional in this
   L2 — every paper analysis carries them, in this order, at the top
   of the file.
5. **Draft the standard sections** that follow: Claim / Method /
   Evidence / Limits / Open questions / Wiki cross-references /
   Notes. These mirror L2 §"Ingest flow" step 3.
6. **Plan side-effects.** Output a short plan before writing:
   ```
   Plan:
   - create: [[<paper-slug>-analysis]]
   - update: [[<concept-1>]] — append Appearance row
   - update: [[<concept-2>]] — append Appearance row
   - create: [[<new-concept>]]   ← only if no existing page covers it
   - update: [[<framework>]] — append linked analysis row
   - defer/create: [[<question>]] ← see "Question-page deferral" below
   - update: [[index]]            ← only if a new wiki page was created
   - prepend: domains/research-papers/log.md
   - prepend: log.md (global, only if cross-domain)
   ```
   Wait for the human's go-ahead unless they pre-approved a batch.

### Pass 2 — Apply

1. Write the analysis file to
   `domains/research-papers/wiki/analyses/<raw-stem>-analysis.md`.
2. Update / create each side-effect page in the plan. For concept
   pages, **append** to the "Appearances" table (`| date | analysis |
   note |` row); never overwrite. For framework pages, **append** to
   the "Connected analyses" list.
3. Update `domains/research-papers/index.md` **only** if a new wiki
   page was created (Dataview blocks pick up updated frontmatter
   automatically).
4. Prepend to `domains/research-papers/log.md` per L1 §6 entry
   insertion point (immediately after preamble separator):
   ```
   ## [YYYY-MM-DD] ingest | <author> <year>, <one-line title>
   - Source: [[<paper-slug>]]
   - Pages touched: [[<analysis>]], [[<concept-A>]], ...
   - One-line synthesis — the headline mechanism + the load-bearing limit.
   ```
5. If this ingest's plan declared `cross-domain` in step 6.5 of the
   parent ingest prompt, also prepend to the global `log.md`.

---

## Required analysis structure (the four readability elements)

Every paper analysis in this L2 opens with these four blocks before
the `## Claim` section. They are what makes a researcher landing on
this page able to decide in **30 seconds** whether to read further.

### 1. 30-second TL;DR — `> [!important]` callout

3-6 sentences. State:
- The headline numerical result with its statistical anchor (effect
  size + p-value or N, confidence interval, or κ).
- The *one* methodological choice that makes the claim load-bearing
  (pre-registration, withdrawal probe, crossover design, blind
  labelling, etc.).
- The single most important limit (what the paper does *not* show).

**Voice rule.** Match the L2 persona (precise, neutral, citation-
rich). Never collapse mechanism into effect. Prefer "the authors
show X under condition Y" over "X is true". A reader who only reads
this callout should walk away with the same epistemic stance you
hold after reading the full paper — no inflation, no hedge inflation.

### 2. How to read this paper — `> [!faq]-` collapsed callout

A numbered list (3-7 steps) telling the researcher which sections of
the **raw paper** to read in what order, with a time budget
(`~20 min`) in the heading. Each step names the section anchor (e.g.
"§3.2 (unassisted-exam table)") and **why** that section is
load-bearing for understanding the claim. Include one explicit "skip
unless ..." item if the paper has sections that don't repay attention.

This element is what surfaces the *epistemic backbone* of the paper —
the sections without which the headline number is unfalsifiable.

### 3. Mechanism / design diagram — Mermaid

Exactly one Mermaid diagram showing the **load-bearing mechanism**
the paper instantiates. Pick the diagram type from this decision
table:

| Paper kind | Diagram type | What it shows |
| --- | --- | --- |
| RCT with multiple arms | `flowchart LR` with arms in a subgraph | Each arm's intervention and the shared assessment path. |
| Crossover / within-subject | `flowchart LR` showing group × week swap | Each student/subject experiences both conditions; order balanced. |
| Mechanism / failure-mode paper | `flowchart TD` with branching condition | The decision point that creates the studied effect; outcome nodes colour-coded. |
| Multi-paper / position-on-a-spectrum | `quadrantChart` | Where this paper sits on the two axes that organise the sub-literature. |
| Pipeline / technique paper | `flowchart LR` with rectangles | The pipeline stages and the supervision / loss signal. |
| Time-arc / programme history | `timeline` | Historical evolution; use sparingly — usually belongs in `wiki/syntheses/`, not analysis. |

**Mermaid robustness rules** (these tripped the validator on the
first pass — bake them in):

- Use `<br/>` (not `\n`) for line breaks inside node labels.
- Avoid colons (`:`) inside `quadrantChart` point labels — they
  conflict with the coordinate syntax. Use a kebab phrase instead
  (`Bastani 2024 PNAS math` not `Bastani 2024: PNAS math`).
- Quote node labels that contain spaces or punctuation:
  `A["Identical lecture<br/>(all arms)"]`.
- Keep one diagram per analysis. A second diagram inside the same
  page belongs in a concept page (mechanism) or a synthesis (cross-
  paper comparison).

### 4. Headline-numbers table

A markdown table with the 3-5 numbers a reader will quote back. The
columns are paper-shape-specific; here are the canonical shapes:

| Paper kind | Recommended columns |
| --- | --- |
| Multi-arm RCT | `Condition` × `During-task metric` × `Post-task / withdrawn metric` |
| Crossover | `Outcome` × `Treatment` × `Comparator` × `Statistical anchor` |
| Mechanism / measurement | `Method` × `Headline metric` × `Baseline(s)` |
| Theoretical / position | Skip the table — a quadrantChart usually replaces it; or use a "Result × Status" table |

Each cell carries the number **and its statistical anchor**
(`p < 0.05`, `n.s.`, `95% CI [a, b]`, `κ = 0.71`). Bold the
load-bearing number. If the headline result is a comparison, add a
trailing-arrow gloss (`← the headline penalty`). **Non-significant
findings are facts too**: if the paper measured an outcome and it
came back n.s., the table should still carry that row — silently
omitting it inflates the apparent positive finding (see Kestin 2025
analysis's Likert table for the worked example: engagement and
motivation are p < 0.001 *and* enjoyment and growth-mindset are
n.s., both reported).

---

## Evidence-section depth — "mechanism, not effect"

The L2 persona is "the careful science-historian who extracts the
mechanism, the evidence quality, and the open questions". The
single failure mode the readability elements above don't catch is
**writing an Evidence section that names only the headline effect
size** — restating the TL;DR with citations — and leaving the
mechanism implicit.

Every analysis's **Evidence** section MUST therefore include **at
least one mechanism-level datum** — a number that comes from the
paper's mechanism / process analysis, not from its headline outcome
table. Concrete examples from the current worked analyses:

- **Bastani 2024** — the §3.B *superficial-conversation drift*:
  56% → 67% in GPT Base vs. 42% → 37% in GPT Tutor within the
  first session. This is what makes the "crutch" claim
  quantitative; without it, the −17% headline is a black box.
- **Vanzo 2024** — the §4.3.2 OLS where the treatment-condition
  coefficient becomes n.s. once `words_typed` is added as a
  covariate (`coef = −0.446, p = 0.666`). This is what makes
  "engagement-mediated" quantitative.
- **Kestin 2025** — the §3.2 *time-on-task* distribution
  (median 49 min vs. 60 min; 70% under 60 min). This is what
  makes "more learning in less time" quantitative rather than
  rhetorical.

Rule of thumb: if you cannot extract one mechanism-level number,
you are under-reading the paper. Re-read its Methods/Results
mechanism subsection (or the equivalent "why does the effect
appear?" passage) before drafting.

Note on **quoting facts vs. quoting prose**: the L2 forbids verbatim
prose quotation from copyrighted papers (paraphrase + section
anchor), but reproducing *numerical facts* with their statistical
anchors is required, not forbidden — a statistic is not protected
expression. See L2 §"What's intentionally missing" for the prose
quotation rule.

---

## Evidence-quality rubric

The L2 requires `evidence_quality:` to be one of `rct | controlled |
observational | theoretical | anecdote`. Use this rubric to assign:

| Value | Criteria |
| --- | --- |
| `rct` | Random assignment to ≥2 arms; pre-registered or near-pre-registered primary outcome; explicit comparator; appropriate clustering / SE handling. Crossover and within-subject designs qualify when assignment to condition order is randomised. |
| `controlled` | Quasi-experimental: pre/post with a matched comparison group, regression discontinuity, instrumental variable, or natural experiment. No randomisation but identification strategy is explicit. |
| `observational` | Correlational, large-N or longitudinal, with no exogenous variation. Confounding is the dominant threat. |
| `theoretical` | Derivation, simulation, or position paper. No primary empirical data; cites prior empirics. |
| `anecdote` | Case study, demo, single-subject, blog-post-grade evidence. Use sparingly; most blog-grade material lives in `raw/notes/` not `raw/papers/`. |
| `unknown` | Acceptable but lint flags for human review. Only use when the paper is mixed-method and the dominant evidence type is genuinely unclear after reading. |

Set `replicated:` to:

- `yes` — ≥1 independent replication of the *same* effect with the
  same direction and overlapping magnitude.
- `partial` — direction confirmed by ≥1 adjacent study, but the
  specific magnitude is single-study.
- `no` — single-site, single-study, no published replication yet.
- `unknown` — you haven't checked. Default; replace with one of the
  above by the end of Pass 1.

---

## Question-page deferral (single-paper restraint)

Default behaviour: do **not** create new `wiki/questions/` pages
during a paper's first ingest. A question page is a *long-arc tracker
that spans multiple papers*; minting one when only one analysis
points at it produces a stub that the lint rule flags within 14 days.

Rules:

1. **Open question in the paper itself → "Open questions" section of
   the analysis page, full stop.** Do not lift it to a `wiki/
   questions/<slug>.md` on first ingest.
2. **Existing question page already touches this thread → append a
   row to its "Evidence so far" table** with the new analysis. This
   is the common case once the domain has ≥3 analyses.
3. **A new question genuinely emerges that already had a stub
   waiting for a second anchor → promote now** (create the page, cite
   both analyses). This is the only path that justifies a question-
   page creation from a single ingest.
4. **The human explicitly asks for the question to be tracked →
   create it.** Add a "Status: stub, awaiting second observation"
   line to the body.

The Vanzo 2024 ingest correctly created
[[llm-tutoring-cognitive-offload]] and [[llm-tutoring-equity-impact]]
on first touch because **the L2 already anticipated they would be
revisited by Bastani and Kestin**. That is the exception, not the
rule — only mint questions on first ingest when you have a concrete
2nd-paper plan within the same session or the immediate next ingest.

---

## Concept-page restraint

Three rules to avoid concept-page proliferation:

1. **Search the snapshot first.** Before creating
   `wiki/concepts/<slug>.md`, scan the index snapshot for the slug
   and its plausible aliases. A concept page exists already more
   often than not.
2. **≥3 inbound links rule.** If a paper introduces a term that has
   not appeared in any prior analysis, default to *defining it
   inline* inside the analysis page (with a footnote or quoted
   sentence). Promote it to a concept page only when a 2nd analysis
   touches the same term, OR when the paper's central contribution
   is the concept itself (e.g. introducing "superposition").
3. **Append-only Appearances.** Every concept page carries an
   "Appearances" table at the bottom. Each ingest appends one row;
   never rewrite past rows.

---

## Synthesis trigger (when to draft a cross-paper page)

Synthesis pages are not created speculatively. Trigger them when:

1. **≥2 analyses point at the same open question with sufficient
   evidence to weight the question.** Synthesis braids them into a
   single "what we now know / what we don't" picture.
2. **A paper closes / reframes a thread across ≥2 prior analyses.**
   Synthesis records the reframe; the analyses themselves are
   unchanged.
3. **The human asks for a comparison.** Then synthesis is the
   filing-back artifact (per L1 §2.2 query flow).

Synthesis structure follows the same TL;DR-first principle as
analysis (see the [[llm-tutoring-causal-evidence-2024-2025]] worked
example).

---

## Framework-page touch

Every paper analysis updates **exactly one** framework page (or
zero, if the paper sits outside any tracked programme):

1. Append a row to the framework's "Sub-programmes" or "Connected
   analyses" table.
2. If the framework's `programme_status:` should change (a paper
   reactivates a dormant programme, or supersedes the framing),
   change it and add a `> [!important] Status change YYYY-MM-DD`
   callout at the top of the framework page summarising why.
3. Frameworks are not created on first ingest — they need ≥3
   analyses to earn the page. Until then, keep the structure inside
   the relevant analysis's "Notes" section.

---

## Quality bar (final pass before commit)

A correct paper ingest produces:

1. **Exactly one** `analysis` file per raw, named `<raw-stem>-
   analysis.md`, with `sources: ["[[<raw-slug>]]"]` of length 1.
2. The **four readability elements** (TL;DR + How-to-read +
   Mermaid + headline table) are present, in order, before
   `## Claim`.
3. `evidence_quality:` and `replicated:` are set per the rubrics
   above (neither left at `unknown` unless genuinely ambiguous).
4. The **Evidence section carries ≥1 mechanism-level number** (per
   §"Evidence-section depth — 'mechanism, not effect'" above), not
   only restatements of the headline effect. If the paper has a
   "why does the effect appear?" subsection (Bastani §3.B,
   Vanzo §4.3, Kestin §3.2 / §3.3), at least one of its numbers
   must land in the analysis.
5. Every concept / framework / entity named in the analysis body
   has been updated in its own wiki page (Appearances / Connected
   analyses tables extended).
6. `wiki/questions/` is *not* touched on first ingest unless a
   pre-existing stub justifies it (see §"Question-page deferral").
7. `index.md` is refreshed only if a new wiki page was created.
8. `log.md` appended per L1 §2.1 with a one-line synthesis that
   names the **headline mechanism + the load-bearing limit** — not
   just the title.
9. No verbatim **prose** quoting from the paper body in any wiki
   page; paraphrase + section anchor (`§4.2` / `[[<paper>#§4.2]]`)
   instead, per L2 §"What's intentionally missing". Reproducing
   **numerical facts** (effect sizes, p-values, CIs, correlations,
   percentage drifts) with their statistical anchors is required,
   not forbidden — a statistic is not protected expression.

If any of (1)-(9) is missing, the ingest is incomplete — do not
output a "done" message.

---

## Worked examples to study

When in doubt about depth or voice, open one of these analyses and
copy the structural shape:

- [[2024-bastani-generative-ai-guardrails-analysis]] — the fully-
  worked multi-arm RCT example; mechanism flowchart + headline
  table + How-to-read all visible.
- [[2025-kestin-ai-tutoring-active-learning-analysis]] — crossover-
  design example; shows how the diagram makes a within-subject
  design legible at a glance.
- [[2024-vanzo-gpt4-homework-tutor-analysis]] — single-site,
  smaller-N example; shows the `quadrantChart` use for positioning
  one paper against its sub-literature.
- [[2024-anthropic-sparse-autoencoders-analysis]] — mechanism /
  technique example (interpretability, not education); shows the
  pipeline flowchart pattern.
