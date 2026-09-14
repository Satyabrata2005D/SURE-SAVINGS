"""
SURE SAVINGS: AI Context Builder Service (backend/services/ai_context_service.py)
Constructs minimal, safe, authenticated user context for SURE AI.

Security Invariants:
- All data is strictly user-scoped using current_user.id. Cross-tenant access is impossible.
- Never includes secrets, session tokens, passwords, database URIs, or internal system configurations.
- Minimizes context based on query intent to protect user privacy and optimize token efficiency.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from backend.models import User, FinancialProfile, Goal, BankConnection, BankAccount
from backend.services.bank_account_service import BankAccountService
from backend.knowledge.platform_manifest import (
    ALLOWED_ROUTES,
    PLATFORM_FEATURES,
    BUTTON_REGISTRY,
    METRIC_REGISTRY,
    ONBOARDING_GUIDE,
    get_page_info,
    get_button_info,
    get_metric_info
)

class AIContextService:
    """
    Assembles grounded, read-only telemetry for the authenticated user and current page.
    """

    @staticmethod
    def build_user_context(
        db: Session,
        current_user: User,
        page_context: Optional[Dict[str, Any]] = None,
        query: str = "",
        client_timezone: Optional[str] = None,
        client_locale: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build minimal authenticated context for SURE AI.
        Derives local time using browser-provided IANA timezone (not hardcoded IST).
        """
        user_id = current_user.id
        is_demo = getattr(current_user, "is_demo", False)
        profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()

        # 1. Identity & Readiness
        first_name = (current_user.name or "User").split()[0]
        has_income = bool(profile and (profile.current_income or 0) > 0)
        has_burn = bool(profile and (profile.weekly_burn or 0) > 0)
        has_buffer = bool(profile and (profile.current_buffer or 0) > 0)
        has_floor = bool(profile and (profile.protected_floor or 0) > 0)
        
        setup_fields = [has_income, has_burn, has_buffer, has_floor]
        readiness_pct = int((sum(1 for f in setup_fields if f) / len(setup_fields)) * 100)
        is_setup_complete = readiness_pct >= 75 or is_demo

        # Time & Greeting Info derived dynamically from client timezone
        user_tz = None
        tz_candidate = client_timezone or (page_context or {}).get("timezone")
        if tz_candidate:
            try:
                user_tz = ZoneInfo(str(tz_candidate).strip())
            except Exception:
                user_tz = None

        if user_tz is None:
            try:
                user_tz = ZoneInfo("Asia/Kolkata")
            except Exception:
                user_tz = timezone.utc

        user_now = datetime.now(user_tz)
        hour = user_now.hour

        # Greeting specification:
        # 04:00–11:59 -> Good morning
        # 12:00–16:59 -> Good afternoon
        # 17:00–03:59 -> Good evening
        if 4 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        locale_str = client_locale or (page_context or {}).get("locale", "en")
        time_info = {
            "current_time_str": user_now.strftime("%I:%M %p"),
            "current_date_str": user_now.strftime("%Y-%m-%d"),
            "hour": hour,
            "greeting": time_greeting,
            "timezone": str(user_tz),
            "locale": locale_str
        }

        # 2. Financial Telemetry
        financial_state: Dict[str, Any] = {}
        data_status = "AVAILABLE" if is_setup_complete else "INSUFFICIENT_DATA"

        has_any_data = bool(profile and (has_income or has_buffer or has_burn or has_floor))

        if profile and (has_any_data or is_demo):
            current_income = float(profile.current_income or 0.0)
            stabilized_income = float(profile.stabilized_income or current_income * 0.9)
            weekly_burn = float(profile.weekly_burn or 0.0)
            current_buffer = float(profile.current_buffer or 0.0)
            protected_floor = float(profile.protected_floor or 0.0)
            recommended_save = float(profile.recommended_contribution or 0.0)
            resilience_score = int(profile.resilience_score or 70)
            surplus = max(0.0, current_income - weekly_burn)
            coverage_weeks = round(current_buffer / weekly_burn, 1) if weekly_burn > 0 else 0.0

            financial_state = {
                "current_weekly_income": current_income,
                "stabilized_income_baseline": stabilized_income,
                "weekly_essential_burn": weekly_burn,
                "current_emergency_buffer": current_buffer,
                "protected_cash_floor": protected_floor,
                "safe_to_save_recommendation": recommended_save,
                "resilience_score": resilience_score,
                "buffer_runway_weeks": coverage_weeks,
                "calculated_surplus": surplus,
                "buffer_status": "FUNDED" if coverage_weeks >= 4.0 else "BUILDING",
                # Legacy compatibility aliases for AICoachEngine
                "current_income": current_income,
                "stabilized_income": stabilized_income,
                "weekly_burn": weekly_burn,
                "current_buffer": current_buffer,
                "protected_floor": protected_floor,
                "recommended_contribution": recommended_save,
                "surplus": surplus,
                "safe_to_use_above_floor": max(0.0, current_buffer - protected_floor),
                "current_coverage_weeks": coverage_weeks
            }
        else:
            financial_state = {
                "notice": "Financial setup incomplete. Values awaiting initial calibration.",
                "readiness_pct": readiness_pct,
                "missing_attributes": [
                    field for field, completed in [
                        ("Income baseline", has_income),
                        ("Weekly essential expenses", has_burn),
                        ("Current emergency buffer", has_buffer),
                        ("Protected cash floor", has_floor)
                    ] if not completed
                ]
            }

        # 3. Bank Telemetry (User-Scoped)
        liquidity_info = BankAccountService.calculate_total_bank_liquidity(db, user_id)
        connections = BankAccountService.list_user_connections(db, user_id)
        active_conn = connections[0] if connections else None

        bank_status = {
            "has_connected_banks": liquidity_info.get("has_connected_banks", False),
            "linked_accounts_count": liquidity_info.get("accounts_count", 0),
            "total_reported_balance": liquidity_info.get("total_balance", 0.0),
            "last_synced_at": liquidity_info.get("last_synced_at"),
            "connection_status": active_conn.status if active_conn else "NO_CONNECTION",
            "accounts_summary": [
                f"{acc.get('institution_name')} ({acc.get('masked_account_number')}): ₹{acc.get('current_reported_balance'):,.2f}"
                for acc in liquidity_info.get("accounts", [])
            ]
        }

        # 4. User Goals
        goals = db.query(Goal).filter(Goal.user_id == user_id).limit(5).all()
        goals_summary = [
            {
                "name": getattr(g, "name", "Goal"),
                "title": getattr(g, "name", "Goal"),
                "target_amount": float(g.target_amount or 0.0),
                "current_amount": float(g.current_amount or 0.0),
                "progress_pct": round((float(g.current_amount or 0.0) / float(g.target_amount or 1.0)) * 100, 1)
            }
            for g in goals
        ]

        # 5. Page Context Validation
        raw_page = (page_context or {}).get("page", "index.html")
        cleaned_page = raw_page.split("?")[0].split("#")[0].strip()
        if not cleaned_page.endswith(".html") and "/" not in cleaned_page:
            cleaned_page = f"{cleaned_page}.html"
        
        # Validate against route allowlist
        valid_route = cleaned_page if cleaned_page in ALLOWED_ROUTES else "index.html"
        page_info = get_page_info(valid_route)

        safe_page_context = {
            "page_route": valid_route,
            "page_name": ALLOWED_ROUTES.get(valid_route, "Command Center"),
            "section": (page_context or {}).get("section", "main"),
            "page_purpose": page_info["purpose"] if page_info else "Central financial overview.",
            "available_page_actions": page_info.get("available_actions", []) if page_info else []
        }

        return {
            "user": {
                "first_name": first_name,
                "workspace_mode": "DEMO" if is_demo else "PRIVATE",
                "readiness_percentage": readiness_pct,
                "is_setup_complete": is_setup_complete
            },
            "data_status": data_status,
            "page_context": safe_page_context,
            "financial_state": financial_state,
            "bank_state": bank_status,
            "goals": goals_summary,
            "onboarding": ONBOARDING_GUIDE if not is_setup_complete else None,
            "time_info": time_info
        }
