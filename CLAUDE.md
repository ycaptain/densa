# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo is **Densa** — an AGENTS.md-native skill pack that compiles raw sources into a queryable markdown wiki (an executable implementation of Karpathy's llm-wiki pattern; the opposite of RAG). It has a **dual nature**, and which one you're in changes the rules:

1. **A content vault.** `domains/<X>/raw/` holds immutable sources; `domains/<X>/wiki/` holds LLM-compiled pages. Here you act as the _wiki maintainer_ via the five operations (`ingest` / `query` / `lint` / `process-inbox` / `promote`).
2. **The upstream tool.** `_system/densa/` is a stdlib-only Python validator (the `densa` CLI) plus prompts/templates. Here you act as a _software contributor_.

**`AGENTS.md` is the authoritative L1 contract** — read it before doing any vault work; it is not duplicated here. Each `domains/<X>/AGENTS.md` is an L2 override (L2-wins inside that domain). `GUIDE.md` is explanatory only; when GUIDE and AGENTS disagree, AGENTS wins. When prose and `_system/densa/schema.py` disagree, the Python wins (AGENTS011 catches the drift).

## Commands

Validator / tests / lint (run from repo root; the package lives under `_system/densa/`, so `PYTHONPATH=_system` is needed until `pip install -e .`):

```bash
PYTHONPATH=_system python -m densa --all     # full validator pass (what CI runs)
PYTHONPATH=_system python -m densa --staged  # what the pre-commit hook runs
PYTHONPATH=_system python -m densa --diff origin/main   # PR-range staged-rule pass
PYTHONPATH=_system python -m densa rules     # print live AGENTS001–012 registry

python -m pytest                  # test suite (testpaths=_system/tests)
python -m pytest -k <check-name> -v   # iterate on one check
python -m ruff check .            # lint validator code (domains/, docs/ excluded)
python -m mypy                    # type-check _system/densa (strict)
```

One-time contributor setup: `pip install -e ".[dev]"` (pytest + ruff + mypy + pyyaml). The pre-commit hook itself is **pure stdlib** — wire it with `git config core.hooksPath _system/hooks`; no install needed for self-use.

Strict-parsing variant (pyyaml backend, used in CI): `DENSA_STRICT=1 PYTHONPATH=_system python -m densa --all`.

## Validator architecture (`_system/densa/`)

A rule-based linter. Each rule has a stable ID `AGENTS001`–`AGENTS012` (pin the ID, never the name, in `# noqa: AGENTS00N` suppressions and commit messages).

- `checks/` — one module per rule, all subclassing `checks/base.py`. The rule↔file mapping is direct (e.g. `raw_immutability.py` → AGENTS001, `operation_writes_scope.py` → AGENTS007).
- `schema.py` — the machine-readable source of truth: `PAGE_TYPES`, the `OPERATIONS` constant (per-operation write scopes for AGENTS007), `CANONICAL_FACTS`.
- `runner.py` / `cli.py` — orchestration and the argparse entry point (`densa = densa.cli:main`). `--staged` / `--all` / `--diff` select the file set; staged-only vs file-level rules differ.
- `git_io.py`, `frontmatter.py`, `wikilink.py`, `paths.py`, `report.py`, `formatters.py` — supporting layers (git plumbing, YAML frontmatter parse, wikilink resolution, path classification, diagnostics, text/json/github output).
- `commands/` — the non-lint subcommands (`init`, `upgrade`, `migrate`, `agent_inject`).

When adding/changing a rule: update its `checks/` module **and** `schema.py` if the contract moved, add a pytest case under `_system/tests/`, and keep the matching `_system/prompts/<op>.md` "What this command will write" table in sync (AGENTS011 warns on drift).

## Commit discipline (machine-enforced — this WILL block commits)

AGENTS007 classifies every commit by its message prefix and restricts which paths it may touch:

- `ingest(<domain>):` / `query:` / `lint:` / `process-inbox:` / `promote:` — operation commits (may write `domains/**` per the operation's scope in `schema.py`).
- **(no prefix)** — treated as schema/docs/validator maintenance and **MUST NOT touch `domains/**`\*\*.

If the hook rejects a commit, the fix is almost always to split it into two commits (operation edit with its prefix, maintenance edit prefix-free) — not to bypass. Last-resort bypass: `WIKI_ALLOW_CROSS_SCOPE=1 git commit ...`, which must be paired with a `## [YYYY-MM-DD] maintenance | …` entry in `log.md`.

**Do not commit autonomously.** After a non-trivial wiki edit (≥3 pages), remind the human to commit; let them run it. Commit-message convention: `<op>(<scope>): <summary>` (e.g. `feat(validate): ...`, `docs(readme): ...`, `ingest(research-papers): 2026-05-29 <slug>`).

## Red lines (non-negotiable — full list + rationale in AGENTS.md §6)

- `raw/` is immutable — never edit/rename/move/delete anything under any `raw/`.
- `log.md` is append-only, reverse-chronological — new entries go immediately below the frontmatter/preamble; never rewrite past entries.
- Never delete a wiki page — deprecate it (`status: deprecated` + `> Superseded by [[new-page]]`, remove from `index.md`).
- No bulk slug renames without human consent (wikilinks cascade).
- No silent web fetches during `ingest` — ask first, cite added context separately.
- Bumping `compiled_against:` requires a migration script under `_system/scripts/migrate_NN_<slug>.py` and a `.legacy/` snapshot for bulk re-ingest.

## Conventions

- Wiki filenames: lowercase-kebab-case; dated sources keep an ISO prefix (`2024-12-11-session-<slug>.md`). Wikilinks prefer `[[short-slug]]`.
- `%%HUMAN: …%%` blocks inside LLM-owned pages are authoritative — always preserve them.
- `outputs/` holds rebuildable artifacts (lint reports, Q&A); wiki pages never cite them. A Q&A becomes a wiki page only via the `promote` operation, never a hand copy.
- ruff `extend-exclude` covers `domains`, `docs`, `attic`, `inbox`, `_system/templates`, `_system/prompts` — markdown content is not linted as code.

## Local dev tracker

Tasks are tracked in `.backlog/` via Backlog.md MCP. Use `mcp__backlog__task_*` tools to create, view, and complete tasks. See `.backlog/` for the full task list.

Pre-launch plan with phase sequencing: [`docs/maintainers/2026-05-29-pre-launch-plan.md`](docs/maintainers/2026-05-29-pre-launch-plan.md).

<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_backlog_instructions()` to load the tool-oriented overview. Use the `instruction` selector when you need `task-creation`, `task-execution`, or `task-finalization`.

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:

- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and finalization
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->
