"""CLI wiring for ``phase7``."""

from __future__ import annotations

from pathlib import Path

import pytest

from graphdebug.cli_phase7 import run_phase7_cli

from .cli_phase7_fixtures import phase7_namespace, write_minimal_phase7_project


def test_run_phase7_review_patch(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    d = tmp_path / "p.diff"
    d.write_text("--- a/x\n+++ b/x\n@@\n+encoding=utf-8\n", encoding="utf-8")
    run_phase7_cli(
        phase7_namespace(
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
    write_minimal_phase7_project(tmp_path)
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
        phase7_namespace(
            p7_step="merge-docs",
            project_root=tmp_path,
            hypothesis_file=hf,
            fix_file=ff,
            verification_file=vf,
        )
    )
    assert "phase7 merge-docs" in capsys.readouterr().out


def test_run_phase7_snapshot_after(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    write_minimal_phase7_project(tmp_path)
    (tmp_path / "obsidian" / "z.md").write_text("# z", encoding="utf-8")
    run_phase7_cli(phase7_namespace(p7_step="snapshot-after", project_root=tmp_path))
    assert "snapshot-after" in capsys.readouterr().out


def test_run_phase7_vault_diff(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    write_minimal_phase7_project(tmp_path)
    before = tmp_path / "results" / "knowledge_snapshots" / "before"
    after = tmp_path / "results" / "knowledge_snapshots" / "after"
    before.mkdir(parents=True)
    after.mkdir(parents=True)
    (before / "manifest.json").write_text('{"files":[]}', encoding="utf-8")
    (after / "manifest.json").write_text('{"files":["z.md"]}', encoding="utf-8")
    run_phase7_cli(phase7_namespace(p7_step="vault-diff", project_root=tmp_path))
    assert "vault-diff" in capsys.readouterr().out
