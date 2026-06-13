"""Rank graph nodes as bug suspects (FR-A3, FR-E1)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from graphdebug.services.agents.state import SuspectNode
from graphdebug.services.analysis.centrality import build_metric_digraph, compute_centrality_rows
from graphdebug.services.graphify.models import CodeGraph
from graphdebug.services.graphify.query import path_between_nodes


def _test_anchor_ids(graph: CodeGraph, failing_tests: Sequence[str]) -> list[str]:
    anchors: list[str] = []
    needles = [ft.replace("\\", "/").lower() for ft in failing_tests]
    for nid, node in graph.nodes.items():
        sf = (node.source_file or "").replace("\\", "/").lower()
        lab = (node.label or "").lower()
        for n in needles:
            if n and (n in sf or n in lab or any(part in sf for part in n.split("::") if part)):
                anchors.append(nid)
                break
    return anchors


def _min_hop_distance(graph: CodeGraph, node_id: str, anchors: Iterable[str]) -> float:
    best = 1e9
    for a in anchors:
        if a == node_id:
            return 0.0
        p = path_between_nodes(graph, node_id, a, direction="both", max_hops=12)
        if p:
            best = min(best, float(len(p) - 1))
    return best if best < 1e8 else 12.0


def rank_suspects(
    graph: CodeGraph,
    *,
    failing_tests: Sequence[str],
    source_prefixes: tuple[str, ...],
    top_k: int = 8,
) -> list[SuspectNode]:
    dg = build_metric_digraph(graph, source_prefixes=source_prefixes)
    rows = compute_centrality_rows(graph, dg)
    anchors = _test_anchor_ids(graph, failing_tests)
    if not anchors:
        anchors = [r.node_id for r in rows[:3]]

    out: list[SuspectNode] = []
    for row in rows[: max(top_k * 4, 16)]:
        nid = row.node_id
        node = graph.nodes.get(nid)
        if node is None:
            continue
        kind = (node.kind or "").lower()
        if kind == "rationale":
            continue
        dist = _min_hop_distance(graph, nid, anchors)
        prox = 1.0 / (1.0 + dist)
        score = row.betweenness + 0.35 * prox + 0.05 * row.closeness
        why = (
            f"betweenness={row.betweenness:.4f}, test_proximity={prox:.4f} "
            f"(~{dist:.0f} hops to anchor), kind={kind or '?'}"
        )
        out.append(
            SuspectNode(
                node_id=nid,
                score=float(score),
                why=why,
                betweenness=float(row.betweenness),
                test_proximity=float(prox),
            )
        )
    out.sort(key=lambda s: s.score, reverse=True)
    return out[:top_k]


__all__ = ["rank_suspects"]
