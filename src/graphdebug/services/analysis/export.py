"""Phase 4 export: centrality, god-node reports, diagrams (SDK-facing)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from graphdebug.services.analysis.centrality import build_metric_digraph, compute_centrality_rows
from graphdebug.services.analysis.export_markdown import (
    write_architecture_rq_report,
    write_god_nodes_markdown,
    write_obsidian_god_nodes,
)
from graphdebug.services.analysis.god_nodes import select_god_nodes
from graphdebug.services.analysis.oop_slice import build_oop_digraph
from graphdebug.services.analysis.render_architecture import (
    block_labels,
    render_architecture_png,
    write_architecture_mermaid,
)
from graphdebug.services.analysis.render_oop import render_oop_png, write_oop_mermaid
from graphdebug.services.analysis.subsystems import infer_subsystems
from graphdebug.services.analysis.types import Phase4ExportResult
from graphdebug.services.graphify.loader import load_graph
from graphdebug.shared.config import AppConfig


def _analysis_cfg(raw: dict[str, Any]) -> dict[str, Any]:
    default: dict[str, Any] = {
        "source_prefixes": ("pysnooper/", "tests/"),
        "god_top_k": 8,
        "god_percentile": 92.0,
        "louvain_seed": 42,
        "louvain_resolution": 1.15,
    }
    user = raw.get("analysis")
    if isinstance(user, dict):
        default.update({k: v for k, v in user.items() if v is not None})
    return default


def export_phase4(
    config: AppConfig,
    *,
    graph_path: Path | None = None,
    reports_dir: Path | None = None,
    assets_dir: Path | None = None,
    vault_dir: Path | None = None,
) -> Phase4ExportResult:
    root = config.project_root
    gp = graph_path or (config.paths["graphify_artifacts"] / "graph.json")
    graph = load_graph(gp)

    acfg = _analysis_cfg(config.raw)
    prefixes = tuple(str(p) for p in acfg.get("source_prefixes", ("pysnooper/", "tests/")))
    seed = int(acfg.get("louvain_seed", 42))
    resolution = float(acfg.get("louvain_resolution", 1.15))

    dg = build_metric_digraph(graph, source_prefixes=prefixes)
    rows = compute_centrality_rows(graph, dg)
    gods = select_god_nodes(
        rows,
        top_k=int(acfg.get("god_top_k", 8)),
        percentile_cutoff=float(acfg.get("god_percentile", 92.0)),
    )

    rep = reports_dir or config.paths["reports"]
    ast = assets_dir or (root / "assets")
    vlt = vault_dir or config.paths["obsidian_vault"]
    rep.mkdir(parents=True, exist_ok=True)
    ast.mkdir(parents=True, exist_ok=True)
    vlt.mkdir(parents=True, exist_ok=True)

    god_report = rep / "god_nodes.md"
    write_god_nodes_markdown(god_report, gods, rows[:25], acfg)

    obs_god = vlt / "God nodes.md"
    write_obsidian_god_nodes(obs_god, gods, acfg)

    communities, inter_links = infer_subsystems(
        graph, source_prefixes=prefixes, seed=seed, resolution=resolution
    )
    labels = block_labels(graph, communities)
    arch_png = ast / "architecture.png"
    arch_mmd = ast / "architecture.mmd"
    write_architecture_mermaid(labels, inter_links, arch_mmd)
    render_architecture_png(labels, inter_links, arch_png)

    oop = build_oop_digraph(graph)
    oop_png = ast / "oop.png"
    oop_mmd = ast / "oop.mmd"
    write_oop_mermaid(oop, graph, oop_mmd)
    render_oop_png(oop, graph, oop_png)

    arch_doc = rep / "architecture.md"
    write_architecture_rq_report(arch_doc, communities, inter_links, labels)

    return Phase4ExportResult(
        god_nodes_report=god_report,
        obsidian_god_nodes=obs_god,
        architecture_png=arch_png,
        architecture_mmd=arch_mmd,
        oop_png=oop_png,
        oop_mmd=oop_mmd,
        architecture_report=arch_doc,
    )
