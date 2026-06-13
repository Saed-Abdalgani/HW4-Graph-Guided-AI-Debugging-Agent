"""Pre-spend budget guards (FR-A5, T5.3)."""

from __future__ import annotations

from typing import Any


class BudgetExceeded(RuntimeError):
    """Raised when the next operation would exceed a configured cap."""


def _b(budget: dict[str, Any]) -> tuple[int, int, int, int, int, int, int]:
    return (
        int(budget["max_tokens"]),
        int(budget["max_tool_calls"]),
        int(budget["max_files"]),
        int(budget["max_iterations"]),
        int(budget["tokens_used"]),
        int(budget["tool_calls"]),
        int(budget["files_read"]),
    )


def assert_can_use_tokens(budget: dict[str, Any], delta: int) -> None:
    mx, _, _, _, used, _, _ = _b(budget)
    if delta < 0:
        raise ValueError("token delta must be non-negative")
    if used + delta > mx:
        raise BudgetExceeded(
            f"Token cap: would use {used + delta} > max_tokens={mx} (delta={delta})."
        )


def assert_can_tool_call(budget: dict[str, Any], delta: int = 1) -> None:
    _, mx, _, _, _, tc, _ = _b(budget)
    if tc + delta > mx:
        raise BudgetExceeded(f"tool_calls cap: {tc + delta} > {mx}.")


def assert_can_read_file(budget: dict[str, Any], delta: int = 1) -> None:
    _, _, mx, _, _, _, fr = _b(budget)
    if fr + delta > mx:
        raise BudgetExceeded(f"max_files cap: {fr + delta} > {mx}.")


def assert_can_iterate(budget: dict[str, Any], iterations: int, delta: int = 1) -> None:
    _, _, _, mx, _, _, _ = _b(budget)
    if iterations + delta > mx:
        raise BudgetExceeded(f"max_iterations cap: {iterations + delta} > {mx}.")


def record_tokens(budget: dict[str, Any], delta: int) -> None:
    budget["tokens_used"] = int(budget["tokens_used"]) + int(delta)


def record_tool_call(budget: dict[str, Any], delta: int = 1) -> None:
    budget["tool_calls"] = int(budget["tool_calls"]) + int(delta)


def record_file_read(budget: dict[str, Any], delta: int = 1) -> None:
    budget["files_read"] = int(budget["files_read"]) + int(delta)


__all__ = [
    "BudgetExceeded",
    "assert_can_iterate",
    "assert_can_read_file",
    "assert_can_tool_call",
    "assert_can_use_tokens",
    "record_file_read",
    "record_tokens",
    "record_tool_call",
]
