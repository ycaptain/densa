# Shared style helper (embedded in every live-* block)

Not a standalone block — this is the canonical copy of the helper
that each `live-*` template embeds. If you improve it, update every
canned block in this folder in the same commit.

```js
// --- densa chart style helper (canonical copy: _system/templates/charts/) ---
const _css = getComputedStyle(document.body);
const C = (v) => _css.getPropertyValue(v).trim() || "#888";
const PALETTE = ["--color-blue","--color-purple","--color-green",
  "--color-orange","--color-cyan","--color-pink","--color-yellow","--color-red"].map(C);
const BASE_OPTS = {
  responsive: true,
  plugins: { legend: { labels: { color: C("--text-muted"), font: { family: _css.getPropertyValue("--font-text") } } } },
  scales: {
    x: { ticks: { color: C("--text-muted") }, grid: { color: C("--background-modifier-border") } },
    y: { ticks: { color: C("--text-muted") }, grid: { color: C("--background-modifier-border") } },
  },
};
const BAR_STYLE = { borderRadius: 6, borderSkipped: false, maxBarThickness: 28 };
// --- end helper ---
```
