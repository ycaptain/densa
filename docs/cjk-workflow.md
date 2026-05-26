# Working in Chinese (and other CJK languages)

> **Scope.** This guide covers conventions for running a vault whose
> raw content, wiki bodies, or both are predominantly Chinese,
> Japanese, or Korean. The schema in [`AGENTS.md`](../AGENTS.md) is
> language-neutral by construction; this doc fills in the
> conventions that the schema deliberately does not enforce so a
> CJK-first vault stays internally consistent.

CJK content works end-to-end out of the box for a single vault.
Everything below is a *recommendation* — the validator will not fail
your vault if you depart from it, but lint reports may surface
inconsistencies (e.g. some slugs romanised, others CJK characters).

---

## 1. Token-budget arithmetic

[`_system/prompts/ingest.md`](../_system/prompts/ingest.md) section 1
estimates tokens from byte count using a `bytes / 4` heuristic that
is calibrated for **English prose**. For CJK content the heuristic
mis-estimates in a predictable direction.

| Content                | UTF-8 bytes / char | Tokens / char (typical) | Effective `tokens ≈ bytes / N` |
|------------------------|--------------------|--------------------------|-----------------------------|
| English prose          | ~1.0               | ~0.25                    | N = 4 (the gate's default)   |
| English code           | ~1.0               | ~0.33                    | N = 3                        |
| Chinese / Japanese     | ~3.0               | ~1.0 (BPE per char)      | **N ≈ 3**                    |
| Korean (Hangul)        | ~3.0               | ~1.0–1.5                 | **N ≈ 2.5**                  |

Practical implications for the L1 `≤20K` / `>20K` / `>60K` gate
thresholds:

- A Chinese transcript of **20 000 characters ≈ 60 KB ≈ ~20 K tokens**
  — *right at* the single-pass threshold. The default `bytes / 4`
  gate would call this 15 K and proceed single-pass; that is
  approximately correct.
- A Chinese transcript of **40 000 characters ≈ 120 KB ≈ ~40 K
  tokens** — the default gate calls this 30 K (above the 20 K
  two-step threshold) and the math agrees.
- The two-step ingest threshold (≥ 20 K tokens) and hard-chunk
  threshold (≥ 60 K tokens) **work correctly on CJK** when you
  treat the byte/token ratio as roughly equal between English and
  Chinese — because Chinese chars use ~3 bytes each *and* tokenise
  at ~1 token each, the bytes-per-token effective ratio still
  lands near 3–4 in practice.

When in doubt: count **characters** for CJK and treat 1 character ≈
1 token. The `_system/prompts/ingest.md` token-gate paragraph
includes this CJK-specific note.

---

## 2. Slugs, aliases, and wikilinks

[`AGENTS.md` §"Naming and linking conventions"](../AGENTS.md#4-naming-and-linking-conventions)
says filenames must be
`lowercase-kebab-case`. It does **not** ban CJK characters in
filenames — Obsidian resolves `wiki/concepts/失语.md` natively, and
the validator's `AGENTS006 wikilink-resolvable` rule treats
filename-stem and aliases symmetrically. Two patterns work, with
trade-offs:

### Pattern A — ASCII slug + CJK alias (recommended)

```yaml
---
type: concept
domain: literature
aliases: ["失语", "言语丧失"]
---
```

Filename: `wiki/concepts/aphasia-literary.md`

Inside a Chinese-language page body you still write `[[失语]]` and
the wikilink resolves via the alias.

**Pros**: filenames stay portable across filesystems / shell tools,
romanised slugs survive `git log` / `gh` / non-CJK editors fine,
and the validator's slug-collision detection is straightforward.

**Cons**: there are two names for the page (slug + alias), and you
must keep aliases in sync when the canonical Chinese term shifts.

### Pattern B — CJK filename (acceptable)

```yaml
---
type: concept
domain: literature
aliases: ["aphasia-literary"]   # optional English alias
---
```

Filename: `wiki/concepts/失语.md`

**Pros**: one canonical name; the slug *is* the term.

**Cons**: shell tools that don't handle UTF-8 cleanly (older Windows
git installs, some CI runners) can choke on the path; URL-encoding
ambiguity in markdown link rendering can surface.

### Rule of thumb

- **Mixed-language vault** (Chinese bodies + English technical
  terms): use Pattern A. The English alias is a no-op overhead
  but every English term you do introduce stays linkable.
- **Strictly CJK vault** (Chinese-only, no Latin-script terms
  appear in bodies): Pattern B is fine and reduces the
  slug-vs-alias bookkeeping.
- **One concept = one page**. Whichever pattern you pick, do not
  let `aliases:` carry two distinct concepts that happen to share
  a Chinese-language synonym; create separate pages and disambig
  with a parenthetical (`失语（医学）` vs `失语（文学）`).

---

## 3. Commit messages

The validator (`AGENTS007`) parses commit subjects by their leading
**ASCII prefix**: `ingest(<domain>):`, `query:`, `lint:`,
`process-inbox:`, `promote:`. The prefix syntax is fixed. The
**body after the prefix** can be in any language — Chinese is
fine, mixed-script is fine.

Recommended shape:

```
ingest(literature): 2026-05-20 莫言访谈
```

The prefix is machine-readable; the body is human-readable in your
working language. Commit body lines (after the subject) follow the
same convention.

---

## 4. Lint report language

[`_system/prompts/lint.md`](../_system/prompts/lint.md) is authored
in English. When an LLM follows it, the findings tend to come back
in English by default — which produces a bilingual report on a
Chinese-content vault.

Two acceptable postures:

- **Author lint in the vault's predominant content language.** Tell
  the LLM at the start of the lint pass: *"Author all findings in
  the vault's predominant content language (Chinese for this
  vault)."* The prompt structure (headings, rule names) stays
  English; the *findings* render in Chinese.
