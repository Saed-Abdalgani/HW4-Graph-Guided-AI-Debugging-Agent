"""End-to-end investigation on a synthetic tree (mocked LLM, no API)."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import AIMessage

from graphdebug.services.agents.runner import run_investigation
from graphdebug.shared.config import load_config
from tests.integration.investigation_fixtures import write_minimal_investigation_project


def test_investigation_graph_mode_mocked(tmp_path: Path) -> None:
    bug = write_minimal_investigation_project(tmp_path)
    cfg = load_config(project_root=tmp_path, require_api_key=False)

    def invoker(_role: str, _messages):  # noqa: ANN001
        body = """ROOT_CAUSE: foo() returned the wrong constant for the contract under test.

```diff
--- a/pkg/foo.py
+++ b/pkg/foo.py
@@ -1,2 +1,2 @@
 def foo():
-    return 1
+    return 2
```"""
        return AIMessage(
            content=body,
            response_metadata={
                "token_usage": {"prompt_tokens": 4, "completion_tokens": 6, "total_tokens": 10}
            },
        )

    def verify_fn(_state):  # noqa: ANN001
        return {
            "verified": True,
            "pytest_returncode": 0,
            "pytest_stdout": "",
            "pytest_stderr": "",
            "verification_attempted": True,
            "log": [],
        }

    res = run_investigation(
        bug,
        "graph",
        cfg,
        verify_fn=verify_fn,
        llm_invoker=invoker,
        assume_hitl_ack=False,
    )
    assert res.halted_reason is None
    fs = res.final_state
    assert fs.get("oriented") is True
    assert fs.get("suspects_ranked") is True
    assert fs.get("code_fetched") is True
    assert fs.get("patch_ready") is True
    assert fs.get("verified") is True
    assert fs.get("scribed") is True
    assert "foo()" in (fs.get("hypothesis") or "")
    assert res.ledger_path.is_file()
    text = res.ledger_path.read_text(encoding="utf-8")
    assert "fixer" in text
    assert "retriever" in text
    assert res.manifest_path is not None and res.manifest_path.is_file()
    assert res.experiment_arm_path is not None
    man = json.loads(res.manifest_path.read_text(encoding="utf-8"))
    assert man["experiment_arm"] == "graph"
    assert man["deliverables"]["candidate_patch"] is True
    arm_man = res.experiment_arm_path / "manifest.json"
    assert arm_man.is_file()
    latest = tmp_path / "results" / "experiment_arms" / "graph" / "LATEST"
    assert latest.read_text(encoding="utf-8").strip() == res.run_id
    hot = (tmp_path / "obsidian" / "hot.md").read_text(encoding="utf-8")
    assert "Navigator oriented" in hot
    assert "## Checked" in hot
