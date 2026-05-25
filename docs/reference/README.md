# Reference docs

> [!faq]- Who reads this folder?
> **Humans: skip by default.** These are the long tables broken out of
> [`AGENTS.md`](../../AGENTS.md) so the contract file stays short. Load
> a page only when you're debugging a specific rule, designing an L2,
> or hunting a particular schema constant. None of these files are
> required reading to operate the vault — the README → GUIDE → first
> ingest path covers everything you need to start.
>
> **LLM: load on demand.** AGENTS.md and the per-operation prompt will
> point you at the specific reference page when one is needed (e.g.
> ingest references `sources-cardinality.md` when filling
> frontmatter). Don't pre-load the whole folder.

Schema details broken out of [`../../AGENTS.md`](../../AGENTS.md) so the
contract file stays short.

| Page | What's in it |
|---|---|
| [`karpathy-mapping.md`](karpathy-mapping.md) | Karpathy llm-wiki ↔ Densa vocabulary glossary; v1 → v2 type rename table |
| [`operation-scopes.md`](operation-scopes.md) | AGENTS007 per-prefix write-scope table + bypass usage |
| [`sources-cardinality.md`](sources-cardinality.md) | `sources` cardinality contract by page type |
| [`schema-versioning.md`](schema-versioning.md) | When/how to bump `schema_version`; `last_validated` semantics; migration runbook |
| [`rules-registry.md`](rules-registry.md) | AGENTS001–012 stable IDs, severity, bypasses |
| [`repository-layout.md`](repository-layout.md) | Full annotated vault tree (broken out of [AGENTS.md §"Layered architecture"](../../AGENTS.md#1-layered-architecture)) |
| [`red-lines.md`](red-lines.md) | Full failure-mode rationale for each red line |
| [`design-rationale.md`](design-rationale.md) | The long-form design essay — every load-bearing decision, the L1/L2 split, the `outputs/` / `promote` design choices, how to design your own L2, anti-patterns |

The Python source of truth is
[`../../_system/densa/schema.py`](../../_system/densa/schema.py) —
page types, operation specs, migrations, and the Karpathy mapping all
live there as plain data. The runtime view (rule registry, assembled
type enum, and operation-write globs) is in
[`../../_system/densa/config.py`](../../_system/densa/config.py), which
re-exports from `schema.py`. When either file disagrees with anything
here, the Python wins (mechanical enforcement) — but please open an
issue.

## Back to the canonical dispatcher

For "what should I read next?" decisions, return to
[`../../README.md` §"Where to read next"](../../README.md#where-to-read-next)
— it is the single source for cross-doc routing across `setup.md`,
`faq.md`, `cjk-workflow.md`, and this reference folder.
