"""
API Key Manager — orchestration/orchestrator/config.py
======================================================
Manages Gemini API keys with 3-tier hierarchical resolution:
  1. Exact Named Role (GEMINI_API_KEY_SEO_SPECIALIST, GEMINI_API_KEY_CODER)
  2. Numbered Worker Fallback (GEMINI_API_KEY_WORKER_10)
  3. Universal Orchestrator Fallback (GEMINI_API_KEY_ORCHESTRATOR / GEMINI_API_KEY)

Resolves Issue #4 (seo_specialist and dummy_system_agent WORKER_10 collision).
"""

import os
import logging
from typing import Literal, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

AgentLevel = Literal["CEO", "MANAGER", "TASK_DOER"]


class KeyManager:
    """
    Manages the Gemini API keys assigned to the Agentic Company hierarchy.
    Uses a 3-tier fallback to resolve key collisions between agents that
    previously shared the same WORKER_N env var.
    """

    # Maps each agent role to an ordered list of env vars to try.
    # The first env var that is set and non-empty wins.
    ROLE_ALIASES = {
        "SEO_SPECIALIST": ["GEMINI_API_KEY_SEO_SPECIALIST", "GEMINI_API_KEY_WORKER_10"],
        "DUMMY_SYSTEM": ["GEMINI_API_KEY_DUMMY_SYSTEM"],
        "DESIGNER": ["GEMINI_API_KEY_DESIGNER", "GEMINI_API_KEY_WORKER_5"],
        "QA_TESTER": ["GEMINI_API_KEY_QA_TESTER", "GEMINI_API_KEY_WORKER_6"],
        "DATA_ANALYST": ["GEMINI_API_KEY_DATA_ANALYST", "GEMINI_API_KEY_WORKER_7"],
        "DEVOPS": ["GEMINI_API_KEY_DEVOPS", "GEMINI_API_KEY_WORKER_8"],
        "SECURITY_AUDITOR": ["GEMINI_API_KEY_SECURITY_AUDITOR", "GEMINI_API_KEY_WORKER_9"],
        "CODER": ["GEMINI_API_KEY_CODER"],
        "RESEARCHER": ["GEMINI_API_KEY_RESEARCHER"],
        "WRITER": ["GEMINI_API_KEY_WRITER"],
        "REASONER": ["GEMINI_API_KEY_REASONER"],
        "INTENT": ["GEMINI_API_KEY_INTENT"],
        "PLANNER": ["GEMINI_API_KEY_PLANNER"],
        "EXECUTOR": ["GEMINI_API_KEY_EXECUTOR"],
        "REVIEWER": ["GEMINI_API_KEY_REVIEWER"],
        "ORCHESTRATOR": ["GEMINI_API_KEY_ORCHESTRATOR"],
    }

    def get_api_key_for_role(self, role: str) -> str:
        """
        Retrieves the API key for a given role using 3-tier fallback:
        1. Try each candidate env var in ROLE_ALIASES for this role.
        2. Try the generic GEMINI_API_KEY_{ROLE} pattern.
        3. Fall back to the universal GEMINI_API_KEY_ORCHESTRATOR or GEMINI_API_KEY.
        """
        clean_role = role.upper().strip()

        # Tier 1 & 2: Check configured aliases for this role
        candidates = self.ROLE_ALIASES.get(
            clean_role, [f"GEMINI_API_KEY_{clean_role}"]
        )
        for env_var in candidates:
            val = os.getenv(env_var, "").strip()
            if val:
                return val

        # Tier 3: Universal fallback
        return (
            os.getenv("GEMINI_API_KEY_ORCHESTRATOR", "")
            or os.getenv("GEMINI_API_KEY", "")
        )

    def get_all_available_keys(self) -> List[str]:
        """Returns all non-empty Gemini API keys configured in the environment."""
        keys = []
        for k, v in os.environ.items():
            if k.startswith("GEMINI_API_KEY") and v.strip() and v.strip() not in keys:
                keys.append(v.strip())
        return keys

    def get_fallback_keys(self, current_key: str) -> List[str]:
        """Returns other available keys excluding the current one for quota rotation."""
        return [k for k in self.get_all_available_keys() if k != current_key]


# Singleton instance used by the Orchestrator and Agent Factory
key_manager = KeyManager()
