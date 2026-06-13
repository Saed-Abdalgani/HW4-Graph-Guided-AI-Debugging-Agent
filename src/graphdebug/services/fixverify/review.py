"""HITL helpers: flag likely symptom-masking patterns in a unified diff (todo T7.1)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PatchReviewResult:
    ok: bool
    warnings: tuple[str, ...]


_BARE_EXCEPT = re.compile(r"^\+\s*except\s*:\s*$", re.M)
_BROAD_EXCEPT_PASS = re.compile(r"^\+\s*except\s+Exception\s*:", re.M)
_SILENCE_LOG = re.compile(r"^\+\s*(?:logger\.|logging\.)?(?:warn|warning|error)\s*\(", re.M)
_FORCE_TRUE = re.compile(r"^\+\s*(?:assert\s+True|return\s+True)\s*$", re.M)


def _only_test_paths(diff: str) -> bool:
    paths = re.findall(r"^\+\+\+ b/(.+)$", diff, re.M)
    if not paths:
        return False
    return all("test" in p.lower() for p in paths)


def review_patch_for_symptom_masks(unified_diff: str) -> PatchReviewResult:
    """Return review hints; ``ok`` is False on high-confidence anti-patterns."""
    warns: list[str] = []
    if _BARE_EXCEPT.search(unified_diff):
        warns.append("Added bare `except:` — often masks real failures.")
    if _BROAD_EXCEPT_PASS.search(unified_diff) and "pass" in unified_diff:
        warns.append("Broad `except Exception` — verify `pass` is not swallowing bugs.")
    if _SILENCE_LOG.search(unified_diff):
        warns.append("Added logging on error path — confirm behavior is still correct.")
    if _FORCE_TRUE.search(unified_diff):
        warns.append("Added `assert True` / `return True` — possible test neutering.")
    if _only_test_paths(unified_diff):
        warns.append("All touched paths look like tests — confirm production code is fixed.")
    hard = bool(_BARE_EXCEPT.search(unified_diff))
    return PatchReviewResult(ok=not hard, warnings=tuple(warns))


__all__ = ["PatchReviewResult", "review_patch_for_symptom_masks"]
