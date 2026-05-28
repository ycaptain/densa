# Roadmap

> Lightweight project roadmap — what's shipped, queued, and on the
> watch-list. Maintained by the upstream maintainer; updated alongside
> [`CHANGELOG.md`](CHANGELOG.md) release markers.
>
> Last updated: 2026-05-28 (showcase v1→v2 migration + structured
> lint promotion-candidates struck — both shipped).

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
- **PyPI publication** — so `pipx install densa` works without a
  prior clone (tracked in CHANGELOG `[Unreleased]`).

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
  [`docs/reference/harness-memory-vs-llm-wiki.md` §2](docs/reference/harness-memory-vs-llm-wiki.md#2-cline-memory-bank--project-state-docs).
- **`query` → `outputs/notes/<date>-<wiki-page>.md` micro-artifact** —
  evaluate giving `query` a way to file *fine-grained fact
  candidates* (one fact per file) that the next `lint` proposes for
  merge into an existing wiki page. The schema-friendly equivalent
  of Letta's `/remember`. Validate on a small sample (≥10 query
  sessions) before deciding; do **not** add a sixth operation —
  this stays inside `query`'s existing write scope. Rationale
  anchor:
  [`docs/reference/harness-memory-vs-llm-wiki.md` §6](docs/reference/harness-memory-vs-llm-wiki.md#6-letta-personal-memory--agent-identity-memory).
- **Prompt progressive-disclosure benchmark** — measure the
  onboarding four-file token cost (L1 + active L2 + op prompt +
  index snapshot) under a typical ingest. If it exceeds ~30% of the
  4-tool consensus context budget (Cursor / Claude Code / Codex /
  Cline), split each `_system/prompts/<op>.md` into a `header +
  on-demand body` per the Codex Skills progressive-disclosure
  pattern. Skip if under budget — `AGENTS.md` already mandates
  on-demand loading.
- **MCP server path — RFC** — Tolaria's "MCP everywhere" posture
  (15 tools auto-registered across Claude Code / Cursor / Gemini
  CLI / OpenCode) is the highest-leverage cross-tool reach we
  haven't taken. Decision needed: build (write `_system/densa/mcp/`
  + Tolaria-style auto-registration installer) vs. publish a stable
  CLI surface (`densa query`, `densa ingest`) and let users wire
  MCP themselves. Source: [`docs/maintainers/prior-art/2026-05-25-tolaria-study.md`](docs/maintainers/prior-art/2026-05-25-tolaria-study.md).

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
  in [`docs/reference/harness-memory-vs-llm-wiki.md`](docs/reference/harness-memory-vs-llm-wiki.md);
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
