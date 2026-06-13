"""Bar chart for token + file comparison (Phase 8, T8.4)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from graphdebug.services.experiment.types import ArmMetrics


def write_token_comparison_chart(naive: ArmMetrics, graph: ArmMetrics, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = ("Total\ntokens", "Files\nread")
    n_vals = (naive.total_tokens, naive.files_read)
    g_vals = (graph.total_tokens, graph.files_read)
    x = (0, 1)
    w = 0.35
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([i - w / 2 for i in x], n_vals, width=w, label="naive", color="#6baed6")
    ax.bar([i + w / 2 for i in x], g_vals, width=w, label="graph", color="#74c476")
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("count")
    ax.set_title("Naive vs graph — tokens & files read (ledger)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


__all__ = ["write_token_comparison_chart"]
