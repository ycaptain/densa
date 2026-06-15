# integrations/

Opt-in agent-specific UX add-ons (slash commands, skill packs, plugin
manifests). Fresh vaults can ignore this directory entirely — every
supported agent (Cursor / Claude Code / Codex / Cline) reads the
canonical contract from [`../AGENTS.md`](../AGENTS.md) natively.
Nothing here changes the schema, the operations, or the red lines.

Currently shipped:

- [`claude-code/`](claude-code/) — `.claude-plugin/` manifest +
  slash-command shims wrapping the six operations.
- [`cursor/densa-plugin/`](cursor/densa-plugin/) — `.cursor-plugin/`
  manifest + Cursor slash-command shims + IDE-agnostic `skills/`
  directory with `SKILL.md` files installable into
  `~/.cursor/skills/` or `~/.claude/skills/` standalone.

The two integration packages mirror each other — same operations,
different host formats. The `SKILL.md` files under
[`cursor/densa-plugin/skills/`](cursor/densa-plugin/skills/) are
deliberately IDE-agnostic and work in any AGENTS.md-aware host that
adopts the SKILL.md trigger discipline.

---

## `@`-mention picker — MCP-native, host-agnostic

The `@`-mention picker is a UX pattern for quickly pulling a wiki page into
context by typing `@` and a prefix. Densa's MCP server (Phase E, `_system/densa/mcp/`)
is the shared backend — any MCP-speaking host gets the picker without a
host-specific implementation.

### Backend calls

| UX action           | MCP call                                          |
| ------------------- | ------------------------------------------------- |
| Browse all concepts | `list_pages(type="concept", limit=50)`            |
| Type-ahead on "cog" | `search_wiki(query="cog", prefix=true, limit=10)` |
| Insert wikilink     | Use `path` from result → format as `[[slug]]`     |

Both `list_pages` and `search_wiki` return `title + preview_line + type` per
result — enough for picker rendering without a follow-up `read_page` call.
Full schema: [`_system/densa/mcp/SPEC.md`](../_system/densa/mcp/SPEC.md).

### Claude Code slash command (example)

```bash
# ~/.claude/commands/densa-search.md
/densa-search [type] <query>
# → calls search_wiki(query=<query>, type=<type>, prefix=true, limit=10)
# → displays title + preview, user picks, command inserts [[slug]]
```

### Cursor `@`-file integration (example)

Cursor's native `@`-picker uses its own index. A Densa MCP integration
runs alongside it: configure the MCP server in `.cursor/mcp.json` and
Cursor offers Densa's `search_wiki` as an `@densa-search` action in the
composer panel.

### Hosts without MCP

For hosts that don't speak MCP yet (Codex, Cline without MCP support), the
`SKILL.md` shim in `cursor/densa-plugin/skills/densa-query/SKILL.md` provides
a text-based fallback: type `/densa query <term>` and the agent runs `query`
with the wiki's index pages in context.
