"""Contract tests for the `promote` operation pre-flight gate.

`promote` is an LLM-driven prompt (`_system/prompts/promote.md`), not a
Python function. These tests pin the **prompt contract** so a careless
edit doesn't silently drop a pre-flight check the wider design depends
on. Every assertion here corresponds to a row in the pre-flight table
in [`/AGENTS.md`](../../AGENTS.md) §2.5 / step 1 of the prompt.

If you intentionally restructure the prompt body, update both files
together — they are the canonical statement of the contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def promote_prompt() -> str:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "_system" / "prompts" / "promote.md"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def agents_md() -> str:
    repo = Path(__file__).resolve().parents[2]
    return (repo / "AGENTS.md").read_text(encoding="utf-8")


class TestPromotePromptExists:
    def test_prompt_file_present(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        assert (repo / "_system" / "prompts" / "promote.md").is_file()


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
        """Plan v3.2: ≥2 sources for synthesis (§3.1)."""
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
    """AGENTS.md §2.5 must reference the prompt and describe the operation."""

    def test_agents_md_mentions_promote(self, agents_md: str) -> None:
        assert "promote" in agents_md.lower()

    def test_agents_md_workflow_table_lists_promote(
        self, agents_md: str,
    ) -> None:
        """§8 workflow table picks up the new trigger pattern."""
        assert "promote (§2.5)" in agents_md

    def test_agents_md_writes_table_lists_promote(
        self, agents_md: str,
    ) -> None:
        """§2.0 OPERATION_WRITES table includes a `promote` row."""
        assert "| promote" in agents_md
