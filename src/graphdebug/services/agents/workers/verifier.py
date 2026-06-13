"""Run pytest on the subject tree (T5.9)."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.agents.state import AgentState, StepRecordTD


def _failed_from_output(blob: str) -> set[str]:
    failed: set[str] = set()
    for line in blob.splitlines():
        if line.startswith("FAILED "):
            parts = line.split()
            if len(parts) >= 2:
                failed.add(parts[1].strip())
    return failed


def default_verify(state: AgentState) -> dict:
    bug = state["bug_task"]
    root = Path(bug["target_root"])
    tests = list(bug.get("failing_tests") or ())
    if not tests:
        return {
            "verified": False,
            "verification_attempted": True,
            "pytest_returncode": 2,
            "pytest_stdout": "",
            "pytest_stderr": "bug_task has no failing_tests",
            "log": [
                StepRecordTD(role="verifier", action="skip", detail="missing failing_tests"),
            ],
        }
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=no", *tests]
    proc = subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    failed = _failed_from_output(blob)
    targets = set(tests)
    extra_failures = failed - targets
    verified = proc.returncode == 0 and not extra_failures
    detail = f"rc={proc.returncode} failed={sorted(failed)[:12]}"
    log = [StepRecordTD(role="verifier", action="pytest", detail=detail)]
    return {
        "verified": verified,
        "verification_attempted": True,
        "pytest_returncode": proc.returncode,
        "pytest_stdout": (proc.stdout or "")[-12000:],
        "pytest_stderr": (proc.stderr or "")[-4000:],
        "log": log,
    }


def run_verifier(
    state: AgentState,
    *,
    verify_fn: Callable[[AgentState], dict] | None = None,
) -> dict:
    if state.get("halted_reason"):
        return {}
    budget = state["budget"]
    it = int(state.get("iterations", 0))
    budget_mod.assert_can_iterate(budget, it, 1)
    fn = verify_fn or default_verify
    result = dict(fn(state))
    log = result.pop("log", [])
    return {"iterations": it + 1, "log": log, **result}


__all__ = ["default_verify", "run_verifier"]
