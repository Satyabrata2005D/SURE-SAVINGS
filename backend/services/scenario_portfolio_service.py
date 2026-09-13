"""
SURE SAVINGS 8.0: Scenario Portfolio & Counterfactual Lab Service
Evaluates 1 to 5 simultaneous financial counterfactual strategies, computes
multi-variable comparison matrices, and ranks strategies by holistic safety and resilience.
"""
from typing import Dict, Any, List, Optional
from backend.services.scenario_service import ScenarioSimulationService
from backend.services.risk_service import RiskService

class ScenarioPortfolioService:
    """
    Evaluates, compares, and ranks multi-scenario counterfactual portfolios.
    Ranks strategies holistically by Safety Index, Liquidity Preservation,
    and Resilience Improvement rather than naive maximum savings.
    """

    @classmethod
    def evaluate_portfolio(
        cls,
        baseline: Dict[str, Any],
        scenarios: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs and compares multiple counterfactual scenarios against baseline.
        If scenarios is None or empty, generates 4 canonical strategies:
        - Strategy A: Income Shock (-20%)
        - Strategy B: Income Shock (-20%) + Active Savings (₹1,000/wk)
        - Strategy C: Income Shock (-20%) + Discretionary Spend Cut (₹800/wk)
        - Strategy D: Income Shock (-20%) + Emergency Buffer Drawdown (₹2,000)
        """
        p = baseline.get("observation", {}).get("profile", {}) or baseline.get("profile", {}) or baseline
        curr_inc = float(p.get("current_income", 0.0))
        burn = float(p.get("weekly_burn", 0.0))
        curr_buf = float(p.get("current_buffer", 0.0))
        resilience = int(p.get("resilience_score", 0))
        floor = float(p.get("protected_floor", 3500.0))
        target_buf = float(p.get("buffer_target", 15000.0))

        if curr_inc <= 0 and burn <= 0 and curr_buf <= 0:
            return {
                "status": "INSUFFICIENT_DATA",
                "message": "Enter your baseline financial data to run scenario comparisons.",
                "strategies": [],
                "comparison_matrix": {},
                "recommended_strategy": None
            }

        # Default 4 strategies if none supplied
        if not scenarios:
            scenarios = [
                {
                    "id": "scenario_a",
                    "name": "Scenario A",
                    "label": "Income −20% (Unmitigated)",
                    "income_delta_pct": -20.0,
                    "expense_delta_pct": 0.0,
                    "weekly_savings_override": 0.0,
                    "one_off_shock": 0.0,
                    "description": "Standard seasonal dip in gig orders without adaptive response."
                },
                {
                    "id": "scenario_b",
                    "name": "Scenario B",
                    "label": "Income −20% + Save ₹1,000/wk",
                    "income_delta_pct": -20.0,
                    "expense_delta_pct": 0.0,
                    "weekly_savings_override": 1000.0,
                    "one_off_shock": 0.0,
                    "description": "Adaptive income shock mitigated by disciplined buffer contributions."
                },
                {
                    "id": "scenario_c",
                    "name": "Scenario C",
                    "label": "Income −20% + Cut Discretionary ₹800/wk",
                    "income_delta_pct": -20.0,
                    "expense_delta_pct": -18.0, # ~₹800 cut on 4400 burn
                    "weekly_savings_override": 0.0,
                    "one_off_shock": 0.0,
                    "description": "Expense tightening protocol to preserve checking runway."
                },
                {
                    "id": "scenario_d",
                    "name": "Scenario D",
                    "label": "Income −20% + Buffer Drawdown (₹2,000)",
                    "income_delta_pct": -20.0,
                    "expense_delta_pct": 0.0,
                    "weekly_savings_override": 0.0,
                    "one_off_shock": 2000.0,
                    "description": "Buffer deployed defensively to bridge living expenses during shock."
                }
            ]

        results = []
        for sc in scenarios[:5]: # Max 5 scenarios
            inc_delta = float(sc.get("income_delta_pct", 0.0))
            exp_delta = float(sc.get("expense_delta_pct", 0.0))
            sav_override = float(sc.get("weekly_savings_override", 0.0))
            shock = float(sc.get("one_off_shock", 0.0))

            proj_inc = max(0.0, round(curr_inc * (1.0 + (inc_delta / 100.0)), 2))
            proj_burn = max(0.0, round(burn * (1.0 + (exp_delta / 100.0)), 2))
            net_operating = proj_inc - proj_burn

            # 6-week horizon simulation
            sim_weeks = 6
            sim_buffer = curr_buf - shock + (sav_override * sim_weeks)
            weekly_deficit = max(0.0, -net_operating)
            sim_buffer = max(0.0, sim_buffer - (weekly_deficit * sim_weeks))

            runway = round(sim_buffer / proj_burn, 1) if proj_burn > 0 else 0.0
            
            # Score delta calculation
            score_delta = round((sim_buffer - curr_buf) / 300.0)
            if inc_delta < 0:
                score_delta += round(inc_delta / 15.0)
            if exp_delta < 0:
                score_delta += round(abs(exp_delta) / 10.0)
            
            sim_resilience = max(25, min(95, resilience + score_delta))
            sim_risk = RiskService.calculate(sim_resilience)
            shortfall = round(weekly_deficit * sim_weeks, 2)
            recovery_weeks = max(1, int(round((target_buf - sim_buffer) / max(500.0, (curr_inc - burn) * 0.7)))) if sim_buffer < target_buf else 0

            # Safety Score Algorithm:
            # 40% Resilience + 30% Runway + 20% Liquidity Clearance - 10% Risk
            clearance_above_floor = max(0.0, sim_buffer - floor)
            floor_intact = sim_buffer >= floor
            safety_score = round(
                (sim_resilience * 0.40) +
                (min(100.0, runway * 20.0) * 0.30) +
                (min(100.0, (clearance_above_floor / max(1.0, floor)) * 50.0) * 0.20) -
                (sim_risk["risk_score"] * 0.10)
            )
            if not floor_intact:
                safety_score = max(10, safety_score - 25)

            results.append({
                "id": sc.get("id"),
                "name": sc.get("name"),
                "label": sc.get("label"),
                "description": sc.get("description"),
                "ending_buffer": round(sim_buffer, 2),
                "runway_weeks": runway,
                "risk_tier": sim_risk["tier"],
                "risk_score": sim_risk["risk_score"],
                "resilience_score": sim_resilience,
                "resilience_delta": sim_resilience - resilience,
                "weekly_shortfall": shortfall,
                "recovery_weeks": recovery_weeks,
                "floor_status": "INTACT" if floor_intact else "BREACHED",
                "safety_score": safety_score
            })

        # Rank strategies by holistic safety score
        ranked = sorted(results, key=lambda r: r["safety_score"], reverse=True)
        for idx, r in enumerate(ranked):
            r["rank"] = idx + 1
        recommended = ranked[0] if ranked else None

        # Build clean comparison matrix columns
        matrix = {
            "metrics": [
                "Ending Buffer",
                "Runway",
                "Risk Tier",
                "Resilience",
                "Est. Recovery",
                "Floor Status"
            ],
            "columns": [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "label": r["label"],
                    "is_recommended": (recommended and r["id"] == recommended["id"]),
                    "ending_buffer": f"₹{r['ending_buffer']:,.0f}",
                    "runway": f"{r['runway_weeks']}w",
                    "risk": r["risk_tier"],
                    "resilience": r["resilience_score"],
                    "recovery": f"{r['recovery_weeks']}w" if r['recovery_weeks'] > 0 else "Ready",
                    "floor_status": r["floor_status"]
                }
                for r in results
            ]
        }

        why_rec = ""
        if recommended:
            why_rec = (
                f"{recommended['name']} achieves the highest resilience improvement "
                f"({recommended['resilience_score']}/100, {recommended['resilience_delta']:+d} pts) "
                f"while sustaining {recommended['runway_weeks']} weeks of runway with acceptable checking liquidity impact."
            )

        return {
            "status": "COMPUTED",
            "strategies_count": len(ranked),
            "scenario_count": len(ranked),
            "strategies": ranked,
            "results": ranked,
            "comparison_matrix": matrix,
            "recommended_strategy": {
                "id": recommended["id"] if recommended else None,
                "name": recommended["name"] if recommended else None,
                "label": recommended["label"] if recommended else None,
                "resilience_score": recommended["resilience_score"] if recommended else None,
                "runway_weeks": recommended["runway_weeks"] if recommended else None,
                "why": why_rec
            },
            "best_safety": max(results, key=lambda r: r["safety_score"]) if results else None,
            "safest_scenario": max(results, key=lambda r: r["safety_score"]) if results else None,
            "highest_risk_scenario": min(results, key=lambda r: r["safety_score"]) if results else None,
            "best_resilience": max(results, key=lambda r: r["resilience_score"]) if results else None,
            "best_runway": max(results, key=lambda r: r["runway_weeks"]) if results else None,
            "best_recovery": min(results, key=lambda r: r["recovery_weeks"]) if results else None
        }
