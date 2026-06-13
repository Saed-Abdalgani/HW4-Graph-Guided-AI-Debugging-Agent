"""Smoke: post-fix verification on a trivial pytest tree."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.fixverify.verify import run_post_fix_verification


def test_run_post_fix_verification_no_baseline(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text("def test_x():\n    assert 1\n", encoding="utf-8")
    res = run_post_fix_verification(
        target_root=tmp_path,
        results_dir=tmp_path / "res",
        target_tests=("tests/t.py::test_x",),
        baseline_red_path=None,
        timeout=60,
    )
    assert res.target_tests_passed
    assert res.baseline_green_path.is_file()
