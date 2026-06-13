"""Construction-time dependencies for the LangGraph workflow."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from graphdebug.services.agents.state import AgentState
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared.config import AppConfig
from graphdebug.shared.gatekeeper import Gatekeeper


@dataclass(slots=True)
class InvestigationDeps:
    """Injectable collaborators for tests (mock verifier / no API key)."""

    config: AppConfig
    gatekeeper: Gatekeeper
    ledger: LedgerWriter
    verify_fn: Callable[[AgentState], dict] | None = None


__all__ = ["InvestigationDeps"]
