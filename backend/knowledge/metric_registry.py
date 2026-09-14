"""
SURE SAVINGS: Financial Metric Registry (backend/knowledge/metric_registry.py)
Authoritative registry of all financial resilience metrics, formulas, concepts, and safety invariants.

Security Invariants:
- Bank Balance != Safe-to-Save. Gross bank balance must NEVER be confused with surplus.
- Protected Cash Floor is strictly ring-fenced; engine allocations always stop above it.
- If data is insufficient, display 'INSUFFICIENT_DATA' or 'Setup Required' instead of fabricated zeros.
"""

from typing import Dict, Any, Optional

METRIC_REGISTRY: Dict[str, Dict[str, Any]] = {
    "SAFE_TO_SAVE": {
        "metric_id": "SAFE_TO_SAVE",
        "display_name": "Safe-to-Save Recommendation",
        "page": "index.html",
        "definition": "The exact surplus amount you can safely allocate into emergency savings this cycle without risking overdrafts, missing bill payments, or breaching your cash floor.",
        "purpose": "Protects you from over-saving on bad weeks and automates emergency buffer growth on good weeks.",
        "calculation_concept": (
            "Derived dynamically as: max(0, min(Inflow - Stabilized Baseline, Surplus × 0.70)). "
            "Automatically clamped to ₹0 if checking liquidity approaches the Protected Cash Floor "
            "or if upcoming calendar obligations exceed current liquid cash."
        ),
        "data_requirements": "Weekly earnings, essential burn rate, and protected floor.",
        "why_important": "Traditional apps force fixed monthly savings that cause overdrafts when income dips. Safe-to-Save adjusts to your real-world cash volatility.",
        "invariant": "Bank Balance ≠ Safe-to-Save. A ₹25,000 bank balance does NOT mean ₹25,000 is safe to save if ₹18,000 is committed to rent, EMIs, and your cash floor.",
        "user_explanation": "Safe-to-Save is calculated after protecting your bills and cash floor. If it shows ₹0, it means all your current cash is actively protecting upcoming commitments or your floor."
    },
    "PROTECTED_FLOOR": {
        "metric_id": "PROTECTED_FLOOR",
        "display_name": "Protected Cash Floor",
        "page": "index.html",
        "definition": "The non-negotiable minimum balance that must remain in your primary checking account at all times for immediate operational needs.",
        "purpose": "Shields you against everyday liquidity failure, transit costs, daily meals, and unexpected urgent outlays.",
        "calculation_concept": "Typically configured as 3 to 5 days of immediate operating expenses (e.g. ₹3,500 for fuel, daily food, and transit).",
        "data_requirements": "Configured in Financial Setup Wizard or Quick Start.",
        "why_important": "Acts as an impenetrable shield. The engine will NEVER recommend saving or locking funds that would breach this floor.",
        "invariant": "The floor is strictly ring-fenced in checking; savings sweeps always stop above this baseline.",
        "user_explanation": "Your Protected Floor is your daily operating cushion. The engine treats this money as untouchable."
    },
    "SMART_BUFFER": {
        "metric_id": "SMART_BUFFER",
        "display_name": "Smart Buffer (Emergency Reserve)",
        "page": "index.html",
        "definition": "Capitalized emergency reserve vault ring-fenced specifically to absorb volatile gig income drops, illness, or platform downtime.",
        "purpose": "Transforms variable-income earners into resilient operators who never need predatory payday loans.",
        "calculation_concept": "Cumulative sum of approved Safe-to-Save sweeps minus emergency withdrawals. Target is 4 to 8 weeks of essential burn.",
        "data_requirements": "Essential weekly burn rate and approved savings sweeps.",
        "why_important": "Provides runway. If platform earnings drop by 50% for 3 weeks, your buffer absorbs the loss without defaulting on bills.",
        "invariant": "Funds in the buffer are tracked deterministically and require manual confirmation to sweep or withdraw.",
        "user_explanation": "Your Smart Buffer is your financial safety net. It grows when you approve surplus savings and protects you when earnings slump."
    },
    "RESILIENCE_SCORE": {
        "metric_id": "RESILIENCE_SCORE",
        "display_name": "Financial Resilience Score (0 to 100)",
        "page": "index.html",
        "definition": "A comprehensive mathematical index quantifying your capacity to withstand income volatility and economic shocks.",
        "purpose": "Provides a single authoritative benchmark for financial health and recovery readiness.",
        "calculation_concept": (
            "Multi-factor weighted index: "
            "35% Buffer Runway Coverage + 25% Income Volatility Dampening + "
            "20% Cash Flow Health & Obligation Coverage + 20% Savings Adherence."
        ),
        "data_requirements": "Complete Financial Setup (income, burn, buffer, floor).",
        "why_important": "A score above 70 indicates strong resilience; above 85 indicates fortress resilience capable of surviving 8+ weeks of shock.",
        "invariant": "Requires setup data. When data is insufficient, displays 'Setup Required' rather than a fabricated or guessed number.",
        "user_explanation": "Your Resilience Score reflects your total financial defense across buffer runway, income stability, and bill protection."
    },
    "WEEKLY_BURN": {
        "metric_id": "WEEKLY_BURN",
        "display_name": "Weekly Essential Burn Rate",
        "page": "index.html",
        "definition": "The non-discretionary weekly cash required to survive: rent, food, transport/fuel, utility bills, and loan EMIs.",
        "purpose": "Defines your survival baseline and sets the scale for buffer targets and runway calculations.",
        "calculation_concept": "Sum of monthly essential obligations divided by 4.33, plus verified weekly operating transit/food expenses.",
        "data_requirements": "Configured in Financial Setup or imported from bank activity.",
        "why_important": "Every week of runway requires exactly 1.0× weekly burn in your buffer.",
        "invariant": "Burn only counts essential survival needs, not discretionary leisure spending.",
        "user_explanation": "Weekly Burn is the absolute minimum cash you need each week to pay rent, buy groceries, and cover essential bills."
    },
    "STABILIZED_BASELINE": {
        "metric_id": "STABILIZED_BASELINE",
        "display_name": "Stabilized Income Baseline",
        "page": "income-intelligence.html",
        "definition": "The smoothed, predictable weekly earning power derived by dampening erratic gig spikes and slumps.",
        "purpose": "Prevents temporary good weeks from tricking you into unsustainable spending.",
        "calculation_concept": "Weighted combination of 60% historical average weekly earnings + 40% recent cycle earnings.",
        "data_requirements": "Historical earnings records or connected bank account transactions.",
        "why_important": "Surplus is calculated only on earnings above this stabilized baseline.",
        "invariant": "Stabilized baseline updates smoothly; sudden one-week surges do not inflate your baseline overnight.",
        "user_explanation": "Your Stabilized Baseline is your dependable weekly income after smoothing out lucky spikes and rainy slumps."
    },
    "REPORTED_BALANCE": {
        "metric_id": "REPORTED_BALANCE",
        "display_name": "Reported Bank Balance",
        "page": "bank-accounts.html",
        "definition": "Gross point-in-time liquid balance reported by your connected bank accounts via Account Aggregator sync.",
        "purpose": "Provides verified real-time visibility across all checking and savings accounts.",
        "calculation_concept": "Sum of available balances across all active linked bank accounts.",
        "data_requirements": "At least one connected bank account synced via Setu AA.",
        "why_important": "Ensures the financial engine operates on real, verified liquidity.",
        "invariant": "Gross bank balance is NOT Safe-to-Save. Upcoming commitments and floor must always be subtracted first.",
        "user_explanation": "Reported Bank Balance is the total cash currently in your bank accounts. It is not the amount you can safely save."
    },
    "VOLATILITY_COEFFICIENT": {
        "metric_id": "VOLATILITY_COEFFICIENT",
        "display_name": "Income Volatility Coefficient",
        "page": "income-intelligence.html",
        "definition": "Percentage measure of earnings fluctuation across weekly payout cycles.",
        "purpose": "Dynamically scales your emergency buffer target: higher volatility requires a larger buffer.",
        "calculation_concept": "Standard deviation of weekly earnings divided by average weekly earnings.",
        "data_requirements": "At least 3 weeks of earnings data.",
        "why_important": "A worker with 40% volatility needs 6 weeks of buffer, whereas a worker with 10% volatility only needs 3 weeks.",
        "invariant": "High volatility automatically triggers protective clamping on discretionary recommendations.",
        "user_explanation": "Volatility shows how much your earnings swing from week to week. Higher volatility means you need a bigger safety cushion."
    },
    "BUFFER_RUNWAY_WEEKS": {
        "metric_id": "BUFFER_RUNWAY_WEEKS",
        "display_name": "Buffer Runway (Weeks)",
        "page": "index.html",
        "definition": "The exact number of weeks you could survive with zero income using only your emergency buffer.",
        "purpose": "Measures your financial breathing room in clear, tangible weeks.",
        "calculation_concept": "Current Smart Buffer balance divided by Weekly Essential Burn Rate.",
        "data_requirements": "Smart Buffer and Weekly Burn.",
        "why_important": "A runway of 4.0+ weeks means you are immune to common 30-day payout delays.",
        "invariant": "Direct mathematical ratio; cannot be modified arbitrarily.",
        "user_explanation": "Runway tells you how many weeks your emergency savings will last if your income drops to zero today."
    }
}

def get_metric_info(metric_name: str) -> Optional[Dict[str, Any]]:
    """Lookup metric specification by ID or common name."""
    clean = metric_name.upper().replace("-", "_").replace(" ", "_")
    if clean in METRIC_REGISTRY:
        return METRIC_REGISTRY[clean]
    for key, spec in METRIC_REGISTRY.items():
        if clean in key or clean in spec["display_name"].upper():
            return spec
    return None
