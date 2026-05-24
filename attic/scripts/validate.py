#!/usr/bin/env python3
"""Deprecation shim — forwards to the :mod:`densa` package.

The validator used to live in this file as ~500 lines of glue. It has
been refactored into the :mod:`densa` package under
``_system/densa/``. This shim keeps the legacy entry point working
for one release cycle so users with stale ``core.hooksPath`` configs
or external CI scripts don't break overnight.

Invoke directly via ``python -m densa`` going forward.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SYSTEM = _HERE.parent
if str(_SYSTEM) not in sys.path:
    sys.path.insert(0, str(_SYSTEM))

from densa.cli import main  # noqa: E402

if __name__ == "__main__":
    if os.environ.get("DENSA_SUPPRESS_DEPRECATION") != "1":
        print(
            "warning: _system/scripts/validate.py is a deprecation shim. "
            "Use `python -m densa` (or `densa` if installed) instead. "
            "Set DENSA_SUPPRESS_DEPRECATION=1 to silence this notice.",
            file=sys.stderr,
        )
    sys.exit(main())
