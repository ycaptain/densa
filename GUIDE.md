---
type: manual
scope: vault
updated: 2026-05-25
compiled_against: 2
---

# GUIDE — using a Densa vault day to day

> Picks up after your first ingest; pitch + Quickstart live in [`README.md`](README.md).

This file is **explanatory** — what a week of using the wiki actually
feels like, where the operations seam together, and the questions
that come up after your first few ingests. The **normative** contract
lives in [`AGENTS.md`](AGENTS.md) (L1) and each
`domains/<X>/AGENTS.md` (L2). When GUIDE and AGENTS disagree, AGENTS
wins; schema-shaped tables here are mirrors for human reading, not the
source of truth.

---

## 🃏 Cheat sheet

The only verbs you ever type. Per-op write scopes + forbids live in
[`AGENTS.md` §"The six operations"](AGENTS.md#2-the-six-operations).

The **ingest tier ranges** are: light L2 (e.g. one paper) ≈ 3–6 pages;
medium (one meeting + decisions) ≈ 5–10 pages; heavy (one therapy
session) ≈ 8–15 pages. See
[`AGENTS.md` §"ingest" step 3](AGENTS.md#21-ingest-path).

The **page-type matrix** (which folder, what `sources` cardinality)
lives in
[`AGENTS.md` §"Frontmatter schema"](AGENTS.md#3-frontmatter-schema-universal)
plus
[`docs/reference/sources-cardinality.md`](docs/reference/sources-cardinality.md).
The **red lines** (what no operation may do) and their machine-enforced
IDs (AGENTS001–013) live in
[`AGENTS.md` §"Red lines"](AGENTS.md#6-red-lines-non-negotiable)
+ [§"Machine-enforced rule registry"](AGENTS.md#61-machine-enforced-rule-registry).
Pin those two anchors — every other "is this allowed?" question routes
through them.

### Mapping natural language to operations

When in doubt about which verb a user request maps to:

| User intent (examples) | Op | Command | Contract | Procedure |
| --- | --- | --- | --- | --- |
| "ingest \<path\>" / "process this source" / drops new file | 📥 [ingest](AGENTS.md#21-ingest-path) | `ingest <path>` | [AGENTS.md §2.1](AGENTS.md#21-ingest-path) | [`ingest.md`](_system/prompts/ingest.md) |
| "what does the wiki say about X" / "summarise across …" | 🔍 [query](AGENTS.md#22-query-question) | `query <question>` | [AGENTS.md §2.2](AGENTS.md#22-query-question) | [`query.md`](_system/prompts/query.md) |
| "lint" / "health check" / "find contradictions" | 🩺 [lint](AGENTS.md#23-lint---domain-x) | `lint [--domain <X>]` | [AGENTS.md §2.3](AGENTS.md#23-lint---domain-x) | [`lint.md`](_system/prompts/lint.md) |
| "process-inbox" / "triage inbox" / drops a file in inbox/ | 📨 [process-inbox](AGENTS.md#24-process-inbox-optional-opt-in) | `process-inbox` | [AGENTS.md §2.4](AGENTS.md#24-process-inbox-optional-opt-in) | [`process-inbox.md`](_system/prompts/process-inbox.md) |
| "promote outputs/qa/\<file\>" / "this Q&A is wiki-grade" | ⬆️ [promote](AGENTS.md#25-promote-qa-path-qa--wiki-page) | `promote outputs/qa/<file>` | [AGENTS.md §2.5](AGENTS.md#25-promote-qa-path-qa--wiki-page) | [`promote.md`](_system/prompts/promote.md) |
| Ambiguous request | — | — | — | Ask one short clarifying question |

Always reference `_system/prompts/<op>.md` rather than improvising.

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
- create wiki/summaries/2026-04-08-meeting-q2-planning-summary.md
- update wiki/entities/q2-platform-migration.md  (project status, risks)
- update wiki/entities/microservices-split.md    (decision ADR text)
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
> transcript into a summary + project / decision entity updates,
> citing the same raw transcript from five distinct angles — all
> cross-linked, all frontmatter-validated. (`project` and `decision`
> live as `entity` pages under v2's nine-type schema; the L2 carries
> their lifecycle fields. See
> [`docs/reference/karpathy-mapping.md`](docs/reference/karpathy-mapping.md).)

### Wednesday afternoon — you ask a quick question

You're writing a Slack reply and need to remember a number.

> *query when did we ship the v2 ingest pipeline?*

The agent reads the global `index.md`, drills into
`domains/workspace/index.md`, opens the relevant decision entity and
summary pages, and answers inline:

> Shipped on 2026-03-14 (see [[microservices-split]] section "Rollout";
> retrospective in [[2026-03-21-postmortem-summary]]).

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
| **≥ 2 distinct sources**      | Inline `[[wikilinks]]` already satisfy the target type's cardinality (see [`sources-cardinality.md`](docs/reference/sources-cardinality.md)). |
| **Repeated visits**           | You re-read this Q&A across separate sessions; or `lint` flags it as a promotion candidate. |

Anti-signals (let the Q&A age out under `outputs/qa/`):

- The question is *"what did I say about X last week?"* — the answer
  is time-bound; promoting freezes a snapshot the wiki doesn't need.
- The Q&A's load-bearing prose is *"I'm not sure, but…"* — promote
  requires declarative voice. An unresolved question belongs in
  `wiki/open-questions/` via `promote --as open-question`, not in
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

> Moved to [`docs/faq.md`](docs/faq.md) — the red lines, scale &
> drift, operation philosophy. Operational recipes (install, plugins,
> encryption, disabling the hook, CI) now live in
> [`docs/setup.md`](docs/setup.md).

---

## 🏷 Choosing or replacing the default domain

> Moved to
> [`docs/setup.md` §"Choosing or replacing the default domain"](docs/setup.md#choosing-or-replacing-the-default-domain)
> — the day-one decision tree, adopt/remove/rename recipes, the
> showcase migration walkthrough.

---

## 📚 Where to read next

Back to
[`README.md` §"Where to read next"](README.md#where-to-read-next)
— that's the canonical dispatcher (setup / faq / design-rationale /
bootstrap / CONTRIBUTING). This file deliberately doesn't mirror it
to avoid drift.
