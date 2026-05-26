# attic/

Quarantine for non-wiki artifacts that aren't safe to delete yet
(superseded scripts, retired templates, legacy migration drafts). The
validator ignores this directory entirely. Wiki pages use the
deprecation pattern (`status: deprecated` + `> Superseded by [[…]]`),
not attic.

Currently here: `templates-v1/` — the 15 v1-schema templates kept for
re-ingest of `wiki/.legacy/` snapshots. See
[`../docs/reference/karpathy-mapping.md`](../docs/reference/karpathy-mapping.md)
for the v1↔v2 type-rename table, and
[`../docs/reference/repository-layout.md`](../docs/reference/repository-layout.md)
for the full role.
