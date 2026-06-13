"""LangGraph ``AgentState`` TypedDict and nested row types (plan §6.1)."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, NotRequired, TypedDict

Mode = Literal["naive", "graph"]


class SuspectNodeTD(TypedDict):
    node_id: str
    score: float
    why: str
    betweenness: float
    test_proximity: float


class PatchTD(TypedDict, total=False):
    unified_diff: str
    rationale: str


class StepRecordTD(TypedDict):
    role: str
    action: str
    detail: str


class BudgetStateTD(TypedDict):
    max_tokens: int
    max_tool_calls: int
    max_files: int
    max_iterations: int
    tokens_used: int
    tool_calls: int
    files_read: int


class AgentState(TypedDict, total=False):
    bug_task: dict[str, Any]
    mode: Mode
    run_id: str
    oriented: bool
    suspects: list[SuspectNodeTD]
    suspects_ranked: bool
    fetched_code: dict[str, str]
    code_fetched: bool
    hypothesis: str
    patch: PatchTD | None
    patch_ready: bool
    verified: bool
    verification_attempted: bool
    scribed: bool
    iterations: int
    budget: BudgetStateTD
    halted_reason: str
    hitl_ack: NotRequired[bool]
    naive_file_suspects: NotRequired[list[str]]
    log: Annotated[list[StepRecordTD], operator.add]
    pytest_stdout: str
    pytest_stderr: str
    pytest_returncode: int


__all__ = [
    "AgentState",
    "BudgetStateTD",
    "Mode",
    "PatchTD",
    "StepRecordTD",
    "SuspectNodeTD",
]
