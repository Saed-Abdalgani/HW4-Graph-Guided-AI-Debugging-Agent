"""Render OOP subgraph diagram (inherits / contains / uses / method)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from graphdebug.services.graphify.models import CodeGraph


def _trim_digraph(dg: nx.DiGraph, graph: CodeGraph, max_nodes: int) -> nx.DiGraph:
    if dg.number_of_nodes() <= max_nodes:
        return dg
    ranked = sorted(dg.nodes, key=lambda n: dg.degree(n), reverse=True)[:max_nodes]
    keep = set(ranked)
    return dg.subgraph(keep).copy()


def _node_caption(graph: CodeGraph, nid: str) -> str:
    node = graph.nodes.get(nid)
    if not node:
        return nid[-20:]
    base = node.label or nid
    return base if len(base) < 22 else base[:20] + "…"


def _write_placeholder(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _, ax = plt.subplots(figsize=(8, 3), dpi=100)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=11)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def write_oop_mermaid(dg: nx.DiGraph, graph: CodeGraph, path: Path, *, max_edges: int = 50) -> None:
    edges = sorted(dg.edges(data=True), key=lambda t: -float(t[2].get("weight", 1)))[:max_edges]
    nodes = {u for u, _, _ in edges} | {v for _, v, _ in edges}
    idmap = {nid: f"N{i}" for i, nid in enumerate(sorted(nodes))}
    lines = ["flowchart TB"]
    if not nodes:
        lines.append('  empty["(no OOP edges in selection)"]')
    else:
        for nid in sorted(nodes):
            lab = _node_caption(graph, nid).replace('"', "'")
            lines.append(f'  {idmap[nid]}["{lab}"]')
        for u, v, data in edges:
            rel = str(data.get("relation", ""))[:16]
            lines.append(f"  {idmap[u]} -->|{rel}| {idmap[v]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_oop_png(dg: nx.DiGraph, graph: CodeGraph, path: Path, *, max_nodes: int = 45) -> None:
    h = _trim_digraph(dg, graph, max_nodes)
    if not len(h):
        _write_placeholder(
            path,
            "No OOP edges (inherits / contains / uses / method) in this graph slice.",
        )
        return
    pos = nx.spring_layout(h.to_undirected(), seed=7, k=1.6 / max(1, len(h) ** 0.5))
    labels = {n: _node_caption(graph, n) for n in h}
    _, ax = plt.subplots(figsize=(12, 8), dpi=120)
    colors = ["#bbdefb"] * len(h)
    nx.draw_networkx_nodes(h, pos, node_color=colors, node_size=900, ax=ax)
    nx.draw_networkx_labels(h, pos, labels=labels, font_size=7, ax=ax)
    edges = list(h.edges(data=True))
    nx.draw_networkx_edges(
        h,
        pos,
        edgelist=[(u, v) for u, v, _ in edges],
        arrows=True,
        arrowsize=10,
        width=1.2,
        ax=ax,
    )
    el = {(u, v): str(d.get("relation", ""))[:10] for u, v, d in edges}
    nx.draw_networkx_edge_labels(h, pos, edge_labels=el, font_size=6, ax=ax)
    ax.set_axis_off()
    ax.set_title("OOP slice (inherits / contains / uses / method)", fontsize=11)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
