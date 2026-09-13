"""
SURE SAVINGS 8.0: Transaction Intelligence, Recurring Detection, Anomaly Detection,
Weekly Financial Briefing, and Multi-Horizon Outlook Service.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict
import statistics

class TransactionIntelligenceService:
    """
    Unified intelligence service for:
    - Recurring payment detection (rent, EMI, subscriptions, utilities)
    - Financial behavior anomaly detection (UNUSUAL_ACTIVITY signals)
    - Weekly Financial Briefing ("Your Week In Money")
    - 7 / 30 / 90-Day Outlook trajectories
    - Financial Stress Test Suite (10 presets)
    """

    @classmethod
    def detect_recurring_patterns(
        cls,
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Groups transactions by merchant/description and detects recurring debit patterns.
        """
        if not transactions or len(transactions) < 3:
            return []

        # Group debits by normalized description/merchant
        merchant_groups = defaultdict(list)
        for tx in transactions:
            amt = float(tx.get("amount", 0.0))
            is_debit = str(tx.get("type", "debit")).lower() == "debit" or amt < 0
            desc = str(tx.get("description", tx.get("merchant", "General Expense"))).strip()
            date_str = str(tx.get("date", tx.get("created_at", "")))
            
            if is_debit and abs(amt) > 0:
                merchant_groups[desc.lower()].append({
                    "description": desc,
                    "amount": abs(amt),
                    "date": date_str,
                    "category": tx.get("category", "Uncategorized")
                })

        recurring = []
        for norm_desc, items in merchant_groups.items():
            if len(items) >= 2: # At least 2 occurrences
                amounts = [it["amount"] for it in items]
                avg_amt = round(statistics.mean(amounts), 2)
                variance = statistics.stdev(amounts) if len(amounts) > 1 else 0.0
                
                # Check category & regularity
                orig_desc = items[0]["description"]
                cat = items[0]["category"]
                
                if any(k in norm_desc for k in ["rent", "lease", "pg", "hostel"]):
                    pattern_type = "HOUSING_RENT"
                    freq = "Monthly"
                elif any(k in norm_desc for k in ["emi", "loan", "hdfc", "bajaj", "finance"]):
                    pattern_type = "DEBT_EMI"
                    freq = "Monthly"
                elif any(k in norm_desc for k in ["wifi", "broadband", "jio", "airtel", "electricity", "bill"]):
                    pattern_type = "UTILITIES"
                    freq = "Monthly"
                elif any(k in norm_desc for k in ["netflix", "prime", "spotify", "subscription"]):
                    pattern_type = "SUBSCRIPTION"
                    freq = "Monthly"
                else:
                    pattern_type = "RECURRING_EXPENSE"
                    freq = "Weekly" if len(items) >= 4 else "Monthly"

                recurring.append({
                    "pattern_type": pattern_type,
                    "description": orig_desc,
                    "category": cat,
                    "frequency": freq,
                    "average_amount": avg_amt,
                    "occurrences_detected": len(items),
                    "amount_consistency": "High" if variance < 100.0 else "Moderate",
                    "status": "CONFIRMED_RECURRING"
                })

        return recurring

    @classmethod
    def detect_anomalies(
        cls,
        transactions: List[Dict[str, Any]],
        current_weekly_burn: float = 4400.0
    ) -> List[Dict[str, Any]]:
        """
        Detects unusual financial transactions using explainable telemetry signals.
        Never accuses fraud; classifies strictly as UNUSUAL_ACTIVITY.
        """
        if not transactions:
            return []

        anomalies = []
        debit_amounts = [
            abs(float(tx.get("amount", 0.0)))
            for tx in transactions
            if str(tx.get("type", "debit")).lower() == "debit" and abs(float(tx.get("amount", 0.0))) > 0
        ]

        if not debit_amounts:
            return []

        avg_debit = statistics.mean(debit_amounts)
        threshold_large = max(current_weekly_burn * 0.75, avg_debit * 3.5, 3000.0)

        for tx in transactions:
            amt = abs(float(tx.get("amount", 0.0)))
            is_debit = str(tx.get("type", "debit")).lower() == "debit" or float(tx.get("amount", 0.0)) < 0
            desc = str(tx.get("description", "Transaction"))
            
            if is_debit and amt >= threshold_large:
                anomalies.append({
                    "id": f"anom_{tx.get('id', 'large')}",
                    "type": "UNUSUAL_ACTIVITY",
                    "subtype": "LARGE_UNUSUAL_AMOUNT",
                    "severity": "WARNING",
                    "description": f"Unusually large outflow of ₹{amt:,.0f} for '{desc}' (exceeds 3.5× your average transaction size).",
                    "transaction_id": tx.get("id"),
                    "amount": amt,
                    "baseline_average": round(avg_debit, 2),
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })

        return anomalies

    @classmethod
    def generate_weekly_briefing(
        cls,
        digital_twin: Dict[str, Any],
        weather: Dict[str, Any],
        resilience_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates 'YOUR WEEK IN MONEY' executive briefing.
        """
        prof = digital_twin.get("observation", {}).get("profile", {}) or digital_twin.get("profile", {})
        curr_inc = float(prof.get("current_income", 0.0))
        stab_inc = float(prof.get("stabilized_income", 0.0))
        burn = float(prof.get("weekly_burn", 0.0))
        curr_buf = float(prof.get("current_buffer", 0.0))
        resilience = int(prof.get("resilience_score", 0))
        risk = int(prof.get("risk_score", 0))
        surplus = float(prof.get("surplus", 0.0))
        save_rec = float(prof.get("recommended_contribution", 0.0))
        drift_pct = float(prof.get("recent_drift_pct", 0.0))

        if curr_inc <= 0 and burn <= 0 and curr_buf <= 0:
            return {
                "title": "Your Week In Money",
                "status": "AWAITING_DATA",
                "summary": "Record your income and expenses to unlock your weekly resilience briefing.",
                "metrics": []
            }

        actions = resilience_plan.get("actions", [])
        top_action = actions[0]["action"] if actions else f"Continue buffer contribution at ₹{save_rec:,.0f}."

        metrics = [
            {
                "label": "Income Movement",
                "value": f"₹{curr_inc:,.0f}",
                "change": f"{drift_pct:+.1f}% vs baseline",
                "badge_color": "emerald" if drift_pct >= 0 else "rose",
                "icon": "📈" if drift_pct >= 0 else "📉"
            },
            {
                "label": "Essential Burn",
                "value": f"₹{burn:,.0f}",
                "change": "Fixed Rent & Commitments",
                "badge_color": "stone",
                "icon": "🏷️"
            },
            {
                "label": "Smart Buffer",
                "value": f"₹{curr_buf:,.0f}",
                "change": f"+₹{save_rec:,.0f} recommended sweep",
                "badge_color": "emerald",
                "icon": "🛡️"
            },
            {
                "label": "Resilience Score",
                "value": f"{resilience}/100",
                "change": f"Risk: {risk}/100 ({weather.get('label', 'Stable')})",
                "badge_color": "tertiary",
                "icon": "⭐"
            }
        ]

        return {
            "title": "Your Week In Money",
            "status": "ACTIVE",
            "headline": f"Financial Weather: {weather.get('label', 'Stable with Attention')}",
            "main_driver": weather.get("main_driver", "Operations balanced inside safe corridor."),
            "metrics": metrics,
            "top_action": top_action,
            "next_week_outlook": weather.get("overall", "STABLE"),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    def generate_multi_horizon_outlook(
        cls,
        digital_twin: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Produces 7D, 30D, and 90D trajectory forecasts.
        """
        prof = digital_twin.get("observation", {}).get("profile", {}) or digital_twin.get("profile", {})
        curr_inc = float(prof.get("current_income", 0.0))
        burn = float(prof.get("weekly_burn", 0.0))
        curr_buf = float(prof.get("current_buffer", 0.0))
        target_buf = float(prof.get("buffer_target", 15000.0))
        save_rec = float(prof.get("recommended_contribution", 0.0))
        resilience = int(prof.get("resilience_score", 0))

        if curr_inc <= 0 and burn <= 0 and curr_buf <= 0:
            return {
                "status": "INSUFFICIENT_DATA",
                "horizons": {
                    "7D": {"available": False, "message": "Awaiting baseline data."},
                    "30D": {"available": False, "message": "Awaiting baseline data."},
                    "90D": {"available": False, "message": "Awaiting baseline data."}
                }
            }

        # 7-Day trajectory (1 cycle)
        buf_7d = curr_buf + save_rec
        res_7d = min(95, resilience + 2)

        # 30-Day trajectory (~4.3 weeks)
        buf_30d = curr_buf + (save_rec * 4.3)
        res_30d = min(95, resilience + 7)

        # 90-Day trajectory (~12.8 weeks)
        buf_90d = min(target_buf * 1.2, curr_buf + (save_rec * 12.8))
        res_90d = min(95, resilience + 14)

        return {
            "status": "ACTIVE",
            "horizons": {
                "7D": {
                    "available": True,
                    "horizon": "7-Day Immediate",
                    "projected_buffer": round(buf_7d, 2),
                    "runway_weeks": round(buf_7d / burn, 1) if burn > 0 else 1.0,
                    "projected_resilience": res_7d,
                    "outlook": "STABLE_WITH_ATTENTION",
                    "summary": "Preserves checking liquidity while absorbing upcoming commitments."
                },
                "30D": {
                    "available": True,
                    "horizon": "30-Day Intermediate",
                    "projected_buffer": round(buf_30d, 2),
                    "runway_weeks": round(buf_30d / burn, 1) if burn > 0 else 2.5,
                    "projected_resilience": res_30d,
                    "outlook": "BUILDING",
                    "summary": f"Advances emergency runway toward {round(buf_30d / burn, 1) if burn > 0 else 2.5} weeks."
                },
                "90D": {
                    "available": True,
                    "horizon": "90-Day Strategic",
                    "projected_buffer": round(buf_90d, 2),
                    "runway_weeks": round(buf_90d / burn, 1) if burn > 0 else 3.8,
                    "projected_resilience": res_90d,
                    "outlook": "HEALTHY",
                    "summary": "Completes core 3.5+ week runway buffer milestone."
                }
            }
        }

    @classmethod
    def run_stress_test_suite(
        cls,
        digital_twin: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes standard 10-scenario financial stress-test library against a digital twin.
        """
        p = digital_twin.get("observation", {}).get("profile", {}) or digital_twin.get("profile", {}) or digital_twin
        curr_buf = float(p.get("current_buffer", 6800.0 if p.get("is_demo_user") else 0.0))
        resilience = int(p.get("resilience_score", 74 if p.get("is_demo_user") else 50))
        curr_inc = float(p.get("current_income", 8400.0 if p.get("is_demo_user") else 0.0))
        burn = float(p.get("weekly_burn", 4400.0 if p.get("is_demo_user") else 0.0))
        floor = float(p.get("protected_floor", 3500.0 if p.get("is_demo_user") else 0.0))

        results = cls.get_stress_test_suite(
            current_buffer=curr_buf,
            current_resilience=resilience,
            base_income=curr_inc,
            weekly_burn=burn,
            floor=floor
        )
        return {
            "status": "EVALUATED",
            "stress_presets_count": len(results),
            "results": results
        }

    @classmethod
    def get_stress_test_suite(
        cls,
        current_buffer: float = 6800.0,
        current_resilience: int = 74,
        base_income: float = 8400.0,
        weekly_burn: float = 4400.0,
        floor: float = 3500.0
    ) -> List[Dict[str, Any]]:
        """
        Executes standard 10-scenario financial stress-test library.
        """
        presets = [
            {"id": "shock_inc_10", "name": "Income −10% (Mild Drift)", "drop_pct": 10.0, "exp_pct": 0.0, "shock": 0.0},
            {"id": "shock_inc_20", "name": "Income −20% (Seasonal Dip)", "drop_pct": 20.0, "exp_pct": 0.0, "shock": 0.0},
            {"id": "shock_inc_40", "name": "Income −40% (Platform Downtime)", "drop_pct": 40.0, "exp_pct": 0.0, "shock": 0.0},
            {"id": "shock_inc_60", "name": "Income −60% (Severe Drought)", "drop_pct": 60.0, "exp_pct": 0.0, "shock": 0.0},
            {"id": "shock_delay", "name": "Income Delayed by 7 Days", "drop_pct": 0.0, "exp_pct": 0.0, "shock": 0.0, "is_delay": True},
            {"id": "shock_exp_10", "name": "Expenses +10% (Inflation / Fuel)", "drop_pct": 0.0, "exp_pct": 10.0, "shock": 0.0},
            {"id": "shock_exp_20", "name": "Expenses +20% (Rent / Vehicle Spike)", "drop_pct": 0.0, "exp_pct": 20.0, "shock": 0.0},
            {"id": "shock_unexp", "name": "Unexpected Emergency Expense (₹3,000)", "drop_pct": 0.0, "exp_pct": 0.0, "shock": 3000.0},
            {"id": "shock_obligation", "name": "New EMI Added (₹2,500/wk)", "drop_pct": 0.0, "exp_pct": 56.8, "shock": 0.0},
            {"id": "shock_combined", "name": "Combined Shock: Income −30% + Expense +15%", "drop_pct": 30.0, "exp_pct": 15.0, "shock": 1500.0}
        ]

        results = []
        for p in presets:
            drop = p.get("drop_pct", 0.0)
            exp_inc = p.get("exp_pct", 0.0)
            shock = p.get("shock", 0.0)

            sim_inc = round(base_income * (1.0 - (drop / 100.0)), 2)
            sim_burn = round(weekly_burn * (1.0 + (exp_inc / 100.0)), 2)
            deficit = max(0.0, sim_burn - sim_inc)
            
            # 6-week survival projection
            net_buf = max(0.0, current_buffer - shock - (deficit * 6))
            runway = round(net_buf / sim_burn, 1) if sim_burn > 0 else 0.0
            floor_breached = net_buf < floor
            
            score_delta = -int(round((drop / 10.0) + (exp_inc / 10.0) + (shock / 1000.0)))
            sim_res = max(25, min(95, current_resilience + score_delta))

            results.append({
                "id": p["id"],
                "name": p["name"],
                "projected_income": sim_inc,
                "projected_burn": sim_burn,
                "weekly_deficit": deficit,
                "ending_buffer_6w": net_buf,
                "runway_weeks": runway,
                "floor_breached": floor_breached,
                "resilience_score": sim_res,
                "resilience_delta": sim_res - current_resilience,
                "survival_horizon_weeks": round(current_buffer / deficit, 1) if deficit > 0 else 99.0,
                "defensive_status": "CRITICAL" if floor_breached else ("TIGHT" if deficit > 0 else "ABSORBABLE")
            })

        return results
