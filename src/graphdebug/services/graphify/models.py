"""Typed in-memory representation for Graphify artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def freeze_attrs(attrs: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(attrs))


@dataclass(frozen=True, slots=True)
class GraphNode:
    id: str
    label: str
    kind: str | None
    source_file: str | None
    source_location: str | None
    attrs: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str
    target: str
    relation: str
    confidence: str | None
    source_file: str | None
    source_location: str | None
    weight: float | None
    attrs: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class GraphCluster:
    id: str
    label: str
    node_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GraphSanity:
    node_count: int
    edge_count: int
    hyperedge_count: int
    dangling_edges: tuple[GraphEdge, ...]
    isolated_node_ids: tuple[str, ...]
    relation_counts: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class CodeGraph:
    path: str
    nodes: Mapping[str, GraphNode]
    edges: tuple[GraphEdge, ...]
    clusters: Mapping[str, GraphCluster]
    metadata: Mapping[str, Any]
    hyperedge_count: int
    directed: bool = True

    def require_node(self, node_id: str) -> GraphNode:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"Unknown graph node: {node_id}") from exc
