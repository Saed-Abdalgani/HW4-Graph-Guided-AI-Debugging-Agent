"""SDK-level tests for loading Graphify artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphdebug.sdk.api import GraphLoadError, graph_sanity, load_code_graph

ROOT = Path(__file__).resolve().parents[2]
REAL_GRAPH = ROOT / "artifacts" / "graphify" / "graph.json"


def test_load_real_graphify_artifact() -> None:
    graph = load_code_graph(REAL_GRAPH)

    assert len(graph.nodes) == 149
    assert len(graph.edges) == 462
    assert graph.hyperedge_count == 0
    assert graph.metadata["input_tokens"] == 0
    assert graph.metadata["output_tokens"] == 0
    assert graph.metadata["raw_node_count"] == 150
    assert graph.metadata["duplicate_node_ids"] == {"object": 2}

    filewriter_write = graph.nodes["pysnooper_tracer_filewriter_write"]
    assert filewriter_write.label == ".write()"
    assert filewriter_write.source_file == "pysnooper/tracer.py"

    sanity = graph_sanity(graph)
    assert sanity.node_count == 149
    assert sanity.edge_count == 462
    assert sanity.relation_counts["calls"] == 193


def test_load_links_schema_and_cluster_labels(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "directed": True,
                "nodes": [
                    {"id": "module", "label": "module.py", "community": 1},
                    {"id": "fn", "label": "fn()", "community": 1},
                ],
                "links": [{"source": "module", "target": "fn", "type": "contains"}],
                "hyperedges": [{"id": "h"}],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".graphify_labels.json").write_text('{"1": "Core"}', encoding="utf-8")

    graph = load_code_graph(graph_path)

    assert graph.clusters["1"].label == "Core"
    assert graph.clusters["1"].node_ids == ("fn", "module")
    assert graph.edges[0].relation == "contains"
    assert graph.hyperedge_count == 1
    assert graph.metadata["raw_node_count"] == 2


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ({"nodes": {}, "edges": []}, "nodes"),
        ({"nodes": [{"label": "missing id"}], "edges": []}, "node #0"),
        ({"nodes": [{"id": "a"}], "edges": [{"source": "a"}]}, "endpoint"),
    ],
)
def test_malformed_graph_raises(
    tmp_path: Path, payload: dict[str, object], match: str
) -> None:
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(GraphLoadError, match=match):
        load_code_graph(graph_path)


def test_missing_graph_raises(tmp_path: Path) -> None:
    with pytest.raises(GraphLoadError, match="not found"):
        load_code_graph(tmp_path / "missing.json")
