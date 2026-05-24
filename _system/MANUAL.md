---
type: manual
scope: vault
updated: 2026-05-23
compiled_against: 1
---

# Densa — User Manual

> A second brain built on Andrej Karpathy's `llm-wiki` pattern,
> instantiated for an LLM agent (Cursor / Claude Code / Codex / Cline)
> operating over an Obsidian vault.

This file is **explanatory** — what a week of using the wiki actually
feels like, where the operations seam together, and the questions
that come up after your first few ingests. The **normative** contract
lives in [`/AGENTS.md`](../AGENTS.md) (L1) and each
`domains/<X>/AGENTS.md` (L2). When MANUAL and AGENTS disagree, AGENTS
wins; schema-shaped tables here are mirrors for human reading, not the
source of truth.

### The 60-second mental model (for first-time readers)

If you've never seen an "LLM wiki" before, here's the whole thing in
five sentences:

1. You drop sources (papers, transcripts, journal entries) into a
   `raw/` folder. **You never edit them again.**
2. An LLM agent inside your IDE reads each source and *compiles* it
   into structured markdown pages under `wiki/`. Each page cites the
   raw it came from.
3. When you ask a question, the agent reads the **wiki**, not the
   original raw — so it gets faster and more accurate as the wiki
   compounds, not slower like a RAG haystack.
4. The wiki's shape (what page types exist, what frontmatter each
   needs, which folders are immutable) is governed by a markdown
   file called `AGENTS.md`. A small Python validator enforces it on
   every commit.
5. The five verbs you ever type at the agent are `ingest`, `query`,
   `lint`, `process-inbox`, `promote`. That's it.

If you're brand-new, the right reading order is:
**README → this file → first ingest**. README pitches the architecture;
this file gets you fluent in a day of operating it.

---

## 🃏 Cheat sheet

The only verbs you ever type. Each links to its canonical procedure.

| Op | Command | Writes to | Procedure |
| -- | ------- | --------- | --------- |
| 📥 ingest        | `ingest <path>`             | `wiki/analyses/` + 3–15 wiki nodes (tier per L2 density) + logs        | [`prompts/ingest.md`](prompts/ingest.md) |
| 🔍 query         | `query <question>`          | read-only by default; optional `outputs/qa/<date>-<slug>.md`           | [`prompts/query.md`](prompts/query.md) |
| 🩺 lint          | `lint [--domain <X>]`       | `outputs/lint/<date>.md` + `outputs/snapshots/index-snapshot.md`       | [`prompts/lint.md`](prompts/lint.md) |
| 📨 process-inbox | `process-inbox`             | `git mv inbox/* → domains/<X>/raw/<bucket>/`; logs (no wiki edits)     | [`prompts/process-inbox.md`](prompts/process-inbox.md) |
| ⬆️ promote        | `promote outputs/qa/<file>` | `git mv` Q&A → `domains/<X>/wiki/<type>/<slug>.md`; logs               | [`prompts/promote.md`](prompts/promote.md) |

The **ingest tier ranges** are: light L2 (e.g. one paper) ≈ 3–6 pages;
medium (one meeting + decisions) ≈ 5–10 pages; heavy (one therapy
session) ≈ 8–15 pages. See [`AGENTS.md`](../AGENTS.md) §2.1 step 3.

The **page-type matrix** (which folder, what `sources` cardinality)
lives in [`AGENTS.md` §3.1](../AGENTS.md). The **red lines** (what no
operation may do) and their machine-enforced IDs (AGENTS001–009) live
in [`AGENTS.md` §6 + §6.1](../AGENTS.md). Pin those two anchors — every
other "is this allowed?" question routes through them.

---

## 🧠 Mental model

### One sentence

> **Wiki is the codebase. Obsidian is the IDE. The LLM is the
> programmer.** You select sources, ask questions, and review. Every
> other keystroke happens as incremental edits the LLM applies to the
> wiki.

### Three semantic layers

```
+-------------------------------------------------------+
|  AGENTS.md  <- rules (schema, operations, red lines)  |
+-------------------------------------------------------+
|  wiki/      <- hypotheses (LLM-owned, rewritten freely)|
+-------------------------------------------------------+
|  raw/       <- evidence (immutable, append-only)      |
+-------------------------------------------------------+
```

- **`raw/` is fact.** Clipped articles, transcribed sessions, recorded
  meetings. The LLM never edits them. Their purpose is to let you walk
  any wiki claim back to its source three years from now.
- **`wiki/` is the current best model.** Rewritten repeatedly.
  Compresses information in `raw/` into queryable, structured prose.
- **`AGENTS.md` is the contract.** It tells the LLM which material
  goes into which bucket, which pages each `ingest` should touch, and
  what `lint` should check. Editing AGENTS.md = editing the language
  the LLM and you share.

