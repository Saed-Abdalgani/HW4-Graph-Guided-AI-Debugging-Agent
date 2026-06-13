# PRD — Multi-Agent Workflow (`graphdebug`)

> **Status:** Phase 5 implemented. LangGraph supervisor + six workers; naive vs graph mode.

## State & routing

- **`AgentState`** (`services/agents/state.py`): `bug_task`, `mode` (`naive`|`graph`), progress
  flags (`oriented`, `suspects_ranked`, `code_fetched`, `patch_ready`, `verification_attempted`,
  `scribed`, `verified`), `suspects`, `fetched_code`, `patch`, `budget`, `log`, pytest outputs.
- **Supervisor** returns `Command(goto=...)` (`supervisor.py`) in deterministic order:
  Navigator → Investigator → Retriever → Fixer → (optional HITL) → Verifier → Scribe → END.
- **HITL** (`hitl.py`): `interrupt()` when `features.hitl_required` is true; resume with
  `Command(resume=...)` from a checkpointer-backed client. Non-interactive automation may set
  `assume_hitl_ack=True` on `investigate()` **only** when the operator accepts skipping human
  review (subject tree is never auto-patched by this workflow).

## Workers

| Worker | Reads | Writes / side effects |
|--------|--------|------------------------|
| Navigator | `index.md`, `hot.md`, `GRAPH_REPORT.md` | `oriented`, log |
| Investigator | `graph.json` (+ centrality / test proximity) | `suspects`, `suspects_ranked` |
| Retriever | Minimal **source slices** (budget) | `fetched_code`, ledger `file_read` |
| Fixer | Gatekeeper LLM only | `patch`, `patch_ready` |
| Verifier | subprocess `pytest` | `verified`, return codes |
| Scribe | state | `hot.md`, `results/<run_id>/run.log` |

**Naive mode** (`T5.15`): Navigator skips vault text; Investigator walks `.py` files under
`target_root` without graph context; Retriever still applies file caps. Same supervisor graph
and budgets profile (`budgets.naive` vs `budgets.graph`).

## References

- `prd.md` **FR-A\***
- `plan.md` §2, §5.4, §6.1
