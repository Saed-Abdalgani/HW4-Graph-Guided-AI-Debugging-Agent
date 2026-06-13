"""SDK entrypoints for Phase 8 token experiment (keeps ``api_core`` small)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage

from graphdebug.services.agents.state import BugTask
from graphdebug.services.experiment.runner import run_token_experiment as _run_experiment
from graphdebug.services.experiment.types import ArmMetrics, KPIResult, TokenExperimentResult
from graphdebug.shared.config import AppConfig, load_config


def run_token_experiment(
    bug_task: BugTask,
    *,
    project_root: Path | None = None,
    require_api_key: bool = True,
    assume_hitl_ack: bool = False,
    verify_fn: Callable[..., dict[str, Any]] | None = None,
    llm_invoker: Callable[..., AIMessage] | None = None,
    write_artifacts: bool = True,
) -> TokenExperimentResult:
    """Run **naive** then **graph** with one config load (same model/seed/temperature)."""
    root = (project_root or Path.cwd()).resolve()
    need_key = require_api_key if llm_invoker is None else False
    cfg: AppConfig = load_config(project_root=root, require_api_key=need_key)
    return _run_experiment(
        bug_task,
        cfg,
        verify_fn=verify_fn,
        llm_invoker=llm_invoker,
        assume_hitl_ack=assume_hitl_ack,
        write_artifacts=write_artifacts,
    )


__all__ = ["ArmMetrics", "KPIResult", "TokenExperimentResult", "run_token_experiment"]
