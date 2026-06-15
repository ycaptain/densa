# Roadmap

> Lightweight project roadmap — what's shipped, queued, and on the
> watch-list. Maintained by the upstream maintainer; updated alongside
> [`CHANGELOG.md`](CHANGELOG.md) release markers.
>
> Last updated: 2026-05-29 (pre-launch plan filed — MCP-server RFC
> closed as "build, stdlib JSON-RPC"; three n=7-backed differentiators
> promoted to short term).

## Current state (2026-05-26)

- **Schema version:** v2 (Karpathy vocab) — see
  [`AGENTS.md`](AGENTS.md) frontmatter.
- **Release marker:** v0.5.0 (Karpathy vocab + onboarding clarity
  sweep) — see [`CHANGELOG.md`](CHANGELOG.md).
- **Validator:** 210+ files tracked, AGENTS001–AGENTS013 enforced;
  CI parity via direct `python -m X` commands
  (`densa --all` / `pytest` / `ruff check .` / `mypy`).
- **Integrations:** Cursor plugin + Claude Code plugin under
  [`integrations/`](integrations/); manifests align with each host's
  official plugin schema; submission to public registries pending
  (see Short term below).

## Short term (0–3 months)

> **Pre-launch focus.** The four items marked **[launch]** below are
> sequenced as Phases A–D of the maintainers' pre-launch plan and
> gate the `v0.7.0` open-source launch tag. Each is anchored to an
> n=7 prior-art finding.

