"""Thin CLI entrypoint — delegates to the SDK (G.3)."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="graphdebug",
        description="Graph-guided AI debugging agent (HW4).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=_version_string(),
    )
    subparsers = parser.add_subparsers(dest="command")
    graphify_load = subparsers.add_parser(
        "graphify-load",
        help="Load a Graphify graph.json artifact and print sanity counts.",
    )
    graphify_load.add_argument(
        "--in",
        dest="graph_path",
        required=True,
        type=Path,
        help="Path to artifacts/graphify/graph.json.",
    )
    vault_build = subparsers.add_parser(
        "vault-build",
        help="Build Obsidian vault pages from graph.json (Phase 3).",
    )
    vault_build.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repo root (default: current working directory).",
    )
    vault_build.add_argument(
        "--graph",
        type=Path,
        default=None,
        help="Override path to graph.json (default: config paths.graphify_artifacts/graph.json).",
    )
    vault_build.add_argument(
        "--snapshot",
        action="store_true",
        help="Also capture results/knowledge_snapshots/before/ (FR-O4).",
    )
    vault_snapshot = subparsers.add_parser(
        "vault-snapshot",
        help="Capture a before-fix knowledge snapshot of the vault.",
    )
    vault_snapshot.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repo root (default: current working directory).",
    )
    args = parser.parse_args()
    if args.command == "graphify-load":
        _print_graphify_summary(args.graph_path)
    elif args.command == "vault-build":
        _run_vault_build(args)
    elif args.command == "vault-snapshot":
        _run_vault_snapshot(args)


def _version_string() -> str:
    from graphdebug.sdk.api import get_version

    return get_version()


def _print_graphify_summary(path: Path) -> None:
    from graphdebug.sdk.api import graph_sanity, load_code_graph

    graph = load_code_graph(path)
    sanity = graph_sanity(graph)
    print(
        " ".join(
            (
                f"nodes={sanity.node_count}",
                f"edges={sanity.edge_count}",
                f"hyperedges={sanity.hyperedge_count}",
                f"dangling={len(sanity.dangling_edges)}",
                f"isolated={len(sanity.isolated_node_ids)}",
            )
        )
    )


def _run_vault_build(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import (
        build_project_vault,
        build_vault,
        capture_knowledge_snapshot,
        load_code_graph,
        load_config,
    )

    root = (args.project_root or Path.cwd()).resolve()
    config = load_config(project_root=root, require_api_key=False)
    if args.graph is not None:
        graph = load_code_graph(args.graph)
        result = build_vault(graph, config.paths["obsidian_vault"])
        if args.snapshot:
            capture_knowledge_snapshot(
                config.paths["obsidian_vault"],
                config.paths["results"],
            )
    else:
        result = build_project_vault(config, capture_snapshot=args.snapshot)
    print(
        "vault-build:",
        f"graph_pages={len(result.graph_pages)}",
        f"suspects={len(result.suspect_pages)}",
        f"findings={len(result.finding_pages)}",
        f"stubs={len(result.stubs)}",
        f"graph_report={'yes' if result.graph_report_copy else 'no'}",
    )


def _run_vault_snapshot(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import capture_knowledge_snapshot, load_config

    root = (args.project_root or Path.cwd()).resolve()
    config = load_config(project_root=root, require_api_key=False)
    dest = capture_knowledge_snapshot(config.paths["obsidian_vault"], config.paths["results"])
    print(f"vault-snapshot: wrote {dest}")


if __name__ == "__main__":
    main()  # pragma: no cover
