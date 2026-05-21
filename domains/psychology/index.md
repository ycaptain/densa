---
type: index
scope: psychology
domain: psychology
updated: 2026-05-21
compiled_against: 1
example_status: worked-example
---
<!-- updated 2026-05-21: schema-only → worked-example (six-week father-grief arc, 4 raws → ~25 wiki pages, English-language for open-source showcase) -->


# Psychology — Index

Domain-level index for therapy / psychiatry sessions, recurring
patterns, multi-session arcs. See [`AGENTS.md`](AGENTS.md) for the L2
schema (persona, ontology, lint rules) before authoring any wiki page
in this domain.

> [!important] What this domain demonstrates
> This is the **heavy reference L2** of the wiki — a worked example
> of what one *bereavement-arc* of psychotherapy + psychiatry
> ingests produces. Four raw sessions (three therapy + one
> psychiatry, spanning **2026-04-02 → 2026-05-14**) become
> **~25 linked wiki pages**: four `analysis` pages bound 1:1
> with raws, three `pattern` pages with evolving instance
> ledgers, two `theme` pages tracking multi-session arcs,
> three `entity` pages (therapist + psychiatrist + IFS
> Manager-part), four `concept` pages, two `framework` pages,
> one `protocol` page (the medication-arc), two long-arc
> `question` pages, and three `synthesis` pages serving three
> distinct readers.
>
> **The four raw sessions are synthesised** — they are not real
> clinical material; each raw begins with an HTML-comment
> banner declaring this. The schema (`AGENTS.md`), the ingest
> prompt, the templates, and the validator are
> production-grade. Clinical adopters MUST re-read
> [`AGENTS.md`](AGENTS.md) §"Privacy posture" and select an
> appropriate posture *before* ingesting any real session.
>
> **Three reading paths give a fast grok of the depth this
> produces:**
>
> 1. **Clinician / doctor-to-doctor** —
>    [[2026-05-14-six-week-retrospective]] (~8 min) is the
>    arc-level entry point. It cites every analysis, every
>    pattern, every theme, every concept it relies on; it does
>    not re-paraphrase.
> 2. **Client / case-protagonist** —
>    [[father-grief-arc]] (~3 min) is the theme-level entry
>    point. The What-changed-across-the-arc delta table is the
>    most concise account of what's shifted in six weeks.
>    Then read one accessible concept page,
>    e.g. [[grief-as-love-transformed]].
> 3. **Open-source evaluator** —
>    [[what-this-domain-demonstrates]] (~10 min) is the
>    explicit capability list with anchor-style proof for each
>    of ten capabilities the worked example exercises. Quote
>    this in your evaluation report.
>
> For the full navigator with time-budgeted reading paths and
> the wiki-graph map, start at
> [[domains/psychology/wiki/syntheses/how-to-read-this-domain|how-to-read-this-domain]].

## Featured: Father-grief six-week arc (2026-04 → 2026-05)

> [!important] The flagship worked example
> A 41-year-old man (fictional, slug `mark-eldridge`) presents
> 8 weeks after the sudden cardiac death of his father, with
> [[masked-depression]] / [[complicated-grief]] risk markers.
> Across four sessions (three therapy with
> [[therapist-reyes]], one psychiatry with
> [[psychiatrist-han]]), the arc demonstrates IFS
> Manager-part work, somatic anchoring (EFT), attachment
> formulation, biopsychosocial 4P, diagnostic conservatism,
> meaning-reconstruction integration, conservative-prescribing
> rationale, and a documented turning point (2026-05-09
> client-initiated phone call with mother).
>
> - **Arc retrospective**:
>   [[2026-05-14-six-week-retrospective]] — the clinician-grade
>   six-week synthesis.
> - **Three-audience navigator**:
>   [[domains/psychology/wiki/syntheses/how-to-read-this-domain|how-to-read-this-domain]]
>   — clinician / client / evaluator reading paths.
> - **Theme page**: [[father-grief-arc]] — the multi-session
>   arc with turning point annotated.
> - **Capability demo**: [[what-this-domain-demonstrates]] —
>   ten capabilities with anchor-style proof. **This is the
>   evaluator's entry point.**

## Sessions (raw)

```dataview
TABLE WITHOUT ID
    file.link AS "Session",
    date AS "Date",
    participants AS "Participants",
    mode AS "Mode"
FROM "domains/psychology/raw/sessions"
WHERE file.name != "session"
SORT date DESC
```

## Analyses

```dataview
TABLE WITHOUT ID
    file.link AS "Analysis",
    session_kind AS "Kind",
    analysis_lens AS "Lenses",
    updated AS "Updated"
FROM "domains/psychology/wiki/analyses"
WHERE type = "analysis" AND status = "active"
SORT updated DESC
```

## Entities

```dataview
TABLE WITHOUT ID
    file.link AS "Entity",
    role AS "Role",
    first_seen AS "First seen"
FROM "domains/psychology/wiki/entities"
WHERE type = "entity" AND status = "active"
SORT first_seen DESC
```

## Concepts

```dataview
TABLE WITHOUT ID
    file.link AS "Concept",
    last_validated AS "Last validated",
    updated AS "Updated"
FROM "domains/psychology/wiki/concepts"
WHERE type = "concept" AND status = "active"
SORT updated DESC
```

## Patterns

```dataview
TABLE WITHOUT ID
    file.link AS "Pattern",
    triggers AS "Triggers",
    severity AS "Severity",
    last_observed AS "Last observed"
FROM "domains/psychology/wiki/patterns"
WHERE type = "pattern" AND status = "active"
SORT last_observed DESC
```

## Themes

```dataview
TABLE WITHOUT ID
    file.link AS "Theme",
    arc_start AS "Started",
    arc_status AS "Arc status",
    updated AS "Updated"
FROM "domains/psychology/wiki/themes"
WHERE type = "theme" AND status = "active"
SORT updated DESC
```

## Frameworks

```dataview
TABLE WITHOUT ID
    file.link AS "Framework",
    last_validated AS "Last validated"
FROM "domains/psychology/wiki/frameworks"
WHERE type = "framework" AND status = "active"
SORT file.name ASC
```

## Protocols

```dataview
TABLE WITHOUT ID
    file.link AS "Protocol",
    area AS "Area",
    status AS "Status",
    last_revised AS "Last revised"
FROM "domains/psychology/wiki/protocols"
WHERE type = "protocol" AND status = "active"
SORT last_revised DESC
```

## Syntheses

```dataview
TABLE WITHOUT ID
    file.link AS "Synthesis",
    scope AS "Scope",
    updated AS "Updated"
FROM "domains/psychology/wiki/syntheses"
WHERE type = "synthesis" AND status = "active"
SORT updated DESC
```

## Open questions

```dataview
TABLE WITHOUT ID
    file.link AS "Question",
    arc_status AS "Status",
    first_asked AS "First asked",
    updated AS "Last update"
FROM "domains/psychology/wiki/questions"
WHERE type = "question" AND arc_status != "answered"
SORT updated DESC
```

## Recent domain activity

```dataviewjs
const log = await dv.io.load("domains/psychology/log.md");
if (!log) {
    dv.paragraph("_log.md not yet populated._");
} else {
    const entries = log.split("\n").filter(l => l.startsWith("## ["));
    dv.list(entries.slice(-15).reverse());
}
```
