"""CLI smoke tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REAL_GRAPH = ROOT / "artifacts" / "graphify" / "graph.json"


def test_cli_main_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["graphdebug"])
    from graphdebug.cli import main

    main()


def test_graphdebug_help_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "graphdebug.cli", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "graphdebug" in proc.stdout.lower() or "graph-guided" in proc.stdout.lower()


def test_graphdebug_graphify_load_command() -> None:
    graph_path = "artifacts/graphify/graph.json"
    proc = subprocess.run(
        [sys.executable, "-m", "graphdebug.cli", "graphify-load", "--in", graph_path],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "nodes=149" in proc.stdout


def test_graphdebug_vault_build_command() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "graphdebug.cli",
            "vault-build",
            "--project-root",
            str(ROOT),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert "graph_pages=4" in proc.stdout


@pytest.mark.skipif(not REAL_GRAPH.is_file(), reason="Graphify artifact not present")
def test_graphdebug_vault_build_with_graph_flag() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "graphdebug.cli",
            "vault-build",
            "--project-root",
            str(ROOT),
            "--graph",
            str(REAL_GRAPH),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert "graph_pages=4" in proc.stdout


def test_graphdebug_vault_snapshot_command() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "graphdebug.cli",
            "vault-snapshot",
            "--project-root",
            str(ROOT),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert "vault-snapshot:" in proc.stdout
