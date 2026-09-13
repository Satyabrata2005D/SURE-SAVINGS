"""
SURE SAVINGS 8.0: Personal Financial Memory & Timeline Service
Maintains the continuous chronological financial story of the user workspace,
recording state transitions, buffer milestones, liquidity gaps, and resilience recovery points.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.models import FinancialEvent, FinancialSnapshot, User

class FinancialTimelineService:
    """
    Synthesizes the human-readable chronological 'Your Financial Story'
    from authoritative financial events, snapshots, and buffer ledger events.
    """

    @classmethod
    def get_financial_story(
        cls,
        db: Session,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Builds the complete chronological timeline and milestone story.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"timeline_events": [], "milestones_count": 0, "story_summary": "User not found."}

        # 1. Fetch persistent financial events
        events = (
            db.query(FinancialEvent)
            .filter(FinancialEvent.user_id == user_id)
            .order_by(FinancialEvent.timestamp.desc())
            .limit(limit)
            .all()
        )

        # 2. Canonical demo story if demo user and events are sparse
        if user.is_demo_user and len(events) < 3:
            canonical_story = [
                {
                    "date": "Sep 01, 2026",
                    "type": "INCOME_SPIKE",
                    "title": "Platform Inflow Peak (+18%)",
                    "description": "Weekly gig earnings touched ₹8,400, providing ₹1,300 operational surplus.",
                    "severity": "POSITIVE",
                    "badge_color": "emerald",
                    "icon": "📈"
                },
                {
                    "date": "Sep 05, 2026",
                    "type": "BUFFER_CHANGED",
                    "title": "Smart Buffer Sweep Approved",
                    "description": "Transferred ₹900 (70% surplus safeguard) to Smart Buffer vault; ₹400 pocket cash preserved.",
                    "severity": "POSITIVE",
                    "badge_color": "emerald",
                    "icon": "🛡️"
                },
                {
                    "date": "Sep 10, 2026",
                    "type": "LIQUIDITY_GAP_DETECTED",
                    "title": "Intraday Timing Gap Hedged",
                    "description": "₹4,500 HDFC EV EMI debited at 09:00 AM; buffer vault absorbed ₹1,000 deficit until 06:00 PM payout cleared.",
                    "severity": "WARNING",
                    "badge_color": "amber",
                    "icon": "⚡"
                },
                {
                    "date": "Sep 15, 2026",
                    "type": "INCOME_CHANGED",
                    "title": "Income Decline Monitored",
                    "description": "Monsoon order dip slowed weekly earnings by 15%; defensive smoothing active.",
                    "severity": "INFO",
                    "badge_color": "stone",
                    "icon": "🌧️"
                },
                {
                    "date": "Sep 18, 2026",
                    "type": "BUFFER_CHANGED",
                    "title": "Sweeps Paused Automatically",
                    "description": "Zero surplus detected; automated savings paused to maintain 100% checking floor protection.",
                    "severity": "INFO",
                    "badge_color": "stone",
                    "icon": "⏸️"
                },
                {
                    "date": "Sep 22, 2026",
                    "type": "RECOVERY_DETECTED",
                    "title": "Income Recovery & Resilience Upgrade",
                    "description": "Order volumes rebounded; resilience score upgraded from 68 → 74.",
                    "severity": "POSITIVE",
                    "badge_color": "emerald",
                    "icon": "🎉"
                }
            ]
            return {
                "user_id": user_id,
                "story_title": "Your Financial Story — Arjun K.",
                "story_summary": "6 significant financial milestones logged. Smart Buffer successfully insulated 1 timing gap and preserved floor.",
                "milestones_count": len(canonical_story),
                "timeline_events": canonical_story,
                "active_state": "STABLE_WITH_ATTENTION"
            }

        # 3. Format real user events
        timeline = []
        for e in events:
            ev_type = e.event_type
            sev = e.severity or "INFO"
            
            # Choose icon
            if "SPIKE" in ev_type or "RECOVERY" in ev_type or "TARGET" in ev_type:
                icon = "📈" if "SPIKE" in ev_type else ("🎉" if "TARGET" in ev_type else "✨")
                badge = "emerald"
            elif "DROP" in ev_type or "GAP" in ev_type or "DEFICIT" in ev_type or sev == "CRITICAL":
                icon = "⚡" if "GAP" in ev_type else "⚠️"
                badge = "rose" if sev == "CRITICAL" else "amber"
            elif "BUFFER" in ev_type or "SWEEP" in ev_type:
                icon = "🛡️"
                badge = "tertiary"
            else:
                icon = "ℹ️"
                badge = "stone"

            d_str = e.timestamp.strftime("%b %d, %Y") if e.timestamp else "Recently"

            timeline.append({
                "id": e.id,
                "date": d_str,
                "type": e.event_type,
                "title": e.title,
                "description": e.description,
                "severity": sev,
                "badge_color": badge,
                "icon": icon,
                "metadata": getattr(e, "metadata_json", None)
            })

        summary = (
            f"{len(timeline)} milestone events recorded in your financial story. Continuous telemetry tracking is active."
            if timeline else
            "Your financial story is calibrating. Significant income shifts, buffer milestones, and obligation events will be logged here."
        )

        return {
            "user_id": user_id,
            "story_title": f"Your Financial Story — {user.name}",
            "story_summary": summary,
            "milestones_count": len(timeline),
            "timeline_events": timeline,
            "active_state": getattr(user, "behavior_profile", "STABLE")
        }
