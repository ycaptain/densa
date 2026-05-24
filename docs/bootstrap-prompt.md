# Bootstrap prompt — set up my LLM wiki

> Paste the body of this file (everything below the `---` line) into
> Cursor / Claude Code / Codex / a similar IDE-bound coding agent
> *after* you've forked the Densa upstream into your own vault:
>
> ```bash
> # Fork ycaptain/densa on GitHub (one click), then:
> git clone git@github.com:<you>/densa.git ~/your-vault
> cd ~/your-vault
> git remote add upstream https://github.com/ycaptain/densa.git
>
> # Open ~/your-vault in your AI-pair coding IDE and paste the prompt below.
> ```
>
> Forking (not template-cloning) keeps your vault on the upgrade
> train: `git fetch upstream && git merge upstream/main` brings in
> new lint rules and schema versions. Upstream never touches
> `domains/**`, so merges stay clean.
>
> The prompt below is what the AI should read. It's deliberately
> step-by-step, with a hard "no edits until I confirm" gate at each
> step, so you stay in control.

---

You are setting up a personal LLM-maintained wiki for me — a
Densa vault, based on Andrej Karpathy's `llm-wiki` pattern adapted
to Obsidian + an IDE-resident AI agent. The fork is already cloned in
the current directory with `upstream` configured. Your job is to
walk me through standing it up, one step at a time, **never editing
anything until I explicitly approve**.

## Step 1 — orient yourself (read-only)

Read these four files end-to-end before doing anything else:

1. [`AGENTS.md`](AGENTS.md) — L1 schema (the universal contract).
2. [`_system/MANUAL.md`](_system/MANUAL.md) — design philosophy + FAQ.
3. [`domains/psychology/AGENTS.md`](domains/psychology/AGENTS.md) — one
   of three shipped L2 examples (the heaviest). Study its structure;
   you'll be writing similar
   files for my domains.
4. [`_system/prompts/ingest.md`](_system/prompts/ingest.md) — the
   canonical ingest procedure (so you know what the most common
   operation will demand).

Then briefly tell me, in 5-7 bullets, your understanding of:

- The three semantic layers (`raw/`, `wiki/`, `AGENTS.md`) and why
  they're separated.
- The five operations (`ingest`, `query`, `lint`, `process-inbox`, `promote`).
- The red lines you must not cross during any operation.
- What an `analysis` page is vs a `synthesis` page.
- Where the L1 contract ends and an L2's domain-specific schema begins.

This is a sanity check — if your bullets are wrong, we abort and
re-read before proceeding.

## Step 2 — interview me to surface my domains

Ask me 3-5 questions, one at a time (not all at once). Wait for my
answer before asking the next one. Recommended question set, but
adapt as needed:

1. *"Which 2-4 areas of your life do you want this wiki to track?"*
   (Examples I might give: research-papers, family, mood, side-
   projects, language-learning, household-decisions, fitness.)
2. *"For each area, do you have a continuous stream of raw material
   (transcripts, articles, journal entries, meeting notes, photos)?
   Or is it more sporadic?"*
3. *"Which area, if any, has the highest privacy stakes — material
   you'd want encrypted with git-crypt before any remote push?"*
4. *"Do you prefer the wiki to be authored in English, Chinese, or
   another language?"*
5. *"How often do you imagine yourself running `query` (asking the
   wiki a question) vs `ingest` (adding new material)? The answer
   shapes how heavy-weight each L2 should be."*
6. *"Do you publish externally (blog / newsletter / Twitter / Substack)?
   If yes, I'll scaffold an optional `writing/{drafts,published}/`
   layer for in-progress posts that consume wiki knowledge."* → if
   yes, plan to create `writing/drafts/` and `writing/published/`
   later. If no, skip that step entirely.
7. *"Do you run multi-week research projects with hypotheses and
   experiment logs? If yes, I'll scaffold an optional
   `projects/<slug>/` workspace layer for those."* → if yes, plan to
   create `projects/` later. If no, skip.

Summarise my answers back to me in a short table before moving on.

## Step 3 — design each L2 schema with me

