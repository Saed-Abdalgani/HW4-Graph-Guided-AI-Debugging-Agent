# graphdebug vault — index

> **HW4** graph-guided debugging. Target: **BugsInPy — PySnooper bug 1** (UTF-8 / non-ASCII snoop output).

## Start here

- **Live scratchpad:** [[hot]]
- **Graph narrative (Graphify copy):** [[GRAPH_REPORT]]
- **Architecture (stub → Phase 4 diagrams):** [[Architecture]]
- **God nodes (stub → Phase 4 metrics):** [[God nodes]]
- **Suspect hub:** [[suspects/FileWriter encoding|FileWriter encoding]]
- **Seeded finding:** [[findings/UTF-8 log path|UTF-8 log path]]

## Bug-1 graph focus (generated)

- [[generated/pysnooper_tracer_filewriter|FileWriter (`pysnooper_tracer_filewriter`)]]
- [[generated/pysnooper_tracer_filewriter_write|`.write()` (`pysnooper_tracer_filewriter_write`)]]
- [[generated/tests_test_chinese|Test module (`tests_test_chinese`)]]
- [[generated/tests_test_chinese_test_chinese|Failing test (`tests_test_chinese_test_chinese`)]]

## Repo paths (outside Obsidian)

- `data/pysnooper-bugsinpy-1/SETUP.md` — subject checkout + `uv`
- `results/baseline_red.txt` — red baseline log
- `reports/bug_analysis.md` — metadata + future hypothesis

## Regenerate

- `uv run graphdebug vault-build` — refresh `generated/`, stubs, and in-vault `GRAPH_REPORT.md` copy
- `uv run graphdebug vault-build --snapshot` — also capture `results/knowledge_snapshots/before/`
