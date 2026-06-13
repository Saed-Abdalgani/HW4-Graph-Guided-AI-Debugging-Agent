# Token comparison — naive vs graph-guided

This file is **generated** by the Phase 8 harness so numbers always match the ledgers.

```bash
uv sync --all-groups
uv run graphdebug experiment \
  --target-root data/pysnooper-bugsinpy-1 \
  --test tests/test_chinese.py::test_chinese \
  --symptom "UnicodeEncodeError on non-ASCII snoop output" \
  --assume-hitl-ack
```

Equivalent API: `graphdebug.sdk.api.run_token_experiment`. After a run, reopen this file from `reports/token_comparison.md` and check `assets/token_chart.png`.

Until you run the command above, there is **no** measured comparison here — placeholders would violate the “measured, not guessed” rule (`todo.md` **C.10**).
