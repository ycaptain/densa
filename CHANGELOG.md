# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/) for
the L1 schema version recorded in [`AGENTS.md`](AGENTS.md) frontmatter
(`schema_version`).

## [Unreleased]

Tracked but not yet shipped — file an issue or PR against any of these:

### Planned

- First-`ingest` end-to-end walkthrough in `docs/EXAMPLES.md` (mirrors
  the existing `promote` walkthrough), using a shipped real-paper raw.
- `how-to-read-this-domain.md` synthesis page for `workspace` (matching
  the `research-papers` and `psychology` pattern).
- Structured "promotion candidates" output from `lint` (currently
  surfaced only as free-text in the report).

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
- **`wikilint` Python validator** ([`_system/wikilint/`](_system/wikilint/)) —
  pure-stdlib (~1k lines) schema + red-line enforcement; pre-commit
  hook under [`_system/hooks/`](_system/hooks/) and GitHub Action
  under [`.github/workflows/validate.yml`](.github/workflows/validate.yml).
- **Three worked-example domains** under [`domains/`](domains/) covering
  light/medium/heavy schema density (`research-papers`, `workspace`,
  `psychology`).
- **Claude Code plugin** at [`integrations/claude-code/`](integrations/claude-code/) —
  thin slash-command shims wrapping all five operations.
