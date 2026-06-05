# PRD — Graph-Guided AI Debugging Agent (`graphdebug`)

> **HW4 — AI Agents Orchestration.** Product Requirements Document.
> Companion file: [`plan.md`](./plan.md). This PRD defines **what** and **why**; the PLAN defines **how**.

---

## 0. Document Control

| Field | Value |
|---|---|
| Project | `graphdebug` — graph-guided, multi-agent reverse-engineering & bug-fixing system |
| Type | Academic assignment (pairs) + production-quality engineering |
| Owners | _Pair: <member A>, <member B>_ |
| Status | DRAFT → REVIEW → APPROVED |
| Related docs | `plan.md`, `docs/TODO.md`, `docs/PRD_multiagent.md`, `docs/PRD_token_ledger.md`, `README.md` |
| Source of truth | This file for scope/acceptance; `plan.md` for architecture |

---

## 1. Executive Summary

`graphdebug` is a Python system that turns an **unfamiliar buggy codebase** into a
**queryable knowledge graph** (via **Graphify**) and a **navigable Obsidian vault**, then
runs a **high-level multi-agent workflow** (LangGraph supervisor/worker pattern) that
**locates, explains, fixes, and verifies a real bug** while **minimizing tokens and files read**.

The thesis (from the lecture): graph-guided, focused-context investigation beats naive
linear reading of raw files. We **prove** this with a controlled token-savings experiment
comparing a *naive baseline* agent against the *graph-guided* agent.

---

## 2. Background & Problem Statement

- **Lost in the Middle**: LLMs degrade when relevant facts sit in the middle of long
  contexts. Dumping whole files wastes tokens and hides signal.
- **Unfamiliar code**: real bugs live in projects whose architecture is undocumented or
  partially documented. Reverse engineering is required before fixing.
- **Cost & rate limits**: free LLM accounts impose strict call/token budgets, so the
  workflow must be *context-frugal* and *call-controlled*.

**Problem**: Given an unfamiliar buggy Python repository, find the root cause and fix it
**fast, cheaply, and verifiably**, while producing durable knowledge artifacts (graph +
vault + diagrams + reports) that justify the approach.

---

## 3. Goals & Non-Goals

### 3.1 Goals
1. Reverse-engineer an unfamiliar repo and extract its **real** architecture (block + OOP diagrams).
2. Build a **Graphify** representation (`graph.json`, `GRAPH_REPORT.md`, `graph.html`).
3. Build an **Obsidian vault** with `index.md`, `hot.md`, and linked component/finding pages.
4. Run a **multi-agent** workflow (LangGraph) that consumes graph+vault first, code last.
5. **Fix one real bug** with before/after evidence at code and knowledge levels.
6. **Prove token savings**: naive vs graph-guided, with hard numbers.
7. Ship at least one **original extension** per major area.

### 3.2 Non-Goals
- Fixing many bugs or an entire system (one small/medium bug only).
- Building a general-purpose IDE or replacing Graphify.
- Production deployment / multi-tenant service.
- Training or fine-tuning models.

---

## 4. Target Users & Personas

| Persona | Need | How `graphdebug` helps |
|---|---|---|
| **Maintainer (new to repo)** | Understand architecture fast | Graph + vault + diagrams |
| **Debugging engineer** | Find root cause cheaply | Agent ranks suspects, fetches minimal code |
| **Course reviewer/grader** | Verify process & evidence | README, reports, before/after, token report |
| **Future teammate** | Reuse knowledge | Linked Obsidian pages, ADRs, impact report |

---

## 5. Research & Understanding Questions (must be answered in artifacts)

These are tracked as first-class requirements and answered in `README.md`, `reports/`, and Obsidian.

