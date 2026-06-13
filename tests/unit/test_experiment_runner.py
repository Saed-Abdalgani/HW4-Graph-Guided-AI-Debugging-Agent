"""Integration-style tests for ``run_token_experiment`` (Phase 8, mocked LLM runs)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.agents.state import BugTask
from graphdebug.services.experiment.runner import run_token_experiment
from graphdebug.shared.config import AppConfig, load_config
from tests.unit.experiment_fixtures import manifest_row, write_minimal_project_config


def test_run_token_experiment_mocked_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_minimal_project_config(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    def fake_run(
        bug_task: BugTask,
        mode: str,
        config: AppConfig,
        **_: object,
    ) -> InvestigationResult:
        run_dir = config.paths["results"] / f"fake-{mode}"
        run_dir.mkdir(parents=True, exist_ok=True)
        ledger = run_dir / "ledger.jsonl"
        ledger.write_text("", encoding="utf-8")
        manifest = run_dir / "manifest.json"
        spec = manifest_row(
            mode,
            run_dir.name,
            total_tokens=10_000 if mode == "naive" else 3_000,
            files_read=30 if mode == "naive" else 6,
            iterations=3,
        )
        manifest.write_text(json.dumps(spec), encoding="utf-8")
        return InvestigationResult(
            run_id=run_dir.name,
            mode=mode,
            ledger_path=ledger,
            final_state={},
            halted_reason=None,
            manifest_path=manifest,
            experiment_arm_path=None,
        )

    monkeypatch.setattr(
        "graphdebug.services.experiment.runner.run_investigation",
        fake_run,
    )
    cfg = load_config(project_root=tmp_path, require_api_key=True)
    bug = BugTask(target_root="/t", failing_tests=("x::y",), symptom="s")
    res = run_token_experiment(bug, cfg, write_artifacts=True)
    assert res.report_path.is_file()
    assert res.chart_path.is_file()
    assert res.kpis.meets_token_kpi


def test_run_token_experiment_respects_write_artifacts_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_minimal_project_config(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    def fake_run(
        bug_task: BugTask,
        mode: str,
        config: AppConfig,
        **_: object,
    ) -> InvestigationResult:
        run_dir = config.paths["results"] / f"z-{mode}"
        run_dir.mkdir(parents=True, exist_ok=True)
        manifest = run_dir / "manifest.json"
        manifest.write_text(
            json.dumps(
                manifest_row(mode, run_dir.name, total_tokens=100, files_read=1, iterations=1),
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
    cfg = load_config(project_root=tmp_path, require_api_key=True)
    bug = BugTask(target_root="/t", failing_tests=("a::b",), symptom="s")
    res = run_token_experiment(bug, cfg, write_artifacts=False)
    assert not res.report_path.is_file()


def test_experiment_public_package_exports() -> None:
    import graphdebug.services.experiment as pkg

    assert callable(pkg.run_token_experiment)
