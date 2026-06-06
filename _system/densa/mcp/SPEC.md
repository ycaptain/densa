# Densa MCP Server — Tool Surface Specification (v1)

> **Status: frozen pre-launch.** These schemas are the API contract. Changes after the
> launch tag require a version bump. Implementation lives in `_system/densa/mcp/server.py`
> (Phase E). This document is the spec the implementation must match.

## Design decisions

| Decision             | Choice                                                           | Rationale                                                                     |
| -------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Tool count           | 8 read-only tools                                                | Middle ground between Tolaria (15) and nashsu (0); no write tools in v1       |
| Operations           | MCP `prompts`, not tools                                         | LLM still authors; human gate is unchanged                                    |
| Transport            | stdio JSON-RPC 2.0                                               | Zero-dependency; stdlib `json` + `sys.stdin/stdout` only                      |
| Pagination           | Cursor-based                                                     | Stateless server; cursor = opaque base64 offset string                        |
| Error envelope       | JSON-RPC codes for transport; diagnostics array for lint results | Lint violations are expected output, not errors                               |
| Tool naming          | Flat snake_case (`read_page`, not `pages.read`)                  | Consistent; simpler for type-ahead completion                                 |
| `read_page` output   | Raw markdown                                                     | Let client render                                                             |
| `read_page` + `raw/` | Wrap body in `<untrusted>` fence (D+B protocol)                  | Trust vocabulary uniform across in-vault and MCP reads — see `AGENTS.md §4.5` |
| `search_wiki`        | grep + wikilink follow; no embeddings                            | Zero-dep; reproducible across sessions                                        |

---

## Transport: MCP stdio JSON-RPC 2.0

Each message is a newline-delimited JSON object. The server reads from `stdin`
and writes to `stdout`. All objects follow JSON-RPC 2.0:

```json
// Request (host → server)
{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "read_page", "arguments": {"path": "domains/psychology/wiki/concepts/cbt.md"}}}

// Response (server → host)
{"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "..."}]}}

// Error
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32602, "message": "Invalid params: path not found"}}
```

Standard JSON-RPC error codes used: `-32700` parse error, `-32600` invalid request,
`-32601` method not found, `-32602` invalid params, `-32603` internal error.

---

## Tool 1: `vault_status`

Summary of mounted domains, page counts by type, and log staleness.

### Input schema

```json
{}
```

_(No parameters.)_

### Output schema

```json
{
  "type": "object",
  "properties": {
    "domains": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "path": {
            "type": "string",
            "description": "Repo-root-relative path, e.g. domains/psychology"
          },
          "page_counts": {
            "type": "object",
            "description": "Keys = page types (summary, concept, entity, …); values = integer counts"
          },
          "log_staleness_days": {
            "type": ["integer", "null"],
            "description": "Days since last log.md entry; null if log.md absent"
          }
        },
        "required": ["name", "path", "page_counts"]
      }
    },
    "total_pages": { "type": "integer" },
    "densa_version": { "type": "string" }
  },
  "required": ["domains", "total_pages"]
}
```

### Example

```json
{
  "domains": [
    {
      "name": "psychology",
      "path": "domains/psychology",
      "page_counts": {
        "summary": 14,
        "concept": 7,
        "entity": 3,
        "overview": 1
      },
      "log_staleness_days": 2
    },
    {
      "name": "research-papers",
      "path": "domains/research-papers",
      "page_counts": { "summary": 3, "overview": 1 },
      "log_staleness_days": 0
    }
  ],
  "total_pages": 29,
  "densa_version": "1.0.0"
}
```

---

## Tool 2: `list_domains`

List all mounted domains detected under `domains/`.

### Input schema

```json
{}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "domains": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "path": { "type": "string" },
          "has_l2": {
            "type": "boolean",
            "description": "True if domains/<name>/AGENTS.md exists"
          },
          "has_wiki": { "type": "boolean" },
          "has_raw": { "type": "boolean" }
        },
        "required": ["name", "path", "has_l2", "has_wiki", "has_raw"]
      }
    }
  },
  "required": ["domains"]
}
```

### Example

