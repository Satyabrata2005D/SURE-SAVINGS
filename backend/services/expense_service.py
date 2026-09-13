"""
SURE SAVINGS 2.0: Expense Analytics Domain Service
Analyzes structural essential burn (rent, mobility EMI, utilities) versus variable outlays.
"""
from typing import List, Dict, Any, Optional
from backend.policy import DEFAULT_POLICY, FinancialPolicyConfig

def _get_val(o: Any, attr: str, default: Any = None) -> Any:
    if hasattr(o, attr):
        val = getattr(o, attr)
        return val if val is not None else default
    if isinstance(o, dict):
        return o.get(attr, default)
    return default

class ExpenseAnalyticsService:
    """
    Evaluates obligations, expense items, and ledger debits to categorize expenses into
    nondiscretionary survival baseline vs discretionary consumption.
    """

    @staticmethod
    def normalize_frequency(amount: float, frequency: str) -> float:
        freq = (frequency or "monthly").lower().strip()
        if freq == "daily":
            return round(amount * 7.0, 2)
        elif freq == "weekly":
            return round(amount, 2)
        elif freq in ["biweekly", "bi-weekly", "fortnightly"]:
            return round(amount / 2.0, 2)
        elif freq in ["monthly", "month"]:
            return round(amount / (52.0 / 12.0), 2)
        elif freq in ["annual", "yearly", "year"]:
            return round(amount / 52.0, 2)
        return round(amount / 4.333, 2)

    @classmethod
    def calculate_essential_burn(
        cls,
        obligations: List[Any],
        default_burn: Optional[float] = None,
        expense_items: Optional[List[Any]] = None
    ) -> float:
        """
        Calculates total essential outflow requirement per week from obligations and/or expense items.
        If user has neither, returns 0.0 (or default_burn if explicitly specified).
        """
        burn = 0.0
        if expense_items:
            for item in expense_items:
                is_ess = _get_val(item, "is_essential", True)
                is_act = _get_val(item, "is_active", True)
                if is_ess and is_act:
                    amt = _get_val(item, "amount", 0.0)
                    freq = _get_val(item, "frequency", "monthly")
                    burn += cls.normalize_frequency(amt, freq)

        if obligations:
            for o in obligations:
                is_ess = _get_val(o, "is_essential", True) if hasattr(o, "is_essential") else _get_val(o, "essential", True)
                o_type = _get_val(o, "type", "debit")
                if is_ess and o_type == "debit":
                    burn += _get_val(o, "amount", 0.0)

        if burn > 0:
            return round(burn, 2)
        return default_burn if default_burn is not None else 0.0

    @classmethod
    def calculate_discretionary_spend(
        cls,
        expense_items: Optional[List[Any]] = None
    ) -> float:
        """
        Calculates weekly discretionary consumption from non-essential expense items.
        """
        spend = 0.0
        if expense_items:
            for item in expense_items:
                is_ess = _get_val(item, "is_essential", True)
                is_act = _get_val(item, "is_active", True)
                if not is_ess and is_act:
                    amt = _get_val(item, "amount", 0.0)
                    freq = _get_val(item, "frequency", "monthly")
                    spend += cls.normalize_frequency(amt, freq)
        return round(spend, 2)

    @classmethod
    def analyze_expenses(
        cls,
        obligations: List[Any],
        stabilized_income: float,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        weekly_burn = cls.calculate_essential_burn(obligations, policy.default_weekly_burn)
        burn_ratio = round((weekly_burn / stabilized_income), 2) if stabilized_income > 0 else 1.0

        # Health score: lower burn ratio is better (e.g. 4400 / 7100 = 0.62 -> ~75 score)
        health_score = max(20, min(100, int(round(100 - (burn_ratio * 40)))))

        return {
            "weekly_essential_burn": weekly_burn,
            "burn_ratio": burn_ratio,
            "burn_ratio_pct": f"{int(burn_ratio * 100)}%",
            "expense_health_score": health_score,
            "status": "HEALTHY • SUSTAINABLE" if burn_ratio < 0.70 else "TIGHT • ELEVATED OVERHEAD",
            "breakdown": [
                {"category": "Mobility & Transit", "share": "45%", "essential": True},
                {"category": "Housing & Utilities", "share": "40%", "essential": True},
                {"category": "Subsistence & Charging", "share": "15%", "essential": True}
            ]
        }
