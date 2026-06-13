"""Aggregate ledger JSONL for experiment reports (FR-T3)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LedgerSummary:
    entries: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_tool_calls: int
    total_files_read: int
    roles: tuple[str, ...]


def aggregate_ledger(path: Path) -> LedgerSummary:
    if not path.is_file():
        return LedgerSummary(0, 0, 0, 0, 0, 0, ())
    roles: set[str] = set()
    n = pt = ct = tt = tc = fr = 0
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            n += 1
            pt += int(row.get("prompt_tokens", 0))
            ct += int(row.get("completion_tokens", 0))
            tt += int(row.get("total_tokens", 0))
            tc += int(row.get("tool_calls", 0))
            fr += int(row.get("files_read", 0))
            r = row.get("role")
            if isinstance(r, str):
                roles.add(r)
    return LedgerSummary(n, pt, ct, tt, tc, fr, tuple(sorted(roles)))


__all__ = ["LedgerSummary", "aggregate_ledger"]
