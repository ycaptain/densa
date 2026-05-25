---
type: concept
domain: hello-world
created: 2026-05-24
updated: 2026-05-24
sources: ["[[docstring-overview-summary]]"]
tags: [python, documentation, conventions]
aliases: ["docstring-format", "docstring-conventions"]
status: active
compiled_against: 2
last_validated: 2026-05-24
---

# Docstring style

The choice of which docstring **format** a project uses. Three
canonical options; pick one and enforce mechanically.

| Style | Shape | Renders natively in |
|---|---|---|
| **PEP 257** | one-line summary, blank line, optional longer prose | the Python standard library |
| **Google** | `Args:` / `Returns:` / `Raises:` sections | Sphinx + `napoleon` |
| **NumPy** | explicit `Parameters` / `Returns` headers | scientific Python (NumPy, SciPy, scikit-learn) |

Enforcement: `pydocstyle` or `ruff`'s `D` rules. Mixing styles in one
codebase costs more than it saves.

## Appearances

| Source | Where |
|---|---|
| [[docstring-overview-summary]] | three-style overview + enforcement note |

## See also

- [[docstring]] — the underlying language feature.
