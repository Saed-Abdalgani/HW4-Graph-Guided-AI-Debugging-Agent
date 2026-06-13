"""Budget guard boundaries (T5.3)."""

from __future__ import annotations

import pytest

from graphdebug.services.agents.budget import (
    BudgetExceeded,
    assert_can_iterate,
    assert_can_read_file,
    assert_can_tool_call,
    assert_can_use_tokens,
)
from graphdebug.services.agents.state import initial_budget_row
from graphdebug.shared.config import BudgetProfile


def _budget() -> dict:
    return initial_budget_row(
        BudgetProfile(
            max_tokens=100,
            max_tool_calls=5,
            max_files=3,
            max_iterations=10,
        )
    )


def test_token_cap_at_boundary() -> None:
    b = _budget()
    b["tokens_used"] = 100
    with pytest.raises(BudgetExceeded):
        assert_can_use_tokens(b, 1)


def test_tool_call_cap() -> None:
    b = _budget()
    for _ in range(5):
        pass
    b["tool_calls"] = 5
    with pytest.raises(BudgetExceeded):
        assert_can_tool_call(b, 1)


def test_file_cap() -> None:
    b = _budget()
    b["files_read"] = 3
    with pytest.raises(BudgetExceeded):
        assert_can_read_file(b, 1)


def test_iteration_cap() -> None:
    b = _budget()
    with pytest.raises(BudgetExceeded):
        assert_can_iterate(b, 10, 1)
