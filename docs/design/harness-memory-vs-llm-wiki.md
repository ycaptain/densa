# Harness memory vs LLM Wiki — where Densa sits

> Reference companion to [`design-rationale.md`](design-rationale.md). The
> umbrella doc explains _why each load-bearing Densa decision exists_;
> this page zooms in on one specific question that adopters ask early:
>
> > "Isn't this just `CLAUDE.md` / Cline Memory Bank / Letta memory /
> > Codex Skills under a different name?"
>
> Short answer: no. Long answer: there are **six other things** in the
> agent-tooling stack that look like "knowledge bases" but aren't, and
> Densa is the seventh — the one that _compounds_. This page draws the
> distinctions verbatim so the comparison can be cited rather than
> re-argued.

## TL;DR

| Layer                             | What it stores                                             | Who reads it                | Compounds across sessions?                 | Source-grounded?              | Densa equivalent (if any)                                  |
| --------------------------------- | ---------------------------------------------------------- | --------------------------- | ------------------------------------------ | ----------------------------- | ---------------------------------------------------------- |
| `AGENTS.md` / `CLAUDE.md` / Rules | project conventions, do/don't, commands                    | agent                       | no (re-read each session)                  | no (instructions, not facts)  | the L1/L2 contracts themselves                             |
| Cline Memory Bank                 | project state, brief, active context, progress             | agent + human               | partially (state, not knowledge)           | no (no `sources:`)            | `overview.md` carries the same job under stricter schema   |
| Skills (Codex / Pi / Cline)       | reusable workflows, SOPs                                   | agent (loaded on demand)    | no (procedure, not knowledge)              | no                            | `_system/prompts/` + `integrations/*/skills/`              |
| Session memory / compaction       | recent tool calls, branch summaries                        | agent (runtime only)        | no (per-session checkpoint)                | no                            | not applicable — Densa is schema, not runtime              |
| RAG / MCP search / VFS            | chunks, vectors, external docs                             | agent (query-time retrieve) | no (query-time reassembly)                 | optional                      | not applicable — Densa is the inverse of RAG               |
| Letta personal memory             | user preferences, agent experience, identity               | agent (self-edits)          | yes (within one vendor harness)            | no                            | not applicable — Densa's memory is filesystem, not runtime |
| **LLM Wiki (Densa)**              | summaries, entities, concepts, comparisons, open-questions | human **and** agent         | **yes — every ingest densifies the graph** | **enforced by AGENTS001–012** | this repo                                                  |

The fault line is "does the artifact survive when you swap your agent
harness?" The first six layers don't. Densa does.

---

## 1. `AGENTS.md` / `CLAUDE.md` / Rules

