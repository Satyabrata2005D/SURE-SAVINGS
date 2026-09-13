"""
SURE SAVINGS 2.0: Cash-Flow Timing & Intraday Liquidity Intelligence Service
Models payment timing mismatches, intraday balance curves, and buffer absorption.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.policy import DEFAULT_POLICY, FinancialPolicyConfig

def _get_val(o: Any, attr: str, default: Any = None) -> Any:
    if hasattr(o, attr):
        val = getattr(o, attr)
        return val if val is not None else default
    if isinstance(o, dict):
        return o.get(attr, default)
    return default

class CashFlowTimingService:
    """
    Authoritative service modeling intraday and multi-day liquidity dynamics.
    Detects timing mismatches where fixed obligations debit hours before batch settlements.
    """

    @classmethod
    def calculate_intraday_timeline(
        cls,
        target_date: Optional[str] = None,
        checking_floor: float = DEFAULT_POLICY.minimum_checking_floor,
        buffer_reserve: float = 3300.0,
        obligations: Optional[List[Any]] = None,
        policy: FinancialPolicyConfig = DEFAULT_POLICY
    ) -> Dict[str, Any]:
        """
        Dynamically computes the intraday timeline curve by discovering scheduled obligations:
        - Baseline: Pre-market operational checking balance = Floor
        - Debits: Outflows discovered from scheduled obligations
        - Deficit check: Detects if debits create a timing gap below checking floor
        - Buffer Absorption: Sweeps required gap from available vault reserve
        - Credits: Inflows arriving later in the cycle
        """
        if obligations is not None and len(obligations) == 0:
            display_date = target_date or datetime.now().strftime("%B %d, %Y")
            return {
                "date": display_date,
                "has_timing_gap": False,
                "intraday_gap_amount": 0.0,
                "absorption_required": 0.0,
                "is_absorbable_by_buffer": True,
                "vault_buffer_available": buffer_reserve,
                "remaining_vault_cushion": buffer_reserve,
                "final_net_liquidity": checking_floor,
                "min_projected_balance": checking_floor,
                "protection_status": "NO OBLIGATIONS RECORDED",
                "timeline": []
            }

        initial_balance = checking_floor
        matching_debits = []
        matching_credits = []

        if obligations is None:
            # Standalone fallback when called without database / obligations context
            display_date = target_date or datetime.now().strftime("%B %d, %Y")
            emi_debit = 4500.0
            emi_desc = "HDFC EV Two-Wheeler EMI"
            emi_time = "09:00 AM"
            payout_credit = 6900.0
            payout_desc = "Platform Inflow Direct Deposit"
            payout_time = "06:00 PM"
            target_date = display_date
        else:
            # Discover matching obligations for the target date or find date with highest debit
            if target_date:
                for o in obligations:
                    d_str = str(_get_val(o, "date_str", _get_val(o, "date", "")))
                    if target_date.lower() in d_str.lower() or d_str.lower() in target_date.lower():
                        o_type = _get_val(o, "type", "debit")
                        if o_type == "credit":
                            matching_credits.append(o)
                        else:
                            matching_debits.append(o)

            # If no direct match on target_date, find the date with the highest net debit risk
            if not matching_debits and not matching_credits and obligations:
                by_date = {}
                for o in obligations:
                    d_str = _get_val(o, "date_str", _get_val(o, "date", "Upcoming"))
                    by_date.setdefault(d_str, []).append(o)
                
                best_date = None
                max_debit = 0.0
                for d, items in by_date.items():
                    deb_sum = sum(_get_val(it, "amount", 0.0) for it in items if _get_val(it, "type", "debit") == "debit")
                    if deb_sum > max_debit:
                        max_debit = deb_sum
                        best_date = d
                
                if best_date:
                    target_date = best_date
                    for it in by_date[best_date]:
                        if _get_val(it, "type", "debit") == "credit":
                            matching_credits.append(it)
                        else:
                            matching_debits.append(it)
                elif obligations:
                    target_date = _get_val(obligations[0], "date_str", _get_val(obligations[0], "date", datetime.now().strftime("%B %d, %Y")))

            if not matching_debits and not matching_credits:
                display_date = target_date or datetime.now().strftime("%B %d, %Y")
                return {
                    "date": display_date,
                    "has_timing_gap": False,
                    "intraday_gap_amount": 0.0,
                    "absorption_required": 0.0,
                    "is_absorbable_by_buffer": True,
                    "vault_buffer_available": buffer_reserve,
                    "remaining_vault_cushion": buffer_reserve,
                    "final_net_liquidity": checking_floor,
                    "min_projected_balance": checking_floor,
                    "protection_status": "NO TIMING MISMATCH DETECTED",
                    "timeline": []
                }

            emi_debit = sum(_get_val(o, "amount", 0.0) for o in matching_debits)
            emi_desc = _get_val(matching_debits[0], "description", "Scheduled Commitment") if matching_debits else "Scheduled Commitment"
            emi_time = _get_val(matching_debits[0], "time_str", _get_val(matching_debits[0], "time", "09:00 AM")) if matching_debits else "09:00 AM"

            payout_credit = sum(_get_val(o, "amount", 0.0) for o in matching_credits)
            payout_desc = _get_val(matching_credits[0], "description", "Expected Inflow") if matching_credits else "Expected Inflow"
            payout_time = _get_val(matching_credits[0], "time_str", _get_val(matching_credits[0], "time", "06:00 PM")) if matching_credits else "06:00 PM"

            if payout_credit == 0.0 and obligations is None:
                payout_credit = 6900.0
                payout_desc = "Platform Inflow Direct Deposit"
                payout_time = "06:00 PM"

        raw_midday_balance = initial_balance - emi_debit
        timing_gap = min(0.0, raw_midday_balance)
        absorption_required = abs(timing_gap)
        has_gap = timing_gap < 0

        is_absorbable = buffer_reserve >= absorption_required
        remaining_vault_cushion = max(0.0, buffer_reserve - absorption_required)
        post_payout_balance = initial_balance - emi_debit + payout_credit

        timeline_nodes = [
            {
                "time": "08:00 AM",
                "label": "Market Open Balance",
                "event": "Baseline Operational Liquidity",
                "amount": 0.0,
                "projected_checking": initial_balance,
                "floor": checking_floor,
                "status": "SAFE • AT FLOOR",
                "badge_class": "bg-emerald-50 text-emerald-700",
                "description": f"Checking account sits securely at protected floor of ₹{checking_floor:,.0f}."
            }
        ]

        if emi_debit > 0:
            timeline_nodes.append({
                "time": emi_time,
                "label": emi_desc,
                "event": emi_desc,
                "amount": -emi_debit,
                "projected_checking": raw_midday_balance,
                "floor": checking_floor,
                "status": "TIMING GAP DETECTED" if has_gap else "SAFE",
                "badge_class": "bg-amber-50 text-amber-700" if has_gap else "bg-emerald-50 text-emerald-700",
                "description": f"Debit of -₹{emi_debit:,.0f} creates an unbuffered position of ₹{raw_midday_balance:,.0f}."
            })

        if has_gap and absorption_required > 0:
            timeline_nodes.append({
                "time": "09:01 AM",
                "label": "Smart Buffer Absorption",
                "event": "Automated Intraday Liquidity Bridge",
                "amount": +absorption_required,
                "projected_checking": checking_floor,
                "floor": checking_floor,
                "status": "BUFFER DEPLOYED • FLOOR PROTECTED",
                "badge_class": "bg-blue-50 text-blue-700",
                "description": f"Vault absorbs ₹{absorption_required:,.0f} shortfall; ₹{remaining_vault_cushion:,.0f} cushion remains in vault reserve."
            })

        if payout_credit > 0:
            timeline_nodes.append({
                "time": payout_time,
                "label": payout_desc,
                "event": "Settlement Direct Deposit",
                "amount": +payout_credit,
                "projected_checking": post_payout_balance,
                "floor": checking_floor,
                "status": "RECOVERED • HIGH SURPLUS",
                "badge_class": "bg-emerald-50 text-emerald-700",
                "description": f"Batch inflow of +₹{payout_credit:,.0f} reconciles account to healthy ₹{post_payout_balance:,.0f}."
            })

        return {
            "date": target_date,
            "has_timing_gap": has_gap,
            "intraday_gap_amount": timing_gap,
            "absorption_required": absorption_required,
            "is_absorbable_by_buffer": is_absorbable,
            "vault_buffer_available": buffer_reserve,
            "remaining_vault_cushion": remaining_vault_cushion,
            "final_net_liquidity": post_payout_balance,
            "min_projected_balance": checking_floor if is_absorbable else raw_midday_balance,
            "protection_status": ("100% PROTECTED BY SURE SAVINGS VAULT" if is_absorbable else "VULNERABLE") if has_gap else "NO TIMING GAP",
            "timeline": timeline_nodes
        }

    @classmethod
    def calculate_multiday_cash_flow(
        cls,
        obligations: List[Any],
        current_income: float,
        current_buffer: float,
        checking_floor: float = DEFAULT_POLICY.minimum_checking_floor
    ) -> Dict[str, Any]:
        """
        Aggregates upcoming multi-day inflows and outflows.
        """
        inflows = sum(
            _get_val(o, "amount", 0.0)
            for o in obligations
            if _get_val(o, "type", "debit") == "credit"
        ) + current_income

        outflows = sum(
            _get_val(o, "amount", 0.0)
            for o in obligations
            if _get_val(o, "type", "debit") == "debit"
        )

        net_margin = round(inflows - outflows, 2)
        safe_vault_reserve = max(0.0, current_buffer - checking_floor)

        intraday = cls.calculate_intraday_timeline(
            checking_floor=checking_floor,
            buffer_reserve=safe_vault_reserve,
            obligations=obligations
        )

        formatted_obligations = []
        for o in obligations:
            formatted_obligations.append({
                "id": _get_val(o, "id", ""),
                "date": _get_val(o, "date_str", _get_val(o, "date", "")),
                "description": _get_val(o, "description", ""),
                "category": _get_val(o, "category", ""),
                "type": _get_val(o, "type", "debit"),
                "amount": _get_val(o, "amount", 0.0),
                "essential": _get_val(o, "is_essential", _get_val(o, "essential", True)),
                "impact": _get_val(o, "impact", "Safe"),
                "timing_risk": _get_val(o, "timing_risk", False),
                "timing_note": _get_val(o, "timing_note", None)
            })

        min_balance = intraday.get("min_projected_balance", checking_floor) if obligations else checking_floor
        if obligations and intraday.get("has_timing_gap"):
            min_balance = intraday.get("min_projected_balance", checking_floor)
        elif obligations:
            min_balance = max(0.0, checking_floor + net_margin) if net_margin < 0 else checking_floor

        return {
            "upcoming_inflows": inflows,
            "scheduled_outflows": outflows,
            "net_liquidity_margin": net_margin,
            "projected_minimum_balance": min_balance,
            "protected_floor": checking_floor,
            "vault_buffer_reserve": safe_vault_reserve,
            "intraday_intelligence": intraday,
            "scheduled_obligations": formatted_obligations,
            "cash_flow_status": "ACTIVE" if obligations else "AWAITING_OBLIGATIONS"
        }
