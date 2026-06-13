"""Regression set algebra (T7.4)."""

from __future__ import annotations

from graphdebug.services.fixverify.verify import new_failures_since_baseline


def test_new_failures_since_baseline_only_target_fixed() -> None:
    before = {"tests/t.py::one", "tests/u.py::two"}
    after: set[str] = set()
    new = new_failures_since_baseline(failed_before=before, failed_after=after)
    assert new == set()


def test_new_failures_detects_regression() -> None:
    before = {"tests/t.py::one"}
    after = {"tests/t.py::one", "tests/z.py::new"}
    new = new_failures_since_baseline(failed_before=before, failed_after=after)
    assert new == {"tests/z.py::new"}
