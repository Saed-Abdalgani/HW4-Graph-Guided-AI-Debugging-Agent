"""Public result type for ``investigate`` (T5.14)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from graphdebug.services.agents.state import Mode


@dataclass(frozen=True, slots=True)
class InvestigationResult:
    run_id: str
    mode: Mode
    ledger_path: Path
    final_state: dict[str, Any]
    halted_reason: str | None


__all__ = ["InvestigationResult"]
