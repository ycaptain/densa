# Claude Code integration (experimental)

Optional Claude Code plugin that exposes the five canonical operations
as slash commands:

- `/ingest <path>` → runs the procedure in [`../../_system/prompts/ingest.md`](../../_system/prompts/ingest.md)
- `/query <question>` → runs [`../../_system/prompts/query.md`](../../_system/prompts/query.md)
- `/lint [--domain <X>]` → runs [`../../_system/prompts/lint.md`](../../_system/prompts/lint.md)
- `/process-inbox` → runs [`../../_system/prompts/process-inbox.md`](../../_system/prompts/process-inbox.md)
- `/promote <qa-path>` → runs [`../../_system/prompts/promote.md`](../../_system/prompts/promote.md)

The plugin is a thin shim — every command body just delegates to the
matching prompt file in `_system/prompts/`. Schema, red lines, and
behaviour come from [`AGENTS.md`](../../AGENTS.md), exactly as for any
other agent.

## Install

```text
/plugin marketplace add ycaptain/llm-wiki-starter
/plugin install llm-wiki-starter
```

Once installed, type `/ingest`, `/query`, `/lint`, `/process-inbox`,
or `/promote` in a fresh Claude Code chat opened against this vault.

> [!warning] Experimental
> The Claude Code plugin marketplace is still evolving (2026-05).
> Manifest formats and the install command may shift. If the plugin
> fails to load, fall back to invoking the prompts directly:
> `read _system/prompts/ingest.md and apply it to <path>`. The vault
> works identically without this directory.

## What's in here

```text
claude-code/
├── README.md                       (this file)
├── .claude/commands/{ingest,query,lint,process-inbox,promote}.md
└── .claude-plugin/{plugin,marketplace}.json
```

`.claude/commands/` and `.claude-plugin/` are the directory shapes
Claude Code expects. Other agents (Cursor, Codex, Cline) ignore them
entirely.
