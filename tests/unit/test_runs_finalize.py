"""Phase 6 run manifest + experiment-arm archive."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.services.ledger.schema import LedgerRecord
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.services.runs.finalize import finalize_investigation_run
from graphdebug.shared.config import BudgetProfile


def test_finalize_writes_manifest_and_arm_mirror(tmp_path: Path) -> None:
    run_dir = tmp_path / "results" / "run-abc"
    run_dir.mkdir(parents=True)
    ledger = run_dir / "ledger.jsonl"
    LedgerWriter(ledger).append(
        LedgerRecord(
            role="navigator",
            event="llm_completion",
            prompt_tokens=1,
            completion_tokens=2,
            total_tokens=3,
            latency_ms=0.0,
            tool_calls=0,
            files_read=0,
        )
    )
    profile = BudgetProfile(
        max_tokens=100,
        max_tool_calls=10,
        max_files=5,
        max_iterations=8,
    )
    final = {
        "oriented": True,
        "budget": {
            "max_tokens": 100,
            "tokens_used": 3,
            "tool_calls": 0,
            "files_read": 0,
            "max_tool_calls": 10,
            "max_files": 5,
            "max_iterations": 8,
        },
        "hypothesis": "bad default",
        "patch": {"unified_diff": "--- a/x\n+++ b/x\n", "rationale": ""},
        "iterations": 4,
    }
    mf, arm = finalize_investigation_run(
        project_root=tmp_path,
        run_dir=run_dir,
        bug_task={"target_root": "/t", "failing_tests": ["a::b"], "symptom": "boom"},
        mode="graph",
        profile=profile,
        final_state=final,
        halted_reason=None,
        ledger_path=ledger,
    )
    assert mf == run_dir / "manifest.json"
    data = json.loads(mf.read_text(encoding="utf-8"))
    assert data["experiment_arm"] == "graph"
    assert data["phase_tag"] == "phase6_investigation"
    assert data["ledger_aggregate"]["entries"] == 1
    assert data["iterations"] == 4
    assert (arm / "ledger.jsonl").is_file()
    assert (arm / "manifest.json").is_file()
    assert (tmp_path / "results" / "experiment_arms" / "graph" / "LATEST").read_text(
        encoding="utf-8"
    ).strip() == "run-abc"
