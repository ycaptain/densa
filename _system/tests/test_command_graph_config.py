"""Tests for ``densa graph-config`` (``densa.commands.graph_config``)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from densa.commands import graph_config as gc


def _vault(tmp_path: Path, domains: tuple[str, ...] = ("r",)) -> Path:
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (tmp_path / "_system" / "densa").mkdir(parents=True)
    for d in domains:
        (tmp_path / "domains" / d / "wiki").mkdir(parents=True)
    return tmp_path


def _args(**overrides: object) -> argparse.Namespace:
    base: dict[str, object] = {
        "exclude": [], "force": False, "print_only": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


class TestDiscoverDomains:
    def test_sorted_and_wiki_gated(self, tmp_path: Path) -> None:
        repo = _vault(tmp_path, domains=("zeta", "alpha"))
        # A dir without wiki/ is not a domain.
        (repo / "domains" / "not-a-domain").mkdir()
        assert gc.discover_domains(repo) == ["alpha", "zeta"]

    def test_no_domains_dir(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_text("# A\n", encoding="utf-8")
        assert gc.discover_domains(tmp_path) == []


class TestBuildGraphConfig:
    def test_color_groups_shape(self) -> None:
        config = gc.build_graph_config(["alpha", "beta"])
        groups = config["colorGroups"]
        assert isinstance(groups, list)
        # Two domain groups + index + syntheses landmarks.
        assert len(groups) == 4
        assert groups[0]["query"] == 'path:"domains/alpha/"'
        assert groups[0]["color"] == {"a": 1, "rgb": 0x9B59B6}
        assert groups[1]["color"] == {"a": 1, "rgb": 0x3498DB}
        assert groups[-2]["query"] == 'file:"index.md"'
        assert groups[-1]["query"] == 'path:"/syntheses/"'

    def test_palette_recycles_beyond_its_length(self) -> None:
        domains = [f"d{i:02d}" for i in range(9)]
        config = gc.build_graph_config(domains)
        groups = config["colorGroups"]
        assert groups[7]["color"]["rgb"] == groups[0]["color"]["rgb"]

    def test_base_filter_and_excludes(self) -> None:
        config = gc.build_graph_config([], excludes=["share/"])
        search = config["search"]
        assert isinstance(search, str)
        assert search.startswith('-path:"share/" ')
        for term in ('-path:"_system/"', '-path:"/raw/"', '-file:"log.md"'):
            assert term in search

    def test_display_and_forces_defaults(self) -> None:
        config = gc.build_graph_config([])
        assert config["hideUnresolved"] is True
        assert config["showOrphans"] is False
        assert config["linkDistance"] == 110


class TestRun:
    def test_writes_graph_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        repo = _vault(tmp_path, domains=("r",))
        monkeypatch.chdir(repo)
        rc = gc.run(_args())
        assert rc == 0
        payload = json.loads(
            (repo / ".obsidian" / "graph.json").read_text(encoding="utf-8"),
        )
        assert payload["colorGroups"][0]["query"] == 'path:"domains/r/"'
        assert "wrote .obsidian/graph.json" in capsys.readouterr().out

    def test_refuses_overwrite_without_force(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        repo = _vault(tmp_path)
        target = repo / ".obsidian" / "graph.json"
        target.parent.mkdir()
        target.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(repo)
        rc = gc.run(_args())
        assert rc == 2
        assert target.read_text(encoding="utf-8") == "{}"
        assert "--force" in capsys.readouterr().err

    def test_force_overwrites(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        repo = _vault(tmp_path)
        target = repo / ".obsidian" / "graph.json"
        target.parent.mkdir()
        target.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(repo)
        rc = gc.run(_args(force=True))
        assert rc == 0
        assert json.loads(target.read_text(encoding="utf-8"))["close"] is False

    def test_print_only_writes_nothing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        repo = _vault(tmp_path)
        monkeypatch.chdir(repo)
        rc = gc.run(_args(print_only=True))
        assert rc == 0
        assert not (repo / ".obsidian").exists()
        payload = json.loads(capsys.readouterr().out)
        assert "colorGroups" in payload


def test_add_parser_registers_graph_config() -> None:
    parent = argparse.ArgumentParser()
    sub = parent.add_subparsers(dest="command")
    gc.add_parser(sub)
    args = parent.parse_args(
        ["graph-config", "--exclude", "share/", "--force"],
    )
    assert args.command == "graph-config"
    assert args.exclude == ["share/"]
    assert args.force is True
