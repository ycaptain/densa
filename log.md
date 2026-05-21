---
type: log
scope: global
updated: 2026-05-21
compiled_against: 1
---

# Global Log

Append-only timeline of cross-domain events (see [`AGENTS.md`](AGENTS.md)
§6 for the append-only rule and §2.1 for entry format). Newest entries
go immediately below this preamble; older entries scroll down.

Entry format:

```
## [YYYY-MM-DD] <operation> | <one-line summary>
- Source: [[<path>]]
- Pages touched: [[…]], [[…]]
- One-line synthesis.
```

---
