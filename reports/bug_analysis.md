# Bug analysis — PySnooper (BugsInPy #1)

> **Status**: Phase 1 — baseline red confirmed. Root cause / fix sections are placeholders until Phase 6–7.

## Metadata

| Field | Value |
|-------|--------|
| **Benchmark** | [BugsInPy](https://github.com/soarsmu/BugsInPy) |
| **Project** | PySnooper ([cool-RR/PySnooper](https://github.com/cool-RR/PySnooper)) |
| **Bug id** | `PySnooper` / **1** |
| **Buggy commit** | `e21a31162f4c54be693d8ca8260e42393b39abd3` |
| **Fixed commit (validation only)** | `56f22f8ffe1c6b2be4d2cf3ad1987fdb66113da2` |
| **Failing test** | `tests/test_chinese.py::test_chinese` |
| **BugsInPy `run_test.sh`** | `pytest -q -s tests/test_chinese.py::test_chinese` |

## Symptom (Phase 1 — observed)

- **Type**: `UnicodeEncodeError`
- **Codec**: `charmap` / **cp1252** (typical Windows code page when UTF-8 mode is off)
- **Where**: Writing snoop log lines that contain non-ASCII variable text (Chinese characters **失败**) in `pysnooper.tracer.FileWriter.write` → `open(...).write(...)`.
- **Evidence**: `results/baseline_red.txt` (two manual re-runs were identical in failure class before capture).

### Reproducibility notes

- **PYTHONUTF8=1** (or global “Beta: Use Unicode UTF-8 for worldwide language support”) can make the test **pass** on Windows even before the real fix — keep UTF-8 mode **off** for a honest red baseline on this OS.
- **Python version**: subject uses **3.8.x** per BugsInPy metadata; newer CPython removed `collections.Mapping` imports used by this vintage tree.

## Official ground truth (do not “solve from” this)

Per `todo.md` **T1.9**: the authoritative patch is published by BugsInPy for independent validation **after** our own investigation:

- Patch text: `https://raw.githubusercontent.com/soarsmu/BugsInPy/master/projects/PySnooper/bugs/1/bug_patch.txt`
- Upstream fixed commit: `https://github.com/cool-RR/PySnooper/commit/56f22f8ffe1c6b2be4d2cf3ad1987fdb66113da2`

## Hypothesis / root cause

_TBD (Phase 6)._

## Fix summary

_TBD (Phase 7)._

## Verification

_TBD: red → green log, regression note._
