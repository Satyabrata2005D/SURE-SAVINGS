"""
SURE SAVINGS: Refusal Policy Registry (backend/knowledge/refusal_registry.py)
Granular refusal policies for protected, confidential, and out-of-scope queries.

Security Invariants:
- Replaces generic collapsing refusals with distinct, professional category responses.
- Enforces strict read-only advisory boundary: Zero balance mutation or transaction authority.
- Strictly protects source code, API keys, credentials, database configurations, and other users' private data.
"""

from typing import Dict, Any, Optional, Tuple
import re

# ── Refusal Category Definitions ──

REFUSAL_POLICIES: Dict[str, Dict[str, Any]] = {
    "CONFIDENTIAL_SOURCE_CODE": {
        "title": "Confidential Information Protected",
        "answer": (
            "This is confidential information, so I can't share the website's source code "
            "or private internal implementation.\n\n"
            "I can explain how SURE SAVINGS works from a user perspective, including its pages, "
            "features, buttons, workflows, calculations, and navigation."
        ),
        "topic": "confidential_source_code",
        "response_type": "refusal",
        "badge": "Confidential Protected",
        "next_step": "Ask me to explain any user-facing feature, page, button, or financial calculation."
    },
    "CONFIDENTIAL_USER_DATA": {
        "title": "User Privacy Protected",
        "answer": (
            "This is confidential user information, so I can't share it. SURE SAVINGS keeps "
            "each user's financial information isolated and private.\n\n"
            "I can explain how your own account and financial information work."
        ),
        "topic": "confidential_user_data",
        "response_type": "refusal",
        "badge": "Privacy Protected",
        "next_step": "Ask about your own financial metrics, buffer status, or bank accounts."
    },
    "CONFIDENTIAL_CREDENTIAL": {
        "title": "Security Information Protected",
        "answer": (
            "This is confidential security information and cannot be shared. API keys, "
            "secrets, authentication credentials, and private system tokens are never disclosed."
        ),
        "topic": "confidential_credential",
        "response_type": "refusal",
        "badge": "Security Protected",
        "next_step": "Explore platform features or ask how to link your bank account via RBI Account Aggregator."
    },
    "CONFIDENTIAL_INTERNAL_CONFIG": {
        "title": "Internal Security Information Protected",
        "answer": (
            "Database credentials, private configurations, authentication secrets, and internal "
            "infrastructure information cannot be shared.\n\n"
            "I can explain the platform from a user's perspective instead."
        ),
        "topic": "confidential_internal_config",
        "response_type": "refusal",
        "badge": "Infrastructure Protected",
        "next_step": "Ask how SURE SAVINGS calculates Safe-to-Save or manages financial resilience."
    },
    "CONFIDENTIAL_SYSTEM_PROMPT": {
        "title": "Internal Instructions Protected",
        "answer": (
            "I can explain what SURE AI is designed to do and how you can use it, but private "
            "internal instructions and security policies cannot be disclosed."
        ),
        "topic": "confidential_system_prompt",
        "response_type": "refusal",
        "badge": "Policy Protected",
        "next_step": "Ask what SURE AI can do for you, or ask about any button or financial metric."
    },
    "MUTATION_REQUEST": {
        "title": "Read-Only Advisory Boundary",
        "answer": (
            "SURE AI operates strictly as a read-only advisory guide and has no authority to "
            "transfer money, alter balances, or mutate financial records.\n\n"
            "To perform this action, please use the designated controls in the user interface "
            "(such as on the Command Center or Bank Accounts page)."
        ),
        "topic": "mutation_request",
        "response_type": "refusal",
        "badge": "Read-Only Invariant",
        "next_step": "Use the interactive buttons on the Command Center or Bank Accounts page."
    }
}

# ── Pattern Matchers for Refusal Categories ──

SOURCE_CODE_PATTERNS = [
    re.compile(r"\b(give|show|dump|leak|send|view|share|print|display|tell)\s+(me\s+)?(all\s+)?(the\s+)?([a-z_\-]+\s+)?code\b", re.IGNORECASE),
    re.compile(r"\b(source\s*code|source\s+files|backend\s+code|frontend\s+code|internal\s+code|python\s+code|javascript\s+code)\b", re.IGNORECASE),
    re.compile(r"\b(show\s+code|view\s+code|get\s+code|see\s+code|all\s+code)\b", re.IGNORECASE),
    re.compile(r"\b(internal\s+architecture|implementation\s+files|developer\s+architecture)\b", re.IGNORECASE),
    re.compile(r"\b(what\s+backend\s+framework|what\s+technologies\s+were\s+used|show\s+github\s+repo|repository\s+code)\b", re.IGNORECASE),
    re.compile(r"\bhow\s+(was\s+this\s+website|is\s+this\s+website|was\s+the\s+website|is\s+the\s+website)\s+(built|coded|engineered|programmed)\b", re.IGNORECASE),
]

USER_DATA_PATTERNS = [
    re.compile(r"\b(show|give|display|fetch|view|leak)\s+(me\s+)?(an?other|someone\s+else's?|all)\s+user('?s)?\s+(account|data|info|information|balance|transactions?|profile)\b", re.IGNORECASE),
    re.compile(r"\b(other\s+users?|another\s+user('?s)?|other\s+user's)\s+(account|data|info|information|balance|transactions?|profile)\b", re.IGNORECASE),
    re.compile(r"\bwho\s+else\s+uses\s+(this|sure\s*savings)\b", re.IGNORECASE),
    re.compile(r"\b(show|get|find)\s+user\s+usr_[0-9a-fA-F]+\b", re.IGNORECASE),
    re.compile(r"\bother\s+user\b", re.IGNORECASE),
    re.compile(r"\banother\s+user\b", re.IGNORECASE),
]

