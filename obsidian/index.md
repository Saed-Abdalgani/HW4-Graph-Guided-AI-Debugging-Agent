# graphdebug vault — index

> **HW4** graph-guided debugging. Phase 1 target: **BugsInPy — PySnooper bug 1** (UTF-8 / non-ASCII snoop output).

## Working set

- **Subject layout**: `data/pysnooper-bugsinpy-1/SETUP.md` (clone + `uv` commands).
- **Isolated test env**: `data/pysnooper-subject-env/` (separate `uv.lock`; not merged into `graphdebug`).
- **Baseline evidence**: `results/baseline_red.txt`
- **Structured metadata**: `reports/bug_analysis.md`
- **Live investigation scratchpad**: [[hot]]

## Navigation (upcoming phases)

| Phase | Artifact |
|-------|-----------|
| 2 | `artifacts/graphify/` (`graph.json`, report, vault export) |
| 3 | Component / suspect pages (vault builder) |
| 4 | `assets/` diagrams + `reports/architecture.md` |
| 5–6 | LangGraph run logs + hypothesis in `reports/bug_analysis.md` |

## Requirements map (quick)

- **Selection / justification**: root `README.md` § “Target repository & bug”.
- **RQ5** (how found / root cause): `reports/bug_analysis.md` + [[hot]].
