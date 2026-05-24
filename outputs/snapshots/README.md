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

Lint regenerates `index-snapshot.md` here on every run — a static
mirror of every Dataview / dataviewjs block in `index.md` and
`domains/<X>/index.md`, since LLM sessions can't execute Dataview.

The template ships a pre-populated snapshot so the L1 §1.1 step-4
onboarding pointer always resolves to something readable on a fresh
clone. Re-run `lint` whenever:

- the snapshot's `updated:` field lags the most recent `ingest` entry
  in `log.md`, **or**
- you deleted the file (`git rm outputs/snapshots/index-snapshot.md`)
  to force a clean rebuild.

In either case the new snapshot is part of `lint`'s auto-applied
output (see [`_system/prompts/lint.md`](../../_system/prompts/lint.md)
step 8).

This directory is in git so the snapshot travels across machines,
but the wikilink resolver ignores everything under `outputs/`; wiki
pages MUST NOT cite this file.
