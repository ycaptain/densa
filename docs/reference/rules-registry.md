# Rules registry (AGENTS001–012)

Reference companion to
[`AGENTS.md` §"Machine-enforced rule registry"](../../AGENTS.md#61-machine-enforced-rule-registry).
The red lines in
[`AGENTS.md` §"Red lines"](../../AGENTS.md#6-red-lines-non-negotiable)
are mechanically enforced by the `densa` validator under stable IDs.
**Pin the ID — never the name — in any suppression comment or commit
message; rule names may be refined, IDs are forever.**

The Python data source is
[`_system/densa/schema.py`](../../_system/densa/schema.py) (page types,
operation specs, migrations); the rule registry itself — IDs, bypass
env vars, and severities — is assembled in
[`_system/densa/config.py`](../../_system/densa/config.py)
`RULES`. Run `python -m densa rules` for the live registry; this page
mirrors it for human reading.

## The registry

Each rule links the AGENTS.md anchor or reference page that documents
the contract it enforces.

| ID        | Rule                          | Enforces                                                                                                                                                                                 | Severity     | Notes                                                                                       |
| --------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------- |
| AGENTS001 | raw-immutability              | [AGENTS.md §"Red lines"](../../AGENTS.md#6-red-lines-non-negotiable) (raw immutable)                                                                                                     | error        | rejects edits, deletes, renames of `*/raw/**`                                               |
| AGENTS002 | log-append-only               | [AGENTS.md §"Red lines"](../../AGENTS.md#6-red-lines-non-negotiable) (log reverse-chronological append-only)                                                                             | error        | bypass: `WIKI_ALLOW_LOG_REORDER=1` (reorder) or `WIKI_ALLOW_MIGRATION=1` (migration commit) |
| AGENTS003 | frontmatter-required-keys     | [AGENTS.md §"Frontmatter schema"](../../AGENTS.md#3-frontmatter-schema-universal) (universal frontmatter)                                                                                | error        | universal keys: `type`, `domain`, `created`, `updated`, `status`, `compiled_against`        |
| AGENTS004 | frontmatter-type-allowed      | [AGENTS.md §"Frontmatter schema"](../../AGENTS.md#3-frontmatter-schema-universal) (type enum)                                                                                            | error        | enum source: `_system/densa/schema.py` `ALLOWED_TYPES`                                      |
| AGENTS005 | analysis-sources-cardinality  | [`sources-cardinality.md`](sources-cardinality.md)                                                                                                                                       | error        | `analysis.sources` MUST contain exactly one raw wikilink                                    |
| AGENTS006 | wikilink-resolvable           | [AGENTS.md §"Naming and linking conventions"](../../AGENTS.md#4-naming-and-linking-conventions)                                                                                          | error / warn | error on unresolved; warn on ambiguous                                                      |
| AGENTS007 | operation-writes-within-scope | [AGENTS.md §"Operation writes"](../../AGENTS.md#20-operation-writes-machine-enforced-via-agents007)                                                                                      | error        | bypass: `WIKI_ALLOW_CROSS_SCOPE=1`; enforced by the `commit-msg` hook (real subject via `DENSA_COMMIT_MSG_FILE` = `$1`) — the pre-commit hook skips it, the message doesn't exist yet at that stage |
| AGENTS008 | last-validated-fresh          | [`schema-versioning.md`](schema-versioning.md) (`last_validated` semantics)                                                                                                              | warning      | fires at 180 days                                                                           |
| AGENTS009 | compiled-against-current      | [`schema-versioning.md`](schema-versioning.md)                                                                                                                                           | warning      | fires when page lags current `schema_version`                                               |
| AGENTS010 | schema-version-consistency    | [`schema-versioning.md`](schema-versioning.md) (vN pages outside `.legacy/` MUST declare current `compiled_against`)                                                                     | error        | fix: `python -m densa migrate`                                                              |
| AGENTS011 | prompt-schema-sync            | [AGENTS.md §"Operation writes"](../../AGENTS.md#20-operation-writes-machine-enforced-via-agents007) (prompt's `## What this command will write` table mirrors `densa.schema.OPERATIONS`) | warning      | catches "AI changed rules in one place, forgot the others"                                  |
| AGENTS012 | migration-history-hygiene     | [AGENTS.md §"Upgrading an existing vault"](../../AGENTS.md#12-upgrading-an-existing-vault) (`migration_history` is well-formed and consistent with `compiled_against`)                   | warning      | keeps the upgrade audit trail honest                                                        |

`DENSA-IO` (also returned by `python -m densa rules`) is a meta
diagnostic, not a rule — it signals the validator could not read a
file. Treat it as infrastructure: fix the file-read problem, then
re-run.

## Bypass env vars

| Env var                    | Effect                                                                                   | Pair with                                                                                         |
| -------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `WIKI_ALLOW_LOG_REORDER=1` | Skip AGENTS002 for one commit (narrow exception: pure-permutation reorder sweep)         | a follow-up `## [YYYY-MM-DD] maintenance \| …` entry in `log.md`                                  |
| `WIKI_ALLOW_MIGRATION=1`   | Skip AGENTS002 for one migration commit (wikilink rewrites inside past `log.md` entries) | a staged addition to `_system/migrations.log` in the **same commit** — the env var alone is inert |
| `WIKI_ALLOW_CROSS_SCOPE=1` | Skip AGENTS007 for one commit (sanctioned multi-scope maintenance)                       | a follow-up `## [YYYY-MM-DD] maintenance \| …` entry in `log.md`                                  |

All bypasses are deliberately narrow. The audit pairing requirement
means a bypass leaves a trail; reviewers see at a glance how often
the escape hatch was used and why.

## Selecting / ignoring rules

```bash
# Run only one rule (handy when debugging an AGENTS003 false positive):
PYTHONPATH=_system python -m densa --all --select AGENTS003

# Skip a rule (e.g. while landing a wikilink renaming spree):
PYTHONPATH=_system python -m densa --all --ignore AGENTS006
```

Rule selection is a developer convenience; CI (`.github/workflows/ci.yml`)
runs the full set unconditionally.
