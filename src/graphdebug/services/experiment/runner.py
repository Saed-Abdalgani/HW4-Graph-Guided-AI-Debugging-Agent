"""Run naive + graph investigations and emit comparison artifacts (Phase 8, T8.1)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage

from graphdebug.services.agents.runner import run_investigation
from graphdebug.services.agents.state import BugTask
from graphdebug.services.experiment.chart import write_token_comparison_chart
from graphdebug.services.experiment.kpis import estimated_cost_usd, evaluate_kpis
from graphdebug.services.experiment.metrics import metrics_from_result
from graphdebug.services.experiment.report_md import write_token_comparison_markdown
from graphdebug.services.experiment.types import TokenExperimentResult
from graphdebug.shared.config import AppConfig


def _pricing(cfg: AppConfig) -> tuple[float, float]:
    ex = cfg.raw.get("experiment") or {}
    return (
        float(ex.get("usd_per_1k_prompt_tokens", 0.0)),
        float(ex.get("usd_per_1k_completion_tokens", 0.0)),
    )


def _seed_repr(cfg: AppConfig) -> str:
    s = cfg.llm.get("seed")
    return str(s) if s is not None else "(none)"


def run_token_experiment(
    bug_task: BugTask,
    config: AppConfig,
    *,
    verify_fn: Callable[..., dict[str, Any]] | None = None,
    llm_invoker: Callable[..., AIMessage] | None = None,
    assume_hitl_ack: bool = False,
    write_artifacts: bool = True,
) -> TokenExperimentResult:
    """Execute **naive** then **graph** with the same task and LLM settings (T8.1)."""
    usd_pt, usd_ct = _pricing(config)
    t0 = time.perf_counter()
    naive = run_investigation(
        bug_task,
        "naive",
        config,
        verify_fn=verify_fn,
        llm_invoker=llm_invoker,
        assume_hitl_ack=assume_hitl_ack,
    )
    naive_wall = time.perf_counter() - t0
    t1 = time.perf_counter()
    graph = run_investigation(
        bug_task,
        "graph",
        config,
        verify_fn=verify_fn,
        llm_invoker=llm_invoker,
        assume_hitl_ack=assume_hitl_ack,
    )
    graph_wall = time.perf_counter() - t1
    mn = metrics_from_result(naive, wall_seconds=naive_wall)
    mg = metrics_from_result(graph, wall_seconds=graph_wall)
    kpis = evaluate_kpis(mn, mg)
    report_path = config.paths["reports"] / "token_comparison.md"
    chart_path = config.project_root / "assets" / "token_chart.png"
    n_cost = estimated_cost_usd(mn, usd_pt=usd_pt, usd_ct=usd_ct)
    g_cost = estimated_cost_usd(mg, usd_pt=usd_pt, usd_ct=usd_ct)
    if write_artifacts:
        write_token_comparison_markdown(
            report_path,
            naive=mn,
            graph=mg,
            kpis=kpis,
            naive_cost_usd=n_cost,
            graph_cost_usd=g_cost,
            model_name=str(config.llm.get("model", "")),
            temperature=float(config.llm.get("temperature", 0.0)),
            seed_repr=_seed_repr(config),
        )
        write_token_comparison_chart(mn, mg, chart_path)
    return TokenExperimentResult(
        naive=naive,
        graph=graph,
        naive_metrics=mn,
        graph_metrics=mg,
        kpis=kpis,
        report_path=report_path,
        chart_path=chart_path,
        naive_cost_usd=n_cost,
        graph_cost_usd=g_cost,
    )


__all__ = ["run_token_experiment"]
