# inbox/

Un-routed staging area. Drop a source here when you're **not sure**
which `domains/<X>/raw/<bucket>/` it belongs in — Obsidian Mobile
captures, Web Clipper drops, photos waiting for OCR, etc.

This directory is **opt-in**: most material can be dropped directly
into the correct domain's `raw/` bucket. Use `inbox/` only when the
routing decision genuinely needs a desktop session with full L2
context.

To clear it, run the `process-inbox` operation in your AI chat. The
agent reads each file's first paragraph, proposes `domains/<X>/raw/
<bucket>/<slug>`, waits for your OK, then `git mv`s. Procedure:
[`_system/prompts/process-inbox.md`](../_system/prompts/process-inbox.md).
`process-inbox` does **not** ingest — that remains a separate
decision per file.

> **Routing immunity.** Files in `inbox/` are deliberately exempt
> from `AGENTS.md` §5 routing (the LLM must not silently guess a
> domain for an inbox file). Only `process-inbox` may move them
> into `raw/`.
