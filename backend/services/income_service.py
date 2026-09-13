"""
SURE SAVINGS 2.0: Income Analytics & Stabilized Baseline Domain Services
Provides deterministic volatility analysis, trend forecasting, and baseline stabilization.
"""
from typing import List, Dict, Any, Optional
import statistics
from backend.policy import DEFAULT_POLICY, FinancialPolicyConfig

class StabilizedIncomeService:
    """
    Authoritative service for computing the stabilized income baseline.
    Formula: 0.60 * Median + 0.40 * Mean
    Insulates gig workers against temporary windfalls while adjusting to genuine drift.
    """

    @classmethod
    def calculate(
        cls,
        inflows: List[float],
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> float:
        if not inflows:
            return 0.0
        if len(inflows) == 1:
            return round(inflows[0], 2)

        med = statistics.median(inflows)
        avg = statistics.mean(inflows)
        stabilized = (policy.stabilized_median_weight * med) + (policy.stabilized_mean_weight * avg)
        return round(stabilized, 2)


def _get_val(o: Any, attr: str, default: Any = None) -> Any:
    if hasattr(o, attr):
        val = getattr(o, attr)
        return val if val is not None else default
    if isinstance(o, dict):
        return o.get(attr, default)
    return default

class IncomeAnalyticsService:
    """
    Authoritative analytical service evaluating income volatility,
    consistency corridors, platform distributions, and predictability scores.
    """

    @staticmethod
    def calculate_average(inflows: List[float]) -> float:
        if not inflows:
            return 0.0
        return round(statistics.mean(inflows), 2)

    @staticmethod
    def calculate_median(inflows: List[float]) -> float:
        if not inflows:
            return 0.0
        return round(statistics.median(inflows), 2)

    @staticmethod
    def calculate_volatility(inflows: List[float]) -> float:
        """
        Coefficient of Variation (CV = standard_deviation / mean).
        0.0 - 0.15: High stability
        0.16 - 0.35: Moderate gig fluctuation (Arjun K. canonical is ~0.31)
        0.36+: High erratic variance
        """
        if len(inflows) < 2:
            return 0.0
        mean = statistics.mean(inflows)
        if mean <= 0:
            return 0.0
        std = statistics.stdev(inflows)
        return round(std / mean, 2)

    @classmethod
    def calculate_stability_score(cls, volatility: float) -> int:
        """
        Transforms volatility CV into an intuitive 0-100 stability index.
        CV of 0.31 yields ~82 stability.
        """
        raw = 100.0 - (volatility * 58.0)
        return max(20, min(99, int(round(raw))))

    @classmethod
    def calculate_statistical_forecast(cls, actual_inflows: List[float], volatility: float) -> Dict[str, Any]:
        """
        Computes probabilistic forward cash-flow projection:
        Uses median baseline damped by lower-tercile variability for gig conservatism.
        Requires at least 4 historical periods.
        """
        if not actual_inflows or len(actual_inflows) < 4:
            return {
                "point": 0.0,
                "lower": 0.0,
                "upper": 0.0,
                "confidence": 0.0,
                "status": "INSUFFICIENT_DATA",
                "message": "Add at least 4 weeks of income history to unlock predictive forecasting."
            }
        med = cls.calculate_median(actual_inflows)
        sorted_inf = sorted(actual_inflows)
        p40_idx = int(len(sorted_inf) * 0.40)
        p40 = sorted_inf[p40_idx] if sorted_inf else med
        point = round((0.30 * med + 0.70 * p40) / 100.0) * 100.0
        confidence = max(0.60, min(0.98, round(1.0 - (volatility * 0.25), 2)))
        lower = round(point * (1.0 - volatility), 2)
        upper = round(point * (1.0 + volatility), 2)
        return {
            "point": point,
            "lower": lower,
            "upper": upper,
            "confidence": confidence,
            "status": "CONFIDENT" if len(actual_inflows) >= 8 else "BASIC"
        }

    @classmethod
    def analyze_history(
        cls,
        history_records: List[Any],
        current_income: float,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        """
        Generates full analytical profile dynamically from database records.
        """
        actual_inflows = [
            _get_val(h, "income", 0.0)
            for h in history_records
            if not (_get_val(h, "is_forecast", False) if hasattr(h, "is_forecast") else _get_val(h, "forecast", False))
            and not (_get_val(h, "is_current", False) if hasattr(h, "is_current") else _get_val(h, "current", False))
        ]

        has_historical_evidence = len(actual_inflows) > 0
        if not actual_inflows and current_income > 0:
            actual_inflows = [current_income]

        if not actual_inflows:
            return {
                "current_week_income": 0.0,
                "stabilized_baseline": 0.0,
                "forecast_next_week": 0.0,
                "forecast_confidence": 0.0,
                "forecast_lower_bound": 0.0,
                "forecast_upper_bound": 0.0,
                "volatility_index": 0.0,
                "income_stability_score": 0,
                "median_weekly": 0.0,
                "average_weekly": 0.0,
                "lowest_recorded": 0.0,
                "highest_recorded": 0.0,
                "safe_floor_spread": 0.0,
                "recent_drift_pct": 0.0,
                "formula": "60% Median + 40% Mean",
                "explanation": "No income records available yet. Add your income sources or history to begin.",
                "history": [],
                "forecast_status": "NOT_AVAILABLE",
                "volatility_status": "NOT_AVAILABLE",
                "status": "NO_DATA"
            }

        med = cls.calculate_median(actual_inflows)
        avg = cls.calculate_average(actual_inflows)
        
        # Volatility: CV requires at least 2 data points
        if len(actual_inflows) >= 2:
            vol = cls.calculate_volatility(actual_inflows)
            vol_status = "AVAILABLE"
            stability_score = cls.calculate_stability_score(vol)
        else:
            vol = 0.0
            vol_status = "INSUFFICIENT_DATA"
            stability_score = 0

        stabilized = round(StabilizedIncomeService.calculate(actual_inflows, policy) / 100.0) * 100.0 if len(actual_inflows) > 1 else actual_inflows[0]

        forecast_data = cls.calculate_statistical_forecast(actual_inflows, vol)
        forecast_point = forecast_data["point"]
        forecast_status = forecast_data.get("status", "NOT_AVAILABLE")

        lowest = min(actual_inflows)
        highest = max(actual_inflows)
        recent_drift = round(((current_income - stabilized) / stabilized) * 100, 1) if stabilized > 0 else 0.0

        # Formatted history list
        formatted_history = []
        for h in history_records:
            formatted_history.append({
                "week": _get_val(h, "week", ""),
                "income": _get_val(h, "income", 0.0),
                "stabilized": _get_val(h, "stabilized", stabilized),
                "status": _get_val(h, "status", "Normal"),
                "current": _get_val(h, "is_current", _get_val(h, "current", False)),
                "forecast": _get_val(h, "is_forecast", _get_val(h, "forecast", False))
            })

        return {
            "current_week_income": current_income,
            "stabilized_baseline": stabilized,
            "forecast_next_week": forecast_point,
            "forecast_confidence": forecast_data["confidence"],
            "forecast_lower_bound": forecast_data["lower"],
            "forecast_upper_bound": forecast_data["upper"],
            "volatility_index": vol,
            "income_stability_score": stability_score,
            "median_weekly": med,
            "average_weekly": avg,
            "lowest_recorded": lowest,
            "highest_recorded": highest,
            "safe_floor_spread": round(stabilized - policy.minimum_checking_floor, 2),
            "recent_drift_pct": recent_drift,
            "formula": f"{int(policy.stabilized_median_weight * 100)}% Median + {int(policy.stabilized_mean_weight * 100)}% Mean",
            "explanation": f"Stabilized at ₹{stabilized:,.0f} by combining 12-week median (₹{med:,.0f}) and mean (₹{avg:,.0f}). Current week's ₹{current_income:,.0f} represents a +{recent_drift}% surplus.",
            "history": formatted_history,
            "forecast_status": forecast_status,
            "volatility_status": vol_status
        }
