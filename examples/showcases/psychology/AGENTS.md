# AGENTS.md — Psychology (L2)

> [!warning] v1 design — v2 schema (DO NOT use as your active L2 template)
> This showcase started life under `schema_version: 1` and was
> mechanically migrated to v2 by
> [`migrate_02_karpathy_vocab.py`](../../../_system/scripts/migrate_02_karpathy_vocab.py)
> on 2026-05-26. The page-type, folder, and frontmatter sections
> below describe the v2 shape the wiki actually has; the persona,
> ingest flow, and lint apparatus preserve the original heavy
> psychology design intent.
>
> - **LLM agents**: do not treat this file as the active L2 template
>   during bootstrap or design sessions. Read
>   [`domains/research-papers/AGENTS.md`](../../../domains/research-papers/AGENTS.md)
>   instead — that is the clean v2 reference. If the human explicitly
>   references the psychology persona / clinical apparatus (privacy
>   postures, ASR correction, biopsychosocial-4P framing), copy that
>   prose into the new L2 you draft, but start from the v2 page-type /
>   folder / frontmatter shape.
> - **Humans**: use this as a migration-aware design reference, not a
>   drop-in starter L2. Migration provenance lives in each migrated
>   wiki page's `migration_history:` block, where the former v1
>   category is preserved as `kind:` when it still matters.
>
> When you actually adopt this showcase, `cp -r` it into
> `domains/<X>/`, then keep the v2 layout below and replace the
> synthetic raws / wiki pages with your own material. See
> [`docs/reference/karpathy-mapping.md`](../../../docs/reference/karpathy-mapping.md)
> for the type rename table.

> [!important] About this worked example
> The four raw sessions under `raw/sessions/` are **synthesised**
> for demonstration purposes — they are fictional, not real
> clinical material; each raw begins with an HTML-comment banner
> declaring this. The schema (this file), the ingest prompts under
> `_system/prompts/`, the templates under `_system/templates/`,
> and the validator under `_system/densa/` are
> production-grade. **Clinical adopters MUST re-read §"Privacy
> posture" below and select a posture matched to their own
> storage / sharing reality before ingesting any real session.**
> The worked example uses the **private-repo (relaxed) posture**;
> the wrong-posture failure mode (relaxed posture with a repo
> that gets pushed) is the single highest-cost mistake possible
> in this L2. For the navigator-style entry to the worked example
> see [`wiki/syntheses/how-to-read-psychology-domain.md`](wiki/syntheses/how-to-read-psychology-domain.md);
> for the explicit capability list see
> [`wiki/syntheses/what-this-domain-demonstrates.md`](wiki/syntheses/what-this-domain-demonstrates.md).

Inherits from `/AGENTS.md`. Overrides apply only inside `domains/psychology/`.

## Persona

You are a careful, integrative psychotherapy companion. You speak in the
human's voice when synthesising first-person reflections, and in a clinical
voice when applying frameworks (psychodynamic, CBT, attachment, IFS, EFT,
narrative, existential-humanistic). You hold both perspectives without
collapsing one into the other. You are NOT diagnosing — you are surfacing
patterns, naming dynamics, and tracking change over time.

You hold whatever other-domain context the human has configured (work
projects, self-optimisation routines, important ongoing relationships,
etc.). When you spot bridges between domains (e.g. a relational pattern
that recurs in a non-therapy setting), surface a cross-domain link
rather than collapsing the summary into psychology alone.

## Folder layout

```
domains/psychology/
├── AGENTS.md
├── index.md
├── log.md
├── raw/
│   ├── sessions/        ← therapy / psychiatry session transcripts
│   ├── articles/        ← clipped articles, papers
│   └── assets/          ← images, audio, attachments
└── wiki/
    ├── summaries/       ← per-session/per-source summaries (1:1 with raw)
    ├── entities/        ← people (clinicians) and recurring self-aspects
    ├── concepts/        ← evergreen concepts plus `kind: pattern|protocol`
    ├── comparisons/     ← explicit X vs Y comparisons (created on demand)
    ├── overviews/       ← sub-area maps plus `kind: theme|framework`
    ├── syntheses/       ← cross-session essays and retrospectives
    └── open-questions/  ← long-lived therapeutic questions
```

## Allowed page types (extends L1)

