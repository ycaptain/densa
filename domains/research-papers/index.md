---
type: index
scope: research-papers
domain: research-papers
updated: 2026-05-21
compiled_against: 1
example_status: worked-example
---
<!-- updated 2026-05-21: raw upgraded from paraphrase to full articles + PhD-onboarding navigator added -->


# Research papers — Index

Domain-level index for paper reading, evergreen concepts, cross-paper
syntheses, and open research questions. See [`AGENTS.md`](AGENTS.md)
for the L2 schema (persona, ontology, lint rules) before authoring any
wiki page in this domain.

> [!important] What this domain demonstrates
> This is the **lightweight reference L2** of the wiki — a worked
> example of what one paper-ingest produces in this system. Each
> ingest turns a single raw paper into a **cluster of 5-10 linked
> wiki pages**: one `analysis` (mechanism + evidence + limits +
> open questions), 1-3 `concept` pages (the evergreen ideas the
> paper touches), 0-2 `question` pages (the long-arc threads the
> paper opens), and an update to the relevant `framework` page.
> When ≥2 papers share a thread, a `synthesis` page emerges
> connecting them.
>
> **Raw papers under [`raw/papers/`](raw/papers/) are the actual
> full articles** (extracted from arXiv / PNAS / *Nature
> Scientific Reports* HTML on 2026-05-21), not summaries — so
> every claim in the analyses traces to a primary source you can
> open and re-verify section-by-section. The only exception is
> [[2024-anthropic-sparse-autoencoders]], which is explicitly
> marked as a synthesised demo stand-in.
>
> **New here? Start with [[how-to-read-this-domain]]** — the
> 5-minute / 30-minute / 2-hour / half-day onboarding navigator
> written for PhD students and researchers entering the wiki for
> the first time.
>
> **For first-time readers** — three reading paths give a fast
> grok of the depth this produces:
> 1. **Skim a single analysis end-to-end** —
>    [[2024-bastani-generative-ai-guardrails-analysis]] is the most
>    fully-worked example. Each section corresponds to a
>    schema-required field (`Claim` / `Method` / `Evidence` /
>    `Limits` / `Open questions` / `Wiki cross-references`).
> 2. **Follow one concept across multiple papers** —
>    [[cognitive-offloading]] shows how a single concept page
>    aggregates evidence across three RCTs, with an "Appearances"
>    ledger at the bottom that lint keeps fresh.
> 3. **Read a cross-paper synthesis** —
>    [[llm-tutoring-causal-evidence-2024-2025]] braids three
>    papers into one coherent picture and surfaces what remains
>    empirically open (the "What we don't yet know" section is
>    where the next research questions live).
>
> The point of the structure is **compounding** — every new paper
> ingest adds to the same concept / question / framework pages,
> so by paper 5 the wiki carries more cross-cutting signal than
> any single reading note could.

## Featured: AI in education — causal evidence arc (2024-2025)

> [!important] Start here if you're new to AI-in-education research
> Three classroom RCTs in 2024-2025 gave the field its first causal
> evidence base on whether LLMs help or hurt learning. The
> high-readability navigator
> [[ai-education-2024-2025-researcher-guide]] walks newcomers through
> the arc in ~10 minutes; the deeper cross-paper synthesis is at
> [[llm-tutoring-causal-evidence-2024-2025]]; the framework page is
> [[llm-tutoring-systems]].

## Papers (raw)

```dataview
TABLE WITHOUT ID
    file.link AS "Paper",
    published AS "Published",
    venue AS "Venue",
    authors AS "Authors"
FROM "domains/research-papers/raw/papers"
WHERE file.name != "papers"
SORT published DESC
```

## Analyses

```dataview
TABLE WITHOUT ID
    file.link AS "Analysis",
    evidence_quality AS "Evidence",
    replicated AS "Replicated",
    updated AS "Updated"
FROM "domains/research-papers/wiki/analyses"
WHERE type = "analysis" AND status = "active"
SORT updated DESC
```

## Concepts

```dataview
TABLE WITHOUT ID
    file.link AS "Concept",
    first_appeared AS "First appeared",
    last_validated AS "Last validated"
FROM "domains/research-papers/wiki/concepts"
WHERE type = "concept" AND status = "active"
SORT first_appeared DESC
```

## Frameworks

```dataview
TABLE WITHOUT ID
    file.link AS "Framework",
    programme_status AS "Status",
    programme_start AS "Started"
FROM "domains/research-papers/wiki/frameworks"
WHERE type = "framework" AND status = "active"
SORT programme_start DESC
```

## Open questions

```dataview
TABLE WITHOUT ID
    file.link AS "Question",
    arc_status AS "Status",
    first_asked AS "First asked",
    updated AS "Last update"
FROM "domains/research-papers/wiki/questions"
WHERE type = "question" AND arc_status != "answered"
SORT updated DESC
```

## Syntheses

```dataview
TABLE WITHOUT ID
    file.link AS "Synthesis",
    updated AS "Updated"
FROM "domains/research-papers/wiki/syntheses"
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```

## Recent domain activity

```dataviewjs
const log = await dv.io.load("domains/research-papers/log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(0, 15));
}
```
