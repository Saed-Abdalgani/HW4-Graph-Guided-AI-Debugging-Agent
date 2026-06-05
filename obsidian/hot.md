# hot — active investigation

> Short, high-signal working notes. Update every iteration (per `todo.md` **T3.2**).

## Symptom

- `tests/test_chinese.py::test_chinese` **fails** on buggy PySnooper when logging non-ASCII variable values.
- **Exception**: `UnicodeEncodeError: 'charmap' codec can't encode characters ...` under Windows **cp1252** (see `results/baseline_red.txt`).
- **Repro**: `data/pysnooper-bugsinpy-1/SETUP.md` + `scripts/run_subject_baseline.ps1`.

## Suspects (ranked)

1. `pysnooper/tracer.py` — `FileWriter.write` / `open(...)` encoding for the log file.
2. `pysnooper/tracer.py` — `get_source_from_frame` default encoding when source lines are `bytes` (related UTF-8 hardening in official patch).
3. `tests/utils.py` — unicode string templates (secondary; appears in BugsInPy patch but not primary crash here).

## Checked

- [x] Red baseline reproduced (subject `uv` env, **not** `graphdebug` root env).
- [x] Confirmed **deterministic** failure class across immediate re-runs with `PYTHONHASHSEED=0` and UTF-8 mode **unset**.

## Root cause

_TBD — do not consult BugsInPy `bug_patch.txt` until Phase 7 validation._

## Fix

_TBD._

## Next action

- Phase 2: run Graphify on `data/pysnooper-bugsinpy-1/src` (scoped), persist under `artifacts/graphify/`.
