---
type: index
scope: global
updated: 2026-05-21
compiled_against: 1
---

# Vault Index

Global directory for the LLM-maintained wiki.

- **First time?** Read [[_system/MANUAL|the user manual]] end-to-end.
- **Choosing / removing the example domains** below before your first
  real ingest: [[docs/EXAMPLE-DOMAINS]].
- **Day-to-day reference** for concepts, scenarios, FAQ:
  [[_system/MANUAL]].
- **Schema source of truth**: [[AGENTS]] (L1) and `domains/<X>/AGENTS.md` (L2).
- **Install / plugin setup**: [[_system/SETUP]].

## Domains (example L2s — keep, adapt, or remove per [[docs/EXAMPLE-DOMAINS]])

- [[domains/research-papers/index|Research papers]] — light L2 (6 page
  types). Reading academic papers / technical articles. Ships with a
  **4-paper LLM-tutoring causal-evidence arc (2024-2025)**: three real
  RCTs (Vanzo / Bastani / Kestin) plus one synthesised stand-in
  (Anthropic SAE), cross-paper synthesis, researcher guide, and
  three-audience navigator.
- [[domains/workspace/index|Workspace]] — medium L2 covering meetings,
  decisions, projects, and stakeholder dynamics. Ships with a 3-raw
  worked example (Q2 platform-migration arc).
- [[domains/psychology/index|Psychology]] — heavy L2 for therapy /
  inner work. Ships with a **6-week father-grief arc worked example
  (4 synthesised raws → ~25 wiki pages)** demonstrating IFS / EFT /
  attachment / biopsychosocial 4P / cross-clinical coordination /
  diagnostic conservatism / meaning-reconstruction. See
  [[domains/psychology/wiki/syntheses/what-this-domain-demonstrates|the capability list]]
  for the evaluator entry point; clinical adopters must re-read the
  L2 AGENTS.md §"Privacy posture" before ingesting real sessions.

> Most users will keep at most one of the above and delete the rest
> before their first real ingest. See [[docs/EXAMPLE-DOMAINS]] §3 for
> the mechanics (single bypass commit per removal).

<!-- Add one bullet per new L2 as you stand them up. -->
<!-- Remove the bullets above as you delete the example domains. -->


## What's actively in motion (curated)

> Hand-curated; the human updates this section roughly weekly. The
> Dataview blocks below are the machine view; this section is the
> editor's note.

- (empty — populate once you've ingested a few sources)

## Recent global activity

```dataviewjs
const log = await dv.io.load("log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(-15).reverse());
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

## Operations cheat sheet

- `ingest <path>` — file a new source into the wiki. See `_system/prompts/ingest.md`.
- `query <question>` — answer from the wiki, optionally file the answer back.
- `lint [--domain <X>]` — health-check pages, surface gaps and contradictions.
- `process-inbox` — triage un-routed material in `/inbox/`.
- `promote <outputs/qa/...>` — lift a Q&A artifact into a first-class wiki page. See `_system/prompts/promote.md`.
