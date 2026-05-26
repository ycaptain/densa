---
name: densa-promote
description: This skill should be used when the user invokes "promote `<qa-path>`" or asks to lift an evergreen Q&A from `outputs/qa/` into a first-class wiki page. The skill is NOT a bare `git mv` — it performs a controlled information-shape transform (voice transform, citation hoist, L2 fill-in, section restructure), wrapped in a `git mv` so `git log --follow` traces the new wiki page back to the source Q&A. One Q&A becomes one wiki page (1:1 only).
license: MIT
---

# Densa · promote

> Activates Densa's `promote` operation. Use to lift an evergreen
> Q&A from `outputs/qa/` into the wiki.

## When to use this skill

Trigger phrases:

- "promote outputs/qa/2026-05-25-foo.md"
- "promote `<path>` --as concept"
- "promote `<path>` --slug `<new-slug>`"
- "this Q&A is evergreen, lift it into the wiki"
- "wikify outputs/qa/`<path>`"

Anti-triggers:

- "answer this question" → use `densa-query`
- "create a new wiki page from scratch" → that's an `ingest` from a
  raw source, not a `promote`
- "merge two wiki pages" → not in scope; bulk slug changes need
  maintainer approval

## Procedure

Canonical procedure:

- [`_system/prompts/promote.md`](../../../../../_system/prompts/promote.md)
- [`AGENTS.md` §2.5](../../../../../AGENTS.md#25-promote-qa-path-qa--wiki-page)

Contract:

1. **Pre-flight checks** (all must pass; abort if any fails):
   - Source Q&A exists at the given path under `outputs/qa/`.
   - Source has `type: report` frontmatter (or domain-meta).
   - Target wiki path is computable per the page type (`--as`
     argument or inferred from Q&A content).
   - Target wiki path does **not** already exist (otherwise it's an
     update, not a promote).
2. **Information-shape transform** (do all four):
   - Voice: convert Q&A "answer-to-a-question" voice to wiki
     "canonical-statement" voice.
   - Citation hoist: lift inline citations into the page's
     `sources:` frontmatter, observing the per-type cardinality
     contract ([`docs/reference/sources-cardinality.md`](../../../../../docs/reference/sources-cardinality.md)).
   - L2 fill-in: add any required L2-specific fields the target
     domain declares.
   - Section restructure: reshape the body to match the target
     type's template (see `_system/templates/<type>.md`).
3. **`git mv`** the source Q&A to its new wiki location. This is
   what lets `git log --follow` trace the wiki page back to the
   source Q&A.
4. **Wait for human approval** of the planned diff (frontmatter +
   body + log entry) before committing.

## Examples

```text
User: promote outputs/qa/2026-05-25-icl-vs-finetuning.md --as concept
Agent: [pre-flight: source exists; type report; target
        domains/research-papers/wiki/concepts/icl-vs-finetuning.md
        does not exist - proceed]
       [transforms voice; hoists 3 inline citations to sources:;
        adds L2 fields; restructures into concept template]
       [shows diff; waits for OK]
       [git mv outputs/qa/.../*.md domains/.../concepts/.../*.md]
       [appends log entry to domains/research-papers/log.md + log.md]
```

## Write scope guard

A `promote` commit may write:

- `outputs/qa/**`
- `outputs/lint/**`
- `domains/*/wiki/**`
- `domains/*/log.md`
- `log.md`

A commit prefix of `promote:` is required.

## Red lines

- One Q&A becomes **one** wiki page (1:1 granularity only).
- The transform must preserve every citation; promote is the moment
  to fail loudly on missing source links.
- `lint` may surface promotion candidates but never executes
  `promote` itself — promotion is a deliberate human-initiated step.
