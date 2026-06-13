"""Vault before/after report."""

from __future__ import annotations

import json
from pathlib import Path

from graphdebug.services.fixverify.reports import write_vault_before_after_report


def test_write_vault_before_after_report(tmp_path: Path) -> None:
    b = tmp_path / "before"
    a = tmp_path / "after"
    b.mkdir()
    a.mkdir()
    (b / "manifest.json").write_text(
        json.dumps({"files": ["hot.md"]}),
        encoding="utf-8",
    )
    (a / "manifest.json").write_text(
        json.dumps({"files": ["hot.md", "new.md"]}),
        encoding="utf-8",
    )
    out = tmp_path / "rep.md"
    write_vault_before_after_report(before_dir=b, after_dir=a, out_path=out)
    text = out.read_text(encoding="utf-8")
    assert "new.md" in text