- **[launch] MCP server (stdlib JSON-RPC, zero-dep)** — _RFC closed:
  build it._ Hand-rolled JSON-RPC/stdio under `_system/densa/mcp/`,
  leaving `_system/densa/` core dependency-free. Exposes the compiled
  wiki + validator as read/navigate/lint **tools** and the five
  operations as MCP **prompts** (no write tools; the human gate is
  unchanged) — "the opposite of RAG" rendered in MCP. Completes the
  AGENTS.md + MCP + plugin triple no upstream occupies
  (n=7; Tolaria's 15-tool surface is the spec template). Was
  medium-term "MCP server path — RFC".
- **[launch] `<untrusted>` fenced ingest** — first documented
  prompt-injection mitigation in the wiki-compiler space; injection
  posture is uniformly weak across all n=7 (survey finding §3.9).
  Prompt-only change.
- **[launch] Two-step ingest (analysis → generation)** — nashsu + olw
  independently converge on the split for quality; aligns with the
  existing plan-first gate. Prompt-only change.
- **Cursor plugin marketplace submission** — manifest is schema-aligned
  as of 2026-05-26; logo + submission via
  [`cursor.com/marketplace/publish`](https://cursor.com/marketplace/publish);
  procedural checklist in the maintainers' submission notes.
- ~~**`examples/showcases/` v1 → v2 migration** — the two heavier
  showcases (`psychology/`, `workspace/`) ship on v1 frontmatter
  per the v2-bump CHANGELOG; migration is parametric and will run
  via the existing `_system/scripts/migrate_02_karpathy_vocab.py`
  with an `--extra-roots` flag.~~ _Shipped 2026-05-26: the
  migration ran with `--mode in-place --extra-roots
examples/showcases` (logged in
  [`_system/migrations.log`](_system/migrations.log)); both
  showcase `AGENTS.md` files now carry a "v1 design — v2 schema"
  banner pointing readers at
  [`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md)
  and the active default L2._
- **agentskills.io reference-impl listing** — apply once it accepts
  curated entries; reference-impl rationale anchored at the n=7
  prior-art mid-checkpoint.
- **[launch] PyPI publication** — so `pipx install densa` works without
  a prior clone (tracked in CHANGELOG `[Unreleased]`; Phase C of the
  pre-launch plan: OIDC trusted-publishing workflow + Quickstart
  rewrite to lead with `pipx install densa && densa init`).

## Medium term (3–6 months)

- **`body_hash:` guard — AGENTS014 (warn, Phase B)** — each wiki page
  carries `body_hash: sha256:<hex>` in frontmatter; AGENTS014 warns when
  an ingest would overwrite a page whose hash has diverged from the stored
  value (meaning a human edited it between ingests). Default-on, warn-level
  (matches AGENTS008 precedent). Opt-out: `body_hash_check: skip` per-page
  frontmatter. Guard does **not** fire on `.legacy/` moves (that is the
  legitimate overwrite path). Implementation alongside the
  literal-grounding rule below (both anti-drift validator additions).
- **Literal-grounding rule (warn) — next free `AGENTS0NN`** — port
  olw's Knowledge-Item-Candidates literal-match check; the strongest
  anti-hallucination pattern in the n=7 set (survey finding §3.8).
  Extends the public rule registry. _De-scoped from the launch gate
  2026-06-15: it never shipped, and the `AGENTS013` ID it had been
  pencilled into was instead taken by `obsidian-link-format` (the
  graph-readability batch). Do **not** re-pin a number until it ships
  (pre-pinning is what caused the earlier 013 collision). Re-promote to
  a `[launch]` blocker only if the anti-hallucination posture is judged
  tag-critical._
- **`feedback:` field + `%%FEEDBACK%%` marker (Phase B)** — two-granularity
  user-correction loop. Whole-page: `feedback:` YAML array in frontmatter
  (`opened`, `text`, `applied`); next ingest acknowledges + sets `applied:
<date>`. Section-level: `%%FEEDBACK: …%%` inline parallel to `%%HUMAN%%`;
  LLM fixes the flagged text and removes the marker. Blast radius is
  page-local only. See [`docs/faq.md` §"How do I correct…"](docs/faq.md#how-do-i-correct-the-llms-output-without-it-forgetting).
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
  currently surfaced only as free-text in the report.~~ _Shipped
  2026-05-28 via [`_system/prompts/lint.md`](_system/prompts/lint.md)
  §6.6 + the `## Promotion candidates` report skeleton; each
  candidate is now emitted as a fenced YAML record with `qa /
suggested_type / suggested_slug / criteria_met / reason`, and
  zero-candidate runs explicitly emit `\_No candidates this run._`
  so downstream tooling can distinguish a clean run from a forgotten
  section.\_
- **`overview.md` sub-section template** — evaluate borrowing the
  Cline Memory Bank "multi-section project state" pattern as
  _optional_ anchored sub-sections inside the existing single
  `overview.md` (no schema change). Trigger: when a domain's
  overview exceeds ~200 lines or its mindmap stops being scannable.
  Rationale anchor:
  [`docs/design/harness-memory-vs-llm-wiki.md` §2](docs/design/harness-memory-vs-llm-wiki.md#2-cline-memory-bank--project-state-docs).
- **`query` → `outputs/notes/<date>-<wiki-page>.md` micro-artifact** —
  evaluate giving `query` a way to file _fine-grained fact
  candidates_ (one fact per file) that the next `lint` proposes for
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
- ~~**MCP server path — RFC**~~ _Closed 2026-05-29: **build it**, as a
  hand-rolled stdlib JSON-RPC/stdio server under `_system/densa/mcp/`
  with a Tolaria-style auto-registration installer — promoted to a
  **[launch]** short-term item above. The "stable CLI surface + let
  users wire MCP" alternative was rejected: `densa query`/`ingest` are
  LLM operations, not deterministic CLI calls, so a CLI surface
  wouldn't carry them. Tool surface frozen in
  [`_system/densa/mcp/SPEC.md`](_system/densa/mcp/SPEC.md)._

## Watch-list (informational only)

Projects in the wiki-compiler / agent-memory neighbourhood that we
re-evaluate each release cycle (full studies live in the
maintainers' prior-art notes):

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
- **`densa run` thin orchestrator (v0.8 if demand surfaces)** — a
  `densa run <op> <path>` subcommand that shells out to
  `DENSA_AGENT_CLI` (e.g. `claude`, `codex`) without adding SDK
  deps. Solves the headless/batch-ingest friction case. Land when
  ≥2 users report "headless workflow" as a blocker; until then
  the human-in-the-loop gate is the default. Design sketch:
  [`docs/design/harness-memory-vs-llm-wiki.md` §"Thin orchestrator seam"](docs/design/harness-memory-vs-llm-wiki.md#thin-orchestrator-seam--the-v08-watch-item-t004).

## Non-goals

- A managed hosting / SaaS offering. Densa stays a local-first
  markdown + git substrate; vendor lock-in is the failure mode the
  red lines prevent.
- An in-vault embedding-search runtime. Past ~500 pages, layer
  Smart Connections (Obsidian) or any embedding tool _on top_ of the
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