```json
{
  "domains": [
    {
      "name": "psychology",
      "path": "domains/psychology",
      "has_l2": true,
      "has_wiki": true,
      "has_raw": true
    },
    {
      "name": "research-papers",
      "path": "domains/research-papers",
      "has_l2": true,
      "has_wiki": true,
      "has_raw": true
    }
  ]
}
```

---

## Tool 3: `list_pages`

List wiki pages with optional type/domain filtering and cursor pagination.
Designed to support `@`-mention picker rendering: returns `title` + `preview_line` + `type`
per page so the picker can display without an additional `read_page` call.

### Input schema

```json
{
  "type": "object",
  "properties": {
    "type": {
      "type": "string",
      "description": "Filter by page type (summary, concept, entity, overview, synthesis, report, open-question). Omit for all types."
    },
    "domain": {
      "type": "string",
      "description": "Filter by domain name. Omit for all domains."
    },
    "cursor": {
      "type": "string",
      "description": "Opaque cursor from a previous response for pagination. Omit for first page."
    },
    "limit": { "type": "integer", "minimum": 1, "maximum": 200, "default": 50 }
  }
}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "pages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "Repo-root-relative path"
          },
          "title": { "type": "string" },
          "type": { "type": "string" },
          "domain": { "type": "string" },
          "updated": {
            "type": ["string", "null"],
            "description": "ISO date from frontmatter"
          },
          "preview_line": {
            "type": "string",
            "description": "First non-empty body line, max 120 chars — for picker rendering"
          }
        },
        "required": ["path", "title", "type", "domain"]
      }
    },
    "next_cursor": {
      "type": ["string", "null"],
      "description": "Null when no further pages exist"
    }
  },
  "required": ["pages", "next_cursor"]
}
```

### Example

```json
{
  "pages": [
    {
      "path": "domains/psychology/wiki/concepts/cbt.md",
      "title": "Cognitive Behavioural Therapy",
      "type": "concept",
      "domain": "psychology",
      "updated": "2026-05-20",
      "preview_line": "A structured, time-limited psychotherapy that targets the relationship between thoughts, feelings, and behaviours."
    }
  ],
  "next_cursor": null
}
```

---

## Tool 4: `read_page`

Read a single page (wiki page or raw source). When `path` is under `raw/`, the
body is wrapped in an `<untrusted>` fence with D+B escape-injection defence
(salt-on-close + pre-escaped close tags) per `AGENTS.md §4.5`.

### Input schema

```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "Repo-root-relative path to a wiki page or raw file"
    }
  },
  "required": ["path"]
}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "path": { "type": "string" },
    "is_raw": {
      "type": "boolean",
      "description": "True when path is under any raw/ directory"
    },
    "frontmatter": {
      "type": ["object", "null"],
      "description": "Parsed YAML frontmatter; null for raw files"
    },
    "body": {
      "type": "string",
      "description": "Markdown body. For raw files, wrapped in <untrusted> fence with salt."
    },
    "salt": {
      "type": ["string", "null"],
      "description": "4-char hex salt used in the <untrusted> open/close tags; null for wiki pages"
    }
  },
  "required": ["path", "is_raw", "frontmatter", "body"]
}
```

### Example — wiki page

```json
{
  "path": "domains/psychology/wiki/concepts/cbt.md",
  "is_raw": false,
  "frontmatter": {
    "title": "Cognitive Behavioural Therapy",
    "type": "concept",
    "updated": "2026-05-20"
  },
  "body": "A structured, time-limited psychotherapy…",
  "salt": null
}
```

### Example — raw file (with fence)

```json
{
  "path": "domains/psychology/raw/sessions/2026-03-12-session.md",
  "is_raw": true,
  "frontmatter": null,
  "body": "<untrusted source=\"domains/psychology/raw/sessions/2026-03-12-session.md\" salt=\"A3K9\">\n[Session transcript content — any literal &lt;/untrusted strings have been pre-escaped]\n</untrusted salt=\"A3K9\">",
  "salt": "A3K9"
}
```

---

## Tool 5: `search_wiki`

Full-text search over wiki pages using grep + wikilink follow. No embeddings.
Supports type-ahead via `prefix` mode for `@`-mention picker.