For each domain I named, draft a `domains/<X>/AGENTS.md` patterned on
the psychology example but **tuned to my domain's needs**. For each
draft, work through the four design questions explicitly (see
[`docs/DESIGN.md`](docs/DESIGN.md) §"How to design your own L2"):

1. **Persona** — what voice should the LLM adopt when synthesising
   this domain? Show me 2-3 alternative persona paragraphs to pick
   from, not a single take-it-or-leave-it draft.
2. **Folder layout** under `raw/` and `wiki/`.
3. **Page types** — which subset of L1's allowed types this domain
   uses, plus any L2-specific types (rare; require justification).
4. **L2-required frontmatter additions** per type.
5. **Domain-specific lint rules** — 3-8 bullets each on what would
   signal this domain is drifting.

Show me each draft in full before writing it to disk. Take my edits.
Only `git add` after I say "looks good, commit it".

Default scope: start lean. A new L2 with three page types and one
lint rule is better than a 200-line spec we'll edit five times.

## Step 4 — decide what to do with the example L2s

The template ships **three** example domains:

- `domains/research-papers/` — a light-weight L2 with a 5-paper
  LLM-tutoring evidence arc (3 real RCTs + 1 real review + 1
  synthesised SAE stand-in, 2024-2025). The cleanest reference for
  designing your own.
- `domains/workspace/` — a medium L2 demonstrating
  meetings / decisions / stakeholders with the Q2 platform-migration
  arc plus a positive-pattern engineering-decision retrospective.
- `domains/psychology/` — the heavy L2: 6-week father-grief therapy +
  psychiatry arc (5 synthesised raws → 25 wiki pages). Advanced
  features: ASR correction, privacy postures, biopsychosocial-4P
  framing.

See [`docs/EXAMPLE-DOMAINS.md`](docs/EXAMPLE-DOMAINS.md) for the full
per-domain matrix and the keep/delete/adopt decision tree.

For **each** example, ask me one of three things:

1. **Keep as-is** — if one of my domains will be that L2 verbatim.
2. **Rename and adapt** — e.g. `git mv domains/research-papers
   domains/my-papers` and edit the L2 schema. Lower friction than
   designing a new L2 from scratch when my domain is close.
3. **Move to reference** — `git mv domains/<example>
   domains/.legacy-example-<name>` so it stays browseable but
   doesn't appear in the live index.

Default recommendation: **move every example I don't explicitly want
to keep into `.legacy-example-*`**. Three live example domains
alongside my own real domains is clutter. Don't decide for me
silently — ask, then act.

## Step 4.5 — scaffold optional layers (if answered "yes" in Step 2)

For each optional layer the user opted into:

- **`writing/`** — create `writing/drafts/` and `writing/published/`
  directories (empty) plus a short top-level `writing/README.md`
  explaining the convention (see
  [`docs/DESIGN.md`](docs/DESIGN.md) §"Optional layers"). The
  templates already ship at
  `_system/templates/writing-draft.md` and
  `_system/templates/writing-publication.md`.
- **`projects/`** — create the `projects/` directory and a short
  top-level `projects/README.md` explaining the workspace convention.
  Subprojects live at `projects/<slug>/` and are free-form (see DESIGN).

Skip this step entirely for any layer the user declined. There is no
post-hoc penalty for skipping: both layers can be added later by
re-running this question with the same scaffolding logic.

## Step 5 — set up engineering hooks

Once at least one L2 is approved and committed:

1. Initialise the repo with `git init` **only if you didn't use
   `densa init` or `git clone`** — both already created the `.git`
   directory. Skip this in the common case.
2. Wire the pre-commit hook:
   `git config core.hooksPath _system/hooks`.
3. Make a small test commit (e.g. add a placeholder file under
   `domains/<X>/wiki/concepts/` with proper frontmatter) to verify
   the hook fires and `densa` runs.
4. If any of my domains was flagged "high privacy stakes" in Step 2,
   walk me through the git-crypt setup in
   [`_system/SETUP.md`](_system/SETUP.md) §"Privacy: encrypt
   sensitive raw/ with git-crypt". **Don't push to any remote until
   git-crypt is verified working.**

