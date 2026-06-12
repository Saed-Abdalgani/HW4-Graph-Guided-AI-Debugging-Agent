"""Extract OOP-relevant subgraph (inherits / contains / uses / method)."""

from __future__ import annotations

import networkx as nx

from graphdebug.services.analysis.nx_from_graph import oop_edge_iter
from graphdebug.services.graphify.models import CodeGraph


def build_oop_digraph(graph: CodeGraph) -> nx.DiGraph:
    """Directed graph over all endpoints of OOP relations (project-wide)."""
    g = nx.DiGraph()
    for e in oop_edge_iter(graph.edges):
        if e.source not in graph.nodes or e.target not in graph.nodes:
            continue
        w = 1.0 if e.weight is None else float(e.weight)
        g.add_node(e.source)
        g.add_node(e.target)
        if g.has_edge(e.source, e.target):
            g[e.source][e.target]["weight"] += w
        else:
            g.add_edge(e.source, e.target, relation=e.relation, weight=w)
    return g
