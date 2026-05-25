# attic/

Deprecated or quarantined files that aren't safe to delete yet but
shouldn't sit in the live working tree. The validator ignores this
directory entirely.

> Per [`AGENTS.md`](../AGENTS.md) §4 the wiki uses the **deprecation
> pattern** (`status: deprecated` + `> Superseded by [[…]]` redirect)
> for wiki pages — those don't end up here. `attic/` is for
> *non-wiki* artifacts: superseded scripts, old templates, legacy
> migration drafts.

## What's here

- `templates-v1/` — the 15 v1-schema page templates (e.g.
  `analysis.md`, `pattern.md`, `framework.md`, `question.md`,
  `psychology-analysis.md`). Replaced by the nine v2 templates
  under `_system/templates/`; kept here for re-ingest of legacy
  `wiki/.legacy/` snapshots and for migration-script reference.
  See [`docs/reference/karpathy-mapping.md`](../docs/reference/karpathy-mapping.md)
  for the type-rename table.

## When to add to attic

- The file is non-wiki (no `type:` frontmatter), and
- Deleting outright would lose context useful to a future maintainer,
  and
- Leaving it in its original location would imply it's still active.

Move with `git mv path/to/<file> attic/<bucket>/<file>` so the
history follows. The `attic/` directory itself is created on first
move — there's no `.gitkeep`.
