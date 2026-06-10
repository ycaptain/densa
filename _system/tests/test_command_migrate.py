"""Tests for ``densa migrate`` dispatch — the adopt path (TK-0032).

Densa's repo ships ``_system/migrations.log`` with entries recording
that migrations already ran (against the showcase content). When an
owner adopts densa into a pre-existing v1 vault by copying upstream
``_system/`` over their own, that log lands in a vault that is
genuinely still on v1: the command's ``compiled_against`` scan and the
script's log-based idempotency guard disagree.

``densa migrate`` resolves the conflict by appending ``--force`` to
the script argv whenever its own scan says the migration is pending —
the scan is ground truth and the scripts are idempotent by design.
Hand-run scripts keep the log guard (covered in
``test_migrate_02_karpathy_vocab.py``).
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import densa
from densa.checks.migration_history_hygiene import MigrationHistoryHygiene
from densa.commands import migrate as migrate_cmd
from densa.report import Report
from densa.schema import Migration

_REAL_SYSTEM = Path(densa.__file__).resolve().parents[1]  # …/_system


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _v1_page(type_: str) -> str:
    return (
        "---\n"
        f"type: {type_}\n"
        "domain: research-papers\n"
        "created: 2024-01-01\n"
        "updated: 2024-01-01\n"
        "sources: []\n"
        "aliases: []\n"
        "tags: []\n"
        "status: active\n"
        "compiled_against: 1\n"
        "---\n"
        "# Page\n"
    )


def _build_adopted_v1_vault(root: Path) -> Path:
    """A v1 vault that copied upstream ``_system/`` over its own.

    Carries a working copy of the densa package + the migration script
    (so the subprocess dispatch resolves its imports against the tmp
    vault) and — crucially — the upstream-shipped ``migrations.log``
    that already records the v1→v2 run.
    """
    (root / "AGENTS.md").write_text(
        "---\ntype: schema\nscope: L1\n---\n# AGENTS\n", encoding="utf-8",
    )
    shutil.copytree(
        _REAL_SYSTEM / "densa",
        root / "_system" / "densa",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    scripts = root / "_system" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(
        _REAL_SYSTEM / "scripts" / "migrate_02_karpathy_vocab.py", scripts,
    )
    (root / "_system" / "migrations.log").write_text(
        "2026-01-01  02_karpathy_vocab  mode=in-place  "
        "v1 → v2: Karpathy vocabulary\n",
        encoding="utf-8",
    )
    domain = root / "domains" / "research-papers"
    _write(
        domain / "wiki" / "analyses" / "2024-foo-analysis.md",
        _v1_page("analysis"),
    )
    return root


def _args(**overrides: object) -> argparse.Namespace:
    base: dict[str, object] = {
        "dry_run": False,
        "yes": True,
        "from_version": None,
        "mode": None,
        "extra_roots": [],
    }
    base.update(overrides)
    return argparse.Namespace(**base)


# --- _run_migration: --force plumbing ---------------------------------------


class TestRunMigrationForceFlag:
    @staticmethod
    def _stub_migration(repo: Path) -> Migration:
        """A stub script that records its argv into ``stub-argv.txt``."""
        script = repo / "_system" / "scripts" / "stub_migration.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(
            "import pathlib\n"
            "import sys\n"
            "pathlib.Path('stub-argv.txt').write_text(\n"
            "    ' '.join(sys.argv[1:]), encoding='utf-8',\n"
            ")\n",
            encoding="utf-8",
        )
        return Migration(
            from_version=1,
            to_version=2,
            breaking=True,
            summary="stub",
            script="_system/scripts/stub_migration.py",
        )

    def test_force_true_appends_flag(self, tmp_path: Path) -> None:
        m = self._stub_migration(tmp_path)
        rc = migrate_cmd._run_migration(tmp_path, m, dry_run=False, force=True)
        assert rc == 0
        argv = (tmp_path / "stub-argv.txt").read_text(encoding="utf-8").split()
        assert "--apply" in argv
        assert "--force" in argv

    def test_force_defaults_to_off(self, tmp_path: Path) -> None:
        m = self._stub_migration(tmp_path)
        rc = migrate_cmd._run_migration(tmp_path, m, dry_run=False)
        assert rc == 0
        argv = (tmp_path / "stub-argv.txt").read_text(encoding="utf-8").split()
        assert "--force" not in argv


# --- adopted-vault end-to-end ------------------------------------------------


class TestAdoptedVaultMigration:
    def test_shipped_log_does_not_block_pending_migration(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        repo = _build_adopted_v1_vault(tmp_path)
        monkeypatch.chdir(repo)

        rc = migrate_cmd.run(_args())
        assert rc == 0

        # The vault actually migrated — the stale upstream log entry
        # did not short-circuit the run.
        page = (
            repo / "domains" / "research-papers" / "wiki"
            / "summaries" / "2024-foo-summary.md"
        )
        assert page.is_file()
        text = page.read_text(encoding="utf-8")
        assert "compiled_against: 2" in text
        assert "migration_history:" in text

    def test_agents012_green_after_adopted_migration(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        repo = _build_adopted_v1_vault(tmp_path)
        monkeypatch.chdir(repo)
        assert migrate_cmd.run(_args()) == 0

        report = Report()
        wiki = repo / "domains" / "research-papers" / "wiki"
        for md in wiki.rglob("*.md"):
            rel = md.relative_to(repo).as_posix()
            MigrationHistoryHygiene().visit(
                rel, md.read_text(encoding="utf-8"), {}, report,
            )
        assert [d.message for d in report.diagnostics] == []
