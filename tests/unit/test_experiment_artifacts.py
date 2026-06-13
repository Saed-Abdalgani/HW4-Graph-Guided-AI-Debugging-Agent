"""Markdown report + matplotlib chart for token comparison (Phase 8)."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.experiment.chart import write_token_comparison_chart
from graphdebug.services.experiment.kpis import evaluate_kpis
from graphdebug.services.experiment.report_md import write_token_comparison_markdown
from graphdebug.services.experiment.types import ArmMetrics


def test_write_token_comparison_markdown_and_chart(tmp_path: Path) -> None:
    naive = ArmMetrics(
        "naive",
        "n",
        4000,
        6000,
        10000,
        2,
        20,
        3,
        9.0,
        True,
        True,
        False,
    )
    graph = ArmMetrics(
        "graph",
        "g",
        1000,
        2000,
        3000,
        1,
        5,
        2,
        4.0,
        True,
        True,
        False,
    )
    kpis = evaluate_kpis(naive, graph)
    rp = tmp_path / "token_comparison.md"
    write_token_comparison_markdown(
        rp,
        naive=naive,
        graph=graph,
        kpis=kpis,
        naive_cost_usd=0.01,
        graph_cost_usd=0.002,
        model_name="stub",
        temperature=0.0,
        seed_repr="42",
    )
    text = rp.read_text(encoding="utf-8")
    assert "10000" in text and "3000" in text and "RQ6" in text
    png = tmp_path / "c.png"
    write_token_comparison_chart(naive, graph, png)
    assert png.is_file() and png.stat().st_size > 100


def test_write_token_comparison_includes_deviation_section(tmp_path: Path) -> None:
    naive = ArmMetrics(
        mode="naive",
        run_id="n",
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        tool_calls=0,
        files_read=0,
        iterations=1,
        wall_seconds=1.0,
        has_hypothesis=False,
        has_patch=False,
        verified=False,
    )
    graph = ArmMetrics(
        mode="graph",
        run_id="g",
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2,
        tool_calls=0,
        files_read=1,
        iterations=1,
        wall_seconds=1.0,
        has_hypothesis=False,
        has_patch=False,
        verified=False,
    )
    kpis = evaluate_kpis(naive, graph)
    rp = tmp_path / "out.md"
    write_token_comparison_markdown(
        rp,
        naive=naive,
        graph=graph,
        kpis=kpis,
        naive_cost_usd=0.0,
        graph_cost_usd=0.0,
        model_name="m",
        temperature=0.0,
        seed_repr="0",
    )
    assert "Deviation" in rp.read_text(encoding="utf-8")
