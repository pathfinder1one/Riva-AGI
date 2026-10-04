# Riva-AGI — Orchestration Master Plan

Track 1 · Multi-Agent Orchestration — single reference for current state, confirmed issues, integration status, and the build order. Owner: Chirag Tejasvi.

📅 2026-10-04 📁 orchestration/orchestrator/, orchestration/agents/ 🔗 PRD: Riva-AGI overall + Orchestration Engine PRD

- [1 · Scope](#scope)
- [2 · Current state](#state)
- [3 · Integration status](#integration)
- [4 · Confirmed issues](#issues)
- [5 · Architecture principles](#principles)
- [6 · Build order](#plan)
- [7 · Avoid](#avoid)
- [8 · Latency budget](#latency)
- [9 · Safety gate](#safety)
- [10 · Production checklist](#checklist)

## 1Scope — what's mine, what isn't

Orchestration owns **who does what, in what order, with what state** — not the agents' internal LLM logic, not tool implementations, not model adapters.

| Mine (Orchestration) | Not mine |
| --- | --- |
| CEO / PM hierarchy, task routing, dependency scheduling, parallel execution, shared state, retry/escalation, aggregation, AgentRegistry, schemas/contracts | Agent internals & LLM calls (Agents/LLM track), tool execution (Tool-Calling track), model/provider adapters (Integrations track), RAG retrieval (RAG track) |

Working rule

Orchestration calls other tracks' work through the same interface every time: register as an agent in `AgentRegistry`, accept `InputData`, return `AgentResponse`. Never reach into another track's internals.

Terminology note

"CEO" and "PM" below are architecture-role labels carried over from the Orchestration PRD's own wording for a 3-tier agent hierarchy — **Root Coordinator (CEO-tier) → Domain Manager (PM-tier) → Executor**. They name code-level responsibilities, not an org chart to build literally. If this document is ever handed to another AI as a build prompt, read "CEO agent" as "the top-level coordinator agent" and "PM agent" as "a mid-level domain-manager agent" — not as corporate roles.

## 2Current state of the code

What exists today in `orchestration/`, verified file by file against the Orchestration PRD.

| Piece | Status | Note |
| --- | --- | --- |
| Schemas (`InputData`, `AgentResponse`, `ToolCall`/`ToolResult`) | done | Clean, typed, already supports text/audio/image/multimodal |
| AgentRegistry + decorator registration | done | Works, agent_level tags (CEO/MANAGER/TASK_DOER) exist but unused for CEO |
| TaskStateManager (per-task history) | partial | Tracks owner/status/history — not yet a true shared whiteboard |
| LangGraph pipeline (intent → plan → execute → review) | done | Runs end to end, tests pass |
| 11 Task-Doer agent stubs | done | Registered, callable, tool-calling now wired in by teammate's PR |
| Root coordinator agent (CEO-tier) | missing | Its job is split across intent_classifier + planner + executor |
| Domain-manager layer (PM-tier) | missing | No agent owns a domain and spawns its own task-doers |
| Dynamic agent factory | missing | Agents are hardcoded files imported in main.py, not JSON-spawned |
| Dependency graph / parallel execution | missing | Plan is a flat list, always sequential |
| Retry cap + escalation to CEO | missing | Reviewer "rejected" loops back with no limit |

## 3Integration status with other tracks

| Track | Status | Note |
| --- | --- | --- |
| Agents / LLM & Tool Calling | connected | Teammate's PR wires real tool execution into `llm.py` — pending senior merge, but build against it now |
| Voice / Speech (STT-TTS) | connected | Already hooked into the orchestrator |
| RAG / Knowledge Base | next | Not connected yet — this is the next integration task |
| Vision / camera (future) | designed-for | `InputData.input_type` already supports IMAGE and MULTIMODAL — no schema change needed when it arrives |

### Connecting RAG — concrete steps

1. RAG team registers a `knowledge_agent` in `AgentRegistry` — same pattern as `coder.py`/`researcher.py`: takes `InputData`, returns `AgentResponse` with retrieved context as `content`.
2. Update the intent-classifier's system prompt so `knowledge_agent` is a valid `target_agent` for factual/lookup queries.
3. Add knowledge-style keywords to `config/routing.json` so the rule-based fallback router can also reach it.
4. Decide where retrieved context lands: returned straight to the user, or passed to another agent (e.g. a "writer") to phrase the final answer — this is a graph-routing decision, not a RAG-side one.

### Staying compatible with future modalities (camera, etc.)

No new modality should ever require touching the orchestrator's core graph. A camera feed is just another producer of `InputData` with `input_type: IMAGE` (or a new event-trigger entry point, see §5). As long as whatever team builds it packages its input into the existing schema and registers its agent through `AgentRegistry`, it plugs in without a rewrite.

## 4Confirmed issues (verified against actual code)

| Issue | Severity | Status |
| --- | --- | --- |
| Planner generates a structured subtask per agent, but `create_agent_node()` hands the worker the *original user prompt* instead — the planned instruction never reaches the agent | critical | Open — fix first, before anything else |
| Reviewer's rejection feedback isn't re-injected into the next executor/worker call — correction signal is lost | critical | Open |
| `seo_specialist` and `dummy_system_agent` both resolve to API key role `WORKER_10` (acknowledged in a code comment) | partial | Teammate's PR adds a named alias, but only if the named env var is actually set — collision persists on the fallback path |
| No retry counter / escalation — reviewer "rejected" loops to executor indefinitely | open | Open |
| No dependency graph — plan is a flat list, independent steps can't run in parallel | open | Open |
| `execute_command` tool is now live (via teammate's PR) for coder/devops/qa_tester with no permission or sandbox gate | critical | New — raised by the PR, must land before merge |
| No literal CEO node — its responsibilities are split across intent_classifier/planner/executor | partial | Open |

## 5Architecture principles for this build

- **Three separate abstractions, never merged:** which *agent* acts, which *model* it uses, and what *orchestrator* state it runs in. `llm.py`'s model mapping should move to config, not live hardcoded inside the orchestration folder.
- **Event-driven entry point, not just request–response.** A sensor trigger (face detected, a webhook) isn't a chat prompt — the orchestrator needs an entry point that isn't "user typed something," feeding the same `InputData` contract from a different source.
- **Identity resolution before intent classification** when the input carries a known actor (face match, logged-in session) — so "tell me about myself" resolves to the right person before any routing decision is made.
- **Everything config-driven, nothing hardcoded.** Agent↔model mapping, routing keywords, risk tiers — all in config files an engineer can edit without touching Python.
- **Risk-tiered actions.** Every tool/action carries a risk label (read-only / reversible / irreversible) used by the permission gate (§9).

## 6Build order — start now, independent of the pending PR

Seniors merge the tool-calling PR on their own schedule. Build against its shape now; don't block on the merge.

1. **Fix the planner → executor → worker handoff.** Pass the worker its planned subtask (structured `TaskSpec`), not the raw original prompt. Everything below is wasted effort until this is fixed.
2. **Introduce a `TaskSpec` message contract:** `{task_id, agent, prompt, depends_on, context, status}` — replaces the flat plan list.
3. **Re-inject reviewer feedback** into the next executor/worker call on rejection, instead of dropping it.
4. **Add a retry counter + escalation path.** After *n* rejected retries, escalate up rather than looping forever.
5. **Build the dependency-aware scheduler.** Steps with no pending `depends_on` run in parallel; dependent steps wait.
6. **Build the actual root-coordinator + domain-manager layer** on top of the now-fixed execution chain — the coordinator parses intent/builds the WBS, each domain manager owns one domain and spawns its own task-doers.
7. **Connect RAG** as a registered agent (§3).
8. **Collapse intent_classifier + planner into one coordinator-level call** where it reduces hops without losing clarity (keep executor's routing decision as plain code, not an LLM call — see §8).
9. **Add the permission/risk gate** for destructive tool calls (§9) — needed before the tool-calling PR merges.
10. **Bottom-up aggregation**: worker → domain-manager synthesis → root-coordinator synthesis → final, replacing the flat reviewer-only path.

## 7Avoid

- Don't target single-digit-millisecond latency for any LLM-based decision — physically not achievable even with the smallest model (see §8).
- Don't let destructive/physical actions (shutdown, lab control, merging a PR) execute without a confirmation/permission step.
- Don't hardcode agent↔model mappings or routing tables in Python — config files, hot-editable.
- Don't implement tool execution, model adapters, or RAG retrieval yourself — call them through the registry interface.
- Don't cache *results* of action/side-effect tasks (file creation, system commands) — only cache the *routing decision*, and only cache RAG/knowledge results when scoped by user identity with an invalidation path.

## 8Latency budget — realistic numbers

Reality check

1–2ms or 5–6ms is not achievable for any LLM-based call — network round-trip alone is typically 20–50ms, and even the smallest model adds real inference time on top.

| Path | Realistic budget | How |
| --- | --- | --- |
| Fast/simple routing decision | 1–10ms | Traditional classifier or embedding-similarity lookup — not a generative LLM call |
| LLM-based planning/reasoning | 200ms – 2s | Accept this range for complex multi-step planning; don't force it lower |
| "Next step" routing inside executor | \~0ms | This should be plain code reading `plan[current_step]`, not an LLM call at all |

## 9Permission / risk gate for destructive actions

Needed once physical/system actions (lab shutdown, self-shutdown, `execute_command`) are live — and they already are, via the teammate's tool-calling PR.

- Tag every tool/action with a risk level: **read-only**, **reversible**, **irreversible**.
- Irreversible actions require an explicit confirmation/authorization step inside the orchestrator before execution — never auto-execute on an LLM's say-so alone.
- Log every action taken (who asked, what ran, approved or not) — an immutable audit trail, especially for anything touching real hardware.

## 10Production-readiness checklist

- No hardcoded agent↔model mapping — config-driven, hot-editable
- No hardcoded routing tables where a registry lookup would do
- `TaskSpec` handoff fixed and tested (unit + integration)
- Retry cap + escalation path implemented, not just designed
- Permission gate in place before any destructive tool goes live in production
- Dependency-aware scheduler with real parallel execution, not fake-sequential
- Every new track (RAG, vision, etc.) integrates through `AgentRegistry` + `InputData`/`AgentResponse` — no special-cased wiring per track
- Audit log for every action with a risk tag above read-only

Riva-AGI · Multi-Agent Orchestration · compiled from the Orchestration PRD, the overall Riva-AGI PRD, direct code review of the repo, and teammate PR review.