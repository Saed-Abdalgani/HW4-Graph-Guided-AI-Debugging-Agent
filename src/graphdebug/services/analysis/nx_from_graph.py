"""Build NetworkX graphs from ``CodeGraph`` (structural relations only)."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx

from graphdebug.services.graphify.models import CodeGraph, GraphEdge

ARCH_BLOCK_RELATIONS: frozenset[str] = frozenset(
    {"imports", "imports_from", "calls", "contains"}
)
OOP_RELATIONS: frozenset[str] = frozenset({"inherits", "contains", "uses", "method"})


def _edge_weight(edge: GraphEdge) -> float:
    return 1.0 if edge.weight is None else float(edge.weight)


def project_node_ids(graph: CodeGraph, source_prefixes: tuple[str, ...]) -> frozenset[str]:
    """Keep nodes whose ``source_file`` matches a project prefix; always keep endpoints."""
    if not source_prefixes:
        return frozenset(graph.nodes)
    out: set[str] = set()
    for nid, node in graph.nodes.items():
        sf = (node.source_file or "").replace("\\", "/")
        if any(sf.startswith(p) for p in source_prefixes):
            out.add(nid)
    if not out:
        return frozenset(graph.nodes)
    return frozenset(out)


def _is_rationale(graph: CodeGraph, node_id: str) -> bool:
    node = graph.nodes[node_id]
    kind = (node.kind or "").lower()
    return kind == "rationale"


def structural_digraph(
    graph: CodeGraph,
    *,
    relations: frozenset[str],
    node_ids: frozenset[str] | None = None,
) -> nx.DiGraph:
    """Directed simple graph; parallel edges merged by summed weight."""
    g = nx.DiGraph()
    allowed = node_ids
    for nid, _ in graph.nodes.items():
        if allowed is not None and nid not in allowed:
            continue
        if _is_rationale(graph, nid):
            continue
        g.add_node(nid)
    for e in graph.edges:
        if e.relation not in relations:
            continue
        if e.source not in graph.nodes or e.target not in graph.nodes:
            continue
        if _is_rationale(graph, e.source) or _is_rationale(graph, e.target):
            continue
        if allowed is not None and (e.source not in allowed or e.target not in allowed):
            continue
        w = _edge_weight(e)
        if g.has_edge(e.source, e.target):
            g[e.source][e.target]["weight"] += w
        else:
            g.add_edge(e.source, e.target, weight=w)
    return g


def to_simple_undirected(dg: nx.DiGraph) -> nx.Graph:
    """Undirected simple graph with combined weights for modularity / layout."""
    ug = nx.Graph()
    for u, v, data in dg.edges(data=True):
        w = float(data.get("weight", 1.0))
        if ug.has_edge(u, v):
            ug[u][v]["weight"] += w
        else:
            ug.add_edge(u, v, weight=w)
    for n in dg.nodes:
        ug.add_node(n)
    return ug


def oop_edge_iter(edges: Iterable[GraphEdge]) -> Iterable[GraphEdge]:
    for e in edges:
        if e.relation in OOP_RELATIONS:
            yield e
