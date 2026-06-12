"""Tests for ``services/vault/builder.py``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphdebug.sdk.api import load_code_graph
from graphdebug.services.vault.builder import build_vault

ROOT = Path(__file__).resolve().parents[2]
REAL_GRAPH = ROOT / "artifacts" / "graphify" / "graph.json"


def _tiny_graph(tmp_path: Path) -> Path:
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "directed": True,
                "nodes": [
                    {
                        "id": "tests_test_chinese_test_chinese",
                        "label": "test_chinese()",
                        "kind": "function",
                        "source_file": "tests/test_chinese.py",
                    },
                    {
                        "id": "tests_test_chinese",
                        "label": "test_chinese.py",
                        "kind": "file",
                        "source_file": "tests/test_chinese.py",
                    },
                    {
                        "id": "pysnooper_tracer_filewriter",
                        "label": "FileWriter",
                        "kind": "class",
                        "source_file": "pysnooper/tracer.py",
                    },
                    {
                        "id": "pysnooper_tracer_filewriter_write",
                        "label": ".write()",
                        "kind": "function",
                        "source_file": "pysnooper/tracer.py",
                    },
                ],
                "edges": [
                    {
                        "source": "tests_test_chinese_test_chinese",
                        "target": "pysnooper_tracer_filewriter_write",
                        "relation": "calls",
                    },
                    {
                        "source": "pysnooper_tracer_filewriter_write",
                        "target": "pysnooper_tracer_filewriter",
                        "relation": "member_of",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return graph_path


def test_build_vault_writes_focus_pages(tmp_path: Path) -> None:
    graph = load_code_graph(_tiny_graph(tmp_path))
    vault = tmp_path / "vault"
    result = build_vault(graph, vault, copy_graph_report=False)

    assert len(result.graph_pages) == 4
    assert (vault / "generated" / "pysnooper_tracer_filewriter.md").is_file()
    assert result.graph_report_copy is None
    assert len(result.suspect_pages) == 1
    assert len(result.finding_pages) == 1
    assert len(result.stubs) == 2
    text = (vault / "generated" / "pysnooper_tracer_filewriter_write.md").read_text(
        encoding="utf-8"
    )
    assert "[[generated/tests_test_chinese_test_chinese]]" in text


@pytest.mark.skipif(not REAL_GRAPH.is_file(), reason="Graphify artifact not present")
def test_build_vault_copies_graph_report(tmp_path: Path) -> None:
    graph = load_code_graph(REAL_GRAPH)
    vault = tmp_path / "vault"
    result = build_vault(graph, vault, copy_graph_report=True)
    assert result.graph_report_copy is not None
    assert result.graph_report_copy.name == "GRAPH_REPORT.md"
    assert "Graph Report" in result.graph_report_copy.read_text(encoding="utf-8")


@pytest.mark.skipif(not REAL_GRAPH.is_file(), reason="Graphify artifact not present")
def test_build_project_vault_runs_snapshot() -> None:
    from graphdebug.sdk.api import build_project_vault, load_config

    cfg = load_config(project_root=ROOT, require_api_key=False)
    build_project_vault(cfg, capture_snapshot=True)
    manifest = ROOT / "results" / "knowledge_snapshots" / "before" / "manifest.json"
    assert manifest.is_file()
