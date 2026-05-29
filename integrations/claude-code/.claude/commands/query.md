First confirm the workspace is a Densa vault (`AGENTS.md` at root +
`_system/densa/` present); if not, refuse and tell me.

Then run the canonical `query` procedure from
[`_system/prompts/query.md`](../../../../_system/prompts/query.md)
to answer: $ARGUMENTS. Cite wiki pages inline; for substantive
answers, file the Q&A back to `outputs/qa/<YYYY-MM-DD>-<slug>.md`
(`type: report`). If the Q&A later proves evergreen, the human can
run `promote` to lift it into the wiki — do not edit `wiki/syntheses/`
from inside a `query`.