### Input schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search string (grep pattern or prefix for type-ahead)"
    },
    "type": {
      "type": "string",
      "description": "Restrict to a page type. Omit for all."
    },
    "domain": {
      "type": "string",
      "description": "Restrict to a domain. Omit for all."
    },
    "prefix": {
      "type": "boolean",
      "default": false,
      "description": "When true, treat query as a title-prefix for type-ahead; match titles that start with query (case-insensitive)."
    },
    "cursor": { "type": "string" },
    "limit": { "type": "integer", "minimum": 1, "maximum": 100, "default": 20 }
  },
  "required": ["query"]
}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "title": { "type": "string" },
          "type": { "type": "string" },
          "domain": { "type": "string" },
          "preview_line": {
            "type": "string",
            "description": "Matched excerpt (full-text) or first body line (prefix mode), max 120 chars"
          },
          "line": {
            "type": ["integer", "null"],
            "description": "1-based line number of match; null in prefix mode"
          }
        },
        "required": ["path", "title", "type", "domain", "preview_line"]
      }
    },
    "next_cursor": { "type": ["string", "null"] }
  },
  "required": ["results", "next_cursor"]
}
```

### Example — full-text search

```json
{
  "results": [
    {
      "path": "domains/psychology/wiki/concepts/cbt.md",
      "title": "Cognitive Behavioural Therapy",
      "type": "concept",
      "domain": "psychology",
      "preview_line": "…the relationship between **thoughts**, feelings, and behaviours…",
      "line": 8
    }
  ],
  "next_cursor": null
}
```

### Example — type-ahead (prefix mode)

```json
// Request: {"query": "cog", "prefix": true, "limit": 5}
{
  "results": [
    {
      "path": "domains/psychology/wiki/concepts/cognitive-load.md",
      "title": "Cognitive Load",
      "type": "concept",
      "domain": "psychology",
      "preview_line": "Working-memory capacity consumed by a learning task.",
      "line": null
    },
    {
      "path": "domains/psychology/wiki/concepts/cbt.md",
      "title": "Cognitive Behavioural Therapy",
      "type": "concept",
      "domain": "psychology",
      "preview_line": "A structured, time-limited psychotherapy…",
      "line": null
    }
  ],
  "next_cursor": null
}
```

---

## Tool 6: `resolve_wikilink`

Resolve a `[[slug]]` to its canonical repo-root-relative path.

### Input schema

```json
{
  "type": "object",
  "properties": {
    "slug": {
      "type": "string",
      "description": "Wikilink slug without brackets, e.g. \"cbt\" or \"2026-03-12-session\""
    },
    "domain": {
      "type": "string",
      "description": "Hint: prefer this domain when multiple matches exist. Omit to search all."
    }
  },
  "required": ["slug"]
}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "slug": { "type": "string" },
    "resolved_path": {
      "type": ["string", "null"],
      "description": "Null when unresolved"
    },
    "ambiguous": { "type": "boolean" },
    "candidates": {
      "type": "array",
      "items": { "type": "string" },
      "description": "All matching paths when ambiguous; empty otherwise"
    }
  },
  "required": ["slug", "resolved_path", "ambiguous", "candidates"]
}
```

### Example

```json
// Unambiguous
{"slug": "cbt", "resolved_path": "domains/psychology/wiki/concepts/cbt.md", "ambiguous": false, "candidates": []}

