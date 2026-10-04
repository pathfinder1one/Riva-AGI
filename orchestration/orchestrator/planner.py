"""
Planner Agent — orchestration/orchestrator/planner.py
======================================================
Deconstructs complex requests into a DAG ExecutionPlan containing TaskSpecs.
"""
import json
import logging
import time
from typing import Dict, Any, List, Optional
from orchestration.orchestrator.registry import registry, AgentCapabilities
from orchestration import InputData, AgentResponse, ResponseStatus
from orchestration.orchestrator.config import key_manager
from orchestration.orchestrator.llm import call_gemini

logger = logging.getLogger(__name__)

def clean_json_text(text: str) -> str:
    cleaned = (text or "").strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

DOMAIN_WORKSTREAMS = {
    "engineering": {
        "agents": ["coder", "devops", "security_auditor"],
        "keywords": ["code", "script", "develop", "api", "database", "backend", "deploy", "docker", "server", "fastapi"]
    },
    "verification": {
        "agents": ["qa_tester", "security_auditor"],
        "keywords": ["test", "verify", "audit", "benchmark", "validate", "qa", "pytest"]
    },
    "research_analysis": {
        "agents": ["researcher", "data_analyst", "knowledge_agent"],
        "keywords": ["research", "search", "docs", "analyze", "metrics", "knowledge", "trend", "retrieval"]
    },
    "content_docs": {
        "agents": ["writer", "designer"],
        "keywords": ["write", "doc", "readme", "report", "design", "ui", "mockup", "guide"]
    }
}

def detect_workstreams(goal: str) -> List[str]:
    """Detects technical domain workstreams present in the user goal."""
    lower = goal.lower()
    matched = []
    for domain, spec in DOMAIN_WORKSTREAMS.items():
        if any(kw in lower for kw in spec["keywords"]):
            matched.append(domain)
    return matched or ["engineering"]

def plan_hierarchical_tasks(goal: str) -> List[Dict[str, Any]]:
    """
    Deterministic Hierarchical Task Decomposition (Pillar 2).
    Generates cross-domain DAG tasks based on identified workstreams.
    """
    domains = detect_workstreams(goal)
    tasks = []
    prev_task_id = None

    task_idx = 1
    # 1. Research / Knowledge Workstream if needed
    if "research_analysis" in domains:
        tid = f"task_{task_idx:02d}"
        agent = "knowledge_agent" if "knowledge" in goal.lower() else "researcher"
        tasks.append({
            "task_id": tid,
            "agent": agent,
            "domain": "research_analysis",
            "subtask": f"Research technical specifications and documentation for: {goal}",
            "depends_on": []
        })
        prev_task_id = tid
        task_idx += 1

    # 2. Engineering Workstream
    if "engineering" in domains or not tasks:
        tid = f"task_{task_idx:02d}"
        deps = [prev_task_id] if prev_task_id else []
        tasks.append({
            "task_id": tid,
            "agent": "coder",
            "domain": "engineering",
            "subtask": f"Implement core logic and files for: {goal}",
            "depends_on": deps
        })
        eng_task_id = tid
        task_idx += 1
    else:
        eng_task_id = prev_task_id

    # 3. Verification & Content Workstreams (can run in parallel!)
    if "verification" in domains:
        tid = f"task_{task_idx:02d}"
        deps = [eng_task_id] if eng_task_id else []
        tasks.append({
            "task_id": tid,
            "agent": "qa_tester",
            "domain": "verification",
            "subtask": f"Create and execute test suite verifying implementation of: {goal}",
            "depends_on": deps
        })
        task_idx += 1

    if "content_docs" in domains:
        tid = f"task_{task_idx:02d}"
        deps = [eng_task_id] if eng_task_id else []
        tasks.append({
            "task_id": tid,
            "agent": "writer",
            "domain": "content_docs",
            "subtask": f"Author comprehensive documentation and README for: {goal}",
            "depends_on": deps
        })
        task_idx += 1

    return tasks

@registry.register("planner", AgentCapabilities(description="Plans and breaks down complex tasks into a hierarchical DAG.", tools=["plan"], agent_level="MANAGER"))
def planner_agent(task_data: InputData) -> AgentResponse:
    logger.info("Routing to Planner Agent")
    start_time = time.time()
    
    my_key = key_manager.get_api_key_for_role("PLANNER")
    sys_prompt = """You are the Planner in an Agentic AI system.
Your job is to read the user's complex goal and break it down into a step-by-step DAG Execution Plan.
Each step must be assigned to one of the specialized agents:
'coder', 'writer', 'designer', 'qa_tester', 'data_analyst', 'devops', 'security_auditor', 'seo_specialist', 'researcher', 'reasoner', 'knowledge_agent'.
You MUST output ONLY a valid JSON array of objects with the following schema:
[
  {
    "task_id": "task_01",
    "agent": "coder",
    "subtask": "detailed instruction for the coder",
    "depends_on": []
  }
]"""
    
    prompt = task_data.text_content or ""
    try:
        content = call_gemini(
            prompt=prompt, 
            api_key=my_key, 
            system_instruction=sys_prompt, 
            agent_id="planner"
        )
    except Exception as e:
        logger.warning(f"Planner LLM failed ({e}). Using hierarchical deterministic decomposition.")
        content = ""

    # Validate JSON or build fallback
    cleaned = clean_json_text(content)
    is_valid = False
    if cleaned:
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list) and len(parsed) > 0:
                is_valid = True
        except Exception:
            is_valid = False

    if not is_valid:
        hierarchical_plan = plan_hierarchical_tasks(prompt)
        content = json.dumps(hierarchical_plan, indent=2)

    execution_time = (time.time() - start_time) * 1000
    
    return AgentResponse(
        agent_id="planner",
        status=ResponseStatus.SUCCESS,
        content=content,
        tool_calls=[],
        execution_time_ms=execution_time,
        metadata={"processed_modality": task_data.input_type.value}
    )
