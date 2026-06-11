# visualize — full procedure

Read [`visualize.md`](visualize.md) (header) first. This body is the
execution manual.

## 0. Inputs

One of:

- `visualize <path>` — a single target page.
- `visualize --domain <X>` — sweep the domain's wiki against the
  trigger matrix.
- Carry-over queue — `## [date] ingest | …` log entries whose
  `Chart carry-over:` block lists deferred chart work (written by
  `ingest` Stage V when it chose to defer).

## 1. Pass 1 — Plan

1. Read each candidate page in full (prose + frontmatter + existing
   chart blocks). Do **not** read `raw/**` (anchor verification is
   the only exception, and it never adds chart content).
2. Evaluate the **trigger matrix** (L2 "可视化约定" wins; fallback
   below). For each page emit one of: *no chart* (default), *new
   chart*, *refresh existing* (data drifted / `图截至` stale), or
   *delete* (shape test now fails).
3. Output the chart plan as a table — host page, chart type, trigger
   condition cited verbatim, insert position (after which heading /
   table), collapsed or hero — and stop for human approval. A plan
   in which most pages get zero charts is normal and usually correct.

### Fallback trigger matrix (L1 view; L2 overrides win)

| Page type / page                       | Chart                                            | Trigger                                              | Position & fold |
|----------------------------------------|--------------------------------------------------|------------------------------------------------------|-----------------|
| summary (psychology)                   | Mermaid `timeline` (thread arc)                  | thread has ≥3 prior sessions (existing L2 rule)      | human layer arc section, collapsed |
| summary (psychology)                   | Mermaid `flowchart LR` behaviour chain           | a behaviour-chain analysis ran this session          | machine layer, in that sub-block, collapsed |
| summary (psychology)                   | Mermaid `flowchart TD` mechanism hypothesis      | ≥2 mutually-feeding maintenance loops                | machine layer, end of mechanism section, collapsed |
| debrief                                | single-mechanism loop diagram (≤6 nodes)         | mechanism is a closed loop AND 3 sentences can't carry it; ≤1 per debrief | inside that mechanism block, collapsed |
| overview `kind: formulation`           | mechanism flowchart (hero) + Chronos awareness axis | standing; refreshed on monthly formulation refresh | hero expanded; axis collapsed. Crisis card / medication tables NEVER charted |
| overview `kind: theme`                 | stage-arc timeline (Mermaid or Chronos)          | arc has ≥3 sessions AND named stages                 | after stage narrative, hero expanded (≤1 hero per page) |
| concept `kind: pattern`                | instance-accumulation chart                      | Instances ≥5                                         | after Instances, collapsed |
| concept `kind: protocol` (medication)  | —                                                | never (safety)                                       | — |
| open-question                          | evidence-accumulation timeline                   | evidence ≥3 spanning ≥2 months                       | machine layer, after evidence table, collapsed |
| comparison                             | `quadrantChart` or grouped bar                   | ≥3 quantified dimensions (qualitative stays a table) | after the table (table stays canonical), collapsed |
| entity (people)                        | interaction timeline (Chronos)                   | Appearances ≥5                                       | machine layer, collapsed |
| project overview                       | Mermaid `gantt`                                  | ≥3 dated milestones                                  | collapsed |
| domain `overview.md` / global `index.md` | live data panel (dataviewjs, whitelist)        | install once, auto-updates                           | tail "数据面板" section, collapsed |

Career synthesis pages (profile, skill-gap-map, direction-map) and
their triggers are defined in `domains/career/AGENTS.md`; psychology
specifics in `domains/psychology/AGENTS.md`.

## 2. Pass 2 — Write (after human approval)

For each approved item:

1. Build the block from a canned template under
   `_system/templates/charts/` when one fits; otherwise follow the
   block formats below.
