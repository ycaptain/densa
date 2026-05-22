"""Tests for AGENTS001 — raw/ is immutable.

Adds (letter ``A``, ``C``) into ``raw/`` are permitted; that's how new
sources arrive. Modify (``M``), delete (``D``), rename (``R``) are
rejected unconditionally — there is no sanctioned bypass.
"""

from __future__ import annotations

from pathlib import Path

from wikilint.checks.raw_immutability import RawImmutability
from wikilint.git_io import StagedEntry
from wikilint.report import Report


def _entry(letter: str, path: str, src: str | None = None) -> StagedEntry:
    return StagedEntry(letter, path, src=src)


def _ids(report: Report) -> list[str]:
    return [d.rule_id for d in report.diagnostics]


def _run(*entries: StagedEntry) -> Report:
    report = Report()
    # Path arg is unused by this rule but the signature requires one.
    RawImmutability().apply(Path("."), list(entries), report)
    return report


class TestAllowedActions:
    def test_add_to_raw_is_clean(self) -> None:
        assert _ids(_run(_entry("A", "domains/psy/raw/sessions/x.md"))) == []

    def test_add_outside_raw_is_clean(self) -> None:
        assert _ids(_run(_entry("A", "domains/psy/wiki/foo.md"))) == []

    def test_copy_to_raw_is_clean(self) -> None:
        """`git mv` with --no-actual-move produces letter `C` for copy."""
        assert _ids(_run(_entry("C", "domains/psy/raw/sessions/y.md"))) == []


class TestRejectedActions:
    def test_modify_raw_is_error(self) -> None:
        assert _ids(_run(_entry("M", "domains/psy/raw/sessions/x.md"))) == [
            "AGENTS001",
        ]

    def test_delete_raw_is_error(self) -> None:
        assert _ids(_run(_entry("D", "domains/psy/raw/sessions/x.md"))) == [
            "AGENTS001",
        ]

    def test_rename_raw_is_error(self) -> None:
        assert _ids(_run(_entry("R", "domains/psy/raw/sessions/y.md"))) == [
            "AGENTS001",
        ]

    def test_modify_outside_raw_is_clean(self) -> None:
        """Editing files NOT under raw/ is fine — that's the rule's
        whole purpose (the wiki should be edited; raw should not)."""
        assert _ids(_run(_entry("M", "domains/psy/wiki/foo.md"))) == []
        assert _ids(_run(_entry("M", "log.md"))) == []
        assert _ids(_run(_entry("M", "AGENTS.md"))) == []


class TestMixedBatch:
    def test_only_raw_modifications_flagged(self) -> None:
        report = _run(
            _entry("A", "domains/psy/raw/sessions/new.md"),
            _entry("M", "domains/psy/raw/sessions/old.md"),
            _entry("M", "domains/psy/wiki/page.md"),
        )
        # One AGENTS001 diagnostic for the raw modify, none for the
        # raw add or wiki edit.
        assert _ids(report) == ["AGENTS001"]
        assert report.diagnostics[0].path.endswith("raw/sessions/old.md")


class TestRenameSourceAware:
    """A `R` (rename) is only forbidden when the SOURCE was in raw/.

    `git mv inbox/x.md domains/<X>/raw/<bucket>/<dated>-x.md` is the
    canonical `process-inbox` action (L1 §2.4) and MUST be allowed.
    Renames inside raw/ are still forbidden — they break
    `git log --follow` traces from wiki claims to their source.
    """

    def test_inbox_to_raw_rename_is_allowed(self) -> None:
        assert _ids(_run(_entry(
            "R",
            "domains/psy/raw/sessions/2026-04-23-session.md",
            src="inbox/raw-clip.md",
        ))) == []

    def test_raw_to_raw_rename_is_blocked(self) -> None:
        assert _ids(_run(_entry(
            "R",
            "domains/psy/raw/sessions/y.md",
            src="domains/psy/raw/sessions/x.md",
        ))) == ["AGENTS001"]

    def test_rename_without_src_falls_back_to_dest_check(self) -> None:
        """Legacy callers without src info stay conservative (blocked
        on dest-in-raw)."""
        assert _ids(_run(_entry(
            "R", "domains/psy/raw/sessions/y.md", src=None,
        ))) == ["AGENTS001"]
