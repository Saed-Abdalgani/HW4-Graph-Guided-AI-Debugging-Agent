# TODO — Graph-Guided AI Debugging Agent (`graphdebug`)

> **HW4 — AI Agents Orchestration.** Execution checklist & quality gates.
> Derived from [`prd.md`](./prd.md) and [`plan.md`](./plan.md).
> This file is the **single source of truth for progress**. Update status on every change.
> Requirement IDs (`FR-*`, `NFR-*`, `RQ*`, `ADR-*`) and `plan §N` references are authoritative.

---

## 0. How To Use This File

- Work **top-to-bottom by phase**. Do **not** start a phase until its **Entry Gate** passes.
- Every task has a stable **ID** (`T<phase>.<n>`). Reference IDs in commit messages.
- Mark status honestly. A task is **DONE only when its DoD is verifiably true**, not "coded".
- After finishing any task, run the **Downstream Check** (see §1.3) before moving on.
- Keep `obsidian/hot.md` and this file in sync — they are the project's working memory.

### 0.1 Status Legend
| Symbol | Meaning |
|---|---|
| `[ ]` | Not started |
| `[/]` | In progress |
| `[x]` | Done **and DoD verified** |
| `[-]` | Cancelled / descoped (record why) |
| `[!]` | Blocked (record blocker + owner) |

### 0.2 Priority Legend
| Tag | Meaning | Rule |
|---|---|---|
| `P0` | Must — submission fails without it | Never descope silently |
| `P1` | Should — strongly expected | Descope only with written justification |
| `P2` | Nice — extension / polish | Descope freely if time-boxed out |

### 0.3 Task Fields
Each task carries: **Refs** (requirements/plan), **Deps** (blocking task IDs),
**DoD** (objective completion test), **⚠ Critical** (failure modes / red-team notes).

---

## 1. Global Conventions & Critical Rules (READ FIRST)

These are **non-negotiable**. Violations are blocking defects, not style nits.

### 1.1 Tooling
- [ ] **G.1** (P0) Use **`uv` only**. No `pip`, `venv`, `virtualenv`, or bare `python -m`.
  - **Refs**: system-prompt §Python tooling, `plan §15`.
  - **⚠ Critical**: a single `pip install` in docs/CI invalidates reproducibility. Grep the
    repo for `pip install` / `python -m venv` before submission and remove them.
- [ ] **G.2** (P0) All deps added via `uv add`; `pyproject.toml` + `uv.lock` committed.
  - **⚠ Critical**: never hand-edit dependency versions; never commit without re-`uv lock`.

### 1.2 Architecture invariants
- [ ] **G.3** (P0) **All business logic lives behind the SDK facade** (`sdk/api.py`).
  - **Refs**: FR-S1, ADR-4, `plan §5.1`.
  - **⚠ Critical**: CLI, LangGraph nodes, notebooks, and tests must import the SDK, never
    reach into `services/*` internals. Audit imports in Phase 10.
- [ ] **G.4** (P0) **Every external LLM/API call goes through the Gatekeeper.**
  - **Refs**: FR-S2, ADR-5, `plan §5.7`.
  - **⚠ Critical**: a worker that calls the LLM SDK directly bypasses rate limits, retries,
    and the token ledger — which **breaks the token experiment's integrity**. Zero exceptions.
- [ ] **G.5** (P0) **No hardcoded configurable values** (model names, URLs, timeouts, rate
  limits, paths, budgets, feature flags). All from `config/*.yaml` + `.env`.
  - **Refs**: NFR-4, system-prompt §Code quality.
- [ ] **G.6** (P0) **One responsibility per module**; keep files **≤150 code lines** where
  practical; **no duplicated logic** (extract helpers/base classes).
  - **⚠ Critical**: if `supervisor.py` or `gatekeeper.py` grows past ~150 lines, split by
    responsibility *before* it becomes unmaintainable.

### 1.3 Definition-of-Done discipline (Downstream Check)
- [ ] **G.7** (P0) After **every** code edit, search for **all** downstream impacts: callers,
  interface implementers, subclasses, tests, type defs, imports, config, docs.
  - **⚠ Critical**: incomplete propagation (e.g., changing `AgentState` but not all workers)
    is a top failure mode. Treat a signature change as a mini-migration.
- [ ] **G.8** (P0) Update affected **existing tests**; do not leave them red or stale.

### 1.4 Security & secrets
- [ ] **G.9** (P0) Secrets only in `.env`; commit `.env-example`; `.gitignore` covers `.env`,
  `*.key`, `*.pem`, large `data/`, sensitive `results/`.
  - **Refs**: NFR-4, system-prompt §Security.
- [ ] **G.10** (P0) Gatekeeper + loggers **redact** keys/tokens; no secrets in logs/ledgers.
  - **⚠ Critical**: ledgers are committed as evidence — scan them for leaked prompts/keys.

### 1.5 Quality gates (must stay green continuously)
- [ ] **G.11** (P0) `uv run ruff check .` → **0 violations**.
- [ ] **G.12** (P0) `uv run pytest --cov=src` → **≥85%** coverage on `src/`.
  - **⚠ Critical**: 85% is a floor, not a target gamed by trivial tests. Cover failure paths,
    budget-cap breaches, gatekeeper retries, and graph-query edge cases — not just getters.
- [ ] **G.13** (P1) Run G.11/G.12 before every commit; never commit on red.

---

## 2. Milestone & Phase Map

