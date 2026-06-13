# PRD — Token Ledger (`graphdebug`)

> **Status:** Phase 5 implemented. JSONL per run under `results/<run_id>/ledger.jsonl`.

## Record schema (`LedgerRecord`)

Each JSONL line is one event:

- **`role`**: e.g. `fixer`, `retriever`, future tool roles.
- **`event`**: `llm_completion`, `file_read`, etc.
- **`prompt_tokens`**, **`completion_tokens`**, **`total_tokens`**: from provider metadata when
  available; file reads use zeros for token fields.
- **`latency_ms`**: wall time for LLM round-trips; `0` for file reads.
- **`tool_calls`**: incremented for each mediated LLM completion via Gatekeeper.
- **`files_read`**: per retriever slice read.
- **`meta`**: optional small JSON (e.g. model id, path); must stay free of secrets.

## Redaction (G.10)

- Gatekeeper helper **`redact_secrets`** scrubs `sk-…` and `Bearer …` patterns before anything
  user-facing is encouraged for logs.
- Do not commit ledgers that contain raw API keys or `.env` contents.

## Aggregation

- **`aggregate_ledger(path)`** (`services/ledger/aggregate.py`) sums token and file counters and
  lists distinct roles — used by Phase 8 experiment reports.

## References

- `prd.md` **FR-T\***
- `plan.md` §5.5, §12
