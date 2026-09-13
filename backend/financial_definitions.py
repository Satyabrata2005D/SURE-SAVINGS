"""
SURE SAVINGS 5.0 / 6.0: Centralized Financial Definitions & Formula Governance
Canonical mathematical definitions, parameter boundaries, data requirements, and explainable logic.
Single source of truth for all domain metrics.
"""
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass(frozen=True)
class FinancialFormulaDefinition:
    name: str
    purpose: str
    inputs: List[str]
    formula: str
    rounding: str
    minimum_data: str
    fallback: str
    version: str = "v5.0"

FINANCIAL_FORMULAS: Dict[str, FinancialFormulaDefinition] = {
    "EXPENSE_WEEKLY_NORMALIZATION": FinancialFormulaDefinition(
        name="Expense Frequency Normalization",
        purpose="Converts multi-frequency recurring outlays (daily, weekly, monthly, annual) into a unified 7-day operational baseline.",
        inputs=["amount", "frequency"],
        formula="daily * 7 | weekly * 1 | biweekly / 2 | monthly / 4.333 | annual / 52",
        rounding="Round to 2 decimal places",
        minimum_data="At least 1 active expense record or 0.0",
        fallback="0.0 (Do not fabricate burn)",
        version="v5.0"
    ),
    "STABILIZED_INCOME": FinancialFormulaDefinition(
        name="Stabilized Income Planning Baseline",
        purpose="Insulates irregular gig and freelance earners against temporary windfall distortion while adjusting dynamically to drift.",
        inputs=["historical_inflows", "policy_median_weight=0.60", "policy_mean_weight=0.40"],
        formula="0.60 * Median(Inflows) + 0.40 * Mean(Inflows)",
        rounding="Round to nearest 100",
        minimum_data=">= 1 inflow record (if 1 record, stabilized = inflow)",
        fallback="0.0 if no income data",
        version="v5.0"
    ),
    "INCOME_VOLATILITY": FinancialFormulaDefinition(
        name="Income Volatility Index (Coefficient of Variation)",
        purpose="Quantifies relative dispersion of income. CV < 0.15 indicates high stability, 0.16-0.35 typical gig variance, > 0.36 high volatility.",
        inputs=["historical_inflows"],
        formula="StandardDeviation(Inflows) / Mean(Inflows)",
        rounding="Round to 2 decimal places",
        minimum_data=">= 2 historical inflow periods",
        fallback="None / INSUFFICIENT_DATA",
        version="v5.0"
    ),
    "INCOME_FORECAST": FinancialFormulaDefinition(
        name="Conservative Probabilistic Income Forecast",
        purpose="Projects next week's expected inflow using lower-tercile volatility damping for safety.",
        inputs=["historical_inflows", "volatility"],
        formula="point = 0.30 * median + 0.70 * percentile40; bounds = point * (1 ± volatility)",
        rounding="Round point to nearest 100, bounds to 2 decimals",
        minimum_data=">= 4 historical inflow periods",
        fallback="None / INSUFFICIENT_DATA",
        version="v5.0"
    ),
    "GROSS_SURPLUS": FinancialFormulaDefinition(
        name="Liquid Operational Surplus",
        purpose="Identifies positive disposable margin available above essential nondiscretionary commitments.",
        inputs=["current_income", "weekly_essential_burn", "stabilized_income"],
        formula="max(0.0, current_income - weekly_essential_burn)",
        rounding="Round to 2 decimal places",
        minimum_data="Income > 0",
        fallback="0.0",
        version="v5.0"
    ),
    "SAFE_TO_SAVE": FinancialFormulaDefinition(
        name="70% Surplus Safeguard Allocation",
        purpose="Calculates safe buffer contribution while protecting primary checking liquidity and preserving 30% free pocket margin.",
        inputs=["surplus", "buffer_gap", "policy_cap=0.70", "rounding_increment=50"],
        formula="min(surplus * 0.70, buffer_gap) rounded to nearest 50; never exceeding surplus",
        rounding="Round to nearest 50",
        minimum_data="Surplus > 0 and Buffer Gap > 0",
        fallback="0.0",
        version="v5.0"
    ),
    "FREE_POCKET_LIQUIDITY": FinancialFormulaDefinition(
        name="Unallocated Free Pocket Liquidity",
        purpose="Surplus retained in operational checking to absorb unexpected transit, fuel, or day-to-day variances.",
        inputs=["surplus", "recommended_contribution"],
        formula="max(0.0, surplus - recommended_contribution)",
        rounding="Round to 2 decimal places",
        minimum_data="Surplus > 0",
        fallback="0.0",
        version="v5.0"
    ),
    "PROTECTED_FLOOR": FinancialFormulaDefinition(
        name="Operational Checking Cash Floor",
        purpose="Hard threshold in checking account that automated savings rules will never breach.",
        inputs=["weekly_essential_burn", "user_defined_floor", "preference"],
        formula="User defined if provided, else max(1000.0, weekly_essential_burn * 0.80)",
        rounding="Round to nearest 100",
        minimum_data="Essential burn data or user input",
        fallback="0.0 for empty workspace",
        version="v5.0"
    ),
    "BUFFER_RUNWAY": FinancialFormulaDefinition(
        name="Buffer Runway Coverage (Weeks)",
        purpose="Estimates how many weeks the user can survive zero-income shock solely on buffer reserve.",
        inputs=["current_buffer", "weekly_essential_burn"],
        formula="current_buffer / weekly_essential_burn if weekly_essential_burn > 0 else 0.0",
        rounding="Round to 1 decimal place",
        minimum_data="Weekly burn > 0",
        fallback="0.0",
        version="v5.0"
    ),
    "RESILIENCE_SCORE": FinancialFormulaDefinition(
        name="4-Pillar Financial Resilience Index (0-100)",
        purpose="Holistic measure of shock absorption capacity across Income Predictability (25%), Buffer Coverage (30%), Expense Health (20%), and Cash Flow Insulation (25%).",
        inputs=["income_stability", "buffer_coverage", "expense_health", "cashflow_health"],
        formula="0.25*Stability + 0.30*Coverage + 0.20*ExpenseHealth + 0.25*CashFlowHealth",
        rounding="Integer 0-100",
        minimum_data="Maturity Level >= 2 (Income + Expenses)",
        fallback="None / INSUFFICIENT_DATA",
        version="v5.0"
    ),
    "RISK_SCORE": FinancialFormulaDefinition(
        name="5-Vector Financial Risk Telemetry (0-100)",
        purpose="Algorithmic early warning score tracking Income Deterioration, Volatility, Expense Pressure, Buffer Depletion, and Cash Flow Timing Gaps.",
        inputs=["resilience_score", "volatility", "burn_ratio", "intraday_gap"],
        formula="Base Risk = (100 - Resilience) * 0.88 + risk vector adjustments",
        rounding="Integer 0-100",
        minimum_data="Maturity Level >= 2",
        fallback="None / DATA_INCOMPLETE",
        version="v5.0"
    ),
}

def get_formula_metadata(name: str) -> Dict[str, Any]:
    f = FINANCIAL_FORMULAS.get(name)
    if not f:
        return {}
    return {
        "name": f.name,
        "purpose": f.purpose,
        "inputs": f.inputs,
        "formula": f.formula,
        "rounding": f.rounding,
        "minimum_data": f.minimum_data,
        "fallback": f.fallback,
        "version": f.version
    }
