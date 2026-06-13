"""Ledger JSONL aggregation (T5.4)."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.services.ledger.aggregate import aggregate_ledger
from graphdebug.services.ledger.schema import LedgerRecord
from graphdebug.services.ledger.writer import LedgerWriter


def test_aggregate_empty(tmp_path: Path) -> None:
    p = tmp_path / "missing.jsonl"
    s = aggregate_ledger(p)
    assert s.entries == 0
    assert s.total_tokens == 0


def test_writer_and_aggregate(tmp_path: Path) -> None:
    p = tmp_path / "ledger.jsonl"
    w = LedgerWriter(p)
    w.append(
        LedgerRecord(
            role="fixer",
            event="llm_completion",
            prompt_tokens=3,
            completion_tokens=7,
            total_tokens=10,
            latency_ms=1.0,
            tool_calls=1,
        )
    )
    w.append(
        LedgerRecord(
            role="retriever",
            event="file_read",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=0.0,
            files_read=1,
        )
    )
    agg = aggregate_ledger(p)
    assert agg.entries == 2
    assert agg.total_prompt_tokens == 3
    assert agg.total_completion_tokens == 7
    assert agg.total_tokens == 10
    assert agg.total_files_read == 1
    raw = json.loads(p.read_text(encoding="utf-8").strip().splitlines()[0])
    assert raw["role"] == "fixer"
