"""Centrality metrics over a structural ``CodeGraph`` view (NetworkX)."""

from __future__ import annotations

import networkx as nx

from graphdebug.services.analysis.nx_from_graph import (
    ARCH_BLOCK_RELATIONS,
    project_node_ids,
    structural_digraph,
)
from graphdebug.services.analysis.types import CentralityRow
from graphdebug.services.graphify.models import CodeGraph


def build_metric_digraph(
    graph: CodeGraph,
    *,
    source_prefixes: tuple[str, ...],
) -> nx.DiGraph:
    ids = project_node_ids(graph, source_prefixes)
    return structural_digraph(
        graph,
        relations=ARCH_BLOCK_RELATIONS,
        node_ids=ids if ids else None,
    )


def compute_centrality_rows(graph: CodeGraph, dg: nx.DiGraph) -> list[CentralityRow]:
    """Return nodes sorted by betweenness (desc), then total degree."""
    if not len(dg):
        return []

    n = dg.number_of_nodes()
    if n <= 200:
        between = nx.betweenness_centrality(dg, normalized=True, weight="weight")
    else:
        between = nx.betweenness_centrality(
            dg,
            normalized=True,
            weight="weight",
            k=min(100, n),
            seed=42,
        )
    close = nx.closeness_centrality(dg, distance="weight", wf_improved=True)

    rows: list[CentralityRow] = []
    for nid in dg.nodes:
        node = graph.nodes.get(nid)
        label = node.label if node else nid
        din = int(dg.in_degree(nid, weight="weight") or dg.in_degree(nid))
        dout = int(dg.out_degree(nid, weight="weight") or dg.out_degree(nid))
        rows.append(
            CentralityRow(
                node_id=nid,
                label=label,
                degree_in=din,
                degree_out=dout,
                betweenness=float(between.get(nid, 0.0)),
                closeness=float(close.get(nid, 0.0)),
            )
        )
    rows.sort(
        key=lambda r: (r.betweenness, r.degree_in + r.degree_out, r.label),
        reverse=True,
    )
    return rows