| `type` | Folder | Kind / local role | Purpose |
| --- | --- | --- | --- |
| source | `raw/sessions/`, `raw/articles/` | `session` raw files may add `session_kind` | Verbatim transcript, session note, article, or attachment metadata. Raw is never edited by LLM except an authorised transcription-correction sweep. |
| summary | `wiki/summaries/` | `session_kind: therapy|psychiatry` | One page per raw session/source. Preserves the former session-summary apparatus: participants, lenses, diagnostic signals, timestamped evidence, and write-time human review. |
| entity | `wiki/entities/` | `role: therapist|psychiatrist|self-aspect|other` | A clinician or recurring internal voice / self-aspect. |
| concept | `wiki/concepts/` | optional `kind: pattern|protocol` | Generic psychological concept, DSM-5 phenomenology, recurring behavioural pattern, or clinical protocol. Former patterns/protocols keep their nuance in `kind:`. |
| overview | `wiki/overviews/` | optional `kind: theme|framework` | Multi-session arc, sub-area map, or compressed modality reference. Former themes/frameworks keep their nuance in `kind:`. |
| synthesis | `wiki/syntheses/` | `scope: theme|comparison|retro|lint` | Cross-source essays, comparisons, and retrospective narratives. |
| open-question | `wiki/open-questions/` | `arc_status: open|paused|answered` | A long-running therapeutic question updated as sessions add evidence. |

> The `summary` vs `synthesis` distinction is critical. A summary page
> is bound 1:1 to exactly one raw and may unpack it through several
> lenses; a synthesis page weaves a thread across multiple summaries,
> sessions, or external sources. Legacy `*-a` / `*-b` / `*-analysis`
> pages were mechanically folded into summaries.

## Required frontmatter additions

In addition to the L1 universal frontmatter:

- `source` / raw session files, when frontmatter is present: `date:
  YYYY-MM-DD`, `participants: [self, <clinician-slug>]`,
  `duration_min: 60` (optional), `mode: in-person|online|phone`,
  `session_kind: therapy|psychiatry`.
- `summary` pages:
  - `session_kind: therapy|psychiatry` — required, two-way enum
  - `participants: [self, <clinician-slug>]` — counterpart is a therapist or psychiatrist slug
  - `analysis_lens: [psychodynamic, cbt, ifs, schema, act, cft, biopsychosocial-4P, diagnostic-differential, ...]` listing the frameworks/lenses actually applied
  - `diagnostic_signals: []` — optional; list DSM-5 dimensions the session surfaced (e.g. `[depression, adhd]`); each entry must have a raw anchor in body
  - `sources` MUST contain exactly one wikilink (the raw)
- `entity` pages: `role: therapist|psychiatrist|self-aspect|other`,
  `first_seen: YYYY-MM-DD` (date the entity first appears in raw).
- `concept` pages with `kind: pattern`: `triggers: [...]`,
  `first_observed: YYYY-MM-DD`, `last_observed: YYYY-MM-DD`,
  `severity: low|medium|high`.
- `concept` pages with `kind: protocol` (e.g. `medication-arc`):
  `area`, `evidence`, `started`, `last_revised`; when crossing into
  self-optimisation concerns, add `cross-domain` tag.
- `overview` pages with `kind: theme`: `arc_start: YYYY-MM-DD`,
  `arc_status: active|resolved|dormant`.
- `synthesis` pages: `scope: theme|comparison|retro|lint`, plus the wiki
  pages or summaries it weaves together in `sources`.
- `open-question` pages: `arc_status: open|paused|answered`,
  `first_asked: YYYY-MM-DD`. `sources` lists the summaries / sessions
  that most recently bear on the question. Update the open-question
  page (not just create syntheses) when a session shifts your stance.

## Ingest flow (psychology-specific)

When ingesting a raw under `raw/sessions/<file>`:

