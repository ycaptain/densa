"""Subcommand implementations for the ``densa`` CLI.

The lint / rules / version commands live in :mod:`densa.cli` (they
predate this split). New high-level commands (``init``, ``upgrade``,
future ``new-domain``) are isolated here to keep ``cli.py`` an
argument-parsing thin shell.

Each command module exports:

- ``add_parser(subparsers)`` — register the subcommand with argparse.
- ``run(args)`` → ``int`` — execute the command, return the exit code.

The CLI dispatch table in :mod:`densa.cli` consumes both halves.
"""

from densa.commands import init, upgrade

__all__ = ["init", "upgrade"]
