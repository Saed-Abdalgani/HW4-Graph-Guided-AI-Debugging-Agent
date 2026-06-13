"""bug_analysis.md placeholder merge."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.fixverify.bug_analysis import merge_bug_analysis_sections


def test_merge_bug_analysis_sections(tmp_path: Path) -> None:
    p = tmp_path / "bug_analysis.md"
    p.write_text(
        "## Hypothesis / root cause\n\n_TBD (Phase 6)._\n\n## Fix summary\n\n_TBD (Phase 7)._\n\n"
        "## Verification\n\n_TBD: red → green log, regression note._\n",
        encoding="utf-8",
    )
    merge_bug_analysis_sections(
        p,
        hypothesis="Root is X.",
        fix_summary="Set encoding.",
        verification="pytest green.",
    )
    t = p.read_text(encoding="utf-8")
    assert "Root is X." in t
    assert "_TBD (Phase 6)._" not in t
