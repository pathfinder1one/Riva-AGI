"""
LLM Client Wrapper — orchestration/orchestrator/llm.py
======================================================
Autonomous tool-calling client wrapper supporting:
- Autonomous multi-turn function calling via Google GenAI SDK (AFC)
- 429 Rate Limit / Quota resilience with 15-key rotation pool
- Frequency-based model allocation from config/models.json
- WebSocket Live API fallback for real-time speech/vision
"""

import asyncio
import concurrent.futures
import functools
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Optional, List, Callable, Any, Tuple, Union, Dict

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
except ImportError:
    genai = None
    types = None
    APIError = Exception

from orchestration.tools import tool_registry
from orchestration.orchestrator.schemas.tool import ToolCall, ToolResult
from orchestration.orchestrator.config import key_manager

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "models.json"

LIVE_MODELS = {"gemini-3.8-live", "gemini-3.1-flash-live-preview"}

PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash-lite"]

DEFAULT_MODEL_MAPPING: Dict[str, str] = {
    # High-Frequency Heavy Execution (15 RPM, 500 RPD)
    "coder": "gemini-3.5-flash-lite",
    "qa_tester": "gemini-3.1-flash-lite",
    "researcher": "gemini-3.5-flash-lite",
    "intent_classifier": "gemini-3.1-flash-lite",
    "knowledge_agent": "gemini-3.1-flash-lite",
    "executor": "gemini-3.1-flash-lite",
    "devops": "gemini-3.1-flash-lite",
    "designer": "gemini-3.1-flash-lite",
    "seo_specialist": "gemini-3.1-flash-lite",
    "dummy_system": "gemini-3.1-flash-lite",

    # Low-Frequency Deep Reasoning Models (5 RPM, 20 RPD)
    "planner": "gemini-3.5-flash",
    "reviewer": "gemini-3.7-flash",
    "writer": "gemini-3.6-flash",
    "reasoner": "gemini-3.8-flash",
    "security_auditor": "gemini-3-flash-preview",
    "data_analyst": "gemini-robotics-er-2-preview",
}


def load_models_config() -> Dict[str, Any]:
    """Loads models.json configuration or returns defaults if missing/corrupt."""
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[LLM] Failed to load models config from {CONFIG_PATH}: {e}. Using defaults.")
    return {}


def get_model_for_agent(agent_id: str) -> str:
    """Resolves the configured model name for a given agent_id."""
    cfg = load_models_config()
    mapping = cfg.get("agent_model_mapping", {})
    if agent_id in mapping and isinstance(mapping[agent_id], dict):
        return mapping[agent_id].get("model", DEFAULT_MODEL_MAPPING.get(agent_id, PRIMARY_MODEL))
    return DEFAULT_MODEL_MAPPING.get(agent_id, PRIMARY_MODEL)


def _call_gemini_live(client: Any, model_name: str, prompt: str, system_instruction: str = "") -> str:
    """
    Invokes Gemini Live API via WebSocket with audio transcription,
    providing zero rate-limit (Unlimited RPM/RPD) generation.
    """
    async def _async_call():
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(),
            system_instruction=types.Content(parts=[types.Part.from_text(text=system_instruction)]) if system_instruction else None
        )
        accumulated_text = []
        async with client.aio.live.connect(model=model_name, config=config) as session:
            await session.send_client_content(
                turns=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                turn_complete=True
            )
            async for response in session.receive():
                sc = response.server_content
                if sc and sc.output_transcription and sc.output_transcription.text:
                    accumulated_text.append(sc.output_transcription.text)
                if sc and sc.turn_complete:
                    break
        return "".join(accumulated_text).strip()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _async_call())
            return future.result()
    else:
        return asyncio.run(_async_call())


