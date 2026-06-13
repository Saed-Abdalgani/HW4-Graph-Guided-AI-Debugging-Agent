"""Replace Phase 6–7 placeholders in ``reports/bug_analysis.md`` (todo T7.6)."""

from __future__ import annotations

from pathlib import Path


def merge_bug_analysis_sections(
    path: Path,
    *,
    hypothesis: str,
    fix_summary: str,
    verification: str,
) -> Path:
    """Swap markdown italic TBD lines for supplied prose."""
    text = path.read_text(encoding="utf-8")
    text = text.replace("_TBD (Phase 6)._", hypothesis.strip())
    text = text.replace("_TBD (Phase 7)._", fix_summary.strip())
    text = text.replace(
        "_TBD: red → green log, regression note._",
        verification.strip(),
    )
    path.write_text(text, encoding="utf-8")
    return path


__all__ = ["merge_bug_analysis_sections"]
