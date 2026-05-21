# Contributing to llm-wiki-starter

Thanks for your interest. This project is a *schema-first* template: the
load-bearing artifacts are markdown contracts (`AGENTS.md`, prompts,
templates) and a small validator (`_system/wikilint/`). Most
useful contributions improve those, not application code.

By participating you agree to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).

## Where to start

| You want to...                                  | Open                                                              |
| ----------------------------------------------- | ----------------------------------------------------------------- |
| Report a bug in `wikilint` / hooks / prompts    | a `bug_report` issue                                              |
| Propose a schema change (new page type, etc.)   | a `feature_request` issue (discuss before PR — L1 changes are not lightly merged) |
| Get help designing your own L2 domain           | a `domain-design-help` issue (we'll work through the four design questions with you) |
| Fix a typo, broken link, or doc clarity         | a PR directly                                                     |

## Before submitting a PR

1. **Run the validator locally** against the whole tree:

   ```bash
   python -m wikilint --all
   ```

   It must report `OK: ... 0 error(s) ...`. CI runs the same check on
   every PR.

2. **Wire the pre-commit hook** (one-time):

   ```bash
   git config core.hooksPath _system/hooks
   ```

   This catches red-line violations (raw immutability, log append-only,
   `analysis.sources` cardinality, wikilink resolvability) before they
   reach a PR. The hook is pure stdlib — no `pip install` required.

3. **For changes to the validator** (`_system/wikilint/`):

   ```bash
   pip install -e ".[dev]"
   pytest             # unit tests
   ruff check _system/wikilint _system/tests
   mypy _system/wikilint
   ```

   All four must be green. The same tools run in CI on every PR
   touching the validator. To iterate on a single check, run
   `pytest _system/tests/ -k <check-name> -v`.

4. **Follow the commit message convention** from `AGENTS.md` §9:

   ```
   <op>(<scope>): <short summary>

   <optional body explaining the why>
   ```

   Examples:
   - `docs(readme): clarify quickstart`
   - `feat(validate): warn on stale last_validated`
   - `fix(prompts): unbroken wikilink in ingest.md`

5. **Keep PRs small.** One concern per PR. A typo fix and a schema
   tweak should not share a branch.

## If the pre-commit hook rejects your first commit (AGENTS007)

The validator classifies commits by their leading prefix
(`ingest(<domain>):`, `query:`, `lint:`, `process-inbox:`,
`promote:`, or no recognised prefix). Each class has its own
allowed write scope — see [`AGENTS.md`](AGENTS.md) §2.0. The most
common first-commit rejection looks like:

```
✗ AGENTS007 operation-writes-within-scope
  commit prefix: (no prefix)
  this prefix may write: _system/**, docs/**, integrations/**,
                         outputs/**, projects/**, writing/**,
                         AGENTS.md, README.md, CHANGELOG.md, *.md at root
  violation: domains/research-papers/wiki/concepts/new-page.md
```

What the message is telling you: a commit without an operation
prefix is treated as schema / docs / integrations maintenance and
MUST NOT touch `domains/**`. Two recoveries:

- **Did you mean to ingest?** The change belongs in an `ingest`
  commit. Move the wiki edit out of this commit, redo it via the
  `ingest` flow (`_system/prompts/ingest.md`), and use
  `git commit -m "ingest(<domain>): <date> <slug>"`.
- **Did you mean to do unrelated docs work?** Move the
  `domains/**` edit to a separate commit (with the correct prefix)
  and keep the original commit prefix-free. Two small commits
  beat one rejected omnibus.

Last-resort bypass (sanctioned multi-scope maintenance only):

```bash
WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "<your message>"
```

The bypass MUST be paired with a follow-up `## [YYYY-MM-DD]
maintenance | …` entry in `log.md` explaining the cross-scope
write. Don't reach for this on a first contribution — the
two-commit fix above is almost always cleaner.

## Red lines (will block merge)

These mirror the L1 contract in [`AGENTS.md`](AGENTS.md) §6. Do not:

- Edit, rename, move, or delete anything under `*/raw/`.
- Rewrite past entries in any `log.md` (newest entry goes immediately
  below the preamble; older entries scroll down).
- Delete wiki pages. Deprecate instead (`status: deprecated`).
- Bulk-rename slugs across the wiki — wikilinks cascade and need human
  review.
- Change `compiled_against:` schema version without shipping a
  migration script under `_system/scripts/migrate_NN_<slug>.py`.

## Changing the L1 schema

`AGENTS.md` encodes invariants the LLM relies on across every domain.
Changes here have outsized blast radius. Before opening a PR:

1. Open an issue describing the proposed change, the failure mode it
   addresses, and at least one alternative considered.
2. Wait for maintainer sign-off on the issue.
3. Then send the PR, which must include:
   - The schema edit itself.
   - A migration script under `_system/scripts/` if the change is
     breaking (i.e. existing wiki pages would no longer validate).
   - Bumped `schema_version` in the frontmatter at the top of
     `AGENTS.md` if breaking.
   - An entry in `CHANGELOG.md` under `## [Unreleased]`.

## Adding an example L2 domain

The repo ships **three** example L2s (`research-papers`, `workspace`,
`psychology`) covering light/medium/heavy schema density across
distinct working subjects. See
[`docs/EXAMPLE-DOMAINS.md`](docs/EXAMPLE-DOMAINS.md) for the full
per-domain matrix.

New seed L2s are welcome — open an issue first (use the
[`domain-design-help`](.github/ISSUE_TEMPLATE/domain-design-help.md)
template) to discuss persona / page-types / required frontmatter, then
PR a directory under `domains/`. The bar for inclusion is "would a
plausible adopter of this template ship this exact L2 unmodified" —
worked examples need a real-looking persona and a synthesised raw set
that ingests cleanly.

## License

By contributing, you agree your contributions are licensed under the
[MIT License](LICENSE).
