---
name: densa-lint
description: This skill should be used when the user asks for a wiki health check — phrasings like "lint", "find contradictions", "what's stale", "orphan pages", "concepts mentioned in multiple pages but not yet authored". The skill surveys the wiki against the rule registry, produces a markdown report at `outputs/lint/<YYYY-MM-DD>.md`, and auto-applies only additive fixes (missing index entries, obvious cross-references). Destructive fixes wait for human approval. Operates inside any AGENTS.md-aware IDE.
license: MIT
---

# Densa · lint

> Activates Densa's `lint` operation. Use to surface drift and
> contradictions across the wiki without rewriting anything
> destructively.

## When to use this skill

Trigger phrases:

- "lint"
- "lint --domain `<X>`"
- "health check the wiki"
- "find contradictions"
- "what's stale?" / "what hasn't been touched in a while?"
- "any orphan pages?"

Anti-triggers:

- "ingest this file" → use `densa-ingest`
- "what does the wiki say" → use `densa-query`
- "rename this page" → bulk renames need maintainer approval, not lint

## Procedure

Canonical procedure:

- [`_system/prompts/lint.md`](../../../../../_system/prompts/lint.md)
- [`AGENTS.md` §2.3](../../../../../AGENTS.md#23-lint---domain-x)
- Rule registry:
  [`docs/reference/rules-registry.md`](../../../../../docs/reference/rules-registry.md)
  (live mirror: `python -m densa rules`)

Contract:

1. Run [`PYTHONPATH=_system python -m densa --all`](../../../../../_system/densa/cli.py)
   first; surface every reported issue.
2. Survey for soft signals the validator can't catch: stale
   claims, orphan pages, concepts mentioned in ≥2 pages but lacking
   their own page, missing cross-references, stub pages older than
   14 days, `index.md` drift.
3. Write the report to `outputs/lint/<YYYY-MM-DD>.md`
   (`type: report`).
4. Refresh `outputs/snapshots/index-snapshot.md` if the index has
   moved since its `updated:` stamp.
5. **Auto-apply only additive fixes** (missing index entries,
   obvious cross-references); destructive changes (deletions,
   renames) wait for the human.

## Examples

```text
User: lint
Agent: [densa --all -> 0 errors] [surveys 187 pages]
       [writes outputs/lint/2026-05-25.md with 4 contradictions,
        3 orphans, 2 stale-last-validated]
       [auto-applies 2 missing cross-references; lists destructive
        fixes for approval]
```

```text
User: lint --domain research-papers
Agent: [same flow, scoped to domains/research-papers/]
```

## Write scope guard

A `lint` commit may write:

- `outputs/**`
- `domains/*/wiki/**` (only for additive fixes — missing index
  entries, obvious cross-references)
- `domains/*/log.md`
- `log.md`

A commit prefix of `lint:` is required.

## Red lines

- Never delete a wiki page — use deprecation (set `status:
  deprecated`, add a `> Superseded by` redirect with the new slug).
- Never auto-apply renames, bulk slug changes, or page deletions.
- The lint report is a markdown artifact under `outputs/lint/`, not
  under `wiki/syntheses/`.
