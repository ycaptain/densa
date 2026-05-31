# Design docs — the "why"

> [!faq]- Who reads this folder?
> **Humans evaluating or extending Densa.** These are the long-form
> *explanation* docs — why the design looks the way it does and where
> it sits in the agent-memory landscape. You don't need them to
> *operate* a vault (that's [`../setup.md`](../setup.md) →
> [`../../GUIDE.md`](../../GUIDE.md)), and the machinery never loads
> them at runtime. Read one when you're deciding whether to adopt
> Densa, designing your own L2, or arguing "isn't this just RAG?".
>
> For the precise contract — schema tables, write scopes, rule IDs —
> see [`../reference/`](../reference/README.md) instead. This folder is
> the "why"; that folder is the "what".

| Page | What's in it |
|---|---|
| [`design-rationale.md`](design-rationale.md) | The long-form design essay — every load-bearing decision, the L1/L2 split, the `outputs/` / `promote` design choices, how to design your own L2, anti-patterns |
| [`harness-memory-vs-llm-wiki.md`](harness-memory-vs-llm-wiki.md) | Where Densa sits relative to AGENTS.md / Cline Memory Bank / Skills / session memory / RAG / Letta personal memory — the six "knowledge-base-shaped" layers in the agent stack |

Routing for "what should I read next?" lives in
[`../../README.md` §"Where to read next"](../../README.md#where-to-read-next).
