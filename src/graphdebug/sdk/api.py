"""Public SDK facade (FR-S1). CLI and agents must call into this module."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from graphdebug.services.analysis import (
    CentralityRow,
    GodNode,
    Phase4ExportResult,
    export_phase4,
)
from graphdebug.services.graphify import (
    CodeGraph,
    GraphEdge,
    GraphLoadError,
    GraphNode,
    GraphQueryError,
    GraphSanity,
    edge_details,
    graph_sanity,
    load_graph,
    neighbors,
    path_between_nodes,
    traverse_hops,
)
from graphdebug.services.vault import (
    VaultBuildResult,
    build_vault,
    capture_knowledge_snapshot,
    parse_hot,
    render_hot,
    update_hot as write_hot_sections,
)
from graphdebug.shared.config import AppConfig, ConfigError, load_config
from graphdebug.shared.version import get_version

load_code_graph = load_graph


def build_project_vault(
    config: AppConfig,
    *,
    focus_node_ids: Sequence[str] | None = None,
    capture_snapshot: bool = False,
) -> VaultBuildResult:
    """Load ``graph.json`` from config paths, write vault pages, optionally snapshot."""
    graph_path = config.paths["graphify_artifacts"] / "graph.json"
    graph = load_graph(graph_path)
    result = build_vault(
        graph,
        config.paths["obsidian_vault"],
        focus_node_ids=focus_node_ids,
    )
    if capture_snapshot:
        capture_knowledge_snapshot(config.paths["obsidian_vault"], config.paths["results"])
    return result


def export_project_phase4(
    config: AppConfig,
    *,
    graph_path: Path | None = None,
) -> Phase4ExportResult:
    """Centrality, god-node markdown, and graph-derived architecture / OOP assets."""
    return export_phase4(config, graph_path=graph_path)


def update_hot(path: str | Path, sections: dict[str, str]) -> str:
    """Merge *sections* into ``hot.md``; keys match ``HOT_SECTION_KEYS``."""
    return write_hot_sections(Path(path), sections)


__all__ = [
    "AppConfig",
    "CentralityRow",
    "CodeGraph",
    "ConfigError",
    "GodNode",
    "GraphEdge",
    "GraphLoadError",
    "GraphNode",
    "GraphQueryError",
    "GraphSanity",
    "Phase4ExportResult",
    "VaultBuildResult",
    "build_project_vault",
    "build_vault",
    "capture_knowledge_snapshot",
    "edge_details",
    "export_phase4",
    "export_project_phase4",
    "get_version",
    "graph_sanity",
    "load_code_graph",
    "load_config",
    "neighbors",
    "parse_hot",
    "path_between_nodes",
    "render_hot",
    "traverse_hops",
    "update_hot",
]
