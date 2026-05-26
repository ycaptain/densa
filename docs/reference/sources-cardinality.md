# `sources` cardinality by page type

Reference companion to
[`AGENTS.md` §"Frontmatter schema"](../../AGENTS.md#3-frontmatter-schema-universal).
The `sources` frontmatter field is universal across wiki pages; what
counts as a "source" — and how many are required — depends on the
page type. Treat this as a **strict schema contract**; AGENTS005
enforces the most load-bearing row (`analysis` = exactly 1 raw).

## The table

| `type` | `sources` points to | Cardinality |
| --- | --- | --- |
| `source` / `session` | n/a (the file *is* the source) | empty |
| `analysis` | the **one** raw file in `raw/` that this analyses | exactly 1 |
| `synthesis` | wiki pages and/or raw files this synthesis weaves together | ≥ 2 |
| `pattern` / `theme` | wiki pages (analyses, sessions) and/or raw files where the pattern/theme manifests | ≥ 2 |
| `entity` | wiki pages and/or raw files where the entity appears | ≥ 1 |
| `concept` / `framework` | raw files (papers, articles) and/or canonical wiki pages | ≥ 0 (may be empty for evergreen concepts; ≥ 1 once cited) |
| `protocol` / `experiment` | raw articles + linked experiments / metric files | ≥ 1 |
| `project` / `stakeholder` / `decision` | raw meeting/doc files relevant to the project; for stakeholders also their `Appearances` raw refs | project ≥ 0; stakeholder ≥ 1; decision ≥ 1 (the meeting/thread that produced it) |
| `correction` (recurring failure-mode tracking — see `_system/templates/correction.md`) | analyses / raw files where the failure mode was observed (≥1, since first observation = N=1) | ≥ 1 |
| `question` | wiki pages and/or raw files that bear on the question | ≥ 0 (may be empty when first asked; populated as evidence accrues) |
| `fleeting` | n/a — short-lived note, no provenance required | empty |
| `report` (operation artifact under `outputs/`) | n/a — may reference wiki pages inline via `[[wikilink]]` but the wikilink resolver ignores the report itself | 0..* (empty allowed) |

## Two implications

1. **Wiki-to-wiki citations are first-class** for second-order pages
   (`pattern`, `theme`, `synthesis`, `entity`). They are *not* a
   violation of the "every claim traces to ≥1 source" rule (see
   [`AGENTS.md` §"Red lines"](../../AGENTS.md#6-red-lines-non-negotiable))
   — those second-order pages cite the analyses they generalise, and
   each analysis cites the raw file directly. The chain still
   terminates at raw.

2. **`analysis.sources` MUST contain exactly one raw wikilink**, never
   a wiki page. If you find yourself wanting to cite a second raw
   file or a prior analysis, you are writing a `synthesis`, not an
   `analysis` — change the `type` field and move the file under
   `wiki/syntheses/`. AGENTS005 enforces this mechanically.
