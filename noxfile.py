"""Task runner. Run `nox -l` to list sessions, `nox -s check` for the full gate."""

# -----------------------------------------------------------------------------
# Design notes (for contributors editing this file — not shown by `nox -l`).
#
# Audience split:
#   - Vault users (non-programmers running the template as their wiki)
#     MUST NOT need nox. Their entry points are the pre-commit hook
#     (`_system/hooks/pre-commit`, pure stdlib) and the `densa` CLI.
#   - Contributors (hacking the validator / prompts / schema) use nox
#     to run the same gates CI runs.
#
# Why nox vs alternatives:
#   - make: not cross-platform; BSD-make ≠ GNU-make. An earlier Makefile
#     broke on contributors whose base Python lacked `pip install -e .`.
#   - just: nice, but requires a separate Rust binary install.
#   - invoke: older Python task runner; nox has largely replaced it.
#   - hatch / tox: heavier project managers; we only need a task runner
#     (CI's matrix handles multi-Python-version testing).
#
# We follow the Scientific Python Development Guide's PY007 recommendation:
# nox is the modern OSS Python standard for task runners in 2026.
#
# Sessions use `venv_backend = "none"` so they reuse the contributor's
# current Python env — no per-session venv churn. Run `pip install -e
# ".[dev]"` once; every session is then instant. CI uses these same
# sessions verbatim.
# -----------------------------------------------------------------------------

from __future__ import annotations

import nox

nox.options.default_venv_backend = "none"
nox.options.sessions = ["check"]


@nox.session
def lint(session: nox.Session) -> None:
    """Run densa over the whole repo."""
    # PYTHONPATH trick mirrors `_system/hooks/pre-commit`: lets
    # contributors run `nox -s lint` before `pip install -e .`.
    session.env["PYTHONPATH"] = "_system"
    session.run("python", "-m", "densa", "--all", *session.posargs)


@nox.session(name="lint-strict")
def lint_strict(session: nox.Session) -> None:
    """Run densa with DENSA_STRICT=1 (pyyaml backend)."""
    session.env["PYTHONPATH"] = "_system"
    session.env["DENSA_STRICT"] = "1"
    session.run("python", "-m", "densa", "--all", *session.posargs)


@nox.session(name="lint-diff")
def lint_diff(session: nox.Session) -> None:
    """Run densa --diff against a base ref (default: origin/main)."""
    # Override the base ref with `nox -s lint-diff -- origin/develop`.
    session.env["PYTHONPATH"] = "_system"
    base = session.posargs[0] if session.posargs else "origin/main"
    session.run("python", "-m", "densa", "--diff", base)


@nox.session
def test(session: nox.Session) -> None:
    """Run pytest. Filter with `nox -s test -- -k <pattern>`."""
    session.run("python", "-m", "pytest", *session.posargs)


@nox.session
def ruff(session: nox.Session) -> None:
    """Run ruff check on the repo."""
    session.run("python", "-m", "ruff", "check", ".", *session.posargs)


@nox.session(name="ruff-fix")
def ruff_fix(session: nox.Session) -> None:
    """Run ruff check --fix to auto-apply safe fixes."""
    session.run("python", "-m", "ruff", "check", "--fix", ".", *session.posargs)


@nox.session
def mypy(session: nox.Session) -> None:
    """Run mypy --strict on the validator package."""
    session.run("python", "-m", "mypy", *session.posargs)


@nox.session
def check(session: nox.Session) -> None:
    """Run the full CI gate: lint + test + ruff + mypy."""
    session.notify("lint")
    session.notify("test")
    session.notify("ruff")
    session.notify("mypy")


@nox.session
def hook(session: nox.Session) -> None:
    """Wire the pre-commit hook (one-time per clone) and verify."""
    session.run("git", "config", "core.hooksPath", "_system/hooks", external=True)
    result = session.run(
        "git", "config", "--get", "core.hooksPath",
        external=True, silent=True,
    )
    if result is None:
        session.error("git config returned no output")
    actual = result.strip()
    session.log(f"core.hooksPath = {actual}")
    if actual != "_system/hooks":
        session.error(
            f"core.hooksPath was set to {actual!r}; expected '_system/hooks'"
        )
