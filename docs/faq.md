# FAQ

> Conceptual answers to questions that come up after your first few
> ingests: the red lines, how the wiki scales / drifts, the operation
> philosophy behind `outputs/` and `query`. Operational recipes
> (install, plugins, encryption) live in [`setup.md`](setup.md); a
> day-in-the-life narrative lives in [`../GUIDE.md`](../GUIDE.md).

## First-3-minute questions

If you arrived from the README and haven't ingested anything yet,
these three answers usually unblock the "should I bother" decision.

### Is this project alive?

Yes — see [`../CHANGELOG.md`](../CHANGELOG.md) for the most recent
release marker and the [`../ROADMAP.md`](../ROADMAP.md) for what's
queued next. Activity signals:

- [CI badge](https://github.com/ycaptain/densa/actions/workflows/ci.yml) in the README is green.
- 210+ validator-tracked files, 296+ pytest cases, the four-tool
  parity command (`densa --all` / `pytest` / `ruff` / `mypy`) is
  enforced in CI on every PR.
- The v2 (Karpathy vocab) schema bump landed 2026-05; the next
  watch-list items (plugin marketplace listings,
  `examples/showcases/` v2 migration) are tracked in
  [`../ROADMAP.md`](../ROADMAP.md).

Solo maintainer project (`ycaptain`); contributions welcome via
[GitHub Discussions](https://github.com/ycaptain/densa/discussions)
and PRs against the
[upstream repo](https://github.com/ycaptain/densa).

### Fork-and-self-host vs upstream contribution — which path is the default?

**Fork-and-self-host is the default.** Densa is a personal-knowledge
substrate; you fork once, then your `domains/<X>/` is yours forever
(upstream never touches that namespace). The
[`../README.md` §Quickstart](../README.md#quickstart) flow assumes
you fork. No `pip install` is required for self-use — the pre-commit
hook is pure stdlib.

Upstream PR contributions (against the schema, validator, prompts,
templates) are the secondary path and live under
[`../CONTRIBUTING.md`](../CONTRIBUTING.md). The fork-self-use vs
upstream-contributor split is the first callout on CONTRIBUTING so
self-users don't accidentally read 200 lines of dev-extras
instructions they don't need.

### How is Densa different from RAG and from Obsidian-AI plugins?

Three architectural families currently call themselves "AI knowledge
bases"; Densa sits in family C:

- **A · Retrieval-time (RAG-classic)** — [RAGFlow](https://github.com/infiniflow/ragflow),
  LlamaIndex / LangChain vector stacks. Documents → chunks →
  retrieve at query time. Fast onboarding; never structurally
  consolidates; the hallucination surface is the answer text on
  *every* query.
- **B · In-place assist** — [Smart Composer](https://github.com/glowingjade/obsidian-smart-composer),
  [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections),
  Notion AI. Cursor-flavoured `@`-mention UX; the AI is a typing
  partner that edits your existing notes. Co-installable with
  Densa; doesn't try to compile a wiki.
- **C · Compile-time (wiki-compiler)** — Densa, Karpathy's pattern,
  [Tolaria](https://github.com/refactoringhq/tolaria),
  [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki),
  [olw](https://github.com/kytmanov/obsidian-llm-wiki-local). Raw
  sources → LLM compiles structured prose once → query the
  structured prose. Slower onboarding; structure compounds; the
  hallucination surface is a write-time event under human review.

Densa's specific position within family C — MIT + stdlib-only Python
validator, L2 per-domain schema layering, public AGENTS001–AGENTS012
rule registry, `.legacy/` schema-migration snapshot — is sedimented
by a 2026-05 review of seven adjacent OSS projects at the README +
architecture-docs level
([`../README.md` §"Where this sits in the ecosystem"](../README.md#where-this-sits-in-the-ecosystem)
has the comparison table; maintainer-only study files live under
[`./maintainers/prior-art/`](maintainers/prior-art/)).

---

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
