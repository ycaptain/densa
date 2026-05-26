"""``densa init`` — bootstrap a personal Densa vault from upstream.

Design goals:

- The vault is a **fork**, not a copy. ``git remote add upstream`` is
  load-bearing: it's how the user later runs ``densa upgrade``.
- **No silent decisions.** Every irreversible step (clone destination,
  example-domain disposition, first commit) is interactive by default.
  ``--yes`` accepts every default for unattended use.
- **Idempotent re-entry.** If the user Ctrl-C's halfway through, the
  next ``densa init`` resumes from where it left off (re-running
  produces no net diff).
- **No agent SDK dependency at import time.** Auto-injection is an
  optional flag; the implementation is loaded lazily.

The function ``run(args)`` is the entry point the CLI dispatcher
calls. Tests exercise the same function with a fake git binary on
PATH and an isolated cwd.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final

UPSTREAM_DEFAULT: Final[str] = "https://github.com/ycaptain/densa.git"
EXAMPLE_DOMAINS: Final[tuple[str, ...]] = (
    "research-papers",
    "workspace",
    "psychology",
)


def add_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register ``densa init`` with the top-level argparse parser."""
    p = subparsers.add_parser(
        "init",
        help="bootstrap a personal Densa vault (clone, wire hooks, scaffold)",
        description=(
            "Bootstrap a personal Densa vault from upstream. "
            "Clones the repo, wires the pre-commit hook, walks you "
            "through example-domain disposition, and (optionally) "
            "injects the bootstrap prompt into your AI agent."
        ),
    )
    p.add_argument(
        "destination",
        nargs="?",
        default=None,
        help=(
            "directory to clone into (default: prompt). Pass `.` to "
            "init the current empty directory."
        ),
    )
    p.add_argument(
        "--upstream",
        default=UPSTREAM_DEFAULT,
        help=f"upstream repo URL (default: {UPSTREAM_DEFAULT})",
    )
    p.add_argument(
        "--yes", "-y",
        action="store_true",
        help="accept every default; non-interactive",
    )
    p.add_argument(
        "--auto-inject",
        choices=("cursor", "claude-code", "codex", "auto", "none"),
        default="none",
        help=(
            "after bootstrap, inject docs/bootstrap.md into "
            "the named AI agent. `auto` detects which agent's CLI is on "
            "PATH; `none` (default) just prints next-step instructions."
        ),
    )
    p.add_argument(
        "--examples",
        choices=("keep-all", "keep-research-papers", "legacy-all", "remove-all", "prompt"),
        default="prompt",
        help="example-domain disposition (default: prompt interactively)",
    )


def run(args: argparse.Namespace) -> int:
    """Execute ``densa init``. Returns the CLI exit code."""
    if not _git_available():
        _err("git is not on PATH. Install git and retry.")
        return 2

    dest = _resolve_destination(args.destination, args.yes)
    if dest is None:
        return 2

    try:
        _ensure_clone(dest, args.upstream)
        _wire_upstream(dest, args.upstream)
        _wire_hooks(dest)
        _handle_examples(dest, args.examples, args.yes)
    except _InitError as exc:
        _err(str(exc))
        return 1

    _print_next_steps(dest, args.auto_inject)

    if args.auto_inject != "none":
        # Lazy import: agent_inject pulls in platform-clipboard logic
        # only the --auto-inject path needs, so we keep `densa init`
        # without that flag importing nothing extra.
        from densa.commands import agent_inject  # noqa: PLC0415

        rc = agent_inject.inject(dest, args.auto_inject)
        if rc != 0:
            return rc

    return 0


# --- internals --------------------------------------------------------------


class _InitError(RuntimeError):
    """Recoverable failure during ``densa init``. The CLI surfaces
    the message and returns a non-zero exit code; no traceback."""


def _git_available() -> bool:
    return shutil.which("git") is not None


def _resolve_destination(raw: str | None, yes: bool) -> Path | None:
    """Resolve the destination path the user wants to init into.

    - ``raw is None`` → prompt (unless ``--yes``, where we error out
      because we have no sensible default for "where do you keep your
      vaults?").
    - ``raw == "."`` → current cwd (must be empty or non-existent).
    - otherwise → ``Path(raw).expanduser().resolve()``.
    """
    if raw is None:
        if yes:
            _err("--yes requires an explicit destination (positional argument).")
            return None
        raw = input("Where should your vault live? [./my-vault] ").strip() or "./my-vault"

    dest = Path(raw).expanduser().resolve()

    if dest.exists() and any(dest.iterdir()):
        _err(
            f"destination {dest} is not empty. "
            "Pick an empty directory or remove the existing one."
        )
        return None

    return dest


def _ensure_clone(dest: Path, upstream: str) -> None:
    """Clone ``upstream`` into ``dest`` if not already cloned."""
    if (dest / ".git").is_dir():
        # Already cloned — idempotent re-entry.
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    rc = _run_git(["clone", upstream, str(dest)], cwd=dest.parent)
    if rc != 0:
        raise _InitError(f"git clone failed (exit {rc}). Check upstream URL and network.")


