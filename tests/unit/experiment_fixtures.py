"""Shared manifest fixtures for Phase 8 experiment tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def manifest_row(
    mode: str,
    run_id: str,
    *,
    total_tokens: int,
    files_read: int,
    iterations: int,
) -> dict:
    half = total_tokens // 2
    return {
        "experiment_arm": mode,
        "run_id": run_id,
        "ledger_aggregate": {
            "entries": 3,
            "total_prompt_tokens": half,
            "total_completion_tokens": total_tokens - half,
            "total_tokens": total_tokens,
            "total_tool_calls": 1,
            "total_files_read": files_read,
        },
        "deliverables": {
            "root_cause_hypothesis": True,
            "candidate_patch": True,
        },
        "flags": {"verified": False},
        "iterations": iterations,
        "budget_final": {"files_read": files_read},
    }


def write_minimal_project_config(root: Path) -> None:
    cfg_dir = root / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location(
        "_graphdebug_test_cfg",
        Path(__file__).resolve().parent / "test_config.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    (cfg_dir / "default.yaml").write_text(mod._MINIMAL_YAML + "\n", encoding="utf-8")
    (root / "assets").mkdir(parents=True, exist_ok=True)
    (root / "rep").mkdir(parents=True, exist_ok=True)
    (root / "r").mkdir(parents=True, exist_ok=True)


__all__ = ["manifest_row", "write_minimal_project_config"]