- **Author lint in English regardless.** Useful when the vault is
  cross-language (Chinese raws + English wiki, or vice versa) and
  the lint report is reviewed by readers of both languages.

The `_system/prompts/lint.md` body recommends matching the vault's
predominant content language; override per-pass when needed.

---

## 5. L2 hint convention (optional)

When standing up a CJK-first L2, declare the posture in the L2's
`AGENTS.md`. There is no enforced frontmatter field — this is
documentation discipline, not validator-checked.

Recommended header in the L2's AGENTS.md:

```markdown
## Vault language

This domain is **Chinese-first**: raw sources, wiki bodies, log
entries, and lint findings are authored in Chinese. Slugs follow
[cjk-workflow.md] Pattern A (ASCII slug + Chinese aliases).
```

A two-sentence declaration up front saves the LLM (and the next
human) from having to infer the posture from the data.

---

## 6. Known limitations

- **Obsidian's "shortest unique slug" wikilink resolution** treats
  CJK characters as case-insensitive bytes; if you create both
  `失语` and `失語` (simplified vs traditional) the resolver picks
  whichever shorter slug it sees first. Aliases handle this when
  the variants are documented as synonyms; create separate pages
  only when the variants are genuinely different concepts.
- **`git diff`** on UTF-8 CJK changes is fine on macOS / modern
  Linux. On legacy Windows with a non-UTF-8 console you may see
  garbled bytes in the diff output — this is a console issue,
  not a vault issue; configure Windows to use UTF-8 (`chcp 65001`
  + a UTF-8-aware terminal like Windows Terminal).
- **Web Clipper filename templates** with `{{title|slug}}` will
  romanise CJK titles to pinyin-or-empty-string depending on
  version. Override per-domain to `{{title}}` (preserve CJK) or
  to a manual slug.

---

## 7. Smallest test

Before bulk-ingesting CJK material, run this once:

1. Create `domains/<your-cjk-domain>/wiki/concepts/test-page.md`
   with `aliases: ["测试页"]` in frontmatter and the body
   `Linking with alias: [[测试页]] works.`
2. Open the file in Obsidian, click the wikilink. It should
   resolve back to the same page.
3. `python -m densa --all` should report no AGENTS006
   violations.

If all three pass, your vault is CJK-ready.
