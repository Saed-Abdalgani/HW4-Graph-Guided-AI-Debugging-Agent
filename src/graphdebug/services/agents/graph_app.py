"""Compile the multi-agent LangGraph (T5.12)."""

from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph

from graphdebug.services.agents.budget import BudgetExceeded
from graphdebug.services.agents.deps import InvestigationDeps
from graphdebug.services.agents.hitl import hitl_node
from graphdebug.services.agents.state import AgentState, StepRecordTD
from graphdebug.services.agents.supervisor import supervisor_route
from graphdebug.services.agents.workers.fixer import run_fixer
from graphdebug.services.agents.workers.investigator import run_investigator
from graphdebug.services.agents.workers.navigator import run_navigator
from graphdebug.services.agents.workers.retriever import run_retriever
from graphdebug.services.agents.workers.scribe import run_scribe
from graphdebug.services.agents.workers.verifier import run_verifier


def _guard(worker: str, fn):  # type: ignore[no-untyped-def]
    def inner(state: AgentState) -> dict:
        try:
            return fn(state)
        except BudgetExceeded as exc:
            return {
                "halted_reason": str(exc),
                "log": [
                    StepRecordTD(
                        role=worker,
                        action="budget_halt",
                        detail=str(exc),
                    )
                ],
            }

    return inner


def build_investigation_graph(deps: InvestigationDeps):
    cfg = deps.config
    vault = cfg.paths["obsidian_vault"]
    graph_json = cfg.paths["graphify_artifacts"] / "graph.json"
    report = cfg.paths["graphify_artifacts"] / "GRAPH_REPORT.md"
    prefixes = tuple(cfg.raw.get("analysis", {}).get("source_prefixes", ()))
    hitl_req = bool(cfg.features.get("hitl_required", True))
    gk = deps.gatekeeper
    led = deps.ledger

    def sup(s: AgentState):
        return supervisor_route(s, hitl_required=hitl_req)

    g = StateGraph(AgentState)
    g.add_node("supervisor", sup)
    g.add_node(
        "navigator",
        _guard(
            "navigator",
            lambda s: run_navigator(s, vault=vault, graph_report=report),
        ),
    )
    g.add_node(
        "investigator",
        _guard(
            "investigator",
            lambda s: run_investigator(s, graph_json=graph_json, source_prefixes=prefixes),
        ),
    )
    g.add_node(
        "retriever",
        _guard(
            "retriever",
            lambda s: run_retriever(
                s,
                graph_json=graph_json,
                ledger=led,
                retriever_cfg=cfg.retriever,
            ),
        ),
    )
    g.add_node("fixer", _guard("fixer", lambda s: run_fixer(s, gatekeeper=gk)))
    g.add_node("hitl", lambda s: hitl_node(s, enabled=hitl_req))
    g.add_node("verifier", _guard("verifier", lambda s: run_verifier(s, verify_fn=deps.verify_fn)))
    g.add_node(
        "scribe",
        _guard(
            "scribe",
            lambda s: run_scribe(s, vault=vault, run_dir=cfg.paths["results"] / s["run_id"]),
        ),
    )

    for n in (
        "navigator",
        "investigator",
        "retriever",
        "fixer",
        "hitl",
        "verifier",
        "scribe",
    ):
        g.add_edge(n, "supervisor")
    g.add_edge(START, "supervisor")
    return g.compile(checkpointer=InMemorySaver())


__all__ = ["build_investigation_graph"]
