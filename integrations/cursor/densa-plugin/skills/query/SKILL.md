---
name: densa-query
description: This skill should be used when the user asks a question of the wiki — phrasings like "what does the wiki say about X", "summarise across pages on Y", "compare A vs B as I've written them up", "I need a thesis on Z from existing material". The skill reads the global and per-domain `index.md`, follows wikilinks, synthesises an inline-cited answer, and files substantive Q&As back to `outputs/qa/`. Operates inside any AGENTS.md-aware IDE (Cursor / Claude Code / Codex / Cline).
license: MIT
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

Canonical procedure:

- [`_system/prompts/query.md`](../../../../../_system/prompts/query.md)
- [`AGENTS.md` §2.2](../../../../../AGENTS.md#22-query-question)

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
