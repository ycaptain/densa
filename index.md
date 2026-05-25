---
type: index
scope: global
updated: 2026-05-25
compiled_against: 2
---

# Vault Index

Global directory for the LLM-maintained wiki.

- **First time here?** Start at [`README.md`](README.md) — its
  "Pick your path" router picks the right entry for you. This
  `index.md` is the *content map* of the vault, not the onboarding
  entry.
- **Day-to-day reference** (scenarios, mental model, FAQ pointers):
  [[GUIDE]].
- **Setup beyond Quickstart** (Obsidian plugins, encryption,
  domain decisions): [[docs/setup]].
- **Schema source of truth**: [`AGENTS.md`](AGENTS.md) (L1) and `domains/<X>/AGENTS.md` (L2).

## Domains

The template ships with one default example L2 — keep, adapt, or
remove per [[docs/setup]] §"Choosing or replacing the default domain".

- [[domains/research-papers/index|Research papers]] — light L2 (6
  page types). Reading academic papers / technical articles. Ships
  with a **5-paper LLM-tutoring evidence arc (2024-2025)**: three
  real RCTs (Vanzo / Bastani / Kestin), one real review (Kim 2025),
  and one synthesised stand-in (Anthropic SAE) — plus a cross-paper
  synthesis, researcher guide, and three-audience navigator.

Heavier worked examples (`workspace`, `psychology`) live under
`examples/showcases/` as opt-in references. Copy one into `domains/`
if you want to start from its schema; see
[[docs/setup]] §"Adopting a showcase" for the mechanics.

<!-- Add one bullet per new L2 as you stand them up. -->
<!-- Remove the bullet above if you delete research-papers. -->

## Recent global activity

```dataviewjs
const log = await dv.io.load("log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(0, 15));
}
```

## Cross-domain syntheses

```dataview
TABLE WITHOUT ID
    file.link AS "Page",
    domain AS "Domain",
    updated AS "Updated"
FROM "domains" AND #cross-domain
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```
