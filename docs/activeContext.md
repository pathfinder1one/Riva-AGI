# Riva-AGI — Active Execution Context (`activeContext.md`)

## 1. Current Active Focus
We have completed all **5 Phases of the 9-Pillar Implementation Plan** for Track 1 Multi-Agent Orchestration:
- **Completed**:
  - **Phase 1 (Pillars 3 & 7)**: Shared Context Whiteboard & Diff Tracking (`whiteboard.py`, `test_whiteboard_context.py`, injected into `main.py`).
  - **Phase 2 (Pillars 1 & 6)**: Parallel DAG Waves & Async Worker Pool (`compute_execution_waves` in `dag_scheduler.py`, `AsyncWorkerPool` in `executor.py`, `test_parallel_dag_execution.py`).
  - **Phase 3 (Pillars 4 & 8)**: Bottom-Up Aggregator & Deliverable Synthesizer (`aggregator.py`, `test_multi_agent_aggregator.py`, wired into `main.py`).
  - **Phase 4 (Pillar 9)**: Self-Healing & Transactional Auto-Rollback Gate in `security.py` (`WorkspaceTransactionManager`, wired into `reviewer_node` in `main.py`, `test_self_healing_rollback.py`).
  - **Phase 5 (Pillars 2 & 5)**: Hierarchical Domain Decomposition in `planner.py` & RAG Hook in `knowledge_agent.py` (`test_hierarchical_planning.py`).
- **Next Focus**:
  - Run full test suite validation.
  - End-to-end multi-agent verification run.

---

## 2. Recent Decisions Log
1. **Zero Corporate Metaphor in Code**:
   - Replaced all conceptual PRD analogies (`CEO`, `PM`, `manager`) with pure technical software architecture (`RootCoordinator`, `DomainPlanner`, `TaskExecutor`).
   - Removed artificial class hierarchies in favor of config-driven domain mappings in `config/`.
2. **Dual-Graph Separation**:
   - LangGraph `StateGraph` owns macro pipeline lifecycle, retry loops, and quality gates.
   - Kahn's `DAGScheduler` owns dynamic subtask dependencies and execution wave slicing inside the executor.
3. **Quota & Latency Alignment (Google AI Studio Tier Optimization)**:
   - Live API preview models (`gemini-3.8-live`) are categorized under `Live API` with audio dialog streaming, which was forcing speech-cadence generation (~25s) and truncating outputs.
   - Text agents configured to `gemini-3.5-flash-lite`, which provides **500 RPD** quota, sub-second generation (0.9s - 2.8s), and full 8192 token limit.
4. **Dedicated Documentation Directory**:
   - All `.md` project tracking files (except root `README.md`) preserved cleanly in `docs/`:
     - [`docs/context.md`](file:///c:/Coding/New%20folder/github%20riva/Riva-AGI/docs/context.md)
     - [`docs/progress.md`](file:///c:/Coding/New%20folder/github%20riva/Riva-AGI/docs/progress.md)
     - [`docs/skills.md`](file:///c:/Coding/New%20folder/github%20riva/Riva-AGI/docs/skills.md)
     - [`docs/architecture.md`](file:///c:/Coding/New%20folder/github%20riva/Riva-AGI/docs/architecture.md)
     - [`docs/activeContext.md`](file:///c:/Coding/New%20folder/github%20riva/Riva-AGI/docs/activeContext.md)

---

## 3. Verification & Stability Status
- **Voice Frontend Gateway**: Running live on `http://localhost:8000` (FastAPI + Three.js 3D Orb + WebSocket Web Audio Bridge).
- **Test Suite**: 105/105 tests passing (100% pass rate) across 16 test suites.
- **Main Repo Sync**: Merged `upstream/main` with PR #37 (autonomous tool calling) and PR #35 (Tavily search & streaming hardening). User's exact 3-tier KeyManager config preserved.
- **Voice-to-Tool Integration**: `delegate_to_orchestrator`, `open_application`, and `get_latest_news` active in live voice gateway.

