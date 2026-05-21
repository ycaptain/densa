"""Command-line entry point for wikilint.

Three subcommands:

- ``lint``     — the default. Runs the checks against one of three
  sources (``--staged`` for pre-commit, ``--all`` for the full repo,
  or one or more explicit paths).
- ``rules``    — print the rule registry as a table or JSON. Useful
  in ``--select`` discovery and in docs generation.
- ``version``  — print the package version.

Backwards-compatibility: the top-level flags ``--staged`` / ``--all`` /
positional paths are also accepted directly on the ``wikilint`` invocation
(without the ``lint`` subcommand). This kept the legacy ``validate.py
--all`` shim working during the v0.2 → v0.3 cutover; the shim itself now
lives in ``attic/scripts/validate.py`` and ``python -m wikilint`` is the
canonical entry point.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from wikilint import __version__
from wikilint.config import RULES, Config, rule_by_id, rule_by_name
from wikilint.formatters import FORMATTERS
from wikilint.runner import lint_all, lint_paths, lint_staged


def _resolve_repo() -> Path:
    """Discover the repo root by walking up from CWD looking for AGENTS.md.

    Falls back to the legacy ``parents[2]`` heuristic used by the old
    script if no AGENTS.md is found upward.
    """
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").exists():
            return candidate
    # Last resort: the install-relative path that worked for the old script.
    return Path(__file__).resolve().parents[2]


def _normalise_rule_token(token: str) -> str | None:
    """Accept either ``AGENTS003`` or ``frontmatter-required-keys`` and
    return the canonical rule ID, or ``None`` if unknown."""
    if rule_by_id(token):
        return token
    by_name = rule_by_name(token)
    return by_name.id if by_name else None


def _parse_rule_csv(raw: str | None) -> frozenset[str]:
    if not raw:
        return frozenset()
    out: set[str] = set()
    for token in (t.strip() for t in raw.split(",")):
        if not token:
            continue
        rid = _normalise_rule_token(token)
        if rid is None:
            raise argparse.ArgumentTypeError(
                f"unknown rule: {token!r} "
                "(use `wikilint rules` to list available IDs)"
            )
        out.add(rid)
    return frozenset(out)


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser.

    The parser doubles as the ``lint`` subcommand's parser: any
    invocation without a subcommand (``wikilint --all``,
    ``wikilint --staged``, ``wikilint path1 path2``) is interpreted as
    ``wikilint lint <same args>``. This also keeps the archived
    ``validate.py --all`` shim (``attic/scripts/validate.py``)
    working without explicit aliasing.
    """
    parser = argparse.ArgumentParser(
        prog="wikilint",
        description=(
            "Validate an llm-wiki vault against the L1 schema "
            "(see AGENTS.md §3, §6)."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"wikilint {__version__}",
    )
    _add_lint_args(parser)

    sub = parser.add_subparsers(dest="command")

    rules = sub.add_parser("rules", help="list all rules with their IDs")
    rules.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format",
    )

    sub.add_parser("version", help="print the package version")

    return parser


def _add_lint_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--staged",
        action="store_true",
        help="check the git staged set (used by the pre-commit hook)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="check every markdown file in the repo",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="explicit file paths to check",
    )
    parser.add_argument(
        "--format",
        choices=tuple(FORMATTERS.keys()),
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--select",
        type=_parse_rule_csv,
        default=frozenset(),
        help="comma-separated rule IDs / names to run exclusively",
    )
    parser.add_argument(
        "--ignore",
        type=_parse_rule_csv,
        default=frozenset(),
        help="comma-separated rule IDs / names to skip",
    )
    parser.add_argument(
        "--no-warnings",
        action="store_true",
        help="drop warning-level diagnostics from output",
    )


def _cmd_lint(args: argparse.Namespace) -> int:
    if not (args.staged or args.all or args.paths):
        print(
            "error: specify --staged, --all, or one or more PATHs",
            file=sys.stderr,
        )
        return 2
    config = Config(
        select=args.select,
        ignore=args.ignore,
        no_warnings=args.no_warnings,
    )
    repo = _resolve_repo()

    if args.staged:
        report = lint_staged(repo, config)
    elif args.all:
        report = lint_all(repo, config)
    else:
        report = lint_paths(repo, args.paths, config)

    formatter = FORMATTERS[args.format]
    formatter(report, args.no_warnings)
    return 1 if report.has_errors else 0


def _cmd_rules(args: argparse.Namespace) -> int:
    if args.format == "json":
        payload = [
            {
                "id": r.id,
                "name": r.name,
                "summary": r.summary,
                "anchor": r.agents_anchor,
                "default_enabled": r.default_enabled,
            }
            for r in RULES
        ]
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    width_id = max(len(r.id) for r in RULES)
    width_name = max(len(r.name) for r in RULES)
    header = f"{'ID':<{width_id}}  {'NAME':<{width_name}}  ANCHOR"
    print(header)
    print("-" * len(header))
    for r in RULES:
        print(
            f"{r.id:<{width_id}}  {r.name:<{width_name}}  {r.agents_anchor}"
        )
        print(f"{' ' * width_id}  {r.summary}")
    return 0


def _cmd_version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    command = args.command

    # Legacy mode: no subcommand but lint flags were given.
    if command is None:
        return _cmd_lint(args)

    dispatch = {
        "lint": _cmd_lint,
        "rules": _cmd_rules,
        "version": _cmd_version,
    }
    return dispatch[command](args)


if __name__ == "__main__":
    sys.exit(main())
