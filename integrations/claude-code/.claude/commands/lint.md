First confirm the workspace is a Densa vault (`AGENTS.md` at root +
`_system/densa/` present); if not, refuse and tell me.

Then run the canonical `lint` procedure from
[`_system/prompts/lint.md`](../../../../_system/prompts/lint.md).
Scope is `$ARGUMENTS` (e.g. `--domain psychology`); empty arguments
mean global scope. Write the report to `outputs/lint/<YYYY-MM-DD>.md`
and refresh `outputs/snapshots/index-snapshot.md`.