2. Wrap in the chart callout (unless hero):

   ```markdown
   > [!chart]- 图:<one line — what question this chart answers>
   > 这张图回答:<same line, reader-facing phrasing>
   >
   > ```mermaid
   > …
   > ```
   >
   > 图截至: <YYYY-MM-DD> · 数据源: [[<host-or-source-page>]]
   ```

   Hero charts (≤1 per page, only where the matrix says "hero") sit
   unfolded directly in the section, still followed by the `图截至`
   line. Live dataviewjs charts omit `图截至` (they self-update) but
   keep the intro line.
3. Run the **mini-critique** on every block:
   - **(z1) Compiled-ness** — every node / data point / edge has a
     supporting statement in the host page. Anything sourced from
     memory of the raw → remove or fix the page first.
   - **(z2) Shape test** — cover the chart: does the reader lose a
     *shape* (loop, fork, density, position)? If the chart merely
     restates an adjacent table/list → delete it.
   - **(z3) Safety** — crisis / SI / medication content present →
     delete immediately. (Mechanism names are fine; drug names,
     doses, SI phrasing are not.)
   - **(z4) Conventions** — callout + intro line + `图截至` line;
     node label ≤12 chars (use `<br/>` to wrap); flowchart ≤8 nodes
     horizontally (else `TD` or split); no hard-coded colors; Mermaid
     handDrawn header present; ≤1 hero per page; live charts only on
     whitelisted hubs.
4. Edit mechanics: write via Bash/python script (PostToolUse
   formatter wraps wikilinks); after editing run
   `awk '/\[\[[^]]*$/' <file>` to confirm no split wikilinks, and
   `PYTHONPATH=_system python3 -m densa --all` before committing.
5. Prepend the log entry (newest first) to `domains/<X>/log.md`:

   ```markdown
   ## [YYYY-MM-DD] visualize | <scope>
   - Wrote:
     - domains/<X>/wiki/<folder>/<page>.md (chart: <type> — <what it answers>)
   - Skipped (trigger not met): <page> — <condition>
   - One-line synthesis.
   ```

   Commit prefix: `visualize(<X>): <YYYY-MM-DD> <scope>`.

## 3. Block formats

### Mermaid (structure: causal loops, layered DAGs, timelines, quadrants)

Every Mermaid block opens with the handDrawn header:

```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
flowchart TD
    …
```

- Layered causal DAG for "multiple factors → mechanisms → current
  state": one `subgraph` per layer, arrows flow down, feedback edges
  `<-->`. The loops are the value — make them visible.
- Complex flowcharts (≥6 nodes or crossing edges): first line
  `%% elk %%` (Mermaid ELK Renderer plugin).
- Timelines: `timeline` for coarse arcs; Chronos for dated, dense,
  zoomable ones.

### Chronos (dated arcs)

````markdown
```chronos
- [2026-03-12] 首次命名该机制
- [2026-04-02~2026-04-30] 阶段:塌方期
- [2026-05-27] 镜像场
```
````

### dataviewjs + Charts (live data panels — hub whitelist only)

Use the canned blocks in `_system/templates/charts/` (they embed the
shared style helper: palette from CSS variables via
`getComputedStyle`, rounded bars, gradients). Install = copy the
block, adjust the marked parameters (folder path, title). Never
hand-write a divergent style.

## 4. Aesthetic conventions (summary)

- handDrawn look on all Mermaid; theme follows Obsidian (no theme
  override in `%%{init}%%`).
- Colors only via CSS variables / computed styles, never hex.
- One hero chart per page max; everything else default-collapsed.
- Callout title is a *question answered*, not a chart-type name.
- `.obsidian/snippets/densa-charts.css` owns container sizing, grid
  panels, and print/PDF expansion — don't inline-style.

## 5. Quality bar

A visualize commit passes when: every block passed (z1)–(z4); the
plan and the writes match 1:1; the log entry lists writes *and*
trigger-not-met skips; `densa --all` is clean; no split wikilinks.
