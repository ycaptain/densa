"""AGENTS012 — migration-history-hygiene.

Pages that were mechanically migrated by a ``densa migrate`` run carry
a ``migration_history`` list in their frontmatter (see
:mod:`_system/scripts/migrate_02_karpathy_vocab.py`). The presence of
that field is informational: it tells the user "this page was renamed
+ frontmatter-rewritten by the migration script, but its prose still
reflects the v(N-1) narrative shape — re-ingest the source under the
current schema when the content becomes load-bearing".

This rule warns when:

- A wiki page carries ``migration_history`` but its
  ``compiled_against`` lags the current ``SCHEMA_VERSION``. That
  combination is contradictory — migration should have brought
  ``compiled_against`` up to the latest run's ``to_version``.
- ``migration_history`` is present but malformed (not a list, no
  entries, or an entry missing the required ``from`` / ``to`` /
  ``on`` / ``mode`` keys).

The rule does **not** warn merely on the presence of
``migration_history`` — that field is the audit trail Densa wants to
keep, not a defect. Users can query for "pages with migration history"
via Dataview (see the per-domain ``overview.md`` template's *"Pages
migrated mechanically"* block) to decide which ones to re-ingest.
"""

from __future__ import annotations

from densa.config import SCHEMA_VERSION
from densa.frontmatter import parse
from densa.paths import is_wiki
from densa.report import Diagnostic, Report, Severity
from densa.wikilink import SlugIndex

_RULE_ID = "AGENTS012"
_REQUIRED_KEYS_PER_ENTRY = ("from", "to", "on", "mode")


class MigrationHistoryHygiene:
    id: str = _RULE_ID

    def visit(
        self,
        path: str,
        text: str,
        idx: SlugIndex,
        report: Report,
    ) -> None:
        if not is_wiki(path):
            return
        fm = parse(text)
        if fm is None:
            return
        history = fm.get("migration_history")
        if history is None:
            return

        # The stdlib frontmatter parser returns list-of-string for
        # ``- foo`` blocks but the entries we write are nested
        # mappings (``- from: 1`` followed by indented keys). The
        # stdlib parser can't decode that into a list of dicts. We
        # accept either: a non-empty list, or a presence-shaped value
        # indicating an indented block is present. The deeper
        # structural check requires pyyaml; when pyyaml is not
        # available we limit ourselves to a presence + raw-substring
        # check (which is what AGENTS012 needs in stdlib mode).
        if not history:
            # Empty list / empty string: definitely malformed.
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.WARNING,
                path=path,
                line=1,
                message=(
                    "AGENTS012 migration-history-hygiene: "
                    "`migration_history:` is present but empty. "
                    "Either remove the key or populate at least one "
                    "entry per the migration script's output."
                ),
            ))
            return

        # Sanity-check the raw frontmatter substring for the required
        # keys; this works regardless of YAML backend.
        raw_block = _frontmatter_text(text)
        if raw_block is not None:
            for key in _REQUIRED_KEYS_PER_ENTRY:
                if f"{key}:" not in raw_block:
                    report.add(Diagnostic(
                        rule_id=self.id,
                        severity=Severity.WARNING,
                        path=path,
                        line=1,
                        message=(
                            f"AGENTS012 migration-history-hygiene: "
                            f"`migration_history` entries should "
                            f"include `{key}:` (saw the field but "
                            f"missing the key)."
                        ),
                    ))

        # Cross-check ``compiled_against`` is at least the schema
        # version. (AGENTS010 catches the < case directly; AGENTS012
        # carries the *human-friendly* hint that migration_history is
        # what records the chain.)
        raw_version = fm.get("compiled_against")
        if raw_version not in (None, ""):
            try:
                version = int(str(raw_version).strip())
            except ValueError:
                return
            if version < SCHEMA_VERSION:
                report.add(Diagnostic(
                    rule_id=self.id,
                    severity=Severity.WARNING,
                    path=path,
                    line=1,
                    message=(
                        f"AGENTS012 migration-history-hygiene: page "
                        f"has `migration_history` but "
                        f"`compiled_against={version}` lags "
                        f"SCHEMA_VERSION={SCHEMA_VERSION}. The "
                        f"migration script should have set "
                        f"compiled_against to the latest `to:` value; "
                        f"if you edited the frontmatter by hand, "
                        f"re-bump it."
                    ),
                ))


def _frontmatter_text(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]
