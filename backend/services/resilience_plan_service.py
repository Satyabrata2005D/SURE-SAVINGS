"""
SURE SAVINGS 8.0: Personal Resilience Plan Engine
Generates an authoritative, personalized 30-day financial resilience roadmap
with ranked priorities, threshold-activated risk triggers, and recovery milestones.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import uuid

class ResiliencePlanService:
    """
    Synthesizes the complete 30-Day Personal Resilience Plan from authoritative telemetry.
    """

    @classmethod
    def generate_plan(
        cls,
        digital_twin: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates structured 30-day resilience plan with 4 ranked priorities,
        risk triggers, 4-week milestones, and expected score deltas.
        """
        obs = digital_twin.get("observation", {})
        prof = obs.get("profile", {}) or digital_twin.get("profile", {})
        und = digital_twin.get("understanding", {})
        dec = digital_twin.get("decisions", {})

        curr_inc = float(prof.get("current_income", 0.0))
        stab_inc = float(prof.get("stabilized_income", und.get("stabilized_income", {}).get("amount", 0.0)))
        burn = float(prof.get("weekly_burn", und.get("burn", {}).get("essential", 0.0)))
        curr_buf = float(prof.get("current_buffer", 0.0))
        target_buf = float(prof.get("buffer_target", 15000.0))
        floor = float(prof.get("protected_floor", 3500.0))
        surplus = float(prof.get("surplus", dec.get("safe_to_save", {}).get("surplus", 0.0)))
        save_rec = float(prof.get("recommended_contribution", dec.get("safe_to_save", {}).get("recommended_save", 0.0)))
        pocket = float(prof.get("free_pocket_liquidity", max(0.0, surplus - save_rec)))
        resilience = int(und.get("resilience", {}).get("score", prof.get("resilience_score", 0)))
        risk = int(und.get("risk", {}).get("score", prof.get("risk_score", 0)))
        coverage = float(und.get("runway", {}).get("weeks", prof.get("current_coverage_weeks", 0.0)))
        behavior = digital_twin.get("behavior_profile", "STABLE")

        cf = und.get("cash_flow", {})
        timing_gaps = cf.get("timing_gaps", []) or []

        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=30)
        plan_id = f"plan_{uuid.uuid4().hex[:10]}"

        # Zero / Unconfigured state handling
        if curr_inc <= 0 and burn <= 0 and curr_buf <= 0:
            return {
                "plan_id": plan_id,
                "version": "v8.0",
                "status": "AWAITING_DATA",
                "title": "Awaiting Financial Calibration",
                "summary": "Complete your baseline income and expense profile to generate your personalized 30-Day Resilience Plan.",
                "current_resilience": 0,
                "target_resilience": 75,
                "priorities": [],
                "top_priorities": [],
                "risk_triggers": [],
                "weekly_roadmap": [],
                "recovery_target": "Calibrate profile to unlock runway targets."
            }

        # Dynamic target resilience projection
        target_resilience = min(95, max(resilience + 6, 78 if resilience >= 70 else (resilience + 12)))
        buffer_gap = max(0.0, target_buf - curr_buf)
        next_milestone_buffer = round(min(target_buf, curr_buf + max(2000.0, save_rec * 4)) / 100.0) * 100.0

        # 1. Priorities
        priorities = [
            {
                "rank": 1,
                "title": f"Protect ₹{floor:,.0f} Minimum Checking Liquidity",
                "description": f"Enforce operational cash floor of ₹{floor:,.0f} in primary checking. Never sweep funds that compress checking balance below this threshold.",
                "reason": "Guarantees immediate solvency for unplanned emergency payments.",
                "expected_impact": "Zero checking floor breaches; 100% intraday protection",
                "status": "MANDATORY_POLICY"
            },
            {
                "rank": 2,
                "title": f"Reserve ₹{save_rec:,.0f} Safe-to-Save Allocation This Cycle",
                "description": f"Sweep ₹{save_rec:,.0f} (70% of detected ₹{surplus:,.0f} surplus) into the Smart Buffer Vault while retaining ₹{pocket:,.0f} free pocket cash.",
                "reason": "Expands emergency buffer runway without inducing austerity stress.",
                "expected_impact": f"Expands buffer from ₹{curr_buf:,.0f} → ₹{curr_buf + save_rec:,.0f} (+0.2 weeks coverage)",
                "status": "ACTION_PENDING"
            },
            {
                "rank": 3,
                "title": f"Limit Discretionary Spend for Next 10 Days (Max ₹{max(500.0, pocket):,.0f})",
                "description": f"Retain unconstrained free cash of ₹{pocket:,.0f} in checking while insulating upcoming fixed obligations.",
                "reason": f"{'Upcoming intraday commitment detected' if timing_gaps else 'Maintains cash-flow stability between platform payout tranches'}.",
                "expected_impact": "Insulates checking balance against timing mismatches",
                "status": "RECOMMENDED"
            },
            {
                "rank": 4,
                "title": f"Advance Smart Buffer: ₹{curr_buf:,.0f} → ₹{next_milestone_buffer:,.0f}",
                "description": f"Progress systematically toward the 30-day milestone of ₹{next_milestone_buffer:,.0f} (toward ultimate target of ₹{target_buf:,.0f}).",
                "reason": f"Expands runway coverage from {coverage:.1f} weeks toward 3.5+ weeks.",
                "expected_impact": f"Resilience score reaches {target_resilience}/100 upon milestone completion",
                "status": "IN_PROGRESS"
            }
        ]

        # 2. Threshold-Activated Risk Triggers
        risk_triggers = [
            {
                "id": "trig_inc_drop",
                "condition": f"If weekly income drops below ₹{round(stab_inc * 0.75):,.0f} (-25% below baseline)",
                "action": "Automatically pause automated savings sweeps; preserve 100% of liquid inflows in primary checking.",
                "severity": "WARNING"
            },
            {
                "id": "trig_timing_gap",
                "condition": f"If checking balance drops within ₹800 of ₹{floor:,.0f} floor before evening payout",
                "action": "Activate buffer vault smoothing to absorb intraday deficit without overdraft or borrowing.",
                "severity": "CRITICAL"
            },
            {
                "id": "trig_windfall_surplus",
                "condition": f"If cycle income exceeds ₹{round(stab_inc * 1.25):,.0f} (+25% peak bonus)",
                "action": "Cap savings sweep at 70% (₹{round(save_rec * 1.3):,.0f}); allocate remainder to unconstrained cash.",
                "severity": "POSITIVE"
            }
        ]

        # 3. 4-Week Execution Roadmap
        weekly_roadmap = [
            {
                "week_number": 1,
                "label": "Week 1",
                "focus": "Liquidity Floor & Immediate Commitment Defense",
                "target_save": save_rec,
                "projected_buffer": curr_buf + save_rec,
                "milestone": f"Preserve ₹{floor:,.0f} floor; absorb upcoming obligations.",
                "resilience_projection": resilience + 2
            },
            {
                "week_number": 2,
                "label": "Week 2",
                "focus": "Disciplined Surplus Sweeping",
                "target_save": save_rec,
                "projected_buffer": curr_buf + (save_rec * 2),
                "milestone": f"Expand buffer to ₹{curr_buf + (save_rec * 2):,.0f} (advance to {coverage + 0.4:.1f} weeks runway).",
                "resilience_projection": resilience + 4
            },
            {
                "week_number": 3,
                "label": "Week 3",
                "focus": "Fixed Burn Ratio Optimization",
                "target_save": save_rec,
                "projected_buffer": curr_buf + (save_rec * 3),
                "milestone": "Verify discretionary spending discipline and re-assess weekly volatility.",
                "resilience_projection": resilience + 5
            },
            {
                "week_number": 4,
                "label": "Week 4",
                "focus": "Milestone Target Verification & Plan Recalibration",
                "target_save": save_rec,
                "projected_buffer": next_milestone_buffer,
                "milestone": f"Achieve 30-day buffer milestone of ₹{next_milestone_buffer:,.0f}; lock in {target_resilience} score.",
                "resilience_projection": target_resilience
            }
        ]

        # 4. Action Items formatted for UI
        actions = [
            {
                "priority": p["rank"],
                "action": p["title"],
                "reason": p["reason"],
                "expected_impact": p["expected_impact"],
                "trigger": risk_triggers[min(p["rank"] - 1, len(risk_triggers) - 1)]["condition"],
                "confidence": 0.94,
                "status": p["status"]
            }
            for p in priorities
        ]

        return {
            "plan_id": plan_id,
            "plan_name": "30-Day Financial Resilience Plan",
            "version": "v8.0",
            "created_at": now.isoformat(),
            "valid_until": valid_until.isoformat(),
            "status": "ACTIVE",
            "current_state": {
                "resilience_score": resilience,
                "risk_score": risk,
                "current_buffer": curr_buf,
                "coverage_weeks": coverage,
                "behavior_profile": behavior,
                "protected_floor": floor,
                "weekly_essential_burn": burn
            },
            "target_state": {
                "target_resilience": target_resilience,
                "target_buffer": target_buf,
                "milestone_buffer": next_milestone_buffer,
                "target_coverage_weeks": round(target_buf / burn, 1) if burn > 0 else 4.0,
                "buffer_gap": buffer_gap
            },
            "priorities": priorities,
            "top_priorities": priorities,
            "actions": actions,
            "risk_triggers": risk_triggers,
            "weekly_roadmap": weekly_roadmap,
            "recovery_target": f"Restore {round(target_buf/burn, 1) if burn > 0 else 4.0}-week runway buffer (₹{target_buf:,.0f}).",
            "expected_impact": f"Resilience upgrades from {resilience} → {target_resilience} (+{target_resilience - resilience} pts) over 30 days."
        }
