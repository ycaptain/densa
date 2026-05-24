"""densa — schema + wikilink validator for a Densa vault.

Public surface:

    from densa import (
        Diagnostic, Report, Severity,
        lint_all, lint_diff, lint_paths, lint_staged,
    )

The CLI lives in :mod:`densa.cli` and is invoked as either
``python -m densa`` or via the ``densa`` console script when the
package is installed.

This package targets stdlib-only at import time: the pre-commit hook
runs on every ``git commit``, so a fast cold start matters. The
optional ``pyyaml`` dependency is loaded lazily by
:mod:`densa.frontmatter` and **only used when the user opts in**
via ``DENSA_STRICT=1`` (typically together with
``pip install -e ".[strict]"``); the stdlib default is deterministic
across machines regardless of whether pyyaml happens to be installed.
"""

from __future__ import annotations

from densa.report import Diagnostic, Report, Severity
from densa.runner import lint_all, lint_diff, lint_paths, lint_staged

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