| Milestone | Phases | Exit outcome | Hard gate before next |
|---|---|---|---|
| **M0** | 0–1 | Env scaffolded; bug chosen; **red baseline reproduced** | Failing test is deterministic |
| **M1** | 2–3 | Graphify artifacts + base Obsidian vault | `graph.json` parses; vault navigable |
| **M2** | 4 | Block + OOP diagrams; God-nodes | Diagrams derived from graph, not folders |
| **M3** | 5–6 | Multi-agent workflow runs; root-cause hypothesis | Stays within budget caps |
| **M4** | 7 | Bug fixed + verified | Red→green; no new regressions |
| **M5** | 8–9 | Token experiment + extensions | KPIs met or deviation explained |
| **M6** | 10 | Docs/README; final audit | Verdict = READY |

> **Critical sequencing rule**: Do **not** build the agent (Phase 5) before the graph/vault
> (Phases 2–3) exist. An agent without graph-first context cannot demonstrate the thesis and
> wastes scarce free-tier tokens. Resist the urge to "just start coding the agent".

---

## Phase 0 — Environment & Scaffolding  *(M0)*

**Entry Gate**: none (start here). **Exit Gate**: skeleton runs; Ruff clean; pytest collects.

### 0.A Project bootstrap
- [ ] **T0.1** (P0) Initialize project with `uv init`; set Python version pin.
  - **Refs**: `plan §15`, G.1. **Deps**: —.
  - **DoD**: `pyproject.toml` exists; `uv run python --version` prints pinned version.
  - **⚠ Critical**: confirm the pinned interpreter is available on Windows dev env *and*
    compatible with LangGraph + the chosen LLM SDK before going further.
- [ ] **T0.2** (P0) Create full directory tree from `plan §3`.
  - **DoD**: tree matches `plan §3`; each package has `__init__.py`.
  - **⚠ Critical**: empty dirs are not tracked by Git — add `.gitkeep` to `results/`,
    `data/`, `artifacts/graphify/`, `assets/` so structure survives a fresh clone.
- [ ] **T0.3** (P0) Add `version.py` (single version source) and `constants.py`
  (non-config constants only — NOT tunables).
  - **Refs**: `plan §5.7`. **⚠ Critical**: do not let `constants.py` absorb things that
    belong in `config/` (model names, limits). That violates G.5.

### 0.B Dependencies
- [ ] **T0.4** (P0) Add runtime deps via `uv add`: `langgraph`, `langchain-core`, the chosen
  provider SDK, `networkx`, `pyyaml`, `python-dotenv`.
  - **DoD**: `uv.lock` updated; `uv sync` clean.
  - **⚠ Critical**: pick exactly **one** LLM provider now (ADR-1). Two SDKs double surface
    area and complicate the Gatekeeper.
- [ ] **T0.5** (P0) Add dev deps: `pytest`, `pytest-cov`, `ruff` (+ `pytest-mock` if used).
  - **DoD**: `uv run pytest`, `uv run ruff check .` both execute.
- [ ] **T0.6** (P1) Add experiment deps in an optional/dev group: `matplotlib`, `ipykernel`.
  - **⚠ Critical**: keep these optional so the core install stays lean.

### 0.C Config & secrets scaffolding
- [ ] **T0.7** (P0) Create `config/default.yaml`: model name(s), gatekeeper rate limits
  (RPM/TPM), retry/backoff params, **budget caps** (`max_tokens`, `max_tool_calls`,
  `max_files`, `max_iterations`), paths, feature flags.
  - **Refs**: FR-A5, FR-S2, G.5.
  - **⚠ Critical**: define separate budget profiles for **naive** vs **graph** arms so the
    experiment is controlled and reproducible (`plan §12`).
- [ ] **T0.8** (P0) Implement `shared/config.py` loader (yaml + `.env` overlay, typed access,
  validation, clear errors on missing keys).
  - **DoD**: unit test loads config and rejects missing required keys.
  - **⚠ Critical**: fail **loudly** on missing/invalid config; silent defaults hide cost bugs.
- [ ] **T0.9** (P0) Create `.env-example` (key var names, no real values) and local,
  gitignored `.env`.
  - **Refs**: G.9. **DoD**: `.env` in `.gitignore`; `.env-example` committed.
- [ ] **T0.10** (P0) Write `.gitignore` (`.env`, `__pycache__`, `.venv`, `*.key`, `*.pem`,
  large `data/`, raw `results/`, notebook checkpoints).

### 0.D Per-mechanism PRDs & docs stubs
- [ ] **T0.11** (P1) Create `docs/PRD_multiagent.md` (state, nodes, routing, budget) stub.
  - **Refs**: system-prompt §Mandatory docs, `plan §5.4`.
- [ ] **T0.12** (P1) Create `docs/PRD_token_ledger.md` (schema, aggregation, redaction) stub.
- [ ] **T0.13** (P1) Decide doc home: keep `prd/plan/todo.md` at root and mirror into `docs/`
  to satisfy the system-prompt `docs/` layout.
  - **⚠ Critical**: pick **one** canonical copy to edit; stale duplicates mislead reviewers.

### 0.E Sanity skeleton
- [ ] **T0.14** (P0) Add trivial `sdk/api.py` + `version.py` smoke test so coverage runs.
  - **DoD**: `uv run pytest` green with ≥1 test; `uv run ruff check .` = 0.
- [ ] **T0.15** (P1) Add CLI entrypoint stub (`graphdebug --help`) wired to SDK (no logic).
  - **Refs**: FR-S3, G.3.

**Phase 0 DoD**: structure (`plan §3`) present; `uv.lock` committed; config loads; Ruff 0;
pytest green; secrets safe. **❗Do not start Phase 1 until all P0 above are `[x]`.**

