# live-pipeline-freshness — company signal age (career overview)

> Install on: `domains/career/wiki/overview.md` 数据面板.
> Intro line: 这张图回答:哪些公司管线的信号已经陈旧?

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
    x: { ticks: { color: C("--text-muted") }, grid: { color: C("--background-modifier-border") }, title: { display: true, text: "天(自最后信号)", color: C("--text-muted") } },
    y: { ticks: { color: C("--text-muted") }, grid: { display: false } },
  },
};
const BAR_STYLE = { borderRadius: 6, borderSkipped: false, maxBarThickness: 18 };
// --- end helper ---

const FOLDER = '"domains/career/wiki/entities"'; // PARAM
const today = dv.date("today");
const rows = dv.pages(FOLDER)
  .where(p => p.kind === "company" && p.last_signal)
  .map(p => ({ name: p.file.name, days: Math.round(today.diff(dv.date(p.last_signal), "days").days) }))
  .array().sort((a, b) => b.days - a.days).slice(0, 15);
window.renderChart({
  type: "bar",
  data: { labels: rows.map(r => r.name),
    datasets: [{ data: rows.map(r => r.days),
      backgroundColor: rows.map(r => r.days > 30 ? C("--color-red") + "AA" : PALETTE[2] + "CC"), ...BAR_STYLE }] },
  options: BASE_OPTS,
}, this.container);
```
````
