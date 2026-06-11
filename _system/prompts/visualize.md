# Prompt: visualize

Use this prompt when the human says `visualize <path>` or
`visualize --domain <X>` (or when consuming the Stage V carry-over
queue left by a prior `ingest`). Canonical procedure for
[`/AGENTS.md` §"visualize"](../../AGENTS.md#26-visualize-path---domain-x-charts-on-existing-pages).
It embeds or refreshes **chart blocks** (Mermaid / dataviewjs) on
existing wiki pages whose trigger conditions pass. It never authors
new claims: charts are compiled from the host page's own prose and
frontmatter.

## What this command will write (schema contract)

| Path                                  | When                                                    | Why                                                                                  |
|---------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------------|
| `domains/<X>/wiki/<folder>/<slug>.md` | chart blocks only, on pages whose trigger conditions pass | embed/refresh a chart block (+ data-as-of line) compiled from the host page's own prose and frontmatter |
| `domains/<X>/log.md`                  | always                                                  | audit trail (newest first per AGENTS002)                                             |
| `log.md`                              | only when cross-domain                                  | global timeline (newest first)                                                       |

> This table mirrors `densa.schema.OPERATIONS['visualize'].writes`.
> AGENTS011 warns on drift.

## In one paragraph

Run in two passes with a human gate. **Pass 1 — Plan**: evaluate the
per-domain trigger matrix (L2 AGENTS.md "可视化约定" section, fallback
matrix in the body) against the target pages and emit a chart plan —
host page, chart type, trigger condition cited, insert position. Most
pages correctly get **zero** charts. **Pass 2 — Write**: after human
approval, embed exactly the approved blocks, run the mini-critique
(z1–z4), and prepend the log entry. Every static chart carries a
`图截至: <date> · 数据源: [[page]]` line; `lint` flags staleness.

## Non-negotiables

- **Compiled, never authored** — every node / data point / edge in a
  chart must already be stated in the host page's prose or
  frontmatter. A relation that exists only in `raw/` is a
  completeness defect of the *page*: fix the page first (normal edit
  path, separate commit), then chart it.
- **Shape test** — a chart must express a shape prose/tables cannot
  carry (feedback loop, branching, time density, quadrant position).
  A chart that restates an adjacent table is noise: omit or delete.
- **Safety red line** — crisis-card, SI-grade, and medication
  material (drug names / doses / start-stop) is never charted.
- **Trigger conditions are gates, not suggestions** — when in doubt,
  don't draw. A missed chart is recoverable via `lint` nomination; a
  wrong chart is noise.
- **Live-chart whitelist** — `dataviewjs` chart blocks only on hub
  pages: `index.md`, `domains/*/wiki/overview.md`,
  career `profile.md` / `skill-gap-map.md`, psychology
  `current-state.md`. Everything else uses static Mermaid/Chronos.
- **No silent additions** — Pass 2 writes exactly the Pass-1-approved
  plan, nothing more.

## Before you execute

Load **[`visualize.body.md`](visualize.body.md)** for the full
procedure: the domain trigger matrices, chart-type selection guide,
block formats (Mermaid handDrawn header, dataviewjs + renderChart,
Chronos DSL), the mini-critique (z1)–(z4), aesthetic conventions, the
carry-over queue contract, and the log-entry shape. Canned blocks
live in `_system/templates/charts/`.
