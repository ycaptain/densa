"""Tests for :func:`wikilint.runner.lint_paths`.

This entry point feeds explicit file paths (relative or absolute) and
returns a :class:`Report`. Three behaviours matter:

1. Relative paths are resolved against the repo root.
2. Absolute paths must point inside the repo (else
   :class:`Path.relative_to` raises a clear `ValueError`).
3. Missing paths surface as a `WIKILINT-IO` diagnostic, not a crash.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from wikilint.runner import lint_paths


def _seed(tmp_path: Path) -> Path:
    (tmp_path / "AGENTS.md").write_text(
        "---\ntype: schema\nscope: L1\n---\n", encoding="utf-8",
    )
    return tmp_path


def test_relative_path_resolves_against_repo(tmp_path: Path) -> None:
    repo = _seed(tmp_path)
    (repo / "domains" / "x" / "wiki").mkdir(parents=True)
    page = repo / "domains" / "x" / "wiki" / "p.md"
    page.write_text(
        "---\n"
        "type: concept\n"
        "domain: x\n"
        "created: 2026-01-01\n"
        "updated: 2026-01-01\n"
        "status: active\n"
        "compiled_against: 1\n"
        "---\n# P\n",
        encoding="utf-8",
    )
    report = lint_paths(repo, ["domains/x/wiki/p.md"])
    assert report.files_checked == 1


def test_absolute_path_inside_repo_resolves(tmp_path: Path) -> None:
    repo = _seed(tmp_path)
    (repo / "domains" / "x" / "wiki").mkdir(parents=True)
    page = repo / "domains" / "x" / "wiki" / "p.md"
    page.write_text(
        "---\n"
        "type: concept\n"
        "domain: x\n"
        "created: 2026-01-01\n"
        "updated: 2026-01-01\n"
        "status: active\n"
        "compiled_against: 1\n"
        "---\n# P\n",
        encoding="utf-8",
    )
    report = lint_paths(repo, [str(page.resolve())])
    assert report.files_checked == 1


def test_missing_path_reports_wikilint_io_not_crash(
    tmp_path: Path,
) -> None:
    repo = _seed(tmp_path)
    report = lint_paths(repo, ["does-not-exist.md"])
    # `files_checked` only counts files the visitor actually opened;
    # a read-error short-circuits before `saw()`. What matters is that
    # the error is reported and the runner did not crash.
    assert any(d.rule_id == "WIKILINT-IO" for d in report.diagnostics)
    assert report.has_errors


def test_absolute_path_outside_repo_raises(tmp_path: Path) -> None:
    repo = _seed(tmp_path)
    outside = tmp_path.parent / "totally-elsewhere.md"
    outside.write_text("# outside\n", encoding="utf-8")
    # Path.resolve().relative_to(repo) raises ValueError when the path
    # is not under repo. This is intentional (better than silently
    # mis-classifying).
    with pytest.raises(ValueError):
        lint_paths(repo, [str(outside.resolve())])


def test_empty_path_list_returns_empty_report(tmp_path: Path) -> None:
    repo = _seed(tmp_path)
    report = lint_paths(repo, [])
    assert report.files_checked == 0
    assert report.diagnostics == []
