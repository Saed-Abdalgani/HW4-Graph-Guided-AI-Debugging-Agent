"""Heuristic doc vs. structural graph signals (FR-E3, T9.4)."""

from __future__ import annotations

from dataclasses import dataclass

from graphdebug.services.graphify.models import CodeGraph
from graphdebug.services.graphify.query import neighbors

_STABLE = ("immutable", "read-only", "no side effect", "does not modify", "pure function")
_RISKY = ("write", "remove", "delete", "mutate", "open(", "os.remove", "unlink")


@dataclass(frozen=True, slots=True)
class DocSignal:
    node_id: str
    signal: str


def doc_graph_signals(graph: CodeGraph) -> tuple[DocSignal, ...]:
    """Flag nodes whose documentation claims stability but graph shows risky callees."""
    out: list[DocSignal] = []
    for nid, node in graph.nodes.items():
        doc = str(node.attrs.get("documentation", "") or "").lower()
        doc += " " + (node.label or "").lower()
        if not any(s in doc for s in _STABLE):
            continue
        for nb in neighbors(graph, nid, direction="out"):
            lab = (nb.label or "").lower()
            if any(r in lab for r in _RISKY):
                out.append(
                    DocSignal(
                        nid,
                        "doc implies stable/pure but an outgoing neighbor looks side-effecting",
                    )
                )
                break
    return tuple(out)


__all__ = ["DocSignal", "doc_graph_signals"]
