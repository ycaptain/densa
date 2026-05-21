<!--
Template for a per-vault README. Copy this file to the vault root and
replace `_my-vault_` with your vault name:

    cp _system/README-template.md README.md
    # then edit README.md and replace `_my-vault_` with the real name

The bootstrap prompt walks you through this in Step 7. Once copied to
the root, the relative links below (`AGENTS.md`, `_system/MANUAL.md`,
`_system/SETUP.md`) resolve correctly.
-->

# _my-vault_

An Obsidian-based personal LLM wiki, built on Andrej Karpathy's
[llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

> The vault is the codebase, Obsidian is the IDE, the LLM is the
> programmer. You curate sources, ask questions, and review — the LLM
> does all the bookkeeping.

## Start here

1. **First-time orientation** — read
   [`_system/MANUAL.md`](_system/MANUAL.md) end-to-end (~250 lines, ~10
   minutes).
2. **Schema source of truth** — [`AGENTS.md`](AGENTS.md) (L1) and each
   `domains/<X>/AGENTS.md` (L2).
3. **Install / plugin setup** — [`_system/SETUP.md`](_system/SETUP.md).

## Daily use

The five operations the human ever runs:

- `ingest <path>` — file a new source into the wiki
- `query <question>` — ask the wiki a question (read-only by default)
- `lint [--domain <X>]` — health-check the wiki
- `process-inbox` — triage un-routed material in `/inbox/`
- `promote <outputs/qa/...>` — lift a Q&A archive into a first-class wiki page

Each one has a canonical procedure in `_system/prompts/`.

## Layout

```
<vault>/
├── AGENTS.md            ← L1 schema (the contract)
├── index.md             ← global directory of domain indexes
├── log.md               ← global timeline
├── _system/             ← prompts, templates, scripts, hooks
├── domains/
│   └── psychology/      ← example L2 (rename or remove to taste)
├── inbox/               ← un-routed material (optional)
└── attic/               ← deprecated / quarantined files
```

See [`AGENTS.md`](AGENTS.md) §1 for the full annotated tree.
