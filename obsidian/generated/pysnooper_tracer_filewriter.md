# FileWriter

> **Component** · graph node `pysnooper_tracer_filewriter`

| Field | Value |
| --- | --- |
| id | `pysnooper_tracer_filewriter` |
| kind | `code` |
| source_file | `pysnooper/tracer.py` |
| source_location | `L127` |

## Neighbors (graph)

- [[generated/pysnooper_tracer]] — **tracer.py** (`code`)
- [[generated/object]] — **object** (`code`)
- [[generated/pysnooper_tracer_filewriter_init]] — **.__init__()** (`code`)
- [[generated/pysnooper_tracer_filewriter_write]] — **.write()** (`code`)
- [[generated/pysnooper_tracer_get_write_function]] — **get_write_function()** (`code`)
- [[generated/pysnooper_variables_commonvariable]] — **CommonVariable** (`code`)
- [[generated/pysnooper_variables_exploding]] — **Exploding** (`code`)
- [[generated/pysnooper_variables_basevariable]] — **BaseVariable** (`code`)

## Incident edges (sample)

- `contains` ← [[generated/pysnooper_tracer]]
- `inherits` → [[generated/object]]
- `method` → [[generated/pysnooper_tracer_filewriter_init]]
- `method` → [[generated/pysnooper_tracer_filewriter_write]]
- `calls` ← [[generated/pysnooper_tracer_get_write_function]]
- `uses` → [[generated/pysnooper_variables_commonvariable]]
- `uses` → [[generated/pysnooper_variables_exploding]]
- `uses` → [[generated/pysnooper_variables_basevariable]]

## See also

- [[hot]]
- [[index]]
- [[GRAPH_REPORT]]
