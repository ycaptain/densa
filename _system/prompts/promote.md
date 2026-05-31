# Prompt: promote

Use this prompt when the human says `promote <qa-path>` (with an
optional `--as <type>`). Canonical procedure for
[`/AGENTS.md` §"promote"](../../AGENTS.md#25-promote-qa-path-qa--wiki-page).
It upgrades a `query`-produced Q&A artifact under `outputs/qa/` into a
first-class wiki page via a controlled information-shape transform, not
a bare `git mv`.

## What this command will write (schema contract)

| Path                                              | When                                                      | Why                                                  |
|---------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| `domains/<X>/wiki/<folder>/<slug>.md`             | always (created via git mv from outputs/qa/)              | the promoted Q&A becomes a first-class wiki page     |
| `outputs/qa/<source>.md`                          | always (the source Q&A is moved away)                     | git mv preserves history; `git log --follow` traces back |
| `outputs/lint/<latest>.md`                        | when the latest lint report has a Human-review queue      | append residual issues from the promoted Q&A         |
| `domains/<X>/log.md`                              | always                                                    | audit trail                                          |
| `log.md`                                          | only when cross-domain                                    | global timeline                                      |

> This table mirrors `densa.schema.OPERATIONS['promote'].writes`.
> AGENTS011 warns on drift. Promote is **1:1**: one Q&A becomes one
> wiki page; never batch multiple Q&As in a single promote commit.

## In one paragraph

Run all pre-flight checks first (source is a real `outputs/qa/` report,
target type is L2-allowed, slug/aliases don't collide, `sources:`
cardinality is met) and abort cleanly if any fails. Then, in a single
`promote:` commit, `git mv` the Q&A into its wiki home and apply the
four-stage transform — voice (Q&A scaffold → declarative prose),
citation hoist (inline links → `sources:` frontmatter), L2 fill-in
(target-type fields), section restructure (match the template) — and
prepend newest-first log entries. The `git mv` is load-bearing: it
keeps `git log --follow` history back to the original question.

## Non-negotiables

- **Pre-flight is non-skippable** — any failed check aborts with a
  specific message; no partial promotion, no silent edits.
- **1:1 granularity** — one Q&A → one wiki page; never batch multiple
  Q&As in a single commit.
- **No `--in-place` mode** — the move is always `outputs/qa/` →
  `domains/<X>/wiki/<folder>/`, or the `query`/`promote` write scopes
  would overlap.
- **`lint` never promotes** — only the human invokes `promote`.
- **Use `git mv`, not write+delete** — preserves the audit trail.

## Before you execute

Load **[`promote.body.md`](promote.body.md)** for the full procedure:
the pre-flight checklist, the four-stage transform with its L2 field
tables, the git-operation and log-entry shapes, the complete
hard-rules list, and the quality bar. The header above is enough to
know *what* `promote` does and *what it writes*; the body is what you
follow to *run* it.
