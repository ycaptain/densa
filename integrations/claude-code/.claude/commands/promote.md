First confirm the workspace is a Densa vault (`AGENTS.md` at root +
`_system/densa/` present) and that `$ARGUMENTS` resolves to a file
under `outputs/qa/`; if either fails, refuse and tell me.

Then run the canonical `promote` procedure from
[`_system/prompts/promote.md`](../../../../_system/prompts/promote.md)
against `$ARGUMENTS` (path to a `outputs/qa/<file>.md`, optionally
followed by `--as <type>` and/or `--slug <new-slug>`). Run all
pre-flight checks first and abort with specific remediation if any
fails; do not partially apply. Wait for my approval after showing
the planned diff (frontmatter + body changes + log entries) before
committing.
