# live-skill-proof — skills by proof_level (career profile)

> Install on: `domains/career/wiki/syntheses/profile.md`, after the
> skills narrative. Intro line: 这张图回答:我的技能证明强度分布如何?

````markdown
```dataviewjs
// --- densa chart style helper (canonical copy: _system/templates/charts/) ---
const _css = getComputedStyle(document.body);
const C = (v) => _css.getPropertyValue(v).trim() || "#888";
const PALETTE = ["--color-blue","--color-purple","--color-green",
  "--color-orange","--color-cyan","--color-pink","--color-yellow","--color-red"].map(C);
const BASE_OPTS = {
  responsive: true, indexAxis: "y",
  plugins: { legend: { labels: { color: C("--text-muted") } } },
  scales: {
    x: { stacked: true, ticks: { color: C("--text-muted"), precision: 0 }, grid: { color: C("--background-modifier-border") } },
    y: { stacked: true, ticks: { color: C("--text-muted") }, grid: { display: false } },
  },
};
const BAR_STYLE = { borderRadius: 6, borderSkipped: false, maxBarThickness: 22 };
// --- end helper ---

const FOLDER = '"domains/career/wiki/concepts"'; // PARAM
const LEVELS = ["claimed", "in-progress", "resume-ready", "deep"];
const skills = dv.pages(FOLDER).where(p => p.skill_id && p.proof_level);
const byLevel = Object.fromEntries(LEVELS.map(l => [l, 0]));
for (const s of skills) if (byLevel[s.proof_level] != null) byLevel[s.proof_level]++;
window.renderChart({
  type: "bar",
  data: { labels: ["技能数"],
    datasets: LEVELS.map((l, i) => ({ label: l, data: [byLevel[l]],
      backgroundColor: PALETTE[i] + "CC", ...BAR_STYLE })) },
  options: BASE_OPTS,
}, this.container);
```
````
