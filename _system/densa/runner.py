"""Orchestration — turn a Config + source spec into a populated Report.

Four entry points mirror the four CLI modes:

- :func:`lint_staged`  — fan out staged rules over the diff, fan out
  file rules over the staged blob contents.
- :func:`lint_diff`    — same as ``lint_staged`` but driven by a
  ``base_ref..HEAD`` range instead of the git index. Lets CI catch
  ``--no-verify`` bypasses of AGENTS001 / AGENTS002 / AGENTS007.
- :func:`lint_all`     — walk every markdown in the repo (minus
  :data:`~densa.config.SKIP_DIRS`), run file rules. Staged rules are
  no-ops here.
- :func:`lint_paths`   — only the explicit paths; useful for
  ``pre-commit`` integration with ``--files`` and for IDE plugins.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from densa.checks import FILE_RULES, STAGED_RULES
from densa.checks.base import FileRule, StagedRule
from densa.config import Config
from densa.fswalk import iter_markdown
from densa.git_io import diff_entries, ref_blob, staged_blob, staged_entries
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex, build_index


def _enabled_file_rules(config: Config) -> tuple[FileRule, ...]:
    return tuple(r for r in FILE_RULES if config.is_enabled(r.id))


def _enabled_staged_rules(config: Config) -> tuple[StagedRule, ...]:
    return tuple(r for r in STAGED_RULES if config.is_enabled(r.id))


def _visit(
    path: str,
    text: str,
    idx: SlugIndex,
    report: Report,
    config: Config,
) -> None:
    report.saw()
    for rule in _enabled_file_rules(config):
        rule.visit(path, text, idx, report)


def lint_staged(repo: Path, config: Config | None = None) -> Report:
    config = config or Config()
    report = Report()
    idx = build_index(repo)

    entries = staged_entries(repo)
    for rule in _enabled_staged_rules(config):
        rule.apply(repo, entries, report)

    for entry in entries:
        if entry.letter == "D" or not entry.path.endswith(".md"):
            continue
        text = staged_blob(repo, entry.path)
        if text is None:
            continue
        _visit(entry.path, text, idx, report, config)
    return report


def lint_diff(
    repo: Path,
    base_ref: str,
    config: Config | None = None,
) -> Report:
    """Apply staged + file rules over ``base_ref..HEAD``.

    Mirrors :func:`lint_staged` but sources entries from a git range
    rather than the index, so CI can enforce the staged rules
    (AGENTS001 / AGENTS002 / AGENTS007) on every PR even when contributors
    use ``git commit --no-verify`` locally. File contents are read from
    ``HEAD`` (the post-merge state).
    """
    config = config or Config()
    report = Report()
    idx = build_index(repo)

    entries = diff_entries(repo, base_ref)
    for rule in _enabled_staged_rules(config):
        rule.apply(repo, entries, report)

    for entry in entries:
        if entry.letter == "D" or not entry.path.endswith(".md"):
            continue
        text = ref_blob(repo, "HEAD", entry.path)
        if text is None:
            continue
        _visit(entry.path, text, idx, report, config)
    return report


def lint_all(repo: Path, config: Config | None = None) -> Report:
    config = config or Config()
    report = Report()
    idx = build_index(repo)
    for path in _walk_repo_markdown(repo):
        _check_path(repo, path, idx, report, config)
    return report


def lint_paths(
    repo: Path,
    paths: Iterable[str | Path],
    config: Config | None = None,
) -> Report:
    config = config or Config()
    report = Report()
    idx = build_index(repo)
    for raw in paths:
        p = Path(raw)
        abs_p = p if p.is_absolute() else (repo / p)
        rel = str(abs_p.resolve().relative_to(repo)).replace("\\", "/")
        _check_path(repo, rel, idx, report, config)
    return report


def _walk_repo_markdown(repo: Path) -> Iterable[str]:
    """Every markdown path ``--all`` checks, via the shared vault walk
    (prunes :data:`~densa.config.SKIP_DIRS` and nested git checkouts)."""
    for rel in iter_markdown(repo):
        yield str(rel).replace("\\", "/")


def _check_path(
    repo: Path,
    rel: str,
    idx: SlugIndex,
    report: Report,
    config: Config,
) -> None:
    try:
        text = (repo / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.add(Diagnostic(
            rule_id="DENSA-IO",
            severity=Severity.ERROR,
            path=rel,
            line=0,
            message=f"cannot read: {exc}",
        ))
        return
    _visit(rel, text, idx, report, config)
