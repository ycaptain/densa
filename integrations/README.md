# Agent integrations

`share/` is agent-neutral: the single canonical schema at
[`AGENTS.md`](../AGENTS.md) is read by Cursor, Claude Code, Codex,
Cline, and any other agent honouring the AGENTS.md convention.

| Agent       | Setup                                                                          |
|-------------|--------------------------------------------------------------------------------|
| Cursor      | Open the vault. `AGENTS.md` is picked up natively.                             |
| Codex CLI   | Same.                                                                          |
| Cline       | Same.                                                                          |
| Claude Code | Same, plus the optional [`claude-code/`](claude-code/) plugin for `/ingest`-style slash commands. |

This directory only holds agent-specific UX add-ons (slash commands,
plugin manifests). It is **opt-in** — fresh vaults can ignore it
entirely. Agents always read the canonical contract from `AGENTS.md`;
nothing here changes the schema, the operations, or the red lines.
