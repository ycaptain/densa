---
name: densa-ingest
description: This skill should be used when the user says "ingest <path>", "process this source", drops a new file into a Densa vault under `raw/`, or asks the agent to add a raw source to the wiki. The skill plans which `wiki/` pages to create or update, waits for human approval, applies the planned edits, then appends a per-domain and global log entry. Operates inside any AGENTS.md-aware coding-agent IDE (Cursor / Claude Code / Codex / Cline).
license: MIT
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
vault at:

- [`_system/prompts/ingest.md`](../../../../../_system/prompts/ingest.md) — operation contract
- [`AGENTS.md`](../../../../../AGENTS.md) §2.1 — schema-level overview
- Any matching `_system/prompts/domains/<domain>-*-analysis.md` —
  domain-specific sub-prompt (load if present)

Load these before doing anything. The contract is **read the source
in full → plan the wiki edits → wait for OK → apply edits → log**.

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

Per [`AGENTS.md` §2.0](../../../../../AGENTS.md#20-operation-writes-machine-enforced-via-agents007)
and the validator's `AGENTS007` rule, an `ingest` commit may write:

- `domains/*/wiki/**`
- `domains/*/log.md`
- `log.md`

A commit prefix of `ingest(<domain>):` is required. The pre-commit
hook rejects out-of-scope writes; if rejected, the
[`CONTRIBUTING.md` §"If the pre-commit hook rejects your first commit"](../../../../../CONTRIBUTING.md)
section explains recovery.

## Red lines (the validator enforces; the skill must also respect)

- Never modify any file under `*/raw/` ([AGENTS.md §6](../../../../../AGENTS.md#6-red-lines-non-negotiable)).
- Append log entries in reverse chronological order at the entry
  insertion point.
- If re-ingesting a previously-authored wiki page, `git mv` it to
  `domains/<X>/wiki/.legacy/<same-name>.md` before writing the new
  version.