---

## Phase 1 — Repo & Bug Selection + Red Baseline  *(M0)*

**Entry Gate**: Phase 0 DoD met. **Exit Gate**: a failing test reproduced deterministically.

### 1.A Selection
- [ ] **T1.1** (P0) Choose target per `prd §11` / ADR-6: **primary** = one light-dependency
  BugsInPy bug from a medium, OOP-rich, pure-Python project; **fallback** = buggy-python.
  - **Refs**: assignment §2. **Deps**: T0.1.
  - **⚠ Critical**: vet dependencies **before** committing. Avoid heavy native builds on a
    free-tier/Windows timeline. If env setup will blow the time box, **switch to fallback
    now** (R1) — do not sink days into dependency hell.
- [ ] **T1.2** (P0) Record selection + **justification** in README draft (assignment §2 hard
  requirement) and `obsidian/index.md`.
  - **DoD**: README has a "Why this repo/bug" section linking the bug id.
- [ ] **T1.3** (P1) Capture bug metadata (project, bug id, symptom, failing test path,
  buggy/fixed refs) in `reports/bug_analysis.md` skeleton.

### 1.B Isolated environment
- [ ] **T1.4** (P0) Stand up an **isolated env** for the target (uv-managed; conda/Docker only
  if the bug's pinned Python forces it). Keep target deps separate from `graphdebug`.
  - **Refs**: assignment §6.1, NFR-7, R1.
  - **⚠ Critical**: do **not** pollute `graphdebug`'s `pyproject.toml` with the target's
    deps. The target is a *subject under study*, not our dependency.
- [ ] **T1.5** (P0) Check out the **buggy** version into `data/<target>/`; record commit ref.
- [ ] **T1.6** (P1) Document exact setup commands in `data/<target>/SETUP.md` for reproducibility.

### 1.C Red baseline (the key gate of M0)
- [ ] **T1.7** (P0) Run target test(s) → **confirm FAIL**; capture full output.
  - **Refs**: FR-B1, RQ5, R5. **Deps**: T1.5.
  - **DoD**: failing output saved to `results/baseline_red.txt`.
  - **⚠ Critical**: if the test does not fail **reproducibly**, the entire downstream proof
    collapses. Re-run ≥2×; pin seeds. If still flaky, **change the bug now**, not in Phase 7.
- [ ] **T1.8** (P0) Record observed **symptom** (exception/type/message/wrong output) in
  `hot.md` and `bug_analysis.md`.
- [ ] **T1.9** (P1) Locate the official fixed-version diff (ground truth) but **do not read it
  as the answer** — reserve it only to validate the agent's independent fix later.
  - **⚠ Critical**: peeking at the official patch and reverse-justifying it is self-deception.
    Keep the investigation honest; compare only at the end (Phase 7).

**Phase 1 DoD**: target chosen + justified; isolated env; **red baseline reproduced
deterministically**; symptom documented. **❗No Graphify run until red is proven.**

---

## Phase 2 — Graphify Representation  *(M1)*

**Entry Gate**: red baseline proven (Phase 1). **Exit Gate**: `graph.json` parses; report opens.

### 2.A Run Graphify
- [ ] **T2.1** (P0) Run Graphify on the target repo with `--obsidian`.
  - **Refs**: FR-G1, FR-G2, `plan §8`. **Deps**: T1.5.
  - **DoD**: `graph.html`, `GRAPH_REPORT.md`, `graph.json`, vault produced.
  - **⚠ Critical**: Graphify itself consumes tokens (LLM semantic pass). Run it **once**,
    on the right scope. Scoping the whole monorepo when the bug lives in one package wastes
    budget and dilutes the graph — point it at the relevant subtree if possible.
- [ ] **T2.2** (P0) Persist outputs to `artifacts/graphify/` (immutable artifacts).
  - **Refs**: FR-G3. **DoD**: files committed; not regenerated per query.
- [ ] **T2.3** (P1) Record exact Graphify version + command + scope in
  `artifacts/graphify/RUN.md`.
  - **⚠ Critical**: without this, the graph is not reproducible and RQ7 evidence is weak.

### 2.B Validate & load the graph
- [ ] **T2.4** (P0) Implement `services/graphify/loader.py`: parse `graph.json` → typed
  `CodeGraph` (nodes/edges/clusters/metadata).
  - **Refs**: FR-G4, `plan §5.2`, `plan §6.2`. **Deps**: T2.2.
  - **DoD**: unit test parses the real `graph.json` into typed objects.
  - **⚠ Critical**: do **not** assume Graphify's schema — inspect the actual `graph.json`
    keys/edge-relation vocabulary first and write the loader against reality, with a clear
    error if the schema differs from expectation.
- [ ] **T2.5** (P0) Implement `services/graphify/query.py`: neighbors, hop traversal,
  path-between-nodes, edge detail — **without reading source files**.
  - **Refs**: `plan §5.2`, `plan §8`. **DoD**: unit tests on a fixture graph.
  - **⚠ Critical**: this module is the heart of the token-saving thesis. If any query path
    secretly falls back to reading source, the experiment is invalidated (see G.4 analogue).
- [ ] **T2.6** (P1) Sanity-check the graph: node/edge counts, dangling edges, isolated nodes.
  - **DoD**: a short `reports/graph_sanity.md` note.

**Phase 2 DoD**: Graphify artifacts committed under `artifacts/graphify/`; loader + query
unit-tested against the real graph; reproducibility recorded.

---

## Phase 3 — Obsidian Knowledge Vault  *(M1)*

**Entry Gate**: Phase 2 DoD met. **Exit Gate**: `index.md`/`hot.md` exist and links resolve.

### 3.A Core navigation pages
- [ ] **T3.1** (P0) Author `obsidian/index.md`: system map + main navigation paths; links to
  architecture, God-nodes, components, tests, and `hot.md`.
  - **Refs**: FR-O1, RQ1, `plan §9`. **DoD**: opens in Obsidian; links resolve.
  - **⚠ Critical**: `index.md` is the agent's entry context. Keep it **dense but short** —
    a bloated index reintroduces the Lost-in-the-Middle problem it's meant to solve.
- [ ] **T3.2** (P0) Author `obsidian/hot.md`: *Symptom*, *Suspects (ranked)*, *Checked*,
  *Root cause*, *Fix*, *Next action* sections, seeded from Phase 1 symptom.
  - **Refs**: FR-O2, RQ5. **DoD**: reflects current investigation state.
  - **⚠ Critical**: `hot.md` is a **living** doc. If it goes stale, the agent reads wrong
    context and the whole "focused memory" claim is undermined. Update it every iteration.

### 3.B Component & finding pages
- [ ] **T3.3** (P0) Implement `services/vault/builder.py`: generate component/test/finding/
  suspect pages with `[[wikilinks]]`.
  - **Refs**: FR-O3, `plan §5.3`. **DoD**: ≥4 linked pages generated.
- [ ] **T3.4** (P0) Implement `services/vault/hot.py`: programmatic create/update of `hot.md`.
  - **Refs**: FR-O2. **DoD**: unit test writes/updates sections idempotently.
- [ ] **T3.5** (P1) Implement `services/vault/snapshot.py`: capture a **before** knowledge
  snapshot now (for the Phase 7 before/after diff).
  - **Refs**: FR-O4. **⚠ Critical**: you cannot produce a before/after if you forget the
    "before". Snapshot **now**, not after the fix.

### 3.C Wiring
- [ ] **T3.6** (P1) Expose `build_vault`/`update_hot` via SDK (`sdk/api.py`); CLI calls SDK.
  - **Refs**: FR-S1, G.3.
- [ ] **T3.7** (P2) Add a screenshot of the Obsidian graph view to `assets/` for the README.

**Phase 3 DoD**: navigable vault with `index.md` + `hot.md` + ≥4 linked pages; before-snapshot
captured; vault generation exposed via SDK.

---

## Phase 4 — Reverse Engineering & Diagrams  *(M2)*

**Entry Gate**: graph + vault exist (Phases 2–3). **Exit Gate**: block + OOP diagrams committed.

### 4.A Centrality & complexity analysis
- [ ] **T4.1** (P0) Implement `services/analysis/` centrality (degree/betweenness/closeness)
  over `CodeGraph` (NetworkX).
  - **Refs**: FR-R3, RQ2, `plan §5.2`, `plan §10`. **Deps**: T2.4.
  - **DoD**: ranked node list with scores; unit-tested on a fixture graph.
- [ ] **T4.2** (P0) Identify **God Nodes** / complexity centers; write `reports/god_nodes.md`
  + an Obsidian page.
  - **Refs**: RQ3. **DoD**: each God-node backed by a centrality number + a one-line "why".
  - **⚠ Critical**: "God-node" must be **evidence-backed** (high centrality / mixed
    responsibility), not a vibe. State the metric and threshold you used.

### 4.B Diagrams (derived from the graph, NOT folders)
- [ ] **T4.3** (P0) Produce the **architecture block diagram** by collapsing nodes into
  clusters/subsystems and drawing their real edges (imports/calls).
  - **Refs**: FR-R1, RQ1, RQ4, `plan §10`, `plan §11`. **DoD**: `assets/architecture.*`.
  - **⚠ Critical**: the assignment explicitly forbids relying on folder structure/file names.
    If your block diagram mirrors the directory tree, you have **not** done reverse
    engineering — derive it from graph relationships and justify each block.
- [ ] **T4.4** (P0) Produce the **OOP diagram** from `class` nodes + `inherits`/`contains`/
  `uses` edges (inheritance, composition, usage, wrappers).
  - **Refs**: FR-R2, RQ4. **DoD**: `assets/oop.*`.
  - **⚠ Critical**: validate a few relationships against actual code (budgeted reads) — LLM
    semantic edges can hallucinate inheritance. A wrong OOP diagram is worse than none.
- [ ] **T4.5** (P1) Write `reports/architecture.md` answering RQ1 & RQ4 (what surprised you;
  how diagrams were extracted from poor docs).
  - **⚠ Critical**: explicitly state **what was NOT clear at first glance** and what the
    graph revealed — that contrast is the graded insight, not the diagram alone.

**Phase 4 DoD**: centrality ranking + God-nodes documented; block diagram + OOP diagram in
`assets/` and embedded in README; both derived from the graph and spot-validated.

---

## Phase 5 — Multi-Agent Workflow Build  *(M3)*

**Entry Gate**: graph + vault + diagrams exist. **Exit Gate**: workflow compiles & dry-runs
on a fixture within budget caps. Detail spec: `docs/PRD_multiagent.md`.

### 5.A Shared foundations
- [ ] **T5.1** (P0) Implement `services/agents/state.py` (`AgentState` TypedDict per `plan §6.1`),
  plus `BugTask`, `SuspectNode`, `Patch`, `BudgetState`, `StepRecord`.
  - **Refs**: FR-A4, `plan §6`. **DoD**: importable, typed; unit test constructs/round-trips.
  - **⚠ Critical**: get the state schema **right early** — every worker depends on it (G.7).
    Adding a field later means touching all nodes. Review the full schema before coding nodes.
- [ ] **T5.2** (P0) Implement `shared/gatekeeper.py`: token-bucket rate limit (RPM/TPM from
  config), bounded queue (backpressure), retry+exponential backoff, structured logging,
  **ledger hook**, secret redaction.
  - **Refs**: FR-S2, FR-A5, ADR-5, NFR-3, G.4, G.10. **DoD**: unit tests for rate-limit,
    retry-on-transient, and that **every** call emits a ledger record.
  - **⚠ Critical**: this is the cost-control linchpin. Test the *limit-exceeded* and
    *retry-exhausted* paths, not just the happy path. Mock the LLM — never hit the real API
    in unit tests.
- [ ] **T5.3** (P0) Implement `services/agents/budget.py`: pre-call guard that halts/raises
  when `max_tokens`/`max_tool_calls`/`max_files`/`max_iterations` would be exceeded.
  - **Refs**: FR-A5. **DoD**: unit tests for each cap boundary (at, just under, just over).
  - **⚠ Critical**: the budget guard must run **before** the spend, not after. An after-the-fact
    check still burns the tokens it was meant to prevent.
- [ ] **T5.4** (P0) Implement `services/ledger/` (record + aggregate, JSONL to
  `results/<run_id>/ledger.jsonl`).
  - **Refs**: FR-T3, `plan §5.5`, `docs/PRD_token_ledger.md`. **DoD**: aggregation unit-tested.

### 5.B Workers (each = small, role-scoped prompt)
- [ ] **T5.5** (P0) `workers/navigator.py`: reads `index.md`, `hot.md`, `GRAPH_REPORT.md`
  to orient; sets `oriented`. **No raw source reads.**
  - **Refs**: FR-A2, FR-A3. **DoD**: node updates state from vault context only.
- [ ] **T5.6** (P0) `workers/investigator.py`: queries `graph.json` (+ centrality, test
  proximity) to produce ranked `suspects`; sets `suspects_ranked`.
  - **Refs**: FR-A3, FR-E1, RQ2. **DoD**: outputs ≥1 ranked suspect with rationale.
- [ ] **T5.7** (P0) `workers/retriever.py`: fetches **minimal** code slices for top suspects,
  **budget-gated**; the **only** worker allowed to read source.
  - **Refs**: FR-A2, FR-A5. **DoD**: respects `max_files`; records files read to ledger.
  - **⚠ Critical**: enforce "minimal slice", not whole-file dumps. Whole-file reads here
    quietly erase the token advantage the whole project is trying to prove.
- [ ] **T5.8** (P0) `workers/fixer.py`: proposes a minimal patch (unified diff) + rationale;
  sets `patch_ready`. **Does not apply** the patch.
  - **Refs**: FR-B3, FR-A7. **DoD**: emits a valid diff object referencing real locations.
- [ ] **T5.9** (P0) `workers/verifier.py`: runs the target test(s) via subprocess; sets
  `verified` on red→green with no new failures.
  - **Refs**: FR-B4. **DoD**: parses pytest result; distinguishes target-pass vs regressions.
  - **⚠ Critical**: "tests pass" must mean *the previously-failing test now passes AND nothing
    else newly fails*. A patch that green-lights the target by breaking others is a regression.
- [ ] **T5.10** (P0) `workers/scribe.py`: updates `hot.md`, suspect/finding pages, and run log.
  - **Refs**: FR-O2, FR-A3. **DoD**: vault reflects latest state after each cycle.

### 5.C Orchestration
- [ ] **T5.11** (P0) `supervisor.py`: routing node returning `Command(goto=...)` from state
  flags (`oriented`→`suspects_ranked`→`code_fetched`→`patch_ready`→`verified`).
  - **Refs**: FR-A1, FR-A6, ADR-3, `plan §2`. **DoD**: deterministic routing unit-tested.
- [ ] **T5.12** (P0) `graph_app.py`: build/compile the LangGraph; wire workers + supervisor;
  optional checkpointer for HITL.
  - **Refs**: FR-A1, FR-A7. **DoD**: compiles; dry-run on fixture traverses all nodes.
- [ ] **T5.13** (P0) HITL gate before applying any code change.
  - **Refs**: FR-A7. **⚠ Critical**: never let the agent write to `data/<target>/` source
    without an explicit human approval step — autonomous edits to the subject corrupt evidence.
- [ ] **T5.14** (P0) Expose `investigate(bug_task, mode)` via SDK; CLI subcommand calls SDK.
  - **Refs**: FR-S1, FR-S3, G.3.
- [ ] **T5.15** (P1) Implement the **naive baseline** mode in the same harness (free raw-file
  reading, no graph/index/hot/vault context) for Phase 8.
  - **Refs**: FR-T1, `plan §12`. **⚠ Critical**: the naive arm must be a *fair* baseline —
    same model, same task, same stop criteria — differing **only** in context strategy.

**Phase 5 DoD**: compiled multi-agent graph; gatekeeper+budget+ledger tested; all workers
unit-tested with **mocked** LLM; dry-run stays within caps; SDK/CLI wired. **No real LLM in
unit tests.**

---

## Phase 6 — Run Investigation (graph-guided)  *(M3)*

**Entry Gate**: Phase 5 DoD met. **Exit Gate**: root-cause hypothesis + candidate patch under caps.

- [ ] **T6.1** (P0) Run `investigate --mode graph` on the real bug; capture full run.
  - **Refs**: FR-A2, RQ5, RQ6. **Deps**: T5.12, T1.7.
  - **DoD**: `InvestigationResult` produced; `results/<run_id>/ledger.jsonl` populated.
- [ ] **T6.2** (P0) Confirm the agent reached a concrete **root-cause hypothesis** (not just
  the symptom) and a candidate patch — within budget caps.
  - **⚠ Critical**: if the agent stalls or loops, do **not** keep re-running blindly (burns
    tokens). Inspect routing/ledger, fix the workflow, then re-run once. Record iterations.
- [ ] **T6.3** (P1) Scribe updates `hot.md`: suspects checked, root cause, proposed fix, next.
  - **Refs**: FR-O2. **DoD**: `hot.md` matches the run outcome.
- [ ] **T6.4** (P1) Archive the run log + ledger for the token comparison (Phase 8).
  - **⚠ Critical**: tag this run clearly as the **graph arm** to avoid mixing it with naive.

**Phase 6 DoD**: a documented root-cause hypothesis + candidate patch, produced under caps,
with a saved ledger tagged as the graph arm.

---

## Phase 7 — Bug Fix & Verification  *(M4)*

**Entry Gate**: candidate patch from Phase 6. **Exit Gate**: red→green, no new regressions.

- [ ] **T7.1** (P0) Review the proposed patch (HITL); confirm it addresses the **root cause**,
  not the symptom.
  - **Refs**: FR-B2, FR-B3, RQ5. **⚠ Critical**: a patch that suppresses the exception or
    special-cases the failing input is a **symptom mask**, not a fix. Reject masks.
- [ ] **T7.2** (P0) Apply the fix to `data/<target>/` (after approval); keep the diff.
  - **Refs**: FR-B3. **DoD**: `reports/fix.diff` saved.
- [ ] **T7.3** (P0) Run the target test → **PASS**; save `results/baseline_green.txt`.
  - **Refs**: FR-B4. **DoD**: previously-failing test now passes.
- [ ] **T7.4** (P0) Run the available suite → **no new failures** (regression check).
  - **Refs**: FR-B4, NFR. **⚠ Critical**: compare against the red-baseline run, not memory.
    Newly broken tests = not done.
- [ ] **T7.5** (P1) Compare the fix to the official patch (from T1.9) — agreement or a valid
  alternative? Document the comparison.
  - **Refs**: RQ5. **⚠ Critical**: if they differ, justify why yours is also correct (or fix).
- [ ] **T7.6** (P0) Complete `reports/bug_analysis.md`: Problem → Reproduction → Investigation
  trail → **Root cause** → Change → Tests.
  - **Refs**: FR-B5, RQ5.
- [ ] **T7.7** (P0) Capture **after** knowledge snapshot; produce before/after diff (pages,
  links, insights added; architectural understanding change).
  - **Refs**: FR-O4, RQ1. **DoD**: before/after recorded in `reports/` + `obsidian/`.
- [ ] **T7.8** (P2) If architecture understanding changed, update the block/OOP diagrams or
  add an "after" variant (extension FR-E5).

**Phase 7 DoD**: fix applied; target test green; no regressions; `bug_analysis.md` complete;
before/after knowledge snapshot done.

---

## Phase 8 — Token-Savings Experiment  *(M5)*

**Entry Gate**: graph arm run exists (Phase 6); naive mode implemented (T5.15).
**Exit Gate**: comparison report with KPIs met or deviation explained.

- [ ] **T8.1** (P0) Implement `services/experiment/` harness: run the **same** bug task in
  **naive** and **graph** modes with identical model/temperature/seed/stop criteria.
  - **Refs**: FR-T1, FR-T2, FR-T5, `plan §12`. **DoD**: one command runs both arms.
  - **⚠ Critical**: any uncontrolled difference (different model, prompt, or stop rule) makes
    the comparison meaningless. Hold everything constant except context strategy.
- [ ] **T8.2** (P0) Collect per-arm metrics from ledgers: total tokens (prompt+completion),
  files/text-units read, iterations, wall-clock, reached-root-cause (Y/N), fix-correct (Y/N).
  - **Refs**: FR-T3, assignment §5.5. **DoD**: metrics table generated programmatically.
- [ ] **T8.3** (P0) Write `reports/token_comparison.md`: side-by-side table + **explicit %
  savings** + verdict answering RQ6 & RQ7.
  - **Refs**: FR-T4, RQ6, RQ7. **DoD**: report present with numbers, not adjectives.
- [ ] **T8.4** (P1) Generate a bar chart to `assets/token_chart.*`; embed in README.
  - **Refs**: FR-T4.
- [ ] **T8.5** (P1) Provide `notebooks/experiment.ipynb` to reproduce the comparison.
  - **Refs**: FR-T5.
- [ ] **T8.6** (P1) Validate KPIs vs `prd §6` (≥50% token & file reduction, ≤ iterations).
  - **⚠ Critical**: if the graph arm does **not** win, do not fake numbers. Investigate why
    (naive baseline too weak? graph scope wrong? whole-file reads leaking?), fix, and re-run.
    An honest negative with analysis beats a fabricated positive — but most likely the leak is
    in the retriever (T5.7) or an over-stuffed `index.md` (T3.1).
- [ ] **T8.7** (P2) Report estimated **cost** ($) per arm using config token prices.
  - **Refs**: system-prompt §Research/results (cost analysis).

**Phase 8 DoD**: reproducible two-arm experiment; `token_comparison.md` + chart; KPIs met or
deviation explained with root-cause analysis.

---

## Phase 9 — Extensions & Original Initiatives  *(M5)*

**Entry Gate**: core flow works (Phases 5–8). **Exit Gate**: ≥1 extension per area, documented.
> Assignment §5.6 requires **at least one original extension per part**. Pick deliberately.

- [ ] **T9.1** (P1) **Suspect ranking** by centrality + proximity to failing tests (wire into
  Investigator).
  - **Refs**: FR-E1, RQ2. **DoD**: ranking function + test; used in a real run.
- [ ] **T9.2** (P1) **Dynamic `hot.md`** generated from `git diff` + `graph.json` (map changed
  lines → graph nodes → impacted neighbors).
  - **Refs**: FR-E2. **DoD**: `update_hot(diff, graph)` produces a focused hot page.
  - **⚠ Critical**: this is a strong, on-theme extension — but only valuable if the mapping
    from diff hunks to graph nodes is accurate. Validate on the real fix diff.
- [ ] **T9.3** (P2) **Impact report**: "what breaks if we change node X?" (reverse-dependency
  traversal).
  - **Refs**: FR-E4. **DoD**: `impact_of(graph, node_id)` + a sample report.
- [ ] **T9.4** (P2) **Doc-vs-behavior contradiction** detector (docstring/README claims vs
  graph/behavior).
  - **Refs**: FR-E3.
- [ ] **T9.5** (P2) **Before/after architecture comparison** (graph delta around the fix).
  - **Refs**: FR-E5, RQ1.
- [ ] **T9.6** (P1) Document all extensions in `reports/extensions.md` with examples + RQ8
  ("what we'd add next").
  - **Refs**: RQ8.
  - **⚠ Critical**: an extension that is coded but undocumented earns little. Each needs a
    short rationale, a runnable example, and a sentence on the insight it produced.

**Phase 9 DoD**: ≥1 extension per major area implemented, tested, and documented with examples.

---

## Phase 10 — Documentation & Final Audit  *(M6)*

**Entry Gate**: all prior phase DoDs met. **Exit Gate**: README complete; verdict = READY.

### 10.A README (assignment §8 — hard requirement)
- [ ] **T10.1** (P0) Write `README.md` covering: repo choice + **justification**; bug
  description; **RQ1–RQ8** answers; architecture overview; agent workflow; Graphify+Obsidian
  usage; reverse-engineering process; bug + **root cause** + fix; before/after; token
  efficiency; extensions; **clear run instructions**.
  - **Refs**: assignment §8, RQ1–RQ8. **DoD**: every §8 bullet present.
  - **⚠ Critical**: the README is graded heavily. A great codebase with a thin README reads as
    incomplete. Ensure each RQ is answered **explicitly**, not implied.
- [ ] **T10.2** (P0) Embed visuals: block diagram, OOP diagram, multi-agent flow, token chart,
  Obsidian screenshots.
  - **Refs**: assignment §8 (visual elements). **DoD**: images render from `assets/`.
- [ ] **T10.3** (P1) Add installation/usage/config/examples/troubleshooting/credits/license.
  - **Refs**: system-prompt §Mandatory docs.

### 10.B Repo hygiene & docs sync
- [ ] **T10.4** (P0) Sync `prd.md`/`plan.md`/`todo.md` ↔ `docs/` (single canonical copy).
- [ ] **T10.5** (P1) Fill `docs/PRD_multiagent.md` and `docs/PRD_token_ledger.md` fully.
- [ ] **T10.6** (P1) Ensure `LICENSE` + credits/attribution (Graphify, BugsInPy, libraries).
  - **⚠ Critical**: BugsInPy/target code carries its own license — attribute it; do not
    relicense someone else's project under yours.

### 10.C Final audit (run the checklist in §6 below)
- [ ] **T10.7** (P0) `uv run ruff check .` = 0; `uv run pytest --cov=src` ≥ 85%.
- [ ] **T10.8** (P0) Secret scan: no `.env`, keys, tokens, or PII in Git or ledgers.
- [ ] **T10.9** (P0) Fresh-clone dry run: follow README from scratch; it must work.
  - **⚠ Critical**: "works on my machine" is not done. Verify on a clean checkout (G.1).
- [ ] **T10.10** (P0) Produce the final readiness verdict (§6).

**Phase 10 DoD**: README complete with visuals; docs synced; quality gates green; fresh-clone
verified; verdict recorded.

---

## 3. Cross-Cutting Tasks (apply across all phases)

### 3.1 Testing (NFR-6, `plan §13`)
- [ ] **X.1** (P0) TDD where practical (Red→Green→Refactor) for SDK/services.
- [ ] **X.2** (P0) Unit tests: graph loader/query/metrics, vault builder/hot, budget guard,
  gatekeeper (mock LLM), ledger aggregation, suspect ranking, impact report.
- [ ] **X.3** (P0) Integration test: end-to-end workflow on a **tiny synthetic buggy fixture**
  with a **scripted/mocked LLM**, asserting routing, budget caps, and red→green.
  - **⚠ Critical**: do not depend on the real external repo or real LLM in CI — flaky + costs.
- [ ] **X.4** (P0) Cover failure paths: cap breaches, retry exhaustion, malformed `graph.json`,
  missing config, subprocess test failures.
- [ ] **X.5** (P1) Keep coverage ≥85% continuously; add tests with each new module (G.8).

### 3.2 Config & security (NFR-4, `plan §14`)
- [ ] **X.6** (P0) Re-verify no hardcoded tunables on every PR (grep for model names, URLs).
- [ ] **X.7** (P0) Validate all external inputs (paths, node ids); guard against unsafe path
  joins into `data/`.
- [ ] **X.8** (P0) Confirm logs/ledgers are redacted before committing as evidence (G.10).

### 3.3 Observability (NFR-8)
- [ ] **X.9** (P1) Structured logs + per-run ledger persisted to `results/<run_id>/`.
- [ ] **X.10** (P2) Optional: LangGraph/LangSmith trace for the demo run.

### 3.4 Reproducibility (NFR-9)
- [ ] **X.11** (P0) Pin deps (`uv.lock`); set seeds; record Graphify + model versions.
- [ ] **X.12** (P1) One-command paths for: graphify-load, build-vault, investigate, experiment.

---

## 4. Critical Review / Red-Team Checklist (challenge your own work)

Run this **before** declaring any milestone done. Each is a known way this project silently fails.

- [ ] **C.1** Does the block diagram merely mirror the folder tree? → If yes, **not** reverse
  engineering (Phase 4 fails). Re-derive from graph edges.
- [ ] **C.2** Does any "graph-mode" path read source files outside the budget-gated Retriever?
  → If yes, the token thesis is compromised (G.4 analogue). Trace every read.
- [ ] **C.3** Is the naive baseline a **straw man** (artificially dumb) or **artificially
  strong** (also focused)? Either invalidates the comparison. It must be a fair, unfocused
  raw-file reader with the same model/task.
- [ ] **C.4** Is the fix a **root-cause** fix or a **symptom mask** (try/except, special-case)?
  → Masks fail RQ5/Phase 7.
- [ ] **C.5** Does "tests pass" include a **regression** check, or only the target test?
- [ ] **C.6** Are God-nodes/centrality claims **backed by numbers**, or asserted?
- [ ] **C.7** Did you peek at the official patch and reverse-justify it? → Dishonest; redo
  the trail or disclose it.
- [ ] **C.8** Is `hot.md` **stale** relative to the actual investigation state?
- [ ] **C.9** Do all LLM calls go through the Gatekeeper and land in the ledger? Count them.
- [ ] **C.10** Are token numbers **measured** (ledger) or **estimated/guessed**? Must be measured.
- [ ] **C.11** Is any secret present in Git history, `.env`, logs, or committed ledgers?
- [ ] **C.12** Does the project install + run on a **fresh clone** using only `uv` + README?
- [ ] **C.13** Are files bloated (>150 code lines) or duplicating logic? Split/extract.
- [ ] **C.14** Are RQ1–RQ8 each **explicitly** answered in README/reports/Obsidian?
- [ ] **C.15** Is every committed extension **documented with an example** (else low value)?
- [ ] **C.16** Did an edit break **downstream** callers/implementers/tests (G.7)? Re-scan.

---

## 5. Risk Gates (do not pass a phase with an open red risk)

| Gate | Risk (prd §14) | Blocks phase | Mitigation owner action |
|---|---|---|---|
| RG1 | R1 dependency hell | 1→2 | Switch to fallback repo if env unstable |
| RG2 | R5 non-reproducible bug | 1→2 | Re-run ≥2×; pin seeds; else change bug |
| RG3 | R3 Graphify cost/time | 2 | Run once; scope subtree; persist artifacts |
| RG4 | R2 rate/token limits | 5→6 | Enforce budget caps; small bug; cache queries |
| RG5 | R4 over-engineered flow | 5 | Keep 6 workers; HITL; staged calls |
| RG6 | R6 weak savings delta | 8 | Fair baseline; fix retriever leaks; re-run |
| RG7 | R7 secrets leakage | 10 | Redaction + secret scan before submission |

---

## 6. Final Readiness Checklist (system-prompt audit)

Answer exactly one: **READY** / **CONDITIONALLY READY** / **NOT READY**, then justify each:

- [ ] Documentation completeness (README §8, RQ1–RQ8, per-mechanism PRDs).
- [ ] Architecture correctness (C4/diagrams; graph-derived, not folder-derived).
- [ ] SDK usage (all logic behind `sdk/api.py`; CLI/agents thin) — G.3.
- [ ] API Gatekeeper usage (all LLM calls mediated; ledgered) — G.4.
- [ ] No duplicated logic; one responsibility per module.
- [ ] File-size/modularity (≤150 code lines where practical).
- [ ] Tests + **≥85%** coverage on `src/`; failure paths covered.
- [ ] Ruff **zero** violations.
- [ ] Config/secrets safety (`.env-example`; no secrets committed; redacted ledgers).
- [ ] `uv` usage throughout (no pip/venv).
- [ ] README quality (rich, visual, run instructions).
- [ ] Results/visualizations/costs (token report, chart, cost estimate).
- [ ] Deliverables present (Graphify outputs, vault, diagrams, reports, before/after, extensions).
- [ ] Git/license/credits/attribution (Graphify, BugsInPy, libs).

---

## 7. Backlog / Deferred (record, don't lose)

- [ ] **B.1** (P2) Multi-bug or multi-repo comparison as a second case study.
- [ ] **B.2** (P2) Cache layer for graph queries to further cut tokens.
- [ ] **B.3** (P2) Auto-generate the README architecture section from `graph.json`.
- [ ] **B.4** (P2) LangSmith dashboard export for the demo run.
- [ ] **B.5** (P2) CI workflow (lint+test) — note: keep `uv`-based; out of core scope.

> **Closing note (be critical):** the grade hinges on **proof**, not effort. Every claim
> (architecture, root cause, token savings) must be backed by a committed artifact a reviewer
> can open. If you cannot point to the file that proves a statement, the statement is not done.