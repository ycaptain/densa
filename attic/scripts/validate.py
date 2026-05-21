#!/usr/bin/env python3
"""Deprecation shim — forwards to the :mod:`wikilint` package.

The validator used to live in this file as ~500 lines of glue. It has
been refactored into the :mod:`wikilint` package under
``_system/wikilint/``. This shim keeps the legacy entry point working
for one release cycle so users with stale ``core.hooksPath`` configs
or external CI scripts don't break overnight.

Invoke directly via ``python -m wikilint`` going forward.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SYSTEM = _HERE.parent
if str(_SYSTEM) not in sys.path:
    sys.path.insert(0, str(_SYSTEM))

from wikilint.cli import main  # noqa: E402

if __name__ == "__main__":
    if os.environ.get("WIKILINT_SUPPRESS_DEPRECATION") != "1":
        print(
            "warning: _system/scripts/validate.py is a deprecation shim. "
            "Use `python -m wikilint` (or `wikilint` if installed) instead. "
            "Set WIKILINT_SUPPRESS_DEPRECATION=1 to silence this notice.",
            file=sys.stderr,
        )
    sys.exit(main())
