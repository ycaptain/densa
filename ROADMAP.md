# Roadmap

> Lightweight project roadmap — what's shipped, queued, and on the
> watch-list. Maintained by the upstream maintainer; updated alongside
> [`CHANGELOG.md`](CHANGELOG.md) release markers.
>
> Last updated: 2026-05-29 (pre-launch plan filed — MCP-server RFC
> closed as "build, stdlib JSON-RPC"; three n=7-backed differentiators
> promoted to short term. Sequencing in
> [`docs/maintainers/2026-05-29-pre-launch-plan.md`](docs/maintainers/2026-05-29-pre-launch-plan.md)).

## Current state (2026-05-26)

- **Schema version:** v2 (Karpathy vocab) — see
  [`AGENTS.md`](AGENTS.md) frontmatter.
- **Release marker:** v0.5.0 (Karpathy vocab + onboarding clarity
  sweep) — see [`CHANGELOG.md`](CHANGELOG.md).
- **Validator:** 210+ files tracked, AGENTS001–AGENTS012 enforced;
  CI parity via direct `python -m X` commands
  (`densa --all` / `pytest` / `ruff check .` / `mypy`).
- **Integrations:** Cursor plugin + Claude Code plugin under
  [`integrations/`](integrations/); manifests align with each host's
  official plugin schema; submission to public registries pending
  (see Short term below).

## Short term (0–3 months)

> **Pre-launch focus.** The four items marked **[launch]** below are
> sequenced as Phases A–D in
> [`docs/maintainers/2026-05-29-pre-launch-plan.md`](docs/maintainers/2026-05-29-pre-launch-plan.md)
> and gate the `v0.7.0` open-source launch tag. Each is anchored to an
> n=7 prior-art finding; the plan carries the file-level scope.

