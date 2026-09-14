"""
SURE SAVINGS: Targeted Knowledge Retriever (backend/knowledge/knowledge_retriever.py)
Retrieves targeted, minimal product knowledge slices based on user intent and page context.

Prevents prompt bloat and guarantees grounded explanations without sending the entire
codebase or database to Gemini.
"""

from typing import Dict, Any, Optional, List

from backend.knowledge.button_registry import BUTTON_REGISTRY, get_button_info, list_buttons_for_page
from backend.knowledge.metric_registry import METRIC_REGISTRY, get_metric_info
from backend.knowledge.onboarding_registry import ONBOARDING_STEPS, COMPREHENSIVE_TOUR
from backend.knowledge.intent_taxonomy import (
    INTENT_BUTTON_HELP,
    INTENT_PAGE_HELP,
    INTENT_METRIC_EXPLANATION,
    INTENT_FINANCIAL_EXPLANATION,
    INTENT_BANK_HELP,
    INTENT_BANK_SYNC,
    INTENT_BANK_CONNECTION,
    INTENT_COMPREHENSIVE_TOUR,
    INTENT_ONBOARDING,
    INTENT_WHAT_NEXT,
    INTENT_CALENDAR_HELP,
    INTENT_PLANNER_HELP,
    INTENT_INCOME_HELP,
    INTENT_GOAL_HELP,
    INTENT_RISK_HELP,
    INTENT_HEALTH_HELP,
    INTENT_ACTIVITY_HELP,
    INTENT_SIMULATOR_HELP,
    INTENT_DECISION_PIPELINE_HELP,
    INTENT_RESILIENCE_PLAN_HELP,
    INTENT_AI_HELP
)

class KnowledgeRetriever:
    """
    Pulls minimal, highly relevant knowledge chunks for Gemini system context.
    """

    @classmethod
    def retrieve(
        cls,
        intent: str,
        query: str,
        page_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Returns targeted knowledge artifacts based on classified intent.
        """
        q_lower = query.lower()
        curr_page = (page_context or {}).get("page", "index.html")
        retrieved: Dict[str, Any] = {
            "intent": intent,
            "relevant_buttons": [],
            "relevant_metrics": [],
            "relevant_pages": [],
            "guidance_slice": None
        }

        # 1. Comprehensive Tour
        if intent == INTENT_COMPREHENSIVE_TOUR:
            retrieved["guidance_slice"] = COMPREHENSIVE_TOUR
            return retrieved

        # 2. Onboarding / Getting Started
        if intent in (INTENT_ONBOARDING, INTENT_WHAT_NEXT):
            retrieved["guidance_slice"] = {"onboarding_steps": ONBOARDING_STEPS}
            return retrieved

        # 3. Button Explanations
        if intent == INTENT_BUTTON_HELP or "button" in q_lower or "sync now" in q_lower:
            # Check specific buttons mentioned in query
            found_button = None
            if "sync" in q_lower:
                found_button = BUTTON_REGISTRY.get("SYNC_NOW")
            elif "connect" in q_lower or "link bank" in q_lower:
                found_button = BUTTON_REGISTRY.get("CONNECT_BANK")
            elif "approve" in q_lower or "sweep" in q_lower:
                found_button = BUTTON_REGISTRY.get("APPROVE_RECOMMENDATION")
            elif "withdraw" in q_lower:
                found_button = BUTTON_REGISTRY.get("WITHDRAW_BUFFER")
            elif "quick start" in q_lower:
                found_button = BUTTON_REGISTRY.get("QUICK_START")
            elif "setup" in q_lower:
                found_button = BUTTON_REGISTRY.get("LAUNCH_SETUP")
            
            # If no specific button mentioned, look up buttons for current page
            if found_button:
                retrieved["relevant_buttons"].append(found_button)
            else:
                page_buttons = list_buttons_for_page(curr_page)
                retrieved["relevant_buttons"].extend(page_buttons[:3])

        # 4. Metric Explanations
        if intent in (INTENT_METRIC_EXPLANATION, INTENT_FINANCIAL_EXPLANATION):
            for m_key, m_spec in METRIC_REGISTRY.items():
                name_words = m_spec["display_name"].lower().split()
                if any(w in q_lower for w in [m_key.lower(), m_spec["display_name"].lower()]):
                    retrieved["relevant_metrics"].append(m_spec)
            if not retrieved["relevant_metrics"] and "safe to save" in q_lower or "safe-to-save" in q_lower:
                retrieved["relevant_metrics"].append(METRIC_REGISTRY["SAFE_TO_SAVE"])

        # 5. Bank Account Help
        if intent in (INTENT_BANK_HELP, INTENT_BANK_SYNC, INTENT_BANK_CONNECTION):
            if BUTTON_REGISTRY.get("SYNC_NOW") not in retrieved["relevant_buttons"]:
                retrieved["relevant_buttons"].append(BUTTON_REGISTRY["SYNC_NOW"])
            if BUTTON_REGISTRY.get("CONNECT_BANK") not in retrieved["relevant_buttons"]:
                retrieved["relevant_buttons"].append(BUTTON_REGISTRY["CONNECT_BANK"])
            retrieved["relevant_metrics"].append(METRIC_REGISTRY["REPORTED_BALANCE"])

        return retrieved
