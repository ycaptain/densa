# Prompt: lint

Use this prompt when the human says `lint` or `lint --domain <X>`.
Canonical procedure for
[`/AGENTS.md` §"lint"](../../AGENTS.md#23-lint---domain-x).

## What this command will write (schema contract)

| Path                                          | When                          | Why                                                  |
|-----------------------------------------------|-------------------------------|------------------------------------------------------|
| `outputs/lint/<YYYY-MM-DD>.md`                | always                        | the lint report itself                               |
| `outputs/snapshots/index-snapshot.md`         | always                        | machine-readable index mirror (refreshed every lint) |
| `domains/<X>/wiki/<page>.md`                  | additive auto-fix only        | missing cross-references / cross-domain tag / index entry |
| `domains/<X>/log.md`                          | always                        | audit trail                                          |
| `log.md`                                      | always                        | global lint timeline                                 |

> This table mirrors `densa.schema.OPERATIONS['lint'].writes`.
> AGENTS011 warns on drift. Destructive fixes (page deletion, rename,
> rewrite) are *always* surfaced as human-review, never auto-applied.

## In one paragraph

Enumerate the wiki against the previous report as a baseline, then run
four tiers of checks: mechanical residue (orphans, stubs, index drift,
alias collisions), provenance gates (citation depth, quote integrity,
`last_validated` TTL — the anti-poisoning core), narrative (contradictions,
stale claims, missing pages/cross-refs), and domain-specific rules.
Compose a delta-first report under `outputs/lint/`, refresh the
machine-readable index snapshot, surface promotion candidates, and
**auto-apply only additive, low-risk fixes** — everything destructive
is flagged `human-review`. The pre-commit hook already catches the
mechanical errors, so a healthy lint report is *boring*.

## Non-negotiables

- **Never delete or rename pages** — flag for deprecation/rename and
  leave the call to the human; renames cascade through wikilinks.
- **Auto-apply additive fixes only** — missing cross-refs, index
  entries, empty required fields, `cross-domain` tags, snapshot
  refresh. Deletes / status flips / rewrites stay `human-review`.
- **`lint` never promotes** — it surfaces candidates; the human runs
  `promote`.
- **Provenance findings dominate** — if mechanical issues appear, a
  pre-commit hook bypass happened and should be investigated.

## Before you execute

Load **[`lint.body.md`](lint.body.md)** for the full procedure: the
pre-commit-overlap note, all four check tiers, the Q&A spot-check
ingestion and promotion-candidate scoring, the full report skeleton
and index-snapshot shape, the log-entry shape, the complete hard-rules
list, and the quality bar. The header above is enough to know *what*
`lint` does and *what it writes*; the body is what you follow to *run*
it.
