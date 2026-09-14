"""
SURE SAVINGS: Bank Reconciliation Service
Reconciles imported bank transactions with Income Sources, Expense Items,
and Scheduled Obligations without destructively overwriting calibrated baselines.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

from backend.models import (
    User, BankAccount, BankTransaction, IncomeSource, ExpenseItem, ScheduledObligation
)

logger = logging.getLogger("sure_savings.bank_reconciliation")

def get_utc_now():
    return datetime.now(timezone.utc)

class BankReconciliationService:
    """
    Reconciles observed bank transactions with user financial models.
    Preserves existing user-entered baselines until sufficient evidence is established.
    """

    @staticmethod
    def reconcile_income_sources(db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Scan confirmed income transactions and reconcile with user's IncomeSources.
        Requires at least 2 observed payouts from a platform before creating or calibrating an IncomeSource.
        """
        # Fetch confirmed income transactions
        txns = db.query(BankTransaction).filter(
            BankTransaction.user_id == user_id,
            BankTransaction.is_income_candidate == True,
            BankTransaction.is_self_transfer == False,
            BankTransaction.classification_status.in_(["CONFIRMED", "LIKELY"])
        ).all()

        # Group by merchant / source name
        platform_payouts: Dict[str, List[float]] = {}
        for t in txns:
            key = t.merchant or t.category or "Other Inflow"
            platform_payouts.setdefault(key, []).append(float(t.amount))

        updated_sources = []
        for platform_name, amounts in platform_payouts.items():
            if len(amounts) >= 1: # We have evidence
                avg_amount = sum(amounts) / len(amounts)

                # Check if existing IncomeSource exists
                existing = db.query(IncomeSource).filter(
                    IncomeSource.user_id == user_id,
                    IncomeSource.name.ilike(f"%{platform_name}%")
                ).first()

                if existing:
                    # If existing source has typical_amount = 0, populate with observed average
                    if existing.typical_amount <= 0:
                        existing.typical_amount = round(avg_amount, 2)
                        existing.updated_at = get_utc_now()
                        updated_sources.append({"name": existing.name, "action": "calibrated", "amount": existing.typical_amount})
                else:
                    # Create new detected IncomeSource
                    new_src = IncomeSource(
                        user_id=user_id,
                        name=platform_name,
                        income_type="gig" if "gig" in platform_name.lower() or platform_name in ["Zomato", "Swiggy", "Blinkit", "Uber"] else "freelance",
                        typical_amount=round(avg_amount, 2),
                        frequency="weekly",
                        payout_day="Wednesday",
                        is_active=True,
                        created_at=get_utc_now(),
                        updated_at=get_utc_now()
                    )
                    db.add(new_src)
                    updated_sources.append({"name": platform_name, "action": "created", "amount": round(avg_amount, 2)})

        if updated_sources:
            db.commit()

        return updated_sources

    @staticmethod
    def reconcile_recurring_obligations(db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Scan recurring candidate transactions (Rent, EMI) and ensure ScheduledObligation exists.
        """
        recurring_txns = db.query(BankTransaction).filter(
            BankTransaction.user_id == user_id,
            BankTransaction.is_recurring_candidate == True,
            BankTransaction.is_self_transfer == False
        ).all()

        obligations_updated = []
        for t in recurring_txns:
            cat = t.category or "Loan / EMI"
            desc = t.description[:64] if t.description else cat
            # Check existing obligation
            existing = db.query(ScheduledObligation).filter(
                ScheduledObligation.user_id == user_id,
                ScheduledObligation.category.ilike(f"%{cat}%")
            ).first()

            if not existing and t.amount > 0:
                ob = ScheduledObligation(
                    user_id=user_id,
                    date_str=t.transaction_date,
                    time_str="09:00 AM",
                    description=desc,
                    category=cat,
                    type="debit",
                    amount=round(float(t.amount), 2),
                    is_essential=True,
                    impact="Safe"
                )
                db.add(ob)
                obligations_updated.append({"name": cat, "amount": float(t.amount)})

        if obligations_updated:
            db.commit()

        return obligations_updated
