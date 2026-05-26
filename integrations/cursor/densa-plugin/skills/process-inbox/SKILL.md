---
name: densa-process-inbox
description: This skill should be used when the user invokes "process-inbox", "triage the inbox", or has dropped un-routed files into `/inbox/` that need classifying. The skill classifies each inbox file by domain + bucket, proposes a canonical slug, and uses `git mv` to move it into `domains/<X>/raw/<bucket>/`. It does NOT ingest — that is a deliberate separate step (use `densa-ingest` after).
license: MIT
---

# Densa · process-inbox

> Activates Densa's `process-inbox` operation. Use only when the
> `/inbox/` directory contains un-routed material.

## When to use this skill

Trigger phrases:

- "process-inbox"
- "triage the inbox"
- "what's in `inbox/`?" + intent to classify
- "I dropped some files in `inbox/`, please route them"

Anti-triggers:

- "ingest `<path>`" with a path under `raw/` → use `densa-ingest` directly
- A specific file the user already knows the domain for → ask
  whether they want `process-inbox` (full triage) or to skip inbox
  and `git mv` directly

## Procedure

Canonical procedure:

- [`_system/prompts/process-inbox.md`](../../../../../_system/prompts/process-inbox.md)
- [`AGENTS.md` §2.4](../../../../../AGENTS.md#24-process-inbox-optional-opt-in)
- Routing rules: [`AGENTS.md` §5](../../../../../AGENTS.md#5-routing-rules-where-does-a-new-source-go)

Contract:

1. List every file under `inbox/` (recurse).
2. For each, propose `<domain> / <bucket> / <slug>`. Use the routing
   rules from [`AGENTS.md` §5](../../../../../AGENTS.md#5-routing-rules-where-does-a-new-source-go);
   if any file is genuinely ambiguous, ask one short question rather
   than guess silently.
3. Show the full move plan to the human as a unified diff (a list of
   `git mv` operations).
4. **Wait for approval** before running `git mv`.
5. After approval, `git mv` each file. Do **not** modify file
   contents.

## Examples

```text
User: process-inbox
Agent: [lists inbox/2026-04-19-paper.md, inbox/2026-04-20-call.md]
       [proposes:
         git mv inbox/2026-04-19-paper.md domains/research-papers/raw/papers/2026-04-19-mamba2.md
         git mv inbox/2026-04-20-call.md   domains/psychology/raw/conversations/2026-04-20-yuan.md]
       [waits for OK]
       [git mv x 2]
       [appends log entry; reminds: ingest is a separate step]
```

## Write scope guard

A `process-inbox` commit may write (i.e. accept `git mv` from
inbox/ INTO these targets):

- `domains/*/raw/**`
- `domains/*/log.md`
- `log.md`

A commit prefix of `process-inbox:` is required.

## Red lines

- `process-inbox` does **not** ingest. It only routes files to their
  domain. The `ingest` operation is a deliberate next step.
- Never modify file contents during routing — just `git mv`.
- If a file is genuinely cross-domain, ask one short question;
  silent guessing is the failure mode this contract prevents.
