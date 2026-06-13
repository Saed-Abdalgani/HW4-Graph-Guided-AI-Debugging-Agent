"""Tests for loading ``ArmMetrics`` from manifests (Phase 8)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphdebug.services.agents.result import InvestigationResult
from graphdebug.services.experiment.metrics import metrics_from_manifest, metrics_from_result
from tests.unit.experiment_fixtures import manifest_row


def test_metrics_from_manifest_uses_max_files(tmp_path: Path) -> None:
    m = tmp_path / "m.json"
    body = manifest_row("naive", "n1", total_tokens=100, files_read=3, iterations=1)
    body["ledger_aggregate"]["total_files_read"] = 5
    body["budget_final"] = {"files_read": 12}
    m.write_text(json.dumps(body), encoding="utf-8")
    am = metrics_from_manifest(m, wall_seconds=2.0)
    assert am.files_read == 12
    assert am.total_tokens == 100


def test_metrics_from_result_requires_manifest_file() -> None:
    inv = InvestigationResult(
        run_id="x",
        mode="graph",
        ledger_path=Path("nope.jsonl"),
        final_state={},
        halted_reason=None,
        manifest_path=None,
    )
    with pytest.raises(FileNotFoundError):
        metrics_from_result(inv, wall_seconds=0.0)


def test_metrics_from_result_reads_investigation_manifest(tmp_path: Path) -> None:
    m = tmp_path / "manifest.json"
    m.write_text(
        json.dumps(manifest_row("graph", "g1", total_tokens=50, files_read=2, iterations=1)),
        encoding="utf-8",
    )
    inv = InvestigationResult(
        run_id="g1",
        mode="graph",
        ledger_path=tmp_path / "l.jsonl",
        final_state={},
        halted_reason=None,
        manifest_path=m,
    )
    am = metrics_from_result(inv, wall_seconds=0.25)
    assert am.total_tokens == 50 and am.mode == "graph"
