"""Phase-5 worker / HITL / verifier coverage."""

from __future__ import annotations

from pathlib import Path

import pytest

from graphdebug.services.agents.hitl import hitl_node
from graphdebug.services.agents.state import BudgetStateTD, initial_budget_row
from graphdebug.services.agents.workers.investigator import run_investigator
from graphdebug.services.agents.workers.navigator import run_navigator
from graphdebug.services.agents.workers.retriever import run_retriever
from graphdebug.services.agents.workers.verifier import default_verify
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared._rate_limit import RefillBucket
from graphdebug.shared.config import BudgetProfile, RetrieverConfig


def _budget() -> BudgetStateTD:
    return initial_budget_row(
        BudgetProfile(
            max_tokens=100_000,
            max_tool_calls=50,
            max_files=20,
            max_iterations=30,
        )
    )


def test_refill_bucket_consumes() -> None:
    b = RefillBucket(capacity=10.0, refill_per_second=50.0)
    b.consume(3.0)
    b.consume(2.0)


def test_hitl_skipped_when_disabled() -> None:
    st = {
        "bug_task": {"target_root": ".", "failing_tests": [], "symptom": ""},
        "mode": "graph",
        "run_id": "r",
        "budget": _budget(),
        "patch_ready": True,
        "patch": {"unified_diff": "", "rationale": ""},
    }
    out = hitl_node(st, enabled=False)
    assert out["hitl_ack"] is True


def test_navigator_naive_mode(tmp_path: Path) -> None:
    st = {
        "bug_task": {"target_root": ".", "failing_tests": [], "symptom": "x"},
        "mode": "naive",
        "run_id": "r",
        "budget": _budget(),
        "iterations": 0,
    }
    out = run_navigator(st, vault=tmp_path, graph_report=tmp_path / "g.md")
    assert out["oriented"] is True


def test_investigator_and_retriever_naive(tmp_path: Path) -> None:
    subj = tmp_path / "s"
    (subj / "a").mkdir(parents=True)
    (subj / "a" / "x.py").write_text("x=1\n", encoding="utf-8")
    st = {
        "bug_task": {"target_root": str(subj), "failing_tests": ["t"], "symptom": "s"},
        "mode": "naive",
        "budget": _budget(),
        "iterations": 0,
        "suspects": [],
    }
    inv = run_investigator(
        dict(st),
        graph_json=tmp_path / "missing.json",
        source_prefixes=(),
    )
    assert inv["suspects_ranked"] is True
    st2 = {**st, **inv, "code_fetched": False}
    led = LedgerWriter(tmp_path / "l.jsonl")
    ret = run_retriever(
        dict(st2),
        graph_json=tmp_path / "missing.json",
        ledger=led,
        retriever_cfg=RetrieverConfig(max_lines_per_file=5, max_suspects_fetched=2),
    )
    assert ret["code_fetched"] is True


def test_default_verify_subprocess(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    subj = tmp_path / "sub"
    subj.mkdir()
    (subj / "t.py").write_text("def test_a():\n    pass\n", encoding="utf-8")

    class Proc:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(*_args, **_kwargs):
        return Proc()

    monkeypatch.setattr(
        "graphdebug.services.agents.workers.verifier.subprocess.run",
        fake_run,
    )
    st = {
        "bug_task": {"target_root": str(subj), "failing_tests": ["t.py::test_a"], "symptom": ""},
        "mode": "graph",
        "run_id": "r",
        "budget": _budget(),
        "iterations": 0,
    }
    out = default_verify(st)
    assert out["verified"] is True
    assert out["verification_attempted"] is True
