---
type: log
scope: global
updated: 2026-05-25
compiled_against: 2
---

# Global Log

Append-only timeline of cross-domain events (see [`AGENTS.md`](AGENTS.md)
§6 for the append-only rule and §2.1 for entry format). Newest entries
go immediately below this preamble; older entries scroll down.

Entry format:

```
## [YYYY-MM-DD] <operation> | <one-line summary>
- Source: [[<path>]]
- Pages touched: [[…]], [[…]]
- One-line synthesis.
```

---

## [2026-05-25] maintenance | schema v2 (Karpathy vocab) + newcomer-friendliness sweep
- Bypass used: WIKI_ALLOW_CROSS_SCOPE=1 (single sweep touches `_system/**`, `domains/**`, `examples/**`, `docs/**`, root docs, `integrations/**`, `.github/**`).
- Schema v2 (BREAKING): 16 v1 page types collapsed to nine Karpathy-vocab types (`source`, `summary`, `entity`, `concept`, `comparison`, `overview`, `synthesis`, `open-question`, `report`); `_system/densa/schema.py` becomes the single Python source of truth; new checks AGENTS010 (schema-version-consistency), AGENTS011 (prompt-schema-sync), AGENTS012 (migration-history-hygiene); `densa migrate` subcommand + `migrate_02_karpathy_vocab.py` script (idempotent, three modes: in-place / archive / recover); `domains/psychology/` and `domains/workspace/` reorganised to `examples/showcases/`; `domains/research-papers/` (active default L2) ships on v2; v1 templates parked under `attic/templates-v1/`. Full transform: `CHANGELOG.md [Unreleased]`.
- Newcomer-friendliness sweep (clusters A-H of the internal newcomer-friendliness review plan): Quickstart single-sourced (4 docs no longer redrop the hooksPath three-step); 5-ops table thinned to 2 sources (AGENTS §2 + GUIDE NL-mapping); `operation-scopes.md` `lint:` row adds the missing `domains/*/wiki/**` auto-fix scope; Python authority unified on `schema.py` across 5 reference docs; `bootstrap.md` Step 1 references AGENTS.md §1.1 minimal onboarding; CHANGELOG `CHOOSING-A-DOMAIN.md` updated to current `docs/setup.md`; `densa init` lifted from Planned to Added with README Alternative section; `research-papers/` dual-identity warning surfaced in README + hello-world; `setup.md` opener reframed as "What this adds beyond Quickstart"; `GUIDE.md` top callout collapsed to one line; `repository-layout.md` removes `bootstrap` from op-prompts list (it lives at `docs/bootstrap.md`, not `_system/prompts/`).
- Validator self-check: `python -m densa --all` is green (191 files, 0 error, 0 warning).

## [2026-05-23] maintenance | rename project llm-wiki-starter → densa + carry-forward of 81f4e83's residue
- Bypass used: WIKI_ALLOW_CROSS_SCOPE=1 (single sweep touches `_system/**`, `.github/**`, `domains/**`, root docs, `integrations/**`, `pyproject.toml`).
- Why rename: the starter shipped under two names — repo `llm-wiki-starter`, validator `wikilint` — and neither covered the whole (schema + prompts + validator + integrations); `wikilint` in particular undersold the validator's scope (schema, write scopes, red lines — not just wikilinks). An in-flight candidate `lectern` collided with an existing unrelated PyPI package (`lectern` 0.35.0, "Literate Minecraft data packs"). `densa` is unclaimed on PyPI + GitHub and names the artefact itself — the dense, LLM-compiled distillation the wiki accumulates. Renames are mechanical: package directory `_system/wikilint/` → `_system/densa/`; CLI `wikilint` → `densa`; meta rule `WIKILINT-IO` → `DENSA-IO`. No back-compat alias kept — nothing was ever published under the old names.
- Concurrent carry-forward: this commit also lands the ~95 unstaged items from the post-`81f4e83` sweep that were on disk but not yet committed (new psychology session-3 retrofit raw + analyses, research-papers Kim 2025 paper raw + analyses + frameworks, `outputs/snapshots/`, `noxfile.py`, agent-inject / init / upgrade subcommands, new templates, new regression tests, doc cleanups). Folding them into the rename commit avoids a churny rebase against the directory move.
- Validator self-check: `python -m densa --all` is green (168 files, 0 error, 0 warning); pytest suite passes (329 tests).

