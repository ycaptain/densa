# Setup

One-time setup after cloning. The vault is fully usable from your AI
coding agent *without* any of this — these steps either harden the
schema guarantees (hooks, encryption) or improve the Obsidian editing
UX (plugins). Take them in this order.

> **Used `densa init`?** It already wired the pre-commit hook and
> set up the `upstream` remote. Skip ahead to *Obsidian plugins*.
> If you cloned manually, start here.

## ⚙️ Engineering hooks (do this first)

The pre-commit hook turns the L1 red lines from prose into a gate.
Skip this step and the vault still works — but a stray bad commit
won't be caught until CI.

```bash
git config core.hooksPath _system/hooks
git config --get core.hooksPath        # should print: _system/hooks
```

That's it. The hook is pure stdlib — **no `pip install` needed**. A
silent misconfiguration here means months of unguarded commits, so
the verify step matters.

### Manual validation any time

```bash
PYTHONPATH=_system python -m densa --all
```

The `PYTHONPATH` trick mirrors what the pre-commit hook does, so it
works without `pip install`. If you've run `pip install -e ".[strict]"`
you can drop the prefix and run `densa --all`. Contributors editing
the validator typically use `nox -s lint` (full developer gate:
`nox -s check`); see [`CONTRIBUTING.md`](../CONTRIBUTING.md).

### Rule reference

`python -m densa rules` prints the live registry — that's the
source of truth. The mirror below is for human reading. Pin the ID
(never the name) in any suppression comment or commit message.

| ID         | Rule                             | Anchor          | Severity     |
| ---------- | -------------------------------- | --------------- | ------------ |
| AGENTS001  | raw-immutability                 | AGENTS.md §6    | error        |
| AGENTS002  | log-append-only                  | AGENTS.md §6    | error        |
| AGENTS003  | frontmatter-required-keys        | AGENTS.md §3    | error        |
| AGENTS004  | frontmatter-type-allowed         | AGENTS.md §3    | error        |
| AGENTS005  | analysis-sources-cardinality     | AGENTS.md §3.1  | error        |
| AGENTS006  | wikilink-resolvable              | AGENTS.md §4    | error / warn |
| AGENTS007  | operation-writes-within-scope    | AGENTS.md §2.0  | error        |
| AGENTS008  | last-validated-fresh             | AGENTS.md §3.3  | warning      |
| AGENTS009  | compiled-against-current         | AGENTS.md §3.2  | warning      |

Use `--select AGENTS003` or `--ignore AGENTS006` to control which
rules run. Output formats: `--format=text` (default), `--format=json`,
`--format=github` (workflow annotations).

Schema docs (`AGENTS.md`, `_system/`, `attic/`, `inbox/`) are excluded
from wikilink checks because they contain `[[<placeholder>]]` examples
by design. `outputs/` is also excluded — it holds runtime artifacts
that point at wiki pages but never receive inbound links.

### Optional stricter parsing

The default frontmatter parser is stdlib-only — it handles the YAML
subset templates use, no dependencies. For full YAML (nested maps,
anchors), install the extra and opt in explicitly:

```bash
pip install -e ".[strict]"
DENSA_STRICT=1 densa --all
```

The default stays stdlib-only regardless of whether pyyaml is on PATH
— the validator no longer hot-swaps backends silently, so the same
vault behaves identically across machines. CI runs with
`DENSA_STRICT=1`; the pre-commit hook does not, so the hook stays
fast on every commit.

### 🩹 Disabling the hook

```bash
# One-shot bypass (e.g. sanctioned transcription sweep):
git commit --no-verify -m "..."

# Permanently disable on this clone:
git config --unset core.hooksPath
```

Re-enable any time by re-running
`git config core.hooksPath _system/hooks`. The validator still runs in
CI on every push, so disabling locally doesn't let red-line violations
land in `main`.

---

## 🔌 Obsidian plugins (UX layer)

The wiki itself doesn't need Obsidian — any markdown editor works. But
if you do open the vault in Obsidian, install one required plugin and
a few recommended ones to make daily use pleasant.

### Required

- **Dataview** — powers the dynamic blocks in every `index.md`. Enable
  "JavaScript Queries" in its settings (needed for `dataviewjs`).

### Recommended

| Plugin                    | Purpose                                                                        | Pre-config |
| ------------------------- | ------------------------------------------------------------------------------ | ---------- |
| **Templater**             | Insert page templates with frontmatter into the right folders.                 | yes — `.obsidian/plugins/templater-obsidian/data.json` already points to `_system/templates` and binds folder templates |
| **Obsidian Web Clipper**  | Browser extension. Clip articles directly into the vault.                      | configure manually after install (see below) |
| **Marp**                  | Render markdown to slide decks for syntheses you want to present.              | n/a |
| **Smart Connections**     | Embedding-based similarity search. Add only when wiki > ~300 pages and `index.md` no longer suffices. | n/a |

After installing Templater:

1. Settings → Templater → Template folder location → confirm
   `_system/templates`.
2. Settings → Templater → Folder Templates → confirm the bindings are
   present (auto-loaded from the pre-written `data.json`).
3. Reload the vault if templates don't appear.

### Web Clipper — default to inbox

Open Web Clipper's settings and use this configuration. It's optimised
for mobile capture (where you can't browse domains comfortably anyway).

- **Vault:** the name you used to add this folder to Obsidian.
- **Default note location:** `inbox/` — the un-routed staging area
  ([`/AGENTS.md`](../AGENTS.md) §2.4). A weekend `process-inbox`
  desktop session will `git mv` each clip into the right
  `domains/<X>/raw/<bucket>/`.
- **Filename template:** `{{date|YYYY-MM-DD}}-{{title|slug}}`. For
  CJK titles, use `{{title}}` (no slug filter) — Web Clipper's slug
  filter romanises CJK unreliably; see
  [`docs/CJK-WORKFLOW.md`](../docs/CJK-WORKFLOW.md) §6.

Routing happens at `process-inbox` time, not capture time, so no
per-domain overrides are needed. This trades a small daily latency
(un-routed material sits in `inbox/` for hours-to-days) for capture
friction → 0.

> **Clipping only from a laptop where you know the destination
> domain?** Set "Default note location" to
> `domains/<your-default-domain>/raw/articles` and add per-domain
> override rules in "Settings → Templates" (one per L2). Posture B
> above is the default recommendation; this is the desktop-only
> variant.

### Cursor / Claude Code / Codex setup

Open the vault as a workspace. The agent picks up `/AGENTS.md`
natively; no further action. The five operations are invoked via
natural language in the chat:

- `ingest <relative-path>`
- `query <question>`
- `lint` or `lint --domain <X>`
- `process-inbox`
- `promote <outputs/qa/...>`

Sub-prompts in `_system/prompts/` are pulled in via `@`-mentions when
you want explicit control.

---

## 🔒 Privacy: encrypt sensitive raw/ with git-crypt

If any of your L2s contains material you wouldn't post in a public
thread — therapy transcripts, medical records, NDA-bound meeting
notes — encrypt that L2's `raw/` tree with
[git-crypt](https://github.com/AGWA/git-crypt) **before pushing to any
remote**.

```bash
brew install git-crypt gnupg          # macOS; use your package manager elsewhere
```

Then:

1. Edit
   [`scripts/setup_encryption.sh`](scripts/setup_encryption.sh) and
   uncomment a path in the `ENCRYPT_PATHS` array for each tree you
   want encrypted (e.g. `"domains/psychology/raw/**"`). The script
   ships with all defaults commented out — it cannot silently encrypt
   anything you didn't pick. Running it with an empty array exits
   with `No paths configured.` and instructions.

2. Run the script:

   ```bash
   bash _system/scripts/setup_encryption.sh
   ```

   It's safe to re-run: it appends the `.gitattributes` filter rule
   if absent and prints the next manual steps (`git-crypt init`,
   `git-crypt add-gpg-user <your@email>`, `git-crypt status -e` to
   verify).

3. Set up a **cold backup remote on a different provider**. Add a
   second remote (Codeberg / GitLab / a self-hosted forge) and push
   periodically:

   ```bash
   git remote add backup git@codeberg.org:<you>/<vault>.git
   git push backup --all
   ```

   Different-provider backup shields against single-vendor account
   loss; encryption ensures the cold remote can't read raw.

4. **Key hygiene:** never commit `.git-crypt/keys/default`. Store the
   GPG private key on a hardware token (YubiKey) or in a secrets
   manager. Treat loss of the private key as loss of the encrypted
   history.

---

## When to revisit indexing

The navigation layer is Dataview-driven today
([`AGENTS.md`](../AGENTS.md) §4.1 and §7). Re-evaluate switching to
Obsidian Bases (`.base` files) when **either** of these fires:

- Any single Dataview block in an `index.md` exceeds ~50 rendered rows
  (manual eyeball — if a Dataview table now scrolls a screen, the
  `.base` table view is a better UX).
- Reading-view rendering of `index.md` becomes noticeably slow (>1s
  visible delay between opening the file and seeing the rendered
  blocks). At that scale, Dataview's per-render computation is the
  bottleneck and `.base` materialisation wins.

Until one fires, don't migrate — Dataview is more diff-friendly in
git history and the LLM operates on its source markdown more
naturally.

## Sanity check

Open `index.md` in Obsidian. The "Recent global activity" Dataview
block should show your bootstrap log entries. Click into a per-domain
`index.md` — Dataview blocks should render row counts for the buckets
that L2 expects (e.g. `raw/sessions`, `wiki/analyses`). For **a new
L2 you stood up yourself**, `wiki/syntheses` will likely show `0`
until your first cross-source essay; that's the intended steady state
per [`AGENTS.md`](../AGENTS.md) §3. The shipped example L2s already
contain syntheses, so their counts won't be zero.
