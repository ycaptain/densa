"""``densa doctor`` — preflight diagnosis of a local Densa setup.

The #1 cause of "tried it, bounced" for a CLI-plus-git-hook tool is a
**silently broken local setup**: the hook isn't wired, ``PYTHONPATH``
is wrong, the Python is too old, or an active L2 domain's ``AGENTS.md``
doesn't parse. The failure mode is a confusing validator error, not a
clear "here's what to fix."

``densa doctor`` turns that silent-misconfig support thread into a
self-service ✓/✗ checklist. Each check prints its status and, on
failure, the **exact fix command**. The process exits non-zero if any
check fails, so it is usable in CI and setup scripts too.

Design notes:

- **Stdlib-only**, like the rest of ``_system/densa/`` (the package
  must stay ``cp -R``-able and the pre-commit hook imports it on every
  commit). No third-party deps.
- **Diagnoses setup, not content.** It deliberately does *not* run a
  full ``densa --all`` pass — that checks the vault's pages, which is
  a separate concern. The last check is a *dry probe* that the linter
  is importable and the repo is walkable, nothing more.
- **Robust when the setup is broken.** Every check is wrapped so one
  failing probe degrades to a ✗ row instead of crashing the whole
  command. A user with a half-broken vault is exactly who needs this.

The function ``run(args)`` is the entry point the CLI dispatcher calls.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# Mirrors pyproject.toml ``requires-python``. Kept as a literal (not
# parsed from pyproject) so ``doctor`` works from a ``cp -R``'d core
# that may not ship pyproject.toml.
MIN_PYTHON: Final[tuple[int, int]] = (3, 10)
HOOKS_PATH: Final[str] = "_system/hooks"


@dataclass
class CheckResult:
    """Outcome of one preflight check.

    ``ok`` drives the ✓/✗ glyph and the process exit code. ``detail``
    is a short human line shown next to the label. ``fix`` is the exact
    command (or one-line instruction) to run on failure — shown only
    when ``not ok``.
    """

    label: str
    ok: bool
    detail: str
    fix: str = ""


def add_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register ``densa doctor`` with the top-level argparse parser."""
    p = subparsers.add_parser(
        "doctor",
        help="diagnose a broken local setup (hook, PYTHONPATH, Python, L2)",
        description=(
            "Preflight check of your Densa setup. Prints a ✓/✗ checklist "
            "and, for each failure, the exact command to fix it. Exits "
            "non-zero if anything is wrong, so it is CI/script-usable. "
            "Checks setup (hook wiring, Python version, importability, "
            "active domain) — not vault content; run `densa --all` for that."
        ),
    )
    p.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )


def run(args: argparse.Namespace) -> int:
    """Execute ``densa doctor``. Returns 0 if all checks pass, 1 otherwise."""
    repo = _find_repo()
    checks = _run_checks(repo)

    fmt = getattr(args, "format", "text")
    if fmt == "json":
        _emit_json(repo, checks)
    else:
        _emit_text(repo, checks)

    return 0 if all(c.ok for c in checks) else 1


# --- check orchestration ----------------------------------------------------


def _run_checks(repo: Path | None) -> list[CheckResult]:
    """Run every preflight check, in display order.

    Each check is individually guarded: a probe that raises degrades to
    a ✗ row with the exception text, rather than aborting the whole
    command. A user running ``doctor`` is, by definition, possibly in a
    broken state.
    """
    checks = [_check_repo_found(repo), _check_python_version()]
    # The remaining checks need a repo root. If we couldn't find one,
    # the repo check above already failed and explains why; skip the
    # rest rather than emit a cascade of confusing failures.
    if repo is not None:
        checks.append(_guard(lambda: _check_hooks_wired(repo)))
        checks.append(_guard(lambda: _check_importable(repo)))
        checks.append(_guard(lambda: _check_active_domain(repo)))
        checks.append(_guard(lambda: _check_lint_runnable(repo)))
    return checks


