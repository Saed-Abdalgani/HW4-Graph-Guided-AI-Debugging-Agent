# Phase 6 — graph-guided investigation runs

Each `graphdebug investigate --mode graph` (or SDK `investigate(..., "graph")`) produces:

| Artifact | Location |
|---|---|
| Token ledger (JSONL) | `results/<run_id>/ledger.jsonl` |
| Run log (scribe steps) | `results/<run_id>/run.log` |
| Machine-readable summary | `results/<run_id>/manifest.json` |
| Phase 8 archive (tagged arm) | `results/experiment_arms/graph/<run_id>/` (copy of ledger + manifest + log) |
| Latest run pointer | `results/experiment_arms/graph/LATEST` (contains last `run_id`) |

`obsidian/hot.md` is updated by the scribe with suspects, **Checked** (pipeline flags), root cause hypothesis, proposed diff, and next action.

Example (from graphdebug repo root, with API key in `.env`):

```bash
uv run graphdebug investigate --mode graph ^
  --target-root data/<target> ^
  --test tests/test_file.py::test_case ^
  --symptom "Short symptom" ^
  --assume-hitl-ack
```

Replace paths with your subject repo and failing node ids from Phase 1. Prefer a single controlled re-run after inspecting `manifest.json` if the workflow halts (`halted_reason`).
