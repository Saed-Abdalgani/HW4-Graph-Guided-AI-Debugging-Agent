"""Subsystem (block) discovery via modularity communities — graph topology, not folders."""

from __future__ import annotations

from collections import defaultdict

import networkx as nx

from graphdebug.services.analysis.centrality import build_metric_digraph
from graphdebug.services.analysis.nx_from_graph import ARCH_BLOCK_RELATIONS, to_simple_undirected
from graphdebug.services.graphify.models import CodeGraph


def infer_subsystems(
    graph: CodeGraph,
    *,
    source_prefixes: tuple[str, ...],
    seed: int,
    resolution: float,
) -> tuple[list[frozenset[str]], list[tuple[int, int, str, float]]]:
    """
    Return (communities, inter_links) where each inter_link is
    (block_a, block_b, relation, weight) aggregated from original directed edges.
    """
    dg = build_metric_digraph(graph, source_prefixes=source_prefixes)
    ug = to_simple_undirected(dg)
    if ug.number_of_nodes() == 0:
        return [], []
    communities = list(
        nx.community.louvain_communities(ug, weight="weight", seed=seed, resolution=resolution)
    )
    node_to_block: dict[str, int] = {}
    for bi, comm in enumerate(communities):
        for nid in comm:
            node_to_block[nid] = bi

    pair_rel_w: dict[tuple[int, int, str], float] = defaultdict(float)
    for e in graph.edges:
        if e.relation not in ARCH_BLOCK_RELATIONS:
            continue
        bu, bv = node_to_block.get(e.source), node_to_block.get(e.target)
        if bu is None or bv is None or bu == bv:
            continue
        w = 1.0 if e.weight is None else float(e.weight)
        a, b = (bu, bv) if bu < bv else (bv, bu)
        pair_rel_w[(a, b, e.relation)] += w

    inter_links = [(a, b, rel, w) for (a, b, rel), w in pair_rel_w.items()]
    inter_links.sort(key=lambda t: -t[3])
    return communities, inter_links
