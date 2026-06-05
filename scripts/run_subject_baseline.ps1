# Re-run the Phase 1 red baseline for the BugsInPy PySnooper subject (Windows-oriented).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "data\pysnooper-subject-env")
Remove-Item Env:PYTHONUTF8 -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue
$env:PYTHONHASHSEED = "0"
$out = Join-Path $root "results\baseline_red.txt"
New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
$output = uv run pytest -vv "..\pysnooper-bugsinpy-1\src\tests\test_chinese.py::test_chinese" 2>&1
$code = $LASTEXITCODE
$header = @"
graphdebug - Phase 1 red baseline (BugsInPy PySnooper / bug 1)
Captured: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') (local)
Command: uv run pytest -vv ..\pysnooper-bugsinpy-1\src\tests\test_chinese.py::test_chinese
CWD: data/pysnooper-subject-env
Env: PYTHONHASHSEED=0; PYTHONUTF8 unset (Windows cp1252 repro)

"@
Set-Content -Path $out -Value $header -Encoding utf8
$output | Add-Content -Path $out -Encoding utf8
exit $code
