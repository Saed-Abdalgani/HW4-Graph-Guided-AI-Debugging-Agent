"""Symptom-mask heuristics on diffs."""

from __future__ import annotations

from graphdebug.services.fixverify.review import review_patch_for_symptom_masks


def test_review_flags_bare_except() -> None:
    diff = "--- a/x.py\n+++ b/x.py\n@@\n+except:\n+    pass\n"
    r = review_patch_for_symptom_masks(diff)
    assert r.ok is False
    assert any("bare" in w.lower() for w in r.warnings)


def test_review_ok_minimal_diff() -> None:
    diff = "--- a/x.py\n+++ b/x.py\n@@\n+encoding='utf-8'\n"
    r = review_patch_for_symptom_masks(diff)
    assert r.ok is True
