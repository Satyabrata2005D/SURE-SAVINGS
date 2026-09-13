"""
SURE SAVINGS 8.0: Financial Weather Engine
Translates complex multi-dimensional financial telemetry into an intuitive,
human-interpretable financial weather forecast across 7D, 30D, and 90D horizons.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

class FinancialWeatherService:
    """
    Computes holistic financial weather telemetry:
    - Overall Outlook (POSITIVE, STABLE, STABLE_WITH_ATTENTION, PRESSURED, HIGH_PRESSURE, CRITICAL)
    - Sub-vectors: income_outlook, liquidity_pressure, buffer_condition, obligation_pressure
    - Multi-horizon synthesis: 7D, 30D, 90D
    - Primary Driver diagnosis
    - Next 7 Days day-by-day cash flow pressure map
    """

    OUTLOOK_METRICS = {
        "POSITIVE": {"label": "CLEAR & POSITIVE", "badge": "emerald", "icon": "☀️"},
        "STABLE": {"label": "STABLE", "badge": "emerald", "icon": "🌤️"},
        "STABLE_WITH_ATTENTION": {"label": "STABLE WITH ATTENTION", "badge": "amber", "icon": "⛅"},
        "PRESSURED": {"label": "MODERATE PRESSURE", "badge": "amber", "icon": "🌦️"},
        "HIGH_PRESSURE": {"label": "HIGH PRESSURE", "badge": "rose", "icon": "🌧️"},
        "CRITICAL": {"label": "CRITICAL RISK", "badge": "rose", "icon": "⛈️"}
    }

    @classmethod
    def evaluate(
        cls,
        twin_or_telemetry: Dict[str, Any],
        horizon: str = "7D"
    ) -> Dict[str, Any]:
        """
        Synthesizes financial telemetry into a complete financial weather report.
        """
        # Extract normalized telemetry
        p = twin_or_telemetry.get("observation", {}).get("profile", {}) or twin_or_telemetry.get("profile", {}) or twin_or_telemetry
        u = twin_or_telemetry.get("understanding", {})
        d = twin_or_telemetry.get("decisions", {})

        curr_inc = float(p.get("current_income", 0.0))
        stab_inc = float(p.get("stabilized_income", u.get("stabilized_income", {}).get("amount", 0.0)))
        burn = float(p.get("weekly_burn", u.get("burn", {}).get("essential", 0.0)))
        curr_buf = float(p.get("current_buffer", twin_or_telemetry.get("buffer_state", {}).get("balance", 0.0)))
        target_buf = float(p.get("buffer_target", twin_or_telemetry.get("buffer_state", {}).get("target", 0.0)))
        floor = float(p.get("protected_floor", twin_or_telemetry.get("liquidity_state", {}).get("protected_floor", 0.0)))
        coverage_weeks = float(p.get("current_coverage_weeks", u.get("runway", {}).get("weeks", 0.0)))
        volatility = float(p.get("income_volatility", 0.0))
        drift_pct = float(p.get("recent_drift_pct", 0.0))
        
        cf = u.get("cash_flow", {}) or twin_or_telemetry.get("cash_flow", {})
        timing_gaps = cf.get("timing_gaps", []) or []
        obligations = twin_or_telemetry.get("observation", {}).get("obligations", []) or []

        # Zero-data check
        if curr_inc <= 0 and burn <= 0 and curr_buf <= 0:
            return {
                "overall": "AWAITING_DATA",
                "label": "CALIBRATING TELEMETRY",
                "badge_color": "stone",
                "icon": "⏳",
                "horizon": horizon,
                "main_driver": "Financial profile awaiting initial income, expense, and buffer inputs.",
                "sub_outlooks": {
                    "income": "AWAITING_DATA",
                    "liquidity": "AWAITING_DATA",
                    "buffer": "AWAITING_DATA",
                    "obligations": "AWAITING_DATA"
                },
                "daily_forecast": [],
                "horizons": {
                    "7D": {"outlook": "AWAITING_DATA", "summary": "Add baseline data to view 7-day weather."},
                    "30D": {"outlook": "AWAITING_DATA", "summary": "Add baseline data to view 30-day outlook."},
                    "90D": {"outlook": "AWAITING_DATA", "summary": "Add baseline data to view 90-day trajectory."}
                }
            }

        # 1. Income Outlook Vector
        if stab_inc > 0 and curr_inc >= stab_inc * 1.15:
            income_outlook = "IMPROVING"
            income_label = "↗ Improving (+15% above baseline)"
        elif stab_inc > 0 and curr_inc <= stab_inc * 0.80:
            income_outlook = "WEAKENING"
            income_label = "↘ Weakening (-20% below baseline)"
        elif volatility >= 0.35:
            income_outlook = "VOLATILE"
            income_label = "● Volatile (Erratic weekly swings)"
        else:
            income_outlook = "STABLE"
            income_label = "→ Stable (Within baseline corridor)"

        # 2. Obligation Pressure Vector
        total_sched_debt = sum(float(o.get("amount", 0.0)) for o in obligations)
        if len(timing_gaps) > 0:
            obligation_pressure = "ELEVATED"
            ob_label = f"● Elevated ({len(timing_gaps)} intraday timing mismatch detected)"
        elif total_sched_debt >= burn * 0.8:
            obligation_pressure = "ELEVATED"
            ob_label = "● Elevated (Upcoming fixed commitments absorb majority of burn)"
        elif total_sched_debt > 0:
            obligation_pressure = "MODERATE"
            ob_label = "● Moderate (Commitments scheduled and tracked)"
        else:
            obligation_pressure = "MINIMAL"
            ob_label = "● Minimal (No outstanding immediate debits)"

        # 3. Buffer Condition Vector
        if target_buf > 0 and curr_buf >= target_buf:
            buffer_condition = "HEALTHY"
            buf_label = f"★ Healthy ({coverage_weeks:.1f} weeks fully funded)"
        elif curr_buf >= floor * 1.5:
            buffer_condition = "BUILDING"
            buf_label = f"↗ Building ({curr_buf:,.0f} reserve, {coverage_weeks:.1f} wks runway)"
        elif curr_buf > 0:
            buffer_condition = "ABSORBING"
            buf_label = f"● Absorbing ({curr_buf:,.0f} active defense)"
        else:
            buffer_condition = "DEPLETED"
            buf_label = "⚠ Depleted (0 weeks runway buffer)"

        # 4. Cash-Flow / Liquidity Pressure Vector
        if timing_gaps and not cf.get("intraday_intelligence", {}).get("is_absorbable_by_buffer", True):
            liquidity_pressure = "ACUTE"
            liq_label = "⚠ Acute Deficit (Timing gap exceeds buffer cushion)"
        elif len(timing_gaps) > 0:
            liquidity_pressure = "MODERATE"
            liq_label = "● Moderate (Buffer absorbable intraday gap)"
        elif curr_inc < burn and curr_inc > 0:
            liquidity_pressure = "ELEVATED"
            liq_label = "● Elevated (Burn exceeds current cycle income)"
        else:
            liquidity_pressure = "LOW"
            liq_label = "● Low (Checking clearance safely above floor)"

        # 5. Composite Overall Outlook
        if liquidity_pressure == "ACUTE" or buffer_condition == "DEPLETED":
            overall = "HIGH_PRESSURE" if curr_buf > 0 else "CRITICAL"
        elif len(timing_gaps) > 0 or obligation_pressure == "ELEVATED":
            overall = "STABLE_WITH_ATTENTION"
        elif income_outlook == "WEAKENING":
            overall = "PRESSURED"
        elif income_outlook == "IMPROVING" and buffer_condition in ("BUILDING", "HEALTHY"):
            overall = "POSITIVE"
        else:
            overall = "STABLE"

        # 6. Main Driver Synthesis
        if len(timing_gaps) > 0:
            first_gap = timing_gaps[0]
            desc = first_gap.get("description", "Scheduled commitment")
            amt = float(first_gap.get("intraday_gap_amount", first_gap.get("amount", 0.0)))
            main_driver = f"Upcoming commitment '{desc}' creates a temporary intraday gap before evening payout clears."
        elif income_outlook == "WEAKENING":
            main_driver = f"Weekly inflow dropped {abs(drift_pct):.0f}% below baseline, activating defensive buffer smoothing."
        elif income_outlook == "IMPROVING":
            main_driver = f"Surplus earnings (+{drift_pct:.1f}% above baseline) provide strong capacity to build runway buffer."
        elif buffer_condition == "HEALTHY":
            main_driver = "Smart Buffer target is 100% achieved; surplus can be deployed to secondary financial goals."
        else:
            main_driver = "Inflows and essential fixed burn are balanced within normal variance corridors."

        # 7. Day-by-Day 7-Day Forecast Map
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        daily_forecast = []
        for i, day in enumerate(days):
            # Wed typically platform payout, Thu or Mon typical EMI
            if i == 2: # Wed
                status_d = "Positive"
                note_d = "Weekly platform inflow expected"
                badge_d = "emerald"
            elif i == 3 and len(timing_gaps) > 0: # Thu
                status_d = "High Pressure"
                note_d = "Intraday commitment settlement"
                badge_d = "rose"
            elif i == 4 and len(timing_gaps) > 0: # Fri
                status_d = "Recovery"
                note_d = "Buffer sweeps rebalance floor"
                badge_d = "tertiary"
            elif i == 1 and len(timing_gaps) > 0: # Tue
                status_d = "Attention"
                note_d = "Pre-settlement liquidity check"
                badge_d = "amber"
            else:
                status_d = "Stable"
                note_d = "Operating above protected floor"
                badge_d = "stone"

            daily_forecast.append({
                "day": day,
                "day_index": i,
                "status": status_d,
                "note": note_d,
                "badge_color": badge_d
            })

        meta = cls.OUTLOOK_METRICS.get(overall, cls.OUTLOOK_METRICS["STABLE"])

        return {
            "overall": overall,
            "label": meta["label"],
            "badge_color": meta["badge"],
            "icon": meta["icon"],
            "horizon": horizon,
            "main_driver": main_driver,
            "sub_outlooks": {
                "income": {
                    "status": income_outlook,
                    "label": income_label,
                    "badge": "emerald" if income_outlook in ("IMPROVING", "STABLE") else "amber"
                },
                "liquidity": {
                    "status": liquidity_pressure,
                    "label": liq_label,
                    "badge": "emerald" if liquidity_pressure == "LOW" else ("amber" if liquidity_pressure == "MODERATE" else "rose")
                },
                "buffer": {
                    "status": buffer_condition,
                    "label": buf_label,
                    "badge": "emerald" if buffer_condition in ("HEALTHY", "BUILDING") else "amber"
                },
                "obligations": {
                    "status": obligation_pressure,
                    "label": ob_label,
                    "badge": "emerald" if obligation_pressure == "MINIMAL" else ("amber" if obligation_pressure == "MODERATE" else "rose")
                }
            },
            "daily_forecast": daily_forecast,
            "horizons": {
                "7D": {
                    "outlook": overall,
                    "summary": f"Next 7 Days: {main_driver}"
                },
                "30D": {
                    "outlook": "STABLE" if curr_buf >= burn * 2 else "PRESSURED",
                    "summary": f"30-Day Outlook: Buffer sustains {coverage_weeks:.1f} weeks of fixed burn across platform cycles."
                },
                "90D": {
                    "outlook": "POSITIVE" if curr_buf >= target_buf else "STABLE",
                    "summary": f"90-Day Outlook: Target buffer completion projected within {max(1, int(round((target_buf - curr_buf)/max(1.0, (curr_inc - burn)*0.7))))} weeks."
                }
            },
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