// Ambiguous
{"slug": "overview", "resolved_path": null, "ambiguous": true, "candidates": ["domains/psychology/wiki/overview.md", "domains/research-papers/wiki/overview.md"]}
```

---

## Tool 7: `run_lint`

Run the Densa validator and return structured diagnostics. Lint results are returned
in the `diagnostics` array — they are expected output, not JSON-RPC errors.

### Input schema

```json
{
  "type": "object",
  "properties": {
    "domain": {
      "type": "string",
      "description": "Restrict lint to this domain. Omit for all."
    },
    "select": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Rule IDs to run, e.g. [\"AGENTS001\", \"AGENTS006\"]. Omit for all rules."
    },
    "all": {
      "type": "boolean",
      "default": false,
      "description": "Equivalent to densa --all (include gitignored files). Default false."
    }
  }
}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "summary": {
      "type": "object",
      "properties": {
        "errors": { "type": "integer" },
        "warnings": { "type": "integer" },
        "files_checked": { "type": "integer" }
      },
      "required": ["errors", "warnings", "files_checked"]
    },
    "diagnostics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "line": { "type": ["integer", "null"] },
          "rule_id": {
            "type": "string",
            "description": "AGENTS001–AGENTS012 (and future IDs)"
          },
          "severity": { "type": "string", "enum": ["error", "warning"] },
          "message": { "type": "string" }
        },
        "required": ["path", "rule_id", "severity", "message"]
      }
    }
  },
  "required": ["summary", "diagnostics"]
}
```

### Example

```json
{
  "summary": { "errors": 0, "warnings": 1, "files_checked": 31 },
  "diagnostics": [
    {
      "path": "domains/psychology/wiki/concepts/cbt.md",
      "line": 14,
      "rule_id": "AGENTS008",
      "severity": "warning",
      "message": "last_validated is 192 days old (threshold: 180)"
    }
  ]
}
```

---

## Tool 8: `list_rules`

List the live AGENTS001–AGENTS0NN rule registry.

### Input schema

```json
{}
```

### Output schema

```json
{
  "type": "object",
  "properties": {
    "rules": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "description": "e.g. AGENTS001" },
          "name": { "type": "string", "description": "e.g. raw-immutability" },
          "description": { "type": "string" },
          "severity": { "type": "string", "enum": ["error", "warning"] },
          "staged_only": {
            "type": "boolean",
            "description": "True if the rule only runs in --staged mode"
          }
        },
        "required": ["id", "name", "description", "severity", "staged_only"]
      }
    }
  },
  "required": ["rules"]
}
```

### Example

```json
{
  "rules": [
    {
      "id": "AGENTS001",
      "name": "raw-immutability",
      "description": "raw/ files must not be modified",
      "severity": "error",
      "staged_only": true
    },
    {
      "id": "AGENTS002",
      "name": "log-append-only",
      "description": "log.md entries must be prepended, not rewritten",
      "severity": "error",
      "staged_only": true
    },
    {
      "id": "AGENTS006",
      "name": "wikilink-resolve",
      "description": "every [[wikilink]] must resolve to a real file",
      "severity": "error",
      "staged_only": false
    }
  ]
}
```

---

## Full round-trip example: `tools/call read_page`

```json
// → host sends
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "tools/call",
  "params": {
    "name": "read_page",
    "arguments": {"path": "domains/psychology/wiki/concepts/cbt.md"}
  }
}

// ← server replies
{
  "jsonrpc": "2.0",
  "id": 42,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"path\": \"domains/psychology/wiki/concepts/cbt.md\", \"is_raw\": false, \"frontmatter\": {\"title\": \"Cognitive Behavioural Therapy\", \"type\": \"concept\", \"updated\": \"2026-05-20\", \"sources\": [\"[[2026-03-12-session]]\"]}, \"body\": \"A structured, time-limited psychotherapy…\", \"salt\": null}"
      }
    ]
  }
}
```

---

## `@`-mention picker design constraints

The picker is host-native UX backed by the MCP tool surface (see `TK-0011`).
Both `list_pages` and `search_wiki` are shaped to serve it without a
translation layer:

- **Type-ahead**: `search_wiki(query="cog", prefix=true, limit=10)` — returns
  title-prefix matches with `preview_line` for display. No full-text scan needed.
- **Browse by type**: `list_pages(type="concept", limit=50)` — returns all
  concept pages paginated.
- **Picker rendering per row**: `title` + `preview_line` + `type` badge — all
  returned in a single `list_pages` or `search_wiki` call.
- **Insert**: resolved `path` → formatted as `[[slug]]` by the host (slug = stem
  of the filename without the date prefix for dated sources).

For the full picker pattern and host-specific examples (Claude Code slash command,
Cursor `@`-file flow), see `integrations/README.md` §"`@`-mention picker".
