"""Budget-gated minimal source reads (T5.7) — only this worker reads code."""

from __future__ import annotations

import re
from pathlib import Path

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.agents.state import AgentState, StepRecordTD
from graphdebug.services.graphify import load_graph
from graphdebug.services.graphify.models import GraphNode
from graphdebug.services.ledger.schema import LedgerRecord
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared.config import RetrieverConfig

_LOC_RE = re.compile(r":(\d+)(?:\)|$|:)")


def _center_line(node: GraphNode) -> int | None:
    loc = (node.source_location or "").strip()
    if loc.upper().startswith("L"):
        tail = loc[1:].split(":", 1)[0]
        if tail.isdigit():
            return int(tail)
    m = _LOC_RE.search(loc)
    if m:
        return int(m.group(1))
    return None

def _resolve_path(root: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    rel = rel.replace("\\", "/").lstrip("/")
    for candidate in (root / rel, root / "src" / rel):
        if candidate.is_file():
            return candidate
    return None

def _read_slice(path: Path, center: int | None, max_lines: int) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not raw:
        return ""
    idx = max(0, (center or 1) - 1)
    half = max(1, max_lines // 2)
    start = max(0, idx - half)
    end = min(len(raw), start + max_lines)
    body = "\n".join(f"{i+1:4d}| {raw[i]}" for i in range(start, end))
    return f"## {path}\n```{path.suffix or '.txt'}\n{body}\n```\n"

def run_retriever(
    state: AgentState,
    *,
    graph_json: Path,
    ledger: LedgerWriter,
    retriever_cfg: RetrieverConfig,
) -> dict:
    if state.get("halted_reason"):
        return {}
    budget = state["budget"]
    it = int(state.get("iterations", 0))
    budget_mod.assert_can_iterate(budget, it, 1)
    bug = state["bug_task"]
    root = Path(bug["target_root"])
    suspects = state.get("suspects") or []
    max_files = retriever_cfg.max_suspects_fetched
    max_lines = retriever_cfg.max_lines_per_file

    fetched: dict[str, str] = {}
    logs: list[StepRecordTD] = []

    if state.get("mode") == "graph":
        graph = load_graph(graph_json)
        count = 0
        for row in suspects[: max_files + 5]:
            if count >= max_files:
                break
            nid = row["node_id"]
            node = graph.nodes.get(nid)
            rel = node.source_file if node else None
            path = _resolve_path(root, rel)
            if path is None:
                continue
            budget_mod.assert_can_read_file(budget, 1)
            center = _center_line(node) if node else None
            text = _read_slice(path, center, max_lines)
            fetched[nid] = text
            budget_mod.record_file_read(budget, 1)
            ledger.append(
                LedgerRecord(
                    role="retriever",
                    event="file_read",
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency_ms=0.0,
                    files_read=1,
                    meta={"path": str(path)},
                )
            )
            count += 1
            logs.append(
                StepRecordTD(
                    role="retriever",
                    action="slice",
                    detail=f"{nid} -> {path} ({max_lines} lines max)",
                )
            )
    else:
        for row in suspects[:max_files]:
            rel = row["node_id"]
            path = _resolve_path(root, rel)
            if path is None:
                continue
            budget_mod.assert_can_read_file(budget, 1)
            text = _read_slice(path, None, max_lines)
            fetched[rel] = text
            budget_mod.record_file_read(budget, 1)
            ledger.append(
                LedgerRecord(
                    role="retriever",
                    event="file_read",
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency_ms=0.0,
                    files_read=1,
                    meta={"path": str(path)},
                )
            )
            logs.append(
                StepRecordTD(role="retriever", action="slice", detail=str(path)),
            )

    if not fetched and suspects:
        logs.append(
            StepRecordTD(
                role="retriever",
                action="no_files",
                detail="Could not resolve on-disk paths for top suspects.",
            )
        )

    return {
        "fetched_code": fetched,
        "code_fetched": True,
        "iterations": it + 1,
        "log": logs,
    }
__all__ = ["run_retriever"]
