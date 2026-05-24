---
type: guide
domain: meta
created: 2026-05-20
updated: 2026-05-23
status: active
compiled_against: 1
---

# Example domains — choose, adapt, remove, or replace

> A practical guide for the *first 30 minutes* with the
> Densa template. Three example L2 domains ship under
> `domains/`. They're worked examples, not endorsements — most users
> keep one or two and delete the rest before their first real ingest.
> This doc helps you decide, then walks you through the mechanics.

## 📦 What ships, and what each example is *for*

| Example L2 | Weight | Demonstrates | Reach for it if you... |
|---|---|---|---|
| [`research-papers/`](../domains/research-papers/) | light | Minimum viable L2 — 6 page types, one ingest flow, focused lint rules. Ships with a 5-paper LLM-tutoring evidence arc (3 real RCTs + 1 real review + 1 synthesised SAE stand-in) | read academic papers / technical articles and want a queryable record of mechanism + evidence + open questions |
| [`workspace/`](../domains/workspace/) | medium | Multi-stakeholder narrative — meetings, decisions, entity tracking, cross-raw pattern detection (both a negative arc and a positive engineering-decision pattern). Ships with a multi-raw Q2 platform-migration + cross-decision retrospective | run / manage projects with stakeholders and want to track *why decisions actually happened* (not just task lists) |
| [`psychology/`](../domains/psychology/) | heavy (worked example) | The deepest L2 schema we know how to specify — privacy postures, ASR correction, biopsychosocial framing, multi-modal handling. Ships with a 5-raw (4 therapy + 1 psychiatry) six-week father-grief arc → 25 wiki pages: 5 analyses, 3 patterns, 2 themes, 4 concepts, 3 entities, 2 frameworks, 1 protocol, 2 questions, 3 syntheses | track therapy / inner work over years; **note the synthesised-demo nature of the raw sessions** (each raw begins with an HTML banner declaring it is not a real session); clinical adopters must re-read L2 AGENTS.md §"Privacy posture" before ingesting real material |

`research-papers/` is the best starting point for designing your own
L2 — short AGENTS.md, focused page-type set, and a worked cross-paper
synthesis showing how the graph of analysis → concept → framework →
question compounds.

> **The three example domains are not exhaustive.** They cover three
> rough quadrants (academic reading / collaborative work /
> privacy-sensitive personal material). Your domain may not fit any of
> them — that's normal. Skip ahead to §4.

## 🤔 How to decide what to keep

A short decision tree:

```
Will you ingest material for this kind of work this month?
├── Yes  → keep the L2 as-is; replace its `raw/` and `wiki/` with
│         your own content per §3 (don't try to "build on" the
│         worked example — start fresh)
├── Maybe later → keep the L2 schema (the AGENTS.md is reusable),
│                 but delete the worked-example raws + wikis per §3
└── No  → delete the entire `domains/<X>/` directory per §3
```

### Pitfalls

- **"Keep them all just in case."** Each example L2 brings
  ~600-2000 lines of fictional content into your repo. After three
  months of your own ingests, that's noise the LLM has to filter
  through every time it runs `lint` or follows a wikilink. Delete
  aggressively.
- **"Let me read all three L2 AGENTS.md files first."** You don't
  need to. The example you're most likely to keep is the one whose
  name you reacted to with *"oh, that's me"*. The others can be
  evaluated in 30 seconds: read the first 20 lines of the L2
  AGENTS.md (Persona + Folder layout). If the persona doesn't sound
  like the synthesiser you want, delete.
- **"I'll fork the schema and tweak it before my first ingest."**
  L2 schemas evolve fastest in the first 5-10 ingests of *real*
  content. Premature schema changes (before you've felt the schema's
  friction against your own raws) almost always over-engineer the L2.
  Keep the schema as-is for your first 5 ingests; let the pain points
  teach you which fields to add or remove.

## 🧹 Removing an example domain you don't want

The repo's red lines (`/AGENTS.md` §6) forbid wiki-page deletion *for
pages that are part of your active knowledge base*. **The
worked-example domains are explicitly NOT part of your knowledge
base** — they're starter scaffolding. Removing them is a one-time
clean operation, not a wiki edit.

### Option A — remove the entire domain (recommended)

```bash
git rm -r domains/<X>/
```

In the same commit:

1. Remove the bullet for `<X>` from `/index.md`.
2. Skim `/log.md` for historical worked-example ingest entries
   referencing `<X>`. Per `/AGENTS.md` §6, log entries are append-only
   — **leave them in place** as historical record. The new
   maintenance entry below documents the removal.
3. Append a maintenance entry to `/log.md`:

   ```
   ## [<today>] maintenance | removed example domain <X>
   - Removed: `domains/<X>/` (AGENTS.md, index.md, log.md, raw/**, wiki/**)
   - Why: <one line>
   - Bypass used: WIKI_ALLOW_CROSS_SCOPE=1 (touches domains/**)
   ```

