"""Markdown for graph-backed vault pages (one node → one ``.md`` file)."""

from __future__ import annotations

from graphdebug.services.graphify.models import CodeGraph, GraphNode
from graphdebug.services.graphify.query import neighbors

from ._paths import GENERATED_DIR


def wikilink(node_id: str) -> str:
    """Obsidian link for a page under ``generated/``."""
    return f"[[{GENERATED_DIR}/{node_id}]]"


def _is_test_node(node: GraphNode) -> bool:
    sf = (node.source_file or "").replace("\\", "/").lower()
    nid = node.id.lower()
    return (
        "/tests/" in sf
        or sf.startswith("tests/")
        or "test_" in sf
        or nid.startswith("tests_")
    )


def neighbor_lines(graph: CodeGraph, node_id: str, *, limit: int = 12) -> str:
    lines: list[str] = []
    try:
        nbrs = neighbors(graph, node_id, direction="both")
    except KeyError:
        return "_No graph neighbors (missing node)._"
    for other in nbrs[:limit]:
        lines.append(f"- {wikilink(other.id)} — **{other.label}** (`{other.kind or '?'}`)")
    if len(nbrs) > limit:
        lines.append(f"- … _{len(nbrs) - limit} more_")
    return "\n".join(lines) if lines else "_No in-graph neighbors._"


def edge_sample(graph: CodeGraph, node_id: str, *, limit: int = 10) -> str:
    lines: list[str] = []
    for edge in graph.edges:
        if edge.source != node_id and edge.target != node_id:
            continue
        other = edge.target if edge.source == node_id else edge.source
        if other not in graph.nodes:
            continue
        arrow = "→" if edge.source == node_id else "←"
        lines.append(f"- `{edge.relation}` {arrow} {wikilink(other)}")
        if len(lines) >= limit:
            break
    return "\n".join(lines) if lines else ""


def render_graph_node_page(graph: CodeGraph, node: GraphNode) -> str:
    role = "Test" if _is_test_node(node) else "Component"
    lines = [
        f"# {node.label}",
        "",
        f"> **{role}** · graph node `{node.id}`",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| id | `{node.id}` |",
        f"| kind | `{node.kind or ''}` |",
        f"| source_file | `{node.source_file or ''}` |",
        f"| source_location | `{node.source_location or ''}` |",
        "",
        "## Neighbors (graph)",
        "",
        neighbor_lines(graph, node.id),
        "",
        "## Incident edges (sample)",
        "",
    ]
    block = edge_sample(graph, node.id)
    lines.append(block if block else "_No resolved incident edges in this sample._")
    lines.append("")
    lines.append("## See also")
    lines.append("")
    lines.append("- [[hot]]")
    lines.append("- [[index]]")
    lines.append("- [[GRAPH_REPORT]]")
    lines.append("")
    return "\n".join(lines)
