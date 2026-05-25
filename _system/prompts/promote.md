# Prompt: promote

Use this prompt body when the human says `promote <qa-path>` (with an
optional `--as <type>`). Canonical procedure for `/AGENTS.md` §2.5.
The operation upgrades a `query`-produced Q&A artifact under
`outputs/qa/` into a first-class wiki page, performing a controlled
information-shape transform rather than a bare `git mv`.

## What this command will write (schema contract)

| Path                                              | When                                                      | Why                                                  |
|---------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| `domains/<X>/wiki/<folder>/<slug>.md`             | always (created via git mv from outputs/qa/)              | the promoted Q&A becomes a first-class wiki page     |
| `outputs/qa/<source>.md`                          | always (the source Q&A is moved away)                     | git mv preserves history; `git log --follow` traces back |
| `outputs/lint/<latest>.md`                        | when the latest lint report has a Human-review queue      | append residual issues from the promoted Q&A         |
| `domains/<X>/log.md`                              | always                                                    | audit trail                                          |
| `log.md`                                          | only when cross-domain                                    | global timeline                                      |

> This table mirrors `densa.schema.OPERATIONS['promote'].writes`.
> AGENTS011 warns on drift. Promote is **1:1**: one Q&A becomes one
> wiki page; never batch multiple Q&As in a single promote commit.


## Input

- **`<qa-path>`**: path to the Q&A file (`outputs/qa/<YYYY-MM-DD>-<slug>.md`).
- **`--as <type>`** *(optional)*: target wiki type
  (`synthesis | concept | framework | question | …`). When omitted,
  propose one based on the Q&A body and let the human confirm.
- **`--slug <new-slug>`** *(optional)*: override the target wiki slug.
  When omitted, derive from the source filename and offer it for
  confirmation.

## Procedure

### 1. Pre-flight checks (reject early, do not partially apply)

Run *all* checks first. If any fails, surface the specific blocker and
suggest a remediation; do not modify any file.

| Check                                    | Reject when                                                | Suggested fix                                                                |
| ---------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Source exists & lives in `outputs/qa/`   | Path missing or outside `outputs/qa/`                      | List the current `outputs/qa/` directory; ask user to repick.                |
| Source has `type: report`                | Frontmatter `type` is anything else                        | The file isn't a Q&A artifact — abort.                                       |
| Target type is in the L2's allowed set   | L2 `AGENTS.md` doesn't allow that page type                | Show the L2's allowed types; ask user to rechoose.                           |
| Slug + aliases dedup                     | Same slug exists, or any wiki page declares the slug as an alias | Suggest merging into the existing page, or pick a fresh slug.                |
| `sources:` cardinality per §3.1          | < 2 distinct `[[wikilinks]]` in body for `synthesis`; etc. | Ask user to enrich the Q&A with more inline citations before re-running.    |
| Required L2-specific fields are derivable | E.g. `concept` needs `first_appeared`, can't infer         | List missing fields; ask user to supply or to switch target type.            |

### 2. Information-shape transform (4 stages, applied to the moved file)

After pre-flight passes, perform the move and rewrite in a single
commit.

**Stage 1 — Voice transform.** Convert the Q&A scaffold into wiki
prose:

