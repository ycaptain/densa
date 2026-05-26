# inbox/

Opt-in staging area for un-routed material. Drop a source here when
you're not sure which `domains/<X>/raw/<bucket>/` it belongs in; clear
it via the `process-inbox` operation (see
[`../_system/prompts/process-inbox.md`](../_system/prompts/process-inbox.md)).
Files in `inbox/` are deliberately exempt from
[`AGENTS.md` §"Routing rules"](../AGENTS.md#5-routing-rules-where-does-a-new-source-go)
until `process-inbox` moves them.

Ships nominally empty: this README is the only tracked file. The dir
materialises on first use — `process-inbox` is the only operation
that reads from it, and it `git mv`s each entry into the appropriate
`domains/<X>/raw/<bucket>/`.

Full role + layout context:
[`../docs/reference/repository-layout.md`](../docs/reference/repository-layout.md).
