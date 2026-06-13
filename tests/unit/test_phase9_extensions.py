"""Phase 9 extension helpers (impact, diff→hot, doc signals, ego report)."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.sdk.api import (
    architecture_ego_report,
    doc_graph_signals,
    impact_of,
    merge_git_diff_into_hot,
    node_ids_for_paths,
    paths_from_diff,
)
from graphdebug.services.graphify.loader import load_graph
from graphdebug.services.vault.hot import render_hot


def _graph(tmp_path: Path) -> Path:
    p = tmp_path / "g.json"
    p.write_text(
        json.dumps(
            {
                "nodes": [
                    {"id": "lib", "label": "lib", "file_type": "code", "source_file": "pkg/lib.py"},
                    {"id": "app", "label": "app", "file_type": "code", "source_file": "pkg/app.py"},
                ],
                "edges": [{"source": "app", "target": "lib", "relation": "imports"}],
            }
        ),
        encoding="utf-8",
    )
    return p


def test_impact_of_finds_importer(tmp_path: Path) -> None:
    g = load_graph(_graph(tmp_path))
    assert impact_of(g, "lib", max_hops=3) == ("app",)


def test_paths_and_nodes_from_diff(tmp_path: Path) -> None:
    diff = "--- a/pkg/lib.py\n+++ b/pkg/lib.py\n@@\n+1\n"
    assert "pkg/lib.py" in paths_from_diff(diff)
    g = load_graph(_graph(tmp_path))
    assert "lib" in node_ids_for_paths(g, ("pkg/lib.py",))


def test_merge_git_diff_into_hot_updates(tmp_path: Path) -> None:
    g = load_graph(_graph(tmp_path))
    hot = tmp_path / "hot.md"
    hot.write_text(render_hot({"symptom": "x"}), encoding="utf-8")
    diff = "--- a/pkg/lib.py\n+++ b/pkg/lib.py\n"
    merge_git_diff_into_hot(hot, diff, g)
    text = hot.read_text(encoding="utf-8")
    assert "pkg/lib.py" in text
    assert "lib" in text


def test_doc_graph_signals_flags_mismatch(tmp_path: Path) -> None:
    p = tmp_path / "g.json"
    p.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "fn",
                        "label": "immutable cache (read-only)",
                        "file_type": "code",
                        "source_file": "x.py",
                        "documentation": "This API is immutable.",
                    },
                    {
                        "id": "rm",
                        "label": "os.remove wrapper",
                        "file_type": "code",
                        "source_file": "y.py",
                    },
                ],
                "edges": [{"source": "fn", "target": "rm", "relation": "calls"}],
            }
        ),
        encoding="utf-8",
    )
    g = load_graph(p)
    sigs = doc_graph_signals(g)
    assert any(s.node_id == "fn" for s in sigs)


def test_architecture_ego_report(tmp_path: Path) -> None:
    g = load_graph(_graph(tmp_path))
    md = architecture_ego_report(g, ("lib",), hops=2)
    assert "ego" in md.lower()
    assert "imports" in md