def _wrap_tool_for_execution(name: str, func: Callable, execution_log: list) -> Callable:
    """
    Wraps a tool function to track its execution time, parameters, and output
    for audit trails, schemas, and UI telemetry.
    """
    @functools.wraps(func)
    def tracked_tool(*args, **kwargs):
        call_id = f"call_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        logger.info(f"LLM triggered tool [{name}] with args: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000.0
            
            tool_call = ToolCall(
                call_id=call_id,
                tool_name=name,
                parameters=kwargs,
                expected_return_type=str(type(result).__name__)
            )
            execution_log.append(tool_call)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000.0
            error_msg = f"Tool Execution Error ({name}): {str(e)}"
            logger.error(error_msg)
            
            tool_call = ToolCall(
                call_id=call_id,
                tool_name=name,
                parameters=kwargs,
                expected_return_type="str"
            )
            execution_log.append(tool_call)
            return error_msg

    return tracked_tool


def call_gemini(
    prompt: str,
    api_key: str,
    system_instruction: str,
    agent_id: str,
    tools: Optional[List[Union[str, Callable]]] = None,
    return_tool_calls: bool = False
) -> Union[str, Tuple[str, List[ToolCall]]]:
    """
    Calls Google GenAI SDK using agent-assigned models, supporting autonomous
    multi-turn tool calling, 429 quota key rotation, and Live API.
    """
    if genai is None:
        msg = f"[LLM Offline Mode] google-genai SDK not installed. Generated stub response for {agent_id}."
        logger.warning(msg)
        return (msg, []) if return_tool_calls else msg

    if not api_key:
        api_key = key_manager.get_api_key_for_role(agent_id)
        if not api_key:
            raise ValueError(f"API Key is missing for agent [{agent_id}].")

    model_name = get_model_for_agent(agent_id)

    # 1. Try Live API (Zero rate limit, Unlimited RPM/RPD) if configured
    if model_name in LIVE_MODELS and not tools:
        try:
            client = genai.Client(api_key=api_key)
            logger.info(f"Agent [{agent_id}] triggering Live API -> {model_name}")
            live_result = _call_gemini_live(client, model_name, prompt, system_instruction)
            if live_result:
                return (live_result, []) if return_tool_calls else live_result
        except Exception as live_e:
            logger.warning(f"Agent [{agent_id}] Live API failed: {live_e}. Falling back to standard model.")

    executed_tools: List[ToolCall] = []
    wrapped_tools: List[Callable] = []

    # Resolve tools from tool_registry or direct callables
    if tools:
        for t in tools:
            if isinstance(t, str):
                tool_func = tool_registry.get_tool(t)
                if tool_func:
                    wrapped_tools.append(_wrap_tool_for_execution(t, tool_func, executed_tools))
                else:
                    logger.warning(f"Tool '{t}' requested by agent '{agent_id}' was not found in tool_registry.")
            elif callable(t):
                tool_name = getattr(t, "__name__", "custom_tool")
                wrapped_tools.append(_wrap_tool_for_execution(tool_name, t, executed_tools))

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        tools=wrapped_tools if wrapped_tools else None
    )

    candidate_models = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]
    candidate_keys = [api_key] + key_manager.get_fallback_keys(api_key)

    content = ""
    last_error = None
    success = False

    for current_key in candidate_keys:
        client = genai.Client(api_key=current_key)
        for current_model in candidate_models:
            try:
                logger.info(f"Agent [{agent_id}] invoking LLM -> {current_model} (tools: {len(wrapped_tools)})")
                chat = client.chats.create(model=current_model, config=config)
                response = chat.send_message(prompt)
                content = response.text or ""
                last_error = None
                success = True
                break
            except APIError as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    logger.warning(f"Agent [{agent_id}] hit 429 quota limit on {current_model}. Rotating key/model...")
                    last_error = e
                    continue
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    logger.warning(f"Agent [{agent_id}] model {current_model} not found (404). Trying next model...")
                    last_error = e
                    continue
                else:
                    logger.warning(f"Agent [{agent_id}] encountered APIError on {current_model}: {e}")
                    last_error = e
                    continue
            except Exception as e:
                logger.error(f"Agent [{agent_id}] encountered error on {current_model}: {e}")
                last_error = e
                break
        if success:
            break

    if not success and last_error:
        content = f"LLM Generation Error: {last_error}"

    if return_tool_calls:
        return content, executed_tools
    return content
