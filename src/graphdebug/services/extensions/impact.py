"""Reverse-dependency impact set (FR-E4, Phase 9 T9.3)."""

from __future__ import annotations

from collections import deque

from graphdebug.services.graphify.models import CodeGraph
from graphdebug.services.graphify.query import neighbors


def impact_of(graph: CodeGraph, node_id: str, *, max_hops: int = 8) -> tuple[str, ...]:
    """Nodes that transitively depend on *node_id* (BFS along incoming edges).

    If ``source -> target`` means *source uses target*, callers/importers sit on incoming
    edges to *node_id*; we walk those up to *max_hops* away.
    """
    graph.require_node(node_id)
    visited: set[str] = {node_id}
    q: deque[tuple[str, int]] = deque([(node_id, 0)])
    while q:
        cur, depth = q.popleft()
        if depth >= max_hops:
            continue
        for nb in neighbors(graph, cur, direction="in"):
            if nb.id in visited:
                continue
            visited.add(nb.id)
            q.append((nb.id, depth + 1))
    return tuple(sorted(n for n in visited if n != node_id))


__all__ = ["impact_of"]
