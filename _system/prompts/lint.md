# Prompt: lint

Use this prompt body when the human says `lint` or `lint --domain <X>`.
Canonical procedure for `/AGENTS.md` §2.3.

## What this command will write (schema contract)

| Path                                          | When                          | Why                                                  |
|-----------------------------------------------|-------------------------------|------------------------------------------------------|
| `outputs/lint/<YYYY-MM-DD>.md`                | always                        | the lint report itself                               |
| `outputs/snapshots/index-snapshot.md`         | always                        | machine-readable index mirror (refreshed every lint) |
| `domains/<X>/wiki/<page>.md`                  | additive auto-fix only        | missing cross-references / cross-domain tag / index entry |
| `domains/<X>/log.md`                          | always                        | audit trail                                          |
| `log.md`                                      | always                        | global lint timeline                                 |

> This table mirrors `densa.schema.OPERATIONS['lint'].writes`.
> AGENTS011 warns on drift. Destructive fixes (page deletion, rename,
> rewrite) are *always* surfaced as human-review, never auto-applied.


> **Note**: the pre-commit hook (`_system/hooks/pre-commit` →
> `python -m densa --staged`) already enforces raw immutability,
> `log.md` append-only, universal frontmatter presence, `analysis`
> `sources` cardinality, and wikilink resolvability at commit time.
> Lint here focuses on higher-order semantic and provenance issues a
> static validator can't see.

## Input

- **Scope**: global (all domains) or single `<domain>`.
- Optional flag `--quick` to limit to mechanical checks (no narrative
  contradiction analysis).

## Procedure

1. **Enumerate the wiki**. List every wiki page in scope with:
   `(path, type, status, updated, inbound-link-count)`.
2. **Read the previous lint report** if one exists. Glob
   `outputs/lint/*.md`, pick the most recent by ISO date, and load its
   "## Domain-specific findings" + "## Mechanical findings" + "##
   Provenance findings" + "## Narrative findings" sections into working
   memory. This becomes the **baseline** the new report compares
   against. If no prior report exists, mark this run as `baseline` in
   the report frontmatter (`tags: [lint, baseline]`).
3. **Mechanical checks (residual after pre-commit)**:
   - **Orphans**: pages with 0 inbound wikilinks and no listing in
     `index.md` Dataview groupings.
   - **Stubs**: pages with body < 30 words AND `created` more than 14 days
     ago.
   - **Broken wikilinks** *(primarily enforced by pre-commit; lint
     re-runs only when pre-commit was bypassed)*: links pointing to
     non-existent files.
   - **Frontmatter compliance** *(primarily enforced by pre-commit;
     lint re-runs only when pre-commit was bypassed)*: every page has
     the universal fields (§3 of L1 schema) and the L2-required
     fields.
   - **Index drift**: pages on disk not surfaced by any Dataview block in
     `index.md`, or vice versa.
   - **Duplicate concepts**: page slugs and titles that look like
     near-duplicates (Levenshtein similarity, shared key terms).
   - **Aliases coherence**: scan every wiki page's frontmatter
     `aliases:` list. If two pages of **different `type`** declare the
     same alias (e.g. one `concept` and one `entity` both claim
     `"inner critic"`), flag both as `human-review` — the wikilink
     resolver will pick non-deterministically and the semantics will
     drift.
   - **`compiled_against` lag**: current L1 `schema_version: 1`. Any
     wiki page whose `compiled_against < schema_version` → flag as
     `human-review` (a re-ingest may be needed). At v1 this should
     produce zero hits; the rule exists so v2 migrations have a
     ready-made audit gate.
4. **Provenance integrity checks** (the high-leverage anti-poisoning gates):
   - **Citation depth**: for each non-trivial claim in any
     `pattern` / `theme` / `synthesis` page, at least one wikilink
     chain must reach a `raw/` file in ≤2 hops. Specifically:
     either the page itself cites a raw file directly, or its `sources`
     contain wiki pages whose own `sources` reach raw. Flag any claim
     whose only path to raw is ≥3 hops as `human-review` — citation
     drift makes claims unverifiable.
   - **Quote integrity**: every `> [!quote]` block (per L1 §4.1) in
     any wiki page MUST be locatable verbatim (whitespace-tolerant)
     in at least one raw file referenced by the page's `sources`
     chain. Use `git grep -F` or equivalent on the cited raw paths.
     If the quote text isn't found, the LLM may have invented it —
     flag as `human-review` with both the quoted text and the searched
     raw paths.
   - **`last_validated` TTL**: every page with `type` in
     {concept, framework, protocol, entity} whose `last_validated`
     is older than 180 days → `human-review` with note "re-read the
     cited sources or accept that this page is stale".
