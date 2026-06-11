# Canned chart blocks

Copy-paste library for the `visualize` operation
([`_system/prompts/visualize.md`](../../prompts/visualize.md)).
Install = copy the block into the host page, adjust only the lines
marked `// PARAM`. Never fork the style helper — visual consistency
across the vault depends on every block sharing it.

| Block | Renders | Host pages |
|---|---|---|
| `live-monthly-ingest.md` | bar: summaries per month | domain `overview.md` |
| `live-lens-frequency.md` | bar: analysis_lens usage | psychology `overview.md` |
| `live-skill-proof.md` | horizontal bar: skills by proof_level | career `profile.md` |
| `live-pipeline-freshness.md` | bar: company last_signal age | career `overview.md` |
| `live-vault-rhythm.md` | stacked bar: ingests per domain per month | global `index.md` |
| `mermaid-blocks.md` | handDrawn header + causal DAG / timeline / quadrant skeletons | any page passing a trigger |
| `chronos-blocks.md` | Chronos DSL skeletons | arc/timeline triggers |

All `live-*` blocks require the **Charts** plugin (`window.renderChart`)
and **Dataview** (dataviewjs). They are whitelisted for hub pages only
(see visualize.md Non-negotiables).
