"""KPI and cost helpers for the token experiment (Phase 8)."""

from __future__ import annotations

from graphdebug.services.experiment.kpis import estimated_cost_usd, evaluate_kpis
from graphdebug.services.experiment.types import ArmMetrics


def test_evaluate_kpis_detects_failures() -> None:
    naive = ArmMetrics(
        mode="naive",
        run_id="a",
        prompt_tokens=5000,
        completion_tokens=5000,
        total_tokens=10000,
        tool_calls=2,
        files_read=40,
        iterations=5,
        wall_seconds=10.0,
        has_hypothesis=True,
        has_patch=True,
        verified=False,
    )
    graph_win = ArmMetrics(
        mode="graph",
        run_id="b",
        prompt_tokens=1500,
        completion_tokens=1500,
        total_tokens=3000,
        tool_calls=1,
        files_read=8,
        iterations=4,
        wall_seconds=6.0,
        has_hypothesis=True,
        has_patch=True,
        verified=False,
    )
    k = evaluate_kpis(naive, graph_win)
    assert k.token_savings_pct is not None and k.token_savings_pct > 50
    assert k.file_savings_pct is not None and k.file_savings_pct > 50
    assert k.meets_iteration_kpi

    graph_bad_iter = ArmMetrics(
        mode="graph",
        run_id="c",
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2,
        tool_calls=0,
        files_read=1,
        iterations=99,
        wall_seconds=1.0,
        has_hypothesis=False,
        has_patch=False,
        verified=False,
    )
    k2 = evaluate_kpis(naive, graph_bad_iter)
    assert not k2.meets_iteration_kpi


def test_estimated_cost_usd() -> None:
    m = ArmMetrics(
        mode="graph",
        run_id="x",
        prompt_tokens=1000,
        completion_tokens=500,
        total_tokens=1500,
        tool_calls=0,
        files_read=0,
        iterations=0,
        wall_seconds=0.0,
        has_hypothesis=False,
        has_patch=False,
        verified=False,
    )
    c = estimated_cost_usd(m, usd_pt=0.001, usd_ct=0.002)
    assert abs(c - 0.002) < 1e-9
