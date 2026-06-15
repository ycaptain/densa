---
type: overview
domain: meta
created: 2026-05-24
updated: 2026-05-24
sources: []
tags: [reference, layout]
aliases: ["vault layout", "repo layout"]
status: active
compiled_against: 2
---

# Repository layout

Reference companion to
[`AGENTS.md` §"Layered architecture"](../../AGENTS.md#1-layered-architecture).
The full annotated tree of every directory a Densa vault is expected
to have, broken out of the contract file so AGENTS.md stays short.

> When this page and `AGENTS.md` disagree, `AGENTS.md` wins (it is
> the normative schema). When `AGENTS.md` and
> [`_system/densa/schema.py`](../../_system/densa/schema.py) disagree,
> the Python wins (machine-enforced).

## Full annotated tree

```
<vault>/
├── AGENTS.md                    ← L1 schema (the contract)
├── GUIDE.md                     ← human-facing day-to-day guide (explanatory)
├── README.md                    ← human onboarding entry (Pick your path)
├── CHANGELOG.md                 ← release notes (this template's history)
├── index.md                     ← global content map
├── log.md                       ← global append-only timeline
├── inbox/                       ← optional: un-routed material (see AGENTS.md §"process-inbox")
├── outputs/                     ← operation artifacts (in git, not in wikilink graph)
│   ├── lint/<YYYY-MM-DD>.md
│   ├── snapshots/index-snapshot.md
│   └── qa/<YYYY-MM-DD>-<slug>.md
├── _system/
│   ├── prompts/{ingest,query,lint,process-inbox,promote,visualize}.md   ← 6 operation prompts the agent loads on demand
│   ├── prompts/domains/         ← domain-specific sub-prompts
│   ├── templates/               ← page templates (one per v2 type) + vault-readme.md skeleton
│   ├── scripts/                 ← migration scripts (migrate_NN_<slug>.py)
│   ├── hooks/pre-commit         ← stdlib-only shim → `python -m densa --staged`
│   ├── densa/                   ← Python validator package (schema.py is SSOT)
│   ├── migrations.log           ← record of applied migrations
│   └── tests/
├── docs/
│   ├── bootstrap.md             ← one-shot prompt the human pastes into a fresh fork (NOT an op-prompt)
│   ├── setup.md                 ← install + Obsidian + encryption + domain decisions
│   ├── faq.md                   ← red lines, scale & drift, operation philosophy
│   ├── cjk-workflow.md          ← Chinese / Japanese / Korean conventions
│   ├── design/                  ← the "why" essays (read when evaluating the design)
│   │   ├── README.md
│   │   ├── design-rationale.md  ← long-form design essay
│   │   └── harness-memory-vs-llm-wiki.md
│   ├── reference/               ← schema reference (long tables; the "what")
│   │   ├── README.md
│   │   ├── karpathy-mapping.md
│   │   ├── operation-scopes.md
│   │   ├── red-lines.md
│   │   ├── repository-layout.md ← this file
│   │   ├── rules-registry.md
│   │   ├── schema-versioning.md
│   │   └── sources-cardinality.md
│   ├── .gitattributes.example   ← fork-template dotfile (git-crypt / filter setup)
│   └── maintainers/             ← .gitignored: design archive, prior-art, tracker
├── .github/                     ← GitHub community-health + CI (rendered by GitHub from here)
│   ├── CONTRIBUTING.md          ← contributor guide
│   ├── SECURITY.md              ← vulnerability reporting + vault hardening
│   ├── CODE_OF_CONDUCT.md
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/ci.yml
├── examples/                    ← opt-in showcases + hello-world demo (not in wikilink graph)
│   ├── hello-world/             ← 5-minute demo: source.md + expected wiki output + hello-world-ingest.svg
│   └── showcases/<X>/           ← heavier shipped L2s (workspace, psychology, …)
├── integrations/                ← (optional) agent-specific UX add-ons (Claude Code plugin)
├── domains/<X>/                 ← your active L2(s) — this is the namespace you own
│   ├── AGENTS.md                ← L2 schema (persona + ontology)
│   ├── index.md
│   ├── log.md
│   ├── raw/                     ← READ ONLY: source material
│   └── wiki/                    ← LLM-owned synthesised pages
│       ├── overview.md          ← per-domain reader entry point (mindmap + Dataview)
│       ├── summaries/           ← 1:1 with raw (`type: summary`)
│       ├── entities/            ← people / orgs / objects (`type: entity`)
│       ├── concepts/            ← recurring terms (`type: concept`)
│       ├── comparisons/         ← X vs Y (`type: comparison`)
│       ├── overviews/           ← sub-area bird's-eye views (`type: overview`)
│       ├── syntheses/           ← braided cross-source narratives (`type: synthesis`)
│       ├── open-questions/      ← long-arc trackers (`type: open-question`)
│       └── .legacy/             ← optional: pre-vN snapshots, lint-skipped
└── attic/                       ← deprecated / quarantined files
```

## Which directories upstream owns vs. you own

Densa upstream commits never touch `domains/**` — that namespace is
yours, even when you fetch / merge upstream. Everything else is
template-managed:

- **Upstream-managed**: `AGENTS.md`, `_system/**`, `docs/**`,
  `integrations/**`, `examples/**`, root-level `*.md`,
  `.github/**`, `pyproject.toml`, `noxfile.py`.
- **You-managed**: `domains/**`, `inbox/**`, `outputs/**`,
  `attic/**`. (`outputs/**` is technically machine-written by the
  agent during `lint`/`query`, but it never collides with upstream.)

When upstream ships a breaking schema change, the merge brings a
`_system/scripts/migrate_NN_<slug>.py` that idempotently brings your
`domains/**` content forward. See
[`schema-versioning.md` §"Migration runbook"](schema-versioning.md#migration-runbook).

## On-demand directories

Several listed paths are created lazily — they don't exist on a
fresh fork:

- `inbox/` — created at first `process-inbox` invocation, or by the
  human dropping the first un-routed clip.
- `outputs/lint/`, `outputs/qa/` — created the first time `lint`
  writes a report or `query` files a Q&A artifact.
- `attic/` — created the first time you quarantine a deprecated file.
- `domains/<X>/wiki/.legacy/` — created at first bulk re-ingest of
  pre-existing content.

The validator skips paths that don't yet exist; their absence is not
a `lint` finding.
