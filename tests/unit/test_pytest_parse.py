"""Pytest stdout parsing."""

from __future__ import annotations

from graphdebug.services.pytest_parse import failed_nodeids_from_pytest_text


def test_failed_nodeids_from_pytest_text() -> None:
    blob = "FAILED tests/x.py::a\nPASSED t\nFAILED tests/y.py::b\n"
    assert failed_nodeids_from_pytest_text(blob) == {"tests/x.py::a", "tests/y.py::b"}