| ID | Question | Primary evidence artifact |
|---|---|---|
| RQ1 | What is the **actual** architecture vs first impression? | `reports/architecture.md`, block diagram |
| RQ2 | Which modules/classes/functions are **most central**? | Centrality ranking from `graph.json` |
| RQ3 | Where are **complexity centers / God Nodes**? | `reports/god_nodes.md`, vault page |
| RQ4 | How to extract block + OOP diagrams from poor docs? | `plan.md` method + `assets/` diagrams |
| RQ5 | How was the bug found; what is the **root cause**? | `reports/bug_analysis.md`, `hot.md` |
| RQ6 | Advantage of graph/Obsidian vs linear reading? | `reports/token_comparison.md` |
| RQ7 | How did graph-guided agent **save tokens**? | Token ledger + comparison report |
| RQ8 | What extensions/mechanisms would we add next? | `reports/future_work.md`, README |

---

## 6. Success Metrics / KPIs

| KPI | Target | Measurement |
|---|---|---|
| Token reduction (graph-guided vs naive) | **≥ 50%** fewer total LLM tokens | Token ledger per run |
| Files/text-units read by agent | **≥ 50%** fewer | Tool-call ledger |
| Investigation iterations to root cause | **≤ naive**, ideally fewer | Run log step count |
| Bug fix correctness | Target test(s) pass after fix; previously failing | `pytest` exit + diff |
| Regression safety | No new failures in available suite | `pytest` before/after |
| Code coverage (our `src/`) | **≥ 85%** | `uv run pytest --cov` |
| Lint | **0** Ruff violations | `uv run ruff check .` |
| Reproducibility | Fresh clone runs end-to-end via documented commands | Dry-run on clean env |

---

## 7. Functional Requirements

> Priority: **P0** = must, **P1** = should, **P2** = nice. IDs are referenced by `plan.md` phases.

### 7.1 Graphify Representation (FR-G)
- **FR-G1 (P0)** Generate `graph.json`, `GRAPH_REPORT.md`, `graph.html` for the target repo.
- **FR-G2 (P0)** Generate Obsidian vault from Graphify (`--obsidian`) into `obsidian/`.
- **FR-G3 (P1)** Persist Graphify outputs under `artifacts/graphify/` (versioned, reproducible).
- **FR-G4 (P1)** Provide an SDK loader that parses `graph.json` into typed node/edge objects.

### 7.2 Obsidian Knowledge Vault (FR-O)
- **FR-O1 (P0)** `index.md` entry page: system map + navigation paths.
- **FR-O2 (P0)** `hot.md` focused page for the bug investigation (suspects, checks, status).
- **FR-O3 (P0)** Component/test/finding/suspect pages, linked via `[[wikilinks]]`.
- **FR-O4 (P1)** Before/after knowledge snapshot (pages/links/insights added post-fix).

### 7.3 Multi-Agent Workflow (FR-A) — *high-level multi-agent structure*
- **FR-A1 (P0)** Implement a **LangGraph supervisor** orchestrating specialized worker agents.
- **FR-A2 (P0)** Agents consume **graph + vault first**, request raw code **only when justified**.
- **FR-A3 (P0)** Worker roles (minimum): **Navigator**, **Investigator/Hypothesis**,
  **Code-Retriever**, **Fixer**, **Verifier**, **Scribe** (Obsidian writer).
- **FR-A4 (P0)** Shared typed **AgentState** with explicit **context budget** fields.
- **FR-A5 (P0)** A **Context/Token Budget mechanism** caps tokens & tool-calls per phase.
- **FR-A6 (P1)** Deterministic **routing** rules + supervisor `Command(goto=...)` handoffs.
- **FR-A7 (P1)** Human-in-the-loop checkpoint before applying any code change.
- **FR-A8 (P2)** Run is fully **traceable** (per-step log of inputs/outputs/tokens).

### 7.4 Bug Fixing (FR-B)
- **FR-B1 (P0)** Reproduce the failing test(s) on the buggy version (baseline red).
- **FR-B2 (P0)** Identify and document the **root cause** (not just symptom).
- **FR-B3 (P0)** Apply a minimal, justified **code fix**.
- **FR-B4 (P0)** Verify: target test(s) pass; no new regressions in available suite.
- **FR-B5 (P1)** Produce `reports/bug_analysis.md` (problem → cause → change → test).

