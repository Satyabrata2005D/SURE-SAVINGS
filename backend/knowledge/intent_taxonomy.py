"""
SURE SAVINGS: Intent Taxonomy & Classifier (backend/knowledge/intent_taxonomy.py)
Multi-stage intent classification engine for SURE AI.

Classification Hierarchy:
1. Public Attribution (Evaluated first to guarantee developer attribution)
2. Confidential Refusal checks (Source code, other users, credentials, database, prompts, mutations)
3. Greetings (Time-aware greetings without massive financial reports)
4. Comprehensive Tour & Platform Overview
5. Specific Feature & Domain Help (Buttons, Pages, Bank, Calendar, Goals, Risk, Metrics, etc.)
6. Personalized Financial Explanations
7. General Platform Help / Fallback
"""

from typing import Dict, Any, Optional
import re

from backend.knowledge.attribution_registry import is_attribution_query
from backend.knowledge.refusal_registry import check_refusal

# ── Intent Categories ──
INTENT_PUBLIC_ATTRIBUTION = "PUBLIC_ATTRIBUTION"
INTENT_CONFIDENTIAL_SOURCE_CODE = "CONFIDENTIAL_SOURCE_CODE"
INTENT_CONFIDENTIAL_USER_DATA = "CONFIDENTIAL_USER_DATA"
INTENT_CONFIDENTIAL_CREDENTIAL = "CONFIDENTIAL_CREDENTIAL"
INTENT_CONFIDENTIAL_INTERNAL_CONFIG = "CONFIDENTIAL_INTERNAL_CONFIG"
INTENT_CONFIDENTIAL_SYSTEM_PROMPT = "CONFIDENTIAL_SYSTEM_PROMPT"
INTENT_MUTATION_REQUEST = "MUTATION_REQUEST"
INTENT_GREETING = "GREETING"
INTENT_COMPREHENSIVE_TOUR = "COMPREHENSIVE_TOUR"
INTENT_PLATFORM_OVERVIEW = "PLATFORM_OVERVIEW"
INTENT_ONBOARDING = "ONBOARDING"
INTENT_WHAT_NEXT = "WHAT_NEXT"
INTENT_PAGE_HELP = "PAGE_HELP"
INTENT_BUTTON_HELP = "BUTTON_HELP"
INTENT_BANK_HELP = "BANK_HELP"
INTENT_BANK_SYNC = "BANK_SYNC"
INTENT_BANK_CONNECTION = "BANK_CONNECTION"
INTENT_CALENDAR_HELP = "CALENDAR_HELP"
INTENT_PLANNER_HELP = "PLANNER_HELP"
INTENT_INCOME_HELP = "INCOME_HELP"
INTENT_GOAL_HELP = "GOAL_HELP"
INTENT_RISK_HELP = "RISK_HELP"
INTENT_HEALTH_HELP = "HEALTH_HELP"
INTENT_ACTIVITY_HELP = "ACTIVITY_HELP"
INTENT_SIMULATOR_HELP = "SIMULATOR_HELP"
INTENT_DECISION_PIPELINE_HELP = "DECISION_PIPELINE_HELP"
INTENT_RESILIENCE_PLAN_HELP = "RESILIENCE_PLAN_HELP"
INTENT_AI_HELP = "AI_HELP"
INTENT_METRIC_EXPLANATION = "METRIC_EXPLANATION"
INTENT_FINANCIAL_EXPLANATION = "FINANCIAL_EXPLANATION"
INTENT_DATA_READINESS = "DATA_READINESS"
INTENT_UNSUPPORTED = "UNSUPPORTED"

# ── Regex Matchers for Specific Intents ──

GREETING_REGEX = re.compile(
    r"^(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|namaste|welcome|greetings|hola)\b",
    re.IGNORECASE
)

COMPREHENSIVE_TOUR_REGEX = re.compile(
    r"\b(explain\s+(everything|the\s+entire\s+website|the\s+whole\s+website|all\s+features|all\s+pages)|tell\s+me\s+everything|complete\s+tour|walk\s+me\s+through\s+(everything|the\s+whole\s+platform))\b",
    re.IGNORECASE
)

ONBOARDING_REGEX = re.compile(
    r"\b(i('?m| am)\s+new|get\s+started|getting\s+started|how\s+do\s+i\s+start|where\s+do\s+i\s+begin|first\s+step|beginner|new\s+user|what\s+should\s+i\s+do\s+first)\b",
    re.IGNORECASE
)

WHAT_NEXT_REGEX = re.compile(
    r"\b(what\s+should\s+i\s+do\s+next|what\s+next|next\s+step|where\s+should\s+i\s+go\s+now|what('?s|\s+is)\s+my\s+next\s+step)\b",
    re.IGNORECASE
)

BUTTON_HELP_REGEX = re.compile(
    r"\b(what\s+does\s+(this|that|the)\s+button\s+do|button\s+do|what\s+is\s+(this\s+)?button|how\s+to\s+use\s+(this|that)\s+button|why\s+is\s+(this|the)\s+button\s+disabled|sync\s+now\s+button|approve\s+recommendation\s+button|quick\s+start\s+button)\b",
    re.IGNORECASE
)

PAGE_HELP_REGEX = re.compile(
    r"\b(what\s+is\s+this\s+page|what\s+does\s+this\s+page\s+do|explain\s+this\s+page|how\s+to\s+use\s+this\s+page|what\s+can\s+i\s+do\s+here|where\s+am\s+i)\b",
    re.IGNORECASE
)

