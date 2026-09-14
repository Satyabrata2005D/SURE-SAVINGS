"""
SURE SAVINGS: Bank Transaction Normalization & Ingestion Service
Handles transaction parsing, stable SHA-256 deduplication, category normalization,
self-transfer filtering, and candidate classification.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
import logging

from backend.models import BankAccount, BankTransaction, BankSyncRun

logger = logging.getLogger("sure_savings.bank_transaction")

def get_utc_now():
    return datetime.now(timezone.utc)

# Known Gig platforms and employers in India
GIG_PLATFORMS = {
    "zomato": "Zomato",
    "swiggy": "Swiggy",
    "blinkit": "Blinkit",
    "zepto": "Zepto",
    "uber": "Uber",
    "ola": "Ola",
    "rapido": "Rapido",
    "urban company": "Urban Company",
    "porter": "Porter",
    "shadowfax": "Shadowfax",
    "amazon": "Amazon Flex",
    "flipkart": "Flipkart Delivery"
}

# Expense keywords
EXPENSE_KEYWORDS = {
    "fuel": ["fuel", "petrol", "diesel", "indian oil", "hpcl", "bpcl", "shell", "cng"],
    "groceries": ["blinkit", "zepto", "bigbasket", "dmart", "d-mart", "supermarket", "grocery", "provision"],
    "emi": ["emi", "loan", "hero electric", "bajaj finance", "tvs credit", "chola", "ach debit", "hdb financial"],
    "rent": ["rent", "landlord", "house rent", "room rent"],
    "utilities": ["bescom", "tata power", "electricity", "airtel", "jio", "vodafone", "vi ", "water bill", "gas bill"],
    "dining": ["swiggy food", "zomato food", "restaurant", "cafe", "dhaba", "food court", "mcdonalds", "kfc"]
}

class BankTransactionService:
    """
    Normalizes bank transaction payloads, computes deduplication hashes,
    filters internal transfers, and classifies income vs expenses safely.
    """

    @staticmethod
    def generate_stable_hash(
        account_id: str,
        txn_date: str,
        amount: float,
        direction: str,
        reference: Optional[str],
        narration: Optional[str]
    ) -> str:
        """
        Produce a deterministic SHA-256 hash identifying this transaction.
        Used to prevent duplicate transaction records during repeated sync runs.
        """
        ref_norm = (reference or "").strip().lower()
        narr_norm = (narration or "").strip().lower()
        amt_norm = f"{float(amount):.2f}"
        dir_norm = direction.strip().lower()
        date_norm = txn_date.strip()

        raw_str = f"{account_id}|{date_norm}|{amt_norm}|{dir_norm}|{ref_norm}|{narr_norm}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    @staticmethod
    def normalize_and_classify(
        account: BankAccount,
        raw_txn: Dict[str, Any],
        user_account_numbers: List[str]
    ) -> Dict[str, Any]:
        """
        Normalize a single transaction from provider payload and classify its purpose.
        """
        # Direction
        raw_type = str(raw_txn.get("type", "DEBIT")).strip().upper()
        direction = "credit" if raw_type in ("CREDIT", "CR", "INFLOW") else "debit"

        # Amount
        try:
            amount = abs(float(raw_txn.get("amount", 0.0)))
        except (ValueError, TypeError):
            amount = 0.0

        # Reference & Narration
        reference = raw_txn.get("reference") or raw_txn.get("txnId") or ""
        narration = raw_txn.get("narration") or raw_txn.get("description") or ""
        narration_clean = narration.strip()
        narr_lower = narration_clean.lower()

        # Date parsing
        txn_timestamp_raw = raw_txn.get("transactionTimestamp") or raw_txn.get("valueDate")
        txn_date = raw_txn.get("valueDate") or raw_txn.get("transactionDate")
        txn_datetime = None

        if txn_timestamp_raw:
            try:
                # Handle ISO format
                ts_clean = txn_timestamp_raw.replace("Z", "+00:00")
                txn_datetime = datetime.fromisoformat(ts_clean)
                if not txn_date:
                    txn_date = txn_datetime.strftime("%Y-%m-%d")
            except Exception:
                pass

        if not txn_date:
            txn_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Stable hash
        stable_hash = BankTransactionService.generate_stable_hash(
            account_id=account.id,
            txn_date=txn_date,
            amount=amount,
            direction=direction,
            reference=reference,
            narration=narration_clean
        )

        # Balance after
        balance_after = None
        if "currentBalance" in raw_txn:
            try:
                balance_after = float(raw_txn["currentBalance"])
            except (ValueError, TypeError):
                pass

        # 1. Self-transfer detection
        is_self_transfer = False
        if "self" in narr_lower or "own account" in narr_lower:
            is_self_transfer = True
        for acc_num in user_account_numbers:
            # Check last 4 digits
            last_4 = acc_num[-4:] if len(acc_num) >= 4 else acc_num
            if last_4 and (last_4 in narr_lower or f"xxxx{last_4}" in narr_lower):
                # Only if it references another account, not the current one
                curr_last_4 = account.masked_account_number[-4:] if account.masked_account_number else ""
                if last_4 != curr_last_4:
                    is_self_transfer = True
                    break

        # 2. Refund detection
        is_refund = False
        if any(kw in narr_lower for kw in ["refund", "reversal", "cashback", "returned"]):
            is_refund = True

        # 3. ATM Withdrawal detection
        is_atm = "atm" in narr_lower or "cash wdl" in narr_lower or "nfs cash" in narr_lower

        # Category and candidate classification
        category = "General"
        subcategory = None
        merchant = None
        is_income_candidate = False
        is_expense_candidate = False
        is_recurring_candidate = False
        confidence_score = 0.5
        classification_status = "UNCLASSIFIED"

        if is_self_transfer:
            classification_status = "SELF_TRANSFER"
            category = "Internal Transfer"
            confidence_score = 0.95
        elif direction == "credit":
            if is_refund:
                category = "Refund"
                classification_status = "CONFIRMED"
                confidence_score = 0.90
            else:
                # Check for Gig Platforms
                matched_gig = None
                for kw, name in GIG_PLATFORMS.items():
                    if kw in narr_lower:
                        matched_gig = name
                        break

                if matched_gig:
                    merchant = matched_gig
                    category = "Gig Platform Income"
                    subcategory = matched_gig
                    is_income_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.95
                elif "salary" in narr_lower or "payroll" in narr_lower:
                    category = "Salary"
                    is_income_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.95
                elif amount > 500:
                    category = "Incoming Transfer"
                    is_income_candidate = True
                    classification_status = "LIKELY"
                    confidence_score = 0.70
                else:
                    category = "General Credit"
                    classification_status = "UNCERTAIN"
                    confidence_score = 0.50
        else:
            # Debit classification
            if is_atm:
                category = "Cash Withdrawal"
                classification_status = "LIKELY"
                confidence_score = 0.85
            else:
                matched_cat = None
                for cat, keywords in EXPENSE_KEYWORDS.items():
                    if any(kw in narr_lower for kw in keywords):
                        matched_cat = cat
                        break

                if matched_cat == "emi":
                    category = "Loan / EMI"
                    is_expense_candidate = True
                    is_recurring_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.95
                elif matched_cat == "rent":
                    category = "Housing / Rent"
                    is_expense_candidate = True
                    is_recurring_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.95
                elif matched_cat == "fuel":
                    category = "Transportation / Fuel"
                    is_expense_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.90
                elif matched_cat == "groceries":
                    category = "Groceries & Supplies"
                    is_expense_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.90
                elif matched_cat == "utilities":
                    category = "Utilities"
                    is_expense_candidate = True
                    is_recurring_candidate = True
                    classification_status = "CONFIRMED"
                    confidence_score = 0.85
                elif matched_cat == "dining":
                    category = "Food & Dining"
                    is_expense_candidate = True
                    classification_status = "LIKELY"
                    confidence_score = 0.80
                else:
                    category = "General Expense"
                    is_expense_candidate = True
                    classification_status = "LIKELY"
                    confidence_score = 0.65

        return {
            "external_transaction_id_or_stable_hash": stable_hash,
            "transaction_date": txn_date,
            "transaction_timestamp": txn_datetime,
            "amount": amount,
            "direction": direction,
            "description": narration_clean,
            "merchant": merchant,
            "category": category,
            "subcategory": subcategory,
            "currency": account.currency or "INR",
            "reference": reference,
            "balance_after_if_available": balance_after,
            "source": "BANK_SETU",
            "classification_status": classification_status,
            "is_income_candidate": is_income_candidate,
            "is_expense_candidate": is_expense_candidate,
            "is_recurring_candidate": is_recurring_candidate,
            "is_self_transfer": is_self_transfer,
            "confidence_score": confidence_score
        }

    @staticmethod
    def ingest_account_transactions(
        db: Session,
        account: BankAccount,
        raw_transactions: List[Dict[str, Any]],
        user_account_numbers: List[str]
    ) -> Tuple[int, int, int]:
        """
        Ingest normalized transactions for a bank account with deduplication.
        Returns: (records_received, records_imported, records_skipped_duplicate)
        """
        received = len(raw_transactions)
        imported = 0
        skipped = 0

        # Fetch existing stable hashes for this account to optimize check
        existing_hashes = set(
            h[0] for h in db.query(BankTransaction.external_transaction_id_or_stable_hash).filter(
                BankTransaction.bank_account_id == account.id
            ).all()
        )

        for raw in raw_transactions:
            normalized = BankTransactionService.normalize_and_classify(
                account=account,
                raw_txn=raw,
                user_account_numbers=user_account_numbers
            )
            stable_hash = normalized["external_transaction_id_or_stable_hash"]

            if stable_hash in existing_hashes:
                skipped += 1
                continue

            btx = BankTransaction(
                user_id=account.user_id,
                bank_account_id=account.id,
                external_transaction_id_or_stable_hash=stable_hash,
                transaction_date=normalized["transaction_date"],
                transaction_timestamp=normalized["transaction_timestamp"],
                amount=normalized["amount"],
                direction=normalized["direction"],
                description=normalized["description"],
                merchant=normalized["merchant"],
                category=normalized["category"],
                subcategory=normalized["subcategory"],
                currency=normalized["currency"],
                reference=normalized["reference"],
                balance_after_if_available=normalized["balance_after_if_available"],
                source=normalized["source"],
                classification_status=normalized["classification_status"],
                is_income_candidate=normalized["is_income_candidate"],
                is_expense_candidate=normalized["is_expense_candidate"],
                is_recurring_candidate=normalized["is_recurring_candidate"],
                is_self_transfer=normalized["is_self_transfer"],
                confidence_score=normalized["confidence_score"],
                imported_at=get_utc_now(),
                updated_at=get_utc_now()
            )
            db.add(btx)
            existing_hashes.add(stable_hash)
            imported += 1

        db.commit()
        return received, imported, skipped