5. **Narrative checks** (skip when `--quick`):
   - **Contradictions**: pairs of pages making opposite claims about the
     same entity/concept. Cite both.
   - **Stale claims**: pages whose claims are superseded by a newer
     `[[source]]` or `[[synthesis]]` not yet linked.
   - **Missing pages**: concepts mentioned in ≥2 wiki pages with no own
     page.
   - **Missing cross-references**: page A discusses entity B but does not
     link `[[B]]`.
   - **Cross-domain tag candidates**: any wiki page whose `sources:`
     field references raw or wiki paths from ≥2 distinct domains, or
     whose body contains wikilinks resolving into ≥2 domains, **and**
     does not already carry the `cross-domain` tag in frontmatter.
     Propose adding the tag (auto-applicable as an additive frontmatter
     fix). The global `index.md` Dataview block depends on this tag, so
     missing tags = invisible cross-pollination.
   - **GUIDE ↔ AGENTS drift**: read `GUIDE.md` §"Cheat sheet" table;
     for each row, locate the corresponding canonical statement in
     `AGENTS.md` (or `domains/<X>/AGENTS.md`). If the two disagree,
     flag as `human-review`. AGENTS wins per L1 §1 authority rule,
     but the LLM should suggest the textual delta to bring GUIDE back
     in line.
6. **Domain-specific checks**: read the `Domain-specific lint rules`
   section in each `domains/<X>/AGENTS.md` and run those too.
6.5. **Q&A spot-check ingestion**. Scan every `outputs/qa/*.md` for an
    "Issues to surface at next lint" section (populated by `query`
    step 3.5) and any `promote` runs since the last lint (which append
    their Q&A "Issues to surface" payloads in the same shape). Route
    each bullet:
    - If it matches a specific category — `Provenance findings →
      Quote-integrity failures`, `Provenance findings → Citation depth
      violations`, `Provenance findings → last_validated stale`, etc.
      — file it under that section.
    - Otherwise file it under `## Human-review queue` (the catch-all
      section in the report skeleton below). This is the section
      `promote` step 5 appends to and the one the human should scan
      first when triaging a fresh lint.
    After ingestion, clear that section of the Q&A file (leave the
    heading; empty body) so the next `query` can populate it again
    without duplicating. This is a non-bypassable lint substep because
    it is `query`'s only legitimate channel for flagging lint backlog
    items (AGENTS007 forbids `query` writing to `outputs/lint/`
    directly).
6.6. **Promotion candidates surfacer**. Scan `outputs/qa/*.md` and
    score each by lightweight heuristics: (a) Q&A referenced by other
    Q&A files ≥ 3 times, (b) `sources:`/inline citations cover ≥ 3
    distinct raw files, (c) `created` is > 30 days ago and the file
    hasn't been modified since. Files meeting ≥ 2 criteria get listed
    under a new report section `## Promotion candidates`, each with a
    suggested target `type` and `slug`. The human decides whether to
    invoke `promote`; lint NEVER promotes autonomously.
7. **Compose the report** at `outputs/lint/<YYYY-MM-DD>.md`. Use
   frontmatter:

   ```yaml
   ---
   type: report
   domain: <scoped-domain-or-vault>
   created: <YYYY-MM-DD>
   updated: <YYYY-MM-DD>
   sources: []
   tags: [lint]
   status: active
   ---
   ```

   `outputs/lint/` is in git but excluded from the wikilink graph
   (AGENTS006 does not require its own wikilinks to resolve into the
   wiki, and wiki pages MUST NOT cite this file).

   Sections:
   ```
   ## Delta vs outputs/lint/<prev-date>.md   ← only when a prior report exists
   ### Resolved since last lint
   ### Still open from last lint
   ### New since last lint

   ## Mechanical findings
   ### Orphans
   ### Stubs
   ### Broken wikilinks
   ### Frontmatter compliance
   ### Index drift
   ### Duplicate candidates
   ### Aliases coherence
   ### compiled_against lag

   ## Provenance findings
   ### Citation depth violations
   ### Quote-integrity failures
   ### last_validated stale
   ### MANUAL/AGENTS drift

   ## Graph hygiene
   ### In/out-degree summary
   ### Hubs
   ### Rings
   ### Orphan clusters

   ## Narrative findings
   ### Contradictions
   ### Stale claims
   ### Missing pages
   ### Missing cross-references

   ## Promotion candidates
   <!-- One row per outputs/qa/<file> meeting the heuristics in step
   6.6: filename, suggested type, suggested slug, brief reason.
   The human runs `promote` (§2.5) — lint never executes it. -->

   ## Human-review queue
   <!-- Catch-all for items routed here from step 6.5 (Q&A "Issues to
   surface" bullets that don't fit a specific Provenance / Narrative
   sub-section) and from `promote` step 5 (which appends the
   promoted Q&A's residual "Issues to surface" payload here). Each
   row: source file, one-line issue, suggested next action. Empty
   when there's nothing pending. -->

   ## Domain-specific findings
   ### …
   ```

   The **Delta** section is mandatory whenever a prior lint exists; its
   purpose is to make subsequent runs cheap to read (the "boring lint"
   ideal in §Quality bar). For each backlog item carried over, cite the
   prior report with a wikilink so the human can trace history. New
   items that did not appear last time go under "New since last lint".

   For every finding: cite the involved pages with wikilinks, propose a
   concrete fix, and tag the action as `auto-applied` or `human-review`.
