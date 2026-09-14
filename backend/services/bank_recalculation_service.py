"""
SURE SAVINGS: Central Bank Recalculation Service (BankRecalculationService)
Orchestrates:
1. Ingestion of raw FI data into BankAccount and BankTransaction records
2. Update of authoritative bank liquidity position
3. Synchronization with Financial Calendar (OBSERVED transactions)
4. Triggering deterministic FinancialEngine recalculation
5. Audit trail generation and BankSyncRun completion
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json
import logging

from backend.models import (
    User, BankConnection, BankAccount, BankTransaction, BankSyncRun,
    LiquidityPosition, CalendarEvent, FinancialEvent
)
from backend.services.bank_transaction_service import BankTransactionService
from backend.services.bank_reconciliation_service import BankReconciliationService
from backend.services.bank_account_service import BankAccountService
from backend.financial_engine import FinancialEngine

logger = logging.getLogger("sure_savings.bank_recalculation")

def get_utc_now():
    return datetime.now(timezone.utc)

class BankRecalculationService:
    """
    Central pipeline orchestrating bank data ingestion, liquidity updates,
    and financial engine recalculation.
    """

    @staticmethod
    def process_fi_data_and_recalculate(
        db: Session,
        connection: BankConnection,
        fi_payload: List[Dict[str, Any]],
        sync_run: Optional[BankSyncRun] = None
    ) -> Dict[str, Any]:
        """
        Process bank payload, ingest accounts and transactions, update liquidity,
        sync calendar, and trigger authoritative financial engine recalculation.
        """
        user_id = connection.user_id
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        total_records_received = 0
        total_records_imported = 0
        total_records_skipped = 0
        accounts_updated = []

        # 1. First pass: Collect all masked account numbers for this user to assist self-transfer detection
        existing_accounts = db.query(BankAccount).filter(
            BankAccount.user_id == user_id
        ).all()
        user_account_numbers = [acc.masked_account_number for acc in existing_accounts if acc.masked_account_number]

        # Scan incoming payload for new account numbers
        for fip_item in fi_payload:
            for item in fip_item.get("data", []):
                acc_data = item.get("account", {})
                acc_num = acc_data.get("maskedAccNumber")
                if acc_num and acc_num not in user_account_numbers:
                    user_account_numbers.append(acc_num)

        # 2. Ingest accounts and their transactions
        for fip_item in fi_payload:
            fip_id = fip_item.get("fipId", "SETU_FIP")
            for item in fip_item.get("data", []):
                acc_data = item.get("account", {})
                masked_acc = acc_data.get("maskedAccNumber", "XXXXXX0000")
                inst_name = acc_data.get("institutionName") or ("HDFC Bank" if "HDFC" in fip_id else "State Bank of India" if "SBI" in fip_id else "Bank")
                summary = acc_data.get("summary", {})
                
                # Balance extraction
                current_bal = float(summary.get("currentBalance", 0.0))
                avail_bal = float(summary.get("availableBalance", current_bal)) if summary.get("availableBalance") else current_bal
                bal_dt_str = summary.get("balanceDateTime")
                bal_dt = None
                if bal_dt_str:
                    try:
                        bal_dt = datetime.fromisoformat(bal_dt_str.replace("Z", "+00:00"))
                    except Exception:
                        bal_dt = get_utc_now()
                else:
                    bal_dt = get_utc_now()

                acc_type = str(summary.get("type", "SAVINGS")).upper()

                # Find or create BankAccount record
                bank_acc = db.query(BankAccount).filter(
                    BankAccount.bank_connection_id == connection.id,
                    BankAccount.masked_account_number == masked_acc
                ).first()

                if not bank_acc:
                    bank_acc = BankAccount(
                        bank_connection_id=connection.id,
                        user_id=user_id,
                        fip_id=fip_id,
                        institution_name=inst_name,
                        masked_account_number=masked_acc,
                        account_type=acc_type,
                        currency=summary.get("currency", "INR"),
                        current_reported_balance=current_bal,
                        available_reported_balance_if_supported=avail_bal,
                        balance_as_of=bal_dt,
                        status="ACTIVE",
                        created_at=get_utc_now(),
                        updated_at=get_utc_now()
                    )
                    db.add(bank_acc)
                    db.commit()
                    db.refresh(bank_acc)
                else:
                    bank_acc.current_reported_balance = current_bal
                    bank_acc.available_reported_balance_if_supported = avail_bal
                    bank_acc.balance_as_of = bal_dt
                    bank_acc.status = "ACTIVE"
                    bank_acc.institution_name = inst_name
                    bank_acc.updated_at = get_utc_now()
                    db.commit()
                    db.refresh(bank_acc)

                accounts_updated.append(bank_acc)

                # Ingest transactions
                raw_txns = acc_data.get("transactions", {}).get("transaction", [])
                rcvd, imp, skip = BankTransactionService.ingest_account_transactions(
                    db=db,
                    account=bank_acc,
                    raw_transactions=raw_txns,
                    user_account_numbers=user_account_numbers
                )
                total_records_received += rcvd
                total_records_imported += imp
                total_records_skipped += skip

        # 3. Update LiquidityPosition from Authoritative Bank Balances
        # Sum balances across all active bank accounts for this user
        liquidity_data = BankAccountService.calculate_total_bank_liquidity(db, user_id)
        total_bank_balance = liquidity_data["total_balance"]

        liq_pos = user.liquidity_position
        if not liq_pos:
            liq_pos = LiquidityPosition(
                user_id=user_id,
                checking_cash=total_bank_balance,
                savings_cash=0.0,
                emergency_cash=0.0,
                investments_liquid=0.0,
                created_at=get_utc_now(),
                updated_at=get_utc_now()
            )
            db.add(liq_pos)
        else:
            liq_pos.checking_cash = total_bank_balance
            liq_pos.updated_at = get_utc_now()

        # Increment source_data_version on user
        user.source_data_version = (user.source_data_version or 1) + 1
        db.commit()

        # 4. Reconcile Income Sources and Obligations
        BankReconciliationService.reconcile_income_sources(db, user_id)
        BankReconciliationService.reconcile_recurring_obligations(db, user_id)

        # 5. Enrich Financial Calendar with OBSERVED bank transactions
        new_imported_txns = db.query(BankTransaction).filter(
            BankTransaction.user_id == user_id,
            BankTransaction.is_self_transfer == False
        ).order_by(BankTransaction.transaction_date.desc()).limit(50).all()

        for btx in new_imported_txns:
            # Check if event exists
            event_id = f"evt_bank_{btx.id}"
            existing_event = db.query(CalendarEvent).filter(
                CalendarEvent.id == event_id
            ).first()

            if not existing_event:
                is_credit = (btx.direction == "credit")
                cal_event = CalendarEvent(
                    id=event_id,
                    user_id=user_id,
                    date_str=btx.transaction_date,
                    time_str="12:00 PM",
                    title=btx.description[:64] if btx.description else ("Bank Credit" if is_credit else "Bank Debit"),
                    description=f"{btx.category} • Ref: {btx.reference or 'N/A'}",
                    event_type="inflow" if is_credit else "outflow",
                    direction=btx.direction,
                    amount=btx.amount,
                    source="BANK_SETU",
                    category=btx.category or "General",
                    status="SETTLED",
                    is_actual=True,
                    is_expected=False,
                    notes=f"btx:{btx.id}",
                    created_at=get_utc_now(),
                    updated_at=get_utc_now()
                )
                db.add(cal_event)

        db.commit()

        # 6. Recalculate Deterministic Financial Engine
        # Note: Bank Balance updates checking_cash above floor, but Safe-to-Save
        # is strictly calculated through FinancialEngine respecting all safety rules.
        twin_result = FinancialEngine.recalculate_user_workspace(db, user_id)

        # 7. Record Financial Telemetry Event
        fin_event = FinancialEvent(
            user_id=user_id,
            event_type="BANK_SYNC_COMPLETED",
            severity="INFO",
            title="Bank Synchronization Completed",
            description=f"Synchronized {len(accounts_updated)} accounts and processed {total_records_imported} new transactions.",
            source="SETU_AA",
            timestamp=get_utc_now()
        )
        db.add(fin_event)

        # 8. Update Connection & SyncRun Status
        connection.status = "CONNECTED"
        connection.last_sync_at = get_utc_now()
        connection.last_successful_sync_at = get_utc_now()
        connection.error_code = None
        connection.error_message_safe = None
        connection.updated_at = get_utc_now()

        if sync_run:
            sync_run.status = "SUCCESS"
            sync_run.completed_at = get_utc_now()
            sync_run.records_received = total_records_received
            sync_run.records_imported = total_records_imported
            sync_run.records_skipped_duplicate = total_records_skipped
            sync_run.records_updated = len(accounts_updated)

        db.commit()

        return {
            "success": True,
            "connection_id": connection.id,
            "status": "CONNECTED",
            "accounts_count": len(accounts_updated),
            "records_received": total_records_received,
            "records_imported": total_records_imported,
            "records_skipped_duplicate": total_records_skipped,
            "total_reported_balance": total_bank_balance,
            "last_synced_at": connection.last_successful_sync_at.isoformat(),
            "financial_engine": {
                "safe_to_save": twin_result.get("safe_to_save", {}).get("recommended_amount", 0.0),
                "buffer_status": twin_result.get("smart_buffer", {}).get("status", "BUILDING"),
                "weekly_income": twin_result.get("income_intelligence", {}).get("baseline", 0.0),
                "weekly_expenses": twin_result.get("expense_intelligence", {}).get("essential_burn", 0.0),
                "resilience_score": twin_result.get("health_resilience", {}).get("score", 70)
            }
        }
