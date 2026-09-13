"""
SURE SAVINGS 8.0: Recovery Planner Service
Generates personalized, data-driven recovery pathways (Conservative, Balanced, Accelerated)
to rebuild buffer runway and recover from shocks with explicit, transparent trade-offs.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class RecoveryPlanService:
    """
    Computes 3 distinct recovery strategies (Conservative, Balanced, Accelerated)
    to bridge the gap between Current Buffer and Target Buffer.
    """

    @classmethod
    def generate_plans(
        cls,
        digital_twin_or_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        p = digital_twin_or_profile.get("observation", {}).get("profile", {}) or digital_twin_or_profile.get("profile", {}) or digital_twin_or_profile
        und = digital_twin_or_profile.get("understanding", {})
        dec = digital_twin_or_profile.get("decisions", {})

        curr_inc = float(p.get("current_income", 0.0))
        stab_inc = float(p.get("stabilized_income", und.get("stabilized_income", {}).get("amount", 0.0)))
        burn = float(p.get("weekly_burn", und.get("burn", {}).get("essential", 0.0)))
        curr_buf = float(p.get("current_buffer", 0.0))
        target_buf = float(p.get("buffer_target", 15000.0))
        surplus = float(p.get("surplus", dec.get("safe_to_save", {}).get("surplus", 0.0)))
        save_rec = float(p.get("recommended_contribution", dec.get("safe_to_save", {}).get("recommended_save", 0.0)))
        floor = float(p.get("protected_floor", 3500.0))
        resilience = int(und.get("resilience", {}).get("score", p.get("resilience_score", 0)))
        coverage = float(und.get("runway", {}).get("weeks", p.get("current_coverage_weeks", 0.0)))

        buffer_gap = max(0.0, target_buf - curr_buf)
        target_weeks = round(target_buf / burn, 1) if burn > 0 else 4.0

        if curr_inc <= 0 and burn <= 0 and curr_buf <= 0:
            return {
                "status": "INSUFFICIENT_DATA",
                "message": "Enter your baseline financial data to generate personalized recovery pathways.",
                "buffer_gap": 0.0,
                "current_buffer": 0.0,
                "target_buffer": 0.0,
                "plans": []
            }

        # If buffer target is already reached
        if buffer_gap <= 0.0:
            return {
                "status": "TARGET_ACHIEVED",
                "message": f"Smart Buffer target of ₹{target_buf:,.0f} is fully achieved ({coverage:.1f} weeks coverage).",
                "buffer_gap": 0.0,
                "current_buffer": curr_buf,
                "target_buffer": target_buf,
                "plans": []
            }

        # Base safe capacity
        nominal_safe = save_rec if save_rec > 0 else max(500.0, (curr_inc - burn) * 0.5 if curr_inc > burn else 500.0)

        # 1. Conservative Plan: ~65% of safe rate
        c_rate = round(max(300.0, nominal_safe * 0.65) / 50.0) * 50.0
        c_weeks = round(buffer_gap / c_rate, 1)
        c_pocket = max(0.0, surplus - c_rate)
        c_resilience_delta = min(15, max(4, int(round(buffer_gap / 1200.0))))

        # 2. Balanced Plan: Standard safe rate (100%)
        b_rate = round(nominal_safe / 50.0) * 50.0
        b_weeks = round(buffer_gap / b_rate, 1)
        b_pocket = max(0.0, surplus - b_rate)
        b_resilience_delta = min(20, max(6, int(round(buffer_gap / 900.0))))

        # 3. Accelerated Plan: ~135% of safe rate (capped by surplus)
        max_accel = min(surplus if surplus > 0 else nominal_safe * 1.5, nominal_safe * 1.4)
        a_rate = round(max(b_rate + 200.0, max_accel) / 50.0) * 50.0
        a_weeks = round(buffer_gap / a_rate, 1)
        a_pocket = max(0.0, surplus - a_rate)
        a_resilience_delta = min(25, max(8, int(round(buffer_gap / 700.0))))

        plans = [
            {
                "id": "plan_conservative",
                "tier": "Conservative",
                "label": "Conservative Recovery",
                "weekly_contribution": c_rate,
                "weeks_to_target": c_weeks,
                "liquidity_retained_weekly": c_pocket,
                "cash_flexibility": "Maximum",
                "risk_posture": "Very Low Liquidity Stress",
                "resilience_delta": c_resilience_delta,
                "projected_resilience": min(95, resilience + c_resilience_delta),
                "is_recommended": False,
                "badge_color": "emerald",
                "trade_off": f"Smallest impact on daily cash flow (leaves ₹{c_pocket:,.0f} pocket cash), but requires {c_weeks} weeks to achieve {target_weeks}-week target."
            },
            {
                "id": "plan_balanced",
                "tier": "Balanced",
                "label": "Balanced Recovery",
                "weekly_contribution": b_rate,
                "weeks_to_target": b_weeks,
                "liquidity_retained_weekly": b_pocket,
                "cash_flexibility": "Balanced",
                "risk_posture": "Optimal Safe-to-Save Safeguard",
                "resilience_delta": b_resilience_delta,
                "projected_resilience": min(95, resilience + b_resilience_delta),
                "is_recommended": True,
                "badge_color": "tertiary",
                "trade_off": f"Optimal tradeoff: Restores full runway in {b_weeks} weeks while preserving ₹{b_pocket:,.0f} free pocket liquidity and ₹{floor:,.0f} floor."
            },
            {
                "id": "plan_accelerated",
                "tier": "Accelerated",
                "label": "Accelerated Recovery",
                "weekly_contribution": a_rate,
                "weeks_to_target": a_weeks,
                "liquidity_retained_weekly": a_pocket,
                "cash_flexibility": "Constrained",
                "risk_posture": "Aggressive Runway Build",
                "resilience_delta": a_resilience_delta,
                "projected_resilience": min(95, resilience + a_resilience_delta),
                "is_recommended": False,
                "badge_color": "amber",
                "trade_off": f"Fastest target completion ({a_weeks} weeks), but leaves only ₹{a_pocket:,.0f} pocket cash and tighter checking buffer."
            }
        ]

        pathways = {
            "conservative": plans[0],
            "balanced": plans[1],
            "accelerated": plans[2]
        }

        return {
            "status": "RECOVERY_ACTIVE",
            "current_buffer": curr_buf,
            "target_buffer": target_buf,
            "buffer_gap": buffer_gap,
            "current_coverage_weeks": coverage,
            "target_coverage_weeks": target_weeks,
            "current_resilience": resilience,
            "recommended_plan": "Balanced Recovery",
            "plans": plans,
            "pathways": pathways,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
