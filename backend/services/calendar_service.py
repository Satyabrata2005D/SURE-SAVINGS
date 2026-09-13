"""
SURE SAVINGS 8.0: Institutional Financial Calendar Engine
Generates an authoritative, user-driven financial calendar timeline from actual transactions,
scheduled obligations, income sources, buffer events, and goals.
Computes daily liquidity heatmaps, intraday payment timing curves, and dynamic critical day detection.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import calendar
import re
import uuid

from backend.policy import DEFAULT_POLICY

def _parse_time_to_minutes(time_str: str) -> int:
    """Helper to convert time string (e.g. '09:00 AM', '18:00', '9:30') to minutes from midnight."""
    if not time_str:
        return 540 # default 09:00 AM
    time_str = time_str.strip().upper()
    try:
        # Match 12-hour format: 09:00 AM
        m12 = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)?", time_str)
        if m12:
            hrs = int(m12.group(1))
            mins = int(m12.group(2))
            ampm = m12.group(3)
            if ampm == "PM" and hrs < 12:
                hrs += 12
            elif ampm == "AM" and hrs == 12:
                hrs = 0
            return hrs * 60 + mins
    except Exception:
        pass
    return 540


class FinancialCalendarService:
    """
    Authoritative service orchestrating the multi-horizon financial calendar.
    Translates user telemetry into normalized chronological events, daily liquidity matrices,
    and intraday critical gap curves.
    """

    @classmethod
    def get_calendar(
        cls,
        db: Any,
        user_id: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        view: str = "month"
    ) -> Dict[str, Any]:
        """
        Generates the comprehensive monthly calendar for the user.
        Calculates daily heatmaps, critical days, intraday projections, and summary metrics.
        """
        now = datetime.now(timezone.utc)
        target_year = year if (year and 2000 <= year <= 2100) else now.year
        target_month = month if (month and 1 <= month <= 12) else now.month

        # Days in target month
        _, num_days = calendar.monthrange(target_year, target_month)
        month_name = calendar.month_name[target_month]
        month_short = calendar.month_abbr[target_month]

        start_date_str = f"{target_year:04d}-{target_month:02d}-01"
        end_date_str = f"{target_year:04d}-{target_month:02d}-{num_days:02d}"

        # Fetch user telemetry
        from backend.models import (
            User, FinancialProfile, LedgerTransaction, ScheduledObligation,
            CalendarEvent, IncomeSource, ExpenseItem, BufferLedgerEvent, Goal, LiquidityPosition
        )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return cls._get_empty_calendar(target_year, target_month, month_name, num_days)

        prof = user.profile
        liq = user.liquidity_position
        protected_floor = float(prof.protected_floor if (prof and prof.protected_floor is not None) else (liq.protected_floor if liq else DEFAULT_POLICY.minimum_checking_floor))
        current_buffer = float(prof.current_buffer if (prof and prof.current_buffer is not None) else (liq.savings_balance if liq else 0.0))
        checking_cash = float(liq.checking_cash if (liq and liq.checking_cash is not None) else (prof.current_income if prof else 8000.0))
        weekly_burn = float(prof.weekly_burn if (prof and prof.weekly_burn is not None) else 0.0)

        # 1. Gather all events for this month
        all_events: List[Dict[str, Any]] = []

        # A. Custom Calendar Events (with dynamic recurrence expansion across month)
        cal_events = db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id).all()
        expanded_cal_events = cls._expand_calendar_events(
            cal_events=cal_events,
            user_id=user_id,
            target_year=target_year,
            target_month=target_month,
            num_days=num_days,
            start_date_str=start_date_str,
            end_date_str=end_date_str,
            created_at_iso=now.isoformat()
        )
        all_events.extend(expanded_cal_events)

        # B. Scheduled Obligations
        for o in user.obligations:
            d_str = getattr(o, "date_str", "")
            # Check if obligation matches current month/year
            matched_date = cls._resolve_obligation_date(d_str, target_year, target_month, num_days)
            if matched_date:
                # Avoid duplicates if already added via CalendarEvent
                if not any(e.get("title") == o.description and e.get("date") == matched_date for e in all_events):
                    all_events.append({
                        "id": f"obl_{o.id}",
                        "user_id": user_id,
                        "date": matched_date,
                        "time": getattr(o, "time_str", "09:00 AM") or "09:00 AM",
                        "end_time": None,
                        "title": o.description,
                        "description": getattr(o, "timing_note", "") or f"Scheduled {o.category} payment",
                        "type": "OBLIGATION",
                        "direction": getattr(o, "type", "debit") or "debit",
                        "amount": float(o.amount),
                        "source": "OBLIGATION",
                        "category": o.category or "Obligation",
                        "status": "EXPECTED",
                        "is_actual": False,
                        "is_expected": True,
                        "is_simulation": False,
                        "is_essential": getattr(o, "is_essential", True),
                        "recurrence": getattr(o, "frequency", "monthly") or "monthly",
                        "impact": getattr(o, "impact", "Safe"),
                        "risk_level": "ATTENTION" if getattr(o, "timing_risk", False) else "SAFE",
                        "cash_before": 0.0,
                        "cash_after": 0.0,
                        "buffer_before": 0.0,
                        "buffer_after": 0.0,
                        "notes": getattr(o, "timing_note", None),
                        "created_at": now.isoformat(),
                        "updated_at": now.isoformat()
                    })

        # C. Settled Ledger Transactions in this month
        for tx in user.transactions:
            tx_date = cls._resolve_tx_date(tx, target_year, target_month)
            if tx_date and start_date_str <= tx_date <= end_date_str:
                all_events.append({
                    "id": f"tx_{tx.id}",
                    "user_id": user_id,
                    "date": tx_date,
                    "time": tx.timestamp.strftime("%I:%M %p") if tx.timestamp else "12:00 PM",
                    "end_time": None,
                    "title": tx.source or "Settled Transaction",
                    "description": f"Settled {tx.category} payment",
                    "type": "INCOME" if tx.direction == "credit" else "EXPENSE",
                    "direction": tx.direction,
                    "amount": float(tx.amount),
                    "source": tx.platform or "LEDGER",
                    "category": tx.category or "General",
                    "status": "ACTUAL",
                    "is_actual": True,
                    "is_expected": False,
                    "is_simulation": False,
                    "is_essential": getattr(tx, "is_essential", False),
                    "recurrence": "none",
                    "impact": "Normal",
                    "risk_level": "SAFE",
                    "cash_before": 0.0,
                    "cash_after": 0.0,
                    "buffer_before": 0.0,
                    "buffer_after": 0.0,
                    "notes": None,
                    "created_at": tx.timestamp.isoformat() if tx.timestamp else now.isoformat(),
                    "updated_at": tx.timestamp.isoformat() if tx.timestamp else now.isoformat()
                })

        # D. Expected Recurring Income from IncomeSources
        for src in user.income_sources:
            if getattr(src, "is_active", True) and getattr(src, "typical_amount", 0.0) > 0:
                payout_dates = cls._project_income_source_dates(src, target_year, target_month, num_days)
                for p_date in payout_dates:
                    # Only add if no actual settled credit exists from this source on this date
                    if not any(e.get("date") == p_date and e.get("direction") == "credit" and src.name.lower() in e.get("title", "").lower() for e in all_events):
                        all_events.append({
                            "id": f"src_{src.id}_{p_date}",
                            "user_id": user_id,
                            "date": p_date,
                            "time": "06:00 PM", # standard evening direct deposit
                            "end_time": None,
                            "title": f"{src.name} Direct Deposit",
                            "description": f"Expected recurring {src.frequency} payout",
                            "type": "FORECAST",
                            "direction": "credit",
                            "amount": float(src.typical_amount),
                            "source": src.name,
                            "category": "Income",
                            "status": "EXPECTED",
                            "is_actual": False,
                            "is_expected": True,
                            "is_simulation": False,
                            "is_essential": False,
                            "recurrence": getattr(src, "frequency", "weekly") or "weekly",
                            "impact": "Inflow",
                            "risk_level": "SAFE",
                            "cash_before": 0.0,
                            "cash_after": 0.0,
                            "buffer_before": 0.0,
                            "buffer_after": 0.0,
                            "notes": None,
                            "created_at": now.isoformat(),
                            "updated_at": now.isoformat()
                        })

        # E. Buffer Ledger Movements
        for b_evt in (getattr(user, "buffer_events", []) or []):
            b_dt = b_evt.timestamp.strftime("%Y-%m-%d") if b_evt.timestamp else None
            if b_dt and start_date_str <= b_dt <= end_date_str:
                all_events.append({
                    "id": f"buf_{b_evt.id}",
                    "user_id": user_id,
                    "date": b_dt,
                    "time": b_evt.timestamp.strftime("%I:%M %p") if b_evt.timestamp else "10:00 AM",
                    "end_time": None,
                    "title": f"Buffer {b_evt.event_type.replace('_', ' ').title()}",
                    "description": b_evt.reason or f"Vault {b_evt.event_type}",
                    "type": "BUFFER",
                    "direction": "credit" if b_evt.amount > 0 else "debit",
                    "amount": abs(float(b_evt.amount)),
                    "source": "SMART_BUFFER",
                    "category": "Buffer",
                    "status": "ACTUAL",
                    "is_actual": True,
                    "is_expected": False,
                    "is_simulation": False,
                    "is_essential": True,
                    "recurrence": "none",
                    "impact": "Buffer Reserve Movement",
                    "risk_level": "SAFE",
                    "cash_before": 0.0,
                    "cash_after": 0.0,
                    "buffer_before": 0.0,
                    "buffer_after": 0.0,
                    "notes": b_evt.reason,
                    "created_at": b_evt.timestamp.isoformat() if b_evt.timestamp else now.isoformat(),
                    "updated_at": b_evt.timestamp.isoformat() if b_evt.timestamp else now.isoformat()
                })

        # F. Goal Milestones
        for g in (user.goals or []):
            if g.deadline:
                g_dt = g.deadline.strftime("%Y-%m-%d") if hasattr(g.deadline, "strftime") else str(g.deadline)[:10]
                if start_date_str <= g_dt <= end_date_str:
                    all_events.append({
                        "id": f"goal_{g.id}",
                        "user_id": user_id,
                        "date": g_dt,
                        "time": "12:00 PM",
                        "end_time": None,
                        "title": f"Goal Deadline: {g.name}",
                        "description": f"Target: ₹{g.target_amount:,.0f} (Current: ₹{g.current_amount:,.0f})",
                        "type": "GOAL",
                        "direction": "neutral",
                        "amount": float(g.target_amount - g.current_amount) if g.target_amount > g.current_amount else 0.0,
                        "source": "GOAL",
                        "category": "Goal",
                        "status": "EXPECTED",
                        "is_actual": False,
                        "is_expected": True,
                        "is_simulation": False,
                        "is_essential": False,
                        "recurrence": "none",
                        "impact": "Goal Milestone Target",
                        "risk_level": "SAFE",
                        "cash_before": 0.0,
                        "cash_after": 0.0,
                        "buffer_before": 0.0,
                        "buffer_after": 0.0,
                        "notes": f"Priority: {g.priority}",
                        "created_at": now.isoformat(),
                        "updated_at": now.isoformat()
                    })

        # 2. Sort all events chronologically (date then time)
        all_events.sort(key=lambda x: (x["date"], _parse_time_to_minutes(x.get("time", "09:00 AM"))))

        # 3. Simulate Day-by-Day Cash Flow & Build Days Array
        running_balance = checking_cash
        days_map: Dict[str, Dict[str, Any]] = {}

        # Pre-initialize every day of month
        for day_num in range(1, num_days + 1):
            date_key = f"{target_year:04d}-{target_month:02d}-{day_num:02d}"
            weekday_name = calendar.day_name[calendar.weekday(target_year, target_month, day_num)]
            days_map[date_key] = {
                "day": day_num,
                "date": date_key,
                "weekday": weekday_name[:3],
                "weekday_full": weekday_name,
                "events": [],
                "opening_balance": 0.0,
                "closing_balance": 0.0,
                "minimum_balance": 0.0,
                "inflows": 0.0,
                "outflows": 0.0,
                "status": "GREY", # GREEN, AMBER, RED, BLUE, GREY
                "has_timing_gap": False,
                "gap_amount": 0.0,
                "absorption_required": 0.0,
                "risk_reason": None
            }

        # Distribute events into days_map
        for ev in all_events:
            d_key = ev["date"]
            if d_key in days_map:
                days_map[d_key]["events"].append(ev)

        # Calculate daily projections
        total_inflow = 0.0
        total_outflow = 0.0
        min_month_balance = running_balance
        critical_days: List[Dict[str, Any]] = []
        total_absorption_needed = 0.0

        for day_num in range(1, num_days + 1):
            date_key = f"{target_year:04d}-{target_month:02d}-{day_num:02d}"
            d_info = days_map[date_key]
            d_info["opening_balance"] = running_balance
            
            day_events = d_info["events"]
            intraday_balance = running_balance
            lowest_intraday = running_balance
            day_inflows = 0.0
            day_outflows = 0.0
            has_buffer_event = False

            # Sort day events by time
            day_events.sort(key=lambda e: _parse_time_to_minutes(e.get("time", "09:00 AM")))

            timing_gap_detected = False
            max_day_gap = 0.0

            for ev in day_events:
                ev["cash_before"] = intraday_balance
                amt = float(ev["amount"])
                direction = ev.get("direction", "debit")
                ev_type = ev.get("type", "EXPENSE")
                is_credit = direction in ("credit", "inflow")
                is_debit = direction in ("debit", "outflow")

                if ev_type == "BUFFER":
                    has_buffer_event = True

                if is_credit:
                    intraday_balance += amt
                    day_inflows += amt
                elif is_debit:
                    intraday_balance -= amt
                    day_outflows += amt
                
                ev["cash_after"] = intraday_balance

                if intraday_balance < lowest_intraday:
                    lowest_intraday = intraday_balance

                # Check gap against floor
                if intraday_balance < protected_floor:
                    timing_gap_detected = True
                    gap = protected_floor - intraday_balance
                    if gap > max_day_gap:
                        max_day_gap = gap

            running_balance = intraday_balance
            d_info["closing_balance"] = running_balance
            d_info["minimum_balance"] = lowest_intraday
            d_info["inflows"] = day_inflows
            d_info["outflows"] = day_outflows
            total_inflow += day_inflows
            total_outflow += day_outflows

            if lowest_intraday < min_month_balance:
                min_month_balance = lowest_intraday

            # Assign Heatmap Status
            if timing_gap_detected:
                d_info["status"] = "RED"
                d_info["has_timing_gap"] = True
                d_info["gap_amount"] = max_day_gap
                d_info["absorption_required"] = max_day_gap
                total_absorption_needed += max_day_gap
                d_info["risk_reason"] = f"Projected balance dips to ₹{lowest_intraday:,.0f} (₹{max_day_gap:,.0f} below protected floor of ₹{protected_floor:,.0f})."
                critical_days.append({
                    "day": day_num,
                    "date": date_key,
                    "weekday": d_info["weekday"],
                    "min_balance": lowest_intraday,
                    "gap": max_day_gap,
                    "reason": d_info["risk_reason"],
                    "events_count": len(day_events)
                })
            elif lowest_intraday < protected_floor + 1000:
                d_info["status"] = "AMBER"
                d_info["risk_reason"] = f"Projected balance approaches floor (₹{lowest_intraday:,.0f} vs ₹{protected_floor:,.0f} floor)."
            elif has_buffer_event:
                d_info["status"] = "BLUE"
            elif len(day_events) > 0:
                d_info["status"] = "GREEN"
            else:
                d_info["status"] = "GREY"

        days_list = [days_map[k] for k in sorted(days_map.keys())]

        # Calculate largest upcoming expense
        debits = [e for e in all_events if e.get("direction") in ("debit", "outflow")]
        largest_expense = max(debits, key=lambda x: x["amount"]) if debits else None

        # Summary
        summary = {
            "expected_income": round(total_inflow, 2),
            "actual_income": round(sum(e["amount"] for e in all_events if e.get("direction") in ("credit", "inflow") and e.get("is_actual")), 2),
            "essential_outflows": round(sum(e["amount"] for e in all_events if e.get("direction") in ("debit", "outflow") and e.get("is_essential")), 2),
            "discretionary_outflows": round(sum(e["amount"] for e in all_events if e.get("direction") in ("debit", "outflow") and not e.get("is_essential")), 2),
            "net_cash_flow": round(total_inflow - total_outflow, 2),
            "upcoming_obligations_count": len(debits),
            "largest_upcoming_expense": {
                "title": largest_expense["title"] if largest_expense else "None",
                "amount": largest_expense["amount"] if largest_expense else 0.0,
                "date": largest_expense["date"] if largest_expense else None
            },
            "minimum_projected_balance": round(min_month_balance, 2),
            "protected_floor": protected_floor,
            "vault_buffer_available": current_buffer,
            "critical_gap_days_count": len(critical_days),
            "buffer_absorption_needed": round(total_absorption_needed, 2)
        }

        # First day of month weekday offset (0 = Monday, 6 = Sunday)
        first_weekday = calendar.weekday(target_year, target_month, 1)

        return {
            "status": "success",
            "year": target_year,
            "month": target_month,
            "month_name": month_name,
            "month_short": month_short,
            "num_days": num_days,
            "first_weekday": first_weekday,
            "days": days_list,
            "events": all_events,
            "critical_days": critical_days,
            "summary": summary
        }

    @classmethod
    def get_day_detail(
        cls,
        db: Any,
        user_id: str,
        date_str: str
    ) -> Dict[str, Any]:
        """
        Calculates granular intraday liquidity timeline for a specific date.
        Answers 'Why is this day risky?' with chronological ledger progression.
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            year = dt.year
            month = dt.month
        except Exception:
            year = datetime.now().year
            month = datetime.now().month

        cal = cls.get_calendar(db, user_id, year, month)
        day_info = next((d for d in cal.get("days", []) if d["date"] == date_str), None)
        if not day_info:
            return {
                "status": "error",
                "message": f"Day {date_str} not found in calendar range.",
                "date": date_str,
                "timeline": []
            }

        prof_floor = cal.get("summary", {}).get("protected_floor", DEFAULT_POLICY.minimum_checking_floor)
        buf_avail = cal.get("summary", {}).get("vault_buffer_available", 0.0)

        # Build intraday timeline nodes
        timeline_nodes = []
        running = prof_floor

        timeline_nodes.append({
            "time": "08:00 AM",
            "event": "Opening Cash Liquidity",
            "amount": 0.0,
            "projected_balance": running,
            "floor": prof_floor,
            "status": "SAFE • AT FLOOR" if running >= prof_floor else "BELOW FLOOR",
            "badge_color": "emerald" if running >= prof_floor else "rose",
            "description": f"Day opens with ₹{running:,.0f} checking balance."
        })

        day_has_gap = False
        max_day_gap = 0.0
        lowest_intraday = running
        day_events = list(day_info.get("events", []))
        day_events.sort(key=lambda e: _parse_time_to_minutes(e.get("time", "09:00 AM")))

        for ev in day_events:
            amt = float(ev["amount"])
            direction = ev.get("direction", "debit")
            time_str = ev.get("time", "09:00 AM")
            is_inflow = direction in ("credit", "inflow")

            if is_inflow:
                running += amt
                status_txt = "INFLOW RECONCILED"
                color = "emerald"
                desc = f"Batch inflow of +₹{amt:,.0f} reconciles account via {ev['title']}."
            else:
                running -= amt
                if running < lowest_intraday:
                    lowest_intraday = running
                if running < prof_floor:
                    day_has_gap = True
                    gap = prof_floor - running
                    if gap > max_day_gap:
                        max_day_gap = gap
                has_gap = running < prof_floor
                status_txt = "TIMING GAP DETECTED" if has_gap else "DEBIT SETTLED"
                color = "rose" if has_gap else "amber"
                desc = f"Debit of -₹{amt:,.0f} for {ev['title']} creates an unbuffered position of ₹{running:,.0f}."

            timeline_nodes.append({
                "time": time_str,
                "event": ev["title"],
                "amount": amt if is_inflow else -amt,
                "projected_balance": running,
                "floor": prof_floor,
                "status": status_txt,
                "badge_color": color,
                "description": desc
            })

            # Check if buffer absorption needed
            if not is_inflow and running < prof_floor:
                gap = prof_floor - running
                can_absorb = buf_avail >= gap
                cushion_after = max(0.0, buf_avail - gap)
                timeline_nodes.append({
                    "time": "09:01 AM" if "09:00" in time_str else f"{time_str} +1m",
                    "event": "Smart Buffer Standby",
                    "amount": +gap if can_absorb else 0.0,
                    "projected_balance": prof_floor if can_absorb else running,
                    "floor": prof_floor,
                    "status": "BUFFER DEPLOYED • FLOOR PROTECTED" if can_absorb else "VULNERABLE",
                    "badge_color": "blue" if can_absorb else "rose",
                    "description": f"Reserve vault covers ₹{gap:,.0f} shortfall." if can_absorb else f"Buffer insufficient to cover ₹{gap:,.0f} gap."
                })
                if can_absorb:
                    running = prof_floor

        absorption_req = max_day_gap if max_day_gap > 0 else day_info.get("absorption_required", 0.0)
        has_gap = day_has_gap or day_info.get("has_timing_gap", False)
        can_absorb = buf_avail >= absorption_req
        remaining_cushion = max(0.0, buf_avail - absorption_req)

        return {
            "status": "success",
            "date": date_str,
            "day": day_info["day"],
            "weekday": day_info["weekday_full"],
            "day_of_week": day_info["weekday_full"],
            "opening_balance": day_info["opening_balance"],
            "closing_balance": day_info["closing_balance"],
            "minimum_balance": lowest_intraday,
            "lowest_intraday_balance": lowest_intraday,
            "protected_floor": prof_floor,
            "floor": prof_floor,
            "inflows": day_info["inflows"],
            "total_inflow": day_info["inflows"],
            "outflows": day_info["outflows"],
            "total_outflow": day_info["outflows"],
            "has_timing_gap": has_gap,
            "gap_amount": max_day_gap if max_day_gap > 0 else day_info.get("gap_amount", 0.0),
            "intraday_gap_amount": max_day_gap if max_day_gap > 0 else day_info.get("gap_amount", 0.0),
            "absorption_required": absorption_req,
            "is_absorbable_by_buffer": can_absorb,
            "vault_buffer_available": buf_avail,
            "remaining_vault_cushion": remaining_cushion,
            "risk_reason": day_info.get("risk_reason"),
            "events": day_info["events"],
            "timeline": timeline_nodes
        }

    # Helper methods for date resolution
    @staticmethod
    def _resolve_obligation_date(date_str: str, year: int, month: int, max_day: int) -> Optional[str]:
        """Resolves date string like 'Sep 15', '15 Sep', 'September 15, 2026', or '2026-09-15'."""
        if not date_str:
            return None
        # Try YYYY-MM-DD
        m_iso = re.match(r"(\d{4})-(\d{2})-(\d{2})", date_str)
        if m_iso:
            y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
            if y == year and m == month and 1 <= d <= max_day:
                return f"{y:04d}-{m:02d}-{d:02d}"
        
        # Try finding day number in string (e.g. 'Sep 15', '15th', 'Day 10')
        m_day = re.search(r"\b(\d{1,2})\b", date_str)
        if m_day:
            day_val = int(m_day.group(1))
            # If string mentions month name, verify it matches
            month_name = calendar.month_name[month].lower()
            month_abbr = calendar.month_abbr[month].lower()
            d_lower = date_str.lower()
            if any(m.lower() in d_lower for m in calendar.month_name if m) or any(m.lower() in d_lower for m in calendar.month_abbr if m):
                if month_name in d_lower or month_abbr in d_lower:
                    if 1 <= day_val <= max_day:
                        return f"{year:04d}-{month:02d}-{day_val:02d}"
            else:
                # No month mentioned, assume recurring day of month
                if 1 <= day_val <= max_day:
                    return f"{year:04d}-{month:02d}-{day_val:02d}"
        return None

    @staticmethod
    def _resolve_tx_date(tx: Any, year: int, month: int) -> Optional[str]:
        """Resolves transaction date string or timestamp."""
        if getattr(tx, "timestamp", None):
            ts = tx.timestamp
            if ts.year == year and ts.month == month:
                return ts.strftime("%Y-%m-%d")
        d_str = getattr(tx, "date_str", "")
        if d_str:
            # Check YYYY-MM-DD
            m_iso = re.match(r"(\d{4})-(\d{2})-(\d{2})", d_str)
            if m_iso and int(m_iso.group(1)) == year and int(m_iso.group(2)) == month:
                return d_str
            # Check 'Sep 03, 2026'
            month_abbr = calendar.month_abbr[month]
            if month_abbr in d_str and str(year) in d_str:
                m_day = re.search(r"\b(\d{1,2})\b", d_str)
                if m_day:
                    return f"{year:04d}-{month:02d}-{int(m_day.group(1)):02d}"
        return None

    @staticmethod
    def _project_income_source_dates(src: Any, year: int, month: int, max_day: int) -> List[str]:
        """Calculates expected payout dates in the month based on frequency and payout_day."""
        dates = []
        freq = (getattr(src, "frequency", "weekly") or "weekly").lower()
        p_day = (getattr(src, "payout_day", "Wednesday") or "Wednesday").lower()

        # Target weekday (0 = Monday, 6 = Sunday)
        weekday_map = {
            "monday": 0, "mon": 0,
            "tuesday": 1, "tue": 1,
            "wednesday": 2, "wed": 2,
            "thursday": 3, "thu": 3,
            "friday": 4, "fri": 4,
            "saturday": 5, "sat": 5,
            "sunday": 6, "sun": 6
        }
        target_wd = weekday_map.get(p_day, 2) # default Wednesday

        if freq in ("weekly", "gig"):
            for d in range(1, max_day + 1):
                if calendar.weekday(year, month, d) == target_wd:
                    dates.append(f"{year:04d}-{month:02d}-{d:02d}")
        elif freq == "biweekly":
            count = 0
            for d in range(1, max_day + 1):
                if calendar.weekday(year, month, d) == target_wd:
                    count += 1
                    if count % 2 == 1:
                        dates.append(f"{year:04d}-{month:02d}-{d:02d}")
        elif freq == "monthly":
            # 1st of month or 5th
            day_target = min(5, max_day)
            dates.append(f"{year:04d}-{month:02d}-{day_target:02d}")
        return dates

    @classmethod
    def _get_empty_calendar(cls, year: int, month: int, month_name: str, num_days: int) -> Dict[str, Any]:
        """Provides typed zero-state calendar for uninitialized users."""
        days = []
        first_weekday = calendar.weekday(year, month, 1)
        for d in range(1, num_days + 1):
            date_key = f"{year:04d}-{month:02d}-{d:02d}"
            weekday_name = calendar.day_name[calendar.weekday(year, month, d)]
            days.append({
                "day": d,
                "date": date_key,
                "weekday": weekday_name[:3],
                "weekday_full": weekday_name,
                "events": [],
                "opening_balance": 0.0,
                "closing_balance": 0.0,
                "minimum_balance": 0.0,
                "inflows": 0.0,
                "outflows": 0.0,
                "status": "GREY",
                "has_timing_gap": False,
                "gap_amount": 0.0,
                "absorption_required": 0.0,
                "risk_reason": None
            })
        return {
            "status": "success",
            "year": year,
            "month": month,
            "month_name": month_name,
            "month_short": calendar.month_abbr[month],
            "num_days": num_days,
            "first_weekday": first_weekday,
            "days": days,
            "events": [],
            "critical_days": [],
            "summary": {
                "expected_income": 0.0,
                "actual_income": 0.0,
                "essential_outflows": 0.0,
                "discretionary_outflows": 0.0,
                "net_cash_flow": 0.0,
                "upcoming_obligations_count": 0,
                "largest_upcoming_expense": {"title": "None", "amount": 0.0, "date": None},
                "minimum_projected_balance": 0.0,
                "protected_floor": 0.0,
                "vault_buffer_available": 0.0,
                "critical_gap_days_count": 0,
                "buffer_absorption_needed": 0.0
            }
        }

    @classmethod
    def _expand_calendar_events(
        cls,
        cal_events: List[Any],
        user_id: str,
        target_year: int,
        target_month: int,
        num_days: int,
        start_date_str: str,
        end_date_str: str,
        created_at_iso: str
    ) -> List[Dict[str, Any]]:
        """
        Dynamically projects recurring events across the requested month window
        without requiring redundant duplicate records in the database.
        """
        expanded: List[Dict[str, Any]] = []

        for ce in cal_events:
            rec = (ce.recurrence or "none").lower()
            base_date_str = ce.date_str

            def make_dict(evt_id: str, d_str: str) -> Dict[str, Any]:
                return {
                    "id": evt_id,
                    "user_id": user_id,
                    "date": d_str,
                    "time": ce.time_str or "09:00 AM",
                    "end_time": ce.end_time_str,
                    "title": ce.title,
                    "description": ce.description or "",
                    "type": ce.event_type,
                    "direction": ce.direction,
                    "amount": float(ce.amount),
                    "source": ce.source or "MANUAL",
                    "category": ce.category or "General",
                    "status": ce.status,
                    "is_actual": ce.is_actual,
                    "is_expected": ce.is_expected,
                    "is_simulation": ce.is_simulation,
                    "is_essential": ce.is_essential,
                    "recurrence": ce.recurrence or "none",
                    "impact": ce.impact or "Safe",
                    "risk_level": ce.risk_level or "SAFE",
                    "cash_before": 0.0,
                    "cash_after": 0.0,
                    "buffer_before": 0.0,
                    "buffer_after": 0.0,
                    "notes": ce.notes,
                    "created_at": ce.created_at.isoformat() if getattr(ce, "created_at", None) else created_at_iso,
                    "updated_at": ce.updated_at.isoformat() if getattr(ce, "updated_at", None) else created_at_iso
                }

            if rec in ("none", "", None):
                if start_date_str <= base_date_str <= end_date_str:
                    expanded.append(make_dict(ce.id, base_date_str))
            else:
                try:
                    b_year, b_month, b_day = [int(x) for x in base_date_str.split("-")]
                    base_dt = datetime(b_year, b_month, b_day)
                    month_start_dt = datetime(target_year, target_month, 1)
                    month_end_dt = datetime(target_year, target_month, num_days)

                    if base_dt > month_end_dt:
                        continue

                    if rec == "daily":
                        cur_dt = max(base_dt, month_start_dt)
                        while cur_dt <= month_end_dt:
                            d_str = cur_dt.strftime("%Y-%m-%d")
                            ev_id = ce.id if d_str == base_date_str else f"{ce.id}_{d_str}"
                            expanded.append(make_dict(ev_id, d_str))
                            cur_dt += timedelta(days=1)

                    elif rec == "weekly":
                        cur_dt = base_dt
                        while cur_dt < month_start_dt:
                            cur_dt += timedelta(days=7)
                        while cur_dt <= month_end_dt:
                            d_str = cur_dt.strftime("%Y-%m-%d")
                            ev_id = ce.id if d_str == base_date_str else f"{ce.id}_{d_str}"
                            expanded.append(make_dict(ev_id, d_str))
                            cur_dt += timedelta(days=7)

                    elif rec in ("biweekly", "every 2 weeks", "every_2_weeks"):
                        cur_dt = base_dt
                        while cur_dt < month_start_dt:
                            cur_dt += timedelta(days=14)
                        while cur_dt <= month_end_dt:
                            d_str = cur_dt.strftime("%Y-%m-%d")
                            ev_id = ce.id if d_str == base_date_str else f"{ce.id}_{d_str}"
                            expanded.append(make_dict(ev_id, d_str))
                            cur_dt += timedelta(days=14)

                    elif rec == "monthly":
                        occ_day = min(b_day, num_days)
                        occ_dt = datetime(target_year, target_month, occ_day)
                        if occ_dt >= base_dt:
                            d_str = occ_dt.strftime("%Y-%m-%d")
                            ev_id = ce.id if d_str == base_date_str else f"{ce.id}_{d_str}"
                            expanded.append(make_dict(ev_id, d_str))

                    elif rec == "quarterly":
                        month_diff = (target_year - b_year) * 12 + (target_month - b_month)
                        if month_diff >= 0 and month_diff % 3 == 0:
                            occ_day = min(b_day, num_days)
                            occ_dt = datetime(target_year, target_month, occ_day)
                            d_str = occ_dt.strftime("%Y-%m-%d")
                            ev_id = ce.id if d_str == base_date_str else f"{ce.id}_{d_str}"
                            expanded.append(make_dict(ev_id, d_str))
                except Exception:
                    if start_date_str <= base_date_str <= end_date_str:
                        expanded.append(make_dict(ce.id, base_date_str))

        return expanded

    @classmethod
    def compute_expected_vs_actual(
        cls,
        db: Any,
        user_id: str,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Computes variance analysis comparing expected income and scheduled obligations
        against actual settled ledger transactions for the specified month.
        """
        cal = cls.get_calendar(db, user_id, year, month)
        events = cal.get("events", [])

        expected_items = [e for e in events if e.get("is_expected") or e.get("status") == "EXPECTED"]
        actual_items = [e for e in events if e.get("is_actual") or e.get("status") == "ACTUAL"]

        variance_records = []
        total_expected_income = 0.0
        total_actual_income = 0.0
        total_expected_outflow = 0.0
        total_actual_outflow = 0.0

        for exp in expected_items:
            exp_amt = float(exp["amount"])
            is_inflow = exp.get("direction") in ("credit", "inflow")
            if is_inflow:
                total_expected_income += exp_amt
            else:
                total_expected_outflow += exp_amt

            best_match = None
            for act in actual_items:
                if act.get("direction") == exp.get("direction"):
                    if exp.get("category") and exp["category"].lower() == act.get("category", "").lower():
                        best_match = act
                        break
                    elif exp.get("title") and act.get("title") and (exp["title"].lower() in act["title"].lower() or act["title"].lower() in exp["title"].lower()):
                        best_match = act
                        break

            if best_match:
                act_amt = float(best_match["amount"])
                amt_var = act_amt - exp_amt
                try:
                    d_exp = datetime.strptime(exp["date"], "%Y-%m-%d")
                    d_act = datetime.strptime(best_match["date"], "%Y-%m-%d")
                    delay_days = (d_act - d_exp).days
                except Exception:
                    delay_days = 0

                status = "SETTLED" if amt_var >= 0 else "PARTIAL_SETTLED"
                if delay_days > 0:
                    status = "DELAYED"

                variance_records.append({
                    "id": exp["id"],
                    "title": exp["title"],
                    "direction": exp["direction"],
                    "expected_date": exp["date"],
                    "actual_date": best_match["date"],
                    "expected_amount": exp_amt,
                    "actual_amount": act_amt,
                    "amount_variance": round(amt_var, 2),
                    "timing_delay_days": delay_days,
                    "status": status,
                    "explanation": f"Expected ₹{exp_amt:,.0f} on {exp['date']}, settled ₹{act_amt:,.0f} on {best_match['date']} ({delay_days:+d}d delay)."
                })
            else:
                today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                is_past = exp["date"] < today_str
                status = "MISSED" if is_past else "PENDING"
                variance_records.append({
                    "id": exp["id"],
                    "title": exp["title"],
                    "direction": exp["direction"],
                    "expected_date": exp["date"],
                    "actual_date": None,
                    "expected_amount": exp_amt,
                    "actual_amount": 0.0,
                    "amount_variance": round(-exp_amt, 2),
                    "timing_delay_days": 0,
                    "status": status,
                    "explanation": f"Pending settlement of expected ₹{exp_amt:,.0f} due {exp['date']}."
                })

        for act in actual_items:
            amt = float(act["amount"])
            if act.get("direction") in ("credit", "inflow"):
                total_actual_income += amt
            else:
                total_actual_outflow += amt

        return {
            "status": "success",
            "year": cal["year"],
            "month": cal["month"],
            "total_expected_income": round(total_expected_income, 2),
            "total_actual_income": round(total_actual_income, 2),
            "income_variance": round(total_actual_income - total_expected_income, 2),
            "total_expected_outflow": round(total_expected_outflow, 2),
            "total_actual_outflow": round(total_actual_outflow, 2),
            "outflow_variance": round(total_actual_outflow - total_expected_outflow, 2),
            "records": variance_records,
            "count": len(variance_records)
        }

    @classmethod
    def export_calendar_data(
        cls,
        db: Any,
        user_id: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Exports authenticated user calendar data as JSON structure or CSV formatted string.
        Strictly user-isolated.
        """
        cal = cls.get_calendar(db, user_id, year, month)
        events = cal.get("events", [])

        if export_format.lower() == "csv":
            import io, csv
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "Date", "Time", "Title", "Type", "Direction", "Amount",
                "Category", "Status", "Essential", "Impact", "Risk Level", "Notes"
            ])
            for ev in events:
                writer.writerow([
                    ev.get("date", ""),
                    ev.get("time", ""),
                    ev.get("title", ""),
                    ev.get("type", ""),
                    ev.get("direction", ""),
                    ev.get("amount", 0.0),
                    ev.get("category", ""),
                    ev.get("status", ""),
                    "Yes" if ev.get("is_essential") else "No",
                    ev.get("impact", ""),
                    ev.get("risk_level", ""),
                    ev.get("notes", "") or ""
                ])
            return {
                "format": "csv",
                "filename": f"financial_calendar_{cal['year']}_{cal['month']:02d}.csv",
                "content_type": "text/csv",
                "data": output.getvalue()
            }
        else:
            return {
                "format": "json",
                "filename": f"financial_calendar_{cal['year']}_{cal['month']:02d}.json",
                "content_type": "application/json",
                "data": cal
            }

