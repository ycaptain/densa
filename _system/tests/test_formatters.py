"""Test output formatters."""

from __future__ import annotations

import io
import json

from densa.formatters import format_github, format_json, format_text
from densa.report import Diagnostic, Report, Severity


def _populated_report() -> Report:
    r = Report()
    r.files_checked = 3
    r.add(Diagnostic("AGENTS003", Severity.ERROR, "a.md", 1, "missing key"))
    r.add(Diagnostic("AGENTS006", Severity.WARNING, "b.md", 5, "ambiguous"))
    return r


def test_text_emits_findings_and_summary() -> None:
    out, err = io.StringIO(), io.StringIO()
    format_text(_populated_report(), no_warnings=False, out=out, err=err)
    out_lines = out.getvalue().splitlines()
    err_lines = err.getvalue().splitlines()
    assert any("AGENTS003" in line for line in out_lines)
    assert any("AGENTS006" in line for line in err_lines)
    # Summary always goes to stderr, even on FAIL.
    assert any(line.startswith("FAIL:") for line in err_lines)


def test_text_no_warnings_drops_warnings() -> None:
    out, err = io.StringIO(), io.StringIO()
    format_text(_populated_report(), no_warnings=True, out=out, err=err)
    assert "AGENTS006" not in out.getvalue()
    assert "AGENTS006" not in err.getvalue()


def test_json_structure() -> None:
    out = io.StringIO()
    format_json(_populated_report(), no_warnings=False, out=out, err=io.StringIO())
    payload = json.loads(out.getvalue())
    assert payload["summary"]["files_checked"] == 3
    assert payload["summary"]["errors"] == 1
    assert payload["summary"]["warnings"] == 1
    assert payload["summary"]["ok"] is False
    assert len(payload["diagnostics"]) == 2
    assert {d["rule_id"] for d in payload["diagnostics"]} == {
        "AGENTS003", "AGENTS006",
    }


def test_github_uses_workflow_command_syntax() -> None:
    out = io.StringIO()
    format_github(
        _populated_report(),
        no_warnings=False,
        out=out,
        err=io.StringIO(),
    )
    lines = out.getvalue().splitlines()
    assert any(line.startswith("::error file=a.md,line=1") for line in lines)
    assert any(line.startswith("::warning file=b.md,line=5") for line in lines)
    assert all("AGENTS00" in line for line in lines)


def test_summary_says_ok_when_clean() -> None:
    err = io.StringIO()
    format_text(Report(), no_warnings=False, out=io.StringIO(), err=err)
    assert err.getvalue().startswith("OK:")
