"""Ego-network architecture notes for before/after focus (FR-E5, T9.5)."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from graphdebug.services.graphify.models import CodeGraph
from graphdebug.services.graphify.query import neighbors


def _ego_ball(graph: CodeGraph, start_id: str, hops: int) -> frozenset[str]:
    seen: set[str] = {start_id}
    front: set[str] = {start_id}
    for _ in range(hops):
        nxt: set[str] = set()
        for nid in front:
            for nb in neighbors(graph, nid, direction="both"):
                if nb.id not in seen:
                    seen.add(nb.id)
                    nxt.add(nb.id)
        front = nxt
    return frozenset(seen)


def architecture_ego_report(
    graph: CodeGraph,
    seed_ids: Sequence[str],
    *,
    hops: int = 2,
) -> str:
    """Markdown summary of relation mix inside an undirected *hops* ball around each seed."""
    lines: list[str] = ["# Architecture — ego subgraph", ""]
    for sid in seed_ids:
        graph.require_node(sid)
        ball = _ego_ball(graph, sid, hops)
        lines.append(f"## `{sid}` — {len(ball)} nodes within {hops} hop(s)")
        ctr: Counter[str] = Counter()
        for e in graph.edges:
            if e.source in ball and e.target in ball:
                ctr[e.relation] += 1
        if not ctr:
            lines.append("- _(no internal edges in ball)_")
        else:
            for rel, c in ctr.most_common(10):
                lines.append(f"- **{rel}**: {c}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["architecture_ego_report"]