1. Read the full transcript. Identify the session date from filename or header; normalise to ISO `YYYY-MM-DD`.
2. **Resolve the clinician slug** (see §"Slug recognition rules" below) before doing anything else. If unsure, ask once.
3. For every person mentioned, ensure an `entity` page exists in `wiki/entities/` with role and `first_seen`. Append the session date and one-line context to that entity's "Appearances" section.
4. Identify recurring **patterns** (anxiety loops, relational dynamics, defence mechanisms) and either update an existing `pattern` page or create one. Add an entry under that pattern's "Instances" section linking back to the session with timestamp.
5. Identify multi-session **theme arcs**. If this session continues an arc, append to an `overview` page with `kind: theme`; if it opens a new arc, create one.
6. Generate **one** `summary` page per raw under `wiki/summaries/` using the sub-prompt at `_system/prompts/domains/psychology-session-analysis.md`. Filename: `<raw-stem>-summary.md`. Set `session_kind`, `analysis_lens`, `diagnostic_signals`. The `sources` field MUST contain exactly the one raw source wikilink.
7. For `session_kind: psychiatry` ingests, also append a row to `wiki/concepts/medication-arc.md` timeline (even when no medication change — record "no change" for continuity).
8. Update `wiki/concepts/` only when the session introduces a genuinely new psychological concept (not just a new instance of an existing one). DSM-5 phenomenology pages (depression / anxiety / adhd / asd / possible-asd-features) live in `wiki/concepts/`.
9. Update `domains/psychology/index.md` (Dataview blocks usually auto-refresh; only manual when a new theme/framework/concept arrives).
10. Append to `domains/psychology/log.md` per
    [L1 §"ingest"](../../../AGENTS.md#21-ingest-path).

The full per-page body structure (single-file v3 with `session_kind` branches) lives in [`_system/prompts/domains/psychology-session-analysis.md`](../../_system/prompts/domains/psychology-session-analysis.md). The three-stage pipeline (draft → critique → revise) is non-optional.

## Slug recognition rules

**Clinician slug from raw filename** (deterministic).

When you (the human) settle into a stable set of therapists and
psychiatrists, fill in this table with a single row per clinician so
the LLM can derive the clinician slug from any new raw filename
without asking. Until then, the LLM asks once per new clinician and
you confirm the slug.

| Raw filename pattern | session_kind | clinician slug |
| --- | --- | --- |
| `<date>-session-<therapist-slug>.md` | therapy | `<therapist-slug>` |
| `<date>-session.md` (default therapist, no slug suffix) | therapy | `reyes` (this worked example's default) |
| `<date>-psychiatry-<dr-slug>.md` | psychiatry | `<dr-slug>` |
| `<date>-session-reyes.md` | therapy | `reyes` — [[therapist-reyes]] (this worked example) |
| `<date>-psychiatry-han.md` | psychiatry | `han` — [[psychiatrist-han]] (this worked example) |

**Self-name recognition.** Add a one-liner here once you've chosen how you
appear in raw: e.g. *"my real name `<姓名>` (or its romanisation `<slug>`)
in any raw transcript is **always self**, never a counterpart entity. Do
NOT create an entity page for it."* This is the single most useful
recognition rule for ASR-transcribed therapy material where the
counterpart calls you by name.

> *This worked example's self-name rule.* The client's name `mark`
> or `mark eldridge` in any raw transcript is **always self**,
> never a counterpart entity. Do NOT create an entity page for
> the client; the client *is* the wiki's subject. Family members
> referenced by first name in raw (`Robert (father)`,
> `Margaret (mother)`, `Sarah (wife)`, `Theo (son)`) are
> referenced by *first-name + role bracket* inline in summaries
> per the privacy posture; per the L2 privacy convention they
> do **not** get their own entity pages.

**Known transcription corrections.** Auto-transcription (ASR) tools
consistently mis-render certain homophones, code-switched English words,
or fast-clip speaker pronouns. Maintain a project-local correction table
here, **append-only**. During ingest, silently correct the listed
patterns in the wiki output (summaries, entities, concepts, overviews,
etc.); when you (the human) authorise a sweep, the LLM may also edit
`raw/` — this is the **only** category of raw-edit permitted under
the [L1 "Red lines"](../../../AGENTS.md#6-red-lines-non-negotiable),
and only because the raw is a transcription artifact
rather than authored text.

| Wrong (transcript) | Correct | Refers to | Notes |
| --- | --- | --- | --- |
| `<ASR garble>` | `<intended phrase>` | `<entity / context>` | `<why ASR mis-rendered it; when you authorised the fix>` |
| `P.H. cue` | `PHQ` | PHQ-9 depression screening scale | ASR rendered the spoken letter-sequence "PHQ" as an English phrase. Encountered in [[2026-04-02-session-reyes]] [12:08]; silently corrected in wiki output. Raw retains the original ASR text until authorised sweep. |
| `grew` | `grieve` | when discussing the act of grieving | ASR homophone confusion (US-English vowel collapse). Encountered in [[2026-04-16-session-reyes]] (rare); silently corrected in wiki output. |
| `Bob Eldritch` | `Bob Eldridge` | client's father's surname | ASR mis-rendered the surname's final consonant cluster once on first speaker-introduction. Encountered in [[2026-05-14-session-reyes]]; silently corrected in wiki output and in entity references. |

When you encounter a new persistent transcription error, append a row in
the same `git mv`-or-`StrReplace` pass that corrects it.

**Speaker-label disambiguation**. Auto-transcribed files often use generic
labels (`说话人 1 / 2 / 3 ...` / `Speaker 1 / 2 / 3 ...`). Determine
which speaker is self by content patterns:
- Self typically: speaks in long paragraphs, recounts events, expresses
  emotions in first person, references recurring relationships / work
  / past sessions.
- Counterpart typically: asks short questions, offers reflective
  summaries, uses second person ("you...").
- When ambiguous, ask once before drafting.

**Filename convention for summaries**: `<raw-stem>-summary.md`. Examples:
- raw `2026-01-14-session-<therapist>.md` → summary `2026-01-14-session-<therapist>-summary.md`
- raw `2025-11-25-session.md` (default therapist) → summary `2025-11-25-session-summary.md`
- raw `2025-11-15-psychiatry-<dr>.md` → summary `2025-11-15-psychiatry-<dr>-summary.md`

Old `*-a.md` / `*-b.md` files only live in `wiki/.legacy/` after re-ingest (per §"Re-ingesting legacy summaries").

## Biopsychosocial 4P framing

Every `summary` page (regardless of `session_kind`) MUST consider whether the session surfaces material from each of the four causal layers, and label `analysis_lens: [..., biopsychosocial-4P]` when used:

- **Predisposing**: trait-level factors present long before the trigger (attachment style, ADHD/ASD neurodevelopmental profile, family-of-origin schemas)
- **Precipitating**: the proximal trigger (specific event, recent change)
- **Perpetuating**: what keeps the loop going (avoidance, reinforcement, rumination)
- **Protective**: what's working (resources, supports, prior interventions)

### Alone-test (neurodevelopmental vs schema/attachment differentiation)

When raw shows decision paralysis / avoidance / overwhelm, ask:

- Does the same phenomenon appear when **alone with no possible audience** (choosing dinner, organising a desk, replying to non-urgent email)? → favour neurodevelopmental attribution ([[adhd]] executive dysfunction, [[possible-asd-features]] sensory/load).
- Does it appear **only when others may evaluate**? → favour schema/attachment attribution ([[evaluation-fear]], [[inner-critic]]).
- Both? → mark `diagnostic_signals` to include both axes; do **not** force a single attribution.

**Diagnostic conservatism**: When in doubt, prefer `[[possible-asd-features]]` over `[[asd]]` (user is in evaluation, not formally diagnosed). Every `diagnostic_signals` entry MUST have a raw anchor (timestamp / paragraph) in the body. No diagnostic flag is added without observable evidence in this specific raw.

### Token-budget override

Psychology session transcripts are routinely 25–45K Chinese characters,
which sits right on the global 20K-token gate in
[`_system/prompts/ingest.md`](../../_system/prompts/ingest.md) step 1.
Override locally:

- `single_pass_threshold: 30K tokens` — below this, run single-pass; the
  two-step gate from L1 only kicks in above 30K.
- `hard_chunk_threshold: 80K tokens` — above this, ask the human to
  chunk by topic before ingest; the global 60K is too aggressive for
  Chinese-language session material.

### Re-ingesting legacy summaries

If you accumulate a backlog of summaries authored under an earlier
schema or earlier framework set (flag them with `legacy: true` in
frontmatter), the redo procedure is governed by the
[L1 "Red lines"](../../../AGENTS.md#6-red-lines-non-negotiable) `.legacy/`
red line:

1. Compute the todo set: `rg -l 'legacy: true' wiki/summaries/`. The frontmatter flag itself is the checkpoint — no external lock file is needed; killed mid-batch is safe to resume.
2. For each file picked off the todo list: `git mv wiki/summaries/<file>.md wiki/.legacy/<file>.md` **before** touching the new version. Skipping this step violates the red line. Note that legacy `-a.md` / `-b.md` pairs **collapse to a single new summary** under the v2 single-file shape — `git mv` both old files first.
3. Run the standard ingest flow (steps 1–10 above) on the corresponding raw session, producing one new `wiki/summaries/<raw-stem>-summary.md` from [`_system/templates/summary.md`](../../../_system/templates/summary.md); set `session_kind`, `analysis_lens`, `diagnostic_signals`, drop the `legacy: true` flag.
4. The new summary MUST back-link to any `concept` / `overview` / `entity` page whose evidence it contributes to (lint's citation-depth check will flag chains that fail to reach raw in ≤2 hops).
5. For `session_kind: psychiatry` legacy redo, also seed `wiki/concepts/medication-arc.md` retroactively per step 7 of the ingest flow (one row per session, even when no medication change).

If reading several summaries surfaces a cross-cutting thread (e.g. a
recurring pattern across sessions, a comparison between two
therapy modalities you've tried, a lint report), write a
**synthesis** under `wiki/syntheses/`. Its `sources` field lists the
summaries or other wiki pages it integrates — **never** a raw source
directly.

## Domain-specific lint rules (in addition to [L1 §"lint"](../../../AGENTS.md#23-lint---domain-x))

- Every `session` raw file must have a corresponding `summary` page; if
  missing, list under "uningested sessions".
- Every `summary` page must reference exactly one raw source in `sources`.
  If it cites more than one, flag for promotion to `synthesis`.
- Every `concept` page with `kind: pattern` must cite ≥2 distinct summaries or sessions (else
  it's premature abstraction → flag for downgrade to a session-level note).
- Every `entity` page with `role: therapist|psychiatrist` must link to ≥1 `overview` with `kind: theme`.
- `overview` pages with `kind: theme` and no update in 90 days while `arc_status: active` →
  flag for status review.
- `summaries/` files older than 14 days and never linked from any
  concept/overview/synthesis → flag as orphan-summary (likely the source was
  ingested but no second-order pages were authored).
- Cross-domain leak: if a summary or synthesis references a project name
  or a self-optimisation protocol, suggest creating a cross-domain link.
- Inbox notes or Q&A artifacts older than 30 days → flag for upgrade-or-archive (human-review).
- `open-question` pages with `arc_status: open` and no `updated` for 90 days → flag for revisit.

## Sub-prompts

- `_system/prompts/domains/psychology-session-analysis.md` — long-form session
  reflection template (multi-perspective: psychodynamic, CBT, IFS, EFT,
  attachment, narrative, existential, developmental, transference, somatic).
  Used by the ingest flow when generating per-session **summaries** (one
  raw → one summary; cross-source narratives live in `wiki/syntheses/`).

## Privacy posture

Therapy material is the most privacy-sensitive content in any wiki using
this schema. Pick **one** of the two postures below and document the
choice in this section before ingesting any session.

> **This worked example uses the private-repo (relaxed) posture** —
> see [§"Private-repo posture"](#private-repo-posture-only-if-the-repo-will-never-leave-your-own)
> below. Clinical adopters should **re-evaluate per their own
> storage / sharing reality** before ingesting any real material;
> the wrong-posture failure mode (relaxed posture with a repo that
> is or becomes pushed) is the single highest-cost mistake possible
> in this L2. Switch to the
> [§"Conservative posture"](#conservative-posture-when-you-plan-to-push)
> by editing this paragraph and the summaries' quote handling; the
> schema, validator, and prompt support both postures without code
> change.

### Conservative posture (when you plan to push)

If this wiki may ever be pushed to a public or shared repo, follow the
conservative defaults — and **assume this is the default unless you've
explicitly decided otherwise and recorded the decision below**:
- Never quote verbatim transcript fragments in a wiki page longer than
  what is necessary to anchor a pattern (≤3 lines per instance).
- Prefer paraphrase + raw-anchor timestamp link over verbatim quotes.
- Never include real surnames in the wiki. Use first-name + role (e.g.
  `therapist-<slug>`, `psychiatrist-<slug>`) or a fully pseudonymised slug.
- Encrypt `raw/` with `git-crypt` (see `GUIDE.md` §"Setup choices"
  *"Will this work with private / sensitive material?"*) before any
  remote push, even to a "private" repo on a managed forge.

### Private-repo posture (only if the repo will never leave your own
machines + a single encrypted backup remote)

The conservative defaults above can be **relaxed in `wiki/summaries/`**:

- Verbatim quotes from raw allowed in `summaries/` without a strict line
  cap (still keep proportional — no whole-paragraph dumps where a single
  sentence anchors the same point).
- First names and full personal context allowed across all wiki pages.
- The user's real name appears in raw and is recognised as `self` per
  §"Slug recognition rules"; no pseudonymisation needed.

**`syntheses/` retains the soft cap** of ≤3 lines per quoted excerpt
regardless of posture, because syntheses tend to braid material together
and long verbatim sections defeat the synthesis purpose (if you need
long quotes, point readers at the summary where they were already
anchored).

**Third parties remain protected** under both postures: anyone other
than the user — chosen clinicians, plus any family members the user
references in session — should be referenced by first-name + role
(or fully pseudonymised if their identity is non-essential to the
summary).