def _guard(probe: Callable[[], CheckResult]) -> CheckResult:
    """Run a check, converting any unexpected exception into a ✗ row.

    Deliberately broad: ``doctor`` is the tool you reach for *because*
    something is wrong, so a probe blowing up on a half-broken vault
    must degrade to a ✗ row, never abort the whole checklist.
    """
    try:
        return probe()
    except Exception as exc:
        return CheckResult(
            label="(internal)",
            ok=False,
            detail=f"check raised {type(exc).__name__}: {exc}",
            fix="please file a bug with this message",
        )


def _check_repo_found(repo: Path | None) -> CheckResult:
    if repo is None:
        return CheckResult(
            label="vault root",
            ok=False,
            detail="no Densa vault found from here",
            fix=(
                "cd into your vault (a dir with AGENTS.md + _system/densa/), "
                "or run `densa init <dir>` to create one"
            ),
        )
    return CheckResult(
        label="vault root",
        ok=True,
        detail=str(repo),
    )


def _check_python_version() -> CheckResult:
    cur = sys.version_info[:2]
    ok = cur >= MIN_PYTHON
    want = ".".join(str(n) for n in MIN_PYTHON)
    have = ".".join(str(n) for n in cur)
    return CheckResult(
        label="python version",
        ok=ok,
        detail=f"{have} (need ≥ {want})",
        fix=(
            f"install Python {want}+ and re-run with it "
            f"(e.g. `python{want} -m densa doctor`)"
        ),
    )


def _check_hooks_wired(repo: Path) -> CheckResult:
    """The pre-commit hook is wired iff ``core.hooksPath`` points at
    ``_system/hooks`` *and* that directory holds the hook script.

    We accept either an exact ``core.hooksPath`` match or a hook already
    installed under the default ``.git/hooks/`` — both wire the
    validator into ``git commit``.
    """
    configured = _git_config(repo, "core.hooksPath")
    hook_in_managed = (repo / HOOKS_PATH / "pre-commit").is_file()
    hook_in_default = (repo / ".git" / "hooks" / "pre-commit").is_file()

    if configured == HOOKS_PATH and hook_in_managed:
        return CheckResult("pre-commit hook", True, f"core.hooksPath = {HOOKS_PATH}")
    if hook_in_default:
        return CheckResult(
            "pre-commit hook", True, ".git/hooks/pre-commit present",
        )
    detail = (
        f"core.hooksPath = {configured!r}" if configured
        else "core.hooksPath is unset"
    )
    return CheckResult(
        label="pre-commit hook",
        ok=False,
        detail=detail,
        fix="git config core.hooksPath _system/hooks",
    )


def _check_importable(repo: Path) -> CheckResult:
    """``import densa`` must succeed. If we are running, the *currently
    loaded* densa already imported — but the user may be probing a
    *different* vault (via ``--diff`` or a clone) whose ``_system/`` is
    not on the path that a fresh ``python -m densa`` would use.

    We report the version of the densa that is actually executing and
    whether this repo's ``_system`` is the one it came from.
    """
    from densa import __version__  # noqa: PLC0415 (always available here)

    loaded_from = Path(sys.modules["densa"].__file__ or "").resolve()
    this_repo_pkg = (repo / "_system" / "densa").resolve()
    same = loaded_from.parent == this_repo_pkg
    pkg_present = this_repo_pkg.is_dir()

    if not pkg_present:
        return CheckResult(
            label="densa importable",
            ok=False,
            detail=f"no _system/densa/ under {repo}",
            fix="run from a real vault, or `densa init` to scaffold one",
        )
    if same:
        return CheckResult(
            "densa importable", True, f"v{__version__} from this vault",
        )
    # Importable, but from a different install (e.g. a pipx densa running
    # against a cloned vault). That's fine — note it so a mismatched
    # version isn't a silent surprise.
    return CheckResult(
        "densa importable", True, f"v{__version__} (from {loaded_from.parent})",
    )


