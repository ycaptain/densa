"""Render a :class:`~densa.report.Report` for human or machine readers.

Three formats:

- ``text``    — the original ``file:line: SEVERITY: msg`` line format,
  one finding per line, plus a summary line.
- ``json``    — newline-terminated JSON object, suitable for piping into
  other tools or CI annotations.
- ``github``  — `::error file=...,line=...::msg` and `::warning ...::`
  one-liners that GitHub Actions surfaces as PR annotations.

The renderer doubles as the I/O sink: every formatter writes errors to
``stdout`` and the summary to ``stderr``. Callers should not buffer
``stdout`` themselves.
"""

from __future__ import annotations

import json
import sys
from typing import Protocol, TextIO

from densa.report import Diagnostic, Report, Severity


class Formatter(Protocol):
    """Render *report* to *out* and *err*; defaults to stdout/stderr."""

    def __call__(
        self,
        report: Report,
        no_warnings: bool = False,
        out: TextIO = ...,
        err: TextIO = ...,
    ) -> None: ...


def _summary(report: Report) -> str:
    return (
        f"checked {report.files_checked} file(s), "
        f"{len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s)."
    )


def _filtered(report: Report, no_warnings: bool) -> list[Diagnostic]:
    if no_warnings:
        return report.errors
    return list(report.diagnostics)


def format_text(
    report: Report,
    no_warnings: bool = False,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> None:
    for diag in _filtered(report, no_warnings):
        stream = err if diag.severity is Severity.WARNING else out
        print(
            f"{diag.path}:{diag.line}: {diag.severity.value.upper()}: "
            f"{diag.message} [{diag.rule_id}]",
            file=stream,
        )
    summary = _summary(report)
    print(
        f"{'FAIL' if report.has_errors else 'OK'}: {summary}",
        file=err,
    )


def format_json(
    report: Report,
    no_warnings: bool = False,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> None:
    payload = {
        "summary": {
            "files_checked": report.files_checked,
            "errors": len(report.errors),
            "warnings": len(report.warnings),
            "ok": not report.has_errors,
        },
        "diagnostics": [d.to_dict() for d in _filtered(report, no_warnings)],
    }
    json.dump(payload, out, indent=2, sort_keys=True)
    out.write("\n")


def format_github(
    report: Report,
    no_warnings: bool = False,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> None:
    for diag in _filtered(report, no_warnings):
        kind = "error" if diag.severity is Severity.ERROR else "warning"
        # GitHub Actions log-command spec:
        # https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
        line_attr = f",line={diag.line}" if diag.line > 0 else ""
        print(
            f"::{kind} file={diag.path}{line_attr},title={diag.rule_id}::"
            f"{diag.message}",
            file=out,
        )
    summary = _summary(report)
    print(
        f"{'FAIL' if report.has_errors else 'OK'}: {summary}",
        file=err,
    )


FORMATTERS: dict[str, Formatter] = {
    "text": format_text,
    "json": format_json,
    "github": format_github,
}
