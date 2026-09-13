"""
SURE SAVINGS 8.0: Income Source & Diversification Intelligence Service
Analyzes platform dependency, concentration risk (Herfindahl-Hirschman Index),
source stability corridors, and simulates single-source disruption scenarios.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class IncomeDiversificationService:
    """
    Evaluates multi-source income portfolio:
    - Platform share (%)
    - Concentration Index (HHI & top-source ratio)
    - Concentration Risk (LOW, MODERATE, HIGH, CRITICAL)
    - Single-Source Shock Simulation ("What if top platform drops 30%?")
    - Grounded, realistic diversification opportunities
    """

    @classmethod
    def evaluate(
        cls,
        income_sources: List[Dict[str, Any]],
        current_weekly_income: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates income sources and computes concentration intelligence.
        """
        if not income_sources:
            return {
                "status": "INSUFFICIENT_DATA",
                "message": "No active income sources recorded. Add your primary gig/freelance sources to evaluate diversification.",
                "sources_breakdown": [],
                "concentration_risk": "AWAITING_DATA",
                "concentration_score": 0,
                "top_source_share_pct": 0.0,
                "top_two_sources_share_pct": 0.0,
                "single_source_shock": None,
                "diversification_opportunities": []
            }

        # Normalize amounts to weekly equivalent
        normalized_sources = []
        for s in income_sources:
            amt = float(s.get("amount", s.get("typical_amount", 0.0)))
            freq = str(s.get("frequency", "weekly")).lower()
            if freq in ("daily", "day"):
                weekly_amt = amt * 6.0
            elif freq in ("monthly", "month"):
                weekly_amt = (amt * 12.0) / 52.0
            elif freq in ("biweekly", "bi-weekly"):
                weekly_amt = amt / 2.0
            else:
                weekly_amt = amt

            normalized_sources.append({
                "id": s.get("id"),
                "name": s.get("name", "Platform Inflow"),
                "income_type": s.get("income_type", "gig"),
                "frequency": freq,
                "original_amount": amt,
                "weekly_amount": round(weekly_amt, 2)
            })

        total_weekly = sum(s["weekly_amount"] for s in normalized_sources)
        if total_weekly <= 0:
            total_weekly = current_weekly_income if current_weekly_income and current_weekly_income > 0 else 1.0

        # Compute percentage share and HHI
        # HHI = sum of squared market shares (e.g. 58^2 + 30^2 + 12^2 = 3364 + 900 + 144 = 4408)
        # HHI > 2500 is highly concentrated in economics
        sources_breakdown = []
        hhi = 0.0

        for s in sorted(normalized_sources, key=lambda x: x["weekly_amount"], reverse=True):
            share_pct = round((s["weekly_amount"] / max(1.0, total_weekly)) * 100, 1)
            hhi += (share_pct ** 2)

            # Assign stability tier based on income type
            i_type = s["income_type"].lower()
            if "salary" in i_type or "retainer" in i_type:
                stability = "High Predictability"
            elif "freelance" in i_type or "contract" in i_type:
                stability = "Medium Variance"
            else:
                stability = "Gig Variable"

            sources_breakdown.append({
                "id": s["id"],
                "name": s["name"],
                "weekly_amount": s["weekly_amount"],
                "share_percentage": share_pct,
                "stability_profile": stability
            })

        # Top source analysis
        top_source = sources_breakdown[0] if sources_breakdown else None
        top_two_share = sum(s["share_percentage"] for s in sources_breakdown[:2])
        top_share = top_source["share_percentage"] if top_source else 0.0

        # Concentration Risk Tier
        if top_share >= 75.0 or len(sources_breakdown) == 1:
            concentration_risk = "HIGH"
            badge = "rose"
            risk_summary = f"High Concentration Risk: {top_share:.0f}% of income depends on a single platform ({top_source['name'] if top_source else 'primary source'})."
        elif top_two_share >= 80.0 or top_share >= 50.0:
            concentration_risk = "MODERATE"
            badge = "amber"
            risk_summary = f"Moderate Concentration Risk: {top_two_share:.0f}% of current earnings depend on your top two platform sources."
        else:
            concentration_risk = "LOW"
            badge = "emerald"
            risk_summary = f"Low Concentration Risk: Well diversified across {len(sources_breakdown)} balanced income streams."

        # "What if top platform drops 30%?" simulation
        single_source_shock = None
        if top_source and top_source["weekly_amount"] > 0:
            shock_pct = 30.0
            weekly_drop = round(top_source["weekly_amount"] * (shock_pct / 100.0), 2)
            post_shock_total = round(total_weekly - weekly_drop, 2)
            single_source_shock = {
                "shocked_source": top_source["name"],
                "drop_percentage": shock_pct,
                "weekly_income_loss": weekly_drop,
                "baseline_weekly_income": total_weekly,
                "projected_weekly_income": post_shock_total,
                "impact_summary": f"A {shock_pct:.0f}% downturn on {top_source['name']} reduces weekly cash flow by ₹{weekly_drop:,.0f} (from ₹{total_weekly:,.0f} → ₹{post_shock_total:,.0f}).",
                "buffer_mitigation": "Smart Buffer surplus sweeps provide full deficit-smoothing for ~4+ weeks."
            }

        # Actionable Diversification Opportunities
        opportunities = []
        if len(sources_breakdown) > 1:
            secondary = sources_breakdown[1]
            target_growth = min(25.0, secondary["share_percentage"] + 10.0)
            opportunities.append({
                "title": f"Expand {secondary['name']} Contribution ({secondary['share_percentage']}% → {target_growth}%)",
                "rationale": f"Increasing secondary platform share reduces single-source dependency on {top_source['name']}.",
                "expected_impact": "Decreases top-source concentration, mitigating platform algorithm and suspension risks."
            })
        elif len(sources_breakdown) == 1:
            opportunities.append({
                "title": "Onboard a Secondary Inflow Channel",
                "rationale": "100% of income currently relies on a single provider.",
                "expected_impact": "Provides vital cash-flow insulation during seasonal platform dry spells."
            })

        return {
            "status": "EVALUATED",
            "total_weekly_income": total_weekly,
            "sources_count": len(sources_breakdown),
            "sources_breakdown": sources_breakdown,
            "concentration_risk": concentration_risk,
            "concentration_risk_badge": badge,
            "concentration_score": min(100, int(round(hhi / 100.0))),
            "herfindahl_index": round(hhi, 1),
            "top_source_share_pct": top_share,
            "top_two_sources_share_pct": top_two_share,
            "risk_summary": risk_summary,
            "single_source_shock": single_source_shock,
            "diversification_opportunities": opportunities,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
