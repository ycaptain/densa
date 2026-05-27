Run the canonical `lint` procedure from `_system/prompts/lint.md`
(path relative to the Densa vault root). Scope is `$ARGUMENTS`
(e.g. `--domain psychology`); empty arguments mean global scope.
Write the report to `outputs/lint/<YYYY-MM-DD>.md` and refresh
`outputs/snapshots/index-snapshot.md`. If the current workspace is
not a Densa vault clone, stop and ask me to open one.
