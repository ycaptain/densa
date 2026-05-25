---
type: concept
domain: hello-world
created: 2026-05-24
updated: 2026-05-24
sources: ["[[docstring-overview-summary]]"]
tags: [python, documentation]
aliases: ["__doc__", "doc-string"]
status: active
compiled_against: 2
last_validated: 2026-05-24
---

# Docstring

A string literal that appears as the first statement of a Python
module, function, class, or method. Attached to the object as its
`__doc__` attribute and therefore available at runtime to `help()`,
IDE hovers, Sphinx, autocomplete engines, and test frameworks.

## Why it matters

Unlike a `# comment`, a docstring survives parsing and lives on the
object. That makes it visible to every downstream tool that
introspects Python objects.

## Appearances

| Source | Where |
|---|---|
| [[docstring-overview-summary]] | first definition + tooling chain |

(One row per summary citing this concept. New ingests append rows
here rather than fragmenting the concept across multiple pages.)

## See also

- [[docstring-style]] — choosing between PEP 257, Google, and NumPy.
