"""Graph / naive suspect ranking without reading source (T5.6)."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.agents.state import AgentState, StepRecordTD, SuspectNode, suspect_to_td
from graphdebug.services.agents.suspect_rank import rank_suspects
from graphdebug.services.graphify import load_graph


def _naive_py_files(root: Path, limit: int = 40) -> list[str]:
    paths: list[str] = []
    for p in sorted(root.rglob("*.py")):
        rel = str(p.relative_to(root)).replace("\\", "/")
        if "/.venv/" in f"/{rel}/" or "/__pycache__/" in f"/{rel}/":
            continue
        paths.append(rel)
        if len(paths) >= limit:
            break
    return paths


def run_investigator(
    state: AgentState,
    *,
    graph_json: Path,
    source_prefixes: tuple[str, ...],
) -> dict:
    if state.get("halted_reason"):
        return {}
    budget = state["budget"]
    it = int(state.get("iterations", 0))
    budget_mod.assert_can_iterate(budget, it, 1)
    bug = state["bug_task"]
    tests = tuple(bug.get("failing_tests") or ())
    root = Path(bug["target_root"])

    if state.get("mode") == "naive":
        files = _naive_py_files(root)
        if not files:
            files = ["."]
        suspects = [
            suspect_to_td(
                SuspectNode(
                    node_id=rel,
                    score=1.0 - (i * 0.01),
                    why="Naive baseline: shallow file walk ordering (no graph).",
                    betweenness=0.0,
                    test_proximity=0.0,
                )
            )
            for i, rel in enumerate(files[:12])
        ]
        log = [
            StepRecordTD(
                role="investigator",
                action="naive_file_walk",
                detail=f"ranked {len(suspects)} paths without graph context",
            )
        ]
        return {
            "suspects": suspects,
            "suspects_ranked": True,
            "naive_file_suspects": files,
            "iterations": it + 1,
            "log": log,
        }

    graph = load_graph(graph_json)
    ranked = rank_suspects(graph, failing_tests=tests, source_prefixes=source_prefixes, top_k=10)
    suspects = [suspect_to_td(s) for s in ranked]
    log = [
        StepRecordTD(
            role="investigator",
            action="graph_rank",
            detail="; ".join(f"{s.node_id}:{s.score:.3f}" for s in ranked[:5]),
        )
    ]
    return {
        "suspects": suspects,
        "suspects_ranked": True,
        "iterations": it + 1,
        "log": log,
    }


__all__ = ["run_investigator"]
