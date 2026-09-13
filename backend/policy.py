"""
SURE SAVINGS 2.0: Centralized Financial Policy Configuration & Definitions
Source of truth for all mathematical constants, policy caps, safety floors,
resilience weightings, shock scenarios, and rounding rules.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List

class ShockScenarioPreset(BaseModel):
    id: str
    label: str
    drop_pct: float
    description: str
    severity: str # LOW, MODERATE, HIGH, CRITICAL

class FinancialPolicyConfig(BaseModel):
    policy_name: str = "Gig Worker Resilience Baseline Policy"
    policy_version: str = "v2.5"
    currency_code: str = "INR"
    currency_symbol: str = "₹"

    # Core Policy Caps & Safety Floors
    surplus_policy_cap: float = Field(0.70, description="70% safeguard cap applied to detected surplus")
    minimum_checking_floor: float = Field(3500.0, description="Strictly protected operational cash floor in primary checking")
    default_weekly_burn: float = Field(4400.0, description="Essential weekly baseline burn rate (rent, EV EMI, basic food)")
    default_buffer_target: float = Field(15000.0, description="Target smart buffer capital (approx 3.41 weeks of fixed burn)")
    buffer_target_weeks: float = Field(3.41, description="Target buffer coverage in weeks")
    rounding_increment: float = Field(50.0, description="Clean execution increment for safe allocations")

    # Inflow Analysis Constraints
    minimum_history_weeks: int = Field(3, description="Minimum weeks required to establish stabilized baseline")
    stabilized_median_weight: float = Field(0.60, description="Weight of median in stabilized income formula")
    stabilized_mean_weight: float = Field(0.40, description="Weight of mean in stabilized income formula")
    high_income_multiplier: float = Field(1.15, description="Multiplier for surplus identification (+15% above baseline)")
    low_income_multiplier: float = Field(0.80, description="Multiplier for income drought warning (-20% below baseline)")

    # Resilience Scoring Dimension Weights (Sum == 1.0)
    income_stability_weight: float = Field(0.25, description="Income predictability weight")
    buffer_coverage_weight: float = Field(0.30, description="Buffer runway coverage weight")
    expense_health_weight: float = Field(0.20, description="Fixed expense ratio weight")
    cashflow_health_weight: float = Field(0.25, description="Timing gap and liquidity health weight")

    # Risk Telemetry Thresholds
    low_risk_max: int = Field(30, description="Max score for low risk tier")
    moderate_risk_max: int = Field(60, description="Max score for moderate risk tier")

    # Intraday Cash-Flow Timing Thresholds
    intraday_gap_warning_threshold: float = Field(-500.0, description="Net deficit triggering timing gap warning")
    intraday_critical_deficit_threshold: float = Field(-2000.0, description="Net deficit triggering high priority circuit breaker")

    # Pre-defined Shock Scenarios
    shock_presets: List[ShockScenarioPreset] = Field(
        default_factory=lambda: [
            ShockScenarioPreset(
                id="normal",
                label="Normal Inflow",
                drop_pct=0.0,
                description="Baseline conditions with normal platform payout schedule.",
                severity="LOW"
            ),
            ShockScenarioPreset(
                id="drought_10",
                label="-10% Mild Drift",
                drop_pct=10.0,
                description="Slight platform order slowdown; fully absorbable by normal liquidity.",
                severity="LOW"
            ),
            ShockScenarioPreset(
                id="drought_20",
                label="-20% Seasonal Drought",
                drop_pct=20.0,
                description="-20% seasonal dip in orders; automated savings paused, buffer covers gap.",
                severity="MODERATE"
            ),
            ShockScenarioPreset(
                id="drought_40",
                label="-40% Platform Downtime",
                drop_pct=40.0,
                description="Severe disruption or platform outage; buffer cushions fixed burn for ~4.8 weeks.",
                severity="HIGH"
            ),
            ShockScenarioPreset(
                id="drought_60",
                label="-60% Extreme Shock",
                drop_pct=60.0,
                description="Emergency drought; buffer deploys defensive deficit-smoothing to prevent floor breach.",
                severity="CRITICAL"
            )
        ]
    )

    def get_buffer_state(self, current_buffer: float, target: float, floor: float) -> str:
        """
        State machine:
        - HEALTHY: >= target
        - BUILDING: > floor and < target
        - PROTECTING: == floor
        - CRITICAL: < floor
        """
        if current_buffer >= target:
            return "HEALTHY"
        elif current_buffer > floor:
            return "BUILDING"
        elif current_buffer == floor:
            return "PROTECTING"
        else:
            return "CRITICAL"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

# Global default policy instance
DEFAULT_POLICY = FinancialPolicyConfig()
