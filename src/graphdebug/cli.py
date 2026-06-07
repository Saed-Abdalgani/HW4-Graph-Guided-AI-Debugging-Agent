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
    args = parser.parse_args()
    if args.command == "graphify-load":
        _print_graphify_summary(args.graph_path)


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


if __name__ == "__main__":
    main()  # pragma: no cover
