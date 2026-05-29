First confirm the workspace is a Densa vault (`AGENTS.md` at root +
`_system/densa/` present); if not, refuse and tell me.

Then run the canonical `ingest` procedure from
[`_system/prompts/ingest.md`](../../../../_system/prompts/ingest.md)
against `$ARGUMENTS`. Pass 1 (analysis + plan) first; wait for my
approval before Pass 2 (generation) writes anything.
