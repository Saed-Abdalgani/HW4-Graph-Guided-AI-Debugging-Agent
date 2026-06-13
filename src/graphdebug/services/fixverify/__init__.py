"""Phase 7: apply patches, pytest evidence, regression, vault diff."""

from graphdebug.services.fixverify.apply import (
    apply_approved_patch_files,
    apply_unified_diff_git,
    copy_patch_to_reports,
)
from graphdebug.services.fixverify.bug_analysis import merge_bug_analysis_sections
from graphdebug.services.fixverify.reports import (
    compare_patch_text_files,
    write_vault_before_after_report,
)
from graphdebug.services.fixverify.review import PatchReviewResult, review_patch_for_symptom_masks
from graphdebug.services.fixverify.verify import (
    Phase7VerifyResult,
    new_failures_since_baseline,
    run_post_fix_verification,
)

__all__ = [
    "Phase7VerifyResult",
    "PatchReviewResult",
    "apply_approved_patch_files",
    "apply_unified_diff_git",
    "compare_patch_text_files",
    "copy_patch_to_reports",
    "merge_bug_analysis_sections",
    "new_failures_since_baseline",
    "review_patch_for_symptom_masks",
    "run_post_fix_verification",
    "write_vault_before_after_report",
]
