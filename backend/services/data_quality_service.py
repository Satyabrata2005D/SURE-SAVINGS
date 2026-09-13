"""
SURE SAVINGS 7.0: Data Quality Engine
Evaluates completeness, validity, consistency, freshness, and duplication across
authoritative source records. Produces numerical score, status, issues, and warnings.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models import User, FinancialProfile, IncomeSource, ExpenseItem, LiquidityPosition, ScheduledObligation, WeeklyIncomeHistory, LedgerTransaction, Goal

class DataQualityIssue(dict):
    """Enriched data quality issue supporting both dict access (i['dimension']) and string representation."""
    def __init__(self, message: str, dimension: str = "general", severity: str = "warning"):
        super().__init__(message=message, dimension=dimension, severity=severity)

    def __str__(self):
        return self["message"]


class DataQualityService:
    """
    Authoritative Data Quality Engine for SURE SAVINGS 7.0.
    Evaluates evidence integrity without unnecessarily blocking regular users.
    """

    @classmethod
    def evaluate(cls, db: Session, user_id: str) -> Dict[str, Any]:
        db.expire_all()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "overall_score": 0.0,
                "quality_score": 0.0,
                "score": 0.0,
                "quality_status": "INSUFFICIENT_DATA",
                "issues": [DataQualityIssue("User workspace not found", "system", "critical")],
                "warnings": [],
                "dimensions": {
                    "completeness": {"score": 0, "raw": 0},
                    "validity": {"score": 0, "raw": 0},
                    "consistency": {"score": 0, "raw": 0},
                    "freshness": {"score": 0, "raw": 0},
                    "duplication": {"score": 0, "raw": 0}
                },
                "dimensions_breakdown": {
                    "completeness": 0,
                    "validity": 0,
                    "consistency": 0,
                    "freshness": 0,
                    "duplication": 0
                }
            }

        # Demo user canonical pass
        if getattr(user, "is_demo_user", False):
            return {
                "overall_score": 98.0,
                "quality_score": 98.0,
                "score": 98.0,
                "quality_status": "EXCELLENT",
                "issues": [],
                "warnings": ["Demonstration canonical dataset active."],
                "dimensions": {
                    "completeness": {"score": 100, "raw": 30},
                    "validity": {"score": 100, "raw": 25},
                    "consistency": {"score": 95, "raw": 19},
                    "freshness": {"score": 95, "raw": 14},
                    "duplication": {"score": 100, "raw": 10}
                },
                "dimensions_breakdown": {
                    "completeness": 100,
                    "validity": 100,
                    "consistency": 95,
                    "freshness": 95,
                    "duplication": 100
                }
            }

        issues: List[Any] = []
        warnings: List[str] = []

        # Gather source entities
        income_sources = user.income_sources or []
        expense_items = user.expense_items or []
        liq = user.liquidity_position
        history = user.weekly_history or []
        obligations = user.obligations or []
        goals = user.goals or []
        transactions = user.transactions or []

        # 1. COMPLETENESS (Weight: 30 pts)
        completeness_score = 0
        if income_sources:
            completeness_score += 7
        else:
            issues.append(DataQualityIssue("No active income source configured.", "income", "high"))
            warnings.append("No active income source configured.")

        if expense_items:
            completeness_score += 7
        else:
            issues.append(DataQualityIssue("No essential expenses tracked.", "expenses", "high"))
            warnings.append("No essential expenses tracked.")

        if liq and (liq.checking_cash > 0 or liq.savings_balance > 0):
            completeness_score += 6
        else:
            issues.append(DataQualityIssue("Liquidity position not calibrated.", "liquidity", "medium"))
            warnings.append("Liquidity position not calibrated.")

        if len(history) >= 2:
            completeness_score += 5
        elif len(history) == 1:
            completeness_score += 2
            warnings.append("Only 1 week of income history; 2+ weeks recommended for volatility analytics.")
        else:
            issues.append(DataQualityIssue("Income history is empty; automated forecasting requires historical weeks.", "history", "medium"))
            warnings.append("Income history is empty; automated forecasting requires at least 4 historical weeks.")

        if obligations:
            completeness_score += 5
        else:
            warnings.append("No upcoming obligations listed; cash-flow timeline cannot predict timing gaps.")

        completeness_pct = min(100, int((completeness_score / 30) * 100))

        # 2. VALIDITY (Weight: 25 pts)
        validity_score = 25
        # Check negative amounts
        for inc in income_sources:
            if inc.typical_amount < 0:
                validity_score -= 5
                issues.append(f"Income source '{inc.name}' has invalid negative amount.")
        for exp in expense_items:
            if exp.amount < 0:
                validity_score -= 5
                issues.append(f"Expense '{exp.description}' has invalid negative amount.")
        if liq:
            if liq.checking_cash < 0 or liq.savings_balance < 0 or liq.protected_floor < 0:
                validity_score -= 10
                issues.append("Negative cash balances or protected floor detected.")

        for obl in obligations:
            if obl.amount < 0:
                validity_score -= 5
                issues.append(f"Obligation '{obl.description}' has invalid negative amount.")

        validity_score = max(0, validity_score)
        validity_pct = int((validity_score / 25) * 100)

        # 3. CONSISTENCY (Weight: 20 pts)
        consistency_score = 20
        total_weekly_income = sum(
            s.typical_amount * (7 if s.frequency == "daily" else 1 if s.frequency == "weekly" else 0.5 if s.frequency == "biweekly" else 1/4.33 if s.frequency == "monthly" else 1)
            for s in income_sources if s.is_active
        )
        total_weekly_essential_burn = sum(
            e.amount * (7 if e.frequency == "daily" else 1 if e.frequency == "weekly" else 1/4.33 if e.frequency == "monthly" else 1/52 if e.frequency == "annual" else 1)
            for e in expense_items if e.is_active and e.is_essential
        )

        if income_sources and expense_items:
            if total_weekly_essential_burn > total_weekly_income * 1.5 and total_weekly_income > 0:
                consistency_score -= 8
                warnings.append(f"Essential expenses (₹{total_weekly_essential_burn:,.0f}/wk) exceed typical earnings (₹{total_weekly_income:,.0f}/wk) by over 50%.")

        if liq:
            if liq.protected_floor > (liq.checking_cash + liq.savings_balance) and (liq.checking_cash + liq.savings_balance) > 0:
                consistency_score -= 7
                warnings.append("Protected cash floor exceeds total accessible liquidity.")

        consistency_score = max(0, consistency_score)
        consistency_pct = int((consistency_score / 20) * 100)

        # 4. FRESHNESS (Weight: 15 pts)
        freshness_score = 15
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if user.updated_at:
            age_days = (now - user.updated_at).days
            if age_days > 45:
                freshness_score -= 8
                warnings.append("Financial data has not been updated in over 45 days.")
            elif age_days > 21:
                freshness_score -= 4
                warnings.append("Financial profile is over 3 weeks old.")
        freshness_pct = int((freshness_score / 15) * 100)

        # 5. DUPLICATION (Weight: 10 pts)
        duplication_score = 10
        # Check duplicate income source names
        inc_names = [s.name.strip().lower() for s in income_sources]
        if len(inc_names) != len(set(inc_names)):
            duplication_score -= 5
            warnings.append("Duplicate income source names identified.")

        # Check duplicate weeks in history
        hist_weeks = [h.week.strip().lower() for h in history]
        if len(hist_weeks) != len(set(hist_weeks)):
            duplication_score -= 5
            warnings.append("Duplicate weekly records identified in income history.")

        duplication_score = max(0, duplication_score)
        duplication_pct = int((duplication_score / 10) * 100)

        # TOTAL SCORE (0 to 100)
        total_score = round(completeness_score + validity_score + consistency_score + freshness_score + duplication_score, 1)

        # Gate total score if user has neither income nor expenses
        if not income_sources and not expense_items:
            total_score = round(completeness_score * 0.5, 1)
            status = "INSUFFICIENT_DATA"
        elif total_score >= 85:
            status = "EXCELLENT"
        elif total_score >= 65:
            status = "GOOD"
        elif total_score >= 40:
            status = "FAIR"
        else:
            status = "INSUFFICIENT_DATA"

        # Update user record
        user.data_quality_score = total_score
        user.data_quality_status = status
        db.commit()

        return {
            "overall_score": total_score,
            "quality_score": total_score,
            "score": total_score,
            "quality_status": status,
            "issues": issues,
            "warnings": warnings,
            "dimensions": {
                "completeness": {"score": completeness_pct, "raw": completeness_score},
                "validity": {"score": validity_pct, "raw": validity_score},
                "consistency": {"score": consistency_pct, "raw": consistency_score},
                "freshness": {"score": freshness_pct, "raw": freshness_score},
                "duplication": {"score": duplication_pct, "raw": duplication_score}
            },
            "dimensions_breakdown": {
                "completeness": completeness_pct,
                "validity": validity_pct,
                "consistency": consistency_pct,
                "freshness": freshness_pct,
                "duplication": duplication_pct
            }
        }
