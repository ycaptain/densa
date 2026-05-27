Run the canonical `process-inbox` procedure from
`_system/prompts/process-inbox.md` (path relative to the Densa vault
root). Triage every file under `inbox/`, propose a domain + bucket +
slug for each, and `git mv` them only after my approval. Do not
ingest. If the current workspace is not a Densa vault clone, stop
and ask me to open one.
