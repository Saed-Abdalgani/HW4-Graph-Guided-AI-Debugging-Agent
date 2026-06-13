"""Supervisor routing (T5.11)."""

from __future__ import annotations

from langgraph.graph import END

from graphdebug.services.agents.state import initial_budget_row
from graphdebug.services.agents.supervisor import supervisor_route
from graphdebug.shared.config import BudgetProfile


def _base() -> dict:
    b = initial_budget_row(
        BudgetProfile(
            max_tokens=10_000,
            max_tool_calls=50,
            max_files=20,
            max_iterations=50,
        )
    )
    return {
        "budget": b,
        "iterations": 0,
        "run_id": "x",
        "bug_task": {"target_root": ".", "failing_tests": [], "symptom": ""},
        "mode": "graph",
    }


def test_supervisor_chain() -> None:
    s = _base()
    assert supervisor_route(s, hitl_required=False).goto == "navigator"
    s["oriented"] = True
    assert supervisor_route(s, hitl_required=False).goto == "investigator"
    s["suspects_ranked"] = True
    assert supervisor_route(s, hitl_required=False).goto == "retriever"
    s["code_fetched"] = True
    assert supervisor_route(s, hitl_required=False).goto == "fixer"
    s["patch_ready"] = True
    assert supervisor_route(s, hitl_required=False).goto == "verifier"
    s["verification_attempted"] = True
    assert supervisor_route(s, hitl_required=False).goto == "scribe"
    s["scribed"] = True
    assert supervisor_route(s, hitl_required=False).goto == END


def test_supervisor_hitl_branch() -> None:
    s = _base()
    s.update(
        {
            "oriented": True,
            "suspects_ranked": True,
            "code_fetched": True,
            "patch_ready": True,
        }
    )
    cmd = supervisor_route(s, hitl_required=True)
    assert cmd.goto == "hitl"
    s["hitl_ack"] = True
    assert supervisor_route(s, hitl_required=True).goto == "verifier"
