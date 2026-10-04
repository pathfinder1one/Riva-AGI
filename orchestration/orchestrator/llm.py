"""
LLM Client Wrapper — orchestration/orchestrator/llm.py
======================================================
Config-driven model dispatcher supporting:
- Live WebSocket API streaming (gemini-3.8-live, gemini-3.1-flash-live-preview)
  for zero rate-limit (Unlimited RPM/RPD) generation
- Standard Google GenAI generateContent fallback (gemini-3.8-flash, gemini-3.5-flash-lite)
- Dynamic agent-model routing from config/models.json
"""
import asyncio
import concurrent.futures
import json
import logging
from pathlib import Path
from typing import Dict, Any

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
except ImportError:
    genai = None
    types = None
    APIError = Exception

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "models.json"

LIVE_MODELS = {"gemini-3.8-live", "gemini-3.1-flash-live-preview"}

DEFAULT_MODEL_MAPPING: Dict[str, str] = {
    # High-Frequency Heavy Execution (15 RPM, 500 RPD - Pool A & B)
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
        return mapping[agent_id].get("model", DEFAULT_MODEL_MAPPING.get(agent_id, "gemini-3.1-flash-live-preview"))
    return DEFAULT_MODEL_MAPPING.get(agent_id, "gemini-3.1-flash-live-preview")


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


def call_gemini(prompt: str, api_key: str, system_instruction: str, agent_id: str) -> str:
    """
    Calls the Google GenAI SDK using the specific model assigned to the agent.
    If the agent uses a Live API model, connects via WebSocket for Unlimited RPM/RPD.
    Falls back to gemini-3.8-flash or gemini-3.5-flash-lite on errors.
    """
    if genai is None:
        msg = f"[LLM Offline Mode] google-genai SDK not installed. Generated stub response for {agent_id}."
        logger.warning(msg)
        return msg

    if not api_key:
        raise ValueError(f"API Key is missing for agent [{agent_id}].")

    model_name = get_model_for_agent(agent_id)
    client = genai.Client(api_key=api_key)

    # 1. Try Live API (Zero rate limit, Unlimited RPM/RPD)
    if model_name in LIVE_MODELS:
        try:
            logger.info(f"Agent [{agent_id}] triggering Live API (Unlimited RPM) -> {model_name}")
            live_result = _call_gemini_live(client, model_name, prompt, system_instruction)
            if live_result:
                return live_result
        except Exception as live_e:
            logger.warning(f"Agent [{agent_id}] Live API failed: {live_e}. Falling back to standard model.")

    # 2. Standard generate_content fallback
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        max_output_tokens=8192,
    )

    fallback_models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash"]
    target_model = model_name if model_name not in LIVE_MODELS else fallback_models[0]

    try:
        logger.info(f"Agent [{agent_id}] triggering LLM -> {target_model}")
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
            config=config,
        )
        return response.text
    except APIError as e:
        logger.warning(f"Agent [{agent_id}] failed with model {target_model}: {e}. Trying fallback models...")
        for fb_model in fallback_models:
            if fb_model == target_model:
                continue
            try:
                response = client.models.generate_content(
                    model=fb_model,
                    contents=prompt,
                    config=config,
                )
                return response.text
            except Exception:
                continue
        return f"LLM Generation Failed on all fallbacks: {e}"
    except Exception as e:
        return f"LLM Generation Error: {e}"
