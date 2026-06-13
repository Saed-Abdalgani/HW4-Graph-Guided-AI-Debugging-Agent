"""Phase 6 run artifacts: manifest + experiment-arm archive (todo T6.1, T6.4)."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from graphdebug.services.agents.state import Mode
from graphdebug.services.ledger.aggregate import aggregate_ledger
from graphdebug.shared.config import BudgetProfile


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)


def _budget_caps(profile: BudgetProfile) -> dict[str, int]:
    return {
        "max_tokens": profile.max_tokens,
        "max_tool_calls": profile.max_tool_calls,
        "max_files": profile.max_files,
        "max_iterations": profile.max_iterations,
    }


def finalize_investigation_run(
    *,
    project_root: Path,
    run_dir: Path,
    bug_task: dict[str, Any],
    mode: Mode,
    profile: BudgetProfile,
    final_state: dict[str, Any],
    halted_reason: str | None,
    ledger_path: Path,
) -> tuple[Path, Path]:
    """Write ``manifest.json`` under *run_dir* and mirror ledger + log to *experiment_arms*."""
    run_dir.mkdir(parents=True, exist_ok=True)
    results_root = run_dir.parent
    arm_dir = results_root / "experiment_arms" / mode / run_dir.name
    arm_dir.mkdir(parents=True, exist_ok=True)

    agg = aggregate_ledger(ledger_path)
    budget = final_state.get("budget") or {}
    patch = final_state.get("patch") or {}
    hypo = str(final_state.get("hypothesis") or "").strip()
    diff = str(patch.get("unified_diff") or "").strip()

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_arm": mode,
        "phase_tag": "phase6_investigation",
        "completed_at": datetime.now(tz=UTC).isoformat(),
        "run_id": run_dir.name,
        "bug_task": {
            "target_root": str(bug_task.get("target_root", "")),
            "failing_tests": list(bug_task.get("failing_tests") or ()),
            "symptom": str(bug_task.get("symptom", ""))[:2000],
        },
        "halted_reason": halted_reason,
        "flags": {
            "oriented": bool(final_state.get("oriented")),
            "suspects_ranked": bool(final_state.get("suspects_ranked")),
            "code_fetched": bool(final_state.get("code_fetched")),
            "patch_ready": bool(final_state.get("patch_ready")),
            "verified": bool(final_state.get("verified")),
            "scribed": bool(final_state.get("scribed")),
        },
        "deliverables": {
            "root_cause_hypothesis": bool(hypo),
            "candidate_patch": bool(diff),
        },
        "iterations": int(final_state.get("iterations") or 0),
        "budget_final": dict(budget),
        "budget_caps": _budget_caps(profile),
        "ledger_path": _rel(ledger_path, project_root),
        "ledger_aggregate": {
            "entries": agg.entries,
            "total_prompt_tokens": agg.total_prompt_tokens,
            "total_completion_tokens": agg.total_completion_tokens,
            "total_tokens": agg.total_tokens,
            "total_tool_calls": agg.total_tool_calls,
            "total_files_read": agg.total_files_read,
            "roles": list(agg.roles),
        },
    }

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    shutil.copy2(ledger_path, arm_dir / "ledger.jsonl")
    shutil.copy2(manifest_path, arm_dir / "manifest.json")
    log_src = run_dir / "run.log"
    if log_src.is_file():
        shutil.copy2(log_src, arm_dir / "run.log")

    latest = results_root / "experiment_arms" / mode / "LATEST"
    latest.write_text(run_dir.name + "\n", encoding="utf-8")

    return manifest_path, arm_dir


__all__ = ["finalize_investigation_run"]
