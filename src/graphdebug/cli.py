"""Thin CLI entrypoint — delegates to the SDK (G.3)."""

from __future__ import annotations

import argparse
from pathlib import Path

from graphdebug.cli_handlers import (
    print_graphify_summary,
    run_phase4_export,
    run_vault_build,
    run_vault_snapshot,
    version_string,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="graphdebug",
        description="Graph-guided AI debugging agent (HW4).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version_string(),
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
    phase4 = subparsers.add_parser(
        "phase4-export",
        help="Centrality, god-node reports, architecture + OOP diagrams (Phase 4).",
    )
    phase4.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repo root (default: current working directory).",
    )
    phase4.add_argument(
        "--graph",
        type=Path,
        default=None,
        help="Override path to graph.json.",
    )
    args = parser.parse_args()
    if args.command == "graphify-load":
        print_graphify_summary(args.graph_path)
    elif args.command == "vault-build":
        run_vault_build(args)
    elif args.command == "vault-snapshot":
        run_vault_snapshot(args)
    elif args.command == "phase4-export":
        run_phase4_export(args)


if __name__ == "__main__":
    main()  # pragma: no cover
