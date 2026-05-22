"""wikilint — schema + wikilink validator for the llm-wiki vault.

Public surface:

    from wikilint import (
        Diagnostic, Report, Severity,
        lint_all, lint_diff, lint_paths, lint_staged,
    )

The CLI lives in :mod:`wikilint.cli` and is invoked as either
``python -m wikilint`` or via the ``wikilint`` console script when the
package is installed.

This package targets stdlib-only at import time: the pre-commit hook
runs on every ``git commit``, so a fast cold start matters. The single
optional dependency (``pyyaml``) is loaded lazily by
:mod:`wikilint.frontmatter` only when the strict backend is selected
(`pip install -e ".[strict]"` or YAML features the stdlib parser
cannot handle).
"""

from __future__ import annotations

from wikilint.report import Diagnostic, Report, Severity
from wikilint.runner import lint_all, lint_diff, lint_paths, lint_staged

__all__ = [
    "Diagnostic",
    "Report",
    "Severity",
    "__version__",
    "lint_all",
    "lint_diff",
    "lint_paths",
    "lint_staged",
]

__version__ = "0.1.0"
