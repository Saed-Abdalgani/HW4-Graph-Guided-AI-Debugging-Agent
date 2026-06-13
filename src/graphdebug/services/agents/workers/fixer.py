"""Propose a minimal patch via the Gatekeeper (T5.8) — does not apply it."""

from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.agents.state import AgentState, Patch, StepRecordTD, patch_to_td
from graphdebug.shared.gatekeeper import Gatekeeper


def _extract_diff(text: str) -> str:
    fence = re.search(r"```(?:diff|patch)?\s*\n(.*?)```", text, re.S | re.I)
    if fence:
        return fence.group(1).strip()
    if text.strip().startswith("--- "):
        return text.strip()
    return text.strip()


def run_fixer(state: AgentState, *, gatekeeper: Gatekeeper) -> dict:
    if state.get("halted_reason"):
        return {}
    budget = state["budget"]
    it = int(state.get("iterations", 0))
    budget_mod.assert_can_iterate(budget, it, 1)
    bug = state["bug_task"]
    code = "\n\n".join(f"### {k}\n{v}" for k, v in (state.get("fetched_code") or {}).items())
    if not code.strip():
        code = "(no code slices — infer from symptom and test names only)"

    sys = (
        "You are a senior debugger. Write a short rationale (plain text). On its own line "
        "write: ROOT_CAUSE: <one sentence on the underlying defect, not the symptom>. Then "
        "output a minimal unified diff only inside a ```diff``` fence. Prefer the smallest "
        "correct change."
    )
    user = (
        f"Symptom:\n{bug.get('symptom','')}\n\n"
        f"Failing tests:\n{bug.get('failing_tests')}\n\n"
        f"Code slices:\n{code[:24000]}\n"
    )
    msg = gatekeeper.complete_chat(
        role="fixer",
        messages=[SystemMessage(content=sys), HumanMessage(content=user)],
    )
    raw = msg.content if isinstance(msg.content, str) else str(msg.content)
    diff = _extract_diff(raw)
    root_m = re.search(r"ROOT_CAUSE:\s*(.+)$", raw, re.I | re.M)
    if root_m:
        hypothesis = root_m.group(1).strip()
    else:
        fence = re.search(r"```", raw)
        head = raw[: fence.start()] if fence else raw
        hypothesis = " ".join(head.strip().split())[:800] or "See patch rationale / diff."
    patch = Patch(unified_diff=diff, rationale="LLM-proposed minimal fix.")
    log = [StepRecordTD(role="fixer", action="propose_patch", detail=diff[:2000])]
    return {
        "patch": patch_to_td(patch),
        "patch_ready": True,
        "hypothesis": hypothesis,
        "iterations": it + 1,
        "log": log,
    }


__all__ = ["run_fixer"]
