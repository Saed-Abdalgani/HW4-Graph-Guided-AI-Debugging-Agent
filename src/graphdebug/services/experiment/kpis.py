"""KPI math vs ``prd.md`` §6 (Phase 8, T8.6)."""

from __future__ import annotations

from graphdebug.services.experiment.types import ArmMetrics, KPIResult

_TOKEN_TARGET_PCT = 50.0
_FILE_TARGET_PCT = 50.0


def _savings_pct(naive_val: int, graph_val: int) -> float | None:
    if naive_val <= 0:
        return None
    return (1.0 - (graph_val / naive_val)) * 100.0


def evaluate_kpis(naive: ArmMetrics, graph: ArmMetrics) -> KPIResult:
    tok = _savings_pct(naive.total_tokens, graph.total_tokens)
    fil = _savings_pct(naive.files_read, graph.files_read)
    iter_ok = graph.iterations <= naive.iterations
    notes: list[str] = []
    if tok is None and naive.total_tokens == 0:
        notes.append("Naive arm recorded zero LLM tokens — cannot compute token savings.")
    if fil is None and naive.files_read == 0:
        notes.append("Naive arm read zero files — file savings undefined.")
    meets_t = tok is not None and tok >= _TOKEN_TARGET_PCT
    meets_f = fil is not None and fil >= _FILE_TARGET_PCT
    meets_i = iter_ok
    if not meets_t and tok is not None:
        notes.append(f"Token KPI (<{_TOKEN_TARGET_PCT}% vs naive): not met ({tok:.1f}% saved).")
    if not meets_f and fil is not None:
        notes.append(f"File KPI (<{_FILE_TARGET_PCT}% vs naive): not met ({fil:.1f}% saved).")
    if not meets_i:
        notes.append("Iteration KPI: graph arm used more iterations than naive.")
    return KPIResult(
        token_savings_pct=tok,
        file_savings_pct=fil,
        iteration_ok=iter_ok,
        meets_token_kpi=meets_t,
        meets_file_kpi=meets_f,
        meets_iteration_kpi=meets_i,
        notes=tuple(notes),
    )


def estimated_cost_usd(metrics: ArmMetrics, *, usd_pt: float, usd_ct: float) -> float:
    return (metrics.prompt_tokens / 1000.0) * usd_pt + (metrics.completion_tokens / 1000.0) * usd_ct


__all__ = ["evaluate_kpis", "estimated_cost_usd"]
