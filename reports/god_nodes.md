# God nodes (centrality-backed)

## Method

- **Metrics**: directed betweenness (normalized) and weighted in/out degree on the subgraph induced by **imports**, **imports_from**, **calls**, and **contains** edges.
- **Scope**: nodes whose `source_file` matches prefixes `['pysnooper/', 'tests/']`.
- **Selection**: top `8` by betweenness, union nodes at or above the `92.0`th percentile of betweenness.
- **Rationale nodes** (`file_type` / kind = rationale) excluded from the metric graph.

## Ranked god nodes

| Node id | Label | Betweenness | Deg (in+out) | Why |
|---|---:|---:|---:|---|
| `tests_utils_assert_output` | assert_output() | 0.0054 | 29 | High betweenness (0.0054) on imports/calls/contains subgraph; weighted degree 29 (in 27, out 2). |
| `tests_utils_baseevententry_check` | .check() | 0.0029 | 3 | High betweenness (0.0029) on imports/calls/contains subgraph; weighted degree 3 (in 1, out 2). |
| `pysnooper_variables` | variables.py | 0.0021 | 16 | High betweenness (0.0021) on imports/calls/contains subgraph; weighted degree 16 (in 4, out 12). |
| `pysnooper_utils` | utils.py | 0.0015 | 13 | High betweenness (0.0015) on imports/calls/contains subgraph; weighted degree 13 (in 4, out 9). |
| `pysnooper_tracer` | tracer.py | 0.0013 | 14 | High betweenness (0.0013) on imports/calls/contains subgraph; weighted degree 14 (in 1, out 13). |
| `pysnooper_init` | __init__.py | 0.0012 | 10 | High betweenness (0.0012) on imports/calls/contains subgraph; weighted degree 10 (in 3, out 7). |
| `tests_utils` | utils.py | 0.0005 | 18 | High betweenness (0.0005) on imports/calls/contains subgraph; weighted degree 18 (in 2, out 16). |
| `pysnooper_pycompat` | pycompat.py | 0.0004 | 8 | High betweenness (0.0004) on imports/calls/contains subgraph; weighted degree 8 (in 5, out 3). |
| `samples_indentation` | indentation.py | 0.0003 | 6 | High betweenness (0.0003) on imports/calls/contains subgraph; weighted degree 6 (in 1, out 5). |
| `samples_indentation_f3` | f3() | 0.0002 | 3 | High betweenness (0.0002) on imports/calls/contains subgraph; weighted degree 3 (in 2, out 1). |
| `samples_recursion` | recursion.py | 0.0002 | 4 | High betweenness (0.0002) on imports/calls/contains subgraph; weighted degree 4 (in 1, out 3). |
| `samples_indentation_f4` | f4() | 0.0002 | 3 | High betweenness (0.0002) on imports/calls/contains subgraph; weighted degree 3 (in 2, out 1). |
| `samples_indentation_f2` | f2() | 0.0002 | 3 | High betweenness (0.0002) on imports/calls/contains subgraph; weighted degree 3 (in 2, out 1). |

## Top raw centrality (preview)

| Rank | Label | Betweenness | Closeness | deg_in | deg_out |
|---:|---|---:|---:|---:|---:|
| 1 | assert_output() | 0.0054 | 0.1929 | 27 | 2 |
| 2 | .check() | 0.0029 | 0.1018 | 1 | 2 |
| 3 | variables.py | 0.0021 | 0.0286 | 4 | 12 |
| 4 | utils.py | 0.0015 | 0.0298 | 4 | 9 |
| 5 | tracer.py | 0.0013 | 0.0095 | 1 | 13 |
| 6 | __init__.py | 0.0012 | 0.0127 | 3 | 7 |
| 7 | utils.py | 0.0005 | 0.0143 | 2 | 16 |
| 8 | pycompat.py | 0.0004 | 0.0389 | 5 | 3 |
| 9 | indentation.py | 0.0003 | 0.0071 | 1 | 5 |
| 10 | f3() | 0.0002 | 0.0190 | 2 | 1 |
| 11 | recursion.py | 0.0002 | 0.0071 | 1 | 3 |
| 12 | f4() | 0.0002 | 0.0198 | 2 | 1 |
| 13 | f2() | 0.0002 | 0.0161 | 2 | 1 |
| 14 | exception.py | 0.0001 | 0.0071 | 1 | 3 |
| 15 | test_chinese() | 0.0001 | 0.0071 | 1 | 7 |
| 16 | get_write_function() | 0.0001 | 0.0143 | 2 | 1 |
| 17 | get_source_from_frame() | 0.0001 | 0.0143 | 2 | 1 |
| 18 | factorial() | 0.0001 | 0.0161 | 2 | 1 |
| 19 | bar() | 0.0001 | 0.0161 | 2 | 1 |
| 20 | ._safe_keys() | 0.0001 | 0.0071 | 1 | 1 |
| 21 | ._check_content() | 0.0001 | 0.0071 | 1 | 1 |
| 22 | test_with_block() | 0.0000 | 0.0071 | 1 | 7 |
| 23 | test_pysnooper.py | 0.0000 | 0.0000 | 0 | 45 |
| 24 | VariableEntry | 0.0000 | 0.1929 | 27 | 0 |
| 25 | ReturnValueEntry | 0.0000 | 0.1929 | 27 | 0 |
