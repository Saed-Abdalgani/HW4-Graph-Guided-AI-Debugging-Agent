"""Persist investigation narrative to vault + run log (T5.10)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.agents.state import AgentState, StepRecordTD, patch_from_td
from graphdebug.services.vault.hot import update_hot


def _slug(node_id: str) -> str:
    return node_id.replace("/", "_").replace(":", "_")[:120]


def run_scribe(state: AgentState, *, vault: Path, run_dir: Path) -> dict:
    if state.get("halted_reason"):
        return {}
    budget = state["budget"]
    it = int(state.get("iterations", 0))
    budget_mod.assert_can_iterate(budget, it, 1)

    suspects = state.get("suspects") or []
    ranked = "\n".join(
        f"- [[suspects/{_slug(s['node_id'])}]] — {s['why'][:200]}"
        for s in suspects[:8]
    )
    patch = patch_from_td(state.get("patch"))
    fix_body = patch.unified_diff[:8000] if patch else "(none)"
    hypo = state.get("hypothesis", "")
    hot_updates = {
        "suspects": ranked or "(none)",
        "root_cause": hypo[:4000],
        "fix": fix_body,
        "next_action": "Await HITL to apply patch to subject, then re-run verifier.",
    }
    update_hot(vault / "hot.md", hot_updates)

    log_path = run_dir / "run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=UTC).isoformat()
    lines = [f"[{stamp}] scribe: updated hot.md; verified={state.get('verified')}"]
    for rec in state.get("log") or []:
        detail = str(rec.get("detail", ""))[:500]
        lines.append(f"  - {rec.get('role')}: {rec.get('action')} — {detail}")
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    return {
        "scribed": True,
        "iterations": it + 1,
        "log": [StepRecordTD(role="scribe", action="persist", detail=str(log_path))],
    }


__all__ = ["run_scribe"]
