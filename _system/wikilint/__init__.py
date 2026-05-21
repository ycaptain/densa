"""wikilint — schema + wikilink validator for the llm-wiki vault.

Public surface:

    from wikilint import lint_paths, lint_staged, lint_all, Diagnostic, Severity

The CLI lives in :mod:`wikilint.cli` and is invoked as either
``python -m wikilint`` or via the ``wikilint`` console script when the
package is installed.

This package targets stdlib-only at import time: the pre-commit hook runs
on every ``git commit``, so a fast cold start matters. Optional
dependencies (``pyyaml``, ``pydantic``) are loaded lazily by
:mod:`wikilint.frontmatter` and :mod:`wikilint.config` only when their
respective backends are explicitly selected.
"""

from __future__ import annotations

from wikilint.report import Diagnostic, Report, Severity
from wikilint.runner import lint_all, lint_paths, lint_staged

__all__ = [
    "Diagnostic",
    "Report",
    "Severity",
    "__version__",
    "lint_all",
    "lint_paths",
    "lint_staged",
]

__version__ = "0.1.0"
