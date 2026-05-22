---
type: log
scope: global
updated: 2026-05-21
compiled_against: 1
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
