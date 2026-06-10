"""AGENTS007 — operation writes must stay within declared scope.

Each commit is classified by its leading commit-message prefix
(``ingest(<domain>):``, ``query:``, ``lint:``, ``process-inbox:``,
``promote:``). The prefix selects an allow-list of glob patterns from
:data:`densa.config.OPERATION_WRITES`; every staged path must match
at least one pattern, otherwise we report an error.

Commits without a recognised prefix fall back to the ``""`` (no-prefix)
allow-list — schema/docs/integrations maintenance — which forbids
touching ``domains/**``.

Hook staging: the commit message is fundamentally unavailable at
pre-commit time, so the shipped ``_system/hooks/pre-commit`` runs the
validator with ``--ignore AGENTS007`` and the sibling
``_system/hooks/commit-msg`` re-runs ``--staged --select AGENTS007``
with :data:`COMMIT_MSG_FILE_ENV` pointing at the real message file
(``$1``). Both travel under the same ``core.hooksPath``.

Bypass: ``WIKI_ALLOW_CROSS_SCOPE=1`` skips the rule entirely. Use for
sanctioned multi-scope maintenance and pair with a maintenance entry
in ``log.md`` (mirrors the ``WIKI_ALLOW_LOG_REORDER`` discipline).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Final

from densa.config import CROSS_SCOPE_BYPASS_ENV, OPERATION_WRITES
from densa.git_io import StagedEntry
from densa.report import Diagnostic, Report, Severity

_RULE_ID = "AGENTS007"

COMMIT_MSG_FILE_ENV: Final[str] = "DENSA_COMMIT_MSG_FILE"
"""Env var naming the in-flight commit-message file.

Exported by ``_system/hooks/commit-msg``, which receives the real
message path as ``$1``. When set, :func:`_commit_subject` trusts it
over every other source.
"""

_PREFIX_RE = re.compile(
    r"^(?P<op>ingest|query|lint|process-inbox|promote)(?:\([^)]+\))?:\s",
)


class OperationWritesScope:
    id: str = _RULE_ID

    def apply(
        self,
        repo: Path,
        entries: list[StagedEntry],
        report: Report,
    ) -> None:
        if os.environ.get(CROSS_SCOPE_BYPASS_ENV) == "1":
            return
        if not entries:
            return
        subject = _commit_subject(repo)
        op = _classify(subject)
        allowed = OPERATION_WRITES.get(op, frozenset())
        for entry in entries:
            if entry.letter == "D":
                continue
            if _matches_any(entry.path, allowed):
                continue
            would_allow = _prefixes_allowing(entry.path)
            current = f"`{op}:`" if op else "`(no prefix)`"
            if would_allow:
                hint = (
                    f" Allowed prefixes for this path: "
                    f"{', '.join(would_allow)}."
                )
            else:
                hint = (
                    " No prefix's scope covers this path; review the "
                    "OPERATION_WRITES table in AGENTS.md §\"Operation writes\"."
                )
            report.add(Diagnostic(
                rule_id=self.id,
                severity=Severity.ERROR,
                path=entry.path,
                line=0,
                message=(
                    f"AGENTS007 operation-writes-within-scope: path is "
                    f"outside the write scope for {current}.{hint} "
                    f"For sanctioned multi-scope maintenance set "
                    f"`{CROSS_SCOPE_BYPASS_ENV}=1` and add a "
                    f"`## [YYYY-MM-DD] maintenance | ...` log entry "
                    f"(see CONTRIBUTING.md §'If the pre-commit hook "
                    f"rejects your first commit')."
                ),
            ))


def _prefixes_allowing(path: str) -> list[str]:
    """Reverse-lookup: which commit prefixes would allow this path?"""
    normalised = path.replace("\\", "/")
    matches: list[str] = []
    for prefix, patterns in OPERATION_WRITES.items():
        if any(_glob_match(normalised, p) for p in patterns):
            matches.append(f"`{prefix}:`" if prefix else "`(no prefix)`")
    return sorted(matches)


def _commit_subject(repo: Path) -> str:
    """Best-effort read of the relevant commit subject.

    Order:
      1. The file named by the ``DENSA_COMMIT_MSG_FILE`` env var —
         exported by ``_system/hooks/commit-msg``, which is the only
         hook stage where git hands over the real message file
         (``$1``). Relative paths resolve against *repo*.
      2. Most recent ``git log -1 --format=%s HEAD`` (covers post-commit
         re-runs, ``densa --diff`` in CI, and ``densa --staged`` invoked
         manually).
      3. Empty string (falls back to the ``(no prefix)`` scope).

    ``.git/COMMIT_EDITMSG`` is deliberately **not** consulted. Git hook
    timing: during ``git commit`` (including ``-m``) the pre-commit hook
    runs *before* git rewrites ``COMMIT_EDITMSG``, so mid-commit that
    file still holds the PREVIOUS commit's message — trusting it
    classified every commit one-behind (TK-0038).
    """
    env_path = os.environ.get(COMMIT_MSG_FILE_ENV)
    if env_path:
        candidate = Path(env_path)
        if not candidate.is_absolute():
            candidate = repo / candidate
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        first = _first_non_comment_line(text)
        if first:
            return first
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%s", "HEAD"],
            cwd=repo,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return out.strip()


def _first_non_comment_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        return line
    return ""


def _classify(subject: str) -> str:
    match = _PREFIX_RE.match(subject)
    return match.group("op") if match else ""


def _matches_any(path: str, patterns: frozenset[str]) -> bool:
    normalised = path.replace("\\", "/")
    return any(_glob_match(normalised, pattern) for pattern in patterns)


def _glob_match(path: str, pattern: str) -> bool:
    """``**``-aware glob matcher.

    Semantics:
      - ``**`` matches any character, including ``/`` (so any number
        of path segments).
      - ``*`` matches anything except ``/`` (one path segment).
      - ``?`` matches any single character except ``/``.
      - All other characters are literal.
    """
    return re.match(_compile_glob(pattern), path) is not None


def _compile_glob(pattern: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                out.append(".*")
                i += 2
            else:
                out.append("[^/]*")
                i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out) + r"\Z"
