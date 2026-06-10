"""Unit tests for the path classifiers in :mod:`densa.paths`."""

from __future__ import annotations

import pytest

from densa.paths import (
    is_domain_prompt,
    is_log,
    is_output_artifact,
    is_outputs,
    is_raw,
    is_wiki,
    wikilinks_scoped,
)


class TestIsRaw:
    @pytest.mark.parametrize("path", [
        "domains/psychology/raw/sessions/2026-01-14.md",
        "domains/research-papers/raw/papers/x.md",
        "raw/articles/x.md",
    ])
    def test_under_raw_dir(self, path: str) -> None:
        assert is_raw(path) is True

    @pytest.mark.parametrize("path", [
        "domains/psychology/wiki/concepts/x.md",
        "AGENTS.md",
        "raw",
        "domains/psychology/raw",
    ])
    def test_not_under_raw_dir(self, path: str) -> None:
        assert is_raw(path) is False


class TestIsLog:
    @pytest.mark.parametrize("path", [
        "log.md",
        "domains/psychology/log.md",
        "domains/research-papers/log.md",
    ])
    def test_is_log(self, path: str) -> None:
        assert is_log(path) is True

    @pytest.mark.parametrize("path", [
        "logfile.md",
        "domains/psychology/old-log.md",
        "log.txt",
    ])
    def test_not_log(self, path: str) -> None:
        assert is_log(path) is False


class TestIsWiki:
    @pytest.mark.parametrize("path", [
        "domains/psychology/wiki/concepts/x.md",
        "domains/research-papers/wiki/analyses/y-analysis.md",
        "domains/research-papers/wiki/frameworks/z.md",
    ])
    def test_canonical_wiki_paths(self, path: str) -> None:
        assert is_wiki(path) is True

    @pytest.mark.parametrize("path", [
        "domains/psychology/wiki/.legacy/x.md",
        "domains/psychology/raw/sessions/x.md",
        "_system/templates/concept.md",
        "index.md",
        "AGENTS.md",
        "domains/psychology/wiki/concepts/x.txt",
    ])
    def test_not_wiki(self, path: str) -> None:
        assert is_wiki(path) is False


class TestWikilinksScoped:
    @pytest.mark.parametrize("path", [
        "domains/psychology/wiki/concepts/x.md",
        "domains/research-papers/index.md",
        "index.md",
    ])
    def test_scoped(self, path: str) -> None:
        assert wikilinks_scoped(path) is True

    @pytest.mark.parametrize("path", [
        "_system/prompts/ingest.md",
        "_system/templates/concept.md",
        "attic/old.md",
        "inbox/whatever.md",
        "outputs/lint/2026-01-01.md",
        "outputs/snapshots/index-snapshot.md",
        "outputs/README.md",
        "domains/psychology/raw/sessions/x.md",
        "AGENTS.md",
        "domains/psychology/AGENTS.md",
        "domains/people/prompts/people-interaction-analysis.md",
        "domains/projects/prompts/projects-client-call-analysis.md",
    ])
    def test_unscoped(self, path: str) -> None:
        assert wikilinks_scoped(path) is False

    def test_docs_is_scoped(self) -> None:
        # docs/ has no placeholders; remains in the wikilink graph.
        assert wikilinks_scoped("docs/setup.md") is True


class TestIsDomainPrompt:
    @pytest.mark.parametrize("path", [
        "domains/people/prompts/people-interaction-analysis.md",
        "domains/psychology/prompts/psychology-session-analysis.md",
        "domains/projects/prompts/nested/extra.md",
    ])
    def test_domain_prompt(self, path: str) -> None:
        assert is_domain_prompt(path) is True

    @pytest.mark.parametrize("path", [
        "domains/psychology/wiki/prompts/x.md",  # prompts must be directly under the domain
        "domains/people/prompts",  # the bare directory
        "domains/people/prompts/notes.txt",  # not markdown
        "_system/prompts/domains/psychology-session-analysis.md",  # upstream copy
        "prompts/x.md",  # not under domains/
    ])
    def test_not_domain_prompt(self, path: str) -> None:
        assert is_domain_prompt(path) is False


class TestIsOutputs:
    @pytest.mark.parametrize("path", [
        "outputs/lint/2026-01-01.md",
        "outputs/snapshots/index-snapshot.md",
        "outputs/qa/2026-05-20-karpathy-vs-yanhua.md",
        "outputs/README.md",
        "outputs/nested/sub/file.md",
    ])
    def test_under_outputs(self, path: str) -> None:
        assert is_outputs(path) is True

    @pytest.mark.parametrize("path", [
        "outputs",
        "domains/psychology/wiki/concepts/outputs.md",
        "_system/outputs/something.md",
    ])
    def test_not_under_outputs(self, path: str) -> None:
        assert is_outputs(path) is False


class TestIsOutputArtifact:
    @pytest.mark.parametrize("path", [
        "outputs/lint/2026-01-01.md",
        "outputs/snapshots/index-snapshot.md",
        "outputs/qa/2026-05-20-karpathy-vs-yanhua.md",
    ])
    def test_artifacts(self, path: str) -> None:
        assert is_output_artifact(path) is True

    @pytest.mark.parametrize("path", [
        "outputs/README.md",
        "outputs/lint/.gitkeep",
        "outputs",
        "domains/psychology/wiki/concepts/x.md",
    ])
    def test_not_artifacts(self, path: str) -> None:
        assert is_output_artifact(path) is False