BANK_SYNC_REGEX = re.compile(
    r"\b(what\s+is\s+sync\s+now|what\s+does\s+sync\s+now\s+do|how\s+does\s+sync\s+work|synchronize\s+bank|bank\s+sync|last\s+synced)\b",
    re.IGNORECASE
)

BANK_CONNECTION_REGEX = re.compile(
    r"\b(how\s+do\s+i\s+connect\s+(my\s+)?bank|connect\s+bank|connect\s+bank\s+account|link\s+bank|account\s+aggregator|setu\s+aa|disconnect\s+bank|add\s+bank|supported\s+banks)\b",
    re.IGNORECASE
)

METRIC_EXPLANATION_REGEX = re.compile(
    r"\b(what\s+is|how\s+does|explain|tell\s+me\s+about)\s+(the\s+)?(safe-to-save|safe\s+to\s+save|smart\s+buffer|protected\s+floor|resilience\s+score|weekly\s+burn|burn\s+rate|volatility\s+coefficient|runway|stabilized\s+baseline)\b",
    re.IGNORECASE
)

FINANCIAL_WHY_REGEX = re.compile(
    r"\b(why\s+is\s+my\s+(safe-to-save|safe\s+to\s+save|buffer|floor|resilience\s+score|recommendation)\s+(zero|0|low|missing|changed|different|high))\b",
    re.IGNORECASE
)

class IntentClassifier:
    """
    Classifies user message intent using a strict priority hierarchy.
    """

    @classmethod
    def classify(cls, query: str, page_context: Optional[Dict[str, Any]] = None) -> str:
        clean = query.strip()
        if not clean:
            return INTENT_UNSUPPORTED

        # 1. Public Attribution ALWAYS evaluated first
        if is_attribution_query(clean):
            return INTENT_PUBLIC_ATTRIBUTION

        # 2. Granular Confidentiality & Mutation Refusals
        refusal_check = check_refusal(clean)
        if refusal_check:
            return refusal_check[0]

        # 3. Comprehensive Tour ("Explain everything", "Complete tour")
        if COMPREHENSIVE_TOUR_REGEX.search(clean):
            return INTENT_COMPREHENSIVE_TOUR

        # 4. Greetings ("Hi", "Hello", "Good morning")
        # Check if query is primarily a greeting (short or starts with greeting)
        if GREETING_REGEX.search(clean) and len(clean.split()) <= 4:
            return INTENT_GREETING

        # 5. Onboarding / Getting Started
        if ONBOARDING_REGEX.search(clean):
            return INTENT_ONBOARDING

        # 6. What Next
        if WHAT_NEXT_REGEX.search(clean):
            return INTENT_WHAT_NEXT

        # 7. Button Explanations
        if BUTTON_HELP_REGEX.search(clean):
            return INTENT_BUTTON_HELP

        # 8. Page Explanations ("Explain this page", "What is this page")
        if PAGE_HELP_REGEX.search(clean):
            return INTENT_PAGE_HELP

        # 9. Bank Sync & Bank Connection
        if BANK_SYNC_REGEX.search(clean):
            return INTENT_BANK_SYNC
        if BANK_CONNECTION_REGEX.search(clean):
            return INTENT_BANK_CONNECTION

        # 10. Financial "Why is my..." personalized questions
        if FINANCIAL_WHY_REGEX.search(clean):
            return INTENT_FINANCIAL_EXPLANATION

        # 11. Metric definitions ("What is Safe-to-Save")
        if METRIC_EXPLANATION_REGEX.search(clean):
            return INTENT_METRIC_EXPLANATION

        # 12. Specific Feature Area Keywords
        lower = clean.lower()
        if any(w in lower for w in ["calendar", "event", "due date", "payout day", "schedule"]):
            return INTENT_CALENDAR_HELP
        if any(w in lower for w in ["planner", "cash flow", "forecast", "projection"]):
            return INTENT_PLANNER_HELP
        if any(w in lower for w in ["income intelligence", "volatility", "gig earnings", "platform payout"]):
            return INTENT_INCOME_HELP
        if any(w in lower for w in ["goal", "buffer plan", "target reserve"]):
            return INTENT_GOAL_HELP
        if any(w in lower for w in ["risk", "early warning", "down week", "down-week"]):
            return INTENT_RISK_HELP
        if any(w in lower for w in ["health", "diagnostic", "financial health"]):
            return INTENT_HEALTH_HELP
        if any(w in lower for w in ["activity", "transaction", "ledger", "statement", "csv"]):
            return INTENT_ACTIVITY_HELP
        if any(w in lower for w in ["simulator", "shock", "stress test", "emergency shock"]):
            return INTENT_SIMULATOR_HELP
        if any(w in lower for w in ["pipeline", "decision pipeline", "audit trace", "cryptographic"]):
            return INTENT_DECISION_PIPELINE_HELP
        if any(w in lower for w in ["resilience plan", "recovery", "roadmap"]):
            return INTENT_RESILIENCE_PLAN_HELP
        if any(w in lower for w in ["what are you", "who are you", "what is sure ai", "how does ai work"]):
            return INTENT_AI_HELP
        if any(w in lower for w in ["how does the website work", "what is sure savings", "platform overview"]):
            return INTENT_PLATFORM_OVERVIEW
        if any(w in lower for w in ["missing data", "why is page empty", "insufficient data", "setup required"]):
            return INTENT_DATA_READINESS

        # Default to general platform help
        return INTENT_PLATFORM_OVERVIEW
