"""Gatekeeper rate shape + ledger rows (T5.2)."""

from __future__ import annotations

from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from graphdebug.services.agents.state import initial_budget_row
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared.config import AppConfig, BudgetProfile, load_config
from graphdebug.shared.gatekeeper import Gatekeeper, redact_secrets


def _minimal_cfg(root: Path, *, seed: int | None = None) -> AppConfig:
    text = """
llm:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.0
  max_output_tokens: 256
gatekeeper:
  requests_per_minute: 600
  tokens_per_minute: 900000
  max_retries: 2
  backoff_base_seconds: 0.01
  max_backoff_seconds: 0.05
  queue_size: 8
budgets:
  graph:
    max_tokens: 50000
    max_tool_calls: 50
    max_files: 20
    max_iterations: 30
  naive:
    max_tokens: 50000
    max_tool_calls: 50
    max_files: 20
    max_iterations: 30
paths:
  graphify_artifacts: g
  obsidian_vault: o
  results: r
  data_root: d
  reports: rep
retriever:
  max_lines_per_file: 40
  max_suspects_fetched: 2
features:
  hitl_required: false
  enable_langsmith: false
analysis:
  source_prefixes: ["pkg/"]
"""
    if seed is not None:
        text = text.replace(
            "temperature: 0.0",
            f"temperature: 0.0\n  seed: {int(seed)}",
        )
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "default.yaml").write_text(text, encoding="utf-8")
    return load_config(project_root=root, require_api_key=False)


def test_redact_sk() -> None:
    s = "token sk-1234567890abcdef and Bearer abcdefghi"
    assert "sk-***REDACTED***" in redact_secrets(s)
    assert "***REDACTED***" in redact_secrets(s)


def test_gatekeeper_invoker_emits_ledger(tmp_path: Path) -> None:
    cfg = _minimal_cfg(tmp_path)
    budget = initial_budget_row(
        BudgetProfile(
            max_tokens=50000,
            max_tool_calls=10,
            max_files=5,
            max_iterations=10,
        )
    )
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = LedgerWriter(ledger_path)

    def invoker(_role: str, messages):  # noqa: ANN001
        assert messages
        return AIMessage(
            content="hi",
            response_metadata={
                "token_usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5}
            },
        )

    gk = Gatekeeper(app_config=cfg, budget=budget, ledger=ledger, invoker=invoker)
    msg = gk.complete_chat(
        role="fixer",
        messages=[SystemMessage(content="s"), HumanMessage(content="u")],
    )
    assert msg.content == "hi"
    lines = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert budget["tool_calls"] == 1
    assert budget["tokens_used"] == 5


def test_build_chat_model_forwards_seed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from graphdebug.shared import gatekeeper_support as gks

    captured: dict[str, object] = {}

    class _Fake:
        def __init__(self, **kw: object) -> None:
            captured.update(kw)

    monkeypatch.setattr(gks, "ChatOpenAI", _Fake)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-seed-test")
    cfg = _minimal_cfg(tmp_path, seed=91)
    gks.build_chat_model(cfg)
    assert captured.get("model_kwargs") == {"seed": 91}
