# Contributing to Densa

This is a schema-first template. The interesting contributions are
markdown contracts (`AGENTS.md`, prompts, templates) and a small
validator (`_system/densa/`) — not application code. By
participating you agree to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).

## 🚀 Where to start

| You want to...                                  | Open                                                              |
| ----------------------------------------------- | ----------------------------------------------------------------- |
| Report a bug in `densa` / hooks / prompts     | a `bug_report` issue                                              |
| Propose a schema change (new page type, etc.)   | a `feature_request` issue first — L1 changes are not lightly merged |
| Get help designing your own L2 domain           | a `domain-design-help` issue (we'll work the four design questions with you) |
| Fix a typo, broken link, or doc clarity         | a PR directly                                                     |

### Good first PRs

If you want to contribute but don't have an itch yet:

- A typo or clarity fix anywhere in `docs/`, `_system/`, or the
  README.
- A new pytest case under `_system/tests/` exercising an edge case
  one of the AGENTS001–012 rules currently doesn't catch.
- A worked example seed L2 (see *Adding an example L2 domain* below).

## 🛠 Before submitting a PR

This project uses [**nox**](https://nox.thea.codes) as its task
runner — the Scientific Python Development Guide's PY007
recommendation. Cross-platform, Python-coded, explicit about what each
session runs.

### One-time setup

```bash
pip install -e ".[dev]"               # installs pytest + ruff + mypy + nox + pyyaml
```

Wire the pre-commit hook per
[`README.md` §"Quickstart"](README.md#quickstart) (one
`git config core.hooksPath _system/hooks` line). The hook itself is
**pure stdlib** — it doesn't need the `[dev]` extra. Install is only
for the validator's own dev suite.

### Run every gate CI runs

```bash
nox -s check                          # = lint + test + ruff + mypy
```

Or invoke them individually (these mirror `noxfile.py` verbatim;
the bare `densa --all` form is canonical because the pre-commit
hook and CI use it too):

| Session              | What it runs                                                                   |
| -------------------- | ------------------------------------------------------------------------------ |
| `nox -s lint`        | `python -m densa --all` (PYTHONPATH-set so it works pre-install)               |
| `nox -s lint-strict` | `DENSA_STRICT=1 python -m densa --all` (pyyaml backend)                        |
| `nox -s lint-diff`   | `python -m densa --diff origin/main` (PR-range staged-rule pass; override base via `nox -s lint-diff -- <ref>`) |
| `nox -s test`        | `python -m pytest`                                                             |
| `nox -s ruff`        | `python -m ruff check .`                                                       |
| `nox -s ruff-fix`    | `python -m ruff check --fix .`                                                 |
| `nox -s mypy`        | `python -m mypy`                                                               |
| `nox -s hook`        | `git config core.hooksPath _system/hooks` + verify                             |

Sessions reuse your current Python env (`venv_backend = "none"`) so
they run instantly — no per-session venv churn. CI runs the same
sessions over a Python 3.10 / 3.11 / 3.12 matrix.

### Iterate on a single check

```bash
nox -s test -- -k <check-name> -v   # args after `--` reach pytest
nox -s ruff-fix                     # auto-apply ruff fixes
```

### Commit message convention

Follow [`AGENTS.md` §"Versioning"](AGENTS.md#9-versioning):

```
<op>(<scope>): <short summary>

<optional body explaining the why>
```

Examples: `docs(readme): clarify quickstart`,
`feat(validate): warn on stale last_validated`,
`fix(prompts): unbroken wikilink in ingest.md`.

### Keep PRs small

One concern per PR. A typo fix and a schema tweak shouldn't share a
branch.

## If the pre-commit hook rejects your first commit (AGENTS007)

The validator classifies commits by their leading prefix
(`ingest(<domain>):`, `query:`, `lint:`, `process-inbox:`,
`promote:`, or no recognised prefix). Each class has its own allowed
write scope — see
[`AGENTS.md` §"Operation writes"](AGENTS.md#20-operation-writes-machine-enforced-via-agents007).
The most common
first-commit rejection looks like:

```
✗ AGENTS007 operation-writes-within-scope
  commit prefix: (no prefix)
  this prefix may write: _system/**, docs/**, integrations/**,
                         outputs/**, projects/**, writing/**,
                         AGENTS.md, README.md, CHANGELOG.md, *.md at root
  violation: domains/research-papers/wiki/concepts/new-page.md
```

A commit without an operation prefix is treated as schema / docs /
integrations maintenance and MUST NOT touch `domains/**`. Two
recoveries:

- **Did you mean to ingest?** Move the wiki edit out of this commit,
  redo it via the `ingest` flow
  ([`_system/prompts/ingest.md`](_system/prompts/ingest.md)), and use
  `git commit -m "ingest(<domain>): <date> <slug>"`.
- **Did you mean unrelated docs work?** Move the `domains/**` edit to
  a separate commit (with the correct prefix) and keep the original
  commit prefix-free. Two small commits beat one rejected omnibus.

Last-resort bypass (sanctioned multi-scope maintenance only):

```bash
WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "<your message>"
```

The bypass MUST be paired with a follow-up
`## [YYYY-MM-DD] maintenance | …` entry in `log.md` explaining the
cross-scope write. Don't reach for this on a first contribution — the
two-commit fix is almost always cleaner.

## ⚠️ Red lines (will block merge)

These mirror the L1 contract in
[`AGENTS.md` §"Red lines"](AGENTS.md#6-red-lines-non-negotiable).
Do not:

- Edit, rename, move, or delete anything under `*/raw/`.
- Rewrite past entries in any `log.md` (newest entry goes immediately
  below the preamble; older entries scroll down).
- Delete wiki pages. Deprecate instead (`status: deprecated`).
- Bulk-rename slugs across the wiki — wikilinks cascade and need human
  review.
- Change `compiled_against:` schema version without shipping a
  migration script under `_system/scripts/migrate_NN_<slug>.py`.

## 🧬 Changing the L1 schema

`AGENTS.md` encodes invariants the LLM relies on across every domain.
Changes here have outsized blast radius. Before opening a PR:

1. Open an issue describing the proposed change, the failure mode it
   addresses, and at least one alternative considered.
2. Wait for maintainer sign-off on the issue.
3. Then send the PR, which must include:
   - The schema edit itself.
   - A migration script under `_system/scripts/` if the change is
     breaking (existing wiki pages would no longer validate).
   - Bumped `schema_version` in the frontmatter at the top of
     `AGENTS.md` if breaking.
   - An entry in `CHANGELOG.md` under `## [Unreleased]`.

## 🌱 Adding an example L2 domain

The repo ships three example L2s (`research-papers`, `workspace`,
`psychology`) covering light/medium/heavy schema density across
distinct working subjects. See
[`docs/setup.md` §"Choosing or replacing the default domain"](docs/setup.md#choosing-or-replacing-the-default-domain)
for the per-domain matrix.

New seed L2s are welcome — open a
[`domain-design-help`](.github/ISSUE_TEMPLATE/domain-design-help.md)
issue first to discuss persona / page-types / required frontmatter,
then PR a directory under `domains/`. Bar for inclusion: *would a
plausible adopter of this template ship this exact L2 unmodified?*
Worked examples need a real-looking persona and a synthesised raw set
that ingests cleanly.

## License

By contributing, you agree your contributions are licensed under the
[MIT License](LICENSE).
