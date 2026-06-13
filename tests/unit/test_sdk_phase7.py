"""Exercise ``sdk.phase7`` helpers against a minimal config tree."""
from __future__ import annotations
import textwrap
from pathlib import Path
import pytest

_MINIMAL_YAML = (
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


def _write_minimal_config(root: Path) -> None:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "default.yaml").write_text(_MINIMAL_YAML, encoding="utf-8")
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "results").mkdir(parents=True, exist_ok=True)
    (root / "obsidian").mkdir(parents=True, exist_ok=True)


def test_merge_bug_analysis_report(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    (tmp_path / "reports" / "bug_analysis.md").write_text(
        "## Hypothesis / root cause\n\n_TBD (Phase 6)._\n\n## Fix summary\n\n_TBD (Phase 7)._\n\n"
        "## Verification\n\n_TBD: red → green log, regression note._\n",
        encoding="utf-8",
    )
    from graphdebug.sdk.phase7 import merge_bug_analysis_report

    merge_bug_analysis_report(
        hypothesis="Encoding.",
        fix_summary="UTF-8 open.",
        verification="pytest green.",
        project_root=tmp_path,
    )
    text = (tmp_path / "reports" / "bug_analysis.md").read_text(encoding="utf-8")
    assert "Encoding." in text
    assert "_TBD (Phase 6)._" not in text


def test_scaffold_patch_comparison(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    a = tmp_path / "a.patch"
    b = tmp_path / "b.patch"
    a.write_text("x", encoding="utf-8")
    b.write_text("yy", encoding="utf-8")
    from graphdebug.sdk.phase7 import scaffold_patch_comparison

    out = scaffold_patch_comparison(a, b, project_root=tmp_path)
    assert out.is_file()


def test_write_vault_knowledge_delta(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    before = tmp_path / "results" / "knowledge_snapshots" / "before"
    after = tmp_path / "results" / "knowledge_snapshots" / "after"
    before.mkdir(parents=True)
    after.mkdir(parents=True)
    (before / "manifest.json").write_text('{"files": []}', encoding="utf-8")
    (after / "manifest.json").write_text('{"files": ["hot.md"]}', encoding="utf-8")
    from graphdebug.sdk.phase7 import write_vault_knowledge_delta

    p = write_vault_knowledge_delta(project_root=tmp_path)
    assert "hot.md" in p.read_text(encoding="utf-8")


def test_capture_after_knowledge_snapshot(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    (tmp_path / "obsidian" / "hot.md").write_text("# h\n", encoding="utf-8")
    from graphdebug.sdk.phase7 import capture_after_knowledge_snapshot

    dest = capture_after_knowledge_snapshot(project_root=tmp_path)
    assert (dest / "hot.md").is_file()

def test_apply_approved_patch_no_git(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    sub = tmp_path / "subject"
    sub.mkdir()
    diff = tmp_path / "p.diff"
    diff.write_text("--- a/x\n+++ b/x\n", encoding="utf-8")

    def _noop(_root: Path, _t: str) -> None:
        return None

    monkeypatch.setattr(
        "graphdebug.services.fixverify.apply.apply_unified_diff_git",
        _noop,
    )
    from graphdebug.sdk.phase7 import apply_approved_patch

    out = apply_approved_patch(diff, sub, project_root=tmp_path)
    assert out.name == "fix.diff"

def test_run_phase7_verification_sdk(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text("def test_x():\n    assert 1\n", encoding="utf-8")
    from graphdebug.sdk.phase7 import run_phase7_verification

    res = run_phase7_verification(
        tmp_path,
        ("tests/t.py::test_x",),
        project_root=tmp_path,
        baseline_red=None,
        suite_args=(),
    )
    assert res.target_tests_passed