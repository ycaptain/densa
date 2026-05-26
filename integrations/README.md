# integrations/

Opt-in agent-specific UX add-ons (slash commands, skill packs, plugin
manifests). Fresh vaults can ignore this directory entirely — every
supported agent (Cursor / Claude Code / Codex / Cline) reads the
canonical contract from [`../AGENTS.md`](../AGENTS.md) natively.
Nothing here changes the schema, the operations, or the red lines.

Currently shipped:

- [`claude-code/`](claude-code/) — `.claude-plugin/` manifest +
  slash-command shims wrapping the five operations.
- [`cursor/densa-plugin/`](cursor/densa-plugin/) — `.cursor-plugin/`
  manifest + Cursor slash-command shims + IDE-agnostic `skills/`
  directory with `SKILL.md` files installable into
  `~/.cursor/skills/` or `~/.claude/skills/` standalone.

The two integration packages mirror each other — same operations,
different host formats. The `SKILL.md` files under
[`cursor/densa-plugin/skills/`](cursor/densa-plugin/skills/) are
deliberately IDE-agnostic and work in any AGENTS.md-aware host that
adopts the SKILL.md trigger discipline.
