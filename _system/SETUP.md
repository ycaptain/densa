# Setup

One-time setup the human runs in Obsidian after cloning the vault. The wiki
itself is fully usable from Cursor Agent without any of these — they only
improve the Obsidian-side editing UX.

## Required plugins (already enabled)

- **Dataview** — powers the dynamic blocks in every `index.md`. Enable
  "JavaScript Queries" in its settings (needed for `dataviewjs`).

## Recommended plugins (install via Obsidian → Community plugins)

| Plugin                    | Purpose                                                                        | Pre-config |
| ------------------------- | ------------------------------------------------------------------------------ | ---------- |
| `Templater`               | Insert page templates with frontmatter into the right folders.                 | yes (`.obsidian/plugins/templater-obsidian/data.json` already points to `_system/templates` and binds folder templates) |
| `Obsidian Web Clipper`    | Browser extension. Clip articles directly into `domains/<X>/raw/articles/`.    | configure manually after install |
| `Marp`                    | (optional) Render markdown to slide decks for syntheses you want to present.   | n/a |
| `Smart Connections`       | (optional, future) Embedding-based similarity search. Add only when wiki > ~300 pages and `index.md` no longer suffices. | n/a |

After installing Templater:
1. Settings → Templater → Template folder location → confirm `_system/templates`.
2. Settings → Templater → Folder Templates → confirm the bindings are
   present (one per page type, auto-loaded from the pre-written
   `data.json`). Run `ls _system/templates/*.md | wc -l` — there should
   be one template per page type listed in [`AGENTS.md`](../AGENTS.md) §3.
3. Reload the vault if templates do not appear.

## Web Clipper configuration

After installing the browser extension, open its settings and pick
**one** of the two postures below depending on where you typically
capture from.

### Posture A — desktop-only capture, routing-confident

You clip exclusively from a laptop where you already know which
domain each article belongs to.

- Vault: `<your vault name>` (the name you used to add this folder
  to Obsidian).
- Default note location: `domains/<your-default-domain>/raw/articles`
  (override per domain when clipping).
- Filename template: `{{date|YYYY-MM-DD}}-{{title|slug}}`.
- Per-domain overrides in "Settings → Templates": one rule per L2
  you maintain, each routing to `domains/<X>/raw/<bucket>/`.

### Posture B — mixed-device capture (recommended for mobile-heavy use)

You also capture from a phone, where Obsidian Mobile doesn't run
the validator and routing-correctness needs a desktop session anyway.

- Vault: same.
- Default note location: **`inbox/`** — the un-routed-material
  staging area (L1 §2.4). A weekend `process-inbox` desktop session
  will `git mv` each clip into the right `domains/<X>/raw/<bucket>/`.
- Filename template: `{{date|YYYY-MM-DD}}-{{title|slug}}`. For CJK
  titles, use `{{title}}` (no slug filter) — Web Clipper's slug
  filter romanises CJK unreliably; see
  [`docs/CJK-WORKFLOW.md`](../docs/CJK-WORKFLOW.md) §6.
- No per-domain overrides needed; the triage happens at
  `process-inbox` time, not capture time.

Posture B trades a small daily latency (un-routed material sits in
`inbox/` for hours-to-days) for capture friction → 0. Most users
who carry a phone end up here.

## Cursor Agent setup

In Cursor:
1. Open this folder as a workspace.
2. Cursor will pick up `/AGENTS.md` automatically; no further action needed.
3. The five operations are invoked via natural language in the chat:
   - `ingest <relative-path>`
   - `query <question>`
   - `lint` or `lint --domain <X>`
   - `process-inbox`
   - `promote <outputs/qa/...>`
4. Sub-prompts in `_system/prompts/` are pulled in as needed via `@`-mentions
   when you want explicit control.

## When to revisit the indexing layer

The current navigation layer is Dataview-driven (per [`AGENTS.md`](../AGENTS.md)
§4.1 and §7). Re-evaluate switching to Obsidian's first-party `.base`
files when **either** of the following triggers fires:

- Any single Dataview block in an `index.md` exceeds ~50 rendered rows
  (manual eyeball check; if a Dataview table now scrolls a screen, the
  `.base` table view is a better UX).
- Reading-view rendering of `index.md` becomes noticeably slow (>1s
  visible delay between opening the file and seeing the rendered
  blocks). At that scale, Dataview's per-render computation cost is
  the bottleneck and `.base` materialisation wins.

