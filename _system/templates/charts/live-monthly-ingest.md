# live-monthly-ingest — summaries per month (domain overview)

> Install on: `domains/<X>/wiki/overview.md`, tail `## 数据面板`
> section, inside a `[!chart]-` callout. Intro line: 这张图回答:这个域的摄入节律如何?

````markdown
```dataviewjs
// --- densa chart style helper (canonical copy: _system/templates/charts/) ---
const _css = getComputedStyle(document.body);
const C = (v) => _css.getPropertyValue(v).trim() || "#888";
const PALETTE = ["--color-blue","--color-purple","--color-green",
  "--color-orange","--color-cyan","--color-pink","--color-yellow","--color-red"].map(C);
const BASE_OPTS = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: C("--text-muted") }, grid: { color: C("--background-modifier-border") } },
    y: { ticks: { color: C("--text-muted"), precision: 0 }, grid: { color: C("--background-modifier-border") } },
  },
};
const BAR_STYLE = { borderRadius: 6, borderSkipped: false, maxBarThickness: 28 };
// --- end helper ---

const FOLDER = '"domains/psychology/wiki/summaries"'; // PARAM: domain summaries folder
const pages = dv.pages(FOLDER);
const byMonth = {};
for (const p of pages) {
  const m = String(p.file.name).match(/^(\d{4}-\d{2})/);
  const key = m ? m[1] : p.file.ctime.toFormat("yyyy-MM");
  byMonth[key] = (byMonth[key] ?? 0) + 1;
}
const labels = Object.keys(byMonth).sort();
window.renderChart({
  type: "bar",
  data: { labels,
    datasets: [{ data: labels.map(l => byMonth[l]),
      backgroundColor: PALETTE[0] + "CC", ...BAR_STYLE }] },
  options: BASE_OPTS,
}, this.container);
```
````
