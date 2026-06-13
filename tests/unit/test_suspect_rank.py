"""Unit tests for ``rank_suspects`` (FR-E1, Phase 9 T9.1)."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.services.agents.state import SuspectNode
from graphdebug.services.agents.suspect_rank import rank_suspects
from graphdebug.services.graphify.loader import load_graph


def _rank_graph(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "core",
                        "label": "core",
                        "file_type": "code",
                        "source_file": "proj/core.py",
                    },
                    {
                        "id": "leaf",
                        "label": "leaf",
                        "file_type": "code",
                        "source_file": "proj/leaf.py",
                    },
                    {
                        "id": "t",
                        "label": "test_core",
                        "file_type": "code",
                        "source_file": "proj/tests/test_core.py",
                    },
                ],
                "edges": [
                    {"source": "leaf", "target": "core", "relation": "imports"},
                    {"source": "t", "target": "core", "relation": "imports"},
                ],
            }
        ),
        encoding="utf-8",
    )


def test_rank_suspects_prefers_near_test_and_central(tmp_path: Path) -> None:
    gp = tmp_path / "graph.json"
    _rank_graph(gp)
    graph = load_graph(gp)
    ranked: list[SuspectNode] = rank_suspects(
        graph,
        failing_tests=("proj/tests/test_core.py::test_x",),
        source_prefixes=("proj/",),
        top_k=4,
    )
    assert ranked
    ids = [s.node_id for s in ranked]
    assert "core" in ids
    assert all(isinstance(s.score, float) for s in ranked)
    assert all(s.test_proximity >= 0.0 for s in ranked)
