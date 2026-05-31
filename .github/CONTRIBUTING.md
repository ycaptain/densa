# Contributing to Densa

This is a schema-first agent skill pack. The interesting
contributions are markdown contracts (`AGENTS.md`, prompts,
templates) and a small
validator (`_system/densa/`) — not application code. By
participating you agree to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).

> [!faq]- I just want to use Densa in my own vault — do I need this page?
> **No.** This page targets contributors to the upstream
> [`ycaptain/densa`](https://github.com/ycaptain/densa) repo — PRs
> against the schema, validator, prompts, or templates. If you
> forked Densa and only edit your own vault content (your `raw/`
> sources and the `domains/<X>/wiki/` pages the agent compiles
> from them), your workflow is:
> [`README.md` §Quickstart](../README.md#quickstart) → daily use
> guided by [`GUIDE.md`](../GUIDE.md). The pre-commit hook installed
> via `git config core.hooksPath _system/hooks` is **pure stdlib**
> and needs no `pip install` for self-use. The dev extras (ruff /
> mypy / pytest, see below) only matter when you change validator
> code or open a PR against this repo.

| Your contribution kind | Jump to |
| --- | --- |
| Typo / 1-line doc fix | just open a PR |
| Validator / check authoring | [§"Before submitting a PR"](#-before-submitting-a-pr) |
| Schema / red-line change | [§"Changing the L1 schema"](#-changing-the-l1-schema) |

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

Or browse the
[`good first issue`](https://github.com/ycaptain/densa/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
label — each one is a self-contained, 1–2-hour task that links the
exact file to touch. The walkthrough below gets you from clone to a
green test in under half an hour.

## ⏱ Your first 30 minutes

The validator is built so a first contribution is small and
self-contained. Each lint rule is **one module under
[`_system/densa/checks/`](../_system/densa/checks/), one stable ID
(`AGENTS001`–`012`), and one test file** — so you can land a fix
without holding the whole system in your head.

**1. Set up (≈5 min).** From the repo root:

```bash
pip install -e ".[dev]"                     # pytest + ruff + mypy + pyyaml
PYTHONPATH=_system python -m densa doctor   # confirm your setup is wired right
PYTHONPATH=_system python -m densa --all    # confirm a clean baseline
python -m pytest                            # confirm the suite is green
```

If `densa doctor` shows a ✗, fix that first — it catches the usual
setup snags (unwired hook, wrong Python, an L2 domain that won't
parse) before they surface as a confusing validator error.

**2. Find your file via the rule↔file mapping (≈5 min).** The mapping
is direct — no indirection to chase:

```bash
PYTHONPATH=_system python -m densa rules    # the live AGENTS001–012 registry
```

A rule ID maps straight to its module: `AGENTS001` →
[`checks/raw_immutability.py`](../_system/densa/checks/raw_immutability.py),
`AGENTS007` →
[`checks/operation_writes_scope.py`](../_system/densa/checks/operation_writes_scope.py),
and so on (the
[rules registry doc](../docs/reference/rules-registry.md) lists every
pairing). The machine-readable contract those rules enforce lives in
[`_system/densa/schema.py`](../_system/densa/schema.py).

**3. Iterate on one check in a tight loop (≈15 min).** Run just the
test for the rule you're touching so the feedback is instant:

```bash
python -m pytest -k raw_immutability -v     # swap in your check's name
```

Test files mirror the modules under
[`_system/tests/`](../_system/tests/) (e.g.
`test_check_raw_immutability.py`). Add or adjust a fixture, watch it go
red, make your change, watch it go green.

**4. Before you push (≈5 min).** Run the four gates CI runs (next
section). Keep the PR to one concern, prefix the commit per the
[convention](#commit-message-convention) (a docs/validator change is
prefix-free and must not touch `domains/**` — see the AGENTS007 note
below), and open the PR.

That's the whole loop. If your first commit is rejected by the
pre-commit hook, the
[AGENTS007 section](#if-the-pre-commit-hook-rejects-your-first-commit-agents007)
below is almost always the fix.

## 🛠 Before submitting a PR

Canonical local commands are `python -m X` invocations matching the
pre-commit hook and CI verbatim — no task runner required. The
shipped Python validator is stdlib-only by design; the contributor
on-ramp is the same one-line `pip install -e ".[dev]"` plus four
direct `python -m X` invocations below.

### One-time setup

```bash
pip install -e ".[dev]"               # installs pytest + ruff + mypy + pyyaml
```

Wire the pre-commit hook per
[`README.md` §"Quickstart"](../README.md#quickstart) (one
`git config core.hooksPath _system/hooks` line). The hook itself is
**pure stdlib** — it doesn't need the `[dev]` extra. Install is only
for the validator's own dev suite.

### Run every gate CI runs

```bash
PYTHONPATH=_system python -m densa --all   # the full validator pass
python -m pytest                           # the test suite
python -m ruff check .                     # lint the validator code
python -m mypy                             # type-check the validator
```

Each command mirrors what the pre-commit hook (`_system/hooks/pre-
commit`) or CI runs verbatim. The `PYTHONPATH=_system` prefix on the
first command lets `densa` run before `pip install -e .` completes;
once installed, the bare `python -m densa --all` also works.

### Variants and PR-range checks

```bash
DENSA_STRICT=1 PYTHONPATH=_system python -m densa --all   # pyyaml backend
PYTHONPATH=_system python -m densa --diff origin/main     # PR-range staged-rule pass
python -m ruff check --fix .                              # auto-apply safe ruff fixes
python -m pytest -k <check-name> -v                       # iterate on a single check
```

### Commit message convention

Follow [`AGENTS.md` §"Versioning"](../AGENTS.md#9-versioning):

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
[`AGENTS.md` §"Operation writes"](../AGENTS.md#20-operation-writes-machine-enforced-via-agents007).
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
  ([`_system/prompts/ingest.md`](../_system/prompts/ingest.md)), and use
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
[`AGENTS.md` §"Red lines"](../AGENTS.md#6-red-lines-non-negotiable).
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
[`docs/setup.md` §"Choosing or replacing the default domain"](../docs/setup.md#choosing-or-replacing-the-default-domain)
for the per-domain matrix.

New seed L2s are welcome — open a
[`domain-design-help`](ISSUE_TEMPLATE/domain-design-help.md)
issue first to discuss persona / page-types / required frontmatter,
then PR a directory under `domains/`. Bar for inclusion: *would a
plausible adopter of this skill pack ship this exact L2 unmodified?*
Worked examples need a real-looking persona and a synthesised raw set
that ingests cleanly.

## License

By contributing, you agree your contributions are licensed under the
[MIT License](../LICENSE).
