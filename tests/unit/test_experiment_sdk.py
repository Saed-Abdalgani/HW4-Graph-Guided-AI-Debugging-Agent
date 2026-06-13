"""SDK facade for Phase 8 token experiment (mocked)."""

from __future__ import annotations

import json

import pytest

from graphdebug.sdk import api_experiment
from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.agents.state import BugTask
from graphdebug.shared.config import AppConfig
from tests.unit.experiment_fixtures import manifest_row, write_minimal_project_config


def test_sdk_api_experiment_runs_with_mock(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path_factory.mktemp("sdkexp")
    write_minimal_project_config(root)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    def fake_run(
        bug_task: BugTask,
        mode: str,
        config: AppConfig,
        **_: object,
    ) -> InvestigationResult:
        run_dir = config.paths["results"] / f"sdk-{mode}"
        run_dir.mkdir(parents=True, exist_ok=True)
        manifest = run_dir / "manifest.json"
        manifest.write_text(
            json.dumps(
                manifest_row(mode, run_dir.name, total_tokens=500, files_read=2, iterations=1),
            ),
            encoding="utf-8",
        )
        ledger = run_dir / "ledger.jsonl"
        ledger.write_text("", encoding="utf-8")
        return InvestigationResult(
            run_id=run_dir.name,
            mode=mode,
            ledger_path=ledger,
            final_state={},
            halted_reason=None,
            manifest_path=manifest,
        )

    monkeypatch.setattr(
        "graphdebug.services.experiment.runner.run_investigation",
        fake_run,
    )
    bug = BugTask(target_root="/t", failing_tests=("t::t",), symptom="x")
    res = api_experiment.run_token_experiment(
        bug,
        project_root=root,
        write_artifacts=False,
    )
    assert res.naive_metrics.total_tokens == 500
