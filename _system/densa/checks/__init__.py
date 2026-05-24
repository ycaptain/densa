"""Rule implementations.

Each rule is a class implementing one of the two protocols in
:mod:`densa.checks.base`:

- :class:`FileRule`  — applied to every (path, text) pair the runner
  collects. Used for frontmatter / wikilink checks.
- :class:`StagedRule` — applied to the staged change set as a whole.
  Used for raw immutability and log append-only, which are diff-shaped
  rather than content-shaped.

A rule's ``id`` matches a :class:`~densa.config.RuleSpec` in
:data:`densa.config.RULES`, and is the stable string users select
via ``--select`` / ``--ignore``.

To add a new rule:

1. Add a :class:`~densa.config.RuleSpec` to
   :data:`densa.config.RULES` with a never-before-used ``AGENTS00N``
   ID.
2. Implement a ``FileRule`` or ``StagedRule`` subclass in this package
   carrying the same ``id`` and a ``visit`` / ``apply`` method.
3. Register it in :data:`ALL_RULES` below.
"""

from __future__ import annotations

from densa.checks.analysis_sources import AnalysisSourcesCardinality
from densa.checks.base import FileRule, StagedRule
from densa.checks.compiled_against_lag import CompiledAgainstCurrent
from densa.checks.frontmatter_required import (
    FrontmatterRequiredKeys,
    FrontmatterTypeAllowed,
)
from densa.checks.last_validated_stale import LastValidatedFresh
from densa.checks.log_append_only import LogAppendOnly
from densa.checks.operation_writes_scope import OperationWritesScope
from densa.checks.raw_immutability import RawImmutability
from densa.checks.wikilink_resolvable import WikilinkResolvable

FILE_RULES: tuple[FileRule, ...] = (
    FrontmatterRequiredKeys(),
    FrontmatterTypeAllowed(),
    AnalysisSourcesCardinality(),
    WikilinkResolvable(),
    LastValidatedFresh(),
    CompiledAgainstCurrent(),
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
    "CompiledAgainstCurrent",
    "FileRule",
    "FrontmatterRequiredKeys",
    "FrontmatterTypeAllowed",
    "LastValidatedFresh",
    "LogAppendOnly",
    "OperationWritesScope",
    "RawImmutability",
    "StagedRule",
    "WikilinkResolvable",
]
