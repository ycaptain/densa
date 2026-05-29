First confirm the workspace is a Densa vault (`AGENTS.md` at root +
`_system/densa/` present) and that `inbox/` exists; if either is
missing, refuse and tell me.

Then run the canonical `process-inbox` procedure from
[`_system/prompts/process-inbox.md`](../../../../_system/prompts/process-inbox.md).
Triage every file under `inbox/`, propose a domain + bucket + slug for
each, and `git mv` them only after my approval. Do not ingest.
