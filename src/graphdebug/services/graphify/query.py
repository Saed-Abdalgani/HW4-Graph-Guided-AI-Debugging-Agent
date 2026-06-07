"""Graph-only query helpers for Graphify artifacts."""

from __future__ import annotations

from collections import Counter, deque
from typing import Literal

from graphdebug.services.graphify.models import CodeGraph, GraphEdge, GraphNode, GraphSanity

Direction = Literal["out", "in", "both"]


class GraphQueryError(ValueError):
    """Raised when a graph query cannot be evaluated."""


def neighbors(
    graph: CodeGraph,
    node_id: str,
    *,
    direction: Direction = "out",
    relation: str | None = None,
) -> tuple[GraphNode, ...]:
    graph.require_node(node_id)
    seen: set[str] = set()
    result: list[GraphNode] = []
    for edge in _matching_edges(graph, node_id, direction, relation):
        other = edge.target if edge.source == node_id else edge.source
        if other in graph.nodes and other not in seen:
            seen.add(other)
            result.append(graph.nodes[other])
    return tuple(result)


def traverse_hops(
    graph: CodeGraph,
    start_id: str,
    *,
    hops: int,
    direction: Direction = "both",
    relation: str | None = None,
) -> tuple[GraphNode, ...]:
    if hops < 0:
        raise GraphQueryError("hops must be >= 0")
    graph.require_node(start_id)
    visited = {start_id}
    ordered: list[GraphNode] = []
    queue: deque[tuple[str, int]] = deque([(start_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth == hops:
            continue
        for node in neighbors(graph, current, direction=direction, relation=relation):
            if node.id in visited:
                continue
            visited.add(node.id)
            ordered.append(node)
            queue.append((node.id, depth + 1))
    return tuple(ordered)


def path_between_nodes(
    graph: CodeGraph,
    source_id: str,
    target_id: str,
    *,
    direction: Direction = "out",
    relation: str | None = None,
    max_hops: int | None = None,
) -> tuple[str, ...]:
    graph.require_node(source_id)
    graph.require_node(target_id)
    if source_id == target_id:
        return (source_id,)
    queue: deque[tuple[str, tuple[str, ...]]] = deque([(source_id, (source_id,))])
    visited = {source_id}
    while queue:
        current, path = queue.popleft()
        if max_hops is not None and len(path) - 1 >= max_hops:
            continue
        for node in neighbors(graph, current, direction=direction, relation=relation):
            if node.id == target_id:
                return (*path, target_id)
            if node.id not in visited:
                visited.add(node.id)
                queue.append((node.id, (*path, node.id)))
    return ()


def edge_details(
    graph: CodeGraph,
    source_id: str,
    target_id: str,
    *,
    relation: str | None = None,
) -> tuple[GraphEdge, ...]:
    graph.require_node(source_id)
    graph.require_node(target_id)
    return tuple(
        edge
        for edge in graph.edges
        if edge.source == source_id
        and edge.target == target_id
        and (relation is None or edge.relation == relation)
    )


def graph_sanity(graph: CodeGraph) -> GraphSanity:
    node_ids = set(graph.nodes)
    dangling = tuple(
        edge for edge in graph.edges if edge.source not in node_ids or edge.target not in node_ids
    )
    incident = {
        node_id
        for edge in graph.edges
        for node_id in (edge.source, edge.target)
        if node_id in node_ids
    }
    relation_counts = Counter(edge.relation for edge in graph.edges)
    return GraphSanity(
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        hyperedge_count=graph.hyperedge_count,
        dangling_edges=dangling,
        isolated_node_ids=tuple(sorted(node_ids - incident)),
        relation_counts=dict(sorted(relation_counts.items())),
    )


def _matching_edges(
    graph: CodeGraph,
    node_id: str,
    direction: Direction,
    relation: str | None,
) -> tuple[GraphEdge, ...]:
    if direction not in {"out", "in", "both"}:
        raise GraphQueryError(f"Unsupported direction: {direction}")
    return tuple(
        edge
        for edge in graph.edges
        if _touches(edge, node_id, direction) and (relation is None or edge.relation == relation)
    )


def _touches(edge: GraphEdge, node_id: str, direction: Direction) -> bool:
    if direction == "out":
        return edge.source == node_id
    if direction == "in":
        return edge.target == node_id
    return edge.source == node_id or edge.target == node_id
