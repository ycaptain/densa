# Setup

> What this doc adds beyond
> [`README.md` §"Quickstart"](../README.md#quickstart): the Obsidian
> plugin matrix, Web Clipper defaults, non-Cursor agents, encryption
> for private / sensitive material, disabling the hook, what CI runs,
> and the day-one domain decision tree.
>
> Conceptual day-to-day usage lives in [`../GUIDE.md`](../GUIDE.md);
> long-form rationale for each decision lives in
> [`design/design-rationale.md`](design/design-rationale.md).

## Required (everyone) — pre-commit hook + manual validation

Prereqs (fork + clone + `git config core.hooksPath _system/hooks`)
are covered in
[`../README.md` §"Quickstart"](../README.md#quickstart). The hooks
are **pure stdlib** (no `pip install` required), and that single
`core.hooksPath` wires both of them:

- **pre-commit** runs every rule except AGENTS007 — the commit
  message doesn't exist yet at that stage (git rewrites
  `.git/COMMIT_EDITMSG` only after pre-commit passes).
- **commit-msg** re-runs AGENTS007 (operation-writes-within-scope)
  against the real message file git hands it as `$1`.

> **Python ≥ 3.10 required** for the `densa` CLI (validator,
> `init`, `doctor`, `stats`) — the floor `pyproject.toml` pins.
> Fresh macOS / Linux often ship only the `python3` launcher, so
> this doc writes `python3 -m densa` throughout; substitute
> `python` if that is what your platform calls 3.10+.

Manual validation any time:

```bash
PYTHONPATH=_system python3 -m densa --all
```

The 12 enforced rules (`AGENTS001`–`AGENTS012`) are documented at
[`reference/rules-registry.md`](reference/rules-registry.md);
`python3 -m densa rules` prints the live registry. For vulnerability
reporting see [`../.github/SECURITY.md`](../.github/SECURITY.md).

---

## Recommended (Obsidian users)

### Do I need Obsidian?

No. The wiki is plain markdown with YAML frontmatter and
`[[wikilink]]` syntax — any editor works. Obsidian adds three things
this skill pack benefits from: **Dataview** (powers the dynamic blocks
in every `index.md`; without it, indices fall back to static markdown
— still readable, just no auto-refresh), **Templater** (drops the
right frontmatter for each page type), and **Graph view** (makes the
link structure visible). Use VSCode or Neovim if you prefer; the LLM
agent doesn't care about the editor.

When using Obsidian, install these plugins:

| Plugin                    | Required? | Purpose                                                        | Pre-config |
| ------------------------- | --------- | -------------------------------------------------------------- | ---------- |
| **Dataview**              | required  | Powers dynamic blocks in every `index.md`. Enable "JavaScript Queries" in settings (needed for `dataviewjs`). | n/a |
| **Templater**             | recommended | Insert page templates with frontmatter into the right folders.   | `.obsidian/plugins/templater-obsidian/data.json` already points to `_system/templates`; reload vault if templates don't appear |
| **Obsidian Web Clipper**  | recommended | Browser extension. Clip articles directly into the vault.       | configure manually after install (see below) |
| **Marp**                  | optional  | Render markdown to slide decks for syntheses you want to present. | n/a |
| **Smart Connections**     | optional  | Embedding-based similarity search. Add only when wiki > ~300 pages and `index.md` no longer suffices. | n/a |

### Graph view

Out of the box Obsidian graphs **every** markdown file — scaffolding
(`_system/`, `attic/`, `outputs/`), immutable `raw/` sources, and the
append-only logs (a mature domain `log.md` carries hundreds of
outgoing links) bury the wiki pages in a grey hairball. Generate a
tuned config instead:

```bash
# Run while Obsidian is CLOSED — it rewrites .obsidian/*.json on exit.
PYTHONPATH=_system python -m densa graph-config
# Vendored checkouts inside the vault? Exclude them too:
PYTHONPATH=_system python -m densa graph-config --exclude share/
```

What it writes (`.obsidian/graph.json`):

- **Filter**: only the wiki graph — `_system/`, `attic/`, `inbox/`,
  `outputs/`, `raw/`, every `log.md`, and the schema docs are
  excluded; unresolved ghosts hidden.
- **Color groups**: one color per `domains/<X>/`, plus gold for
  `index.md` landmarks and pink for `syntheses/` (the highest-value
  compiled pages). Editable later in the graph settings panel.
- **Forces**: tuned for a few-hundred-node graph (labels fade in
  earlier, tighter link distance).

Two habits make the graph actually useful:

1. **The global graph is a domain map.** Open it to see cluster
   shapes, orphan pockets, and cross-domain bridges — not to navigate.
2. **Navigate with the local graph.** On any wiki page run *Open
   local graph*, set depth to 2 and enable incoming + outgoing links.
   That gives "what is connected to what I'm reading" without the
   other 300 nodes. Save the layout with the core Workspaces plugin
   if you use it daily.

Two related hygiene tools: `densa stats` reports graph health
(ghost-node backlog, hub degrees, orphans), and
`python _system/scripts/fix_obsidian_links.py` rewrites
bucket-relative wikilinks Obsidian can't resolve (AGENTS013).

### Web Clipper defaults

Set "Default note location" to `inbox/`; filename template
`{{date|YYYY-MM-DD}}-{{title|slug}}` (drop the `|slug` filter for
CJK titles — Web Clipper romanises CJK unreliably; see
[`cjk-workflow.md` §"Known limitations"](cjk-workflow.md#6-known-limitations)).
Routing happens at
`process-inbox` time, not capture time, so no per-domain overrides
are needed.

### Can I run this with a non-Cursor agent?

Yes. The prompts and schema are agent-agnostic. The skill pack is
tested with Cursor and Claude Code, but anything that can read
`AGENTS.md`, follow markdown templates, and run shell commands works.
The required file-system tools per operation are read / write /
`git mv` / `git diff` — no exotic capabilities. The optional
Claude Code slash commands (`/ingest`, `/query`, `/lint`, …) ship
under [`../integrations/claude-code/`](../integrations/claude-code/).

### My vault is mostly in Chinese — anything special?

Yes. See [`cjk-workflow.md`](cjk-workflow.md). The schema is
language-neutral; the conventions for slugs, aliases, commit
messages, and lint-report language are documented separately so a
CJK-first vault stays internally consistent.

---

## Privacy — sensitive material

Yes, this skill pack works with private / sensitive material, with
care. **Treat encryption as part of setup — do not push to any
remote until git-crypt is verified working.** Outline:

1. Install: `brew install git-crypt gnupg` (macOS; use your package
   manager elsewhere).
2. Edit [`../_system/scripts/setup_encryption.sh`](../_system/scripts/setup_encryption.sh)
   and uncomment one entry in `ENCRYPT_PATHS` per tree you want
   encrypted (e.g. `"domains/<your-sensitive-domain>/raw/**"`).
   The script ships with all defaults commented out — it cannot
   silently encrypt anything you didn't pick.
3. Run `bash _system/scripts/setup_encryption.sh`. It appends the
   `.gitattributes` filter rule if absent and prints the next manual
   steps (`git-crypt init`, `git-crypt add-gpg-user <your@email>`,
   `git-crypt status -e` to verify).
4. Set up a **cold backup remote on a different provider** (Codeberg
   / GitLab / self-hosted forge). Different-provider backup shields
   against single-vendor account loss; encryption ensures the cold
   remote can't read raw.
5. **Key hygiene**: never commit `.git-crypt/keys/default`. Store the
   GPG private key on a hardware token (YubiKey) or in a secrets
   manager. Treat loss of the private key as loss of the encrypted
   history.

The psychology showcase demonstrates the two privacy postures
(public-shareable vs private-repo) in its
[§"Privacy posture"](../examples/showcases/psychology/AGENTS.md#privacy-posture).
For vulnerability reporting see [`../.github/SECURITY.md`](../.github/SECURITY.md).

---

## Disabling the pre-commit hook

```bash
# One-shot bypass — skips both the pre-commit and commit-msg hooks
# (e.g. sanctioned transcription sweep):
git commit --no-verify -m "..."

# Permanently disable on this clone:
git config --unset core.hooksPath
```

Re-enable any time by re-running
`git config core.hooksPath _system/hooks`. CI still runs the
validator on every push, so disabling locally doesn't let red-line
violations land in `main`.

---

## What does CI run?

A single workflow at `.github/workflows/ci.yml` with two jobs:

- **`validate`** runs `densa --all` on every push and PR, plus
  `densa --diff origin/<base>` (staged rules over the PR range) on
  PRs. Enforces the L1 red lines, the universal frontmatter contract,
  wikilink resolvability, and AGENTS001–012. This is the gate every
  PR must clear.
- **`tests`** runs `pytest`, `ruff check .`, and `mypy --strict`
  across Python 3.10/3.11/3.12. Together with `validate` it covers
  schema correctness and the validator's own code health.

---

## Choosing or replacing the default domain

This skill pack ships **one active default L2 + two opt-in showcases**:

| L2 | Where | Schema | Weight | Reach for it if you... |
|---|---|---|---|---|
| `research-papers/` | `domains/` (default active) | **v2** | light | read academic papers / technical articles |
| `workspace/` | `examples/showcases/` (opt-in) | v1 (migrate before use) | medium | run / manage projects with stakeholders |
| `psychology/` | `examples/showcases/` (opt-in) | v1 (migrate before use) | heavy | track therapy / inner work (re-read Privacy posture before real use) |

Decision tree on day-one:

```
Will you ingest research-paper material this month?
├── Yes  → keep domains/research-papers/ as-is; replace its raw/ + wiki/
│         with your own content (don't try to "build on" the worked
│         example — start fresh)
├── Maybe later → keep the L2 schema (the AGENTS.md is reusable),
│                 but delete the worked-example raws + wikis
└── No  → delete the entire domains/research-papers/ directory
```

**Pitfalls.** Don't keep all three L2s active in `domains/` — each
showcase brings 600-2000 lines of fictional content that the LLM
filters on every `lint` / wikilink walk. Default to one active L2;
copy showcases over only when you actively need them. Don't fork the
schema before your first 5 *real* ingests either — let the pain
points teach you which fields to add or remove.

### Adopting a showcase (`workspace` or `psychology`)

```bash
cp -r examples/showcases/workspace domains/workspace
python _system/scripts/migrate_02_karpathy_vocab.py --apply   # v1 → v2
git rm -r domains/workspace/raw/* domains/workspace/wiki/*
# Add empty bucket .gitkeeps under raw/<bucket>/ and wiki/<type>/
WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "chore(domains): adopt workspace L2 from showcase"
```

Pair the commit with a `## [YYYY-MM-DD] maintenance | …` entry in
`log.md` per
[`../AGENTS.md` §"Operation writes"](../AGENTS.md#20-operation-writes-machine-enforced-via-agents007).

### Removing the default domain entirely (you don't read papers)

```bash
git rm -r domains/research-papers/
# Remove the bullet for research-papers from /index.md
# Append a maintenance entry to /log.md
WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "chore(domains): remove default example research-papers"
```

### Vault-local domain prompts

Domain analysis sub-prompts shipped by upstream live in
`_system/prompts/domains/`. That directory is **upstream-owned**: if
your vault tracks upstream by syncing `_system/` wholesale (e.g.
`rsync -a --delete <upstream>/_system/ _system/`), anything you place
there is overwritten or deleted on the next sync.

To carry a domain prompt of your own — for a domain upstream ships no
prompt for, or to replace a shipped prompt wholesale — put it in the
domain folder instead:

```
domains/<X>/prompts/<X>-<bucket>-analysis.md
```

`ingest` resolves sub-prompts in this order (first match wins; see
[`../_system/prompts/ingest.body.md`](../_system/prompts/ingest.body.md)
step 4.5):

1. `domains/<X>/prompts/<X>-*-analysis.md` (vault-local)
2. `_system/prompts/domains/<X>-*-analysis.md` (shipped)

Notes:

- Vault-local prompts are excluded from the wikilink graph (they
  contain `[[<placeholder>]]` examples by design, same as
  `_system/prompts/`).
- Commit-wise they get the same treatment as a domain's `AGENTS.md`:
  no operation prefix covers them, so edits ride a
  `WIKI_ALLOW_CROSS_SCOPE=1` commit paired with a
  `## [YYYY-MM-DD] maintenance | …` entry in `log.md`.
- Prefer a vault-local prompt over stretching the L2: procedural
  pipelines (multi-stage drafting, critique checklists, worked
  examples) belong in a prompt; schema and invariants belong in the
  L2. When the two disagree, AGENTS still wins.

### Renaming a domain after committing

A deliberate human-approved cascade (wikilinks propagate). Mechanics:
`git mv domains/<old>/ domains/<new>/`, sweep the wiki for
`domains/<old>` references, `python3 -m densa --all` to confirm zero
dangling links, update `/index.md`, commit with bypass + log entry.

Standing up your own L2 from scratch is covered by the bootstrap
prompt at [`bootstrap.md`](bootstrap.md).
The longer essay on persona-before-schema, page-type subsetting, and
schema-by-dogfood lives in
[`design/design-rationale.md` §"How to design your own L2"](design/design-rationale.md#how-to-design-your-own-l2).
