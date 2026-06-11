# live-vault-rhythm — ingests per domain per month (global index)

> Install on: `index.md` tail. Intro line: 这张图回答:整个 vault 的摄入节律与重心在哪?

````markdown
```dataviewjs
// --- densa chart style helper (canonical copy: _system/templates/charts/) ---
const _css = getComputedStyle(document.body);
const C = (v) => _css.getPropertyValue(v).trim() || "#888";
const PALETTE = ["--color-blue","--color-purple","--color-green",
  "--color-orange","--color-cyan","--color-pink","--color-yellow","--color-red"].map(C);
const BASE_OPTS = {
  responsive: true,
  plugins: { legend: { labels: { color: C("--text-muted") } } },
  scales: {
    x: { stacked: true, ticks: { color: C("--text-muted") }, grid: { display: false } },
    y: { stacked: true, ticks: { color: C("--text-muted"), precision: 0 }, grid: { color: C("--background-modifier-border") } },
  },
};
const BAR_STYLE = { borderRadius: 4, borderSkipped: false, maxBarThickness: 28 };
// --- end helper ---

const DOMAINS = ["psychology", "career", "self-optim", "people", "projects"]; // PARAM
const months = new Set(); const data = {};
for (const d of DOMAINS) {
  data[d] = {};
  for (const p of dv.pages(`"domains/${d}/wiki/summaries"`)) {
    const m = String(p.file.name).match(/^(\d{4}-\d{2})/);
    const key = m ? m[1] : p.file.ctime.toFormat("yyyy-MM");
    months.add(key); data[d][key] = (data[d][key] ?? 0) + 1;
  }
}
const labels = [...months].sort();
window.renderChart({
  type: "bar",
  data: { labels,
    datasets: DOMAINS.map((d, i) => ({ label: d,
      data: labels.map(l => data[d][l] ?? 0),
      backgroundColor: PALETTE[i] + "CC", ...BAR_STYLE })) },
  options: BASE_OPTS,
}, this.container);
```
````
