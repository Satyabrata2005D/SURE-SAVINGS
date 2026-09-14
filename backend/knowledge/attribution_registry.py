"""
SURE SAVINGS: Public Attribution Registry (backend/knowledge/attribution_registry.py)
Authoritative public attribution record for SURE SAVINGS.

Security Invariants:
- Scope: PUBLIC
- Evaluated BEFORE generic confidentiality and source-code rules.
- Contains ONLY the approved public attribution statement.
- Under NO circumstances discloses personal addresses, phone numbers,
  private emails, academic grades, credentials, or internal repositories.
"""

from typing import Dict, Any, Optional
import re

# ── Universal Public Attribution Record ──
ATTRIBUTION_STATEMENT = "This website was built by Satyabrata Das from Narula Institute of Technology."

# Attribution intent regex patterns
ATTRIBUTION_PATTERNS = [
    re.compile(r"\bwho\s+(built|created|made|developed|coded|founded|designed|engineered)\s+(this\s+)?(website|platform|site|app|application|project|sure\s*savings)?\b", re.IGNORECASE),
    re.compile(r"\bwho\s+is\s+(the\s+)?(developer|creator|builder|author|founder|owner|maker)\s+(of\s+)?(this\s+)?(website|platform|site|app|sure\s*savings)?\b", re.IGNORECASE),
    re.compile(r"\bwho('s|s|\s+is)?\s+(behind|made)\s+(this\s+)?(website|platform|site|sure\s*savings)?\b", re.IGNORECASE),
    re.compile(r"\bdeveloper\s+of\s+(this\s+)?(website|platform|site|sure\s*savings)\b", re.IGNORECASE),
    re.compile(r"\bcreator\s+of\s+(this\s+)?(website|platform|site|sure\s*savings)\b", re.IGNORECASE),
    re.compile(r"\bbuilt\s+by\s+whom\b", re.IGNORECASE),
    re.compile(r"\bwho\s+built\s+it\b", re.IGNORECASE),
    re.compile(r"\bwho\s+made\s+it\b", re.IGNORECASE),
    re.compile(r"\bwho\s+created\s+it\b", re.IGNORECASE),
    re.compile(r"\bwho\s+developed\s+it\b", re.IGNORECASE),
]

def is_attribution_query(query: str) -> bool:
    """
    Detect whether a query is asking for the builder, developer, or creator of SURE SAVINGS.
    Must be called BEFORE source-code or general confidentiality checks.
    """
    clean = query.strip().lower()
    if not clean:
        return False
    for pattern in ATTRIBUTION_PATTERNS:
        if pattern.search(clean):
            return True
    return False

def get_attribution_response() -> Dict[str, Any]:
    """
    Returns the structured public attribution response.
    """
    return {
        "title": "Platform Attribution",
        "answer": ATTRIBUTION_STATEMENT,
        "topic": "public_attribution",
        "response_type": "attribution",
        "confidence": "high",
        "next_step": "You can ask me how any page or button works, or how to connect your bank.",
        "navigation": None,
        "show_data_source": False,
        "data_status": "AVAILABLE",
        "safety_status": "ALLOWED",
        "badge": "Public Attribution",
        "score_delta": "Neutral",
        "telemetry_facts": ["Built by Satyabrata Das from Narula Institute of Technology"]
    }
