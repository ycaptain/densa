# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/) for
the L1 schema version recorded in [`AGENTS.md`](AGENTS.md) frontmatter
(`schema_version`).

## [Unreleased]

The two subsections below capture two different states. **Planned**
items haven't been built yet — file an issue or PR. **Fixed / Added /
Example L2 cleanup** items have already landed on `main` after the
0.1.0 tag; they're waiting for a 0.1.1 / 0.2.0 release tag to ship.

### Planned

- **Publish `densa` to PyPI** so the `pipx install densa` flow in
  `README.md` works without first cloning the repo (today: install the
  CLI via `pip install -e .` inside a clone, then use `densa init`
  for additional vaults).
- First-`ingest` end-to-end walkthrough in `docs/EXAMPLES.md` (mirrors
  the existing `promote` walkthrough), using a shipped real-paper raw.
- `how-to-read-this-domain.md` synthesis page for `workspace` (matching
  the `research-papers` and `psychology` pattern).
- Structured "promotion candidates" output from `lint` (currently
  surfaced only as free-text in the report).

### Fixed (post-0.1.0 sweep)

Validator bugs (would otherwise bite first-week adopters):

- **AGENTS006 slot-index pollution**. `build_index()` indexed
  everything under `_system/templates/` (and `attic/` / `inbox/` /
  `outputs/`), so a typo like `[[concept]]` silently resolved to the
  template file rather than being flagged MISSING. Index now mirrors
  `wikilinks_scoped` exclusions; explicit-path wikilinks like
  `[[_system/MANUAL]]` still resolve via a separate full-repo index.
- **AGENTS001 inbox→raw rename false positive**. `StagedEntry` now
  carries the rename source path; the rule only forbids renames
  whose *source* sits under `raw/`. `git mv inbox/x.md
  domains/<X>/raw/<bucket>/y.md` (the canonical `process-inbox`
  action per L1 §2.4) is now permitted as designed.
- **AGENTS005 didn't require the source to be a raw file**. Per L1
  §3.1 `analysis.sources` MUST point at a raw file; the rule now
  resolves the wikilink and asserts the target lies under `raw/`.
- **`frontmatter.parse_stdlib` silently lost BOM-prefixed and
  CRLF-terminated frontmatter**, surfacing as false AGENTS003
  errors on Windows-authored pages. Both are now normalised.

CI coverage:

- **`densa --diff <base_ref>` mode** so CI can apply the staged
  rules (AGENTS001 / AGENTS002 / AGENTS007) over a PR range. Before
  this, a local `git commit --no-verify` bypassed every staged rule
  and CI had no way to catch it. `.github/workflows/ci.yml` now runs
  both `--all` (file rules) and `--diff origin/<base>` (staged rules)
  on every PR.

Docs / OSS polish:

- Reconciled the "three vs five example L2 domains" drift across
  `README.md`, `docs/EXAMPLE-DOMAINS.md`, `docs/bootstrap-prompt.md`.
- `_system/MANUAL.md §0` cheat sheet now lists `process-inbox` (was
  missing) and no longer claims a "Capture a fleeting note"
  operation (which violated L1 §6's source-traceability rule).
- `_system/prompts/process-inbox.md` no longer calls itself the
  "fourth operation" (there are five).
- `research-papers/AGENTS.md` opener now correctly says six page
  types (was "three"); `workspace/AGENTS.md` opener documents the
  source/session synonym so the 8 vs 9 row count is unambiguous.
- `setup_encryption.sh` defaults are commented out — `README.md`
  and `_system/SETUP.md` now say so explicitly instead of implying
  there is a default path list.
- `AGENTS.md` §3.4 formalises `cross-domain` as a first-class tag
  (the ingest/lint prompts already required it).
- `DENSA-IO` (meta diagnostic for unreadable files) is now in
  the rule registry, so `--ignore DENSA-IO` works.
- Dropped dead references to `pydantic` and
  `densa.checks.l2_extensions` from `__init__.py` / `config.py`.

Example L2 cleanup:

- Three `index.md` files were displaying recent activity backwards
  (`entries.slice(-15).reverse()` on a reverse-chronological log
  shows the *oldest* 15). All four `index.md` files now use
  `entries.slice(0, 15)`.
- All ~170 broken Obsidian block-id anchors under
  `domains/psychology/wiki/` rewritten from `[[file#^[HH:MM]]]`
  (which never resolved, because the raws use `**[HH:MM]**` not
  `^id`) to `[[file]] [HH:MM]`, matching the L2's own convention in
  `domains/psychology/AGENTS.md`.
- Workspace `engineering-decision-style` instance count reconciled
  between the pattern page (N=2-provisional), the
  2026-05-19 analysis prose, and the log entry.
- `decision-delay-from-skipped-stakeholder.instances_count` updated
  from `1` to `3` so the pattern no longer violates its own L2
  `instances_count ≥ len(sources)` lint rule; the arc-level
  "N=1 provisional" claim is preserved in the prose.
- `workspace/AGENTS.md` folder layout marks `raw/threads/` as
  on-demand (the directory doesn't ship on disk); stakeholder /
  team / project `team:` / `lead:` fields explicitly accept a plain
  string when no entity page is yet warranted (matching what the
  shipped example pages actually do).

### Added

- **AGENTS.md §3.4** — `cross-domain` tagging contract.
- **`densa` rule `DENSA-IO`** registered in `config.RULES`
  with stable ID + summary + anchor.
- **`densa --diff <base_ref>`** subcommand.
- **11 new regression tests** covering each of the fixes above
  (index exclusion, explicit-path fallback, inbox→raw rename,
  raw-to-raw rename, source-aware fallback, analysis source must
  resolve to raw, raw source clean path, BOM frontmatter, CRLF
  frontmatter, diff-mode catches AGENTS001, diff-mode passes clean
  range).

## [0.1.0] - 2026-05-21

### Added

- **L1 schema** ([`AGENTS.md`](AGENTS.md)) — universal contract for
  every domain: page-type enum, `sources` cardinality, red lines,
  routing rules, schema versioning, `last_validated` semantics.
- **Five canonical operations** under [`_system/prompts/`](_system/prompts/) —
  `ingest`, `query`, `lint`, `process-inbox`, `promote`.
- **Page templates** for every page type under
  [`_system/templates/`](_system/templates/), including
  domain-specialised variants and a Q&A template.
- **`densa` Python validator** ([`_system/densa/`](_system/densa/)) —
  pure-stdlib (~1k lines) schema + red-line enforcement; pre-commit
  hook under [`_system/hooks/`](_system/hooks/) and GitHub Action
  under [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
- **Three worked-example domains** under [`domains/`](domains/) covering
  light/medium/heavy schema density (`research-papers`, `workspace`,
  `psychology`).
- **Claude Code plugin** at [`integrations/claude-code/`](integrations/claude-code/) —
  thin slash-command shims wrapping all five operations.
