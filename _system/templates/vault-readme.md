<!--
Template for a per-vault README. Copy this file to the vault root and
replace `_my-vault_` with your vault name:

    cp _system/templates/vault-readme.md README.md
    # then edit README.md and replace `_my-vault_` with the real name

The bootstrap prompt walks you through this in Step 7. Once copied to
the root, the relative links below (`AGENTS.md`, `GUIDE.md`) resolve
correctly.
-->

# _my-vault_

An Obsidian-based personal LLM wiki, built on Andrej Karpathy's
[llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

> The vault is the codebase. Obsidian is the IDE. The LLM is the
> programmer. You curate sources, ask questions, and review — the LLM
> does the bookkeeping.

## 🚀 Start here

1. **First-time orientation** —
   [`GUIDE.md`](GUIDE.md) (a day-in-the-life narrative + the seams
   between operations). FAQ lives at [`docs/faq.md`](docs/faq.md);
   install / Obsidian / encryption recipes at
   [`docs/setup.md`](docs/setup.md).
2. **Schema source of truth** — [`AGENTS.md`](AGENTS.md) (L1) and each
   `domains/<X>/AGENTS.md` (L2).

## 📅 Daily use

The five operations you ever run:

- 📥 `ingest <path>` — file a new source into the wiki
- 🔍 `query <question>` — ask the wiki a question (read-only by default)
- 🩺 `lint [--domain <X>]` — health-check the wiki
- 📨 `process-inbox` — triage un-routed material in `/inbox/`
- ⬆️ `promote <outputs/qa/...>` — lift a Q&A archive into a first-class wiki page

Per-op write scopes + canonical procedures live in
[`AGENTS.md` §"The five operations"](AGENTS.md#2-the-five-operations).

## 🧱 Layout

```
<vault>/
├── AGENTS.md            ← L1 schema (the contract)
├── index.md             ← global directory of domain indexes
├── log.md               ← global timeline
├── _system/             ← prompts, templates, scripts, hooks
├── domains/
│   └── <your-domain>/   ← your L2(s)
├── outputs/             ← lint reports, Q&A archives, index snapshots
├── inbox/               ← un-routed material (optional)
└── attic/               ← deprecated / quarantined files
```

See [`AGENTS.md` §"Layered architecture"](AGENTS.md#1-layered-architecture)
for the full annotated tree.

## 🔌 Cross-tool agent shims (optional)

`AGENTS.md` is the canonical contract — every major coding agent IDE
(Cursor / Claude Code / Codex / Cline) reads it natively. If you
primarily use a tool that defaults to a different filename (older
Claude Code installs, Gemini CLI, etc.), drop a one-line shim at the
vault root pointing back at `AGENTS.md`:

```bash
echo "See [AGENTS.md](AGENTS.md)." > CLAUDE.md
echo "See [AGENTS.md](AGENTS.md)." > GEMINI.md
```

These are **convenience aliases**, not duplicates. Never copy the
contract into the shim file — that creates a drift point. The pattern
is borrowed from [Tolaria](https://github.com/refactoringhq/tolaria),
which ships the same triple in every vault.
