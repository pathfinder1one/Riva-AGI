# Riva-AGI — Project Context (`context.md`)

## 1. Project Overview & Vision
**Riva-AGI** is an autonomous, low-latency multi-agent orchestration and voice interaction platform designed to execute complex, multi-domain user goals (code generation, research, system operations, design, QA, and documentation) with high reliability and minimal token overhead.

The platform is partitioned into independent tracks:
- **Track 1: Multi-Agent Orchestration Core** (Owner: Chirag Tejasvi) — Workflow graph, task routing, DAG dependency scheduling, blackboard memory, quality gates, and tool authorization.
- **Track 2: Voice & Speech Engine** — Full-duplex WebSocket STT/TTS audio streaming (Web Audio live browser interface connected to port 8000).
- **Track 3: RAG & Knowledge Base** — Enterprise document ingestion, vector retrieval, and contextual embedding search.
- **Track 4: Tool Calling & Sandboxing** — File manipulation, terminal command execution, and security risk gating.

---

## 2. Evolution & Conversation History Context

### Genesis & Key Breakthroughs
1. **Live Gemini API vs REST Tradeoffs**:
   - Initial exploration examined Google GenAI Live WebSocket models (`gemini-3.8-live`, `gemini-3.1-flash-live-preview`) which offer unlimited RPM/RPD but stream natural speaking audio tempo (~20-25s for 150 words).
   - Standard REST models (`gemini-3.5-flash-lite`) deliver fast text generation (1.49s–4.4s) but face rate limits.
   - Dual-engine fallback was implemented to balance speed and quota resilience.

2. **Zero-LLM Core Decision (Laya Engine & Deterministic DAG)**:
   - To avoid burning tokens and wasting 1.5s+ on simple routing decisions, the **Laya Non-Autoregressive Decision Engine** was integrated (<35ms, 0 tokens) along with Kahn’s deterministic topological DAG scheduler (<1ms).

3. **End-to-End Voice & Tool Verification**:
   - Live browser interface on `http://localhost:8000` was verified with Web Audio, successfully delegating live audio transcriptions to `run_orchestrator` and executing tool calls (e.g. `duckduckgo_search` for latest AI research trends).

4. **The 9-Pillar Multi-Agent Upgrade**:
   - Comprehensive audit identified 5 architectural gaps and 4 high-impact advanced features.
   - Refined into a pure technical 9-pillar architecture without corporate fluff:
     - Root Task Coordinator & Domain Workstreams (Engineering, Research, Creative)
     - Parallel DAG Waves (`compute_execution_waves`)
     - Thread-safe Shared Whiteboard (`WhiteboardContext` & `ArtifactHistory` with `difflib`)
     - Concurrent Async Worker Pool (`AsyncWorkerPool`)
     - Bottom-up Aggregator & Executive Synthesizer
     - Self-Healing Auto-Rollback Transaction Gate in `SecurityGate`
     - Clean RAG Hook (`knowledge_agent`)

---

## 3. Core Operating Rules & Boundaries
1. **Strict Track 1 Confines**: Do NOT touch audio/speech models. Orchestration communicates exclusively via standard schemas (`InputData` $\rightarrow$ `AgentResponse`).
2. **Zero Hardcoded Hacks**: No mock data dictionaries, no artificial human corporate roleplay (`CEO`, `PM`). All domain profiles and routing rules are config/registry driven.
3. **Preserve Regression Safety**: All existing unit and integration tests must pass continuously.
