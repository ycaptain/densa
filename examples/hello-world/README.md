# Hello-world demo

A 5-minute walkthrough of what one `ingest` produces. No agent needed
to read this; just `cat` the files in order:

| Step | File | Time |
|---|---|---|
| 1. The input | [`source.md`](source.md) | 90 sec |
| 2. The plan the agent would draft | this README §"Plan" below | 30 sec |
| 3. The wiki pages produced | [`expected-wiki/`](expected-wiki/) | 2 min |
| 4. The log entry recorded | [`expected-wiki/log-entry.md`](expected-wiki/log-entry.md) | 30 sec |

That's the whole `ingest` loop. Now scale it to your own material.

## Plan

After reading `source.md` end-to-end the agent would draft (and wait
for your OK):

```
I'll touch 4 pages from this 1-page source (~60 lines diff):
- create wiki/summaries/docstring-overview-summary.md  (1:1 with source)
- create wiki/concepts/docstring.md
- create wiki/concepts/docstring-style.md
- prepend log.md  (ingest entry)

Approve, edit the list, or drop any?
```

You'd say *go*. Four edits land. The pre-commit hook runs
`densa --staged`; the commit goes through.

## Why these four pages

This source is **light** — one page of evergreen material, no
recurring entities, no domain-spanning narrative. Per
[`AGENTS.md` §"ingest"](../../AGENTS.md#21-ingest-path)'s tier guidance, a light source
yields 3–6 wiki pages. We chose:

- **One `summary`** ([`summaries/docstring-overview-summary.md`](expected-wiki/summaries/docstring-overview-summary.md))
  — the canonical 1:1 record of what this source says, in the wiki's
  voice rather than the original's.
- **Two `concept` pages**
  ([`concepts/docstring.md`](expected-wiki/concepts/docstring.md),
  [`concepts/docstring-style.md`](expected-wiki/concepts/docstring-style.md))
  — the two evergreen ideas this source introduces. Each has an
  *Appearances* table that grows when future sources cite it.
- **One log entry**
  ([`log-entry.md`](expected-wiki/log-entry.md)) — the audit trail
  the global `log.md` would receive.

No `overview` page (one ingest doesn't warrant a sub-area survey).
No `synthesis` page (a synthesis requires ≥2 raws — see
[`docs/reference/sources-cardinality.md`](../../docs/reference/sources-cardinality.md)).
No new `open-question` page (the source's "out of scope" notes are
captured in the summary's *Open questions* section, not promoted to
their own pages on first ingest).

## What this demo doesn't show

- **Inbox triage** — `process-inbox` only matters when you have a
  pile of un-routed clips. See
  [`_system/prompts/process-inbox.md`](../../_system/prompts/process-inbox.md).
- **Querying** — `query` walks the wiki to answer a question. The
  shipped showcase [`examples/showcases/psychology/`](../showcases/psychology/)
  has dozens of cross-references that demonstrate where `query`
  shines; this single-source demo doesn't.
- **Lint** — `lint` is meaningful only against a populated wiki at
  scale. Run it once you have a few real ingests.
- **Promotion** — `promote` lifts a Q&A archive into a first-class
  wiki page. Procedure:
  [`_system/prompts/promote.md`](../../_system/prompts/promote.md).

## Try this for real

The shortest path from this demo to your own first ingest:

1. Read [`README.md`](../../README.md) §"Quickstart" — fork upstream,
   wire the pre-commit hook, paste the bootstrap prompt.
2. Drop your own one-page article into
   `domains/research-papers/raw/notes/` (the default L2 shipped with
   the template). **Heads-up:** `research-papers/` is also the shipped
   showcase, so its `raw/` and `wiki/` are populated with the AI-
   education evidence arc. Either replace those contents with your own
   per
   [`docs/setup.md` §"Choosing or replacing the default domain"](../../docs/setup.md#choosing-or-replacing-the-default-domain),
   or rename the domain first — don't try to "build on" the example.
3. In your IDE's AI chat: `ingest <path>`.

The plan format above is what the agent will draft for your file.

## Cross-references

- [`AGENTS.md` §"ingest"](../../AGENTS.md#21-ingest-path) — the canonical ingest contract.
- [`_system/prompts/ingest.md`](../../_system/prompts/ingest.md) — the
  full operation prompt the agent loads on demand.
- [`docs/reference/sources-cardinality.md`](../../docs/reference/sources-cardinality.md)
  — when each page type's `sources` field needs how many entries.
