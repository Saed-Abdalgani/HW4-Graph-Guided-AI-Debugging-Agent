"""CLI smoke tests."""

from __future__ import annotations

import subprocess
import sys

import pytest


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
    assert "edges=462" in proc.stdout
