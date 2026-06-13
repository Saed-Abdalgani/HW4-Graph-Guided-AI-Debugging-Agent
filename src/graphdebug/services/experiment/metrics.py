"""Load per-arm metrics from investigation ``manifest.json`` (Phase 8, T8.2)."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.experiment.types import ArmMetrics


def metrics_from_manifest(manifest_path: Path, *, wall_seconds: float) -> ArmMetrics:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    agg = data.get("ledger_aggregate") or {}
    budget = data.get("budget_final") or {}
    deliv = data.get("deliverables") or {}
    flags = data.get("flags") or {}
    files_ledger = int(agg.get("total_files_read", 0) or 0)
    files_budget = int(budget.get("files_read", 0) or 0)
    files_read = max(files_ledger, files_budget)
    return ArmMetrics(
        mode=str(data.get("experiment_arm", "")),
        run_id=str(data.get("run_id", "")),
        prompt_tokens=int(agg.get("total_prompt_tokens", 0) or 0),
        completion_tokens=int(agg.get("total_completion_tokens", 0) or 0),
        total_tokens=int(agg.get("total_tokens", 0) or 0),
        tool_calls=int(agg.get("total_tool_calls", 0) or 0),
        files_read=files_read,
        iterations=int(data.get("iterations", 0) or 0),
        wall_seconds=float(wall_seconds),
        has_hypothesis=bool(deliv.get("root_cause_hypothesis")),
        has_patch=bool(deliv.get("candidate_patch")),
        verified=bool(flags.get("verified")),
    )


def metrics_from_result(inv: InvestigationResult, *, wall_seconds: float) -> ArmMetrics:
    mp = inv.manifest_path
    if mp is None or not mp.is_file():
        raise FileNotFoundError(f"Missing manifest for run {inv.run_id}")
    return metrics_from_manifest(mp, wall_seconds=wall_seconds)


__all__ = ["metrics_from_manifest", "metrics_from_result"]
