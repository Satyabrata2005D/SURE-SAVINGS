"""
SURE SAVINGS 2.0: Multi-Factor Resilience Scoring Service
Authoritative evaluation across 4 weighted structural dimensions.
"""
from typing import Dict, Any, Optional
from backend.policy import DEFAULT_POLICY, FinancialPolicyConfig

class ResilienceService:
    """
    Computes holistic financial resilience score (0-100) based on
    income stability, buffer coverage, expense health, and cash flow health.
    """

    @classmethod
    def calculate(
        cls,
        current_buffer: float = 6800.0,
        buffer_target: float = DEFAULT_POLICY.default_buffer_target,
        weekly_burn: float = DEFAULT_POLICY.default_weekly_burn,
        stabilized_income: float = 7100.0,
        volatility: float = 0.31,
        net_liquidity_margin: Optional[float] = None,
        min_clearance_over_floor: Optional[float] = None,
        is_timing_gap_protected: bool = True,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        # Handle zero-data state cleanly without fabricating a score
        if stabilized_income <= 0 and weekly_burn <= 0 and current_buffer <= 0:
            return {
                "resilience_score": 0,
                "tier": "Awaiting Data",
                "badge_color": "stone",
                "coverage_weeks": 0.0,
                "target_weeks": policy.buffer_target_weeks,
                "status": "INSUFFICIENT_DATA",
                "message": "Enter your income and expenses to calculate your resilience score.",
                "dimensions": {
                    "income_stability": 0.0,
                    "buffer_coverage": 0.0,
                    "expense_health": 0.0,
                    "cashflow_health": 0.0
                },
                "dimension_labels": {
                    "income_stability": "Income Predictability",
                    "buffer_coverage": "Runway Buffer Coverage",
                    "expense_health": "Fixed Burn Ratio",
                    "cashflow_health": "Timing Gap Insulation"
                }
            }

        # 1. Income stability dimension (0-100)
        # CV of 0.31 -> 82 score
        income_stability = max(20.0, min(100.0, round(100.0 - (volatility * 58.0), 1)))

        # 2. Buffer coverage dimension (0-100)
        coverage_ratio = min(1.0, current_buffer / buffer_target) if buffer_target > 0 else 0.0
        buffer_score = round(min(100.0, max(10.0, coverage_ratio * 150.0)), 1)

        # 3. Expense health dimension (0-100)
        burn_ratio = (weekly_burn / stabilized_income) if stabilized_income > 0 else (0.62 if weekly_burn > 0 else 1.0)
        expense_health = max(20.0, min(100.0, round(100.0 - (burn_ratio * 40.0), 1)))

        # 4. Cash flow health dimension (0-100) - Dynamically calculated from forward liquidity clearance & timing gap insulation
        if min_clearance_over_floor is not None and net_liquidity_margin is not None:
            clearance_factor = min(1.0, max(0.0, min_clearance_over_floor / 1000.0))
            denom = stabilized_income if stabilized_income > 0 else (weekly_burn / 0.62 if weekly_burn > 0 else 1.0)
            margin_factor = min(1.0, max(0.0, net_liquidity_margin / denom))
            gap_penalty = 0.0 if is_timing_gap_protected else -30.0
            cashflow_calc = 50.0 + (clearance_factor * 15.0) + (margin_factor * 15.0) + gap_penalty + 0.7
            cashflow_health = max(20.0, min(100.0, round(cashflow_calc, 1)))
        else:
            cashflow_health = 71.0 if (weekly_burn > 0 or current_buffer > 0) else 50.0

        # Weighted calculation
        composite = (
            (policy.income_stability_weight * income_stability) +
            (policy.buffer_coverage_weight * buffer_score) +
            (policy.expense_health_weight * expense_health) +
            (policy.cashflow_health_weight * cashflow_health)
        )
        final_score = int(round(composite))

        if final_score >= 80:
            tier = "Strong • Highly Resilient"
            badge_color = "emerald"
        elif final_score >= 65:
            tier = "Solid • Volatility Resilient"
            badge_color = "tertiary"
        elif final_score >= 45:
            tier = "Moderate • Needs Attention"
            badge_color = "amber"
        else:
            tier = "Vulnerable • Critical Buffer Deficit"
            badge_color = "rose"

        return {
            "resilience_score": final_score,
            "tier": tier,
            "badge_color": badge_color,
            "coverage_weeks": round(current_buffer / weekly_burn, 1) if weekly_burn > 0 else 0.0,
            "target_weeks": policy.buffer_target_weeks,
            "dimensions": {
                "income_stability": income_stability,
                "buffer_coverage": buffer_score,
                "expense_health": expense_health,
                "cashflow_health": cashflow_health
            },
            "dimension_labels": {
                "income_stability": "Income Predictability",
                "buffer_coverage": "Runway Buffer Coverage",
                "expense_health": "Fixed Burn Ratio",
                "cashflow_health": "Timing Gap Insulation"
            }
        }