### 7.5 Token-Savings Proof (FR-T)
- **FR-T1 (P0)** Implement a **naive baseline** mode (reads many raw files, low focus).
- **FR-T2 (P0)** Implement the **graph-guided** mode (graph + index + hot + vault).
- **FR-T3 (P0)** Record a **token ledger** per run (prompt/completion/total, tool calls, files).
- **FR-T4 (P0)** Produce `reports/token_comparison.md` with a side-by-side table + chart.
- **FR-T5 (P1)** Make the experiment **reproducible** with a single command/notebook.

### 7.6 Reverse Engineering & Diagrams (FR-R)
- **FR-R1 (P0)** Architectural **block diagram** derived from graph relationships (not folders).
- **FR-R2 (P0)** **OOP diagram** (classes, inheritance, composition, usage, wrappers).
- **FR-R3 (P1)** Centrality ranking of nodes; God-node identification.

### 7.7 Extensions (FR-E) — *≥1 per major area required*
- **FR-E1 (P1)** Rank suspect nodes by **centrality** and **proximity to failing tests**.
- **FR-E2 (P1)** **Dynamic `hot.md`** generated from `git diff` + `graph.json`.
- **FR-E3 (P2)** Detect **doc-vs-behavior contradictions**.
- **FR-E4 (P2)** **Impact report**: "what breaks if we change node X?"
- **FR-E5 (P2)** Before/after **architecture comparison** (graph delta).

### 7.8 SDK / CLI (FR-S) — *enforces system-prompt architecture*
- **FR-S1 (P0)** All business logic exposed via **SDK layer**; CLI/agents call SDK only.
- **FR-S2 (P0)** All external LLM calls route through a central **API Gatekeeper**
  (rate limits, retries, queue, backpressure, logging) configured from `config/`.
- **FR-S3 (P1)** A CLI (`uv run ...`) to run: graphify-load, build-vault, investigate, experiment.

---

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Cost | Default run stays within free-tier budgets; gatekeeper enforces caps. |
| NFR-2 | Performance | Graph queries answer without re-reading source files. |
| NFR-3 | Reliability | Retries with backoff on transient LLM/network errors. |
| NFR-4 | Security | No secrets in Git; `.env` only; inputs validated; safe file paths. |
| NFR-5 | Maintainability | Files ≤150 code lines where practical; one responsibility each. |
| NFR-6 | Testability | ≥85% coverage on `src/`; externals mocked; TDD where feasible. |
| NFR-7 | Portability | Runs on Windows (dev env) via `uv`; isolated env for BugsInPy. |
| NFR-8 | Observability | Structured logs + token/tool ledgers persisted to `results/`. |
| NFR-9 | Reproducibility | Pinned deps (`uv.lock`); deterministic seeds where applicable. |

---

## 9. Assumptions
- One LLM provider with a free/low-cost tier and an API key (via `.env`).
- Graphify is runnable on the chosen repo and emits `graph.json` + vault.
- The chosen bug has at least one **reproducible failing test**.
- Reviewer has Obsidian to open the vault (artifacts also viewable as plain Markdown).

## 10. Constraints
- **Tooling**: Python managed by **`uv` only** (no pip/venv/`python -m`).
- **Budgets**: free-account rate/token limits → small bug, staged calls.
- **Env**: BugsInPy needs isolated env (conda/Docker/uv) due to pinned deps.
- **Scope**: pairs; medium-sized assignment, not a final project.

---

## 11. Repository / Bug Selection (decided in `plan.md`, recorded here)

Candidate base repos (assignment §2): `soarsmu/BugsInPy`, `martinpeck/broken-python`,
`andela/buggy-python`.

**Selection policy (acceptance-relevant):**
- **Primary target** = a single **BugsInPy** bug from a **pure-Python, light-dependency,
  medium-architecture** project (good for OOP/God-node analysis), *or*
- **Fallback** = a `martinpeck/broken-python` / `andela/buggy-python` snippet if BugsInPy
  environment setup risks exceeding time budget.
