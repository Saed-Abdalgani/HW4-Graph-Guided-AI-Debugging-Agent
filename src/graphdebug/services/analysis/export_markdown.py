"""Markdown writers for Phase 4 reports."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.analysis.types import CentralityRow, GodNode


def write_god_nodes_markdown(
    path: Path,
    gods: list[GodNode],
    top_rows: list[CentralityRow],
    analysis_cfg: dict,
) -> None:
    lines = [
        "# God nodes (centrality-backed)",
        "",
        "## Method",
        "",
        "- **Metrics**: directed betweenness (normalized) and weighted in/out degree on the "
        "subgraph induced by **imports**, **imports_from**, **calls**, and **contains** edges.",
        "- **Scope**: nodes whose `source_file` matches prefixes "
        f"`{analysis_cfg.get('source_prefixes')!r}`.",
        "- **Selection**: top "
        f"`{analysis_cfg.get('god_top_k', 8)}` by betweenness, union nodes at or above the "
        f"`{analysis_cfg.get('god_percentile', 92.0)}`th percentile of betweenness.",
        "- **Rationale nodes** (`file_type` / kind = rationale) excluded from the metric graph.",
        "",
        "## Ranked god nodes",
        "",
        "| Node id | Label | Betweenness | Deg (in+out) | Why |",
        "|---|---:|---:|---:|---|",
    ]
    for g in gods:
        row = (
            f"| `{g.node_id}` | {g.label} | {g.betweenness:.4f} | {g.degree_total} | "
            f"{g.rationale} |"
        )
        lines.append(row)
    lines.extend(
        [
            "",
            "## Top raw centrality (preview)",
            "",
            "| Rank | Label | Betweenness | Closeness | deg_in | deg_out |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for i, r in enumerate(top_rows, start=1):
        lines.append(
            f"| {i} | {r.label} | {r.betweenness:.4f} | {r.closeness:.4f} | {r.degree_in} | "
            f"{r.degree_out} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_obsidian_god_nodes(path: Path, gods: list[GodNode], analysis_cfg: dict) -> None:
    lines = [
        "# God nodes",
        "",
        "> Phase 4 — evidence-backed hubs (see also [[index]] and `reports/god_nodes.md`).",
        "",
        "## Metric & threshold",
        "",
        "- Betweenness + degree on structural subgraph; prefixes "
        f"{analysis_cfg.get('source_prefixes')!r}.",
        "",
        "## Table",
        "",
        "| Node | Betweenness | Degree | Note |",
        "|---|---:|---:|---|",
    ]
    for g in gods:
        lines.append(f"| `{g.node_id}` | {g.betweenness:.4f} | {g.degree_total} | {g.rationale} |")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_architecture_rq_report(
    path: Path,
    communities: list[frozenset[str]],
    inter_links: list[tuple[int, int, str, float]],
    labels: list[str],
) -> None:
    text = f"""# Architecture insight (RQ1, RQ4)

## RQ1 — What the code *really* does vs first glance

At first glance PySnooper reads like a small decorator around `sys.settrace`. The Graphify
graph shows a denser **runtime composition**: `Tracer` coordinates frame filtering, thread
padding, output sinks, and variable formatting across modules — not a single linear script.
The **block diagram** (`assets/architecture.png`) collapses thousands of AST nodes into
**Louvain communities** on the *structural* edge slice (imports / calls / contains), so blocks
reflect coupling topology rather than directory names.

## RQ4 — How diagrams were extracted when docs are thin

Official docs emphasize the public decorator API; they do not spell out every composition edge.
We derived structure from `graph.json` **relations** (confidence `EXTRACTED` where present),
then **spot-checked** a few `inherits` / `contains` chains (e.g., `PathLike` → `ABC` in
`pycompat.py`) against the subject source. Semantic / LLM-labeled edges in the artifact were
treated skeptically; the OOP diagram prefers the **inherits / contains / uses / method** slice.

## Block model summary

- **Communities detected**: {len(communities)}
- **Strongest cross-block links (relation, weight)**:

"""
    for a, b, rel, w in inter_links[:12]:
        la = labels[a] if a < len(labels) else str(a)
        lb = labels[b] if b < len(labels) else str(b)
        text += f"- `{la}` → `{lb}` — **{rel}** (weight {w:.1f})\n"

    text += """
## What was not obvious before the graph

- Test utilities and helpers attach to the same import hub as core tracing, so regressions can
  surface far from the failing test file.
- Output encoding concerns (`FileWriter`) sit on a high-traffic path between formatting and I/O,
  which centrality ranks near the top even before reading implementation details.

## Assets

- `assets/architecture.png` / `architecture.mmd` — subsystem graph.
- `assets/oop.png` / `oop.mmd` — OOP relation slice (trimmed for readability).
"""
    path.write_text(text, encoding="utf-8")
