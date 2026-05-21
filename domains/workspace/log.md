---
type: log
scope: workspace
domain: workspace
updated: 2026-05-21
compiled_against: 1
---

# Workspace — Log

Append-only domain timeline. New entries go immediately below this
preamble (newest first); older entries scroll down. See
[`/AGENTS.md`](../../AGENTS.md) §6 for the append-only rule and §2.1
for entry format.

Entry format:

```
## [YYYY-MM-DD] <operation> | <one-line summary>
- Source: [[<path>]]
- Pages touched: [[…]], [[…]]
- One-line synthesis.
```

---

## [2026-05-21] ingest | worked-example bundle (Q2 platform-migration arc)
- Sources: [[2026-04-08-meeting-q2-planning]],
  [[2026-04-22-decision-microservices-split]],
  [[2026-05-06-meeting-incident-postmortem]]
- Pages touched:
  [[2026-04-08-meeting-q2-planning-analysis]],
  [[2026-04-22-decision-microservices-split-analysis]],
  [[2026-05-06-meeting-incident-postmortem-analysis]],
  [[team-platform]], [[stakeholder-alex-cs]],
  [[q2-platform-migration]], [[microservices-split]],
  [[decision-delay-from-skipped-stakeholder]],
  [[q2-platform-arc-may]],
  [[should-we-revisit-cs-veto-power]]
- Worked example demonstrating how a workspace ingest produces
  three analyses, two entity pages, a canonical decision page
  (distinct from the raw ADR), the cross-raw `decision-delay-from-
  skipped-stakeholder` pattern, and a 6-week arc synthesis. Synthetic
  / fictional content — see [`docs/EXAMPLE-DOMAINS.md`](../../docs/EXAMPLE-DOMAINS.md)
  for the removal-or-adopt guide.
