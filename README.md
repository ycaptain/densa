# Densa

> **An [AGENTS.md](https://agents.md)-native agent skill pack that
> compiles your sources into a queryable markdown wiki — the opposite
> of RAG.**
> Drop new material into `raw/`. An AI agent in your IDE reads it,
> drafts which `wiki/` pages to touch, waits for your OK, then writes
> the edits. Every ingest *densifies* your second brain instead of
> growing the haystack you re-search every query.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/ycaptain/densa/actions/workflows/ci.yml/badge.svg)](https://github.com/ycaptain/densa/actions/workflows/ci.yml)
[![Schema version](https://img.shields.io/badge/schema-v2-informational)](AGENTS.md)
[![Skill: Cursor / Claude Code / Codex](https://img.shields.io/badge/skill-cursor%20%7C%20claude%20%7C%20codex-blueviolet)](AGENTS.md)

One ingest cycle, end-to-end (cite:
[`examples/hello-world/`](examples/hello-world/) for the literal
files):

```mermaid
sequenceDiagram
    autonumber
    participant You
    participant Agent as AI agent (Cursor / Claude Code / Codex)
    participant Vault as Densa vault (raw / wiki / log)
    You->>Vault: drop source.md into raw/
    You->>Agent: "ingest raw/source.md"
    Agent->>Vault: read source + relevant wiki pages
    Agent->>You: planned edits (4 pages, ~60 lines diff)
    You->>Agent: approve / edit / reject
    Agent->>Vault: write summary + concept pages + log entry
    Vault->>Vault: pre-commit hook validates (AGENTS001-012)
    Vault->>You: green commit; wiki densifies
```

Image of: 1 source → 1 `summary` + 2 `concept` pages + 1 log entry.
That's the loop. Now scale it.

## Pick your path

| You want to... | Open | Time |
|---|---|---|
| **Glance** — see what one ingest produces, no install | [`examples/hello-world/`](examples/hello-world/) (source + expected wiki output + log entry) | 3 min |
| **Try the slash commands** — sideload the plugin into Cursor without committing to a vault | [`integrations/cursor/densa-plugin/` §Install Option B](integrations/cursor/densa-plugin/#option-b--local-sideload-works-today) (symlink + restart Cursor) | ~5 min |
| **Set up your own vault** | [Quickstart](#quickstart) below → [`docs/setup.md`](docs/setup.md) | ~30 min to first ingest |
| **Evaluate the design** | [`docs/reference/design-rationale.md`](docs/reference/design-rationale.md) | ~1 hr deep read |

[`GUIDE.md`](GUIDE.md) is the day-to-day FAQ + scenarios; bookmark
it for *after* your first ingests. [`docs/setup.md`](docs/setup.md)
covers everything from the Obsidian plugin matrix to git-crypt to
the domain decision tree. [`docs/faq.md`](docs/faq.md) answers the
"why" questions (red lines, drift, operation philosophy).

---

## Quickstart

There is one supported path. It works today, no PyPI required.

```bash
# 1. Fork ycaptain/densa on GitHub (one click), then clone your fork:
git clone git@github.com:<you>/densa.git my-vault
cd my-vault
git remote add upstream https://github.com/ycaptain/densa.git

# 2. Wire the pre-commit validator (pure stdlib, no pip install):
git config core.hooksPath _system/hooks
git config --get core.hooksPath        # verify: should print _system/hooks

# 3. Open the folder in Cursor / Claude Code / Codex / Cline, paste
#    docs/bootstrap.md into the chat. The agent interviews
#    you, drafts your first L2 schema, and walks the first ingest.
```

That's it. The agent reads [`AGENTS.md`](AGENTS.md) natively in every
major coding-agent IDE. Manual validation any time:

```bash
PYTHONPATH=_system python -m densa --all
```

**Optional IDE plugins** (slash commands + auto-triggered skills) live
under [`integrations/`](integrations/) — currently
[`claude-code/`](integrations/claude-code/) (Claude Code marketplace
manifest + slash commands) and
[`cursor/densa-plugin/`](integrations/cursor/densa-plugin/) (Cursor
plugin manifest + IDE-agnostic `SKILL.md` files). New users who want
to feel the operations before standing up a vault can take the "Try
the slash commands" path in the table above (~5 min sideload).
Both plugins are **experimental** — they're convenience surfaces on
the same operation prompts; the vault works identically without
them.

The 12 enforced rules (`AGENTS001`–`AGENTS012`) are documented at
[`docs/reference/rules-registry.md`](docs/reference/rules-registry.md);
`python -m densa rules` prints the live registry. Obsidian plugin
setup, encryption, disabling the hook, and the domain decision tree
all live in [`docs/setup.md`](docs/setup.md).

**Realistic time-to-first-ingest**: ~30 minutes for a one-page article,
~60 minutes for a meeting transcript whose L2 schema needs new fields.
The agent does the typing; you do the reviewing.

<sub>*Naming note: the project is **Densa**; `python -m densa` is the
stdlib validator that ships with it. The supported install today is
`git clone` + `git config core.hooksPath _system/hooks` above, or
`densa init` from an existing Densa install (see Alternative below).
PyPI publication (so `pipx install densa` works without first cloning)
is planned but not yet available — see the "Unreleased" entry in
[`CHANGELOG.md`](CHANGELOG.md).*</sub>

### Alternative: scaffold without cloning by hand

If you already have a working Densa clone (or `pip install -e .` in
one), `densa init <destination>` automates the steps above: it clones
upstream into `<destination>`, wires the pre-commit hook, walks
example-domain disposition, and (optionally) injects
`docs/bootstrap.md` into your AI agent.

```bash
PYTHONPATH=_system python -m densa init my-vault
# or, after `pip install -e .` in a Densa clone:
densa init my-vault
```

Useful when you're standing up multiple vaults; for your *first*
vault the fork-and-clone path above stays compatible with the
bootstrap prompt's expectations.

### Staying in sync with upstream

Densa upstream **never touches** `domains/**` — that namespace is
yours. Upgrades evolve `AGENTS.md` (schema), `_system/densa/`
(validator), `_system/prompts/` (operations), and templates only.

```bash
git fetch upstream && git merge upstream/main
```

When a release ships a breaking schema change (new `compiled_against`
version), the merge brings a `_system/scripts/migrate_NN_<slug>.py`
that idempotently brings your existing wiki pages forward.

---

## What this is

Densa is an **AGENTS.md-native agent skill pack** — a complete L1/L2
schema, five-operation contract, and stdlib-only machine validator
that any AGENTS.md-aware IDE (Cursor, Claude Code, Codex, Cline) can
read natively to maintain a personal markdown wiki. It is a
**full, executable implementation of** Andrej Karpathy's
[llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) —
his ~1500-word sketch where an LLM compiles your sources into a
structured wiki that compounds, rather than retrieving raw chunks on
every query (the RAG pattern).

Karpathy described **what to build**. Densa gives you the **how**:

- A **schema** (nine page types: `summary`, `entity`, `concept`,
  `comparison`, `overview`, `synthesis`, `open-question`, `source`,
  `report` — every name comes verbatim from Karpathy's gist plus the
  `report` extension for operation artifacts).
- A **stdlib-only validator** (`python -m densa`) that enforces the
  schema on every commit.
- **Five operation prompts** (`ingest` / `query` / `lint` /
  `process-inbox` / `promote`) the agent loads on demand.
- **Migration tooling** (`python -m densa migrate`) for carrying an
  existing vault forward when upstream ships a breaking schema bump.
- A shipped **example domain** (`research-papers/`) plus two
  heavier showcases under `examples/showcases/`.

> [!important] `research-papers/` is **both** the shipped showcase
> and the active default L2 your fork starts with. Replace its
> contents with your own raws (or rename / delete the directory)
> per
> [`docs/setup.md` §"Choosing or replacing the default domain"](docs/setup.md#choosing-or-replacing-the-default-domain)
> before your first real ingest — don't try to "build on" the
> worked example.

If you read Karpathy's gist and thought "ok but where do I start"
— this is where. Vocabulary glossary:
[`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md).

![Storyboard: one Densa ingest cycle — drop source, agent plans, human approves, agent writes summary + concepts + log entry](assets/hello-world-ingest.svg)

The plan-first-then-apply gate is the same for every operation; you
never see edits land without consent. For a worked example of one
ingest cycle (source → plan → wiki diff → log entry), see
[`examples/hello-world/`](examples/hello-world/); for a week-in-the-life
narrative see
[`GUIDE.md` §"A day in the life"](GUIDE.md#a-day-in-the-life).

---

## The five operations

`ingest` / `query` / `lint` / `process-inbox` / `promote` are the only
verbs you ever type. Each has a canonical procedure under
[`_system/prompts/`](_system/prompts/) the agent loads on demand;
[`AGENTS.md` §"The five operations"](AGENTS.md#2-the-five-operations)
is the long-form contract (what each writes, what it forbids). The
natural-language → operation mapping lives in
[`GUIDE.md` §"Mapping natural language to operations"](GUIDE.md#mapping-natural-language-to-operations).

The validator at [`_system/densa/`](_system/densa/) enforces the
red lines on every commit and in CI:
`PYTHONPATH=_system python -m densa --all`.

---

## Why not just RAG?

Classic RAG (`documents → parser → chunks → vector DB → retrieve →
answer`) **never structurally crystallises** — every question
reassembles fragments at query time, leaving the LLM as a permanent
hallucination surface above the haystack. Densa compiles your
sources into structured prose **once, incrementally**, then queries
the prose. The hallucination surface is a one-time write-time event
(audited by `AGENTS001`–`AGENTS012`), not a per-query risk.

| Tool | Storage | Compounds? | Cites sources? | Local-first? |
| ---- | ------- | ---------- | -------------- | ------------ |
| **Densa** (this repo) | plain markdown + git | yes | enforced by validator | yes |
| Vector RAG (LlamaIndex / LangChain) | vector DB | no | optional | varies |
| Enterprise RAG ([RAGFlow](https://github.com/infiniflow/ragflow)) | ES + MySQL + chunk records | no (chunks re-rank per query) | read-time visual citations | yes (self-host) |
| Notion AI / mem.ai | proprietary DB | partially | sometimes | no |
| [Obsidian + Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) | markdown + index | retrieve-only | no | yes |

**The fault line.** Two architectural families both call themselves
"AI knowledge bases":

- **RAG-classic** ([RAGFlow](https://github.com/infiniflow/ragflow),
  vector stacks, Notion AI) — documents → chunks → retrieve at query
  time. Fast onboarding; never structurally consolidates; the
  hallucination surface is the answer text on every query.
- **Wiki-compiler** (Karpathy pattern; Densa;
  [Tolaria](https://github.com/refactoringhq/tolaria);
  [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki);
  [`kytmanov/obsidian-llm-wiki-local`](https://github.com/kytmanov/obsidian-llm-wiki-local))
  — raw sources → LLM compiles structured prose → query the prose.
  Slower onboarding; structure compounds; the hallucination surface
  is a write-time event under human review.

A 2026-05 review of the wiki-compiler space (six upstream projects
at four artifact layers) sediments Densa's specific differentiation:
**MIT + stdlib-only Python validator**, **L2 per-domain schema**
layering, **public `AGENTS001`–`AGENTS012` rule registry**,
**`.legacy/` schema-migration snapshot** red line, and
**AGENTS.md-native** posture across Cursor / Claude Code / Codex /
Cline. Maintainer-only details:
[`docs/maintainers/prior-art/`](docs/maintainers/prior-art/).

Past ~500 pages, layer embedding search on top of the wiki as fuzzy
fallback. The wiki gives you compounded structure; embedding search
gives you fuzzy recall. **Both, not either.** Detailed comparison
lives in [`docs/reference/design-rationale.md`](docs/reference/design-rationale.md).

---

## Why not just `CLAUDE.md` / Memory Bank / Letta?

Densa is a **schema, not a harness**. Your coding agent (Cursor /
Claude Code / Codex / Cline / Pi / OpenCode) is replaceable; the
markdown wiki it maintains is not. Six other layers in the agent stack
look like "knowledge bases" but bind their data to one runtime:

- **`AGENTS.md` / `CLAUDE.md` / Rules** — static instructions, not
  accumulated knowledge.
- **[Cline Memory Bank](https://docs.cline.bot/best-practices/memory-bank)** —
  project state continuity, no source-grounding.
- **[Codex / Pi Skills](https://developers.openai.com/codex/skills)** —
  reusable procedures, not facts.
- **Session memory / compaction** — runtime checkpoints; transient by
  design.
- **RAG / MCP / VFS retrieval** — synthesises at query time, doesn't
  file the answer back. The Karpathy critique applies.
- **[Letta-style personal memory](https://docs.letta.com/letta-code/memory/)** —
  agent self-edits memory blocks, but the artifact is bound to one
  vendor harness ([LangChain's framing](https://www.langchain.com/blog/your-harness-your-memory)).

Densa is the seventh layer: markdown + git, validated by
`AGENTS001`–`AGENTS012`, browsable in any markdown reader, survives
swapping your agent. Full taxonomy with per-layer decision tree:
[`docs/reference/harness-memory-vs-llm-wiki.md`](docs/reference/harness-memory-vs-llm-wiki.md).

---

## Where this sits in the ecosystem

A 2026-05-25 maintainer-only review (n=7 upstream projects read at
the README + architecture-docs level; see
[`docs/maintainers/prior-art/`](docs/maintainers/prior-art/) for the
full study set) anchors Densa's position relative to adjacent OSS
projects. Every row below cites a specific study file so the diff is
verifiable.

| Project | Pattern | What it does well | Where Densa differs |
| --- | --- | --- | --- |
| [Tolaria](https://github.com/refactoringhq/tolaria) | Wiki-compiler desktop app + MCP-everywhere | 15-tool MCP server auto-registers across Claude Code / Cursor / Gemini CLI / OpenCode / generic clients; per-vault `AGENTS.md` + `CLAUDE.md` + `GEMINI.md` triple ([study](docs/maintainers/prior-art/2026-05-25-tolaria-study.md)) | Tolaria's "types as lenses, not schemas" stance refuses any enum + validator; Densa's closed 9-type enum + `AGENTS001`–`AGENTS012` is the diametric philosophy |
| [`nashsu/llm_wiki`](https://github.com/nashsu/llm_wiki) | Wiki-compiler desktop app + SKILL.md | Two-step CoT ingest (analysis → generation); SHA-256 incremental cache; SKILL.md trigger discipline ([study](docs/maintainers/prior-art/2026-05-25-nashsu-llm-wiki-study.md)) | No `.legacy/` snapshot; no `type:` enum; no L2 per-domain schema layering; lint rule set not publicly documented |
| [`kytmanov/obsidian-llm-wiki-local`](https://github.com/kytmanov/obsidian-llm-wiki-local) | Wiki-compiler Python CLI (MIT) | Closest architectural sibling to Densa; Knowledge Item Candidates ledger (literal-match source-grounding); rejection-feedback loop; hash-mismatch hand-edit guard ([study](docs/maintainers/prior-art/2026-05-25-obsidian-llm-wiki-local-study.md)) | Single flat vault, no L2 domain layering; no `AGENTS.md` (`vault-schema.md` instead); no MCP / SKILL.md / plugin exposure; upstream in maintenance mode (succeeded by [Synto](https://github.com/kytmanov/synto)) |
| [Smart Composer](https://github.com/glowingjade/obsidian-smart-composer) + [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) | Obsidian assistant (out-of-pattern complement) | Cursor-flavoured `@`-mention UX; one-click Apply Edit; Smart Environment shared substrate across plugins ([paired study](docs/maintainers/prior-art/2026-05-25-smart-composer-connections-study.md)) | Not wiki-compilers — they solve "AI assists in-place editing", not "AI compiles a wiki". Co-installable with Densa; source-grounding posture is the weakest in the surveyed set |
| [RAGFlow](https://github.com/infiniflow/ragflow) | Enterprise RAG (Category E anchor) | DeepDoc multimodal parsing (PDF / DOCX / PPT / scanned); visual chunk inspection + read-time citation traceability ([study](docs/maintainers/prior-art/2026-05-25-ragflow-study.md)) | Architectural inverse — read-time grounding vs Densa's write-time grounding; heavy server stack (Docker + ES + MySQL + 16 GB RAM); not a per-vault tool. Pair-with, not substitute |
| [Graphiti](https://github.com/getzep/graphiti) + [Cognee](https://github.com/topoteretes/cognee) | Temporal graph memory (Category F; informational only) | Bi-temporal validity windows on facts; episodes-as-provenance; both ship MCP integration ([paired study](docs/maintainers/prior-art/2026-05-25-graphiti-cognee-study.md)) | Different layer entirely (graph DB vs markdown wiki); v0.8 watch-list anchor only. Densa stays at the markdown layer; pair downstream if fact-level temporal queries ever need it |

**Empirical findings the table sediments** (n=7):

- **No upstream covers more than two agent-exposure surfaces.** Densa's
  planned AGENTS.md + MCP server + plugin / SKILL.md triple is
  empirically unoccupied — a defensible-by-superset bet, not a
  validated-by-precedent one.
- **`.legacy/` schema-migration snapshot is uniquely Densa's red line.**
  Of the seven upstreams, none ships an equivalent mechanism — they
  use SHA-256 cache + cascade delete (nashsu), git history alone
  (Tolaria), hash-mismatch refusal (olw), or no equivalent (the rest).
- **MIT + stdlib-only Python is uniquely Densa's combo.** Tolaria is
  AGPL-3.0-or-later; nashsu is GPL-3.0; RAGFlow + Graphiti + Cognee
  are Apache 2.0 but drag heavy transitive deps; olw is MIT but ships
  SQLite + embedding runtime. Only Densa's `_system/densa/` can be
  `cp -R`'d into a downstream fork with zero runtime deps.
- **Public `AGENTS001`–`AGENTS012` rule registry is uniquely Densa's.**
  nashsu and olw ship lint surfaces but neither publishes the rule
  set; Densa's
  [`docs/reference/rules-registry.md`](docs/reference/rules-registry.md)
  + `python -m densa rules` is the only public stable-ID registry.

---

## Sensitive material

If your `raw/` will ever hold therapy notes, medical records, NDA
material, or anything you wouldn't post in a public thread, treat
encryption as part of setup. See [`SECURITY.md`](SECURITY.md) and
[`docs/setup.md` §"Privacy — sensitive material"](docs/setup.md#privacy--sensitive-material) for
the walkthrough. The schema is language-neutral; the wiki happily
holds CJK content — see [`docs/cjk-workflow.md`](docs/cjk-workflow.md).

---

## Where to read next

Pick one based on what you're trying to do.

- **Day-to-day use** — [`GUIDE.md`](GUIDE.md). A day in the life,
  the seams between operations, mental model.
- **Setup beyond Quickstart** — [`docs/setup.md`](docs/setup.md).
  Obsidian plugins, encryption, disabling the hook, CI, domain
  decisions.
- **Conceptual FAQ** — [`docs/faq.md`](docs/faq.md). The red lines,
  scale & drift, operation philosophy.
- **Evaluating the design** —
  [`docs/reference/design-rationale.md`](docs/reference/design-rationale.md).
  Every load-bearing decision explained.
- **Starting your own vault from scratch** —
  [`docs/bootstrap.md`](docs/bootstrap.md).
- **Hacking on the schema / validator / prompts** —
  [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## License & acknowledgements

[MIT](LICENSE) © 2026 ycaptain. Built on Andrej Karpathy's
[llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f);
selective conventions from
[`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills).
The structural invariants — raw / wiki / AGENTS, the five operations,
the red lines, the frontmatter schema — are domain-agnostic and should
outlive any particular LLM provider.

Discussions and PRs welcome:
[GitHub Discussions](https://github.com/ycaptain/densa/discussions).

<!--
Suggested GitHub repo Topics (Settings → About → topics):
  agents-md, llm, ai-agents, cursor, claude-code, codex, obsidian,
  personal-knowledge-management, second-brain, rag-alternative,
  markdown, knowledge-graph, densa, pkm
-->
