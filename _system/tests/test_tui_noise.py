"""Known-noise classification (`densa.tui.noise`).

The predicate decides which `densa --all` findings are the expected,
gitignored-tree band the viewer mutes by default. It must key on path
*origin*, not rule ID, and be pure/total.
"""

from __future__ import annotations

import pytest

from densa.tui.noise import NOISE_PREFIXES, is_known_noise


class TestIsKnownNoise:
    @pytest.mark.parametrize(
        "path",
        [
            "docs/maintainers/2026-05-29-pre-launch-plan.md",
            "docs/maintainers/notes/whatever.md",
            ".backlog/tasks/task-001.md",
            ".backlog/docs/dev-methodology/evidence.md",
        ],
    )
    def test_noise_paths_are_muted(self, path: str) -> None:
        assert is_known_noise(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "domains/research-papers/wiki/concepts/superposition.md",
            "domains/research-papers/raw/papers/2024-anthropic.md",
            "_system/densa/cli.py",
            "README.md",
            "docs/guide.md",  # docs/ but NOT docs/maintainers/
            "backlog/elsewhere.md",  # no leading dot
            "",
        ],
    )
    def test_real_paths_are_not_muted(self, path: str) -> None:
        assert is_known_noise(path) is False

    def test_prefixes_are_origin_anchored(self) -> None:
        # A noise prefix appearing mid-path must NOT match — origin only.
        assert is_known_noise("domains/x/.backlog/foo.md") is False
        for prefix in NOISE_PREFIXES:
            assert is_known_noise(prefix + "anything.md") is True
