# Red lines — full rationale

Reference companion to [`AGENTS.md`](../../AGENTS.md) §6. The
contract file lists each red line in a single sentence; this page
gives the failure-mode rationale a future maintainer (LLM or human)
needs to understand *why* each rule cannot be relaxed.

Each red line names what cannot be done, the load-bearing reason, and
the sanctioned escape hatch (if any).

## 1. `raw/` is immutable

**Rule.** Never edit, rename, move, or delete files under any `raw/`
directory.

**Enforced by.** AGENTS001 (`raw-immutability`).

**Why.** Every wiki claim's chain of provenance terminates at a raw
file. Editing or renaming raw breaks `git log --follow` traces from a
wiki page back to its source; the audit promise that "any wiki claim
is verifiable years later" collapses.

**Sanctioned exception.** A domain-declared transcription-correction
sweep (see e.g. `examples/showcases/psychology/AGENTS.md` §"Known transcription
corrections"). The L2 declares the exception, lists the patterns, and
the sweep edits raw only in the narrow correction window. Without
that L2 declaration, no raw edit is allowed.

## 2. `log.md` is append-only, written reverse-chronologically

**Rule.** New entries are inserted at the **entry insertion point**
so newest is first. Default insertion point: immediately after YAML
frontmatter. If the log file has a human-facing H1 / intro prose /
entry-format preamble followed by a horizontal rule, the insertion
point is **immediately after that preamble separator**. Never place
entries above the H1 / preamble. Never rewrite past entries; correct
via a new entry.

**Enforced by.** AGENTS002 (`log-append-only`).

**Why.** The log is the *only* artifact that proves the ordering of
ingest / lint decisions over time. Rewriting an old entry to "fix" a
factual error retroactively hides the moment that error was made,
which is exactly the moment a future reader needs to find to
understand the wiki's evolution.

**Sanctioned exception.** `WIKI_ALLOW_LOG_REORDER=1` for one commit
(a pure-permutation reorder sweep to repair drift). The diff must be
set-equal (no content changes, only line reordering) plus a new
`## [YYYY-MM-DD] maintenance | …` entry explaining the reorder.

**Note on terminology.** The word "append" in older prompts / docs is
a legacy synonym for "prepend at the entry insertion point". The
content is appended to the wiki's audit trail; the position is always
the entry insertion point. Frontmatter `updated: YYYY-MM-DD` may be
bumped in lockstep with each new entry (paired `-`/`+`); past entries
themselves are immutable.

## 3. No wiki page deletion

**Rule.** Use the deprecation pattern: set `status: deprecated`, add
a `> Superseded by [[new-page]]` redirect line at the top of the
page, and remove the bullet from `index.md`.

**Enforced by.** Not currently a validator rule — review-only.
Mechanical enforcement is deferred because deletion intent is hard to
distinguish from a `git mv` that the validator hasn't seen the target
of yet.

**Why.** A wiki page may be cited from raw notes the human still
reads, from another wiki page that hasn't been updated yet, or from
external blog posts. Deletion silently breaks those links;
deprecation keeps the slug resolvable while signalling "do not author
against this".

## 4. No bulk renames without human consent

**Rule.** Slugs propagate via wikilinks; one rename = many edits =
human approval gate. Never silently rewrite slugs across the wiki.

**Enforced by.** Not currently a validator rule — operational
discipline only.

**Why.** Slug renames are mechanically simple but semantically
load-bearing — a slug is the identifier the human types in chat to
pull a page into context. Renaming silently (even with full
wikilink-graph fixup) breaks the human's mental index. Always surface
the rename for approval.

## 5. No silent web fetches during ingest

**Rule.** If you need to enrich beyond the source, ask first and cite
added context separately.

**Enforced by.** Operational discipline; not a validator rule.

**Why.** A wiki page that quietly weaves in web-fetched material
defeats the "every claim traces to a source in this repo" invariant.
Future readers can't reproduce the LLM's web context (URLs decay,
search results drift); the claim becomes unverifiable.

## 6. Every claim traces to ≥1 source

**Rule.** Every wiki claim must be backed by a `sources:` frontmatter
entry or an inline `[[source-link]]`. Pure synthesis pages cite the
wiki pages they synthesise.

**Enforced by.** AGENTS003 (presence), AGENTS005 (analysis
cardinality), AGENTS006 (wikilink resolvability).

**Why.** This is the compiler-style invariant the whole architecture
rests on — if a wiki page can make claims without provenance, the
wiki becomes a second LLM hallucination surface rather than a
compounding knowledge base.

## 7. Bulk re-ingest preserves a `.legacy/` snapshot

**Rule.** When re-running ingest on a previously-authored wiki page,
the LLM MUST first `git mv` the existing file under
`domains/<X>/wiki/.legacy/<same-name>.md` before writing the new
version. Do not delete or amend in place.

**Enforced by.** Operational discipline; surfaced by `lint` reviews.

**Why.** A re-ingest under a newer framework reasonably rewrites the
whole page; the human's safeguard against the LLM silently degrading
the prior analysis is that the old version remains diff-able weeks
later. In-place amendment removes that safeguard.

## 8. Multi-modal sources require explicit read-bound declarations

**Rule.** When a `raw/` file contains images, audio, video, or any
non-text payload the LLM cannot fully read in this session, the LLM
MUST state in the ingest plan exactly what it can vs. cannot extract.

**Enforced by.** Operational discipline (the ingest plan that
declares the scope is the audit trail).

**Why.** A wiki page that *looks* like it summarises a 30-minute
recording but actually only ingested the auto-generated transcript —
missing the visual whiteboard in the video, missing the audio
intonation that reveals sarcasm — is worse than no page at all. It
presents partial coverage as full coverage, and downstream syntheses
inherit the gap.

**Mitigation pattern.** When in doubt, downgrade the ingest to a
partial pass and flag the remainder for a follow-up session in the
log entry: *"this ingest covered text only; visual content deferred
to follow-up session 2026-MM-DD"*.
