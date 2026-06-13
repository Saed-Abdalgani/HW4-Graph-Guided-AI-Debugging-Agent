"""Human-in-the-loop gate before destructive steps (T5.13)."""

from __future__ import annotations

from langgraph.types import interrupt

from graphdebug.services.agents.state import AgentState, StepRecordTD


def hitl_node(state: AgentState, *, enabled: bool) -> dict:
    if state.get("halted_reason"):
        return {}
    if not enabled:
        return {
            "hitl_ack": True,
            "log": [
                StepRecordTD(role="hitl", action="skipped", detail="disabled"),
            ],
        }
    if state.get("hitl_ack"):
        return {}
    resume = interrupt(
        {
            "prompt": "Approve continuing. The workflow never auto-applies patches under data/.",
            "patch": state.get("patch"),
        }
    )
    ok = resume is True or (isinstance(resume, dict) and resume.get("approve") is True)
    return {
        "hitl_ack": bool(ok),
        "log": [StepRecordTD(role="hitl", action="ack", detail=str(ok))],
    }


__all__ = ["hitl_node"]
