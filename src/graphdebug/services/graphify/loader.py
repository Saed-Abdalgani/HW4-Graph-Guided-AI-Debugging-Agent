"""Load Graphify ``graph.json`` artifacts into typed objects."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from graphdebug.services.graphify.models import (
    CodeGraph,
    GraphCluster,
    GraphEdge,
    GraphNode,
    freeze_attrs,
)
from graphdebug.services.graphify.schema import (
    GraphLoadError,
    optional_float,
    optional_text,
    sequence,
    text,
)


def load_graph(path: str | Path) -> CodeGraph:
    graph_path = Path(path)
    if not graph_path.is_file():
        raise GraphLoadError(f"Graph artifact not found: {graph_path}")

    try:
        data = json.loads(graph_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GraphLoadError(f"Invalid JSON in {graph_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GraphLoadError(f"Graph artifact must be a JSON object: {graph_path}")

    nodes_raw = sequence(data, "nodes")
    edges_raw = sequence(data, "edges") if "edges" in data else sequence(data, "links")
    nodes, duplicate_node_ids = _parse_nodes(nodes_raw)
    edges = tuple(_parse_edges(edges_raw))
    labels = _load_cluster_labels(graph_path)
    clusters = _parse_clusters(nodes.values(), labels)
    metadata = {k: v for k, v in data.items() if k not in {"nodes", "edges", "links"}}
    metadata["raw_node_count"] = len(nodes_raw)
    metadata["raw_edge_count"] = len(edges_raw)
    if duplicate_node_ids:
        metadata["duplicate_node_ids"] = duplicate_node_ids

    return CodeGraph(
        path=str(graph_path),
        nodes=freeze_attrs(nodes),
        edges=edges,
        clusters=freeze_attrs(clusters),
        metadata=freeze_attrs(metadata),
        hyperedge_count=len(data.get("hyperedges", [])),
        directed=bool(data.get("directed", True)),
    )


def _parse_nodes(nodes_raw: Sequence[Any]) -> tuple[dict[str, GraphNode], dict[str, int]]:
    nodes: dict[str, GraphNode] = {}
    duplicate_counts: dict[str, int] = {}
    for index, raw in enumerate(nodes_raw):
        if not isinstance(raw, dict):
            raise GraphLoadError(f"Node #{index} must be an object.")
        node_id = text(raw, ("id", "key", "name"), where=f"node #{index}")
        if node_id in nodes:
            duplicate_counts[node_id] = duplicate_counts.get(node_id, 1) + 1
            continue
        label = str(raw.get("label") or raw.get("name") or node_id)
        kind = optional_text(raw, "kind") or optional_text(raw, "type")
        kind = kind or optional_text(raw, "file_type")
        nodes[node_id] = GraphNode(
            id=node_id,
            label=label,
            kind=kind,
            source_file=optional_text(raw, "source_file"),
            source_location=optional_text(raw, "source_location"),
            attrs=freeze_attrs(raw),
        )
    return nodes, duplicate_counts


def _parse_edges(edges_raw: Sequence[Any]) -> Iterable[GraphEdge]:
    for index, raw in enumerate(edges_raw):
        if not isinstance(raw, dict):
            raise GraphLoadError(f"Edge #{index} must be an object.")
        source = text(raw, ("source", "from", "u"), where=f"edge #{index}")
        target = text(raw, ("target", "to", "v"), where=f"edge #{index}")
        relation = str(raw.get("relation") or raw.get("type") or raw.get("label") or "related")
        yield GraphEdge(
            source=source,
            target=target,
            relation=relation,
            confidence=optional_text(raw, "confidence"),
            source_file=optional_text(raw, "source_file"),
            source_location=optional_text(raw, "source_location"),
            weight=optional_float(raw.get("weight")),
            attrs=freeze_attrs(raw),
        )


def _parse_clusters(
    nodes: Iterable[GraphNode], labels: Mapping[str, str]
) -> dict[str, GraphCluster]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        cluster = _cluster_value(node.attrs)
        if cluster is not None:
            grouped[cluster].append(node.id)
    return {
        cluster_id: GraphCluster(
            id=cluster_id,
            label=labels.get(cluster_id, f"Community {cluster_id}"),
            node_ids=tuple(sorted(node_ids)),
        )
        for cluster_id, node_ids in sorted(grouped.items())
    }


def _cluster_value(attrs: Mapping[str, Any]) -> str | None:
    for key in ("community", "community_id", "cluster", "group"):
        value = attrs.get(key)
        if value is not None:
            return str(value)
    return None


def _load_cluster_labels(graph_path: Path) -> dict[str, str]:
    labels_path = graph_path.with_name(".graphify_labels.json")
    if not labels_path.is_file():
        return {}
    try:
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GraphLoadError(f"Invalid cluster label JSON in {labels_path}: {exc}") from exc
    if not isinstance(labels, dict):
        raise GraphLoadError(f"Cluster label file must be an object: {labels_path}")
    return {str(key): str(value) for key, value in labels.items()}
