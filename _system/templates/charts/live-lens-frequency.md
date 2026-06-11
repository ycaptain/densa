# live-lens-frequency — analysis_lens usage (psychology overview)

> Install on: `domains/psychology/wiki/overview.md` 数据面板.
> Intro line: 这张图回答:最近的分析都在用哪些镜头?

````markdown
```dataviewjs
// --- densa chart style helper (canonical copy: _system/templates/charts/) ---
const _css = getComputedStyle(document.body);
const C = (v) => _css.getPropertyValue(v).trim() || "#888";
const PALETTE = ["--color-blue","--color-purple","--color-green",
  "--color-orange","--color-cyan","--color-pink","--color-yellow","--color-red"].map(C);
const BASE_OPTS = {
  responsive: true, indexAxis: "y",
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: C("--text-muted"), precision: 0 }, grid: { color: C("--background-modifier-border") } },
    y: { ticks: { color: C("--text-muted") }, grid: { display: false } },
  },
};
const BAR_STYLE = { borderRadius: 6, borderSkipped: false, maxBarThickness: 22 };
// --- end helper ---

const FOLDER = '"domains/psychology/wiki/summaries"'; // PARAM
const counts = {};
for (const p of dv.pages(FOLDER)) {
  const lenses = Array.isArray(p.analysis_lens) ? p.analysis_lens
    : p.analysis_lens ? [p.analysis_lens] : [];
  for (const l of lenses) counts[String(l)] = (counts[String(l)] ?? 0) + 1;
}
const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 12);
window.renderChart({
  type: "bar",
  data: { labels: entries.map(e => e[0]),
    datasets: [{ data: entries.map(e => e[1]),
      backgroundColor: entries.map((_, i) => PALETTE[i % PALETTE.length] + "CC"), ...BAR_STYLE }] },
  options: BASE_OPTS,
}, this.container);
```
````
