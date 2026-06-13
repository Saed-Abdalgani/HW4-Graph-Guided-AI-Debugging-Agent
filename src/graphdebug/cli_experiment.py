"""CLI: Phase 8 naive + graph token experiment (``graphdebug experiment``)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from graphdebug.cli_bugargs import add_bug_task_arguments


def add_experiment_parser(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "experiment",
        help="Run naive then graph investigation; write token report + chart (Phase 8).",
    )
    add_bug_task_arguments(p)


def run_experiment_cli(args: argparse.Namespace) -> None:
    from graphdebug.sdk.api import BugTask, run_token_experiment

    root = (args.project_root or Path.cwd()).resolve()
    bug = BugTask(
        target_root=str(args.target_root.resolve()),
        failing_tests=tuple(args.tests),
        symptom=str(args.symptom),
    )
    res = run_token_experiment(
        bug,
        project_root=root,
        assume_hitl_ack=bool(args.assume_hitl_ack),
    )
    ok = (
        res.kpis.meets_token_kpi
        and res.kpis.meets_file_kpi
        and res.kpis.meets_iteration_kpi
    )
    print(
        "experiment:",
        f"naive_run={res.naive.run_id}",
        f"graph_run={res.graph.run_id}",
        f"report={res.report_path}",
        f"chart={res.chart_path}",
        f"token_savings_pct={res.kpis.token_savings_pct!r}",
        f"kpis_met={ok}",
    )


__all__ = ["add_experiment_parser", "run_experiment_cli"]
