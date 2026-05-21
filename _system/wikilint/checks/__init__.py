"""Rule implementations.

Each rule is a class implementing one of the two protocols in
:mod:`wikilint.checks.base`:

- :class:`FileRule`  — applied to every (path, text) pair the runner
  collects. Used for frontmatter / wikilink checks.
- :class:`StagedRule` — applied to the staged change set as a whole.
  Used for raw immutability and log append-only, which are diff-shaped
  rather than content-shaped.

A rule's ``id`` matches a :class:`~wikilint.config.RuleSpec` in
:data:`wikilint.config.RULES`, and is the stable string users select
via ``--select`` / ``--ignore``.

To add a new rule:

1. Add a :class:`~wikilint.config.RuleSpec` to
   :data:`wikilint.config.RULES` with a never-before-used ``AGENTS00N``
   ID.
2. Implement a ``FileRule`` or ``StagedRule`` subclass in this package
   carrying the same ``id`` and a ``visit`` / ``apply`` method.
3. Register it in :data:`ALL_RULES` below.
"""

from __future__ import annotations

from wikilint.checks.analysis_sources import AnalysisSourcesCardinality
from wikilint.checks.base import FileRule, StagedRule
from wikilint.checks.frontmatter_required import (
    FrontmatterRequiredKeys,
    FrontmatterTypeAllowed,
)
from wikilint.checks.log_append_only import LogAppendOnly
from wikilint.checks.operation_writes_scope import OperationWritesScope
from wikilint.checks.raw_immutability import RawImmutability
from wikilint.checks.wikilink_resolvable import WikilinkResolvable

FILE_RULES: tuple[FileRule, ...] = (
    FrontmatterRequiredKeys(),
    FrontmatterTypeAllowed(),
    AnalysisSourcesCardinality(),
    WikilinkResolvable(),
)

STAGED_RULES: tuple[StagedRule, ...] = (
    RawImmutability(),
    LogAppendOnly(),
    OperationWritesScope(),
)

__all__ = [
    "FILE_RULES",
    "STAGED_RULES",
    "AnalysisSourcesCardinality",
    "FileRule",
    "FrontmatterRequiredKeys",
    "FrontmatterTypeAllowed",
    "LogAppendOnly",
    "OperationWritesScope",
    "RawImmutability",
    "StagedRule",
    "WikilinkResolvable",
]
