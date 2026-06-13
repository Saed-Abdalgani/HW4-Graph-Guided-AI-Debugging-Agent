"""Read vault + GRAPH_REPORT only — no source files (T5.5)."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.agents.state import AgentState, StepRecordTD


def _clip(text: str, limit: int = 12000) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "\n…(truncated)…\n"


def run_navigator(state: AgentState, *, vault: Path, graph_report: Path) -> dict:
    if state.get("halted_reason"):
        return {}
    budget = state["budget"]
    it = int(state.get("iterations", 0))
    budget_mod.assert_can_iterate(budget, it, 1)

    if state.get("mode") == "naive":
        log = [
            StepRecordTD(
                role="navigator",
                action="naive_skip_vault",
                detail="Naive mode: no index/hot/GRAPH_REPORT context.",
            )
        ]
        return {"oriented": True, "iterations": it + 1, "log": log}

    index_p = vault / "index.md"
    hot_p = vault / "hot.md"
    chunks: list[str] = []
    for label, path in (("index", index_p), ("hot", hot_p), ("GRAPH_REPORT", graph_report)):
        if path.is_file():
            chunks.append(f"### {label}: {path.name}\n{_clip(path.read_text(encoding='utf-8'))}")
        else:
            chunks.append(f"### {label}: MISSING ({path})")

    detail = "\n\n".join(chunks)
    log = [
        StepRecordTD(
            role="navigator",
            action="vault_orientation",
            detail=detail[:8000],
        )
    ]
    return {"oriented": True, "iterations": it + 1, "log": log}


__all__ = ["run_navigator"]
