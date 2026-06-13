"""Shared synthetic project layout for investigation integration tests."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from graphdebug.services.agents.state import BugTask
from graphdebug.services.vault.hot import render_hot


def write_minimal_investigation_project(root: Path) -> BugTask:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "default.yaml").write_text(
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
        + "\n",
        encoding="utf-8",
    )
    art = root / "artifacts" / "graphify"
    art.mkdir(parents=True, exist_ok=True)
    (art / "GRAPH_REPORT.md").write_text("# synthetic graph report\n", encoding="utf-8")
    graph = {
        "nodes": [
            {
                "id": "n_foo",
                "label": "foo.py",
                "file_type": "code",
                "source_file": "pkg/foo.py",
                "source_location": "L5",
            },
            {
                "id": "n_test",
                "label": "test_x.py",
                "file_type": "code",
                "source_file": "tests/test_x.py",
                "source_location": "L2",
            },
        ],
        "edges": [{"source": "n_test", "target": "n_foo", "relation": "imports"}],
    }
    (art / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
    vault = root / "obsidian"
    vault.mkdir(parents=True, exist_ok=True)
    (vault / "index.md").write_text("# index\n[[hot]]\n", encoding="utf-8")
    (vault / "hot.md").write_text(render_hot({"symptom": "synthetic"}), encoding="utf-8")
    subj = root / "subject"
    (subj / "pkg").mkdir(parents=True, exist_ok=True)
    (subj / "tests").mkdir(parents=True, exist_ok=True)
    (subj / "pkg" / "foo.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
    (subj / "tests" / "test_x.py").write_text(
        "def test_demo():\n    assert True\n",
        encoding="utf-8",
    )
    (root / "results").mkdir(parents=True, exist_ok=True)
    return BugTask(
        target_root=str(subj.resolve()),
        failing_tests=("tests/test_x.py::test_demo",),
        symptom="AssertionError on foo",
    )
