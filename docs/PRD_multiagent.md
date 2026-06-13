# PRD — Multi-Agent Workflow (`graphdebug`)

> **Scope:** LangGraph supervisor, six workers, HITL gate, naive vs graph modes. **Canonical requirements:** root [`prd.md`](../prd.md) (FR-A*). **Plan refs:** [`plan.md`](../plan.md) §2, §5.4, §6.

---

## 1. Goals

- **Graph-first investigation:** vault + graph queries **before** wide file reads.
- **Fair naive baseline:** same harness, model, temperature, seed, and stop criteria; only context strategy differs (`budgets.naive` vs `budgets.graph` in [`config/default.yaml`](../config/default.yaml)).
- **Cost safety:** every LLM completion is mediated by the **gatekeeper** (rate limit, retries, ledger hook) per **G.4**.
- **Human gate:** no autonomous write to `data/<target>/` source without HITL approval (`features.hitl_required`).

---

## 2. `AgentState` (summary)

Full schema: `services/agents/state_typed.py` / `state.py`. Notable fields:

| Area | Fields |
|------|--------|
| Task | `bug_task` (paths, symptom, failing test id) |
| Mode | `mode` ∈ `{graph, naive}` |
| Progress | `oriented`, `suspects_ranked`, `code_fetched`, `patch_ready`, `verification_attempted`, `scribed`, `verified` |
| Work artifacts | `suspects`, `fetched_code`, `patch`, pytest stdout/stderr |
| Budget | `budget` — updated by `services/agents/budget.py` **before** spend |
| Log | `log` — append-only step records for `run.log` |

---

## 3. Supervisor routing

`services/agents/supervisor.py` returns `Command(goto=...)` in a fixed order:

**Navigator → Investigator → Retriever → Fixer → (HITL) → Verifier → Scribe → END**

Unit tests assert deterministic transitions from flags.

---

## 4. Workers (reads / writes)

| Worker | Allowed reads | Writes / side effects |
|--------|----------------|------------------------|
| **Navigator** | `index.md`, `hot.md`, `GRAPH_REPORT.md` (graph mode); naive skips vault text | `oriented`, `log` |
| **Investigator** | `graph.json` + derived metrics (graph); file walk (naive) | `suspects`, `suspects_ranked` |
| **Retriever** | **Minimal** source slices under caps | `fetched_code`, ledger `file_read` |
| **Fixer** | State + gatekeeper LLM | `patch`, `patch_ready` |
| **Verifier** | subprocess `pytest` on subject | `verified`, exit metadata |
| **Scribe** | State | `hot.md`, `results/<run_id>/run.log` |

**Invariant:** only **Retriever** performs ordinary source reads in the graph design.

---

## 5. Budget guard

`services/agents/budget.py` enforces `max_tokens`, `max_tool_calls`, `max_files`, `max_iterations` from the active profile (`budgets.graph` or `budgets.naive`). Guards run **before** token spend or file reads where wired.

---

## 6. HITL

`services/agents/hitl.py` + LangGraph `interrupt()` when `features.hitl_required` is true. Automation may pass `assume_hitl_ack=True` **only** when the operator accepts skipping review; the workflow still does not auto-apply patches to the subject tree without a dedicated apply step (Phase 7 CLI).

---

## 7. CLI / SDK entrypoints

```bash
uv run graphdebug investigate --mode graph \
  --target-root data/pysnooper-bugsinpy-1 \
  --test tests/test_chinese.py::test_chinese \
  --symptom "UnicodeEncodeError on non-ASCII snoop output"
```

Python facade: `graphdebug.sdk.api.investigate` (see package exports in `sdk/api.py`).

---

## 8. Failure modes (design)

- **Cap breach:** budget guard raises / stops before unbounded spend.
- **Gatekeeper exhausted:** retries bounded; surfaced in ledger + exception chain.
- **Verifier red:** `verified` false; Scribe still records outcome for audit.

---

## 9. References

- **FR-A*, FR-S*, FR-B*** — root `prd.md`
- **Ledger / experiment** — [`PRD_token_ledger.md`](./PRD_token_ledger.md)
