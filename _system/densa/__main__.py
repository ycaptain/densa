"""Allow ``python -m densa``."""

from __future__ import annotations

import sys

from densa.cli import main

if __name__ == "__main__":
    sys.exit(main())
