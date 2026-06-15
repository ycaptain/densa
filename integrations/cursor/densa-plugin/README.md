# Cursor integration — Densa plugin (experimental)

Optional Cursor plugin that exposes the five canonical Densa
operations as **skills** (auto-triggered) and **slash commands**
(explicit invocation).

```text
integrations/cursor/densa-plugin/
├── README.md                            (this file)
├── .cursor-plugin/
│   └── plugin.json                      Cursor plugin manifest
├── skills/                              Auto-triggered SKILL.md (IDE-agnostic format)
│   ├── ingest/SKILL.md
│   ├── query/SKILL.md
│   ├── lint/SKILL.md
│   ├── process-inbox/SKILL.md
│   └── promote/SKILL.md
└── commands/                            Cursor slash-command shims
    ├── ingest.md
    ├── query.md
    ├── lint.md
    ├── process-inbox.md
    └── promote.md
```

`.cursor-plugin/` is the directory shape Cursor expects (per
[Cursor Plugins reference](https://cursor.com/docs/reference/plugins)).
`skills/` follows the SKILL.md format adopted by Claude Code, Codex,
and `skills.sh`; the same `SKILL.md` files can be installed standalone
into `~/.cursor/skills/` or `~/.claude/skills/` without the plugin
wrapper.

## What this gives you

Two activation paths into the same Densa operation prompts:

1. **Automatic** — the agent reads `SKILL.md` frontmatter
   `description:` fields and triggers the right skill when you say
   things like "ingest this file" or "what does the wiki say
   about X". No `/` prefix required.
2. **Explicit** — `/ingest`, `/query`, `/lint`, `/process-inbox`,
   `/promote` slash commands. Useful when you want to force a
   specific operation regardless of phrasing.

Both paths delegate to the canonical procedures under
[`_system/prompts/`](../../../_system/prompts/); behaviour comes
from [`AGENTS.md`](../../../AGENTS.md), exactly as for any other
agent.

> [!warning] Experimental — falls back gracefully
> The Cursor plugin marketplace + Skills format are still evolving
> (2026-05). Manifest fields and discovery paths may shift. **If the
> plugin fails to load, fall back to invoking the prompts directly**:
> `read _system/prompts/ingest.md and apply it to <path>`. The vault
> works identically without this directory; the plugin is just a UX
> shortcut.

## Install

### Option A — Plugin (when the marketplace ships)

```text
# Once the Cursor plugin marketplace supports add-by-repo:
/plugin marketplace add ycaptain/densa
/plugin install densa
```

### Option B — Local sideload (works today)

```bash
# Symlink the WHOLE plugin directory (manifest + skills + commands)
# into Cursor's user-level plugins folder. Run from the densa clone:
mkdir -p ~/.cursor/plugins
ln -sf "$(pwd)/integrations/cursor/densa-plugin" "$HOME/.cursor/plugins/densa"

# Restart Cursor. The 5 skills (`densa-ingest`, ..., `densa-promote`)
# and 5 slash commands (`/ingest`, `/query`, `/lint`,
# `/process-inbox`, `/promote`) become discoverable. Type `/help` to
# confirm the slash commands appear.
```

> [!important] Workspace must be a Densa vault clone
> The skill bodies reference paths relative to the **vault root**
> (e.g. `_system/prompts/ingest.md`). They only resolve when the
> current Cursor workspace IS a Densa vault clone. If you invoke a
> `densa-*` skill in an unrelated workspace, the agent will ask you
> to open a vault first. This is by design — the plugin is a
> trigger surface, not a self-contained operation runner; the
> canonical contract lives at `AGENTS.md` inside the vault.

### Option C — Claude Code zip upload (for the SKILL.md files only)

```bash
cd integrations/cursor/densa-plugin/skills
for op in ingest query lint process-inbox promote; do
  zip -r "densa-$op.zip" "$op"
done
# Then upload each .zip via Settings > Capabilities > Skills in Claude Code.
```

## Relationship to `integrations/claude-code/`

The two directories ship the same six operations in two different
package formats:

| | `integrations/cursor/densa-plugin/` | `integrations/claude-code/` |
| --- | --- | --- |
| Plugin manifest | `.cursor-plugin/plugin.json` | `.claude-plugin/plugin.json` + `marketplace.json` |
| Slash commands | `commands/{op}.md` | `.claude/commands/{op}.md` |
| Auto-triggered skills | `skills/{op}/SKILL.md` | (not shipped — Claude Code reads `SKILL.md` from `~/.claude/skills/` if symlinked) |

The `SKILL.md` files under `skills/` are **IDE-agnostic** by
design — same files work in any AGENTS.md-aware IDE that adopts the
SKILL.md trigger discipline. Cursor, Claude Code, and Codex all
accept them; future host environments inherit for free.

## What this is not

- Not a replacement for [`AGENTS.md`](../../../AGENTS.md). The
  contract still lives at the vault root.
- Not a replacement for the pre-commit validator
  ([`_system/densa/`](../../../_system/densa/)). Skills + commands
  don't enforce the red lines; the validator does.
- Not a replacement for `python -m densa --all`. Always wire the
  pre-commit hook per [`README.md` §"Quickstart"](../../../README.md#quickstart).