8. **Auto-apply** only additive, low-risk fixes:
   - Add an obvious cross-reference (page A literally names entity B in
     prose).
   - Add a missing index entry.
   - Add missing required frontmatter fields with empty values.
   - Add the `cross-domain` tag to a page whose evidence (sources +
     in-body wikilinks) crosses ≥2 domains.
   - **Refresh the Dataview snapshot**: lint runs MUST regenerate
     [`outputs/snapshots/index-snapshot.md`](../../outputs/snapshots/index-snapshot.md)
     in full on every run (overwrite, not append). The file is the
     machine-readable mirror referenced by `/AGENTS.md` §1.1 step 4;
     fresh LLM sessions read it instead of executing Dataview.

     **The file's shape is pinned**, not reverse-engineered. The
     template ships at the path above with three fixed table sections
     and the universal `type: report` frontmatter. Your job is to
     **fill the tables**, not redesign the layout:

     | Section | Columns | Source |
     | --- | --- | --- |
     | `## Per-domain page index` | Domain, Type, Page, Updated, Status | One row per wiki page; group by domain then type; populate from each `domains/<X>/index.md` Dataview block (or, when missing, by walking `domains/<X>/wiki/*/*.md` frontmatter). |
     | `## Recent global activity` | Date, Operation, Scope, Summary | Top 20 entries of `log.md`, newest first. |
     | `## Cross-domain syntheses` | Domain, Page, Crosses into, Tags | Every wiki page whose frontmatter `tags` contains `cross-domain`. |

     Implementation (the LLM executes this itself):

     1. Read [`outputs/snapshots/index-snapshot.md`](../../outputs/snapshots/index-snapshot.md)
        as the *layout template* — preserve frontmatter and section
        headings exactly; replace only the table bodies between
        ``| ------ | …`` and the next `##` heading.
     2. For each section, run an equivalent query over the repo:
        - `Per-domain page index` ≡ walk `domains/<X>/wiki/<bucket>/*.md`,
          read frontmatter (`type`, `updated`, `status`), produce one
          row per page sorted by domain → type → slug.
        - `Recent global activity` ≡ parse `log.md` top-to-bottom,
          take the first 20 `## [YYYY-MM-DD] <op> | <summary>` blocks.
        - `Cross-domain syntheses` ≡ filter the per-domain index by
          `tags` containing `cross-domain`.
     3. Bump the snapshot's `updated:` field to today.
     4. Strip the "_Awaiting first `lint` run._" placeholder rows; if
        a section has no real rows, leave a single placeholder row
        reading `_(none yet)_` so the table still renders.

     This step is `auto-applied` (no human review needed); regenerate
     on every lint run. Do NOT introduce new sections, reorder
     existing ones, or change column headers — fresh LLM sessions
     index against the pinned shape.
   - **Graph hygiene metrics**: as part of the report, include a small
     table of (in-degree, out-degree) summary stats and call out:
     - **Hubs**: pages with ≥10 inbound wikilinks (worth scrutinising for
       over-load — the page may be doing too much).
     - **Rings**: strongly-connected components of size ≥3 (worth
       surfacing — they hint at concept circularity).
     - **Orphan clusters**: connected components of size ≥2 that have
       no edges to the main graph (worth promoting to the index or
       deprecating).

   Everything else (deletes, renames, status flips, large rewrites)
   stays as `human-review`.
9. **Prepend to log.md** (top-of-file under frontmatter, per L1 §6).
   Use plain paths (not wikilinks) for `outputs/` artifacts because
   `outputs/` is deliberately outside the wikilink graph:
   ```
   ## [YYYY-MM-DD] lint | <scope>
   - Report: outputs/lint/<YYYY-MM-DD>.md
   - Previous: outputs/lint/<prev-date>.md   (if any)
   - Auto-applied: <count>
   - Awaiting review: <count>
   - Delta: -<resolved> +<new> =<unchanged>
   ```
10. **Hard rules**:
    - Never delete pages during lint, even if orphaned or stub. Mark for
      deprecation, leave the call to the human.
    - Never rename pages during lint. Renames cascade through wikilinks
      and must be a deliberate human action.
    - Lint reports are `type: report` artifacts under `outputs/lint/`,
      not wiki pages. They still carry the universal frontmatter (type
      / domain / created / updated / status), but `sources` may be
      empty and the file is excluded from the wikilink graph.

## Quality bar

A good lint report is **boring to read** — it surfaces what changed since
the last lint, not the entire state of the wiki. Each subsequent lint
should reference the last lint report and note which findings have been
addressed.

- **Provenance findings dominate the report.** Mechanical issues are now
  pre-commit-time errors; if any appear in lint output, that means a
  hook bypass happened and should be investigated separately.
