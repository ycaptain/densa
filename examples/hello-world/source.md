# What is a docstring?

A **docstring** is a string literal that appears as the first statement
of a Python module, function, class, or method. Unlike a regular code
comment (which the parser discards), the docstring is attached to the
object as its `__doc__` attribute and is therefore available at runtime
to tooling: `help()`, IDE hovers, Sphinx, autocomplete engines, and
test frameworks.

## Why docstrings beat comments for public APIs

A `# comment` is invisible after the source file is loaded. A
docstring travels with the object. Three concrete consequences:

1. **Discoverable.** `help(foo)` in a REPL prints the docstring; it
   prints nothing for a `# comment`-only function.
2. **Tooling-rendered.** Sphinx, mkdocs, pdoc all consume docstrings.
   None of them parse comments.
3. **Type-checker friendly.** Modern type checkers (mypy, pyright)
   surface docstrings in IDE hovers next to type signatures.

## Conventions worth following

Most codebases settle on one of three formats:

- **PEP 257** — minimal: a one-line summary, blank line, optional
  longer prose. The standard library uses this.
- **Google style** — adds `Args:` / `Returns:` / `Raises:` sections.
  Sphinx renders these natively via `napoleon`.
- **NumPy style** — heavier, with explicit `Parameters` /
  `Returns` headers. Common in scientific Python.

Pick one per project and enforce it via `pydocstyle` or `ruff`'s
`D` rules. Mixing styles in one codebase costs more than it saves.

## When to skip the docstring

Trivial private helpers (`_inc`, `_swap`) don't need them. A precise
function name and clear type signature already convey the intent. A
docstring on top adds noise.

The reverse is also true: a docstring that says *"increment by 1"*
on a function called `increment_by_one` is the same kind of noise.
The docstring should explain *why* and the contract; the name and
signature explain *what*.

---

*Adapted from PEP 257 + the Python tutorial. Single-page introduction
intended for the `hello-world` Densa demo — not a comprehensive
reference.*
