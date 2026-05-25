# Operation write scopes (AGENTS007)

Reference companion to
[`AGENTS.md` §"Operation writes"](../../AGENTS.md#20-operation-writes-machine-enforced-via-agents007).
The
validator (`densa`) classifies a staged commit by its leading
commit-message prefix and rejects it if any staged path lies outside
the scope declared below.

The Python source of truth is
[`_system/densa/schema.py`](../../_system/densa/schema.py) `OPERATIONS`
(each op's `scope_globs` tuple); the assembled glob table at runtime
lives in
[`_system/densa/config.py`](../../_system/densa/config.py)
`OPERATION_WRITES`, derived from `OPERATIONS`. This page mirrors that
data for human reference; when the two disagree, the Python wins
(mechanical enforcement) but file a bug — they're meant to stay
synchronised.

## Per-prefix scopes

| Commit prefix | Paths that may be staged |
|---|---|
| `ingest(<domain>):` | `domains/*/wiki/**`, `domains/*/log.md`, `log.md` |
| `query:` | `outputs/qa/**`, `domains/*/log.md`, `log.md` |
| `lint:` | `outputs/**`, `domains/*/wiki/**` (additive auto-fix only), `domains/*/log.md`, `log.md` |
| `process-inbox:` | `domains/*/raw/**` (rename/move only via `git mv`), `domains/*/log.md`, `log.md` |
| `promote:` | `outputs/qa/**` (delete-intent, single file), `outputs/lint/**` (append "Issues to surface"), `domains/*/wiki/**`, `domains/*/log.md`, `log.md` |
| *(no recognised prefix)* | `_system/**`, `docs/**`, `examples/**`, `integrations/**`, `outputs/**`, `projects/**`, `writing/**`, `.github/**`, `AGENTS.md`, `GUIDE.md`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, `*.md` at repo root, `pyproject.toml`, `noxfile.py`, `.editorconfig`, `.gitignore`, `.gitattributes*`, `.pre-commit-hooks.yaml` — **never `domains/**`** |

## Bypass

Set `WIKI_ALLOW_CROSS_SCOPE=1` for one commit to skip AGENTS007. Use
only for sanctioned multi-scope maintenance (e.g. removing a shipped
example domain that touches `domains/**` from a `chore(domains):`
commit). The bypass MUST be paired with a follow-up
`## [YYYY-MM-DD] maintenance | …` entry in `log.md` explaining why.

```bash
WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "chore(domains): remove example domain workspace"
```

## Why this rule exists

A commit that crosses operation scopes is one of three things:

1. **A genuine mistake** (the agent meant to run two operations but
   bundled them into one commit). The validator catches this before
   it lands.
2. **A schema / docs change that incidentally touches a wiki page**
   (e.g. fixing a typo in a shipped example). This is the sanctioned
   `WIKI_ALLOW_CROSS_SCOPE` path.
3. **A drift from operation semantics** — e.g. a `query` commit that
   tried to "fix" a wiki page while reading it. This is the failure
   mode AGENTS007 prevents (see
   [`GUIDE.md` §"The seams"](../../GUIDE.md#the-seams-when-to-use-which-operation)
   *"Contradiction during `query`? Don't fix inline"*).
