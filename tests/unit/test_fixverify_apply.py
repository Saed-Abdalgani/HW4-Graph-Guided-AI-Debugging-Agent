"""Small apply/report helpers."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.fixverify.apply import copy_patch_to_reports
from graphdebug.services.fixverify.reports import compare_patch_text_files


def test_copy_patch_to_reports(tmp_path: Path) -> None:
    out = copy_patch_to_reports("diff body\n", tmp_path / "reports")
    assert out.read_text(encoding="utf-8") == "diff body\n"


def test_compare_patch_text_files(tmp_path: Path) -> None:
    a = tmp_path / "a.patch"
    b = tmp_path / "b.patch"
    a.write_text("x", encoding="utf-8")
    b.write_text("yy", encoding="utf-8")
    out = tmp_path / "c.md"
    compare_patch_text_files(a, b, out)
    assert "1 bytes" in out.read_text(encoding="utf-8")
