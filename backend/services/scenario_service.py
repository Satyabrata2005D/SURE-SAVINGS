"""
SURE SAVINGS 7.0: What-If / Stress Testing Engine 2.0
Multi-variable parametric simulation comparing Baseline vs Scenario vs Delta
across Income, Expenses, Cash, Buffer, Runway, Shortfall, Risk, and Resilience.
"""
from typing import Dict, Any, List, Optional
from backend.policy import DEFAULT_POLICY, FinancialPolicyConfig
from backend.services.resilience_service import ResilienceService
from backend.services.risk_service import RiskService

class ScenarioSimulationService:
    """
    Authoritative What-If & Stress Testing Engine 2.0.
    Evaluates multi-variable shocks, delays, and savings strategies with floor preservation.
    """

    PRESET_LIBRARY = [
        {
            "id": "income_shock_20",
            "name": "Moderate Slowdown (-20%)",
            "category": "INCOME_SHOCK",
            "description": "20% drop in weekly gig orders or client billing across platforms.",
            "params": {"income_change_pct": -20.0, "expense_change_pct": 0.0, "duration_weeks": 4}
        },
        {
            "id": "INCOME_DROP_20",
            "name": "Moderate Slowdown (-20%)",
            "category": "INCOME_SHOCK",
            "description": "20% drop in weekly gig orders or client billing across platforms.",
            "params": {"income_change_pct": -20.0, "expense_change_pct": 0.0, "duration_weeks": 4}
        },
        {
            "id": "income_shock_40",
            "name": "Severe Downturn (-40%)",
            "category": "INCOME_SHOCK",
            "description": "40% platform algorithm shift or off-season delivery drought.",
            "params": {"income_change_pct": -40.0, "expense_change_pct": 0.0, "duration_weeks": 8}
        },
        {
            "id": "expense_hike_15",
            "name": "Living Cost Spike (+15%)",
            "category": "EXPENSE_SHOCK",
            "description": "15% surge in room rent, fuel prices, or grocery staples.",
            "params": {"income_change_pct": 0.0, "expense_change_pct": 15.0, "duration_weeks": 8}
        },
        {
            "id": "EXPENSE_HIKE_20",
            "name": "Living Cost Spike (+20%)",
            "category": "EXPENSE_SHOCK",
            "description": "20% surge in room rent, fuel prices, or grocery staples.",
            "params": {"income_change_pct": 0.0, "expense_change_pct": 20.0, "duration_weeks": 12}
        },
        {
            "id": "PAYOUT_DELAY_10D",
            "name": "10-Day Payout Settlement Delay",
            "category": "TIMING_SHOCK",
            "description": "Gig platforms delay weekly clearing by 10 days while obligations remain due.",
            "params": {"income_delay_days": 10, "duration_weeks": 4}
        },
        {
            "id": "EMERGENCY_REPAIR",
            "name": "Sudden ₹10,000 Emergency Outflow",
            "category": "ONE_TIME_SHOCK",
            "description": "Unplanned vehicle engine breakdown or emergency medical co-pay.",
            "params": {"new_obligation_amount": 10000.0, "duration_weeks": 2}
        },
        {
            "id": "COMBINED_STRESS",
            "name": "Combined Platform Stress (-30% Income, +15% Expense)",
            "category": "COMPOUND_SHOCK",
            "description": "Simultaneous drop in gig orders and inflation in fuel/rent.",
            "params": {"income_change_pct": -30.0, "expense_change_pct": 15.0, "duration_weeks": 8}
        }
    ]

    @classmethod
    def get_library(cls) -> List[Dict[str, Any]]:
        """Returns the pre-built scenario catalog."""
        return cls.PRESET_LIBRARY

    @classmethod
    def get_scenario_library(cls) -> List[Dict[str, Any]]:
        """Alias for get_library."""
        return cls.PRESET_LIBRARY

    @classmethod
    def simulate_parametric(
        cls,
        baseline: Dict[str, Any],
        params: Any,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        """
        Executes a comprehensive What-If simulation against the user's authoritative baseline.
        Returns { baseline, scenario, delta, summary, defensive_protocol }.
        """
        # Baseline inputs from digital twin or raw profile
        if isinstance(baseline, dict):
            if "observation" in baseline:
                p = baseline["observation"].get("profile", {})
                base_income = float(p.get("current_income", 0.0))
                base_burn = float(p.get("weekly_burn", 0.0))
                base_cash = float(p.get("liquid_cash", p.get("current_cash", 0.0)))
                base_buffer = float(p.get("current_buffer", 0.0))
                base_floor = float(p.get("protected_floor", 0.0))
                base_resilience = int(p.get("resilience_score", 0))
            elif "income_state" in baseline:
                base_income = float(baseline.get("income_state", {}).get("current_income", 0.0))
                base_burn = float(baseline.get("expense_state", {}).get("essential_burn", 0.0))
                base_cash = float(baseline.get("liquidity_state", {}).get("total_liquid_cash", 0.0))
                base_buffer = float(baseline.get("buffer_state", {}).get("balance", 0.0))
                base_floor = float(baseline.get("liquidity_state", {}).get("protected_floor", 0.0))
                base_resilience = int(baseline.get("resilience_state", {}).get("score", 0))
            else:
                base_income = float(baseline.get("current_income", 0.0))
                base_burn = float(baseline.get("weekly_burn", 0.0))
                base_cash = float(baseline.get("liquid_cash", baseline.get("current_cash", 0.0)))
                base_buffer = float(baseline.get("current_buffer", 0.0))
                base_floor = float(baseline.get("protected_floor", 0.0))
                base_resilience = int(baseline.get("resilience_score", 0))
        else:
            base_income, base_burn, base_cash, base_buffer, base_floor, base_resilience = 0.0, 0.0, 0.0, 0.0, 0.0, 0

        if hasattr(params, "model_dump"):
            p = params.model_dump()
        elif hasattr(params, "dict"):
            p = params.dict()
        elif isinstance(params, dict):
            p = params
        else:
            p = {}

        # Simulation parameter adjustments
        inc_val = p.get("income_delta_pct") if p.get("income_delta_pct") is not None else p.get("income_change_pct", 0.0)
        inc_change_pct = float(inc_val if inc_val is not None else 0.0)

        exp_val = p.get("expense_delta_pct") if p.get("expense_delta_pct") is not None else p.get("expense_change_pct", 0.0)
        exp_change_pct = float(exp_val if exp_val is not None else 0.0)

        delay_val = p.get("delayed_payout_days") if p.get("delayed_payout_days") is not None else p.get("income_delay_days", 0)
        inc_delay_days = int(delay_val if delay_val is not None else 0)

        shock_val = p.get("one_off_shock") if p.get("one_off_shock") is not None else p.get("new_obligation_amount", 0.0)
        new_ob_amt = float(shock_val if shock_val is not None else 0.0)

        extra_save_wk = float(p.get("additional_saving_weekly", 0.0) or 0.0)
        buffer_withdraw = float(p.get("buffer_withdrawal_amount", 0.0) or 0.0)

        dur_val = p.get("simulation_weeks") if p.get("simulation_weeks") is not None else p.get("duration_weeks", 4)
        duration_wks = max(1, int(dur_val if dur_val is not None else 4))

        # 1. Project adjusted income and burn
        sim_income = max(0.0, round(base_income * (1.0 + inc_change_pct / 100.0), 2))
        sim_burn = max(0.0, round(base_burn * (1.0 + exp_change_pct / 100.0), 2))

        # Weekly operating margin
        weekly_margin = sim_income - sim_burn
        weekly_deficit = max(0.0, -weekly_margin)

        # 2. Project buffer balance over duration
        # Extra savings add to buffer; deficits or withdrawals drain buffer
        total_deficit = weekly_deficit * duration_wks
        total_extra_saved = extra_save_wk * duration_wks

        # Delay shock temporarily depresses checking cash
        delay_cash_suppression = (base_income * (inc_delay_days / 7.0)) if inc_delay_days > 0 else 0.0

        # Projected Buffer
        sim_buffer = max(0.0, base_buffer - buffer_withdraw + total_extra_saved - total_deficit)
        buffer_absorbed = max(0.0, base_buffer - sim_buffer)

        # Projected Checking Cash
        sim_cash = max(0.0, base_cash - new_ob_amt - delay_cash_suppression + (weekly_margin * duration_wks if weekly_margin > 0 else 0.0))

        # 3. Runway calculation
        runway_wks = round(sim_buffer / sim_burn, 1) if sim_burn > 0 else (99.0 if sim_buffer > 0 else 0.0)
        base_runway = round(base_buffer / base_burn, 1) if base_burn > 0 else 0.0

        # 4. Floor Breach Analysis
        floor_breached = sim_cash < base_floor
        floor_deficit = max(0.0, base_floor - sim_cash)

        # 5. Score recalculation
        resilience_impact = 0
        if inc_change_pct < 0:
            resilience_impact += int(inc_change_pct / 10.0)
        if exp_change_pct > 0:
            resilience_impact -= int(exp_change_pct / 10.0)
        if buffer_absorbed > 0:
            resilience_impact -= int(min(15, (buffer_absorbed / max(1.0, base_buffer)) * 20))
        if extra_save_wk > 0:
            resilience_impact += int(min(10, (extra_save_wk / 500.0) * 4))
        if floor_breached:
            resilience_impact -= 12

        sim_resilience = max(20, min(99, base_resilience + resilience_impact))
        sim_risk = RiskService.calculate(sim_resilience)

        # Estimated recovery time
        if sim_resilience < base_resilience:
            pts_to_recover = base_resilience - sim_resilience
            recovery_weeks = max(1, int(round(pts_to_recover / 3.0)))
        else:
            recovery_weeks = 0

        # Defensive protocol
        if inc_change_pct <= -50.0 or floor_breached:
            protocol = "Emergency Circuit Breaker: Freeze all non-essential debits, draw from vault buffer to protect checking floor."
        elif inc_change_pct <= -20.0 or exp_change_pct >= 15.0:
            protocol = f"Deficit Smoothing: Draw ₹{weekly_deficit:,.0f}/wk from buffer; suspend voluntary auto-sweeps."
        elif extra_save_wk > 0:
            protocol = f"Aggressive Buffer Accumulation: Locking in ₹{extra_save_wk:,.0f}/wk expands runway by {runway_wks - base_runway:+.1f} weeks."
        else:
            protocol = "Maintain Standard 70% Surplus Protocol while keeping cash floor intact."

        base_risk = RiskService.calculate(base_resilience)["risk_score"]
        base_traj = []
        sim_traj = []
        c_base = base_buffer
        c_sim = max(0.0, base_buffer - new_ob_amt)
        for w in range(duration_wks):
            base_traj.append(round(c_base, 2))
            c_sim = max(0.0, c_sim + extra_save_wk - weekly_deficit)
            sim_traj.append(round(c_sim, 2))

        return {
            "status": "success",
            "duration_weeks": duration_wks,
            "parameters": {
                "income_delta_pct": inc_change_pct,
                "expense_delta_pct": exp_change_pct,
                "duration_weeks": duration_wks
            },
            "baseline": {
                "metrics": {
                    "income": base_income,
                    "burn": base_burn,
                    "checking_cash": base_cash,
                    "buffer": base_buffer,
                    "runway_weeks": base_runway,
                    "resilience": base_resilience,
                    "risk": base_risk
                },
                "income": base_income,
                "weekly_burn": base_burn,
                "checking_cash": base_cash,
                "buffer": base_buffer,
                "runway_weeks": base_runway,
                "resilience_score": base_resilience,
                "risk_score": base_risk,
                "protected_floor": base_floor
            },
            "scenario": {
                "metrics": {
                    "income": sim_income,
                    "burn": sim_burn,
                    "checking_cash": sim_cash,
                    "buffer": sim_buffer,
                    "runway_weeks": runway_wks,
                    "resilience": sim_resilience,
                    "risk": sim_risk["risk_score"]
                },
                "income": sim_income,
                "weekly_burn": sim_burn,
                "checking_cash": sim_cash,
                "buffer": sim_buffer,
                "runway_weeks": runway_wks,
                "resilience_score": sim_resilience,
                "risk_score": sim_risk["risk_score"],
                "risk_tier": sim_risk["tier"],
                "weekly_shortfall": weekly_deficit,
                "total_buffer_absorbed": buffer_absorbed,
                "floor_breached": floor_breached,
                "floor_deficit": floor_deficit,
                "recovery_weeks": recovery_weeks
            },
            "delta": {
                "income": round(sim_income - base_income, 2),
                "weekly_burn": round(sim_burn - base_burn, 2),
                "checking_cash": round(sim_cash - base_cash, 2),
                "buffer": round(sim_buffer - base_buffer, 2),
                "runway_weeks": round(runway_wks - base_runway, 1),
                "resilience_impact": sim_resilience - base_resilience,
                "risk_impact": sim_risk["risk_score"] - base_risk,
                "resilience_score": sim_resilience - base_resilience,
                "risk_score": sim_risk["risk_score"] - base_risk
            },
            "trajectories": {
                "baseline": base_traj,
                "scenario": sim_traj,
                "weeks": [f"Week {i+1}" for i in range(duration_wks)]
            },
            "recommendations": [protocol],
            "defensive_protocol": protocol
        }

    @classmethod
    def simulate_shock(
        cls,
        current_buffer: float,
        current_resilience: int,
        base_income: float = 8400.0,
        weekly_burn: float = DEFAULT_POLICY.default_weekly_burn,
        drop_percentage: float = 0.0,
        contribution_amount: float = 0.0,
        withdrawal_amount: float = 0.0,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        """Preserves legacy signature for existing tests while routing through deterministic engine."""
        income_multiplier = max(0.0, 1.0 - (drop_percentage / 100.0))
        projected_income = round(base_income * income_multiplier, 2)
        net_weekly_operating_margin = projected_income - weekly_burn
        weekly_deficit = max(0.0, -net_weekly_operating_margin)

        net_cash_adjustment = contribution_amount - withdrawal_amount
        simulated_buffer = max(0.0, current_buffer + net_cash_adjustment)
        available_cushion_above_floor = max(0.0, simulated_buffer - policy.minimum_checking_floor)

        if weekly_deficit > 0:
            weeks_until_floor_touch = round(available_cushion_above_floor / weekly_deficit, 1)
            weeks_until_total_drain = round(simulated_buffer / weekly_deficit, 1)
        else:
            weeks_until_floor_touch = 99.0
            weeks_until_total_drain = round(simulated_buffer / weekly_burn, 1) if weekly_burn > 0 else 99.0

        runway_weeks = round(simulated_buffer / weekly_burn, 1) if weekly_burn > 0 else 0.0
        score_delta = round(net_cash_adjustment / 300.0)
        if drop_percentage > 0:
            score_delta -= round(drop_percentage / 15.0)

        new_resilience = max(35, min(99, current_resilience + score_delta))
        new_risk_data = RiskService.calculate(new_resilience)
        floor_intact = simulated_buffer >= policy.minimum_checking_floor
        floor_status = "SAFE • 100% INTACT" if floor_intact else "BREACH RISK"

        if drop_percentage >= 60.0:
            action = "Activate Emergency Circuit Breaker: Pause all auto-sweeps, draw from vault buffer to cover essential EV EMI."
        elif drop_percentage >= 40.0:
            action = "Enable Deficit Smoothing: Draw from buffer, suspend discretionary spends."
        elif drop_percentage >= 20.0:
            action = "Adaptive Pause: Temporarily lower savings target until order volume rebounds."
        else:
            action = f"Maintain Standard 70% Surplus Safeguard: Save ₹{contribution_amount:,.0f}."

        return {
            "drop_percentage": drop_percentage,
            "projected_weekly_income": projected_income,
            "essential_weekly_burn": weekly_burn,
            "net_weekly_margin": net_weekly_operating_margin,
            "weekly_shortfall": weekly_deficit,
            "simulated_buffer": simulated_buffer,
            "available_above_floor": available_cushion_above_floor,
            "runway_weeks": runway_weeks,
            "weeks_until_floor_touch": weeks_until_floor_touch,
            "weeks_until_total_drain": weeks_until_total_drain,
            "resilience_score": new_resilience,
            "resilience_delta": new_resilience - current_resilience,
            "risk_score": new_risk_data["risk_score"],
            "risk_tier": new_risk_data["tier"],
            "protected_floor": policy.minimum_checking_floor,
            "floor_status": floor_status,
            "is_floor_breached": not floor_intact,
            "defensive_action": action,
            "recovery_time_weeks": max(1, int(round(drop_percentage / 15.0)))
        }

    @classmethod
    def generate_comparison_matrix(
        cls,
        current_buffer: float,
        current_resilience: int,
        base_income: float = 8400.0,
        weekly_burn: float = DEFAULT_POLICY.default_weekly_burn,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        """Produces the complete multi-scenario matrix for the Financial Shock Simulator."""
        scenarios = []
        for preset in policy.shock_presets:
            res = cls.simulate_shock(
                current_buffer=current_buffer,
                current_resilience=current_resilience,
                base_income=base_income,
                weekly_burn=weekly_burn,
                drop_percentage=preset.drop_pct,
                policy=policy
            )
            scenarios.append({
                "id": preset.id,
                "label": preset.label,
                "drop_pct": preset.drop_pct,
                "severity": preset.severity,
                "description": preset.description,
                "metrics": res
            })

        return {
            "baseline_buffer": current_buffer,
            "baseline_resilience": current_resilience,
            "baseline_income": base_income,
            "weekly_burn": weekly_burn,
            "scenarios": scenarios
        }
