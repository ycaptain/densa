---
name: densa-query
description: Answer a question against a Densa vault — read the global and per-domain `index.md`, follow wikilinks, compose an inline-cited answer, and file substantive Q&As to `outputs/qa/<date>-<slug>.md`. Use when the user asks "what does the wiki say about X", "summarise across pages in my wiki on Y", "compare A vs B in my notes", or explicitly names Densa / the vault. Do NOT fire on "search the codebase" (use grep), "what's in this file" (read), "explain this code" (code Q&A), or any question that does not target a Densa-authored wiki; require both `AGENTS.md` at root and `_system/densa/` present before firing. Operates in any AGENTS.md-aware IDE.
---

# Densa · query

> Activates Densa's `query` operation. Use when the human wants the
> wiki to answer a question, not to ingest a new source.

## When to use this skill

Trigger phrases:

- "what does the wiki say about `<topic>`"
- "summarise across `<pages or domain>`"
- "give me a thesis on `<X>` from existing material"
- "what does `[[entity]]` actually do?"
- "compare `[[A]]` vs `[[B]]`"

Anti-triggers:

- "ingest this file" → use `densa-ingest`
- "find contradictions" → use `densa-lint`
- "lift this Q&A into the wiki" → use `densa-promote`

## Procedure

Canonical procedure (paths relative to the Densa vault root — the
workspace must be a Densa vault clone):

- `_system/prompts/query.md`
- `AGENTS.md` §2.2

If the workspace is not a Densa vault, stop and ask the user to
open one.

Contract: **read `index.md` → drill into relevant domain index →
follow wikilinks → synthesise an answer with inline citations to
the wiki pages used**.

For substantive answers, file a Q&A artifact at
`outputs/qa/<YYYY-MM-DD>-<slug>.md` (`type: report`). Never edit
`wiki/syntheses/` from inside a `query` — if the Q&A later earns
wiki-grade status, the human runs `densa-promote`.

## Examples

```text
User: what does the wiki say about ICL vs fine-tuning trade-offs?
Agent: [reads index.md] [follows [[in-context-learning]], [[fine-tuning]],
        [[continual-learning]]] [composes answer with inline citations]
        [files outputs/qa/2026-05-25-icl-vs-finetuning.md]
        [appends log entry]
```

```text
User: summarise across my psychology sessions about decision anxiety
Agent: [reads psychology index.md] [follows [[decision-anxiety]] +
        relevant analyses] [synthesises] [files Q&A]
```

## Write scope guard

A `query` commit may write:

- `outputs/qa/**`
- `domains/*/log.md`
- `log.md`

A commit prefix of `query:` is required.

## Red lines

- Inline citations are **required** for any non-trivial claim.
- Do not edit `wiki/**` from inside a `query`; defer to `promote`.
- Do not skip the Q&A filing step for substantive answers — it's the
  audit trail that makes the next query cheaper.