4. Commit with bypass (since `(no prefix)` can't write `domains/**`):

   ```bash
   WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "chore(domains): remove example domain <X>"
   ```

### Option B — keep the L2 schema but drop the worked content

```bash
git rm -r domains/<X>/raw/
git rm -r domains/<X>/wiki/
mkdir -p domains/<X>/raw/<bucket-1>
mkdir -p domains/<X>/wiki/<type-1>
touch domains/<X>/raw/<bucket-1>/.gitkeep
touch domains/<X>/wiki/<type-1>/.gitkeep
```

Commit with bypass. Edit `domains/<X>/log.md` to leave just the
preamble (drop the worked-example ingest entry).

### Wikilink safety check

After removal, run:

```bash
python -m densa --all
```

If the removed domain was referenced by an inbound wikilink, `AGENTS006
wikilink-resolvable` will surface it. The most common case is
`/index.md` — update that one bullet. **None** of the shipped example
domains link to each other; cross-domain wikilinks happen only when
you create them yourself.

## 🌱 Standing up your own L2 from scratch

Two paths, depending on how much help you want.

### Path 1 — Use the bootstrap prompt (recommended for first L2)

Paste [`docs/bootstrap-prompt.md`](bootstrap-prompt.md) into Cursor /
Claude Code / Codex. The agent interviews you (~5 questions: domain
name, persona, materials, synthesis goals), then emits a complete L2
scaffold — `AGENTS.md`, `index.md`, `log.md`, and folder structure
under `raw/` and `wiki/`. Review, commit with the bypass, drop your
first raw.

### Path 2 — Hand-roll from an existing example

Pick the closest example (usually `research-papers/` for light or
`workspace/` for medium):

```bash
cp -r domains/research-papers/ domains/<your-new-X>/
git rm domains/<your-new-X>/raw/*
git rm domains/<your-new-X>/wiki/*
```

Then edit `domains/<your-new-X>/AGENTS.md`: replace the **Persona**
section (this matters most — persona shapes every ingest), adjust the
allowed **page types** (subset of `/AGENTS.md` §3's enum), the folder
layout, the L2-required frontmatter, the **ingest flow** (numbered
steps the LLM follows), and the **domain-specific lint rules**.
Update `/index.md` to add a bullet, then commit with bypass:

```bash
WIKI_ALLOW_CROSS_SCOPE=1 git commit -m "chore(domains): scaffold <your-new-X> L2"
```

Paired log.md maintenance entry per `/AGENTS.md` §2.0.

### Designing the L2 itself

A few load-bearing principles, drawn from the three worked examples:

- **Persona before schema.** The Persona section drives the LLM's
  voice on every ingest. A precise persona ("careful science-historian
  who reads ML papers to extract mechanism") produces much better
  synthesis than a generic one ("an AI assistant").
- **Page-type subset, not full enum.** L1 §3 lists 18 page types.
  Pick the 4-8 you actually need. Adding a page type later is cheap;
  removing one after you've used it is expensive (deprecation chain).
- **Folder = type, mostly.** One folder per page type, named after
  the type. The 3 examples all follow this. Exceptions need
  justification in the L2 AGENTS.md.
- **L2-required frontmatter sparingly.** Each required field is a tax
  the LLM pays on every ingest. Add fields whose absence would produce
  a real bug ("we forgot to record session date"); skip fields whose
  absence is just inconvenient.
- **Ingest flow as numbered steps.** Future-you reads this when the
  LLM does something wrong on the 47th ingest. One action per step.
- **Domain-specific lint rules** are the closing safety net — what
  should `lint` flag that L1's universal checks won't catch?

If you're hand-rolling and the L2 ends up >300 lines, that's a signal
you may be over-engineering. The `research-papers/` L2 is ~135 lines
and is fully production-quality; the `workspace/` L2 is ~250 lines.
Anything bigger than `psychology/`'s ~280 lines should make you pause
and ask which fields are doing real work.

## 📈 After your first 5 ingests

Re-read your L2 AGENTS.md. You'll find:

- Required fields you've been omitting → either start enforcing or
  delete from the schema.
- Optional fields you keep adding by hand → promote to required.
- Folder buckets you never use → delete.
- Ingest steps the LLM keeps skipping → rewrite them to be more
  specific, or accept that the step was over-prescribed.

This is the **schema-by-dogfood** loop. The L2 you ship in week one
is a draft; the L2 you have in month three is the one that actually
fits.

## Common questions

**Can I have multiple L2s active at the same time?**

Yes. The shipped examples have always co-existed. The validator
handles cross-domain ingests fine. Each L2 owns its own ingest flow,
lint rules, and frontmatter; conflicts between L2s aren't possible
because each L2 only governs inside `domains/<X>/`.

**Can I have nested L2s (sub-domains)?**

No — the architecture doesn't support `domains/<X>/<sub-Y>/`. If you
want nested L2s, do one of: split into two sibling L2s
(`research-papers-ml/` and `research-papers-bio/`); add a `tag:` or
`aliases:` discrimination inside the existing L2 rather than forking
it; or use a `theme` or `project` page type inside one L2 to carry
the sub-domain semantics.

**Renaming a domain after committing?**

Renames propagate via wikilinks (`/AGENTS.md` §6's "no bulk renames
without human consent"). The mechanics:

1. `git mv domains/<old>/ domains/<new>/`
2. `git grep -l '<old>' | xargs sed -i '' "s|domains/<old>|domains/<new>|g"`
3. `python -m densa --all` to confirm zero dangling.
4. Update `/index.md`, `/AGENTS.md` if it names the domain, any L2s
   that wikilink to the old domain.
5. Commit with bypass + log entry.

**What if I want to delete `psychology` because the worked-content
makes my repo look therapy-focused?**

Go ahead. The L2's "about this worked example" callout already
declares the raws are synthesised. Delete the raws + wikis + (if no
intent to ingest real therapy material) the AGENTS.md; the schema is
documented in the AGENTS.md itself and you can always re-import it
from a future starter release.

## What to read next

- [`/AGENTS.md`](../AGENTS.md) — the L1 contract. Allowed page types
  (§3), red lines (§6), routing rules (§5) — these your L2 cannot
  override.
- [`docs/DESIGN.md`](DESIGN.md) — the longer essay on why each design
  decision exists.
- [`_system/MANUAL.md`](../_system/MANUAL.md) — day-in-the-life and
  FAQ.
- [`docs/bootstrap-prompt.md`](bootstrap-prompt.md) — paste-into-AI
  for your first session.
