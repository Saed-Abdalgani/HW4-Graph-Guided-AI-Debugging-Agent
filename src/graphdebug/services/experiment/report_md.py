"""Write ``reports/token_comparison.md`` (Phase 8, T8.3 — RQ6/RQ7)."""

from __future__ import annotations

from pathlib import Path

from graphdebug.services.experiment.types import ArmMetrics, KPIResult


def _row(label: str, naive: str, graph: str) -> str:
    return f"| {label} | {naive} | {graph} |\n"


def write_token_comparison_markdown(
    path: Path,
    *,
    naive: ArmMetrics,
    graph: ArmMetrics,
    kpis: KPIResult,
    naive_cost_usd: float,
    graph_cost_usd: float,
    model_name: str,
    temperature: float,
    seed_repr: str,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tok_s = f"{kpis.token_savings_pct:.1f}%" if kpis.token_savings_pct is not None else "n/a"
    fil_s = f"{kpis.file_savings_pct:.1f}%" if kpis.file_savings_pct is not None else "n/a"
    lines = [
        "# Token comparison — naive vs graph-guided\n",
        "\n",
        "Controlled two-arm run: **same** bug task, model, temperature, and RNG seed; ",
        "arms differ only in **context strategy** (naive = unstructured file reads; ",
        "graph = vault + `graph.json` queries + budgeted retriever). ",
        "Numbers come from **ledger aggregates** in each run’s `manifest.json`.\n",
        "\n",
        "## Reproducibility\n",
        "\n",
        f"- Model: `{model_name}`\n",
        f"- Temperature: `{temperature}`\n",
        f"- Seed: `{seed_repr}` (passed to provider when supported)\n",
        f"- Naive run id: `{naive.run_id}`\n",
        f"- Graph run id: `{graph.run_id}`\n",
        "\n",
        "## Side-by-side metrics\n",
        "\n",
        "| Metric | Naive | Graph |\n",
        "|---|---:|---:|\n",
        _row("Total LLM tokens", str(naive.total_tokens), str(graph.total_tokens)),
        _row("Prompt tokens", str(naive.prompt_tokens), str(graph.prompt_tokens)),
        _row("Completion tokens", str(naive.completion_tokens), str(graph.completion_tokens)),
        _row("Tool calls (ledger)", str(naive.tool_calls), str(graph.tool_calls)),
        _row("Files read (max of ledger vs budget)", str(naive.files_read), str(graph.files_read)),
        _row("Workflow iterations", str(naive.iterations), str(graph.iterations)),
        _row("Wall time (s)", f"{naive.wall_seconds:.2f}", f"{graph.wall_seconds:.2f}"),
        _row("Root-cause hypothesis present", str(naive.has_hypothesis), str(graph.has_hypothesis)),
        _row("Candidate patch present", str(naive.has_patch), str(graph.has_patch)),
        _row("Verifier green", str(naive.verified), str(graph.verified)),
        "\n",
        "## Savings vs naive\n",
        "\n",
        f"- **Token savings**: {tok_s} (graph vs naive total tokens)\n",
        f"- **File-read savings**: {fil_s}\n",
        f"- **Iterations**: graph ≤ naive → **{kpis.iteration_ok}**\n",
        "\n",
        "## KPI verdict (`prd.md` §6)\n",
        "\n",
        f"- ≥50% token reduction: **{kpis.meets_token_kpi}**\n",
        f"- ≥50% file-read reduction: **{kpis.meets_file_kpi}**\n",
        f"- Iterations (graph not higher than naive): **{kpis.meets_iteration_kpi}**\n",
        "\n",
        "## Estimated cost (config `experiment.*`)\n",
        "\n",
        f"- Naive: **${naive_cost_usd:.6f}**\n",
        f"- Graph: **${graph_cost_usd:.6f}**\n",
        "\n",
        "## RQ6 — Advantage of graph / Obsidian vs linear reading?\n",
        "\n",
        "Graph mode routes investigators through **graph queries and vault summaries** before ",
        "opening source, which caps file reads and trims prompts versus the naive arm’s ",
        "baseline of broad file access without structural context.\n",
        "\n",
        "## RQ7 — How did graph-guided work save tokens?\n",
        "\n",
        "Savings are measured as **fewer cumulative prompt+completion tokens** in the graph ",
        "ledger than in the naive ledger for the same task. ",
        "Mechanistically, graph mode spends tokens on **orientation and ranked suspects** ",
        "from the code graph instead of paying for repeated whole-file reads.\n",
        "\n",
    ]
    if kpis.notes:
        lines.append("## Deviation / caveats\n\n")
        for n in kpis.notes:
            lines.append(f"- {n}\n")
        lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")
    return path


__all__ = ["write_token_comparison_markdown"]
