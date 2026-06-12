"""Render architecture block diagram (modularity subsystems) to PNG + Mermaid."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from graphdebug.services.graphify.models import CodeGraph


def _short_label(text: str, max_len: int = 28) -> str:
    t = text.replace('"', "'")
    return t if len(t) <= max_len else t[: max_len - 1] + "…"


def block_labels(graph: CodeGraph, communities: list[frozenset[str]]) -> list[str]:
    out: list[str] = []
    for comm in communities:
        files: set[str] = set()
        for nid in comm:
            node = graph.nodes.get(nid)
            if node and node.source_file:
                files.add(node.source_file.replace("\\", "/").split("/")[-1])
        hint = ", ".join(sorted(files)[:3])
        if hint:
            out.append(f"B{len(out)} (n={len(comm)})\n{hint}")
        else:
            out.append(f"B{len(out)} (n={len(comm)})")
    return out


def write_architecture_mermaid(
    labels: list[str],
    inter_links: list[tuple[int, int, str, float]],
    path: Path,
    *,
    max_edges: int = 40,
) -> None:
    lines = ["flowchart LR"]
    for i, lab in enumerate(labels):
        safe = _short_label(lab.replace("\n", " — "), 40)
        lines.append(f'  _{i}["{safe}"]')
    for a, b, rel, _w in inter_links[:max_edges]:
        lines.append(f"  _{a} -->|{rel}| _{b}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_architecture_png(
    labels: list[str],
    inter_links: list[tuple[int, int, str, float]],
    path: Path,
    *,
    max_edges: int = 40,
) -> None:
    q = nx.DiGraph()
    for i, lab in enumerate(labels):
        q.add_node(i, label=_short_label(lab.replace("\n", " "), 32))
    for a, b, rel, w in inter_links[:max_edges]:
        if q.has_edge(a, b):
            q[a][b]["weight"] += w
        else:
            q.add_edge(a, b, weight=w, relation=rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not len(q):
        _, ax = plt.subplots(figsize=(8, 3), dpi=100)
        ax.text(0.5, 0.5, "No subsystem blocks to draw.", ha="center", va="center", fontsize=11)
        ax.set_axis_off()
        plt.tight_layout()
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return
    pos = nx.spring_layout(q.to_undirected(), seed=42, k=1.8 / max(1, len(q) ** 0.5))
    _, ax = plt.subplots(figsize=(11, 7), dpi=120)
    nx.draw_networkx_nodes(q, pos, node_color="#c8e6c9", node_size=2800, ax=ax)
    nx.draw_networkx_labels(q, pos, labels={i: q.nodes[i]["label"] for i in q}, font_size=8, ax=ax)
    edges = list(q.edges(data=True))
    nx.draw_networkx_edges(
        q,
        pos,
        edgelist=[(u, v) for u, v, _ in edges],
        arrows=True,
        arrowsize=14,
        width=[max(0.8, min(4.0, d.get("weight", 1.0))) for _, _, d in edges],
        ax=ax,
    )
    edge_labels = {(u, v): str(d.get("relation", ""))[:12] for u, v, d in edges}
    nx.draw_networkx_edge_labels(q, pos, edge_labels=edge_labels, font_size=7, ax=ax)
    ax.set_axis_off()
    ax.set_title("Architecture blocks (Louvain on structural graph)", fontsize=11)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
