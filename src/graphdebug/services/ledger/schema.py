"""Ledger JSONL record schema (FR-T3)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LedgerRecord:
    role: str
    event: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    tool_calls: int = 0
    files_read: int = 0
    meta: dict[str, Any] | None = None

    def to_json_row(self) -> dict[str, Any]:
        row = asdict(self)
        if row.get("meta") is None:
            row.pop("meta", None)
        return row


__all__ = ["LedgerRecord"]
