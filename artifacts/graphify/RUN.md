# Graphify Run

## Tool

- Package: `graphifyy`
- CLI version: `0.8.35`
- Runner: `uvx --from graphifyy ...`
- Date: 2026-06-07
- Repo commit at run time: `d9b8a19`

## Scope

Graphify was run on a temporary staged copy of the selected PySnooper bug subject:

- `pysnooper/`
- `tests/`
- `setup.py`

The staged copy was created from `data/pysnooper-bugsinpy-1/src`. A direct scan of the
`data/...` path produced an empty graph with this Graphify build, so the exact relevant
subtree was copied to `%TEMP%\graphdebug-pysnooper-graphify` before extraction. Graphify's
manifest and node `source_file` values remain relative to the PySnooper subtree.

## Commands

```powershell
$scanRoot = Join-Path $env:TEMP 'graphdebug-pysnooper-graphify'
New-Item -ItemType Directory -Path $scanRoot | Out-Null
Copy-Item -LiteralPath 'data\pysnooper-bugsinpy-1\src\pysnooper' `
  -Destination (Join-Path $scanRoot 'pysnooper') -Recurse
Copy-Item -LiteralPath 'data\pysnooper-bugsinpy-1\src\tests' `
  -Destination (Join-Path $scanRoot 'tests') -Recurse
Copy-Item -LiteralPath 'data\pysnooper-bugsinpy-1\src\setup.py' `
  -Destination (Join-Path $scanRoot 'setup.py')

uvx --from graphifyy graphify extract $scanRoot --out artifacts --max-workers 1 --no-cluster
uvx --from graphifyy graphify cluster-only artifacts --graph artifacts\graphify-out\graph.json --no-label
uvx --from graphifyy graphify export obsidian --graph artifacts\graphify-out\graph.json --dir artifacts\graphify-out\obsidian
```

The generated `artifacts\graphify-out` directory was then moved to `artifacts\graphify`.

## Outputs

- `graph.json`: source-of-truth extracted graph, 150 raw nodes and 462 raw edges.
- `graph.html`: browsable Graphify visualization.
- `GRAPH_REPORT.md`: Graphify community and hub report.
- `obsidian/`: Graphify-exported Obsidian vault, including `graph.canvas`.
- `manifest.json`: source file hashes for the staged scan.

`cluster-only --no-label` produced `GRAPH_REPORT.md` and `graph.html` without LLM labels or
token spend. It refused to overwrite `graph.json` after clustering because duplicate external
symbol collapse would reduce the graph from 150 raw nodes to 149 unique ids. The project loader
therefore preserves the extraction graph and records duplicate ids during load.

This Graphify release exposes the Obsidian output through `graphify export obsidian`; that is the
version-specific equivalent of the documented `--obsidian` artifact generation.
