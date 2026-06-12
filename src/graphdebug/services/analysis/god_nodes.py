"""God-node selection from centrality scores (evidence-backed, Phase 4)."""

from __future__ import annotations

from graphdebug.services.analysis.types import CentralityRow, GodNode


def select_god_nodes(
    rows: list[CentralityRow],
    *,
    top_k: int,
    percentile_cutoff: float,
) -> list[GodNode]:
    """
    God nodes = high betweenness hubs in the *project* subgraph.

    Rule: take the top ``top_k`` by betweenness, union any node at or above the
    given betweenness **percentile** (0–100). Each row carries numeric scores.
    """
    if not rows:
        return []
    scores = [r.betweenness for r in rows]
    cutoff = _percentile(scores, percentile_cutoff)
    chosen: dict[str, CentralityRow] = {}
    for r in rows[:top_k]:
        chosen[r.node_id] = r
    for r in rows:
        if r.betweenness >= cutoff:
            chosen[r.node_id] = r
    ordered = sorted(chosen.values(), key=lambda x: -x.betweenness)
    return [_to_god(row) for row in ordered[:20]]


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    if p <= 0:
        return s[0]
    if p >= 100:
        return s[-1]
    idx = (len(s) - 1) * (p / 100.0)
    lo = int(idx)
    hi = min(lo + 1, len(s) - 1)
    frac = idx - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def _to_god(r: CentralityRow) -> GodNode:
    deg = r.degree_in + r.degree_out
    rationale = (
        f"High betweenness ({r.betweenness:.4f}) on imports/calls/contains subgraph; "
        f"weighted degree {deg} (in {r.degree_in}, out {r.degree_out})."
    )
    return GodNode(
        node_id=r.node_id,
        label=r.label,
        betweenness=r.betweenness,
        degree_total=deg,
        rationale=rationale,
    )