**What it is.** A markdown file at vault root that the agent reads on
every session. Tells the agent how the project is structured, which
commands to run, what to avoid. The
[AGENTS.md standard](https://agents.md) formalises this as a cross-tool
contract; Cursor, Claude Code, Codex, and Cline all read it natively.

**What it stores.** Instructions, not facts. "Run `pytest` before
committing." "Don't touch `raw/`." "The Postgres schema lives in
`prisma/`."

**Where it stops.** It's a _static contract_. It doesn't accumulate
across sessions — it's re-read each time. If you ask the agent "what
did we decide about the OAuth refactor?", `AGENTS.md` can't answer
because that's _knowledge_, not _rules_.

**Densa relationship.** `AGENTS.md` is the L1 contract — Densa uses it
the way every AGENTS.md-aware project does. But Densa _also_ maintains
a wiki underneath; the OAuth refactor decision lives in
`domains/<X>/wiki/entities/oauth-refactor.md` with provenance back to
the meeting transcript that produced it.

## 2. Cline Memory Bank — "project state docs"

**What it is.** [Cline](https://github.com/cline/cline) ships a
[Memory Bank pattern](https://docs.cline.bot/best-practices/memory-bank):
six markdown files at `memory-bank/` carrying `projectbrief.md`,
`productContext.md`, `activeContext.md`, `systemPatterns.md`,
`techContext.md`, `progress.md`.

**What it stores.** _Project continuity state._ "Where are we?" "What
just changed?" "What's the next step?" Built so the agent can resume
work after context loss.

**Where it stops.** No `sources:` field, no provenance. The pages are
_the agent's own working notes_, not a source-grounded knowledge
graph. There's no equivalent of Densa's "every claim traces back to a
raw file" red line. If a Memory Bank claim is wrong, you can't grep
for the meeting it came from.

**Densa relationship.** Densa's `domains/<X>/wiki/overview.md` does
the same job for the per-domain "where are we?" question — but with
schema-enforced `sources:` and Dataview-driven freshness. The "active
context" use case is closest to Densa's _most recent_ `log.md` entries.

## 3. Skills (Codex / Pi / Cline / Cursor)

**What it is.** Reusable workflow definitions. A skill is typically a
directory with a `SKILL.md` describing when to invoke + how to
execute, optionally bundled with scripts and reference files. Codex's
[Agent Skills](https://developers.openai.com/codex/skills) doc
formalises this with **progressive disclosure** — only the name +
description + path enters context until the agent decides to load the
full SKILL.md.

**What it stores.** _Procedure knowledge._ "How do I do a code
review?" "How do I bisect a regression?" "How do I onboard a new
contributor?"

**Where it stops.** A skill tells the agent _how to do a thing_. It
doesn't tell the agent _what is currently true about the world_. The
two aren't substitutes.

**Densa relationship.** Densa has skills — they're the
`_system/prompts/<op>.md` files for `ingest` / `query` / `lint` /
`process-inbox` / `promote`, plus the `integrations/*/skills/`
sideload bundles. But these _operate on the wiki_; they aren't the
wiki.

## 4. Session memory / compaction / branch summary

**What it is.** Agent harnesses (Pi, Claude Code, OpenCode, Cline)
all store session histories — usually JSONL of every tool call, with
periodic compaction to keep context under budget. Pi explicitly stores
sessions as
[tree-structured JSONL](https://pi.dev/docs/latest/session-format)
with `id/parentId` so branches survive.

**What it stores.** _Runtime checkpoints._ Recent file edits, recent
tool calls, branch summaries, usage / cost. Built so the agent can
resume mid-task or branch to explore alternatives.

**Where it stops.** Session memory is _transient by design_. Even when
compaction writes a structured summary, that summary is _about this
session's work_, not _about the subject matter_. The next session
starts fresh against the wiki, not against last session's tool calls.

**Densa relationship.** Densa deliberately doesn't have a session
trace layer — that's runtime, Densa is schema. The closest equivalents
are the `log.md` entries (event-level, append-only) and the
`outputs/qa/` artifacts (substantive Q&A worth re-reading). For
session-level observability, use your harness's own facility.

## 5. RAG / MCP search / Virtual filesystem

**What it is.** [Deep Agents](https://docs.langchain.com/oss/python/deepagents/context-engineering)
calls this "context offloading": don't put everything in the prompt,
let the agent retrieve via tools (vector search, MCP server, VFS,
SQL). RAGFlow, Smart Composer, Open WebUI all sit here.

**What it stores.** _Whatever you indexed._ Raw documents, code,
PDFs, chat logs, anything chunkable.

**Where it stops.** Knowledge is _synthesised at query time, then
discarded_. The system stores fragments; the answer doesn't get
filed back. This is exactly the
[Karpathy llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
critique: every query "rediscovers knowledge from scratch."

**Densa relationship.** Densa is the _architectural inverse_ — at
query time you read the _compiled wiki_, not the _raw chunks_. The two
compose: past ~500 pages, layer embedding search on top of the wiki as
fuzzy fallback (see [`design-rationale.md`](design-rationale.md)
"How it compares").

## 6. Letta personal memory / agent identity memory

**What it is.** [Letta Code](https://docs.letta.com/letta-code/) is
explicitly memory-first: the agent self-edits its own memory blocks,
has `/remember` to trigger updates, runs background reflection
subagents to consolidate. The
[LangChain "Your harness, your memory"](https://www.langchain.com/blog/your-harness-your-memory)
essay frames this as the strategic question: who owns the memory when
the harness is closed-source?

**What it stores.** _Agent persona + user preferences + accumulated
experience._ "User prefers TypeScript over Python." "User dislikes
agent touching unrelated files." "Last time I tried X, it failed
because of Y."

**Where it stops.** Letta memory is _bound to the Letta runtime_. If
you switch from Letta Code to Claude Code, the memory doesn't come
with you — it's a vendor-coupled artifact (this is the entire
"harness ↔ memory lock-in" argument).

**Densa relationship.** Densa's stance is the diametric one: _memory
lives in your filesystem as markdown + git_. Your agent harness is
replaceable (Cursor today, Claude Code tomorrow, Pi the day after);
your wiki is not. The "harness-agnostic memory" posture is the single
biggest difference from Letta / Cline Memory Bank as a category.

---

## 7. LLM Wiki (Densa's category)

What's distinct, restated against the six layers above:

| Property                          | First six layers             | LLM Wiki / Densa                             |
| --------------------------------- | ---------------------------- | -------------------------------------------- |
| Persistence                       | per-session or per-runtime   | filesystem + git, harness-independent        |
| Provenance                        | none enforced                | `sources:` required, AGENTS001-012 validates |
| Reader                            | agent only (usually)         | **human + agent**, browsable in Obsidian     |
| Compounds across sessions         | no (state) or no (procedure) | **yes — every ingest densifies the graph**   |
| Cross-references                  | within one tool's UI         | wikilinks render in every markdown reader    |
| Failure mode if vendor disappears | data loss                    | none — your vault is still markdown          |

The Karpathy framing: **"The wiki is the codebase. Obsidian is the
IDE. The LLM is the programmer."** The first six layers are _the
programmer's working notes_; the wiki is _the codebase those notes
edit_. You don't ship working notes — you ship the codebase.

---

## "Which one do I want, in my situation?"

Decision tree:

1. **You want the agent to resume work after context loss within one
   project.** → Cline Memory Bank pattern. Densa covers part of this
   via `overview.md` + the most-recent `log.md` entries.
2. **You want the agent to follow project conventions.** → `AGENTS.md`.
   Densa's L1/L2 contracts _are_ this.
3. **You want the agent to repeat a workflow consistently.** →
   Skills. Densa ships five (`_system/prompts/`).
4. **You want the agent to remember your preferences across all
   projects.** → Letta-style personal memory. Densa doesn't cover
   this; pair externally if you need it.
5. **You want to query a large corpus at retrieval time.** → RAG /
   MCP. Densa is the _inverse_ — compile once, query the compilation.
   They compose past ~500 pages.
6. **You want every source you read to make your knowledge denser, with
   citations, audited, durable.** → LLM Wiki. This is what Densa
   does.

If your need is (1)–(5) only, Densa is probably overkill. If your
need is (6) at all, Densa is what the category is called.

---

## Thin orchestrator seam — the v0.8 watch item (T004)

**Current stance (v1):** Densa stays a non-harness. You invoke the operation
prompts manually from your IDE; the LLM authors; you approve the plan. The
human-in-the-loop gate is load-bearing.

**The real friction case:** A vault owner running nightly batch ingests from CI
wants to type one command:

> `densa run ingest domains/research-papers/raw/2026-06-04-paper.md`

…and have Densa invoke the local `claude` CLI with the ingest prompt pre-loaded,
without opening an IDE. This is genuine friction today.

**The thin-orchestrator design (Option B):** A `densa run <op> <path>` subcommand
that shells out to the user's configured agent CLI — no SDK, no provider
abstraction, no session traces, zero new dependencies. Config is one env var:

```bash
DENSA_AGENT_CLI=claude   # or: codex, gemini, cursor-cli
densa run ingest domains/research-papers/raw/2026-06-04-paper.md
# → invokes: claude --print "$(cat _system/prompts/ingest.md)" <path>
```

This is **harness-as-orchestrator, not harness-as-runtime**: Densa never calls an
LLM directly. It shells out to whichever CLI the user already trusts, keeping the
"your agent harness is replaceable" promise intact.

**Why defer to v0.8:** The batch-ingest user story is real but not yet validated
by actual user demand. Adding `densa run` before that signal arrives couples the
CLI surface prematurely. Land it when ≥2 users report "headless workflow" as a
blocker.

---

## External anchors

- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  — the ~1500-word sketch Densa implements. The "knowledge compounds,
  not retrievable-on-demand" insight is here.
- [LangChain "Your harness, your memory"](https://www.langchain.com/blog/your-harness-your-memory)
  — the public framing of the vendor-coupling problem with runtime
  memory. Densa's harness-agnostic stance is the structural answer.
- [Cline Memory Bank docs](https://docs.cline.bot/best-practices/memory-bank)
  — the canonical six-file project-state pattern.
- [Codex Agent Skills](https://developers.openai.com/codex/skills) —
  the progressive-disclosure pattern Densa's prompts loosely follow.
- [Letta Code memory docs](https://docs.letta.com/letta-code/memory/)
  — the memory-first agent reference; the architectural counterweight
  to Densa's filesystem-first memory.
