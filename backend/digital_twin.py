"""
SURE SAVINGS 7.0: Personal Financial Digital Twin Core
Authoritative, internally computed domain representation of the user's financial state.
Synthesizes Observation (Data) → Understanding (Analytics) → Prediction (Forecast)
→ Decision (Safe-to-Save / Next Best Action) → Explainability.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.models import User
from backend.services.data_quality_service import DataQualityService
from backend.services.personalization_service import PersonalizationService
from backend.services.action_service import ActionService
from backend.services.explainability_service import ExplainabilityService
from backend.services.state_machine_service import FinancialStateMachineService
from backend.services.weather_service import FinancialWeatherService
from backend.services.resilience_plan_service import ResiliencePlanService
from backend.services.recovery_plan_service import RecoveryPlanService
from backend.services.income_diversification_service import IncomeDiversificationService
from backend.services.timeline_service import FinancialTimelineService
from backend.services.transaction_intelligence_service import TransactionIntelligenceService
from backend.services.event_detection_service import EventDetectionService

class FinancialDigitalTwin:
    """
    Authoritative Digital Twin representing a user's total financial intelligence.
    Single unified source of derived truth for APIs, Dashboard 2.0, AI Coach, and Simulator.
    """

    @classmethod
    def build(cls, db: Session, user_id: str) -> Dict[str, Any]:
        from backend.financial_engine import FinancialEngine

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # 1. Authoritative dynamic recalculation
        recalc = FinancialEngine.recalculate_user_workspace(db, user_id)
        prof = recalc["profile"]
        inc = recalc["income_analytics"]
        res = recalc["resilience"]
        risk = recalc["risk"]
        rec = recalc["recommendation"]
        cf = recalc["cash_flow"]
        readiness = recalc["readiness"]

        # 2. Data Quality Analysis
        quality = DataQualityService.evaluate(db, user_id)

        # 3. Behavior-Based Personalization
        telemetry_for_classification = {
            "current_income": prof.get("current_income", 0.0),
            "stabilized_income": prof.get("stabilized_income", 0.0),
            "weekly_burn": prof.get("weekly_burn", 0.0),
            "current_buffer": prof.get("current_buffer", 0.0),
            "protected_floor": prof.get("protected_floor", 0.0),
            "liquid_cash": (user.liquidity_position.checking_cash if user.liquidity_position else 0.0),
            "surplus": prof.get("surplus", 0.0),
            "income_volatility": prof.get("income_volatility", 0.0),
            "current_coverage_weeks": prof.get("current_coverage_weeks", 0.0),
            "recent_drift_pct": inc.get("recent_drift_pct", 0.0),
            "timing_gaps_count": len(cf.get("timing_gaps", []))
        }
        personalization = PersonalizationService.classify(telemetry_for_classification)

        # Update user's behavior profile on record
        user.behavior_profile = personalization["behavior_profile"]
        db.commit()

        # 4. Synthesize Digital Twin State
        curr_inc = prof["current_income"]
        burn = prof["weekly_burn"]
        disc_burn = prof.get("weekly_discretionary_burn", 0.0)
        curr_buf = prof["current_buffer"]
        target_buf = prof["buffer_target"]
        floor = prof["protected_floor"]
        checking_cash = user.liquidity_position.checking_cash if user.liquidity_position else 0.0
        savings_cash = user.liquidity_position.savings_balance if user.liquidity_position else 0.0
        total_liquid = checking_cash + savings_cash
        safe_liq = max(0.0, total_liquid - floor)

        # Buffer lifecycle state determination
        if curr_buf >= target_buf and target_buf > 0:
            lifecycle_state = "HEALTHY"
        elif curr_buf > floor * 1.5:
            lifecycle_state = "BUILDING"
        elif curr_buf > floor:
            lifecycle_state = "PROTECTING"
        elif curr_buf > 0:
            lifecycle_state = "ABSORBING"
        elif checking_cash <= floor and floor > 0:
            lifecycle_state = "CRITICAL"
        else:
            lifecycle_state = "BUILDING"

        now_iso = datetime.now(timezone.utc).isoformat()
        source_version = user.source_data_version or 1

        # Intermediate preview for explainability and next best action
        preview_twin = {
            "income_state": {
                "current_income": curr_inc,
                "stabilized_income": prof["stabilized_income"],
                "surplus": prof["surplus"],
                "recommended_contribution": prof["recommended_contribution"],
                "free_pocket_liquidity": prof["free_pocket_liquidity"],
                "income_volatility": prof["income_volatility"]
            },
            "expense_state": {
                "essential_burn": burn,
                "discretionary_burn": disc_burn,
                "total_burn": burn + disc_burn
            },
            "liquidity_state": {
                "checking_cash": checking_cash,
                "savings_balance": savings_cash,
                "total_liquid_cash": total_liquid,
                "protected_floor": floor,
                "safe_liquidity_above_floor": safe_liq
            },
            "buffer_state": {
                "balance": curr_buf,
                "target": target_buf,
                "coverage_weeks": prof["current_coverage_weeks"]
            },
            "obligation_state": {
                "liquidity_gaps": cf.get("timing_gaps", [])
            },
            "readiness_state": readiness,
            "behavior_profile": personalization["behavior_profile"],
            "strategy": personalization
        }

        # 5. Next Best Action Engine Evaluation
        action_plan = ActionService.evaluate(preview_twin)

        # 6. Explainability Traces
        explainability_traces = {
            "safe_to_save": ExplainabilityService.explain_metric("safe_to_save", preview_twin),
            "resilience_score": ExplainabilityService.explain_metric("resilience_score", preview_twin),
            "risk_score": ExplainabilityService.explain_metric("risk_score", preview_twin),
            "stabilized_income": ExplainabilityService.explain_metric("stabilized_income", preview_twin)
        }

        # 7. SURE SAVINGS 8.0: Adaptive Operating System Services
        state_telemetry = {
            **telemetry_for_classification,
            "resilience_score": res.get("resilience_score", 0),
            "data_maturity_level": quality.get("maturity_level", 1) if quality else 1
        }
        state_machine_eval = FinancialStateMachineService.evaluate(state_telemetry)
        financial_state = state_machine_eval.get("current_state", "STABLE")

        preview_twin_8 = {
            **preview_twin,
            "financial_state": financial_state,
            "state_machine": state_machine_eval,
            "profile": prof,
            "is_demo_user": user.is_demo_user
        }

        weather_eval = FinancialWeatherService.evaluate(preview_twin_8)
        resilience_plan_eval = ResiliencePlanService.generate_plan(preview_twin_8)
        recovery_plan_eval = RecoveryPlanService.generate_plans(preview_twin_8)
        
        income_sources_raw = [
            {"id": s.id, "name": s.name, "amount": s.typical_amount, "frequency": s.frequency, "is_active": s.is_active}
            for s in (user.income_sources or [])
        ]
        income_diversification_eval = IncomeDiversificationService.evaluate(income_sources_raw, curr_inc)
        timeline_story_eval = FinancialTimelineService.get_financial_story(db, user_id)
        weekly_briefing_eval = TransactionIntelligenceService.generate_weekly_briefing(preview_twin_8, weather_eval, resilience_plan_eval)
        multi_horizon_eval = TransactionIntelligenceService.generate_multi_horizon_outlook(preview_twin_8)
        what_changed_eval = EventDetectionService.compute_what_changed(None, preview_twin_8)

        # 8. Unified Complete Digital Twin 2.0
        twin = {
            # Multi-layer 8.0 authoritative contract
            "digital_twin_version": "7.0",
            "resilience_os_version": "8.0",
            "source_data_version": source_version,
            "calculated_at": now_iso,
            "workspace_mode": "DEMO ENVIRONMENT" if user.is_demo_user else "PRIVATE WORKSPACE",
            "financial_state": financial_state,
            "state_machine": state_machine_eval,
            "financial_weather": weather_eval,
            "resilience_plan": resilience_plan_eval,
            "recovery_plan": recovery_plan_eval,
            "income_diversification": income_diversification_eval,
            "timeline_story": timeline_story_eval,
            "weekly_briefing": weekly_briefing_eval,
            "multi_horizon_outlook": multi_horizon_eval,
            "what_changed": what_changed_eval,

            # Layer 1: Observation (Ground Truth Facts)
            "observation": {
                "profile": prof,
                "income_sources": [
                    {"id": s.id, "name": s.name, "amount": s.typical_amount, "frequency": s.frequency, "is_active": s.is_active}
                    for s in (user.income_sources or [])
                ],
                "expense_items": [
                    {"id": e.id, "description": e.description, "amount": e.amount, "frequency": e.frequency, "is_essential": e.is_essential}
                    for e in (user.expense_items or [])
                ],
                "liquidity": {
                    "checking_cash": checking_cash,
                    "savings_balance": savings_cash,
                    "total_liquid_cash": total_liquid,
                    "protected_floor": floor
                },
                "obligations": [
                    {"id": o.id, "description": o.description, "amount": o.amount, "due_date": getattr(o, "date_str", "")}
                    for o in (user.obligations or [])
                ],
                "goals": [
                    {"id": g.id, "name": g.name, "target": g.target_amount, "current": g.current_amount}
                    for g in (user.goals or [])
                ],
                "history": [
                    {"week": h.week, "income": h.income, "is_forecast": h.is_forecast}
                    for h in (user.weekly_history or [])
                ]
            },

            # Layer 2: Understanding (Analytical Meaning)
            "understanding": {
                "stabilized_income": {
                    "amount": prof["stabilized_income"],
                    "method": "Tier 2: Robust Median" if len(user.weekly_history or []) >= 4 else "Tier 1: Baseline Carryforward",
                    "status": "STABLE" if prof["stabilized_income"] > 0 else "AWAITING_DATA"
                },
                "resilience": {**res, "score": res.get("resilience_score", 0)},
                "risk": {**risk, "score": risk.get("risk_score", 0)},
                "runway": {
                    "weeks": prof["current_coverage_weeks"],
                    "status": lifecycle_state,
                    "target_weeks": prof.get("buffer_target_weeks", 4.0)
                },
                "burn": {
                    "essential": burn,
                    "discretionary": disc_burn,
                    "total": burn + disc_burn
                },
                "volatility": {
                    "cv": prof["income_volatility"],
                    "status": prof["volatility_status"]
                },
                "cash_flow": cf
            },

            # Layer 3: Prediction (Future Trajectory)
            "prediction": {
                "forecast": {
                    "next_week": prof["forecast_next_week"],
                    "confidence": prof["forecast_confidence"],
                    "status": prof["forecast_status"]
                },
                "trend": inc.get("trend", "STABLE")
            },

            # Layer 4: Decisions (What to do)
            "decisions": {
                "safe_to_save": {
                    "recommended_save": prof["recommended_contribution"],
                    "surplus": prof["surplus"],
                    "free_pocket": prof["free_pocket_liquidity"],
                    "status": rec.get("status", "AUTHORITATIVE")
                },
                "next_best_action": action_plan,
                "surplus_safeguard": rec
            },

            # Layer 5: Explainability (Why and How)
            "explainability": explainability_traces,

            # Data Quality & Readiness
            "data_quality": quality,
            "data_quality_state": quality,
            "readiness_state": readiness,
            "behavior_profile": personalization["behavior_profile"],
            "strategy": personalization,
            "next_best_action": action_plan,

            # Legacy Keys for 100% Backward Compatibility
            "metadata": {
                "engine_version": "8.0.0",
                "policy_version": "v8.0",
                "source_data_version": source_version,
                "calculated_at": now_iso,
                "workspace_mode": "DEMO ENVIRONMENT" if user.is_demo_user else "PRIVATE WORKSPACE"
            },
            "identity_context": {
                "user_id": user.id,
                "name": user.name,
                "first_name": user.first_name or (user.name.split()[0] if user.name else "Member"),
                "occupation": user.occupation,
                "currency": user.currency or "INR",
                "timezone": user.timezone or "Asia/Kolkata",
                "locale": user.locale or "en-IN",
                "is_demo_user": user.is_demo_user
            },
            "income_state": {
                "current_income": curr_inc,
                "stabilized_income": prof["stabilized_income"],
                "average_income": inc.get("average_income", curr_inc),
                "median_income": inc.get("median_income", curr_inc),
                "income_volatility": prof["income_volatility"],
                "volatility_status": prof["volatility_status"],
                "recent_drift_pct": inc.get("recent_drift_pct", 0.0),
                "sources_count": len(user.income_sources or []),
                "history_weeks_count": len(user.weekly_history or []),
                "surplus": prof["surplus"],
                "recommended_contribution": prof["recommended_contribution"],
                "free_pocket_liquidity": prof["free_pocket_liquidity"]
            },
            "expense_state": {
                "essential_burn": burn,
                "discretionary_burn": disc_burn,
                "total_burn": burn + disc_burn,
                "essential_ratio": round(burn / (burn + disc_burn), 2) if (burn + disc_burn) > 0 else 1.0,
                "expense_pressure": "HIGH" if (burn > curr_inc and curr_inc > 0) else ("MODERATE" if burn > curr_inc * 0.75 else "BALANCED"),
                "tracked_items_count": len(user.expense_items or [])
            },
            "liquidity_state": {
                "checking_cash": checking_cash,
                "savings_balance": savings_cash,
                "total_liquid_cash": total_liquid,
                "protected_floor": floor,
                "safe_liquidity_above_floor": safe_liq,
                "floor_status": "INTACT" if checking_cash >= floor else "BREACHED",
                "coverage_days": round((checking_cash / (burn / 7.0)), 1) if burn > 0 else 0.0
            },
            "buffer_state": {
                "balance": curr_buf,
                "target": target_buf,
                "target_weeks": prof.get("buffer_target_weeks", 4.0),
                "coverage_weeks": prof["current_coverage_weeks"],
                "safe_to_use": prof["safe_to_use_above_floor"],
                "lifecycle_state": lifecycle_state,
                "buffer_gap": max(0.0, target_buf - curr_buf)
            },
            "obligation_state": {
                "scheduled_count": len(user.obligations or []),
                "timing_conflicts_count": len(cf.get("timing_gaps", [])),
                "liquidity_gaps": cf.get("timing_gaps", []),
                "cash_flow_status": prof["cash_flow_status"],
                "timeline_events": cf.get("timeline", [])
            },
            "goal_state": {
                "active_goals_count": len(user.goals or []),
                "total_target_amount": sum(g.target_amount for g in (user.goals or []) if g.is_active),
                "total_saved_amount": sum(g.current_amount for g in (user.goals or []) if g.is_active)
            },
            "forecast_state": {
                "forecast_next_week": prof["forecast_next_week"],
                "forecast_confidence": prof["forecast_confidence"],
                "forecast_status": prof["forecast_status"],
                "method": "Tier 3: Weighted Trend" if len(user.weekly_history or []) >= 8 else ("Tier 2: Robust Median" if len(user.weekly_history or []) >= 4 else "Tier 1: Baseline Carryforward"),
                "data_points_used": len(user.weekly_history or [])
            },
            "risk_state": risk,
            "resilience_state": res
        }

        return twin
