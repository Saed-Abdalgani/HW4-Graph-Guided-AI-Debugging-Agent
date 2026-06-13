"""Public re-exports: graph state + task types + budget row factory (plan §6.1)."""

from __future__ import annotations

from graphdebug.services.agents.state_typed import (
    AgentState,
    BudgetStateTD,
    Mode,
    PatchTD,
    StepRecordTD,
    SuspectNodeTD,
)
from graphdebug.services.agents.task_types import (
    BugTask,
    Patch,
    StepRecord,
    SuspectNode,
    patch_from_td,
    patch_to_td,
    suspect_from_td,
    suspect_to_td,
)
from graphdebug.shared.config import BudgetProfile


def initial_budget_row(profile: BudgetProfile) -> BudgetStateTD:
    return BudgetStateTD(
        max_tokens=int(profile.max_tokens),
        max_tool_calls=int(profile.max_tool_calls),
        max_files=int(profile.max_files),
        max_iterations=int(profile.max_iterations),
        tokens_used=0,
        tool_calls=0,
        files_read=0,
    )


__all__ = [
    "AgentState",
    "BugTask",
    "BudgetStateTD",
    "Mode",
    "Patch",
    "PatchTD",
    "StepRecord",
    "StepRecordTD",
    "SuspectNode",
    "SuspectNodeTD",
    "initial_budget_row",
    "patch_from_td",
    "patch_to_td",
    "suspect_from_td",
    "suspect_to_td",
]
