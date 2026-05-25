---
name: Domain (L2) design help
about: Get help designing a new L2 schema for your own domain
title: "L2: <domain-name>"
labels: domain-design
assignees: ""
---

> Use this template when you want feedback on a new L2 you're standing
> up in your own vault. We'll work through the four design questions
> from
> [`docs/reference/design-rationale.md`](../../docs/reference/design-rationale.md)
> §"How to design your own L2" together. Answer what you can; leave
> the rest blank.

## Domain in one sentence

<!-- e.g. "Tracking research papers across cognitive science, ML
     interpretability, and decision theory." -->

## 1. Persona

What voice should the LLM adopt when synthesising material in this
domain? 2–3 short alternative paragraphs are better than one polished
final draft — the contrast helps us pick the load-bearing words.

<!-- Draft A: ... -->
<!-- Draft B: ... -->
<!-- Draft C: ... -->

## 2. Folder layout

What kinds of source material will you drop into `raw/`?
What kinds of wiki pages will the LLM produce?

```
domains/<your-domain>/
├── raw/
│   ├── <bucket-1>/   ← e.g. papers, transcripts, meeting-notes
│   └── ...
└── wiki/
    ├── <type-1>/     ← e.g. concepts, patterns, analyses
    └── ...
```

## 3. Page types

Which subset of L1's nine allowed types does this domain use?
L1 v2 is a *closed* enum (`type:` cannot be invented) — sub-
categorise within an existing type via L2-specific `kind:` fields
rather than proposing a new top-level type.

- [ ] source
- [ ] summary
- [ ] entity
- [ ] concept
- [ ] comparison
- [ ] overview
- [ ] synthesis
- [ ] open-question
- [ ] report
- L2-specific `kind:` sub-categories you'd want
  (e.g. `entity_kind: project / decision`, `concept_kind: pattern`):
  <!-- list -->


## 4. L2-required frontmatter additions

What extra frontmatter fields does each page type need in your domain?
(See psychology L2 §"Required frontmatter additions" for the pattern.)

## 5. Domain-specific lint rules

What signals "this domain's wiki is drifting"? 3–8 bullets.

- ...
- ...

## Privacy posture

- [ ] Public-shareable (no real names, encryption optional)
- [ ] Private-only (encryption required; will use git-crypt before any push)
- Other notes: <!-- -->

## What you're stuck on

<!-- The one or two decisions you most want input on. -->
