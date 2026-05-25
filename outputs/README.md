# outputs/

`outputs/` contains rebuildable artifacts produced by operations
(`lint`, `query`). Wiki pages MUST NOT cite files here — the wikilink
resolver deliberately ignores this directory, so the wiki link graph
stays free of runtime noise.

Layout:

| Subdir         | Producer  | Contents                                              | Notes                       |
| -------------- | --------- | ----------------------------------------------------- | --------------------------- |
| `lint/`        | `lint` op | `<YYYY-MM-DD>.md` health-check reports (`type: report`) | one per run                 |
| `snapshots/`   | `lint` op | `index-snapshot.md` machine-readable index mirror     | overwritten each run        |
| `qa/`          | `query` op | `<YYYY-MM-DD>-<slug>.md` Q&A archives (`type: report`) | one per substantive query   |

> **On-demand creation.** `lint/` and `qa/` don't ship in a fresh
> fork — the agent creates them the first time it writes a report or
> Q&A artifact. `snapshots/` ships pre-populated (it carries the
> bootstrap `index-snapshot.md` that the LLM onboarding set in
> [AGENTS.md §1.1](../AGENTS.md) points at).

The canonical onboarding entry for fresh LLM sessions is
[`outputs/snapshots/index-snapshot.md`](snapshots/) (see
[AGENTS.md §1.1](../AGENTS.md)).

**Promotion path.** If a Q&A under `qa/` proves to be evergreen knowledge
worth wikilink-graph membership, run
`promote outputs/qa/<file>.md` (see
[`_system/prompts/promote.md`](../_system/prompts/promote.md)). Promote
performs a controlled information-shape transform: question →
declarative voice, inline `[[wikilink]]` set → frontmatter `sources:`,
L2 type-specific fields filled, with pre-flight checks (≥2 sources for
synthesis, slug+aliases dedup) enforced. Manual `git mv` is a viable
escape hatch but loses the audit + pre-flight checks.

Safe to inspect; safe to `git rm` old reports/Q&A when they accumulate
(retention is user-managed — no auto-rotation).
