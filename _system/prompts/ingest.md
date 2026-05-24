# Prompt: ingest

Use this prompt body when the human says `ingest <path>` or drops a new
source. The procedure is the canonical realisation of `/AGENTS.md` §2.1; if
that file changes, this prompt loses authority — re-read the schema.

## Input

- **Source path**: `<path>` — a file under `domains/<X>/raw/...` (or a path
  that must first be moved there per routing rules).

## Output (in order)

1. **Estimate source size** before reading the full source. Count bytes;
   approximate tokens as bytes / 4 for English prose. For **CJK content**
   (Chinese / Japanese / Korean) the conversion is different: each CJK
   character is ~3 UTF-8 bytes and tokenises at ~1 token, so use
   **tokens ≈ characters** (or equivalently `bytes / 3`) — see
   [`docs/CJK-WORKFLOW.md`](../../docs/CJK-WORKFLOW.md) §1 for the full
   ratio table. Apply the **token-budget gate**:
   - **≤ 20K tokens** (≤ ~80 KB English prose, or ≤ ~20K CJK characters):
     proceed straight to step 2 (full read + plan + apply in one pass).
   - **> 20K tokens** (large transcripts, long PDFs): switch to **two-step
     ingest**.
     - Step A: read the full source, output a "key takeaways + entity
       list" pre-summary (≤ 500 words). Do not draft any wiki edits yet.
       Wait for the human to confirm the takeaways match their reading.
     - Step B: only after confirmation, run steps 2–11 below using the
       pre-summary as your working memory anchor; you may re-read
       targeted portions of the source as needed.
   - **> 60K tokens**: ask the human to chunk the source manually before
     ingest (e.g. split a 4-hour meeting transcript by topic). The wiki
     is not the place to enforce structure on truly oversized raw.
2. **Read** the full source (or, in two-step mode, anchor on the
   pre-summary). If it is non-text (image, PDF, audio transcript), state
   explicitly what you can vs. cannot read.
3. **Identify domain** by the routing rules in `/AGENTS.md` §5. Confirm with
   the human only if ambiguous.
4. **Read the corresponding `domains/<X>/AGENTS.md`** for the domain-specific
   ingest flow. Follow it.
4.5. **Load the domain analysis sub-prompt** if one exists. Glob
    `_system/prompts/domains/<domain>-*-analysis.md` (e.g.
    `_system/prompts/domains/psychology-analysis.md`,
    `_system/prompts/domains/research-papers-paper-analysis.md`,
    `_system/prompts/domains/workspace-meeting-analysis.md`); if **any**
    match the current `<domain>` (and, where multiple match, the source
    bucket — e.g. a `domains/workspace/raw/meetings/<file>` matches
    `workspace-meeting-analysis.md`), read it end-to-end before
    drafting the plan in step 6. These sub-prompts carry the
    **load-bearing per-domain procedure** the L2 AGENTS.md only
    sketches (e.g. psychology's biopsychosocial-4P framing, workspace's
    decision-record extraction). Skipping them produces analyses that
    look schema-compliant but miss the domain's actual reasoning shape.
    If no sub-prompt matches, proceed with the generic procedure below.
5. **Read `domains/<X>/index.md`** to understand what wiki pages already
   exist. Bias heavily toward updating existing pages over creating new ones.
6. **Plan the touched pages** before writing. Output a short plan:
   ```
   Plan:
   - update: [[entity/...]]
   - update: [[pattern/...]]
   - create: [[concept/...]]
   - create: [[synthesis/...]]
   - update: [[index]]
   - prepend: log.md (×2 — domain + global if cross-domain;
     "prepend" because L1 §6 logs are reverse-chronological — newest
     first at the entry insertion point. "Append" in older prompts
     is a legacy synonym for the same write.)
   ```
   Wait for the human's go-ahead unless they have already pre-approved
   batch ingest.
6.5. **Cross-domain detection**. Inspect the plan: do the touched
    pages span ≥2 domains, or do their `sources:` / inline wikilinks
    resolve into ≥2 domains? If yes, every newly-created or substantially-updated
    page in this ingest MUST receive `cross-domain` in its frontmatter
    `tags:` list at write time. Do not defer this to a future lint
    run — the global `index.md` MOC's cross-domain Dataview block
    depends on the tag being present immediately so the human can see
    the cross-pollination as soon as it happens.
7. **Apply edits**. For every page touched, update `updated:` frontmatter to
   today. Cite the source via wikilink in `sources:` or inline.
   - When the plan in step 6.5 declared cross-domain, write the
     `cross-domain` tag into the new/updated pages' frontmatter as
     part of this step. Verify the tag is present before moving on.
8. **Refresh `domains/<X>/index.md`** only if a new wiki page was created
   (Dataview blocks pick up most updates automatically).
9. **Prepend to `domains/<X>/log.md`** — insert the new entry immediately
   after the YAML frontmatter (and before any `# <Title>` H1 / intro prose),
   so newest is first per L1 §6:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   - Source: [[<path>]]
   - Pages touched: [[…]], [[…]]
   - One-line synthesis.
   ```
10. **If cross-domain**, also prepend a one-liner to the global `log.md`
    using the same top-of-file insertion point.
11. **Suggest a commit message** for the human:
    `ingest(<domain>): <date> <slug>`.

## Hard rules

- Do NOT modify the source file at `<path>`.
- Do NOT delete any wiki pages. Use deprecation per `/AGENTS.md` §4.
- Do NOT fetch the web mid-ingest unless the human explicitly asks.
- Do NOT inflate. Prefer precision over comprehensiveness; a 5-page edit is
  better than a 15-page edit padded with restatements.
- Quoting raw transcripts (especially psychology) is bounded by the
  domain-specific privacy posture.

## Quality bar

A good ingest produces:
- **At least one entity/pattern/concept page updated** — not just a
  freshly-minted synthesis floating in isolation.
- **Wikilinks both ways** — the new synthesis links back to the source AND
  to every entity/pattern/concept it touches; those pages link forward to
  the synthesis.
- **No duplicate concepts** — before creating `wiki/concepts/<X>.md`,
  search for existing pages by slug AND by aliases in their bodies.
- **Cross-domain tagged at write time**, not after lint — if the plan
  spans domains, every touched page surfaces the tag immediately.
