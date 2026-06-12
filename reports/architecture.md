# Architecture insight (RQ1, RQ4)

## RQ1 — What the code *really* does vs first glance

At first glance PySnooper reads like a small decorator around `sys.settrace`. The Graphify
graph shows a denser **runtime composition**: `Tracer` coordinates frame filtering, thread
padding, output sinks, and variable formatting across modules — not a single linear script.
The **block diagram** (`assets/architecture.png`) collapses thousands of AST nodes into
**Louvain communities** on the *structural* edge slice (imports / calls / contains), so blocks
reflect coupling topology rather than directory names.

## RQ4 — How diagrams were extracted when docs are thin

Official docs emphasize the public decorator API; they do not spell out every composition edge.
We derived structure from `graph.json` **relations** (confidence `EXTRACTED` where present),
then **spot-checked** a few `inherits` / `contains` chains (e.g., `PathLike` → `ABC` in
`pycompat.py`) against the subject source. Semantic / LLM-labeled edges in the artifact were
treated skeptically; the OOP diagram prefers the **inherits / contains / uses / method** slice.

## Block model summary

- **Communities detected**: 36
- **Strongest cross-block links (relation, weight)**:

- `B7 (n=28)
test_pysnooper.py, utils.py` → `B8 (n=8)
test_pysnooper.py, utils.py, variables.py` — **contains** (weight 22.0)
- `B3 (n=6)
exception.py, test_chinese.py, test_pysnooper.py` → `B7 (n=28)
test_pysnooper.py, utils.py` — **calls** (weight 12.0)
- `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` → `B7 (n=28)
test_pysnooper.py, utils.py` — **contains** (weight 6.0)
- `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` → `B7 (n=28)
test_pysnooper.py, utils.py` — **imports** (weight 6.0)
- `B7 (n=28)
test_pysnooper.py, utils.py` → `B8 (n=8)
test_pysnooper.py, utils.py, variables.py` — **imports** (weight 6.0)
- `B0 (n=22)
__init__.py, tracer.py, variables.py` → `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` — **imports_from** (weight 5.0)
- `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` → `B8 (n=8)
test_pysnooper.py, utils.py, variables.py` — **imports** (weight 5.0)
- `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` → `B8 (n=8)
test_pysnooper.py, utils.py, variables.py` — **imports_from** (weight 2.0)
- `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` → `B8 (n=8)
test_pysnooper.py, utils.py, variables.py` — **contains** (weight 2.0)
- `B0 (n=22)
__init__.py, tracer.py, variables.py` → `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` — **imports** (weight 1.0)
- `B0 (n=22)
__init__.py, tracer.py, variables.py` → `B8 (n=8)
test_pysnooper.py, utils.py, variables.py` — **contains** (weight 1.0)
- `B3 (n=6)
exception.py, test_chinese.py, test_pysnooper.py` → `B6 (n=22)
pycompat.py, test_chinese.py, test_pysnooper.py` — **contains** (weight 1.0)

## What was not obvious before the graph

- Test utilities and helpers attach to the same import hub as core tracing, so regressions can
  surface far from the failing test file.
- Output encoding concerns (`FileWriter`) sit on a high-traffic path between formatting and I/O,
  which centrality ranks near the top even before reading implementation details.

## Assets

- `assets/architecture.png` / `architecture.mmd` — subsystem graph.
- `assets/oop.png` / `oop.mmd` — OOP relation slice (trimmed for readability).