def _check_active_domain(repo: Path) -> CheckResult:
    """Every ``domains/<X>/`` with an L2 ``AGENTS.md`` must be readable
    and, if it carries YAML frontmatter, parse cleanly.

    A malformed L2 ``AGENTS.md`` (a ``---`` block with broken YAML) is a
    classic silent-breakage: the validator can't apply the per-domain
    overrides and the failure surfaces far from its cause. We parse each
    L2 here and report the first that won't.

    Note: an L2 ``AGENTS.md`` with **no** frontmatter is perfectly
    valid — most are prose overrides starting with ``# AGENTS.md``. We
    only flag a file that is unreadable or whose ``---`` block fails to
    parse (a :class:`ValueError` from the strict backend).
    """
    from densa.frontmatter import parse  # noqa: PLC0415

    domains_dir = repo / "domains"
    if not domains_dir.is_dir():
        return CheckResult(
            "active domain", True, "no domains/ yet (empty vault)",
        )

    domains = sorted(
        d for d in domains_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    if not domains:
        return CheckResult("active domain", True, "no live domains yet")

    broken: list[str] = []
    for d in domains:
        agents = d / "AGENTS.md"
        if not agents.is_file():
            continue  # L2 override is optional; absence is not an error.
        try:
            # A None return means "no frontmatter block" — valid for a
            # prose L2. Only a read error or a YAML ValueError is broken.
            parse(agents.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            broken.append(d.name)

    if broken:
        return CheckResult(
            label="active domain",
            ok=False,
            detail=f"L2 AGENTS.md has malformed frontmatter in: {', '.join(broken)}",
            fix=(
                "open the named domains/<X>/AGENTS.md and fix the YAML in "
                "its `---` frontmatter block"
            ),
        )
    return CheckResult(
        "active domain", True, f"{len(domains)} domain(s), L2 overrides parse",
    )


def _check_lint_runnable(repo: Path) -> CheckResult:
    """A *dry probe*: the slug index builds over this repo.

    This is deliberately **not** a full ``densa --all`` content pass —
    ``doctor`` checks setup, not pages. Building the index touches every
    markdown file's path (not its frontmatter rules), so a clean build
    means the linter can walk the vault and the repo is structurally
    sound enough to lint.
    """
    from densa.wikilink import build_index  # noqa: PLC0415

    build_index(repo)
    return CheckResult(
        "linter runnable", True, "slug index builds; `densa --all` is ready",
    )


# --- repo discovery ---------------------------------------------------------


def _find_repo() -> Path | None:
    """Locate the vault root, or ``None`` if there isn't one.

    Unlike ``cli._resolve_repo`` (which falls back to an install-relative
    path so the linter always has *something* to run on), ``doctor``
    returns ``None`` when no real vault is found — "you're not in a
    vault" is itself a diagnosis worth surfacing, not something to paper
    over with a fallback.
    """
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if _is_wiki_root(candidate):
            return candidate
    return None


def _is_wiki_root(path: Path) -> bool:
    """A real vault has both ``AGENTS.md`` and the in-repo
    ``_system/densa/`` package (mirrors ``cli._is_wiki_root``)."""
    return (path / "AGENTS.md").is_file() and (
        path / "_system" / "densa"
    ).is_dir()


def _git_config(repo: Path, key: str) -> str | None:
    """Read a git config value scoped to *repo*, or ``None`` if unset /
    git unavailable."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "config", "--get", key],
            check=False,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError):
        return None
    value = out.stdout.strip()
    return value or None


# --- output -----------------------------------------------------------------


def _emit_text(repo: Path | None, checks: list[CheckResult]) -> None:
    print("densa doctor — setup preflight")
    print()
    for c in checks:
        glyph = "✓" if c.ok else "✗"
        print(f"  {glyph} {c.label}: {c.detail}")
        if not c.ok and c.fix:
            print(f"      fix: {c.fix}")
    print()
    failed = [c for c in checks if not c.ok]
    if failed:
        n = len(failed)
        print(f"✗ {n} check{'s' if n != 1 else ''} failed — see fixes above.")
    else:
        print("✓ all checks passed — your setup is healthy.")


def _emit_json(repo: Path | None, checks: list[CheckResult]) -> None:
    import json  # noqa: PLC0415

    payload = {
        "repo": str(repo) if repo else None,
        "ok": all(c.ok for c in checks),
        "checks": [
            {
                "label": c.label,
                "ok": c.ok,
                "detail": c.detail,
                "fix": c.fix,
            }
            for c in checks
        ],
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
