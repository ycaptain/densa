---
name: densa-ingest
description: Ingest a raw source into a Densa vault — distill it into one summary plus updates to entities/concepts/open-questions, then prepend a log entry. Use when the user says "ingest <path>" (in a Densa vault), "compile this raw into my wiki", drops a new file under `raw/`, or explicitly names Densa / the wiki. Do NOT fire on generic "summarise this", "tldr this file", "ingest data from API/logs", or any request where the workspace lacks both `AGENTS.md` at root and `_system/densa/` — those are not Densa ingests. Operates in any AGENTS.md-aware IDE.
---

# Densa · ingest

> Activates Densa's `ingest` operation. Use when a new raw source
> needs to be compiled into the wiki.

## When to use this skill

Trigger phrases (the user says any of these):

- "ingest `<path>`"
- "process this source"
- "compile this into the wiki"
- "add this article to the wiki"
- "I just dropped a new file in `raw/<bucket>/`"

Anti-triggers (do **not** use this skill):

- "what does the wiki say about X" → use `densa-query`
- "find contradictions" / "health check" → use `densa-lint`
- "triage the inbox" → use `densa-process-inbox`
- "promote this Q&A" → use `densa-promote`

## Procedure

This skill is a thin shim. The canonical procedure lives in the
**Densa vault** at the paths below (resolved relative to the vault
root — i.e. the workspace must be a Densa vault clone):

- `_system/prompts/ingest.md` — operation contract
- `AGENTS.md` §2.1 — schema-level overview
- Any matching `_system/prompts/domains/<domain>-*-analysis.md` —
  domain-specific sub-prompt (load if present)

If the current workspace is **not** a Densa vault (no `AGENTS.md`
+ `_system/densa/` at root), stop and ask the user to open one
before proceeding.

Load the prompts before doing anything. The contract is **read the
source in full → plan the wiki edits → wait for OK → apply edits →
log**.

Page-count tier per L2 information density (see operation prompt):
**light** (`research-papers`) 3–6 pages; **medium** 5–10; **heavy**
(e.g. `psychology` session) 8–15.

## Examples

```text
User: ingest raw/notes/2026-04-19-paper-mamba2.md
Agent: [reads source] [plans 5 wiki edits: 1 new summary, 2 updated
       concepts, 1 updated entity, 1 overview mindmap node]
       [waits for OK] [applies edits] [appends log]
```

```text
User: I dropped raw/articles/2026-05-15-karpathy-talk.md, please
      process it
Agent: [same flow]
```

## Write scope guard

Per `AGENTS.md` §2.0 (operation writes — machine-enforced via
AGENTS007), an `ingest` commit may write:

- `domains/*/wiki/**`
- `domains/*/log.md`
- `log.md`

A commit prefix of `ingest(<domain>):` is required. The pre-commit
hook rejects out-of-scope writes; if rejected, see `CONTRIBUTING.md`
§"If the pre-commit hook rejects your first commit" for recovery.

## Red lines (the validator enforces; the skill must also respect)

- Never modify any file under `*/raw/` (`AGENTS.md` §6).
- Append log entries in reverse chronological order at the entry
  insertion point.
- If re-ingesting a previously-authored wiki page, `git mv` it to
  `domains/<X>/wiki/.legacy/<same-name>.md` before writing the new
  version.