Until one of those fires, do not migrate — Dataview is more diff-friendly
in git history and the LLM operates on its source markdown more
naturally.

## Sanity check

Open `index.md` in Obsidian. The "Recent global activity" Dataview block
should show the bootstrap log entries. Click into
a per-domain `index.md` — Dataview blocks should render row counts
for the buckets that L2 expects (e.g. `raw/sessions`, `wiki/analyses`).
`wiki/syntheses` will likely show `0` until your first cross-source
essay is filed; that is the intended steady state per
[`AGENTS.md`](../AGENTS.md) §3.

## Engineering hooks

Mechanised guards for the L1 red lines (`AGENTS.md` §6) live in the
[`wikilint`](wikilint/) package and the pre-commit hook that drives it.

- **One-time hook install**: `git config core.hooksPath _system/hooks`
  This routes git through the in-repo hooks directory instead of the
  default `.git/hooks/`, so the pre-commit guard travels with the
  vault and stays in sync across clones. The hook is pure stdlib —
  no `pip install` required.
- **Manual validation**: at any time, run
  `python -m wikilint --all` to lint the full repo, or
  `python -m wikilint path/to/file.md …` for a subset. CI runs the
  same command via the installed `wikilint` console script.
- **Available rules**: `python -m wikilint rules` prints every rule
  with its stable ID. Use `--select AGENTS003` or
  `--ignore AGENTS006` to control which run.
- **Output formats**: `--format=text` (default), `--format=json`
  (machine-readable), `--format=github` (workflow annotations).

### Rule reference

| ID         | Rule                             | Anchor          |
| ---------- | -------------------------------- | --------------- |
| AGENTS001  | raw-immutability                 | AGENTS.md §6    |
| AGENTS002  | log-append-only                  | AGENTS.md §6    |
| AGENTS003  | frontmatter-required-keys        | AGENTS.md §3    |
| AGENTS004  | frontmatter-type-allowed         | AGENTS.md §3    |
| AGENTS005  | analysis-sources-cardinality     | AGENTS.md §3.1  |
| AGENTS006  | wikilink-resolvable              | AGENTS.md §4    |
| AGENTS007  | operation-writes-within-scope    | AGENTS.md §2.0  |

Schema docs (`AGENTS.md`, `_system/`, `attic/`, `inbox/`) are excluded
from wikilink checks because they contain `[[<placeholder>]]`
examples by design. `outputs/` is also excluded — it holds runtime
artifacts that point at wiki pages but never receive inbound links.

### Optional stricter parsing

The default frontmatter parser is stdlib-only — handles the YAML
subset templates use, no dependencies. For full YAML (nested maps,
anchors), install the `strict` extra:

```bash
pip install -e ".[strict]"   # pulls in pyyaml
```

CI runs in `[strict]` mode; the pre-commit hook does not, so the
hook stays fast on every commit.

## Privacy: encrypt sensitive `raw/` with git-crypt

If any of your L2s contains sensitive material (therapy transcripts,
medical records, NDA-bound meeting notes, etc.), encrypt that L2's
`raw/` tree with `git-crypt` before pushing to any remote.

1. Install: `brew install git-crypt gnupg` (and ensure you have a GPG key).
2. Edit `_system/scripts/setup_encryption.sh` to list the path(s) you
   want to encrypt (it defaults to `domains/<your-sensitive-domain>/raw/**`).
   Then run: `bash _system/scripts/setup_encryption.sh`
   It is idempotent: it appends the `.gitattributes` filter rule if
   absent and prints the next manual steps (`git-crypt init`,
   `git-crypt add-gpg-user <your@email>`, `git-crypt status -e` to
   verify).
3. **Cold backup remote**: add a second remote on a different provider
   (Codeberg / GitLab / a self-hosted forge) and push periodically:
   `git remote add backup git@codeberg.org:<you>/<vault>.git && git push backup --all`.
   Keeping the backup on a different provider shields against
   single-vendor account loss; encryption ensures the cold remote
   can't read raw.
4. **Key hygiene** — never commit `.git-crypt/keys/default`. Store the
   GPG private key on a hardware token (YubiKey) or in a secrets
   manager; treat loss of the private key as loss of the encrypted
   history.