CREDENTIAL_PATTERNS = [
    re.compile(r"\b(gemini\s+)?api\s*key\b", re.IGNORECASE),
    re.compile(r"\b(setu\s+)?(client\s+secret|setu\s+secret|secret\s+key)\b", re.IGNORECASE),
    re.compile(r"\b(auth\s+secret|jwt\s+secret|session\s+cookie|session\s+token|access\s+token|refresh\s+token)\b", re.IGNORECASE),
    re.compile(r"\b(bearer\s+token|private\s+key|signing\s+key|password\s+hash)\b", re.IGNORECASE),
]

INTERNAL_CONFIG_PATTERNS = [
    re.compile(r"\b(database\s+credential|database\s+password|db\s+password|db\s+url|database_url)\b", re.IGNORECASE),
    re.compile(r"\b(show\s+me\s+your\s+database|show\s+database|dump\s+database|sqlite\s+file)\b", re.IGNORECASE),
    re.compile(r"\b(environment\s+variables?|\.env\s+file|server\s+config|infrastructure\s+info)\b", re.IGNORECASE),
    re.compile(r"\b(internal\s+configuration|connection\s+string|smtp_password)\b", re.IGNORECASE),
]

SYSTEM_PROMPT_PATTERNS = [
    re.compile(r"\b(system\s+prompt|hidden\s+prompt|system\s+instructions?)\b", re.IGNORECASE),
    re.compile(r"\b(what\s+are\s+your\s+instructions|show\s+me\s+your\s+prompt|print\s+your\s+prompt)\b", re.IGNORECASE),
    re.compile(r"\b(ignore\s+(previous\s+|all\s+)?instructions|disregard\s+rules|bypass\s+policy|jailbreak)\b", re.IGNORECASE),
    re.compile(r"\b(reveal\s+your\s+instructions|repeat\s+the\s+words\s+above)\b", re.IGNORECASE),
]

MUTATION_PATTERNS = [
    re.compile(r"\b(transfer|wire\s+money|send\s+money\s+to|pay\s+out)\b", re.IGNORECASE),
    re.compile(r"\b(withdraw\s+my\s+buffer\s+now|drain\s+buffer|steal\s+buffer)\b", re.IGNORECASE),
    re.compile(r"\b(reset\s+my\s+account|delete\s+my\s+account|delete\s+user)\b", re.IGNORECASE),
    re.compile(r"\b(change\s+my\s+floor\s+to|change\s+my\s+balance|mutate\s+balance)\b", re.IGNORECASE),
    re.compile(r"\b(delete\s+transaction|approve\s+transfer\s+for\s+me)\b", re.IGNORECASE),
]

def check_refusal(query: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Check if query triggers any specific refusal policy.
    Returns (category_name, response_dict) if refused, else None.
    NOTE: Attribution must be evaluated BEFORE calling this function!
    """
    clean = query.strip()
    if not clean:
        return None

    # 1. Other User Data (high privacy priority)
    for pattern in USER_DATA_PATTERNS:
        if pattern.search(clean):
            return "CONFIDENTIAL_USER_DATA", build_refusal_response("CONFIDENTIAL_USER_DATA")

    # 2. Credentials & API Keys
    for pattern in CREDENTIAL_PATTERNS:
        if pattern.search(clean):
            return "CONFIDENTIAL_CREDENTIAL", build_refusal_response("CONFIDENTIAL_CREDENTIAL")

    # 3. Database & Internal Config
    for pattern in INTERNAL_CONFIG_PATTERNS:
        if pattern.search(clean):
            return "CONFIDENTIAL_INTERNAL_CONFIG", build_refusal_response("CONFIDENTIAL_INTERNAL_CONFIG")

    # 4. System Prompt & Jailbreaks
    for pattern in SYSTEM_PROMPT_PATTERNS:
        if pattern.search(clean):
            return "CONFIDENTIAL_SYSTEM_PROMPT", build_refusal_response("CONFIDENTIAL_SYSTEM_PROMPT")

    # 5. Source Code & Architecture Requests
    for pattern in SOURCE_CODE_PATTERNS:
        if pattern.search(clean):
            return "CONFIDENTIAL_SOURCE_CODE", build_refusal_response("CONFIDENTIAL_SOURCE_CODE")

    # 6. Mutation & Money Movement
    for pattern in MUTATION_PATTERNS:
        if pattern.search(clean):
            return "MUTATION_REQUEST", build_refusal_response("MUTATION_REQUEST")

    return None

def build_refusal_response(category: str) -> Dict[str, Any]:
    """
    Constructs a standardized refusal response dictionary.
    """
    policy = REFUSAL_POLICIES.get(category, REFUSAL_POLICIES["CONFIDENTIAL_SOURCE_CODE"])
    return {
        "title": policy["title"],
        "answer": policy["answer"],
        "topic": policy["topic"],
        "response_type": policy["response_type"],
        "confidence": "high",
        "next_step": policy["next_step"],
        "navigation": None,
        "show_data_source": False,
        "data_status": "AVAILABLE",
        "safety_status": "REFUSED",
        "badge": policy["badge"],
        "score_delta": "Prohibited" if category == "MUTATION_REQUEST" else "Neutral",
        "telemetry_facts": []
    }
