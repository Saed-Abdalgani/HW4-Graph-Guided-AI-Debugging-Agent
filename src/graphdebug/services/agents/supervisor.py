"""Supervisor routing: ``Command(goto=...)`` from state flags (T5.11)."""

from __future__ import annotations

from langgraph.graph import END
from langgraph.types import Command

from graphdebug.services.agents.state import AgentState


def supervisor_route(
    state: AgentState,
    *,
    hitl_required: bool,
) -> Command:
    """Deterministic hand-off chain (FR-A1, FR-A6)."""
    if state.get("halted_reason"):
        return Command(goto=END)
    if state.get("scribed"):
        return Command(goto=END)

    budget = state["budget"]
    if int(state.get("iterations", 0)) >= int(budget["max_iterations"]):
        return Command(goto=END, update={"halted_reason": "max_iterations_exceeded"})

    if not state.get("oriented"):
        return Command(goto="navigator")
    if not state.get("suspects_ranked"):
        return Command(goto="investigator")
    if not state.get("code_fetched"):
        return Command(goto="retriever")
    if not state.get("patch_ready"):
        return Command(goto="fixer")
    if hitl_required and not state.get("hitl_ack"):
        return Command(goto="hitl")
    if not state.get("verification_attempted"):
        return Command(goto="verifier")
    if not state.get("scribed"):
        return Command(goto="scribe")
    return Command(goto=END)


__all__ = ["supervisor_route"]
