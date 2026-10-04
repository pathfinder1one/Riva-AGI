"""
Researcher Agent — orchestration/agents/researcher.py
======================================================
Autonomous research agent capable of executing live DuckDuckGo web searches
and synthesizing findings via Gemini Flash-Lite.
"""
import logging
import time
import uuid
from typing import List

from orchestration.orchestrator.registry import registry, AgentCapabilities
from orchestration import InputData, AgentResponse, ResponseStatus
from orchestration.orchestrator.config import key_manager
from orchestration.orchestrator.llm import call_gemini
from orchestration.orchestrator.schemas.tool import ToolCall
from orchestration.tools.builtin.web_tools import web_search

logger = logging.getLogger(__name__)

@registry.register("researcher", AgentCapabilities(description="Handles internet research and data gathering.", tools=["web_search"], agent_level="TASK_DOER"))
def researcher_agent(task_data: InputData) -> AgentResponse:
    logger.info("Routing to Researcher Agent")
    start_time = time.time()
    
    prompt_text = task_data.text_content or ""
    my_key = key_manager.get_api_key_for_role("RESEARCHER")
    tool_calls: List[ToolCall] = []

    # Check if real-time web search is required
    search_keywords = ["pehle", "yesterday", "recent", "today", "news", "happened", "latest", "ago", "hua", "current", "weather"]
    needs_search = any(k in prompt_text.lower() for k in search_keywords)
    
    augmented_prompt = prompt_text
    if needs_search:
        try:
            logger.info(f"[Researcher Agent] Executing web_search for: {prompt_text}")
            search_snippets = web_search(query=prompt_text, max_results=3)
            tool_calls.append(
                ToolCall(
                    call_id=str(uuid.uuid4()),
                    tool_name="web_search",
                    parameters={"query": prompt_text, "max_results": 3},
                    expected_return_type="str"
                )
            )
            augmented_prompt = f"User Request: {prompt_text}\n\nLive Search Information:\n{search_snippets}\n\nPlease summarize and provide a helpful, factual answer."
        except Exception as e:
            logger.warning(f"Web search execution error: {e}")

    sys_prompt = "You are the expert researcher agent for Riva-AGI. Provide concise, factual, and accurate answers."
    
    try:
        content = call_gemini(
            prompt=augmented_prompt, 
            api_key=my_key, 
            system_instruction=sys_prompt, 
            agent_id="researcher"
        )
    except Exception as e:
        logger.error(f"Researcher LLM generation failed: {e}")
        content = f"Research Error: {e}"
    
    execution_time = (time.time() - start_time) * 1000
    
    return AgentResponse(
        agent_id="researcher",
        status=ResponseStatus.SUCCESS if not content.startswith("Research Error") else ResponseStatus.FAILURE,
        content=content,
        tool_calls=tool_calls,
        execution_time_ms=execution_time,
        metadata={"processed_modality": task_data.input_type.value, "tools_used": len(tool_calls)}
    )