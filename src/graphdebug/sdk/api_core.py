"""Core SDK facade (investigate, vault, graph) — see ``api`` for Phase 7 exports."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage

from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.agents.runner import run_investigation
from graphdebug.services.agents.state import BugTask, Mode
from graphdebug.services.agents.suspect_rank import rank_suspects
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
)
from graphdebug.services.vault import (
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
    """Load graph.json from config paths, build vault, optional before-snapshot."""
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
    """Centrality, god-node reports, architecture + OOP assets."""
    return export_phase4(config, graph_path=graph_path)


def update_hot(path: str | Path, sections: dict[str, str]) -> str:
    """Merge sections into ``hot.md`` (``HOT_SECTION_KEYS``)."""
    return write_hot_sections(Path(path), sections)


def investigate(
    bug_task: BugTask,
    mode: Mode,
    *,
    project_root: Path | None = None,
    require_api_key: bool = True,
    assume_hitl_ack: bool = False,
    verify_fn: Callable[..., dict[str, Any]] | None = None,
    llm_invoker: Callable[..., AIMessage] | None = None,
) -> InvestigationResult:
    """LangGraph investigation (Phase 5). Use ``assume_hitl_ack`` only for automation."""
    root = (project_root or Path.cwd()).resolve()
    need_key = require_api_key if llm_invoker is None else False
    cfg = load_config(project_root=root, require_api_key=need_key)
    return run_investigation(
        bug_task,
        mode,
        cfg,
        verify_fn=verify_fn,
        llm_invoker=llm_invoker,
        assume_hitl_ack=assume_hitl_ack,
    )


__all__ = [
    "AppConfig",
    "BugTask",
    "CentralityRow",
    "CodeGraph",
    "ConfigError",
    "GodNode",
    "GraphEdge",
    "GraphLoadError",
    "GraphNode",
    "GraphQueryError",
    "GraphSanity",
    "InvestigationResult",
    "Mode",
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
    "investigate",
    "load_code_graph",
    "load_config",
    "neighbors",
    "parse_hot",
    "path_between_nodes",
    "rank_suspects",
    "render_hot",
    "traverse_hops",
    "update_hot",
]
