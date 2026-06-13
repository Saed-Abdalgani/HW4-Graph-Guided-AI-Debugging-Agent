"""Post-fix pytest runs + regression vs baseline red (todo T7.3, T7.4)."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from graphdebug.services.pytest_parse import failed_nodeids_from_pytest_text


@dataclass(frozen=True, slots=True)
class Phase7VerifyResult:
    target_rc: int
    target_stdout: str
    suite_rc: int
    suite_stdout: str
    baseline_green_path: Path
    suite_green_path: Path
    regression_report_path: Path
    new_failures_vs_baseline: tuple[str, ...]
    target_tests_passed: bool


def _pytest(root: Path, args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=no", *args]
    return subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def new_failures_since_baseline(*, failed_before: set[str], failed_after: set[str]) -> set[str]:
    """Failures present after fix that were not in the baseline red failure set."""
    return failed_after - failed_before


def run_post_fix_verification(
    *,
    target_root: Path,
    results_dir: Path,
    target_tests: tuple[str, ...],
    baseline_red_path: Path | None,
    suite_extra_args: tuple[str, ...] = (),
    timeout: int = 900,
) -> Phase7VerifyResult:
    """Run target tests then suite; write logs; optional regression vs ``baseline_red``."""
    results_dir.mkdir(parents=True, exist_ok=True)
    tgt = _pytest(target_root, list(target_tests), timeout)
    target_blob = (tgt.stdout or "") + "\n" + (tgt.stderr or "")
    green_path = results_dir / "baseline_green.txt"
    green_path.write_text(
        f"# returncode={tgt.returncode}\n{target_blob}",
        encoding="utf-8",
    )

    suite_args = list(suite_extra_args) if suite_extra_args else ["."]
    suite = _pytest(target_root, suite_args, timeout)
    suite_blob = (suite.stdout or "") + "\n" + (suite.stderr or "")
    suite_path = results_dir / "suite_green.txt"
    suite_path.write_text(
        f"# returncode={suite.returncode}\n{suite_blob}",
        encoding="utf-8",
    )

    failed_after = failed_nodeids_from_pytest_text(suite_blob)
    target_ok = tgt.returncode == 0 and not failed_nodeids_from_pytest_text(target_blob)

    new_f: set[str] = set()
    if baseline_red_path and baseline_red_path.is_file():
        red_blob = baseline_red_path.read_text(encoding="utf-8", errors="replace")
        failed_before = failed_nodeids_from_pytest_text(red_blob)
        new_f = new_failures_since_baseline(
            failed_before=failed_before,
            failed_after=failed_after,
        )

    rep_lines = [
        "# Phase 7 regression summary",
        f"target_rc={tgt.returncode} suite_rc={suite.returncode}",
        f"target_tests_passed={target_ok}",
        f"new_failures_vs_baseline={sorted(new_f)}",
    ]
    rep_path = results_dir / "regression_phase7.txt"
    rep_path.write_text("\n".join(rep_lines) + "\n", encoding="utf-8")

    return Phase7VerifyResult(
        target_rc=tgt.returncode,
        target_stdout=target_blob,
        suite_rc=suite.returncode,
        suite_stdout=suite_blob,
        baseline_green_path=green_path,
        suite_green_path=suite_path,
        regression_report_path=rep_path,
        new_failures_vs_baseline=tuple(sorted(new_f)),
        target_tests_passed=target_ok,
    )


__all__ = [
    "Phase7VerifyResult",
    "new_failures_since_baseline",
    "run_post_fix_verification",
]
