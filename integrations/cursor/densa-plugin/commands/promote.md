Run the canonical `promote` procedure from
`_system/prompts/promote.md` (path relative to the Densa vault root)
against `$ARGUMENTS` (path to a `outputs/qa/<file>.md`, optionally
followed by `--as <type>` and/or `--slug <new-slug>`). Run all
pre-flight checks first and abort with specific remediation if any
fails; do not partially apply. Wait for my approval after showing
the planned diff (frontmatter + body changes + log entries) before
committing. If the current workspace is not a Densa vault clone,
stop and ask me to open one.