## Step 6 — first ingest dry-run

Ask me for one piece of raw material I'd like to file (a single
article, a transcript, a meeting note). Then:

1. I drop the file into the appropriate `domains/<X>/raw/<bucket>/`.
2. You run the canonical `ingest` procedure from
   [`_system/prompts/ingest.md`](_system/prompts/ingest.md).
3. Output the **plan** (the list of wiki pages you intend to touch),
   then **stop**.
4. I review the plan and either approve, edit, or reject it.
5. Only if I approve do you apply the edits.

This is the "hello world" of the wiki. Don't skip the plan-first step
even if I'm impatient — the muscle memory matters.

## Step 7 — clean up project-only files (optional)

The template ships a number of files that exist for the open-source
project itself, not for any user's vault. Once Step 6 succeeds, ask
me whether to remove them. The default recommendation is **yes,
remove**, because they only confuse the LLM in future sessions:

- `LICENSE` — the template's MIT license; replace with your own only
  if you intend to publish *your vault* as a derived work.
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` — project process
  docs; irrelevant to a personal vault.
- `docs/DESIGN.md`, `docs/bootstrap-prompt.md` (you're reading it
  right now), `docs/EXAMPLES.md` — once bootstrap is complete these
  are reference material at best; keep them only if you actively want
  to consult `DESIGN.md` later, otherwise remove.
- `docs/EXAMPLE-DOMAINS.md` — **keep**. You'll re-consult this when
  removing leftover example L2s and when you eventually adopt one.
- `docs/CJK-WORKFLOW.md` — keep only if you work in Chinese / Japanese
  / Korean; otherwise remove.
- `.github/` — issue / PR templates and CI for the template repo;
  not useful in a personal vault.
- `.editorconfig` — keep this; it's harmless and useful.
- `_system/README-template.md` — see below; remove **after** copying
  it to the root as your vault's README.

Suggested commands (run only if I approve):

```bash
# Copy the per-vault README skeleton to the root and edit the title.
cp _system/README-template.md README.md
# (Now edit README.md and replace `_my-vault_` with my vault name.)

# Preserve the upstream MIT LICENSE alongside the densa code that
# travels with the template. Deleting LICENSE outright would strip
# the copyright/attribution that MIT requires you keep on any
# redistribution of the code under `_system/densa/`.
git mv LICENSE LICENSE-upstream

# Remove project-only docs but keep EXAMPLE-DOMAINS.md as a reference.
# (Drop docs/CJK-WORKFLOW.md from the rm list if you work in CJK.)
rm docs/DESIGN.md docs/bootstrap-prompt.md docs/EXAMPLES.md \
   docs/CJK-WORKFLOW.md
rm -rf .github/ CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md \
       CHANGELOG.md _system/README-template.md
```

If I want to keep more of the project metadata as reference, ask me
which specific subset (e.g. "keep `docs/DESIGN.md` and `LICENSE` but
remove the rest").

## Hard rules during bootstrap (and forever after)

- **No edits without my approval.** Always plan first; wait for OK.
- **No real names in committed files** until I've explicitly confirmed
  the privacy posture. Use `<slug>` placeholders when drafting; I'll
  swap in real slugs when we're ready.
- **Don't simplify or "improve" the L1 schema** in
  [`AGENTS.md`](AGENTS.md). It embeds load-bearing invariants. If you
  think a rule is wrong, surface the issue to me as a question; don't
  silently edit the contract.
- **Don't commit autonomously.** I'll run the commits, or you propose
  the commit message and I confirm.
- **Don't `git push` anywhere** until I tell you which remote and
  whether encryption is required.

When in doubt: ask. The cost of one extra clarifying question is much
lower than the cost of a wrong silent decision in a knowledge base
I'll use for years.

---

When you're done with Step 6, the vault is operational; Step 7 is
the optional cleanup pass. Subsequent sessions can start with just
*"ingest this"* or *"query that"* — you'll have the schemas and the
muscle memory by then.
