"""Append-only JSONL ledger under ``results/<run_id>/`` (T5.4)."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from graphdebug.services.ledger.schema import LedgerRecord


class LedgerWriter:
    """Thread-safe JSONL writer."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, record: LedgerRecord) -> None:
        line = json.dumps(record.to_json_row(), ensure_ascii=False) + "\n"
        with self._lock:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line)


__all__ = ["LedgerWriter"]