- Final choice + **justification** MUST appear in `README.md` (assignment §2).

---

## 12. Acceptance Criteria (Definition of Done — product level)

A submission is **READY** only when ALL hold:

1. **Graphify**: `graph.json`, `GRAPH_REPORT.md`, `graph.html` present in `artifacts/graphify/`.
2. **Obsidian**: vault with working `index.md`, `hot.md`, ≥4 linked pages.
3. **Diagrams**: architecture block diagram **and** OOP diagram (in `assets/` + README).
4. **Agent**: LangGraph multi-agent workflow runs end-to-end and reports a located bug.
5. **Fix**: target test red→green; no new regressions; `reports/bug_analysis.md` complete.
6. **Tokens**: `reports/token_comparison.md` shows naive vs graph-guided with KPIs met (§6).
7. **Before/After**: code diff + knowledge snapshot documented.
8. **Extensions**: ≥1 original extension implemented and documented.
9. **Quality**: Ruff 0 violations; coverage ≥85% on `src/`; `uv.lock` committed.
10. **Docs**: README answers RQ1–RQ8 with visuals; `.env-example` present; no secrets committed.

---

## 13. Deliverables → Requirement Map (assignment §7)

| Deliverable | Requirements | Location |
|---|---|---|
| Full Python solution | FR-S, NFR-* | `src/`, `tests/` |
| Agent workflow (LangGraph) | FR-A* | `src/graphdebug/services/agents/` |
| Graphify outputs | FR-G* | `artifacts/graphify/` |
| Obsidian vault | FR-O* | `obsidian/` |
| Bug analysis report | FR-B* | `reports/bug_analysis.md` |
| Token comparison report | FR-T* | `reports/token_comparison.md` |
| Block diagram | FR-R1 | `assets/architecture.*` |
| OOP diagram | FR-R2 | `assets/oop.*` |
| Before/after proof | FR-B, FR-O4 | `reports/`, `obsidian/` |
| Extensions doc | FR-E* | `reports/extensions.md` |

---

## 14. Risks & Mitigations

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | BugsInPy dependency hell | High | Isolated env; pre-vet project; fallback repo |
| R2 | Free-tier rate/token limits | High | Gatekeeper caps; small bug; cache graph queries |
| R3 | Graphify run cost/time | Med | Run once, persist artifacts, reuse |
| R4 | Over-engineered workflow | Med | Minimal agent set; staged calls; HITL gate |
| R5 | Non-reproducible bug | High | Verify red baseline before agent work |
| R6 | Weak token-savings delta | Med | Tight naive baseline definition; identical task/seed |
| R7 | Secrets leakage | High | `.env` only; `.gitignore`; redact logs |

---

## 15. Milestones (high-level; detailed phases in `plan.md`)

| M | Outcome | Maps to PLAN phases |
|---|---|---|
| M0 | Env + repo/bug chosen, red baseline | Phase 0–1 |
| M1 | Graphify + Obsidian base built | Phase 2–3 |
| M2 | Reverse-engineering diagrams done | Phase 4 |
| M3 | Multi-agent workflow runs | Phase 5–6 |
| M4 | Bug fixed + verified | Phase 7 |
| M5 | Token experiment + extensions | Phase 8–9 |
| M6 | Docs/README + final audit READY | Phase 10 |

---

## 16. Out of Scope
- Multiple bugs, multiple repos (beyond one optional extension comparison).
- Custom graph engine (use Graphify).
- Web UI / hosted service / CI/CD pipelines.

---

## 17. Glossary
- **Graphify**: tool turning a codebase into a queryable knowledge graph (`graph.json`).
- **God Node**: a node with disproportionate connectivity/responsibility (complexity center).
- **hot.md**: focused, frequently-updated investigation page for the active bug.
- **Gatekeeper**: central component mediating all external API calls (limits/retries/queue).
- **Token ledger**: per-run record of prompt/completion tokens, tool calls, files read.
- **Naive baseline**: agent mode that reads many raw files without graph/vault focus.
