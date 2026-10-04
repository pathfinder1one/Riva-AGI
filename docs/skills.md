# Riva-AGI — Skills & Tool Capabilities Matrix (`skills.md`)

## 1. Agent Registry & Domain Specializations

| Agent Name | Technical Domain | Level | Registered Capabilities & Tools |
| :--- | :--- | :--- | :--- |
| **`coder`** | Engineering | `TASK_DOER` | Writing, refactoring, and fixing code. Tools: `write_file`, `edit_file`, `read_file`, `execute_command`. |
| **`devops`** | Engineering | `TASK_DOER` | Infrastructure, Docker, CI/CD, system ops. Tools: `execute_command`, `read_file`, `write_file`. |
| **`security_auditor`**| Engineering | `TASK_DOER` | Static security analysis, vulnerability audit, permissions. Tools: `read_file`, `execute_command`. |
| **`qa_tester`** | Verification | `TASK_DOER` | Unit test execution, syntax validation, test plan creation. Tools: `execute_command`, `read_file`. |
| **`researcher`** | Research & Data | `TASK_DOER` | Web search, tech documentation extraction. Tools: `duckduckgo_search`, `fetch_web_page`. |
| **`data_analyst`** | Research & Data | `TASK_DOER` | Log analysis, latency profiling, metric aggregation. Tools: `read_file`, `stats_utils`. |
| **`knowledge_agent`** | Knowledge (RAG) | `TASK_DOER` | Vector search, enterprise doc retrieval. Tools: `search_knowledge_base`, `retrieve_document_chunks`. |
| **`writer`** | Content & Docs | `TASK_DOER` | Markdown reports, API documentation, summaries. Tools: `write_file`, `read_file`. |
| **`designer`** | Creative | `TASK_DOER` | UI/UX specifications, JSON schemas, component layouts. |
| **`reasoner`** | Reasoning | `TASK_DOER` | Complex logic deconstruction, mathematical proofs, tradeoff analysis. |
| **`seo_specialist`** | Optimization | `TASK_DOER` | Metadata optimization, keyword analysis, web structure analysis. |

---

## 2. Orchestration System Skills & Capabilities

### Core Engines
- **Laya Non-Autoregressive Decision Engine**:
  - Sub-35ms intent classification and complexity rating.
  - Zero token consumption for baseline routing.
  - Non-autoregressive quality evaluation in Reviewer gate.
- **Kahn Deterministic DAG Wave Scheduler**:
  - 0ms cycle detection and dependency graph validation.
  - Wave slicing: decomposes DAG into mutually independent, concurrently executable sets of `TaskSpec`s.
- **Shared In-Memory Whiteboard (`WhiteboardContext`)**:
  - Typed blackboard memory for cross-agent artifact exchange.
  - Upstream artifact injection: feeds exact prerequisite outputs into downstream agent prompts.
  - `difflib.unified_diff` tracking across artifact revisions.
- **Concurrent Async Worker Pool (`AsyncWorkerPool`)**:
  - Non-blocking execution of independent tasks across thread and asyncio pools.
  - Caps maximum concurrency to prevent API rate limits.
- **Bottom-Up Multi-Agent Aggregator**:
  - Synthesizes multi-step execution traces into unified executive Markdown deliverables.
  - Extracts workspace file changes and generates clickable `file:///` links.
- **Security & Auto-Rollback Gate (`SecurityGate`)**:
  - 3-tier risk classification: `READ_ONLY`, `REVERSIBLE`, `IRREVERSIBLE`.
  - Command blacklisting (`rm -rf`, `format`, `dd`).
  - Transactional file snapshots: reverts broken or syntax-invalid file modifications.