- **[launch] MCP server (stdlib JSON-RPC, zero-dep)** — *RFC closed:
  build it.* Hand-rolled JSON-RPC/stdio under `_system/densa/mcp/`,
  leaving `_system/densa/` core dependency-free. Exposes the compiled
  wiki + validator as read/navigate/lint **tools** and the five
  operations as MCP **prompts** (no write tools; the human gate is
  unchanged) — "the opposite of RAG" rendered in MCP. Completes the
  AGENTS.md + MCP + plugin triple no upstream occupies
  (n=7; [Tolaria's 15-tool surface](docs/maintainers/prior-art/2026-05-25-tolaria-study.md)
  is the spec template). Was medium-term "MCP server path — RFC".
- **[launch] `<untrusted>` fenced ingest** — first documented
  prompt-injection mitigation in the wiki-compiler space; injection
  posture is uniformly weak across all n=7
  ([finding §3.9](docs/maintainers/prior-art/2026-05-25-research-action-plan.md)).
  Prompt-only change.
- **[launch] Two-step ingest (analysis → generation)** — nashsu + olw
  independently converge on the split for quality; aligns with the
  existing plan-first gate. Prompt-only change.
- **[launch] AGENTS013 literal-grounding rule (warn)** — port olw's
  Knowledge-Item-Candidates literal-match check; the strongest
  anti-hallucination pattern in the set
  ([finding §3.8](docs/maintainers/prior-art/2026-05-25-research-action-plan.md)).
  Extends the public rule registry.
- **Cursor plugin marketplace submission** — manifest is schema-aligned
  as of 2026-05-26; logo + submission via
  [`cursor.com/marketplace/publish`](https://cursor.com/marketplace/publish);
  procedural checklist in
  [`docs/maintainers/skill-pack-submission.md` §C](docs/maintainers/skill-pack-submission.md#c-cursor-plugin-marketplace-live-as-of-2026-05).
- ~~**`examples/showcases/` v1 → v2 migration** — the two heavier
  showcases (`psychology/`, `workspace/`) ship on v1 frontmatter
  per the v2-bump CHANGELOG; migration is parametric and will run
  via the existing `_system/scripts/migrate_02_karpathy_vocab.py`
  with an `--extra-roots` flag.~~ *Shipped 2026-05-26: the
  migration ran with `--mode in-place --extra-roots
  examples/showcases` (logged in
  [`_system/migrations.log`](_system/migrations.log)); both
  showcase `AGENTS.md` files now carry a "v1 design — v2 schema"
  banner pointing readers at
  [`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md)
  and the active default L2.*
- **agentskills.io reference-impl listing** — apply once it accepts
  curated entries; reference-impl rationale anchored at the n=7
  prior-art mid-checkpoint
  ([`docs/maintainers/prior-art/2026-05-25-research-action-plan.md`](docs/maintainers/prior-art/2026-05-25-research-action-plan.md)).
- **[launch] PyPI publication** — so `pipx install densa` works without
  a prior clone (tracked in CHANGELOG `[Unreleased]`; Phase C of the
  pre-launch plan: OIDC trusted-publishing workflow + Quickstart
  rewrite to lead with `pipx install densa && densa init`).

## Medium term (3–6 months)

- **Obsidian `.base` evaluation** — adopt only if Dataview drift
  (any block exceeding ~50 rendered rows, or `index.md` rendering
  becoming noticeably slow) crosses the trigger described in
  [`docs/faq.md` §"Scale & drift"](docs/faq.md#scale--drift).
- **`domains/<X>/wiki/.legacy/` re-ingest flow** — operational
  prompt for re-ingesting a previously-authored wiki page in the
  newer schema, while preserving the `.legacy/` snapshot
  (the contract is in [`AGENTS.md` §6](AGENTS.md#6-red-lines-non-negotiable);
  the operational prompt isn't shipped yet).
- ~~**Structured "promotion candidates" output from `lint`** —
  currently surfaced only as free-text in the report.~~ *Shipped
  2026-05-28 via [`_system/prompts/lint.md`](_system/prompts/lint.md)
  §6.6 + the `## Promotion candidates` report skeleton; each
  candidate is now emitted as a fenced YAML record with `qa /
  suggested_type / suggested_slug / criteria_met / reason`, and
  zero-candidate runs explicitly emit `_No candidates this run._`
  so downstream tooling can distinguish a clean run from a forgotten
  section.*
- **`overview.md` sub-section template** — evaluate borrowing the
  Cline Memory Bank "multi-section project state" pattern as
  *optional* anchored sub-sections inside the existing single
  `overview.md` (no schema change). Trigger: when a domain's
  overview exceeds ~200 lines or its mindmap stops being scannable.
  Rationale anchor:
  [`docs/design/harness-memory-vs-llm-wiki.md` §2](docs/design/harness-memory-vs-llm-wiki.md#2-cline-memory-bank--project-state-docs).
- **`query` → `outputs/notes/<date>-<wiki-page>.md` micro-artifact** —
  evaluate giving `query` a way to file *fine-grained fact
  candidates* (one fact per file) that the next `lint` proposes for
  merge into an existing wiki page. The schema-friendly equivalent
  of Letta's `/remember`. Validate on a small sample (≥10 query
  sessions) before deciding; do **not** add a sixth operation —
  this stays inside `query`'s existing write scope. Rationale
  anchor:
  [`docs/design/harness-memory-vs-llm-wiki.md` §6](docs/design/harness-memory-vs-llm-wiki.md#6-letta-personal-memory--agent-identity-memory).
- **Prompt progressive-disclosure benchmark** — measure the
  onboarding four-file token cost (L1 + active L2 + op prompt +
  index snapshot) under a typical ingest. If it exceeds ~30% of the
  4-tool consensus context budget (Cursor / Claude Code / Codex /
  Cline), split each `_system/prompts/<op>.md` into a `header +
  on-demand body` per the Codex Skills progressive-disclosure
  pattern. Skip if under budget — `AGENTS.md` already mandates
  on-demand loading.
- ~~**MCP server path — RFC**~~ *Closed 2026-05-29: **build it**, as a
  hand-rolled stdlib JSON-RPC/stdio server under `_system/densa/mcp/`
  with a Tolaria-style auto-registration installer — promoted to a
  **[launch]** short-term item above. The "stable CLI surface + let
  users wire MCP" alternative was rejected: `densa query`/`ingest` are
  LLM operations, not deterministic CLI calls, so a CLI surface
  wouldn't carry them. Rationale + tool surface in
  [`docs/maintainers/2026-05-29-pre-launch-plan.md` §1](docs/maintainers/2026-05-29-pre-launch-plan.md).
  Source: [`Tolaria study`](docs/maintainers/prior-art/2026-05-25-tolaria-study.md).*

## Watch-list (informational only)

Projects in the wiki-compiler / agent-memory neighbourhood that we
re-evaluate each release cycle; full studies under
[`docs/maintainers/prior-art/`](docs/maintainers/prior-art/):

- [Synto](https://github.com/kytmanov/synto) — successor to
  `obsidian-llm-wiki-local`; re-read at v0.7 to see whether its
  Knowledge Item Candidates ledger pattern is portable.
- [`lucasastorian/llmwiki`](https://github.com/lucasastorian/llmwiki) /
  [`ussumant/llm-wiki-compiler`](https://github.com/ussumant/llm-wiki-compiler) —
  two additional Karpathy-pattern implementations queued for the
  next prior-art sweep.
- [Graphiti](https://github.com/getzep/graphiti) + [Cognee](https://github.com/topoteretes/cognee) —
  temporal graph memory; v0.8 watch-list anchor if Densa ever needs
  fact-level temporal queries (pair downstream, do not replace the
  markdown layer).
- **Harness ↔ memory boundary** — LangChain's
  ["Your harness, your memory"](https://www.langchain.com/blog/your-harness-your-memory)
  thesis is the public framing of the lock-in problem Densa's
  schema-side approach answers structurally. Distilled positioning
  in [`docs/design/harness-memory-vs-llm-wiki.md`](docs/design/harness-memory-vs-llm-wiki.md);
  re-read each release cycle to confirm the harness landscape
  hasn't moved the goal posts (e.g. a vendor shipping a true
  markdown-export contract).

## Non-goals

- A managed hosting / SaaS offering. Densa stays a local-first
  markdown + git substrate; vendor lock-in is the failure mode the
  red lines prevent.
- An in-vault embedding-search runtime. Past ~500 pages, layer
  Smart Connections (Obsidian) or any embedding tool *on top* of the
  wiki as fuzzy fallback; embeddings don't belong in the validator.
- A non-stdlib validator. The "MIT + stdlib-only Python" combination
  is one of Densa's four uniquely-occupied positions in the prior-art
  n=7 study; we will not introduce runtime dependencies into
  `_system/densa/`.

## How this roadmap evolves

- Each release marker in `CHANGELOG.md` may add / strike items
  here; the file's `updated:` line at the top is bumped in lockstep.
- Watch-list items that get an action plan move from "Watch-list" up
  to "Short term" or "Medium term".
- Strikes use [GitHub-flavoured ~~strikethrough~~](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables)
  with a short rationale and the release that shipped or rejected
  the item.

Feedback / requests / "you should also build X" via
[GitHub Discussions](https://github.com/ycaptain/densa/discussions).
