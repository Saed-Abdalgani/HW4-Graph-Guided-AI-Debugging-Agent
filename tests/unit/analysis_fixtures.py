"""Tiny graphs + minimal AppConfig for analysis unit tests."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.shared.config import AppConfig, BudgetProfile, RetrieverConfig


def write_tiny_hub_graph(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "hub",
                        "label": "hub",
                        "file_type": "code",
                        "source_file": "pysnooper/hub.py",
                    },
                    {"id": "a", "label": "a", "file_type": "code", "source_file": "pysnooper/a.py"},
                    {"id": "b", "label": "b", "file_type": "code", "source_file": "pysnooper/b.py"},
                    {"id": "c", "label": "c", "file_type": "code", "source_file": "pysnooper/c.py"},
                ],
                "edges": [
                    {"source": "a", "target": "hub", "relation": "imports"},
                    {"source": "b", "target": "hub", "relation": "imports"},
                    {"source": "hub", "target": "c", "relation": "calls"},
                ],
            }
        ),
        encoding="utf-8",
    )


def minimal_analysis_config(root: Path) -> AppConfig:
    raw = {
        "llm": {"provider": "openai", "model": "x", "temperature": 0.0, "max_output_tokens": 1},
        "gatekeeper": {
            "requests_per_minute": 1,
            "tokens_per_minute": 1,
            "max_retries": 0,
            "backoff_base_seconds": 0.1,
            "max_backoff_seconds": 0.2,
            "queue_size": 1,
        },
        "budgets": {
            "naive": {
                "max_tokens": 1,
                "max_tool_calls": 1,
                "max_files": 1,
                "max_iterations": 1,
            },
            "graph": {
                "max_tokens": 1,
                "max_tool_calls": 1,
                "max_files": 1,
                "max_iterations": 1,
            },
        },
        "paths": {
            "graphify_artifacts": "gart",
            "obsidian_vault": "ob",
            "results": "res",
            "data_root": "data",
            "reports": "rep",
        },
        "retriever": {"max_lines_per_file": 10, "max_suspects_fetched": 2},
        "features": {"hitl_required": True, "enable_langsmith": False},
        "analysis": {"source_prefixes": ["pysnooper/"]},
    }
    budgets = {
        "naive": BudgetProfile(1, 1, 1, 1),
        "graph": BudgetProfile(1, 1, 1, 1),
    }
    paths = {k: (root / v).resolve() for k, v in raw["paths"].items()}
    return AppConfig(
        raw=raw,
        project_root=root,
        llm=dict(raw["llm"]),
        gatekeeper=dict(raw["gatekeeper"]),
        budgets=budgets,
        paths=paths,
        features=dict(raw["features"]),
        retriever=RetrieverConfig(max_lines_per_file=10, max_suspects_fetched=2),
        openai_api_key=None,
    )
