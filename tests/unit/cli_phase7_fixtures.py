"""Minimal project + argparse helpers for phase7 CLI tests."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

_MIN_YAML = (
    textwrap.dedent(
        """
        llm:
          provider: openai
          model: gpt-4o-mini
          temperature: 0.0
          max_output_tokens: 256
        gatekeeper:
          requests_per_minute: 600
          tokens_per_minute: 900000
          max_retries: 1
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
          graphify_artifacts: artifacts/graphify
          obsidian_vault: obsidian
          results: results
          data_root: data
          reports: reports
        retriever:
          max_lines_per_file: 40
          max_suspects_fetched: 3
        features:
          hitl_required: false
          enable_langsmith: false
        analysis:
          source_prefixes: ["pkg/"]
        """
    ).strip()
    + "\n"
)


def write_minimal_phase7_project(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config" / "default.yaml").write_text(_MIN_YAML, encoding="utf-8")
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / "results").mkdir(parents=True, exist_ok=True)
    (tmp_path / "obsidian").mkdir(parents=True, exist_ok=True)


def phase7_namespace(**kwargs: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "project_root": None,
        "diff": None,
        "target_root": None,
        "tests": None,
        "baseline_red": None,
        "suite_args": None,
        "ours": None,
        "official": None,
        "hypothesis_file": None,
        "fix_file": None,
        "verification_file": None,
        "hypothesis_inline": "",
        "fix_inline": "",
        "verification_inline": "",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)
