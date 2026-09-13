"""
SURE SAVINGS 7.0: Next Best Action Engine
Synthesizes the Digital Twin into an authoritative single Next Best Action
and supporting secondary recommendations. Prevents decision fatigue.
"""
from typing import Dict, Any, List, Optional

class ActionService:
    """
    Evaluates financial state and produces a prioritized, actionable recommendation.
    Answers: "What is the single most important and safest financial move right now?"
    """

    @classmethod
    def evaluate(cls, twin_or_db: Any, user_id: Optional[str] = None) -> Dict[str, Any]:
        if user_id is not None:
            from backend.digital_twin import FinancialDigitalTwin
            twin = FinancialDigitalTwin.build(twin_or_db, user_id)
        elif isinstance(twin_or_db, dict):
            twin = twin_or_db
        else:
            twin = {}

        income_state = twin.get("income_state", {})
        expense_state = twin.get("expense_state", {})
        liq_state = twin.get("liquidity_state", {})
        buffer_state = twin.get("buffer_state", {})
        ob_state = twin.get("obligation_state", {})
        readiness = twin.get("readiness_state", {})
        behavior = twin.get("behavior_profile", "STABLE")

        curr_inc = float(income_state.get("current_income", 0.0))
        surplus = float(income_state.get("surplus", 0.0))
        rec_amt = float(income_state.get("recommended_contribution", 0.0))
        liquid_cash = float(liq_state.get("liquid_cash", 0.0))
        floor = float(liq_state.get("protected_floor", 0.0))
        buffer_bal = float(buffer_state.get("balance", 0.0))
        target_buf = float(buffer_state.get("target", 0.0))
        coverage = float(buffer_state.get("coverage_weeks", 0.0))
        burn = float(expense_state.get("essential_burn", 0.0))
        gaps = ob_state.get("liquidity_gaps", [])
        maturity = int(readiness.get("maturity_level", 0))

        # Scenario 1: New workspace / zero data
        if maturity < 2 or (curr_inc == 0.0 and burn == 0.0):
            return {
                "status": "AWAITING_DATA",
                "priority": "CRITICAL",
                "confidence": 0.85,
                "expected_impact": "Unlocks automated surplus calculations and early-warning risk radar.",
                "reason": "Enter your weekly income and baseline expenses to activate Safe-to-Save and resilience analytics.",
                "behavior_strategy": "Establish your financial baseline to unlock personalized intelligence.",
                "primary_action": {
                    "action_type": "COMPLETE_SETUP",
                    "title": "Complete Quick Start Financial Calibration",
                    "reason": "Enter your weekly income and baseline expenses to activate Safe-to-Save and resilience analytics.",
                    "priority": "CRITICAL",
                    "expected_impact": "Unlocks automated surplus calculations and early-warning risk radar.",
                    "confidence": 0.85,
                    "action_url": "#quickstart"
                },
                "secondary_actions": [
                    {
                        "action_type": "EXPLORE_DEMO",
                        "title": "Explore Sample Portfolio",
                        "reason": "Review Arjun K.'s canonical portfolio to see how the platform protects fluctuating gig earners."
                    }
                ]
            }

        # Scenario 2: Critical Liquidity Gap / Floor Breach Risk
        if gaps:
            first_gap = gaps[0]
            gap_amt = float(first_gap.get("projected_deficit", 0.0))
            act = {
                "status": "ACTION_AVAILABLE",
                "priority": "HIGH",
                "confidence": 0.95,
                "expected_impact": "Eliminates intraday cash shortfalls and prevents payment penalties.",
                "reason": f"Scheduled bill '{first_gap.get('description', 'Obligation')}' will breach your ₹{floor:,.0f} cash floor before pending income clears.",
                "primary_action": {
                    "action_type": "RESOLVE_TIMING_GAP",
                    "title": f"Protect ₹{gap_amt:,.0f} Ahead of {first_gap.get('date', 'Upcoming Due Date')}",
                    "reason": f"Scheduled bill '{first_gap.get('description', 'Obligation')}' will breach your ₹{floor:,.0f} cash floor before pending income clears.",
                    "priority": "HIGH",
                    "expected_impact": "Eliminates intraday cash shortfalls and prevents payment penalties.",
                    "confidence": 0.95,
                    "cta_text": "Review Cash Flow Timeline",
                    "action_payload": {"page": "planner.html", "gap_date": first_gap.get("date")}
                },
                "secondary_actions": [
                    {
                        "action_type": "PAUSE_BUFFER",
                        "title": "Pause Voluntary Buffer Deposits",
                        "reason": "Keep all checking liquidity available until scheduled commitments clear."
                    }
                ]
            }
            return act

        # Scenario 3: Checking Cash at or below Floor
        if liquid_cash > 0 and liquid_cash <= floor:
            act = {
                "status": "ACTION_AVAILABLE",
                "priority": "HIGH",
                "confidence": 0.96,
                "expected_impact": "Maintains day-to-day liquidity for essential daily expenses.",
                "reason": f"Current cash (₹{liquid_cash:,.0f}) is at your defined safety floor. Do not move money into savings this week.",
                "primary_action": {
                    "action_type": "HOLD_LIQUIDITY",
                    "title": f"Preserve Checking Cushion (Floor: ₹{floor:,.0f})",
                    "reason": f"Current cash (₹{liquid_cash:,.0f}) is at your defined safety floor. Do not move money into savings this week.",
                    "priority": "HIGH",
                    "expected_impact": "Maintains day-to-day liquidity for essential daily expenses.",
                    "confidence": 0.96,
                    "cta_text": "View Liquidity Status",
                    "action_payload": {"page": "planner.html"}
                },
                "secondary_actions": [
                    {
                        "action_type": "MONITOR_PAYOUTS",
                        "title": "Track Next Gig Settlement",
                        "reason": "Wait for incoming platform payouts to replenish cash above your floor."
                    }
                ]
            }
            return act

        # Scenario 4: Healthy Safe-to-Save Surplus Available
        if rec_amt > 0 and (liquid_cash > floor or liquid_cash == 0):
            projected_buf = buffer_bal + rec_amt
            projected_runway = round(projected_buf / burn, 1) if burn > 0 else 0.0
            act = {
                "status": "ACTION_AVAILABLE",
                "priority": "MEDIUM",
                "confidence": 0.94,
                "expected_impact": f"Expands runway from {coverage:.1f} → {projected_runway:.1f} weeks.",
                "reason": f"Weekly income is ₹{surplus:,.0f} above baseline burn. Saving ₹{rec_amt:,.0f} preserves your ₹{floor:,.0f} floor and leaves ₹{surplus - rec_amt:,.0f} as free pocket cash.",
                "primary_action": {
                    "action_type": "SAVE_SURPLUS",
                    "title": f"Lock In ₹{rec_amt:,.0f} into Smart Buffer",
                    "reason": f"Weekly income is ₹{surplus:,.0f} above baseline burn. Saving ₹{rec_amt:,.0f} preserves your ₹{floor:,.0f} floor and leaves ₹{surplus - rec_amt:,.0f} as free pocket cash.",
                    "priority": "MEDIUM",
                    "expected_impact": f"Expands runway from {coverage:.1f} → {projected_runway:.1f} weeks.",
                    "confidence": 0.94,
                    "cta_text": f"Approve ₹{rec_amt:,.0f} Buffer Deposit",
                    "action_payload": {"amount": rec_amt, "action": "CONTRIBUTION"}
                },
                "secondary_actions": [
                    {
                        "action_type": "ENJOY_POCKET_CASH",
                        "title": f"Unallocated Pocket Cash: ₹{surplus - rec_amt:,.0f}",
                        "reason": "Reserved for guilt-free discretionary spending to prevent austerity fatigue."
                    }
                ]
            }
            return act

        # Scenario 5: Buffer Target Reached / Maintenance
        if buffer_bal >= target_buf and target_buf > 0:
            act = {
                "status": "ACTION_AVAILABLE",
                "priority": "LOW",
                "confidence": 0.98,
                "expected_impact": "Complete emergency insulation achieved. Surplus can now be allocated to secondary growth goals.",
                "reason": f"Your buffer has reached ₹{buffer_bal:,.0f} ({coverage:.1f} weeks runway), meeting your target of ₹{target_buf:,.0f}.",
                "primary_action": {
                    "action_type": "MAINTAIN_BUFFER",
                    "title": "Smart Buffer Fully Funded (Target Met)",
                    "reason": f"Your buffer has reached ₹{buffer_bal:,.0f} ({coverage:.1f} weeks runway), meeting your target of ₹{target_buf:,.0f}.",
                    "priority": "LOW",
                    "expected_impact": "Complete emergency insulation achieved. Surplus can now be allocated to secondary growth goals.",
                    "confidence": 0.98,
                    "cta_text": "Manage Financial Goals",
                    "action_payload": {"page": "goals.html"}
                },
                "secondary_actions": [
                    {
                        "action_type": "SECONDARY_INVESTING",
                        "title": "Direct Surplus to Secondary Goals",
                        "reason": "Fund tool/equipment upgrades, health insurance, or long-term investments."
                    }
                ]
            }
            return act

        # Default fallback action
        return {
            "status": "NO_ACTION_REQUIRED",
            "priority": "LOW",
            "confidence": 0.90,
            "expected_impact": "Financial position remains stable.",
            "reason": "Current liquidity and spending are in equilibrium with your historical baseline.",
            "primary_action": {
                "action_type": "MONITOR_STABILITY",
                "title": "Maintain Current Cash Trajectory",
                "reason": "Current liquidity and spending are in equilibrium with your historical baseline.",
                "priority": "LOW",
                "expected_impact": "Financial position remains stable.",
                "confidence": 0.90,
                "cta_text": "Review Dashboard",
                "action_payload": {"page": "index.html"}
            },
            "secondary_actions": []
        }