def _wire_upstream(dest: Path, upstream: str) -> None:
    """Ensure the cloned repo has both ``origin`` and ``upstream`` remotes.

    Default ``git clone`` sets only ``origin`` pointing at ``upstream``.
    For the fork-flow we want ``origin`` = user's fork (which they'll
    set later when they push) and ``upstream`` = the canonical repo.
    Rename the default origin → upstream so ``git pull upstream main``
    works immediately; the user can later ``git remote set-url origin
    <their-fork>`` once they've forked on GitHub.
    """
    remotes = _git_output(["remote"], cwd=dest).splitlines()
    if "upstream" in remotes:
        return
    if "origin" in remotes:
        _run_git(["remote", "rename", "origin", "upstream"], cwd=dest)
    else:
        _run_git(["remote", "add", "upstream", upstream], cwd=dest)


def _wire_hooks(dest: Path) -> None:
    """Wire the pre-commit hook directory."""
    rc = _run_git(
        ["config", "core.hooksPath", "_system/hooks"],
        cwd=dest,
    )
    if rc != 0:
        raise _InitError("failed to set core.hooksPath")


def _handle_examples(dest: Path, mode: str, yes: bool) -> None:
    """Apply the example-domain disposition.

    Modes:
    - ``keep-all`` — no-op (every example stays live).
    - ``keep-research-papers`` — keep research-papers, legacy the rest.
    - ``legacy-all`` — move every example to ``domains/.legacy-example-<X>/``.
    - ``remove-all`` — ``git rm -r`` every example.
    - ``prompt`` — ask interactively (unless ``yes``, defaults to
      ``keep-research-papers`` which is the bootstrap-prompt's
      recommendation).
    """
    if mode == "prompt":
        mode = _prompt_examples_mode(yes)
    if mode == "keep-all":
        return

    for name in EXAMPLE_DOMAINS:
        src = dest / "domains" / name
        if not src.exists():
            continue

        if mode == "keep-research-papers" and name == "research-papers":
            continue
        if mode == "legacy-all" or (
            mode == "keep-research-papers" and name != "research-papers"
        ):
            target = dest / "domains" / f".legacy-example-{name}"
            _run_git(["mv", str(src.relative_to(dest)), str(target.relative_to(dest))], cwd=dest)
        elif mode == "remove-all":
            _run_git(["rm", "-r", str(src.relative_to(dest))], cwd=dest)


def _prompt_examples_mode(yes: bool) -> str:
    if yes:
        return "keep-research-papers"
    print()
    print("Three example domains ship with Densa:")
    print("  1) research-papers (light)")
    print("  2) workspace       (medium)")
    print("  3) psychology      (heavy, fictional therapy arc)")
    print()
    print("What would you like to do with them?")
    print("  [k] keep all three live")
    print("  [r] keep research-papers, move others to domains/.legacy-example-*  (recommended)")
    print("  [l] move all three to domains/.legacy-example-*")
    print("  [x] remove all three  (git rm)")
    print()
    choice = input("Choice [r]: ").strip().lower() or "r"
    return {
        "k": "keep-all",
        "r": "keep-research-papers",
        "l": "legacy-all",
        "x": "remove-all",
    }.get(choice, "keep-research-papers")


def _print_next_steps(dest: Path, auto_inject: str) -> None:
    rel = _format_path(dest)
    print()
    print(f"✓ Densa vault initialised at {rel}")
    print()
    print("Next steps:")
    print(f"  1. cd {rel}")
    print("  2. (Fork ycaptain/densa on GitHub and `git remote add origin`")
    print("      pointing at your fork, when you're ready to push.)")
    if auto_inject == "none":
        print("  3. Open the folder in Cursor / Claude Code / Codex / Cline")
        print("     and paste docs/bootstrap.md into the chat.")
    else:
        print("  3. We'll inject the bootstrap prompt into your agent now...")
    print()


def _format_path(p: Path) -> str:
    """Render an absolute path as a `~/` or relative-to-cwd string when
    that's shorter; otherwise return the absolute path."""
    home = Path.home()
    try:
        rel_home = p.relative_to(home)
        return "~/" + str(rel_home)
    except ValueError:
        pass
    try:
        rel_cwd = p.relative_to(Path.cwd())
        return "./" + str(rel_cwd)
    except ValueError:
        return str(p)


def _run_git(argv: list[str], cwd: Path) -> int:
    return subprocess.run(
        ["git", *argv],
        cwd=cwd,
        check=False,
    ).returncode


def _git_output(argv: list[str], cwd: Path) -> str:
    return subprocess.run(
        ["git", *argv],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    ).stdout


def _err(msg: str) -> None:
    print(f"densa init: error: {msg}", file=sys.stderr)
