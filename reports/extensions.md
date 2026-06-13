# Phase 9 — Extensions (RQ8)

This project adds **graph-backed extensions** beyond the core investigate / experiment flow. Each item has a **rationale**, a **callable API** (via `graphdebug.sdk.api`), and a **test** under `tests/unit/`.

## T9.1 — Suspect ranking (centrality + test proximity)

**Rationale:** Rank likely bug locations using graph centrality and shortest-path distance to nodes anchored on failing test paths (`FR-E1`, `RQ2`).

**API:** `rank_suspects(graph, failing_tests=..., source_prefixes=..., top_k=...)` (already used by `run_investigator` in graph mode).

**Example:**

```python
from graphdebug.sdk.api import load_code_graph, rank_suspects

g = load_code_graph(Path("artifacts/graphify/graph.json"))
for s in rank_suspects(
    g,
    failing_tests=("tests/test_x.py::test_demo",),
    source_prefixes=("pkg/",),
    top_k=5,
):
    print(s.node_id, s.score, s.why)
```

**Tests:** `tests/unit/test_suspect_rank.py`

**What we’d add next:** Weight relations by kind (test-only vs prod) and cap expensive path queries on huge graphs.

---

## T9.2 — Dynamic `hot.md` from git diff

**Rationale:** When you have a unified diff, map touched files to `source_file` nodes and inject a compact neighbor list into `hot.md` so humans see graph context without manual copy-paste (`FR-E2`).

**API:** `paths_from_diff`, `node_ids_for_paths`, `merge_git_diff_into_hot(hot_path, diff_text, graph)`

**Example:**

```python
from pathlib import Path
from graphdebug.sdk.api import load_code_graph, merge_git_diff_into_hot

g = load_code_graph(Path("artifacts/graphify/graph.json"))
diff = Path("reports/fix.diff").read_text(encoding="utf-8")
merge_git_diff_into_hot(Path("obsidian/hot.md"), diff, g)
```

**Tests:** `tests/unit/test_phase9_extensions.py` (`test_merge_git_diff_into_hot_updates`)

**Validation note:** Match quality depends on diff paths aligning with `source_file` strings in `graph.json`; re-run Graphify if paths drift.

---

## T9.3 — Impact report (reverse dependencies)

**Rationale:** Answer “what breaks if we change node X?” by walking **incoming** edges up to a hop budget (`FR-E4`).

**API:** `impact_of(graph, node_id, max_hops=8) -> tuple[str, ...]`

**Sample:** `reports/sample_impact.md`

**Tests:** `tests/unit/test_phase9_extensions.py` (`test_impact_of_finds_importer`)

**What we’d add next:** Relation filters (imports-only vs calls) and export to Obsidian `[[wikilinks]]`.

---

## T9.4 — Documentation vs graph signals

**Rationale:** Lightweight **red-flag** list when prose claims stability (“immutable”, “read-only”) but outgoing neighbors look side-effecting (`FR-E3`). This is heuristic, not proof.

**API:** `doc_graph_signals(graph) -> tuple[DocSignal, ...]`

**Tests:** `tests/unit/test_phase9_extensions.py` (`test_doc_graph_signals_flags_mismatch`)

**What we’d add next:** Parse real docstrings from the subject repo (budgeted reads) instead of relying on `documentation` attrs in the graph artifact.

---

## T9.5 — Architecture ego report

**Rationale:** Summarize relation mixes inside a small undirected ball around seeds — useful for before/after narratives around a fix (`FR-E5`, `RQ1`).

**API:** `architecture_ego_report(graph, seed_ids, hops=2) -> str` (Markdown)

**Tests:** `tests/unit/test_phase9_extensions.py` (`test_architecture_ego_report`)

**What we’d add next:** Diff two ego reports from two `graph.json` snapshots taken pre/post Graphify.

---

## Line-budget gate (G.6)

**API:** N/A — enforced by `tests/unit/test_file_line_limits.py` (≤ **150 non-blank** lines per `src/graphdebug/**/*.py` and `tests/**/*.py`).

Run (coverage is optional for this file only):  
`uv run pytest tests/unit/test_file_line_limits.py --no-cov -q`
