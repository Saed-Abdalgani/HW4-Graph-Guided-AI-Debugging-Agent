"""CLI command implementations (keeps ``cli.py`` small)."""

from __future__ import annotations

import argparse
from pathlib import Path


def version_string() -> str:
    from graphdebug.sdk.api import get_version

    return get_version()


def print_graphify_summary(path: Path) -> None:
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


def run_vault_build(args: argparse.Namespace) -> None:
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


def run_vault_snapshot(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import capture_knowledge_snapshot, load_config

    root = (args.project_root or Path.cwd()).resolve()
    config = load_config(project_root=root, require_api_key=False)
    dest = capture_knowledge_snapshot(config.paths["obsidian_vault"], config.paths["results"])
    print(f"vault-snapshot: wrote {dest}")


def run_phase4_export(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import export_project_phase4, load_config

    root = (args.project_root or Path.cwd()).resolve()
    config = load_config(project_root=root, require_api_key=False)
    res = export_project_phase4(config, graph_path=args.graph)
    print(
        "phase4-export:",
        f"god_report={res.god_nodes_report}",
        f"arch_png={res.architecture_png}",
        f"oop_png={res.oop_png}",
    )


def run_investigate_cli(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import BugTask, investigate

    root = (args.project_root or Path.cwd()).resolve()
    bug = BugTask(
        target_root=str(args.target_root.resolve()),
        failing_tests=tuple(args.tests),
        symptom=str(args.symptom),
    )
    res = investigate(
        bug,
        args.mode,
        project_root=root,
        assume_hitl_ack=bool(args.assume_hitl_ack),
    )
    fs = res.final_state
    print(
        "investigate:",
        f"run_id={res.run_id}",
        f"mode={res.mode}",
        f"ledger={res.ledger_path}",
        f"manifest={res.manifest_path}",
        f"experiment_arm={res.experiment_arm_path}",
        f"halted={res.halted_reason!r}",
        f"verified={fs.get('verified')}",
        f"scribed={fs.get('scribed')}",
    )
