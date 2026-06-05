# PySnooper — BugsInPy bug 1 (subject setup)

This folder is the **graphdebug subject workspace** for
[BugsInPy](https://github.com/soarsmu/BugsInPy) **PySnooper / bug 1** (UTF-8 logging).

- **Upstream**: [cool-RR/PySnooper](https://github.com/cool-RR/PySnooper)
- **Buggy commit**: `e21a31162f4c54be693d8ca8260e42393b39abd3`
- **Fixed commit (ground truth, Phase 7 only)**: `56f22f8ffe1c6b2be4d2cf3ad1987fdb66113da2`
- **BugsInPy metadata**: `projects/PySnooper/bugs/1/` in the BugsInPy repo

## Layout

| Path | Purpose |
|------|---------|
| `src/` | Git checkout of PySnooper at the **buggy** commit (ignored by git; clone here). |
| `../pysnooper-subject-env/` | **Isolated `uv` environment** for pytest + deps (not part of `graphdebug`’s root `uv.lock`). |

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) installed.
- One-time Python fetch for the subject: `uv python install 3.8` (matches BugsInPy metadata for this bug).

## One-time clone (buggy tree)

From the **repository root** (`HW4-Graph-Guided AI Debugging Agent/`):

```powershell
git clone https://github.com/cool-RR/PySnooper.git "data/pysnooper-bugsinpy-1/src"
Set-Location "data/pysnooper-bugsinpy-1/src"
git fetch --depth 1 origin e21a31162f4c54be693d8ca8260e42393b39abd3
git checkout e21a31162f4c54be693d8ca8260e42393b39abd3
```

## Add the failing regression test (BugsInPy harness)

The regression test lives on the **fixed** branch in upstream; BugsInPy’s harness expects it while the **buggy** code remains unfixed. Materialize it **without** applying the fix:

```powershell
Set-Location "data/pysnooper-bugsinpy-1/src"
cmd /c "git show 56f22f8ffe1c6b2be4d2cf3ad1987fdb66113da2:tests/test_chinese.py > tests\test_chinese.py"
```

## Isolated environment (`uv` only)

```powershell
Set-Location "data/pysnooper-subject-env"
uv sync
```

Uses **Python 3.8.x** (see `.python-version`) to match the BugsInPy-era codebase.

## Red baseline (must fail)

**Windows**: do **not** enable global UTF-8 (`PYTHONUTF8=1`); with UTF-8 mode the test may pass before the code fix.

```powershell
Set-Location "data/pysnooper-subject-env"
Remove-Item Env:PYTHONUTF8 -ErrorAction SilentlyContinue
$env:PYTHONHASHSEED = "0"
uv run pytest -vv "..\pysnooper-bugsinpy-1\src\tests\test_chinese.py::test_chinese"
```

Expected: `UnicodeEncodeError: 'charmap' codec can't encode characters` when the default Windows console encoding is **cp1252** (typical US English).

Full captured output (Phase 1 evidence): `results/baseline_red.txt`.

## Optional: repo script

From the repo root:

```powershell
./scripts/run_subject_baseline.ps1
```
