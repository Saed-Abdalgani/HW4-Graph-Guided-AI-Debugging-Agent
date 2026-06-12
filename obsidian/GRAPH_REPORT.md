# Graph Report - artifacts  (2026-06-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 149 nodes · 407 edges · 16 communities (15 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9b8a192`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `VariableEntry` - 34 edges
2. `ReturnValueEntry` - 32 edges
3. `assert_output()` - 29 edges
4. `CallEntry` - 28 edges
5. `LineEntry` - 28 edges
6. `ReturnEntry` - 28 edges
7. `Tracer` - 14 edges
8. `CommonVariable` - 14 edges
9. `_BaseEventEntry` - 12 edges
10. `BaseVariable` - 9 edges

## Surprising Connections (you probably didn't know these)
- `test_truncate()` --calls--> `truncate()`  [EXTRACTED]
  tests/test_pysnooper.py → pysnooper/utils.py
- `test_needs_parentheses()` --calls--> `needs_parentheses()`  [EXTRACTED]
  tests/test_pysnooper.py → pysnooper/variables.py
- `UnavailableSource` --uses--> `CommonVariable`  [INFERRED]
  pysnooper/tracer.py → pysnooper/variables.py
- `FileWriter` --uses--> `CommonVariable`  [INFERRED]
  pysnooper/tracer.py → pysnooper/variables.py
- `Tracer` --uses--> `BaseVariable`  [INFERRED]
  pysnooper/tracer.py → pysnooper/variables.py

## Import Cycles
- None detected.

## Communities (16 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (10): Exception, needs_parentheses(), test_needs_parentheses(), _BaseEntry, _BaseEventEntry, _BaseValueEntry, ExceptionEntry, get_function_arguments() (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.34
Nodes (20): test_cellvars(), test_confusing_decorator_lines(), test_depth(), test_file_output(), test_generator(), test_lambda(), test_long_variable(), test_method_and_prefix() (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (10): ABC, PathLike, Helper class that provides a standard way to create an ABC using         inheri, Abstract base class for implementing the file system path protocol., Return the file system path representation of the object., _check_methods(), get_shortish_repr(), truncate() (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.28
Nodes (7): object, FileWriter, get_source_from_frame(), get_write_function(), UnavailableSource, BaseVariable, Exploding

### Community 4 - "Community 4"
Cohesion: 0.25
Nodes (3): get_local_reprs(), Snoop on the function, writing everything it's doing to stderr.      This is u, Tracer

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (3): Attrs, Indices, Keys

### Community 7 - "Community 7"
Cohesion: 0.32
Nodes (3): test_callable(), test_unavailable_source(), VariableEntry

### Community 8 - "Community 8"
Cohesion: 0.47
Nodes (5): bar(), foo(), main(), test_chinese(), test_with_block()

### Community 9 - "Community 9"
Cohesion: 0.60
Nodes (5): f2(), f3(), f4(), f5(), main()

### Community 10 - "Community 10"
Cohesion: 0.47
Nodes (4): test_exception(), test_indentation(), test_single_watch_no_comma(), assert_sample_output()

### Community 11 - "Community 11"
Cohesion: 0.40
Nodes (4): test_overwrite(), test_thread_info(), test_variables_classes(), ReturnValueEntry

### Community 12 - "Community 12"
Cohesion: 0.83
Nodes (3): factorial(), main(), mul()

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CommonVariable` connect `Community 6` to `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `VariableEntry` connect `Community 7` to `Community 0`, `Community 1`, `Community 8`, `Community 10`, `Community 11`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `Tracer` connect `Community 4` to `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **What connects `Helper class that provides a standard way to create an ABC using         inheri`, `Abstract base class for implementing the file system path protocol.`, `Return the file system path representation of the object.` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._