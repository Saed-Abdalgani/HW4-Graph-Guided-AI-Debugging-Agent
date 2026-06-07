"""SDK-level tests for graph-only query helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphdebug.sdk.api import (
    GraphQueryError,
    edge_details,
    graph_sanity,
    load_code_graph,
    neighbors,
    path_between_nodes,
    traverse_hops,
)


def _fixture_graph(tmp_path: Path):
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "nodes": [
                    {"id": "A", "label": "module"},
                    {"id": "B", "label": "function"},
                    {"id": "C", "label": "helper"},
                    {"id": "D", "label": "isolated"},
                ],
                "edges": [
                    {"source": "A", "target": "B", "relation": "calls", "weight": 2},
                    {"source": "B", "target": "C", "relation": "contains"},
                    {"source": "C", "target": "A", "relation": "imports"},
                    {"source": "B", "target": "MISSING", "relation": "calls"},
                ],
                "hyperedges": [],
            }
        ),
        encoding="utf-8",
    )
    return load_code_graph(graph_path)


def test_neighbors_are_direction_and_relation_aware(tmp_path: Path) -> None:
    graph = _fixture_graph(tmp_path)

    assert [node.id for node in neighbors(graph, "A")] == ["B"]
    assert [node.id for node in neighbors(graph, "A", direction="in")] == ["C"]
    assert [node.id for node in neighbors(graph, "B", relation="contains")] == ["C"]


def test_traverse_hops_and_path(tmp_path: Path) -> None:
    graph = _fixture_graph(tmp_path)

    assert [node.id for node in traverse_hops(graph, "A", hops=2, direction="out")] == [
        "B",
        "C",
    ]
    assert path_between_nodes(graph, "A", "C") == ("A", "B", "C")
    assert path_between_nodes(graph, "A", "C", max_hops=1) == ()
    assert path_between_nodes(graph, "A", "A") == ("A",)


def test_edge_details_and_sanity(tmp_path: Path) -> None:
    graph = _fixture_graph(tmp_path)

    edges = edge_details(graph, "A", "B", relation="calls")
    assert len(edges) == 1
    assert edges[0].weight == 2.0

    sanity = graph_sanity(graph)
    assert sanity.dangling_edges[0].target == "MISSING"
    assert sanity.isolated_node_ids == ("D",)
    assert sanity.relation_counts["calls"] == 2


def test_query_errors(tmp_path: Path) -> None:
    graph = _fixture_graph(tmp_path)

    with pytest.raises(GraphQueryError, match="Unsupported direction"):
        neighbors(graph, "A", direction="sideways")  # type: ignore[arg-type]
    with pytest.raises(GraphQueryError, match="hops"):
        traverse_hops(graph, "A", hops=-1)
    with pytest.raises(KeyError, match="Unknown graph node"):
        path_between_nodes(graph, "A", "Z")
