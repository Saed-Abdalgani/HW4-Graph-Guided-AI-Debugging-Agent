"""Thin CLI entrypoint — delegates to the SDK (G.3)."""

from __future__ import annotations

import argparse
from pathlib import Path

from graphdebug.cli_handlers import (
    print_graphify_summary,
    run_investigate_cli,
    run_phase4_export,
    run_vault_build,
    run_vault_snapshot,
    version_string,
)
from graphdebug.cli_phase7 import add_phase7_parser, run_phase7_cli


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
    add_phase7_parser(subparsers)
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
    investigate = subparsers.add_parser(
        "investigate",
        help="Run the graph-guided or naive multi-agent investigation (Phase 5).",
    )
    investigate.add_argument(
        "--mode",
        choices=("graph", "naive"),
        required=True,
        help="graph = vault+graph context; naive = fair baseline without graph/vault.",
    )
    investigate.add_argument(
        "--target-root",
        type=Path,
        required=True,
        help="Path to the buggy project root (subject under data/).",
    )
    investigate.add_argument(
        "--test",
        action="append",
        dest="tests",
        metavar="NODEID",
        required=True,
        help="Pytest node id (repeatable), e.g. tests/test_x.py::test_one.",
    )
    investigate.add_argument(
        "--symptom",
        default="(see baseline logs)",
        help="Short symptom text for prompts.",
    )
    investigate.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="graphdebug repo root (default: cwd).",
    )
    investigate.add_argument(
        "--assume-hitl-ack",
        action="store_true",
        help="Ack the HITL interrupt automatically (non-interactive; use with care).",
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
    elif args.command == "investigate":
        run_investigate_cli(args)
    elif args.command == "phase7":
        run_phase7_cli(args)


if __name__ == "__main__":
    main()  # pragma: no cover
