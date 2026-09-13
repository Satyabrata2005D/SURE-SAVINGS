"""
SURE SAVINGS 8.0: Personal Financial State Machine Service
Defines the authoritative financial lifecycle state machine with 13 discrete states
and deterministic, telemetry-driven state transition rules.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

class FinancialState(str, Enum):
    NEW = "NEW"
    SETUP_IN_PROGRESS = "SETUP_IN_PROGRESS"
    STABLE = "STABLE"
    GROWING = "GROWING"
    VOLATILE = "VOLATILE"
    BUFFER_BUILDING = "BUFFER_BUILDING"
    BUFFER_PROTECTING = "BUFFER_PROTECTING"
    LIQUIDITY_TIGHT = "LIQUIDITY_TIGHT"
    INCOME_DECLINING = "INCOME_DECLINING"
    BUFFER_ABSORBING = "BUFFER_ABSORBING"
    RECOVERING = "RECOVERING"
    HEALTHY = "HEALTHY"
    CRITICAL = "CRITICAL"

class FinancialStateMachineService:
    """
    Evaluates telemetry to transition the user across 13 lifecycle states:
    NEW, SETUP_IN_PROGRESS, STABLE, GROWING, VOLATILE, BUFFER_BUILDING,
    BUFFER_PROTECTING, LIQUIDITY_TIGHT, INCOME_DECLINING, BUFFER_ABSORBING,
    RECOVERING, HEALTHY, CRITICAL.
    """

    STATES = [s.value for s in FinancialState]

    @classmethod
    def evaluate(
        cls,
        telemetry: Dict[str, Any],
        previous_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines current state, transition trigger reason, and verifiable evidence.
        """
        curr_inc = float(telemetry.get("current_income", 0.0))
        stab_inc = float(telemetry.get("stabilized_income", 0.0))
        burn = float(telemetry.get("weekly_burn", 0.0))
        curr_buf = float(telemetry.get("current_buffer", 0.0))
        target_buf = float(telemetry.get("buffer_target", 0.0))
        floor = float(telemetry.get("protected_floor", 0.0))
        liquid_cash = float(telemetry.get("liquid_cash", telemetry.get("checking_cash", 0.0)))
        volatility = float(telemetry.get("income_volatility", 0.0))
        coverage_weeks = float(telemetry.get("current_coverage_weeks", 0.0))
        drift_pct = float(telemetry.get("recent_drift_pct", 0.0))
        timing_gaps_count = int(telemetry.get("timing_gaps_count", 0))
        resilience = int(telemetry.get("resilience_score", 0))
        maturity_level = int(telemetry.get("data_maturity_level", 0))

        # 1. Check for New / Incomplete setup states
        if curr_inc <= 0.0 and burn <= 0.0 and curr_buf <= 0.0:
            if maturity_level == 0:
                state = "NEW"
                reason = "Workspace newly initialized. No financial records recorded yet."
                posture = "Complete the Financial Setup Wizard or Quick Start to initialize telemetry."
            else:
                state = "SETUP_IN_PROGRESS"
                reason = "Baseline setup partially completed. Awaiting full income and burn calibration."
                posture = "Add essential expenses and buffer targets to activate resilience automation."
        elif maturity_level < 2 and (curr_inc <= 0 or burn <= 0):
            state = "SETUP_IN_PROGRESS"
            reason = "Financial calibration requires both income and essential burn to compute surplus."
            posture = "Complete income and expense inputs."

        # 2. Critical & Deficit States
        elif (liquid_cash < floor * 0.5 and floor > 0) and curr_buf <= floor * 0.5:
            state = "CRITICAL"
            reason = f"Primary liquidity (₹{liquid_cash:,.0f}) has severely breached the ₹{floor:,.0f} safety floor with depleted buffer."
            posture = "Halt all sweeps. Retain 100% of liquid inflows in primary checking."
        elif liquid_cash <= floor and curr_buf > floor:
            state = "BUFFER_ABSORBING"
            reason = f"Primary checking dipped to ₹{liquid_cash:,.0f} (at or below floor of ₹{floor:,.0f}); vault buffer is absorbing cash-flow deficit."
            posture = "Deploy buffer smoothing to cover fixed commitments without debt."
        elif timing_gaps_count > 0 or (liquid_cash > floor and (liquid_cash - floor) < 800.0 and timing_gaps_count > 0):
            state = "LIQUIDITY_TIGHT"
            reason = f"Upcoming commitments and intraday timing gaps create near-term liquidity pressure above ₹{floor:,.0f} floor."
            posture = "Reserve available checking cash until upcoming settlement tranche clears."

        # 3. Income Trend States
        elif stab_inc > 0 and curr_inc <= stab_inc * 0.75:
            state = "INCOME_DECLINING"
            reason = f"Current weekly income (₹{curr_inc:,.0f}) is {abs(drift_pct):.0f}% below stabilized baseline (₹{stab_inc:,.0f})."
            posture = "Pause discretionary savings sweeps. Rely on buffer insulation."
        elif volatility >= 0.35:
            state = "VOLATILE"
            reason = f"Gig income coefficient of variation ({volatility:.2f}) indicates severe weekly variance."
            posture = "Maintain conservative 70% surplus safeguard to build runway during peak cycles."

        # 4. Healthy / Buffer Target Reached
        elif target_buf > 0 and curr_buf >= target_buf:
            state = "HEALTHY"
            reason = f"Smart Buffer (₹{curr_buf:,.0f}) has achieved 100% of target runway ({coverage_weeks:.1f} weeks fully funded)."
            posture = "Sustain operational liquidity. Direct surplus to secondary resilience and long-term goals."

        # 5. Recovery & Building States
        elif previous_state in ("CRITICAL", "BUFFER_ABSORBING", "LIQUIDITY_TIGHT", "INCOME_DECLINING") and resilience >= 65 and curr_buf > floor:
            state = "RECOVERING"
            reason = f"Resilience score restored to {resilience}/100 and buffer replenished above safety floor."
            posture = "Gradually resume balanced buffer contributions."
        elif curr_buf >= floor * 1.5 and curr_inc >= burn:
            if drift_pct >= 15.0 and curr_inc > stab_inc:
                state = "GROWING"
                reason = f"Inflows ({drift_pct:+.1f}% above baseline) and active savings sweeps are accelerating buffer growth."
                posture = "Capitalize on high earnings to lock in emergency runway."
            else:
                state = "BUFFER_BUILDING"
                reason = f"Consistent surplus generation is expanding emergency runway ({coverage_weeks:.1f} weeks toward target)."
                posture = "Continue disciplined 70% surplus safeguarding."
        elif curr_buf >= floor and curr_buf > 0:
            state = "BUFFER_PROTECTING"
            reason = f"Buffer (₹{curr_buf:,.0f}) is maintaining core floor protection of ₹{floor:,.0f}."
            posture = "Safeguard liquidity; prioritize building runway to 3+ weeks."
        else:
            state = "STABLE"
            reason = f"Income (₹{curr_inc:,.0f}) and burn (₹{burn:,.0f}) are balanced within standard operating corridors."
            posture = "Maintain current operating routine."

        has_transitioned = previous_state is not None and previous_state != state

        return {
            "current_state": state,
            "previous_state": previous_state or state,
            "has_transitioned": has_transitioned,
            "transition_reason": reason,
            "posture": posture,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "evidence": {
                "current_income": curr_inc,
                "stabilized_income": stab_inc,
                "weekly_burn": burn,
                "current_buffer": curr_buf,
                "buffer_target": target_buf,
                "protected_floor": floor,
                "liquid_cash": liquid_cash,
                "coverage_weeks": coverage_weeks,
                "income_volatility": volatility,
                "recent_drift_pct": drift_pct,
                "timing_gaps_count": timing_gaps_count,
                "resilience_score": resilience
            }
        }
