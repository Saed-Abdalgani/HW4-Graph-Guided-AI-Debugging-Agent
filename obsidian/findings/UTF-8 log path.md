# Finding — UTF-8 log path

> Seeded *finding* page (Phase 3). Refine after Phase 6 root-cause lock.

## Summary

Failure occurs when trace output hits a non-UTF-8 text encoding (e.g. Windows cp1252).

## Evidence links

- [[hot]]
- Structured metadata: repo file `reports/bug_analysis.md` (outside this vault).
- [[generated/pysnooper_tracer_filewriter_write]]

## Related

- [[suspects/FileWriter encoding|Suspect — FileWriter & encoding]]
