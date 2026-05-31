"""Contract tests for the `promote` operation pre-flight gate.

`promote` is an LLM-driven prompt, not a Python function. Since the
T009 progressive-disclosure split it lives in two files —
`_system/prompts/promote.md` (header) and `_system/prompts/promote.body.md`
(on-demand procedure); the `promote_prompt` fixture concatenates both.
These tests pin the **prompt contract** so a careless edit doesn't
silently drop a pre-flight check the wider design depends on. Every
assertion here corresponds to a row in the pre-flight table in
[`/AGENTS.md` §"promote"](../../AGENTS.md#25-promote-qa-path-qa--wiki-page) /
step 1 of the prompt body.

If you intentionally restructure the prompt, update both files
together — they are the canonical statement of the contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def promote_prompt() -> str:
    """The promote contract spans two files since the T009
    progressive-disclosure split: the always-loaded header
    (`promote.md`, carrying the write table + summary + non-negotiables)
    and the on-demand body (`promote.body.md`, carrying the pre-flight
    checklist and the four transform stages). Concatenate both so the
    contract assertions below see the whole prompt regardless of which
    half a given keyword lives in.
    """
    repo = Path(__file__).resolve().parents[2]
    prompts = repo / "_system" / "prompts"
    header = (prompts / "promote.md").read_text(encoding="utf-8")
    body = (prompts / "promote.body.md").read_text(encoding="utf-8")
    return header + "\n" + body


@pytest.fixture(scope="module")
def agents_md() -> str:
    repo = Path(__file__).resolve().parents[2]
    return (repo / "AGENTS.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def operation_scopes_md() -> str:
    """The per-prefix write-scope table lives in the reference doc."""
    repo = Path(__file__).resolve().parents[2]
    path = repo / "docs" / "reference" / "operation-scopes.md"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def guide_md() -> str:
    """The natural-language → operation mapping table lives in GUIDE.md."""
    repo = Path(__file__).resolve().parents[2]
    return (repo / "GUIDE.md").read_text(encoding="utf-8")


class TestPromotePromptExists:
    def test_prompt_file_present(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        prompts = repo / "_system" / "prompts"
        # Both halves of the post-T009 split must exist: the header
        # (always loaded) and the on-demand body (full procedure).
        assert (prompts / "promote.md").is_file()
        assert (prompts / "promote.body.md").is_file()


class TestPreFlightChecks:
    """Each prompt must spell out every pre-flight check by name so the
    LLM cannot silently skip one. Match on substring (case-insensitive
    for resilience) — exact wording can evolve."""

    @pytest.mark.parametrize("needle", [
        "outputs/qa/",
        "type: report",
        "L2",
        "alias",
        "sources",
    ])
    def test_check_keyword_present(
        self, promote_prompt: str, needle: str,
    ) -> None:
        assert needle.lower() in promote_prompt.lower(), (
            f"promote.md is missing pre-flight check keyword: {needle!r}"
        )

    def test_synthesis_min_sources_rule(self, promote_prompt: str) -> None:
        """Plan v3.2: ≥2 sources for synthesis (see sources-cardinality.md)."""
        assert "2" in promote_prompt and "synthesis" in promote_prompt


class TestInformationShapeTransform:
    """Four stages: voice / citation hoist / L2 fill-in / section restructure."""

    @pytest.mark.parametrize("stage", [
        "voice",
        "citation",
        "L2",
        "section",
    ])
    def test_stage_named(self, promote_prompt: str, stage: str) -> None:
        assert stage.lower() in promote_prompt.lower()


class TestGitOperations:
    """promote always uses git mv (preserves history); commit prefix `promote:`."""

    def test_uses_git_mv(self, promote_prompt: str) -> None:
        assert "git mv" in promote_prompt

    def test_commit_prefix_documented(self, promote_prompt: str) -> None:
        assert "promote:" in promote_prompt


class TestHardRules:
    """1:1 only; no `--in-place`; no autonomous lint promotion."""

    @pytest.mark.parametrize("rule", [
        "1:1",
        "in-place",
        "lint",
    ])
    def test_hard_rule_present(self, promote_prompt: str, rule: str) -> None:
        assert rule.lower() in promote_prompt.lower()


class TestAgentsMdAlignment:
    """AGENTS.md's "promote" section must reference the prompt and describe the operation."""

    def test_agents_md_mentions_promote(self, agents_md: str) -> None:
        assert "promote" in agents_md.lower()

    def test_workflow_table_lists_promote(
        self, guide_md: str,
    ) -> None:
        """The natural-language → operation mapping table picks up the
        new trigger pattern. The table lived in AGENTS.md's "Workflow"
        section in v0.2.0 and earlier; it moved to GUIDE.md's "Mapping
        natural language to operations" section in the post-0.2.0
        onboarding cleanup so AGENTS.md stays contract-only.
        """
        assert "[promote](AGENTS.md#25-promote-qa-path" in guide_md

    def test_operation_scopes_lists_promote(
        self, operation_scopes_md: str,
    ) -> None:
        """The per-prefix write-scope reference table includes promote.

        AGENTS.md's "Operation writes" section keeps the headline;
        the full table moved to docs/reference/operation-scopes.md
        when AGENTS.md was trimmed to a contract-only file.
        """
        assert "promote" in operation_scopes_md.lower()
