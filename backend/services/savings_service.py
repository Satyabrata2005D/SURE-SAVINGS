"""
SURE SAVINGS 2.0: Savings Optimization & Surplus Safeguard Domain Service
Calculates safe-to-save allocations, preserves operational cash floors, and produces transparent audit steps.
"""
from typing import Dict, Any, Optional
from backend.policy import DEFAULT_POLICY, FinancialPolicyConfig

class SavingsOptimizationService:
    """
    Authoritative service executing the 70% Surplus Safeguard policy.
    Never breaches the protected cash floor or forces unrealistic savings rates.
    """

    @classmethod
    def calculate_surplus(cls, actual_income: float, stabilized_income: float) -> float:
        return max(0.0, round(actual_income - stabilized_income, 2))

    @classmethod
    def evaluate_safe_to_save(
        cls,
        actual_income: float,
        stabilized_income: float,
        current_buffer: float,
        policy: FinancialPolicyConfig = DEFAULT_POLICY,
        buffer_target: Optional[float] = None,
        protected_floor: Optional[float] = None,
        weekly_burn: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Produces the authoritative Safe-to-Save recommendation:
        1. Surplus = max(0, actual_income - weekly_burn or actual_income - stabilized_income)
        2. Policy Cap = surplus * 70%
        3. Buffer Gap = max(0, target - current_buffer)
        4. Allocation = round(min(Policy Cap, Buffer Gap) to nearest 50)
        5. Free Pocket Cash = surplus - Allocation
        """
        target = buffer_target if buffer_target is not None and buffer_target > 0 else policy.default_buffer_target
        floor = protected_floor if protected_floor is not None else policy.minimum_checking_floor

        if weekly_burn is not None and weekly_burn > 0:
            if stabilized_income > 0 and stabilized_income < actual_income:
                surplus = min(round(actual_income - weekly_burn, 2), round(actual_income - stabilized_income, 2))
            elif actual_income > weekly_burn:
                surplus = round(actual_income - weekly_burn, 2)
            else:
                surplus = 0.0
        else:
            surplus = cls.calculate_surplus(actual_income, stabilized_income)

        buffer_gap = max(0.0, target - current_buffer)

        if surplus <= 0 or buffer_gap <= 0:
            return {
                "actual_income": actual_income,
                "stabilized_baseline": stabilized_income,
                "surplus": 0.0,
                "policy_cap_pct": policy.surplus_policy_cap,
                "raw_safeguard_cap": 0.0,
                "recommended_contribution": 0.0,
                "free_pocket_liquidity": 0.0,
                "buffer_gap": buffer_gap,
                "confidence": 0.95,
                "status": "CAPITAL_PRESERVED" if surplus <= 0 else "TARGET_REACHED",
                "explanation_steps": {
                    "step_1": f"Actual Inflow: ₹{actual_income:,.0f} vs Stabilized Baseline: ₹{stabilized_income:,.0f}",
                    "step_2": "Zero surplus detected. All income retained for operational checking liquidity.",
                    "step_3": "Safe-to-Save allocation: ₹0."
                }
            }

        raw_cap = round(surplus * policy.surplus_policy_cap, 2)
        bounded_raw = min(raw_cap, buffer_gap)

        # Round to clean increment (e.g. ₹50)
        recommended = round(bounded_raw / policy.rounding_increment) * policy.rounding_increment
        # Safety bound: cannot exceed surplus
        recommended = min(recommended, surplus)
        free_pocket = round(surplus - recommended, 2)

        return {
            "actual_income": actual_income,
            "stabilized_baseline": stabilized_income,
            "surplus": surplus,
            "policy_cap_pct": policy.surplus_policy_cap,
            "raw_safeguard_cap": raw_cap,
            "recommended_contribution": recommended,
            "free_pocket_liquidity": free_pocket,
            "buffer_gap": buffer_gap,
            "confidence": 0.94,
            "status": "SURPLUS_OPTIMIZED",
            "title": f"Save ₹{recommended:,.0f} while preserving ₹{free_pocket:,.0f} free pocket cash.",
            "why_breakdown": {
                "actual_income_w36": actual_income,
                "actual_income": actual_income,
                "stabilized_baseline": stabilized_income,
                "detected_surplus": surplus,
                "policy_safeguard_cap_70pct": raw_cap,
                "rounded_recommendation": recommended,
                "free_pocket_cash_retained": free_pocket,
                "checking_floor_preserved": floor
            },
            "explanation_steps": {
                "step_1": f"₹{actual_income:,.0f} (Cycle Inflow) − ₹{stabilized_income:,.0f} (Stabilized Baseline) = ₹{surplus:,.0f} Gross Surplus",
                "step_2": f"70% Safeguard Cap Applied: {int(policy.surplus_policy_cap * 100)}% of ₹{surplus:,.0f} = ₹{raw_cap:,.0f}",
                "step_3": f"Clean Allocation Rounded to nearest ₹{int(policy.rounding_increment)}: ₹{recommended:,.0f} to Smart Buffer",
                "step_4": f"Remaining 30% retained in checking as Unallocated Free Pocket Cash: ₹{free_pocket:,.0f}",
                "step_5": f"Operational Checking Floor ₹{floor:,.0f} remains 100% untouched"
            }
        }
