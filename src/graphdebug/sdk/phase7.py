"""SDK entrypoints for Phase 7 (fix, verify, vault evidence)."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.fixverify.apply import apply_approved_patch_files
from graphdebug.services.fixverify.bug_analysis import merge_bug_analysis_sections
from graphdebug.services.fixverify.reports import (
    compare_patch_text_files,
    write_vault_before_after_report,
)
from graphdebug.services.fixverify.verify import Phase7VerifyResult, run_post_fix_verification
from graphdebug.services.vault.snapshot import AFTER_SNAPSHOT_SUBDIR, capture_knowledge_snapshot
from graphdebug.shared.config import load_config


def apply_approved_patch(
    diff_path: str | Path,
    target_root: str | Path,
    *,
    project_root: Path | None = None,
) -> Path:
    """Save ``reports/fix.diff`` and ``git apply`` in the subject tree (T7.2)."""
    root = (project_root or Path.cwd()).resolve()
    cfg = load_config(project_root=root, require_api_key=False)
    return apply_approved_patch_files(
        diff_path=Path(diff_path),
        target_root=Path(target_root).resolve(),
        reports_dir=cfg.paths["reports"],
    )


def run_phase7_verification(
    target_root: str | Path,
    target_tests: tuple[str, ...],
    *,
    project_root: Path | None = None,
    baseline_red: Path | None = None,
    suite_args: tuple[str, ...] = (),
) -> Phase7VerifyResult:
    """Target pytest + full suite logs + regression summary (T7.3–T7.4)."""
    root = (project_root or Path.cwd()).resolve()
    cfg = load_config(project_root=root, require_api_key=False)
    red = baseline_red if baseline_red is not None else cfg.paths["results"] / "baseline_red.txt"
    red_path = red if red.is_file() else None
    return run_post_fix_verification(
        target_root=Path(target_root).resolve(),
        results_dir=cfg.paths["results"],
        target_tests=target_tests,
        baseline_red_path=red_path,
        suite_extra_args=suite_args,
    )


def capture_after_knowledge_snapshot(*, project_root: Path | None = None) -> Path:
    """Snapshot vault to ``results/knowledge_snapshots/after`` (T7.7)."""
    root = (project_root or Path.cwd()).resolve()
    cfg = load_config(project_root=root, require_api_key=False)
    return capture_knowledge_snapshot(
        cfg.paths["obsidian_vault"],
        cfg.paths["results"],
        subdir=AFTER_SNAPSHOT_SUBDIR,
    )


def write_vault_knowledge_delta(*, project_root: Path | None = None) -> Path:
    """Write ``reports/vault_before_after.md`` from before/after snapshot dirs."""
    root = (project_root or Path.cwd()).resolve()
    cfg = load_config(project_root=root, require_api_key=False)
    res = cfg.paths["results"]
    return write_vault_before_after_report(
        before_dir=res / "knowledge_snapshots" / "before",
        after_dir=res / "knowledge_snapshots" / "after",
        out_path=cfg.paths["reports"] / "vault_before_after.md",
    )


def scaffold_patch_comparison(
    ours: str | Path,
    official: str | Path,
    *,
    project_root: Path | None = None,
) -> Path:
    """T7.5 stub writer for ``reports/patch_comparison.md``."""
    root = (project_root or Path.cwd()).resolve()
    cfg = load_config(project_root=root, require_api_key=False)
    return compare_patch_text_files(
        Path(ours),
        Path(official),
        cfg.paths["reports"] / "patch_comparison.md",
    )


def merge_bug_analysis_report(
    *,
    hypothesis: str,
    fix_summary: str,
    verification: str,
    project_root: Path | None = None,
) -> Path:
    """Replace TBD lines in ``reports/bug_analysis.md`` (T7.6)."""
    root = (project_root or Path.cwd()).resolve()
    cfg = load_config(project_root=root, require_api_key=False)
    return merge_bug_analysis_sections(
        cfg.paths["reports"] / "bug_analysis.md",
        hypothesis=hypothesis,
        fix_summary=fix_summary,
        verification=verification,
    )


__all__ = [
    "Phase7VerifyResult",
    "apply_approved_patch",
    "capture_after_knowledge_snapshot",
    "merge_bug_analysis_report",
    "run_phase7_verification",
    "scaffold_patch_comparison",
    "write_vault_knowledge_delta",
]
