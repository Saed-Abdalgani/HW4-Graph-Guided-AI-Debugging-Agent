"""Phase-5 gatekeeper, CLI/SDK delegation, and graph_app guard."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.agents.state import BugTask, initial_budget_row
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared.config import AppConfig, BudgetProfile, RetrieverConfig
from graphdebug.shared.gatekeeper import Gatekeeper, TransientLLMError


def test_gatekeeper_retries_transient(tmp_path: Path) -> None:
    raw = {
        "llm": {"provider": "openai", "model": "x", "temperature": 0.0, "max_output_tokens": 64},
        "gatekeeper": {
            "requests_per_minute": 600,
            "tokens_per_minute": 900000,
            "max_retries": 3,
            "backoff_base_seconds": 0.01,
            "max_backoff_seconds": 0.05,
            "queue_size": 8,
        },
        "budgets": {
            "graph": {
                "max_tokens": 10000,
                "max_tool_calls": 20,
                "max_files": 10,
                "max_iterations": 10,
            },
            "naive": {
                "max_tokens": 10000,
                "max_tool_calls": 20,
                "max_files": 10,
                "max_iterations": 10,
            },
        },
        "paths": {
            "graphify_artifacts": "a",
            "obsidian_vault": "b",
            "results": "c",
            "data_root": "d",
            "reports": "e",
        },
        "features": {},
        "analysis": {},
        "retriever": {"max_lines_per_file": 10, "max_suspects_fetched": 2},
    }
    paths = {k: (tmp_path / v).resolve() for k, v in raw["paths"].items()}
    cfg = AppConfig(
        raw=raw,
        project_root=tmp_path,
        llm=dict(raw["llm"]),
        gatekeeper=dict(raw["gatekeeper"]),
        budgets={
            "graph": BudgetProfile(10000, 20, 10, 10),
            "naive": BudgetProfile(10000, 20, 10, 10),
        },
        paths=paths,
        features={},
        retriever=RetrieverConfig(10, 2),
        openai_api_key=None,
    )
    budget = initial_budget_row(cfg.budgets["graph"])
    ledger = LedgerWriter(tmp_path / "led.jsonl")
    n = {"c": 0}

    def invoker(_r, _m):
        n["c"] += 1
        if n["c"] < 2:
            raise TransientLLMError("retry me")
        return AIMessage(
            content="ok",
            response_metadata={
                "token_usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
            },
        )

    gk = Gatekeeper(app_config=cfg, budget=budget, ledger=ledger, invoker=invoker)
    msg = gk.complete_chat(
        role="fixer",
        messages=[SystemMessage(content="s"), HumanMessage(content="u")],
    )
    assert msg.content == "ok"
    assert n["c"] == 2


def test_run_investigate_cli_prints(capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_inv(*_a, **_k):
        return InvestigationResult(
            "rid",
            "graph",
            Path("ledger.jsonl"),
            {"verified": True, "scribed": True},
            None,
        )

    monkeypatch.setattr("graphdebug.sdk.api.investigate", fake_inv)
    from graphdebug.cli_handlers import run_investigate_cli

    args = argparse.Namespace(
        project_root=Path("."),
        target_root=Path("."),
        tests=["t::x"],
        symptom="s",
        mode="graph",
        assume_hitl_ack=False,
    )
    run_investigate_cli(args)
    out = capsys.readouterr().out
    assert "run_id=rid" in out


def test_sdk_investigate_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a, **_k):
        return InvestigationResult("1", "naive", Path("x"), {}, None)

    monkeypatch.setattr("graphdebug.sdk.api.run_investigation", fake_run)
    from graphdebug.sdk.api import investigate

    r = investigate(
        BugTask(".", ("t",), "s"),
        "naive",
        project_root=Path("."),
        require_api_key=False,
    )
    assert r.run_id == "1"


def test_graph_app_guard_budget() -> None:
    from graphdebug.services.agents.budget import BudgetExceeded
    from graphdebug.services.agents.graph_app import _guard

    def boom(_state):
        raise BudgetExceeded("nope")

    fn = _guard("x", boom)
    out = fn({})  # type: ignore[arg-type]
    assert "halted_reason" in out
    assert out["log"][0]["action"] == "budget_halt"
