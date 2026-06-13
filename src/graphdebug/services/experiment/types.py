"""Typed rows for naive vs graph token experiment (Phase 8)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from graphdebug.services.agents.result import InvestigationResult


@dataclass(frozen=True, slots=True)
class ArmMetrics:
    """Per-arm numbers from ``manifest.json`` + wall time (measured in harness)."""

    mode: str
    run_id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    tool_calls: int
    files_read: int
    iterations: int
    wall_seconds: float
    has_hypothesis: bool
    has_patch: bool
    verified: bool


@dataclass(frozen=True, slots=True)
class KPIResult:
    """``prd.md`` §6 style checks; honest when naive spend is zero."""

    token_savings_pct: float | None
    file_savings_pct: float | None
    iteration_ok: bool
    meets_token_kpi: bool
    meets_file_kpi: bool
    meets_iteration_kpi: bool
    notes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TokenExperimentResult:
    naive: InvestigationResult
    graph: InvestigationResult
    naive_metrics: ArmMetrics
    graph_metrics: ArmMetrics
    kpis: KPIResult
    report_path: Path
    chart_path: Path
    naive_cost_usd: float
    graph_cost_usd: float


__all__ = ["ArmMetrics", "KPIResult", "TokenExperimentResult"]