### Why this is not RAG

| Dimension     | RAG                                    | LLM Wiki (this design)                         |
| ------------- | -------------------------------------- | ---------------------------------------------- |
| At query time | retrieve raw chunks → stitch an answer | read the already-compiled wiki → answer        |
| Compounding   | none — every query starts from zero    | monotonic — every ingest densifies wiki        |
| Backlinks     | implicit (vector similarity)           | explicit (`sources:` frontmatter, enforced)    |
| Best scale    | millions of chunks, low query rate     | hundreds of sources, high synthesis frequency  |

Past ~300 pages and the `index.md` Dataview routing starts to miss,
layer Smart Connections (embedding search) on top as fallback. Until
then you don't need it.

---

## 📅 A day in the life

### Monday morning — you ingest a meeting transcript

You finish a 90-minute Q2-planning meeting. The Otter export lands in
`domains/workspace/raw/meetings/2026-04-08-meeting-q2-planning.md`.
You open Cursor and type:

> *ingest `domains/workspace/raw/meetings/2026-04-08-meeting-q2-planning.md`*

The agent reads the full transcript, then drafts:

```
I'll touch 6 pages (~80 lines diff):
- create wiki/analyses/2026-04-08-meeting-q2-planning-analysis.md
- update wiki/projects/q2-platform-migration.md  (status, risks)
- create wiki/decisions/microservices-split.md   (ADR draft)
- update wiki/entities/stakeholder-alex-cs.md    (+1 appearance)
- update wiki/entities/team-platform.md          (+1 appearance)
- prepend log.md + domains/workspace/log.md      (ingest entry)
Approve, edit the list, or drop any?
```

You drop the stakeholder update (Alex was a passing mention, not a
contributor) and say *go*. Five edits land. The pre-commit hook fires;
`densa` validates the frontmatter on every touched page; the commit
goes through.

> *What the LLM did here that you didn't have to:* split the
> transcript into an analysis + a fresh decision page + project-status
> updates, citing the same raw transcript from five distinct angles —
> all cross-linked, all frontmatter-validated.

### Wednesday afternoon — you ask a quick question

You're writing a Slack reply and need to remember a number.

> *query when did we ship the v2 ingest pipeline?*

The agent reads the global `index.md`, drills into
`domains/workspace/index.md`, opens the relevant decision and analysis
pages, and answers inline:

> Shipped on 2026-03-14 (see [[microservices-split]] §"Rollout";
> retrospective in [[2026-03-21-postmortem-analysis]]).

No file gets created — the answer is short, it's just an in-chat
citation. You paste the wikilinks into Slack and move on.

> *What the LLM did here that you didn't have to:* walked an index
> graph you don't actively remember, surfaced the two pages that
> answer the question, cited them so future-you can verify.

### Friday afternoon — `lint`

You run `lint`. The agent writes
`outputs/lint/2026-04-10.md`. The report is mostly green:

- 0 broken wikilinks.
- 0 frontmatter-required-keys failures.
- 2 `last_validated > 180d` warnings on two concept pages — you skim
  the cited sources, bump the timestamp on one, deprecate the other.
- 1 "promotion candidate" — a Q&A you re-read three times last month.
  You note it, ignore for now, ship `promote` next week.

The next lint won't show drama if you keep up. A boring lint report is
a healthy lint report.

> *What the LLM did here that you didn't have to:* checked 100+ wiki
> pages for orphans, broken links, stale claims, contradictions —
> rewrote nothing, just told you what needs attention.

### Sunday evening — `process-inbox`

You spent the weekend at a conference, clipping with Obsidian Web
Clipper from your phone. Eight articles landed in `inbox/`. You type:

> *process-inbox*

The agent reads each clip's title + first paragraph, proposes domain +
bucket + canonical slug, waits for OK. You approve, it `git mv`s each
file into `domains/<X>/raw/<bucket>/`. **Critically, it does not
ingest.** That's a separate decision per file — some clips earn an
ingest (you cared enough to make wiki structure for them), others sit
in `raw/` as a searchable archive without ever becoming wiki nodes.

> *What the LLM did here that you didn't have to:* picked a domain for
> each clip, slugged the filename in a way the rest of the wiki will
> resolve, and refused to over-eagerly synthesise unimportant material
> into wiki noise.

---

## 🔀 The seams: when to use which operation

Four decisions that come up in the first month.

### Substantive answer or chat-only?

If your `query` answer is *one paragraph and you'll never re-read it*,
keep it in chat. If it's *a comparison, a thesis, or a timeline you'd
plausibly need again* — file it. The agent defaults to filing as
`outputs/qa/<YYYY-MM-DD>-<slug>.md`; ask it to skip when you don't
want the artifact. Q&A artifacts live alongside lint reports, ignored
by the wikilink resolver — they're runtime products, not wiki.