## [2026-05-21] ingest(psychology) | session 3 retrofit (2026-04-30 — chair-work with the foreman)
- Source: [[2026-04-30-session-reyes]] (synthesised raw — fills the partial-coverage gap that the original ingest deliberately left open).
- Pages touched: [[2026-04-30-session-reyes-analysis]] (new), [[therapist-reyes]], [[avoidant-mother-contact]], [[somatic-grief-containment]], [[automaton-work-mode]], [[inner-protector-stoic]], [[father-grief-arc]], [[2026-05-14-six-week-retrospective]], [[2026-05-14-session-reyes-analysis]].
- The chair-work session is the IFS unblending hinge of the six-week arc; subsequent session-4 release is partly attributable to the protector's "by who?" challenge surfaced at [14:45] and Mark's direct address at [20:00].

## [2026-05-21] maintenance | cross-scope sweep — validator bugs, doc drift, example L2 cleanup
- Bypass used: WIKI_ALLOW_CROSS_SCOPE=1 (single sweep touches `_system/**`, `.github/**`, `domains/**`, root docs).
- Why: a fresh first-time-reader audit of the template surfaced ~30 items across 4 tiers (real validator bugs, doc drift, example-L2 inconsistencies, OSS polish). Fixing them piecemeal would have meant 5+ near-empty commits; bundling lets reviewers see the whole shape of the cleanup in one diff.
- Validator bugs fixed: AGENTS006 slot-index pollution (typo'd `[[concept]]` no longer resolves to `_system/templates/concept.md`); AGENTS001 inbox→raw rename false positive (process-inbox's canonical `git mv` is now permitted); AGENTS005 now requires the analysis source wikilink to resolve to a raw file (was wikilink-syntax-only); `frontmatter.parse_stdlib` no longer silently loses BOM-prefixed / CRLF-terminated frontmatter.
- New `wikilint --diff <base_ref>` mode so CI can enforce the staged rules over PR ranges (closes the `git commit --no-verify` bypass).
- Doc drift: reconciled "three vs five example L2s" across README / EXAMPLE-DOMAINS / bootstrap-prompt; added `process-inbox` to the MANUAL §0 cheat sheet; fixed L2 opener page-type counts in research-papers + workspace; formalised `cross-domain` tag in AGENTS.md §3.4; clarified `setup_encryption.sh` ships with no default paths.
- Example L2 cleanup: 3 `index.md` files fixed the reverse-chronological slice bug (`.slice(-15).reverse()` → `.slice(0, 15)`); ~170 broken Obsidian block-id anchors under `domains/psychology/wiki/` rewritten to L2-canonical `[[file]] [HH:MM]` form; engineering-decision-style instance count reconciled across pattern + analysis + log; decision-delay-from-skipped-stakeholder `instances_count` now satisfies its own L2 lint rule; workspace folder layout marks `raw/threads/` as on-demand; stakeholder / team / project link-fields explicitly accept plain strings.
- 11 new regression tests pin every Tier A fix; full suite passes (239 tests); `wikilint --all` and `wikilint --diff HEAD^` both green.
- See CHANGELOG.md `[Unreleased] § Fixed (post-0.1.0 sweep)` for the full enumerated list.

## [2026-05-21] maintenance | workspace example expanded — domain ingest sub-prompt + 2 new decision arcs + positive pattern + cross-decision synthesis
- Bypass used: WIKI_ALLOW_CROSS_SCOPE=1 (single change set touches `_system/prompts/domains/` and `domains/workspace/**`).
- New: `_system/prompts/domains/workspace-meeting-analysis.md` (v1
  workspace-specific ingest sub-prompt — closes the prompt↔ingest
  correspondence gap for workspace).
- New workspace raws + wiki pages: [[2026-05-13-meeting-api-style-decision]],
  [[2026-05-19-meeting-vector-db-selection]] + 2 analyses + 4
  stakeholders + 2 teams + 2 projects + 1 positive pattern
  ([[engineering-decision-style]]) + 1 cross-decision synthesis
  ([[engineering-decisions-retrospective-may-2026]]).
- Existing 3 Q2-arc analyses retrofitted with the four
  readability elements so worked examples match the new prompt's
  output contract; bidirectional cross-links added.
- Why: the prior workspace worked example demonstrated only the
  negative-pattern path ([[decision-delay-from-skipped-stakeholder]]
  with N=1). Interns / new engineers needed (a) a positive
  pattern to recognise healthy decision-making, (b) a
  cross-project synthesis to see how decisions compound, and (c)
  a domain-specific ingest sub-prompt mirroring the structures
  research-papers and psychology already had. See
  `domains/workspace/log.md` for per-ingest detail.
