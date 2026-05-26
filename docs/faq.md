# FAQ

> Conceptual answers to questions that come up after your first few
> ingests: the red lines, how the wiki scales / drifts, the operation
> philosophy behind `outputs/` and `query`. Operational recipes
> (install, plugins, encryption) live in [`setup.md`](setup.md); a
> day-in-the-life narrative lives in [`../GUIDE.md`](../GUIDE.md).

## The red lines

### Why is `raw/` immutable?

Because the wiki's epistemic integrity depends on being able to walk
any claim back to a verifiable source. If raw is editable, the LLM's
own past synthesis errors can silently propagate into the evidence
base, and the wiki becomes a closed epistemic loop — it cites itself,
not the world. The pre-commit hook (AGENTS001) enforces this. The
only sanctioned exception is a transcription-correction sweep
documented per-L2 (see e.g. the psychology L2's "Known transcription
corrections" section).

### Why is `log.md` append-only and reverse-chronological?

Append-only because the log is the audit trail of every ingest / query
/ lint — rewriting would erase the LLM-vs-human collaboration history.
Reverse-chronological because you read top-down and the most recent
state is what matters. When position drift happens, the
`WIKI_ALLOW_LOG_REORDER=1` bypass permits a single-shot reorder sweep
— but the diff must be a pure permutation plus a maintenance audit
entry.

### Why don't we delete wiki pages?

Wikilinks propagate. Deleting `[[xyz]]` silently breaks every page that
referenced it; renaming is a cascade you must own consciously. The
deprecation pattern (`status: deprecated` + a `> Superseded by [[…]]`
redirect + remove from index) keeps the link graph intact while the
page becomes a gravestone pointing at its successor.

---

## Scale & drift

### How big can the wiki get before it stops scaling?

Empirically, `index.md` Dataview routing suffices to ~500 wiki pages.
Past that, two early-warning signals: any single Dataview block
exceeds ~50 rendered rows, or `index.md` rendering becomes noticeably
slow. Either fires → migrate to Obsidian Bases (`.base` files) or
layer Smart Connections on top. Until then Dataview is more
diff-friendly in git and the LLM operates on its source markdown more
naturally.

### How do I know when a claim has drifted?

`lint` will flag:

- pages whose `last_validated` is older than 180 days (`concept` /
  `entity` types — pages with no built-in raw anchor) — re-read the
  cited sources, bump the timestamp.
- citation chains that take more than 2 hops to reach a `raw/` file —
  claims that float without a recent evidence anchor.
- second-order pages (`concept` / `overview` / `synthesis`) whose
  latest cited summary is older than the L2's configured staleness
  threshold.
- contradictions where two pages make opposite claims about the same
  entity / concept.

Treat lint reports as work-in-progress dashboards, not pass/fail
gates. The goal is a *boring* lint report: each subsequent run mostly
says "no new findings since last lint", with the human-review queue
draining gradually.

---

## Operation philosophy

### Why does `outputs/` exist instead of `wiki/syntheses/`?

Lint reports and Q&A archives are *operation artifacts*, not compiled
knowledge. Three concrete problems with dropping them in
`wiki/syntheses/`:

- Reports accumulate as noise but
  [L1 §"Naming and linking conventions"](../AGENTS.md#4-naming-and-linking-conventions)
  forbids deleting wiki pages, so old reports can't be cleaned up
  cleanly.
- `type: synthesis` requires `sources: ≥ 2`; a lint report doesn't
  fit that contract.
- `query` would occasionally cite a lint report as if it were
  knowledge, polluting answers.

The fix: a separate top-level `outputs/` directory — in git for the
audit trail, but excluded from the wikilink graph and the wiki's
schema contracts. Reports point at wiki pages; wiki never points back.
When `outputs/` grows noisy, `git rm outputs/{lint,qa}/<old>.md`
removes it safely (no wiki page can link there, by design).

### Where do `query` answers go?

Substantive `query` answers are filed as `type: report` Q&A artifacts
under `outputs/qa/<YYYY-MM-DD>-<slug>.md` — alongside `outputs/lint/`
and `outputs/snapshots/`, not inside `wiki/`. Same reasoning as above.
If a particular answer turns out to be evergreen and worth
wikilink-graph membership, the path forward is `promote` (see
[`../GUIDE.md` §"The seams"](../GUIDE.md#the-seams-when-to-use-which-operation)
*"Q&A that recurs"*).