### Q&A that recurs → `promote`. Q&A that's time-bound → leave it.

Reach for `promote` only when **all three** of these hold:

| Signal                        | Translation                                                          |
| ----------------------------- | -------------------------------------------------------------------- |
| **Evergreen claim**           | The answer doesn't depend on a specific timestamp (concept beats event). |
| **≥ 2 distinct sources**      | Inline `[[wikilinks]]` already satisfy the target type's §3.1 cardinality. |
| **Repeated visits**           | You re-read this Q&A across separate sessions; or `lint` flags it as a promotion candidate. |

Anti-signals (let the Q&A age out under `outputs/qa/`):

- The question is *"what did I say about X last week?"* — the answer
  is time-bound; promoting freezes a snapshot the wiki doesn't need.
- The Q&A's load-bearing prose is *"I'm not sure, but…"* — promote
  requires declarative voice. An unresolved question belongs in
  `wiki/questions/` via `promote --as question`, not in
  `wiki/syntheses/`.
- The Q&A cites only 1 raw file. Either run a follow-up `query` to add
  citations, or promote `--as concept` (which allows `sources ≥ 0`) —
  never inflate fake citations to pass pre-flight.

When in doubt, leave it. `git revert` undoes a promote, but the wiki
page accumulates inbound wikilinks once visible; reverse migration is
harder once the link graph adopts it.

### Clear domain → `raw/`. Ambiguous → `inbox/`.

If you know *exactly* which `domains/<X>/raw/<bucket>/` a new source
belongs in, drop it there directly. **Most material can skip the
inbox** — round-tripping is friction. Use `inbox/` only when (a) you
captured from mobile and Obsidian Mobile can't easily browse the right
domain folder, or (b) the source genuinely could land in two domains
and you'd rather decide on the desktop with full L2 context.
`process-inbox` is the only operation that touches `inbox/`; nothing
auto-routes from there.

### Contradiction during `query`? Don't fix inline.

If you notice mid-`query` that page A and page B contradict each
other, the temptation is to ask the agent to fix it on the spot.
Resist. Two reasons:

1. **A `query` commit isn't scoped to write `domains/*/wiki/**`** (per
   AGENTS007). The agent will refuse; if it doesn't, your pre-commit
   hook will.
2. **Mid-query is the wrong time to think about wiki health.** Add
   the contradiction to the next `lint` report's human-review queue
   and address it in batch. You'll resolve it better when you're not
   half-way through answering a different question.

---

## ❓ FAQ

### The red lines

**Why is `raw/` immutable?**

