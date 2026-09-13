"""
SURE SAVINGS 7.0: Personalization Engine
Derives financial strategy and behavior classification from empirical telemetry.
Eliminates demographic stereotypes and bases advice purely on user behavior.
"""
from typing import Dict, Any, List

class PersonalizationService:
    """
    Classifies user behavior into 9 adaptive financial profiles:
    STABLE, GROWING, VOLATILE, BUFFER_BUILDING, BUFFER_DEPENDENT,
    LIQUIDITY_STRESSED, INCOME_DECLINING, RECOVERING, CRITICAL.
    """

    PROFILES = {
        "STABLE": {
            "title": "Optimized Wealth Preservation",
            "strategy": "Consistent capital accumulation with balanced liquidity buffer.",
            "surplus_cap_pct": 0.70,
            "target_weeks": 6.0
        },
        "GROWING": {
            "title": "Surplus Acceleration",
            "strategy": "Channel expanded gig surplus into long-term financial resilience without lifestyle creep.",
            "surplus_cap_pct": 0.75,
            "target_weeks": 6.0
        },
        "VOLATILE": {
            "title": "Shock-Absorbing Liquidity Defense",
            "strategy": "Maintain larger checking cushion and conservative buffer contributions to navigate unpredictable cash flow.",
            "surplus_cap_pct": 0.60,
            "target_weeks": 8.0
        },
        "BUFFER_BUILDING": {
            "title": "Systematic Buffer Accumulation",
            "strategy": "Lock in 70% of weekly surplus until reaching minimum 4-week essential runway.",
            "surplus_cap_pct": 0.70,
            "target_weeks": 4.0
        },
        "BUFFER_DEPENDENT": {
            "title": "Buffer Preservation Protocol",
            "strategy": "Minimize withdrawals and prioritize baseline essential obligations.",
            "surplus_cap_pct": 0.50,
            "target_weeks": 6.0
        },
        "LIQUIDITY_STRESSED": {
            "title": "Cash Floor Lockdown",
            "strategy": "Halt buffer transfers; preserve checking liquidity to avoid payment defaults.",
            "surplus_cap_pct": 0.0,
            "target_weeks": 4.0
        },
        "INCOME_DECLINING": {
            "title": "Austerity & Spend Rationalization",
            "strategy": "Cut discretionary burn immediately to protect buffer runway.",
            "surplus_cap_pct": 0.50,
            "target_weeks": 6.0
        },
        "RECOVERING": {
            "title": "Resilience Restoration",
            "strategy": "Restore depleted buffer reserves following recent income stabilization.",
            "surplus_cap_pct": 0.65,
            "target_weeks": 4.0
        },
        "CRITICAL": {
            "title": "Emergency Stabilization",
            "strategy": "Immediate cash flow triage: freeze non-essential outflows and safeguard primary shelter/food funds.",
            "surplus_cap_pct": 0.0,
            "target_weeks": 4.0
        }
    }

    @classmethod
    def classify(cls, metrics: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Evaluates financial metrics and classifies into an authoritative behavior profile.
        Accepts either a metrics dictionary or keyword arguments.
        """
        m = dict(metrics or {})
        m.update(kwargs)

        current_income = float(m.get("current_income", 0.0))
        stabilized_income = float(m.get("stabilized_income", 0.0))
        weekly_burn = float(m.get("weekly_burn", 0.0))
        current_buffer = float(m.get("current_buffer", 0.0))
        protected_floor = float(m.get("protected_floor", 0.0))
        liquid_cash = float(m.get("liquid_cash", 0.0))
        surplus = float(m.get("surplus", 0.0))
        volatility = float(m.get("income_volatility", m.get("income_cv", 0.0)))
        coverage_weeks = float(m.get("current_coverage_weeks", m.get("runway_weeks", 0.0)))
        drift_pct = float(m.get("recent_drift_pct", 0.0))
        timing_gaps_count = int(m.get("timing_gaps_count", 0))
        burn_ratio = float(m.get("burn_ratio", 0.0))
        buffer_ratio = float(m.get("buffer_ratio", 0.0))
        resilience_score = float(m.get("resilience_score", 0.0))
        risk_score = float(m.get("risk_score", 0.0))

        # Decision tree based on empirical behavior
        if (weekly_burn > 0 and (current_income == 0.0 or liquid_cash < protected_floor * 0.5) and coverage_weeks < 0.5) or (risk_score >= 85 and coverage_weeks < 0.3):
            profile_name = "CRITICAL"
            rationale = f"Checking cash (₹{liquid_cash:,.0f}) is critically below protected floor (₹{protected_floor:,.0f}) with under 0.5 weeks runway."
            priorities = [
                "Protect emergency cash floor immediately",
                "Defer non-essential outflows",
                "Access emergency reserve if obligations are due within 48 hours"
            ]

        elif (liquid_cash <= protected_floor and protected_floor > 0) or timing_gaps_count > 0 or (risk_score >= 70 and coverage_weeks < 1.0) or (burn_ratio >= 0.90 and buffer_ratio < 0.25):
            profile_name = "LIQUIDITY_STRESSED"
            rationale = f"Liquidity stress detected with elevated risk ({risk_score:.0f}) and limited runway ({coverage_weeks:.1f} weeks)."
            priorities = [
                "Preserve all checking liquidity for upcoming scheduled bills",
                "Pause voluntary buffer contributions this week",
                "Ensure payout receipts settle before high-value debits"
            ]

        elif drift_pct <= -15.0 and current_income > 0:
            profile_name = "INCOME_DECLINING"
            rationale = f"Recent weekly earnings have declined by {abs(drift_pct):.0f}% relative to your stabilized baseline of ₹{stabilized_income:,.0f}."
            priorities = [
                "Trim non-essential discretionary burn",
                "Align weekly commitments with current lower earning plateau",
                "Rely on buffer as a shock absorber without panic"
            ]

        elif volatility >= 0.30:
            profile_name = "VOLATILE"
            rationale = f"Income volatility is elevated ({volatility:.2f}), reflecting variable gig platform payouts."
            priorities = [
                "Calibrate spending strictly against stabilized baseline (₹{stabilized_income:,.0f})",
                "Store high-earning week surpluses to smooth future slow periods",
                "Target an 8-week buffer horizon to neutralize gig earnings volatility"
            ]

        elif (coverage_weeks < 2.0 and surplus > 0) or (buffer_ratio < 0.5 and surplus > 0):
            profile_name = "BUFFER_BUILDING"
            rationale = f"Buffer runway is {coverage_weeks:.1f} weeks (below 4-week target), while surplus is ₹{surplus:,.0f}/wk."
            priorities = [
                f"Deposit 70% of surplus (₹{surplus * 0.70:,.0f}) into Smart Buffer",
                "Keep 30% as discretionary pocket liquidity to avoid austerity fatigue",
                "Maintain momentum toward 4-week self-insurance milestone"
            ]

        elif drift_pct >= 10.0 and surplus > 0:
            profile_name = "GROWING"
            rationale = f"Weekly income is pacing {drift_pct:+.0f}% above historical baseline with a ₹{surplus:,.0f} weekly surplus."
            priorities = [
                "Accelerate buffer expansion to lock in recent earnings gains",
                "Establish secondary goal allocations (equipment, medical reserve)",
                "Avoid expanding fixed recurring commitments during peak income"
            ]

        elif coverage_weeks >= 2.0 and volatility < 0.25:
            profile_name = "STABLE"
            rationale = f"Consistent income stability with {coverage_weeks:.1f} weeks of buffer protection and controlled volatility."
            priorities = [
                "Maintain disciplined Safe-to-Save contributions",
                "Optimize long-term savings yield above liquid floor",
                "Stress-test against multi-week platform downtime"
            ]

        else:
            profile_name = "BUFFER_BUILDING"
            rationale = "Ongoing capital accumulation toward complete financial resilience."
            priorities = [
                "Build emergency buffer to 4 weeks of essential expenses",
                "Log all gig platform receipts consistently",
                "Protect liquidity floor against surprise expenses"
            ]

        config = cls.PROFILES.get(profile_name, cls.PROFILES["STABLE"])
        tone = "cautionary" if profile_name in ("CRITICAL", "LIQUIDITY_STRESSED") else ("encouraging" if profile_name in ("GROWING", "STABLE") else "empowering")

        return {
            "behavior_profile": profile_name,
            "profile": profile_name,
            "title": config["title"],
            "strategy": config["strategy"],
            "rationale": rationale,
            "narrative": f"{rationale} Income volatility is {volatility:.2f}." if profile_name == "VOLATILE" else rationale,
            "tone": tone,
            "action_focus": priorities,
            "priorities": priorities,
            "policy_parameters": {
                "surplus_cap_pct": config["surplus_cap_pct"],
                "target_weeks": config["target_weeks"]
            }
        }
