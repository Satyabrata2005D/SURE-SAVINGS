"""
SURE SAVINGS 8.0: Income Integration Provider Abstraction
Provides honest platform integration contracts for gig platforms (Zomato, Blinkit, Uber, Swiggy, Freelance)
with clear distinction between direct API integrations and structured payout pacing.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class IncomeIntegrationProvider:
    """
    Extensible integration provider interface for gig work and multi-platform payouts.
    Honoring the central architectural rule: never pretend API synchronization exists when
    running on manual or paced local schedules.
    """

    SUPPORTED_PROVIDERS = [
        {
            "id": "zomato",
            "name": "Zomato Partner",
            "category": "Food Delivery",
            "integration_type": "PACED_CADENCE",
            "status": "READY_FOR_PACING",
            "typical_frequency": "weekly",
            "default_payout_day": "Wednesday",
            "direct_api_status": "Staging (OAuth Pending Aggregator Certification)",
            "icon": "🍜"
        },
        {
            "id": "blinkit",
            "name": "Blinkit Quick Delivery",
            "category": "Quick Commerce",
            "integration_type": "PACED_CADENCE",
            "status": "READY_FOR_PACING",
            "typical_frequency": "weekly",
            "default_payout_day": "Tuesday",
            "direct_api_status": "Staging (Partner Portal Webhook Ready)",
            "icon": "⚡"
        },
        {
            "id": "swiggy",
            "name": "Swiggy Delivery Partner",
            "category": "Food Delivery",
            "integration_type": "PACED_CADENCE",
            "status": "READY_FOR_PACING",
            "typical_frequency": "weekly",
            "default_payout_day": "Thursday",
            "direct_api_status": "Staging (Account Aggregator Framework Ready)",
            "icon": "🛵"
        },
        {
            "id": "uber",
            "name": "Uber Driver Fleet",
            "category": "Rideshare",
            "integration_type": "PACED_CADENCE",
            "status": "READY_FOR_PACING",
            "typical_frequency": "weekly",
            "default_payout_day": "Monday",
            "direct_api_status": "Staging (Driver API Gateway Ready)",
            "icon": "🚗"
        },
        {
            "id": "freelance",
            "name": "Direct Client & Freelance Invoicing",
            "category": "Freelance",
            "integration_type": "PACED_CADENCE",
            "status": "READY_FOR_PACING",
            "typical_frequency": "biweekly",
            "default_payout_day": "Friday",
            "direct_api_status": "Direct Invoicing Ledger Available",
            "icon": "💻"
        },
        {
            "id": "other",
            "name": "Custom Income Source",
            "category": "Other",
            "integration_type": "PACED_CADENCE",
            "status": "READY_FOR_PACING",
            "typical_frequency": "monthly",
            "default_payout_day": "1st",
            "direct_api_status": "Custom Telemetry Pacing",
            "icon": "💰"
        }
    ]

    @classmethod
    def get_supported_providers(cls) -> List[Dict[str, Any]]:
        """Returns catalogue of supported gig and income platforms with truthful status."""
        return cls.SUPPORTED_PROVIDERS

    @classmethod
    def connect_payout_cadence(
        cls,
        db: Any,
        user_id: str,
        provider_id: str,
        typical_amount: float,
        frequency: str = "weekly",
        payout_day: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Connects an income platform source for the authenticated user and registers
        the scheduled income pacing in the financial engine.
        """
        from backend.models import User, IncomeSource, CalendarEvent
        from backend.repository import FinancialRepository
        from backend.financial_engine import FinancialEngine

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Find provider spec
        provider = next((p for p in cls.SUPPORTED_PROVIDERS if p["id"] == provider_id.lower()), None)
        provider_name = provider["name"] if provider else provider_id.capitalize()

        # Create or update IncomeSource
        existing = db.query(IncomeSource).filter(
            IncomeSource.user_id == user_id,
            IncomeSource.name == provider_name
        ).first()

        eff_day = payout_day or (provider["default_payout_day"] if provider else "Wednesday")

        if existing:
            existing.typical_amount = float(typical_amount)
            existing.frequency = frequency
            existing.payout_day = eff_day
            existing.is_active = True
            source_obj = existing
        else:
            source_obj = FinancialRepository.add_income_source(
                db=db,
                user_id=user_id,
                name=provider_name,
                typical_amount=float(typical_amount),
                income_type="gig" if provider else "other",
                frequency=frequency,
                payout_day=eff_day,
                expected_delay_days=0
            )

        # Ensure a corresponding recurring CalendarEvent exists
        cal_ev = db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.title.like(f"%{provider_name}%")
        ).first()

        day_map = {"monday": "2026-09-07", "tuesday": "2026-09-01", "wednesday": "2026-09-02", "thursday": "2026-09-03", "friday": "2026-09-04", "saturday": "2026-09-05", "sunday": "2026-09-06"}
        seed_date = day_map.get(eff_day.lower(), "2026-09-03")

        if not cal_ev:
            cal_ev = FinancialRepository.create_calendar_event(
                db=db,
                user_id=user_id,
                title=f"{provider_name} Direct Deposit",
                date_str=seed_date,
                time_str="06:00 PM",
                direction="inflow",
                amount=float(typical_amount),
                category="Income",
                event_type="payout",
                recurrence=frequency,
                is_essential=True
            )
        else:
            cal_ev.amount = float(typical_amount)
            cal_ev.recurrence = frequency

        db.commit()

        # Trigger Universal Recalculation across the workspace
        workspace = FinancialEngine.recalculate_user_workspace(db, user_id)

        return {
            "status": "success",
            "message": f"Connected {provider_name} with ₹{typical_amount:,.0f} {frequency} payout cadence ({eff_day}).",
            "income_source": {
                "id": source_obj.id,
                "platform": source_obj.name,
                "name": source_obj.name,
                "amount": source_obj.typical_amount,
                "typical_amount": source_obj.typical_amount,
                "frequency": source_obj.frequency,
                "payout_day": source_obj.payout_day,
                "is_active": source_obj.is_active
            },
            "calendar_event": cal_ev.to_dict() if hasattr(cal_ev, "to_dict") else {
                "id": cal_ev.id,
                "title": cal_ev.title,
                "amount": cal_ev.amount,
                "date": cal_ev.date_str,
                "recurrence": cal_ev.recurrence
            },
            "direct_api_notice": "Direct API integration is in staging. Payout pacing is actively driving your cash-flow and calendar projections.",
            "workspace": workspace
        }
