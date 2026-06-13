"""Execute one investigation run (Phase 5 orchestration)."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage

from graphdebug.services.agents.deps import InvestigationDeps
from graphdebug.services.agents.graph_app import build_investigation_graph
from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.agents.state import AgentState, BugTask, Mode, initial_budget_row
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared.config import AppConfig, BudgetProfile
from graphdebug.shared.gatekeeper import Gatekeeper, build_chat_model


def _initial_state(
    bug_task: BugTask,
    mode: Mode,
    run_id: str,
    profile: BudgetProfile,
) -> dict[str, Any]:
    budget = initial_budget_row(profile)
    return {
        "bug_task": bug_task.to_dict(),
        "mode": mode,
        "run_id": run_id,
        "oriented": False,
        "suspects_ranked": False,
        "suspects": [],
        "code_fetched": False,
        "fetched_code": {},
        "patch_ready": False,
        "patch": None,
        "verified": False,
        "verification_attempted": False,
        "scribed": False,
        "iterations": 0,
        "budget": budget,
        "log": [],
        "pytest_stdout": "",
        "pytest_stderr": "",
        "pytest_returncode": -1,
    }


def run_investigation(
    bug_task: BugTask,
    mode: Mode,
    config: AppConfig,
    *,
    verify_fn: Callable[[AgentState], dict] | None = None,
    llm_invoker: Callable[[str, Any], AIMessage] | None = None,
    assume_hitl_ack: bool = False,
) -> InvestigationResult:
    """Compile and invoke the workflow once (T5.14 core)."""
    run_id = str(uuid.uuid4())
    run_dir = config.paths["results"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = run_dir / "ledger.jsonl"
    ledger = LedgerWriter(ledger_path)
    profile = config.budgets[mode]
    state0 = _initial_state(bug_task, mode, run_id, profile)
    if assume_hitl_ack:
        state0["hitl_ack"] = True
    budget_ref = state0["budget"]

    chat = None if llm_invoker is not None else build_chat_model(config)
    gk = Gatekeeper(
        app_config=config,
        budget=budget_ref,
        ledger=ledger,
        chat_model=chat,
        invoker=llm_invoker,
    )
    deps = InvestigationDeps(config=config, gatekeeper=gk, ledger=ledger, verify_fn=verify_fn)
    graph = build_investigation_graph(deps)
    cfg = {"configurable": {"thread_id": run_id}}
    final = graph.invoke(state0, config=cfg)
    halted = final.get("halted_reason")
    return InvestigationResult(
        run_id=run_id,
        mode=mode,
        ledger_path=ledger_path,
        final_state=dict(final),
        halted_reason=str(halted) if halted else None,
    )


__all__ = ["run_investigation"]