- "Question" heading → drop it; open the body with a declarative
  one-paragraph statement of what is true (the answer's thesis).
- "Sub-claims" numbered list → either inline them into the prose
  as topic sentences for the relevant sections, or keep as
  `## Components` / `## Mechanisms` per the target type's template.
- Inline citations (`[[wiki-page]]`, `[[raw-source]]`) stay; they
  already point at real wiki/raw files.
- Strip epistemic hedging ("I think", "似乎", "也许") **unless** the
  uncertainty itself is the knowledge being captured — in which
  case promote to `type: open-question` with `arc_status: open`.

**Stage 2 — Citation hoist.** Scan the body for every distinct
`[[wikilink]]` and `[[raw-source]]`; deduplicate; write the list
into frontmatter `sources:` per §3.1's cardinality table for the
target type. Keep the inline citations intact (double-link by
design).

**Stage 3 — L2 fill-in.** Apply target-type-specific frontmatter:

| Target type      | Required L2 fields                                                              |
| ---------------- | ------------------------------------------------------------------------------- |
| `concept`        | `first_appeared` (ask user), `last_validated: <today>`, `also_known_as: []`     |
| `overview`       | `programme_start`, `programme_status: active \| dormant \| superseded`           |
| `open-question`  | `arc_status: open \| partial \| answered`, `first_asked`                         |
| `synthesis`      | (none beyond the L1 cardinality `sources: ≥ 2`)                                  |
| `comparison`     | (none beyond `sources: ≥ 2`)                                                     |
| `entity`         | `last_validated: <today>`, `aliases: [...]` (and L2-specific lifecycle fields)   |
| (universal)      | `compiled_against: 2`, `status: active`, `created: <today>`, `updated: <today>`, `domain: <inferred>`, `tags: […]` |

**Stage 4 — Section restructure.** Load `_system/templates/<target-type>.md`
and reorder the body to match the template's section outline. The
Q&A's "Issues to surface at next lint" section is **not** copied into
the new wiki page — instead, append it to today's
`outputs/lint/<YYYY-MM-DD>.md` under the `## Human-review queue`
section declared in [`_system/prompts/lint.md`](lint.md) step 7
(create the file with `tags: [lint]` if it does not yet exist, using
the report skeleton). The next `lint` run reconciles the queue.

### 3. Git operations (single commit; prefix `promote:`)

```bash
git mv outputs/qa/<YYYY-MM-DD>-<orig-slug>.md \
       domains/<X>/wiki/<folder>/<new-slug>.md
# rewrite frontmatter + body per Stage 1–4
# append "Issues to surface" content to outputs/lint/<YYYY-MM-DD>.md
# prepend log entries (see step 4)
git commit -m "promote: <new-slug> ← <YYYY-MM-DD>-<orig-slug>"
```

The `git mv` is load-bearing: `git log --follow
domains/<X>/wiki/<folder>/<new-slug>.md` then traces the full Q&A
history. Replacing the move with a new write + delete loses history.

### 4. Prepend to logs (per L1 §6 — newest first)

Both `domains/<X>/log.md` and the global `log.md` get an entry:

```
## [YYYY-MM-DD] promote | <one-line Q&A core question>
- From: outputs/qa/<YYYY-MM-DD>-<orig-slug>.md
- To: [[<new-slug>]]
- Type: <target-type>
- Sources: <N> wiki + <M> raw (per frontmatter)
- Reason: <one-line: why this Q&A warrants wiki-grade status>
```

`outputs/` paths stay as plain text (no wikilinks) because the
resolver excludes that directory by design.

## Hard rules

- **Pre-flight is non-skippable.** If any check fails, abort with a
  specific message — no partial promotion, no silent edits.
- **1:1 granularity only.** A single Q&A becomes one wiki page. For
  1:N splits, invoke `promote` multiple times with distinct
  `--slug`; for N:1 merges, promote one Q&A and treat subsequent
  ones as `ingest`s that touch the new page.
- **No `--in-place` mode.** The move is always `outputs/qa/` →
  `domains/<X>/wiki/<folder>/`; otherwise the AGENTS007 write-scope
  contract for `query` and `promote` would overlap.
- **No autonomous promotion from `lint`.** `lint` may flag candidates
  in a "Promotion candidates" section, but only the human decides to
  invoke `promote`.
- **Failure rolls back cleanly.** On any error, `git restore --staged
  --worktree .` returns the worktree to pre-promote state. After a
  successful but later-regretted promote, `git revert <commit>`
  restores the Q&A and removes the new wiki page in one shot.

## Quality bar

A good promote produces a wiki page that:

- Reads as declarative knowledge, not as a logged conversation.
- Carries `sources:` frontmatter populated from real wiki/raw links.
- Honours the target type's `sources` cardinality (§3.1).
- Has its `Issues to surface` content already queued in the day's
  lint report, so the next `lint` finds and acts on it.
- Shows the source Q&A via `git log --follow`, giving the audit
  trail back to the original question and answer.
