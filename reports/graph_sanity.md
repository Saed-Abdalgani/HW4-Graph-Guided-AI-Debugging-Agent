# Graph Sanity Check

Phase 2 validation for `artifacts/graphify/graph.json`.

## Counts

| Metric | Value |
|---|---:|
| Raw nodes in `graph.json` | 150 |
| Unique queryable node ids | 149 |
| Raw/queryable edges | 462 |
| Hyperedges | 0 |
| Dangling edges | 46 |
| Isolated nodes | 1 |

## Schema Notes

- Graphify 0.8.35 emits `{nodes, edges, hyperedges, input_tokens, output_tokens}`.
- Edge endpoints use `source` and `target`.
- The raw graph contains two identical external `object` nodes. The loader merges duplicate ids
  for stable lookups and records `duplicate_node_ids = {"object": 2}` in graph metadata.
- `GRAPH_REPORT.md` is derived from Graphify's clustered projection and reports 149 nodes and
  407 edges; `graph.json` remains the immutable extraction artifact with 462 raw edges.

## Relation Counts

| Relation | Count |
|---|---:|
| calls | 193 |
| contains | 76 |
| imports | 74 |
| method | 54 |
| imports_from | 29 |
| inherits | 20 |
| uses | 10 |
| rationale_for | 4 |
| re_exports | 2 |

## Dangling And Isolated Nodes

- Dangling edges: 46, primarily imports to standard-library or third-party symbols that are not
  modeled as nodes, such as `collections`, `os`, `inspect`, `sys`, and `pytest`.
- Isolated node: `samples_init`, the empty `tests/samples/__init__.py` module.

## Verification

```powershell
uv run graphdebug graphify-load --in artifacts\graphify\graph.json
uv run pytest --cov=src
uv run ruff check .
```

Observed CLI summary:

```text
nodes=149 edges=462 hyperedges=0 dangling=46 isolated=1
```
