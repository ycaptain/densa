# Legacy v1 templates

These templates correspond to **`schema_version: 1`** (the pre-Karpathy-
vocabulary type set: `analysis`, `pattern`, `theme`, `framework`,
`protocol`, `experiment`, `decision`, `stakeholder`, `project`,
`fleeting`, `correction`, `question`, `session`, plus the two
psychology-specific analysis variants).

They are kept here for reference — bulk re-ingest of legacy wiki
content under `.legacy/` snapshots may still consult them, and the
v1 → v2 migration script (`_system/scripts/migrate_02_karpathy_vocab.py`)
documents the type renames it applies. New wiki pages MUST use the v2
templates under `_system/templates/` instead.

See [`docs/reference/karpathy-mapping.md`](../../docs/reference/karpathy-mapping.md)
for the type-rename table.
