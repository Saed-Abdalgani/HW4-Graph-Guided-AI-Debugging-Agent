# Sample impact report (T9.3)

Synthetic two-node graph:

- Edges: `app --imports--> lib`

Calling `impact_of(graph, "lib", max_hops=4)` returns **`("app",)`** — the importer would be affected if `lib` changes incompatibly.

On larger graphs, the tuple lists every node found within `max_hops` steps along **incoming** edges from the seed.
