"""Phase 4 analysis: centrality, god nodes, subsystems."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.services.analysis.centrality import build_metric_digraph, compute_centrality_rows
from graphdebug.services.analysis.export import export_phase4
from graphdebug.services.analysis.god_nodes import select_god_nodes
from graphdebug.services.analysis.oop_slice import build_oop_digraph
from graphdebug.services.analysis.subsystems import infer_subsystems
from graphdebug.services.graphify.loader import load_graph
from graphdebug.shared.config import AppConfig, BudgetProfile, RetrieverConfig


def _tiny_graph(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "hub",
                        "label": "hub",
                        "file_type": "code",
                        "source_file": "pysnooper/hub.py",
                    },
                    {"id": "a", "label": "a", "file_type": "code", "source_file": "pysnooper/a.py"},
                    {"id": "b", "label": "b", "file_type": "code", "source_file": "pysnooper/b.py"},
                    {"id": "c", "label": "c", "file_type": "code", "source_file": "pysnooper/c.py"},
                ],
                "edges": [
                    {"source": "a", "target": "hub", "relation": "imports"},
                    {"source": "b", "target": "hub", "relation": "imports"},
                    {"source": "hub", "target": "c", "relation": "calls"},
                ],
            }
        ),
        encoding="utf-8",
    )
def test_centrality_prefers_hub(tmp_path: Path) -> None:
    gp = tmp_path / "graph.json"
    _tiny_graph(gp)
    graph = load_graph(gp)
    dg = build_metric_digraph(graph, source_prefixes=("pysnooper/",))
    rows = compute_centrality_rows(graph, dg)
    assert rows[0].node_id == "hub"
    assert rows[0].betweenness > rows[1].betweenness
def test_god_nodes_include_hub(tmp_path: Path) -> None:
    gp = tmp_path / "graph.json"
    _tiny_graph(gp)
    graph = load_graph(gp)
    dg = build_metric_digraph(graph, source_prefixes=("pysnooper/",))
    rows = compute_centrality_rows(graph, dg)
    gods = select_god_nodes(rows, top_k=3, percentile_cutoff=50.0)
    assert any(g.node_id == "hub" for g in gods)
def test_infer_subsystems_non_empty(tmp_path: Path) -> None:
    gp = tmp_path / "graph.json"
    _tiny_graph(gp)
    graph = load_graph(gp)
    comm, links = infer_subsystems(
        graph, source_prefixes=("pysnooper/",), seed=1, resolution=1.0
    )
    assert len(comm) >= 1
    assert isinstance(links, list)
def test_oop_digraph_builds(tmp_path: Path) -> None:
    gp = tmp_path / "graph.json"
    gp.write_text(
        json.dumps(
            {
                "nodes": [
                    {"id": "C", "label": "C", "file_type": "code", "source_file": "pysnooper/m.py"},
                    {"id": "D", "label": "D", "file_type": "code", "source_file": "pysnooper/m.py"},
                ],
                "edges": [
                    {"source": "C", "target": "D", "relation": "inherits"},
                ],
            }
        ),
        encoding="utf-8",
    )
    graph = load_graph(gp)
    g = build_oop_digraph(graph)
    assert g.has_edge("C", "D")
def _minimal_config(root: Path) -> AppConfig:
    raw = {
        "llm": {"provider": "openai", "model": "x", "temperature": 0.0, "max_output_tokens": 1},
        "gatekeeper": {
            "requests_per_minute": 1,
            "tokens_per_minute": 1,
            "max_retries": 0,
            "backoff_base_seconds": 0.1,
            "max_backoff_seconds": 0.2,
            "queue_size": 1,
        },
        "budgets": {
            "naive": {
                "max_tokens": 1,
                "max_tool_calls": 1,
                "max_files": 1,
                "max_iterations": 1,
            },
            "graph": {
                "max_tokens": 1,
                "max_tool_calls": 1,
                "max_files": 1,
                "max_iterations": 1,
            },
        },
        "paths": {
            "graphify_artifacts": "gart",
            "obsidian_vault": "ob",
            "results": "res",
            "data_root": "data",
            "reports": "rep",
        },
        "retriever": {"max_lines_per_file": 10, "max_suspects_fetched": 2},
        "features": {"hitl_required": True, "enable_langsmith": False},
        "analysis": {"source_prefixes": ["pysnooper/"]},
    }
    budgets = {
        "naive": BudgetProfile(1, 1, 1, 1),
        "graph": BudgetProfile(1, 1, 1, 1),
    }
    paths = {k: (root / v).resolve() for k, v in raw["paths"].items()}
    return AppConfig(
        raw=raw,
        project_root=root,
        llm=dict(raw["llm"]),
        gatekeeper=dict(raw["gatekeeper"]),
        budgets=budgets,
        paths=paths,
        features=dict(raw["features"]),
        retriever=RetrieverConfig(max_lines_per_file=10, max_suspects_fetched=2),
        openai_api_key=None,
    )


def test_export_phase4_writes_outputs(tmp_path: Path) -> None:
    root = tmp_path
    (root / "gart").mkdir()
    _tiny_graph(root / "gart" / "graph.json")
    cfg = _minimal_config(root)
    res = export_phase4(
        cfg,
        graph_path=root / "gart" / "graph.json",
        reports_dir=root / "out_rep",
        assets_dir=root / "out_assets",
        vault_dir=root / "out_vault",
    )
    assert res.architecture_png.is_file()
    assert res.oop_png.is_file()
    assert res.god_nodes_report.is_file()
    assert "hub" in res.god_nodes_report.read_text(encoding="utf-8")
