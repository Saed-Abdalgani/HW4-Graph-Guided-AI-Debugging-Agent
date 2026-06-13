# Phase 7 — fix, verify, evidence (M4)

Automates **T7.2–T7.4**, **T7.5** (stub), **T7.6–T7.7** helpers. **T7.1** remains human judgment; `review-patch` surfaces heuristics only.

## Commands (from graphdebug repo root)

| Step | Command |
|------|---------|
| HITL heuristics (T7.1) | `uv run graphdebug phase7 review-patch --diff path/to/proposed.diff` |
| Save `reports/fix.diff` + `git apply` (T7.2) | `uv run graphdebug phase7 apply --diff proposed.diff --target-root data/<target>` |
| Target + suite pytest + regression file (T7.3–4) | `uv run graphdebug phase7 verify --target-root data/<target> --test tests/t.py::x [--baseline-red results/baseline_red.txt]` |
| After vault snapshot (T7.7) | `uv run graphdebug phase7 snapshot-after` |
| `reports/vault_before_after.md` | `uv run graphdebug phase7 vault-diff` |
| Official patch compare stub (T7.5) | `uv run graphdebug phase7 patch-compare --ours reports/fix.diff --official path/to/official.patch` |
| Fill `reports/bug_analysis.md` TBD lines (T7.6) | `uv run graphdebug phase7 merge-docs --hypothesis-file h.txt --fix-file f.txt --verification-file v.txt` |

**Regression rule**: capture a **full-suite** red log at the same pytest scope as green. Then `new_failures = failed_after - failed_before` (pytest `FAILED` lines). The target test should disappear from the failure set after a correct fix.

**T7.8**: If diagrams change meaningfully, re-run `phase4-export` or add `assets/*_after.*` manually.

SDK: `apply_approved_patch`, `run_phase7_verification`, `capture_after_knowledge_snapshot`, `write_vault_knowledge_delta`, `scaffold_patch_comparison`, `merge_bug_analysis_report`, `review_patch_for_symptom_masks`.
