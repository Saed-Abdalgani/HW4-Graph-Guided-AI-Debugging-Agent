"""Build Obsidian vault pages from a ``CodeGraph`` (FR-O3)."""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from graphdebug.services.graphify.models import CodeGraph

from ._graph_pages import render_graph_node_page
from ._paths import DEFAULT_FOCUS_NODE_IDS, GENERATED_DIR
from ._seed_pages import write_finding_pages, write_stub_nav_pages, write_suspect_pages


@dataclass(frozen=True, slots=True)
class VaultBuildResult:
    vault_root: Path
    graph_pages: tuple[Path, ...]
    suspect_pages: tuple[Path, ...]
    finding_pages: tuple[Path, ...]
    stubs: tuple[Path, ...]
    graph_report_copy: Path | None


def build_vault(
    graph: CodeGraph,
    vault_root: Path,
    *,
    focus_node_ids: Sequence[str] | None = None,
    copy_graph_report: bool = True,
) -> VaultBuildResult:
    """
    Write graph-backed pages under ``vault_root/generated/`` plus seed suspect/finding pages.

    *focus_node_ids* default pulls the PySnooper bug-1 working set from ``todo.md`` / ``hot.md``.
    """
    vault_root = vault_root.resolve()
    vault_root.mkdir(parents=True, exist_ok=True)
    gen = vault_root / GENERATED_DIR
    gen.mkdir(parents=True, exist_ok=True)

    seeds = tuple(focus_node_ids) if focus_node_ids is not None else DEFAULT_FOCUS_NODE_IDS
    graph_paths: list[Path] = []
    for node_id in seeds:
        node = graph.nodes.get(node_id)
        if node is None:
            continue
        out = gen / f"{node_id}.md"
        out.write_text(render_graph_node_page(graph, node), encoding="utf-8")
        graph_paths.append(out)

    suspect_paths = list(write_suspect_pages(vault_root, seeds))
    finding_paths = list(write_finding_pages(vault_root))
    stubs = list(write_stub_nav_pages(vault_root))

    report_copy: Path | None = None
    if copy_graph_report:
        src = Path(graph.path).resolve().parent / "GRAPH_REPORT.md"
        if src.is_file():
            report_copy = vault_root / "GRAPH_REPORT.md"
            shutil.copy2(src, report_copy)

    return VaultBuildResult(
        vault_root=vault_root,
        graph_pages=tuple(graph_paths),
        suspect_pages=tuple(suspect_paths),
        finding_pages=tuple(finding_paths),
        stubs=tuple(stubs),
        graph_report_copy=report_copy,
    )


__all__ = ["DEFAULT_FOCUS_NODE_IDS", "VaultBuildResult", "build_vault"]