Because the wiki's epistemic integrity depends on being able to walk
any claim back to a verifiable source. If raw is editable, the LLM's
own past synthesis errors can silently propagate into the evidence
base, and the wiki becomes a closed epistemic loop — it cites itself,
not the world. The pre-commit hook (AGENTS001) enforces this. The
only sanctioned exception is a transcription-correction sweep
documented per-L2 (see e.g. the psychology L2's "Known transcription
corrections" section).

**Why is `log.md` append-only and reverse-chronological?**

Append-only because the log is the audit trail of every ingest / query
/ lint — rewriting would erase the LLM-vs-human collaboration history.
Reverse-chronological because you read top-down and the most recent
state is what matters. When position drift happens, the
`WIKI_ALLOW_LOG_REORDER=1` bypass permits a single-shot reorder sweep
— but the diff must be a pure permutation plus a maintenance audit
entry.

**Why don't we delete wiki pages?**

Wikilinks propagate. Deleting `[[xyz]]` silently breaks every page that
referenced it; renaming is a cascade you must own consciously. The
deprecation pattern (`status: deprecated` + `> Superseded by
[[new-page]]` redirect + remove from index) keeps the link graph
intact while the page becomes a gravestone pointing at its successor.

### Scale & drift

**How big can the wiki get before it stops scaling?**

Empirically, `index.md` Dataview routing suffices to ~500 wiki pages.
Past that, two early-warning signals: any single Dataview block
exceeds ~50 rendered rows, or `index.md` rendering becomes noticeably
slow. Either fires → migrate to Obsidian Bases (`.base` files) or
layer Smart Connections on top. Until then Dataview is more
diff-friendly in git and the LLM operates on its source markdown more
naturally.

**How do I know when a claim has drifted?**

`lint` will flag:

- pages whose `last_validated` is older than 180 days (concept /
  framework / protocol / entity types) — re-read the cited sources,
  bump the timestamp.
- citation chains that take more than 2 hops to reach a `raw/` file —
  claims that float without a recent evidence anchor.
- patterns / themes whose latest instance is older than the L2's
  configured staleness threshold.
- contradictions where two pages make opposite claims about the same
  entity / concept.

Treat lint reports as work-in-progress dashboards, not pass/fail
gates. The goal is a *boring* lint report: each subsequent run mostly
says "no new findings since last lint", with the human-review queue
draining gradually.

### Setup choices

**Do I need Obsidian?**

No. The wiki is plain markdown with YAML frontmatter and
`[[wikilink]]` syntax — any editor works. Obsidian adds three things
this template benefits from: **Dataview** (powers the dynamic blocks
in every `index.md`; without it, indices fall back to static markdown
— still readable, just no auto-refresh), **Templater** (drops the right
frontmatter for each page type), and **Graph view** (makes the link
structure visible). Use VSCode or Neovim if you prefer; the LLM agent
doesn't care about the editor.

**Can I run this with a non-Cursor agent?**

Yes. The prompts and schema are agent-agnostic. The template is
tested with Cursor and Claude Code, but anything that can read
`AGENTS.md`, follow markdown templates, and run shell commands works.
The required file-system tools per operation are read / write /
`git mv` / `git diff` — no exotic capabilities.

**My vault is mostly in Chinese — anything special?**

Yes. See [`../docs/CJK-WORKFLOW.md`](../docs/CJK-WORKFLOW.md). The
schema is language-neutral; the conventions for slugs, aliases,
commit messages, and lint-report language are documented separately so
a CJK-first vault stays internally consistent.

**Will this work with private / sensitive material?**

Yes, with care. See [`../SECURITY.md`](../SECURITY.md) for the
hardening checklist (git-crypt, cold backup remote, hardware-token
GPG keys). The template ships
[`scripts/setup_encryption.sh`](scripts/setup_encryption.sh) and a
`.gitattributes.example` to make encrypted `raw/` trees a one-command
setup, and the psychology L2 demonstrates the two privacy postures
(public-shareable vs private-repo) in §"Privacy posture".

**What does CI run?**

A single workflow at `.github/workflows/ci.yml` with two jobs:

- **`validate`** runs `densa --all` on every push and PR, plus
  `densa --diff origin/<base>` (staged rules over the PR range) on
  PRs. Enforces the L1 red lines, the universal frontmatter contract,
  wikilink resolvability, and AGENTS001–009. This is the gate every
  PR must clear.
- **`tests`** runs `pytest`, `ruff check .`, and `mypy --strict`
  across Python 3.10/3.11/3.12. Together with `validate` it covers
  schema correctness and the validator's own code health.

### Operation philosophy

**Why does `outputs/` exist instead of `wiki/syntheses/`?**

Lint reports and Q&A archives are *operation artifacts*, not compiled
knowledge. Three concrete problems with dropping them in
`wiki/syntheses/`:

- Reports accumulate as noise but L1 §4 forbids deleting wiki pages,
  so old reports can't be cleaned up cleanly.
- `type: synthesis` requires `sources: ≥ 2`; a lint report doesn't
  fit that contract.
- `query` would occasionally cite a lint report as if it were
  knowledge, polluting answers.

The fix: a separate top-level `outputs/` directory — in git for the
audit trail, but excluded from the wikilink graph and the wiki's
schema contracts. Reports point at wiki pages; wiki never points back.
When `outputs/` grows noisy, `git rm outputs/{lint,qa}/<old>.md`
removes it safely (no wiki page can link there, by design).

**Where do `query` answers go?**

Substantive `query` answers are filed as `type: report` Q&A artifacts
under `outputs/qa/<YYYY-MM-DD>-<slug>.md` — alongside `outputs/lint/`
and `outputs/snapshots/`, not inside `wiki/`. Same reasoning as above.
If a particular answer turns out to be evergreen and worth
wikilink-graph membership, the path forward is `promote` (see
*The seams* §"Q&A that recurs").

---

## 📚 Where to read next

Same four paths the README offers; here for re-orientation mid-use.

- 🧭 **Why the design is shaped this way** —
  [`../docs/DESIGN.md`](../docs/DESIGN.md). Every load-bearing
  decision; the L1 / L2 split; how to design your own L2.
- 🌱 **Starting your own vault** —
  [`../docs/bootstrap-prompt.md`](../docs/bootstrap-prompt.md).
- 🛠 **Install / hooks / encryption** — [`SETUP.md`](SETUP.md).
- 🤝 **Hacking on schema / validator / prompts** —
  [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

For shipped example domains, see
[`../docs/EXAMPLES.md`](../docs/EXAMPLES.md) (guided tour) and
[`../docs/EXAMPLE-DOMAINS.md`](../docs/EXAMPLE-DOMAINS.md) (keep /
adapt / remove matrix).
