# Suspect — FileWriter & encoding

> Ranked hypothesis area for PySnooper bug 1 (UTF-8 / Windows console encoding).

## Why

- Red baseline shows `UnicodeEncodeError` when logging non-ASCII values.
- Graph hub around file writing / trace output.

## Graph anchors

- [[generated/pysnooper_tracer_filewriter]]
- [[generated/pysnooper_tracer_filewriter_write]]
- [[generated/tests_test_chinese_test_chinese]]

## Status

Open — confirm with Phase 6 investigation.
