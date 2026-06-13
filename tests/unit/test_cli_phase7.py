"""CLI wiring for ``phase7``."""
from __future__ import annotations
import argparse
import textwrap
from pathlib import Path
import pytest
from graphdebug.cli_phase7 import run_phase7_cli
_MIN = (
    textwrap.dedent(
        """
        llm:
          provider: openai
          model: gpt-4o-mini
          temperature: 0.0
          max_output_tokens: 256
        gatekeeper:
          requests_per_minute: 600
          tokens_per_minute: 900000
          max_retries: 1
          backoff_base_seconds: 0.01
          max_backoff_seconds: 0.05
          queue_size: 8
        budgets:
          graph:
            max_tokens: 50000
            max_tool_calls: 50
            max_files: 20
            max_iterations: 30
          naive:
            max_tokens: 50000
            max_tool_calls: 50
            max_files: 20
            max_iterations: 30
        paths:
          graphify_artifacts: artifacts/graphify
          obsidian_vault: obsidian
          results: results
          data_root: data
          reports: reports
        retriever:
          max_lines_per_file: 40
          max_suspects_fetched: 3
        features:
          hitl_required: false
          enable_langsmith: false
        analysis:
          source_prefixes: ["pkg/"]
        """
    ).strip()
    + "\n"
)


def _minimal_project(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config" / "default.yaml").write_text(_MIN, encoding="utf-8")
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / "results").mkdir(parents=True, exist_ok=True)
    (tmp_path / "obsidian").mkdir(parents=True, exist_ok=True)


def _ns(**kwargs: object) -> argparse.Namespace:
    defaults: dict[str, object] = {
        "project_root": None,
        "diff": None,
        "target_root": None,
        "tests": None,
        "baseline_red": None,
        "suite_args": None,
        "ours": None,
        "official": None,
        "hypothesis_file": None,
        "fix_file": None,
        "verification_file": None,
        "hypothesis_inline": "",
        "fix_inline": "",
        "verification_inline": "",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_phase7_review_patch(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    d = tmp_path / "p.diff"
    d.write_text("--- a/x\n+++ b/x\n@@\n+encoding=utf-8\n", encoding="utf-8")
    run_phase7_cli(
        _ns(
            p7_step="review-patch",
            project_root=tmp_path,
            diff=d,
        )
    )
    out = capsys.readouterr().out
    assert "phase7 review-patch" in out


def test_cli_main_dispatches_phase7(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    p = tmp_path / "d.diff"
    p.write_text("--- a/f\n+++ b/f\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["graphdebug", "phase7", "review-patch", "--diff", str(p)])
    from graphdebug.cli import main

    main()


def test_run_phase7_merge_docs(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    _minimal_project(tmp_path)
    (tmp_path / "reports" / "bug_analysis.md").write_text(
        "## Hypothesis / root cause\n\n_TBD (Phase 6)._\n\n## Fix summary\n\n_TBD (Phase 7)._\n\n"
        "## Verification\n\n_TBD: red → green log, regression note._\n",
        encoding="utf-8",
    )
    hf = tmp_path / "h.txt"
    hf.write_text("hyp", encoding="utf-8")
    ff = tmp_path / "f.txt"
    ff.write_text("fix", encoding="utf-8")
    vf = tmp_path / "v.txt"
    vf.write_text("ver", encoding="utf-8")
    run_phase7_cli(
        _ns(
            p7_step="merge-docs",
            project_root=tmp_path,
            hypothesis_file=hf,
            fix_file=ff,
            verification_file=vf,
        )
    )
    assert "phase7 merge-docs" in capsys.readouterr().out


def test_run_phase7_snapshot_after(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    _minimal_project(tmp_path)
    (tmp_path / "obsidian" / "z.md").write_text("# z", encoding="utf-8")
    run_phase7_cli(_ns(p7_step="snapshot-after", project_root=tmp_path))
    assert "snapshot-after" in capsys.readouterr().out


def test_run_phase7_vault_diff(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    _minimal_project(tmp_path)
    before = tmp_path / "results" / "knowledge_snapshots" / "before"
    after = tmp_path / "results" / "knowledge_snapshots" / "after"
    before.mkdir(parents=True)
    after.mkdir(parents=True)
    (before / "manifest.json").write_text('{"files":[]}', encoding="utf-8")
    (after / "manifest.json").write_text('{"files":["z.md"]}', encoding="utf-8")
    run_phase7_cli(_ns(p7_step="vault-diff", project_root=tmp_path))
    assert "vault-diff" in capsys.readouterr().out
