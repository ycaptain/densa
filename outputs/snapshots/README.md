---
type: report
domain: vault
created: 2026-05-21
updated: 2026-05-21
sources: []
aliases: []
tags: [snapshot, readme]
status: active
compiled_against: 1
---

# `outputs/snapshots/`

Lint generates `index-snapshot.md` here on every run — a static
mirror of every Dataview / dataviewjs block in `index.md` and
`domains/<X>/index.md`, since LLM sessions can't execute Dataview.

> [!warning] Empty on a fresh clone
> If `index-snapshot.md` is absent (you just cloned the template, or
> nobody has run `lint` yet) the L1 §1.1 step-4 onboarding pointer
> resolves to nothing. **Run `lint` once** — the snapshot becomes
> part of its auto-applied output (see
> [`_system/prompts/lint.md`](../../_system/prompts/lint.md) step 8).

This directory is in git so the snapshot travels across machines,
but the wikilink resolver ignores everything under `outputs/`; wiki
pages MUST NOT cite this file.
