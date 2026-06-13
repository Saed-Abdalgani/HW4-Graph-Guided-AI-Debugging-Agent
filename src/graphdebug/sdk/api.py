"""Public SDK facade (FR-S1): core graphdebug API + Phase 7 fix/verify."""

from __future__ import annotations

from graphdebug.sdk.api_core import *  # noqa: F403
from graphdebug.sdk.api_core import __all__ as _CORE_ALL
from graphdebug.sdk.api_experiment import (
    ArmMetrics,
    KPIResult,
    TokenExperimentResult,
    run_token_experiment,
)
from graphdebug.sdk.phase7 import (
    Phase7VerifyResult,
    apply_approved_patch,
    capture_after_knowledge_snapshot,
    merge_bug_analysis_report,
    run_phase7_verification,
    scaffold_patch_comparison,
    write_vault_knowledge_delta,
)
from graphdebug.services.fixverify.review import PatchReviewResult, review_patch_for_symptom_masks
from graphdebug.services.fixverify.verify import new_failures_since_baseline

__all__ = list(_CORE_ALL) + [
    "ArmMetrics",
    "KPIResult",
    "TokenExperimentResult",
    "run_token_experiment",
    "Phase7VerifyResult",
    "PatchReviewResult",
    "apply_approved_patch",
    "capture_after_knowledge_snapshot",
    "merge_bug_analysis_report",
    "new_failures_since_baseline",
    "review_patch_for_symptom_masks",
    "run_phase7_verification",
    "scaffold_patch_comparison",
    "write_vault_knowledge_delta",
]
