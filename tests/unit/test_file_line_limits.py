"""G.6: no Python module may exceed MAX_CODE_LINES (excluding blanks-only lines)."""

from __future__ import annotations

from pathlib import Path

import pytest

MAX_CODE_LINES = 150
_ROOT = Path(__file__).resolve().parents[2]


def _code_lines(path: Path) -> int:
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            n += 1
    return n


@pytest.mark.parametrize(
    "rel",
    sorted(str(p.relative_to(_ROOT)) for p in _ROOT.joinpath("src/graphdebug").rglob("*.py")),
)
def test_src_modules_respect_line_budget(rel: str) -> None:
    path = _ROOT / rel
    assert _code_lines(path) <= MAX_CODE_LINES, f"{rel} exceeds {MAX_CODE_LINES} non-blank lines"


@pytest.mark.parametrize(
    "rel",
    sorted(str(p.relative_to(_ROOT)) for p in _ROOT.joinpath("tests").rglob("*.py")),
)
def test_test_modules_respect_line_budget(rel: str) -> None:
    path = _ROOT / rel
    assert _code_lines(path) <= MAX_CODE_LINES, f"{rel} exceeds {MAX_CODE_LINES} non-blank lines"
