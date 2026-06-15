"""Command-line entry point for densa.

Subcommands:

- ``lint``     — runs the checks against one of four sources
  (``--staged`` for pre-commit, ``--all`` for the full repo,
  ``--diff <base_ref>`` for a PR range, or one or more explicit
  paths).
- ``rules``    — print the rule registry as a table or JSON. Useful
  in ``--select`` discovery and in docs generation.
- ``version``  — print the package version.
- ``init``     — bootstrap a personal Densa vault from upstream.
- ``doctor``   — preflight a local setup (hook, Python, importability,
  active domain) and print a ✓/✗ checklist with fix commands.
- ``stats``    — read-only vault health report (page counts, types,
  orphans, log staleness, graph health).
- ``upgrade``  — pull upstream schema/validator changes into a vault.
- ``graph-config`` — generate ``.obsidian/graph.json`` tuned for a
  Densa vault (filtered, per-domain colors).

The **canonical lint invocation is the bare form** (``densa --all``,
``densa --staged``, ``densa --diff <ref>``, ``densa <paths>``); the
pre-commit hook, the CI workflow, ``noxfile.py``, and every test in
``_system/tests/`` use this form. The explicit ``lint`` subcommand
(``densa lint --all``) accepts the same flags and is provided for
ergonomic discoverability — ``densa --help`` lists both.

**No ``--fix`` flag by design.** Every red-line violation the
validator surfaces is something the human MUST consciously decide to
fix or bypass (per AGENTS.md §"Red lines"). Auto-fix would let the LLM silently mutate
load-bearing material on behalf of a decision the user hasn't taken.
The sanctioned escape hatches are ``git commit --no-verify`` and the
``WIKI_ALLOW_*`` bypass env vars; they require explicit intent.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from densa import __version__
from densa.commands import doctor as doctor_cmd
from densa.commands import graph_config as graph_config_cmd
from densa.commands import init as init_cmd
from densa.commands import migrate as migrate_cmd
from densa.commands import stats as stats_cmd
from densa.commands import upgrade as upgrade_cmd
from densa.config import RULES, Config, rule_by_id, rule_by_name
from densa.formatters import FORMATTERS
from densa.runner import lint_all, lint_diff, lint_paths, lint_staged


def _is_wiki_root(path: Path) -> bool:
    """Double-factor check: a real wiki repo has both AGENTS.md and the
    in-repo ``_system/densa/`` package. This stops a parent vault that
    happens to ship its own ``AGENTS.md`` from shadowing the wiki we're
    actually validating.
    """
    return (path / "AGENTS.md").is_file() and (
        path / "_system" / "densa"
    ).is_dir()


def _resolve_repo() -> Path:
    """Discover the repo root.

    Order:
      1. ``git rev-parse --show-toplevel`` (cheap, accurate inside any
         git checkout) — but only accept it if it passes the
         ``_is_wiki_root`` double-factor check.
      2. Walk up from CWD looking for an ``AGENTS.md`` that also
         satisfies the double-factor check.
      3. Fall back to the install-relative ``parents[2]`` of this file
         (works when densa is invoked from inside its package
         directly, e.g. via ``python -m densa`` with PYTHONPATH set).
    """
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            top = Path(out).resolve()
            if _is_wiki_root(top):
                return top
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if _is_wiki_root(candidate):
            return candidate

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
                "(use `densa rules` to list available IDs)"
            )
        out.add(rid)
    return frozenset(out)


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser.

    The top-level parser owns only ``--version`` and the subcommand
    table — it deliberately carries **no** ``paths`` positional, because
    a variadic top-level positional cannot coexist with
    ``add_subparsers`` (argparse splits the tokens, so
    ``densa init my-vault`` mis-parses as ``paths=['init'],
    command='my-vault'`` → "invalid choice"). The lint flags + ``paths``
    live on the explicit ``lint`` subparser instead; :func:`main`
    rewrites the canonical bare form (``densa --all``,
    ``densa path1 path2``) to ``densa lint <same args>`` before parsing,
    so both forms work and ``densa --help`` still lists every subcommand.
    """
    parser = argparse.ArgumentParser(
        prog="densa",
        description=(
            "densa — the schema validator for a Densa vault. "
            "Densa (the project) is the markdown template; `densa` (this CLI) "
            "is the tool that validates it against the L1 schema "
            "(see AGENTS.md §\"Frontmatter schema\" and §\"Red lines\"). Also exposes `init` / `upgrade` "
            "for vault bootstrap."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"densa {__version__}",
    )

    sub = parser.add_subparsers(dest="command")

    # Explicit `lint` subcommand. Mirrors the top-level lint flags so both
    # `densa --all` (canonical; used by the pre-commit hook and CI) and
    # `densa lint --all` (explicit; helpful for discoverability) work.
    lint_sub = sub.add_parser(
        "lint",
        help="run the linter (default command; same flags as bare `densa`)",
    )
    _add_lint_args(lint_sub)

    rules = sub.add_parser("rules", help="list all rules with their IDs")
    rules.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format",
    )

    sub.add_parser("version", help="print the package version")

    init_cmd.add_parser(sub)
    doctor_cmd.add_parser(sub)
    stats_cmd.add_parser(sub)
    upgrade_cmd.add_parser(sub)
    migrate_cmd.add_parser(sub)
    graph_config_cmd.add_parser(sub)

    sub.add_parser(
        "mcp",
        help="run the read-only MCP server over stdio (JSON-RPC 2.0)",
    )

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
    group.add_argument(
        "--diff",
        metavar="BASE_REF",
        default=None,
        help=(
            "check the BASE_REF..HEAD range using the staged rules + "
            "file rules; lets CI enforce AGENTS001/002/007 on every PR "
            "(e.g. --diff origin/main)"
        ),
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
    if not (args.staged or args.all or args.diff or args.paths):
        print(
            "error: specify --staged, --all, --diff BASE_REF, "
            "or one or more PATHs",
            file=sys.stderr,
        )
        return 2
    config = Config(
        select=args.select,
        ignore=args.ignore,
        no_warnings=args.no_warnings,
    )
    repo = _resolve_repo()

    try:
        if args.staged:
            report = lint_staged(repo, config)
        elif args.diff:
            report = lint_diff(repo, args.diff, config)
        elif args.all:
            report = lint_all(repo, config)
        else:
            report = lint_paths(repo, args.paths, config)
    except ValueError as exc:
        # lint_paths raises when an explicit path is outside the repo —
        # surface as a clean error rather than a traceback.
        print(f"error: {exc}", file=sys.stderr)
        return 2

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


def _cmd_mcp(_: argparse.Namespace) -> int:
    # Lazy import keeps the MCP server (and its transport surface) off the
    # import path for the common lint invocation.
    from densa.mcp.server import serve  # noqa: PLC0415

    serve(_resolve_repo(), sys.stdin, sys.stdout)
    return 0


_DISPATCH = {
    "lint": _cmd_lint,
    "rules": _cmd_rules,
    "version": _cmd_version,
    "init": init_cmd.run,
    "doctor": doctor_cmd.run,
    "stats": stats_cmd.run,
    "upgrade": upgrade_cmd.run,
    "migrate": migrate_cmd.run,
    "graph-config": graph_config_cmd.run,
    "mcp": _cmd_mcp,
}

# Tokens that must reach the top-level parser verbatim instead of being
# folded into the bare-lint form (so `densa --help` lists subcommands and
# `densa --version` prints the version).
_TOP_LEVEL_FLAGS = ("-h", "--help", "--version")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Disambiguate the canonical bare-lint form from a subcommand. The
    # `paths` positional lives only on the `lint` subparser (see
    # `_build_parser`), so any first token that is neither a subcommand
    # nor a top-level flag is rewritten to `lint <args>`. This is what
    # lets `densa --all` / `densa foo.md` and `densa init my-vault`
    # coexist without argparse mis-splitting the positionals.
    if not argv or (
        argv[0] not in _DISPATCH and argv[0] not in _TOP_LEVEL_FLAGS
    ):
        argv = ["lint", *argv]

    parser = _build_parser()
    args = parser.parse_args(argv)
    return _DISPATCH[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
