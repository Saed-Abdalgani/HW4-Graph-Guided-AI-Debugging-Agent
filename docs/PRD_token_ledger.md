# PRD — Token Ledger (`graphdebug`)

> **Scope:** JSONL ledger per run, aggregation for experiments, redaction policy. **Canonical requirements:** root [`prd.md`](../prd.md) (FR-T*). **Plan refs:** [`plan.md`](../plan.md) §5.5, §12.

---

## 1. Goals

- **Prove token thesis with numbers** — every mediated LLM completion and file read leaves a machine-readable trace (**C.10**).
- **No secrets in artifacts** — redact before sharing or committing evidence (**G.10**).
- **Reproducible aggregation** — Phase 8 reads per-run `manifest.json` + `ledger.jsonl` deterministically.

---

## 2. Storage layout

For a single investigation or experiment arm:

```
results/<run_id>/
  ledger.jsonl      # append-only JSONL records
  manifest.json     # run metadata + aggregates (written at finalize)
  run.log           # human-readable steps (scribe)
```

Experiment harness runs **two** runs (naive + graph) and compares aggregates.

---

## 3. `LedgerRecord` schema (conceptual)

Each JSONL line is one event (see `services/ledger/schema.py` for fields):

| Field | Meaning |
|-------|---------|
| `role` | Worker or subsystem name (e.g. `fixer`, `retriever`) |
| `event` | `llm_completion`, `file_read`, … |
| `prompt_tokens`, `completion_tokens`, `total_tokens` | Provider metadata when present; zeros for non-LLM events |
| `latency_ms` | Wall time for LLM round-trips |
| `tool_calls` | Incremented per gated completion |
| `files_read` | Incremented for retriever-backed reads |
| `meta` | Small JSON blob (model id, path hints); **must not** contain secrets |

---

## 4. Emission path

1. Application calls **`Gatekeeper.complete`** (`shared/gatekeeper.py`) for LLM work.
2. Gatekeeper applies rate limit / retry / **redaction** helper on log lines.
3. On success, writer appends **`llm_completion`** lines with token counts from the provider response.

Retriever emits **`file_read`** lines without token inflation.

---

## 5. Redaction (G.10)

- Patterns such as `sk-…` and `Bearer …` are scrubbed in gatekeeper logging helpers.
- **Do not** commit `.env`, raw API keys, or prompt blobs that include secrets.
- Treat `meta` as **public-ish**; keep it minimal.

---

## 6. Aggregation API

`aggregate_ledger(path: Path) -> LedgerAggregate` (`services/ledger/aggregate.py`):

- Sums **prompt / completion / total** tokens.
- Totals **tool_calls** and **files_read**.
- Lists distinct **roles** for sanity checks.

Used by `services/experiment/metrics.py` and `report_md.py` to build `reports/token_comparison.md`.

---

## 7. KPI hooks (Phase 8)

- **Token reduction %** — compare `total_tokens` naive vs graph from aggregates.
- **File read reduction %** — compare `files_read` or distinct paths from ledger/meta.
- **Cost estimate** — `config/default.yaml` → `experiment.usd_per_1k_*` × token totals (illustrative pricing).

---

## 8. Operator checklist before committing `results/`

- [ ] No `.env` contents or raw keys in JSONL / logs.
- [ ] `manifest.json` does not embed private prompts if your fork logs them — strip or redact first.

---

## 9. References

- **Multi-agent flow** — [`PRD_multiagent.md`](./PRD_multiagent.md)
- **Experiment CLI** — root `README.md` (“Token efficiency”)
