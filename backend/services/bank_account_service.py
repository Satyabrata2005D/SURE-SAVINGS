"""
SURE SAVINGS: Bank Account Service
Manages user-scoped BankConnection and BankAccount records, multi-bank aggregation,
consent lifecycle states, and tenant isolation invariants.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

from backend.models import (
    BankConnection, BankAccount, BankConsent, BankDataSession, BankTransaction, BankSyncRun, User
)

logger = logging.getLogger("sure_savings.bank_account")

def get_utc_now():
    return datetime.now(timezone.utc)

class BankAccountService:
    """
    User-scoped Bank Account & Connection Manager.
    Guarantees that no user can access another user's banking data.
    """

    @staticmethod
    def get_or_create_connection(
        db: Session,
        user_id: str,
        phone_or_vua: Optional[str] = None,
        provider: str = "SETU"
    ) -> BankConnection:
        """
        Retrieve existing active or pending connection for this user, or create a new one.
        """
        conn = db.query(BankConnection).filter(
            BankConnection.user_id == user_id,
            BankConnection.provider == provider,
            BankConnection.status.notin_(["DISCONNECTED", "CONSENT_REVOKED"])
        ).order_by(BankConnection.created_at.desc()).first()

        if not conn:
            conn = BankConnection(
                user_id=user_id,
                provider=provider,
                status="CONNECTING",
                phone_or_vua=phone_or_vua,
                created_at=get_utc_now(),
                updated_at=get_utc_now()
            )
            db.add(conn)
            db.commit()
            db.refresh(conn)
        else:
            if phone_or_vua and conn.phone_or_vua != phone_or_vua:
                conn.phone_or_vua = phone_or_vua
                conn.updated_at = get_utc_now()
                db.commit()
                db.refresh(conn)

        return conn

    @staticmethod
    def get_connection(db: Session, user_id: str, connection_id: str) -> Optional[BankConnection]:
        """User-scoped query ensuring zero cross-tenant access."""
        return db.query(BankConnection).filter(
            BankConnection.id == connection_id,
            BankConnection.user_id == user_id
        ).first()

    @staticmethod
    def get_connection_by_consent_id(db: Session, consent_id: str) -> Optional[BankConnection]:
        """Correlate incoming provider webhook/event by consent ID."""
        consent = db.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
        if consent:
            return db.query(BankConnection).filter(BankConnection.id == consent.bank_connection_id).first()
        return None

    @staticmethod
    def list_user_connections(db: Session, user_id: str) -> List[BankConnection]:
        """List all connections for the authenticated user."""
        return db.query(BankConnection).filter(
            BankConnection.user_id == user_id
        ).order_by(BankConnection.created_at.desc()).all()

    @staticmethod
    def list_user_bank_accounts(db: Session, user_id: str) -> List[BankAccount]:
        """List all linked accounts belonging to the authenticated user."""
        return db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.status == "ACTIVE"
        ).order_by(BankAccount.created_at.desc()).all()

    @staticmethod
    def get_user_bank_account(db: Session, user_id: str, account_id: str) -> Optional[BankAccount]:
        """Retrieve single user bank account with strict user_id scoping."""
        return db.query(BankAccount).filter(
            BankAccount.id == account_id,
            BankAccount.user_id == user_id
        ).first()

    @staticmethod
    def calculate_total_bank_liquidity(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Aggregate total liquid cash across all active connected accounts without double-counting.
        Carries provenance metadata: accounts count, latest reported timestamp, freshness.
        """
        accounts = db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.status == "ACTIVE"
        ).all()

        total_balance = sum(float(acc.current_reported_balance or 0.0) for acc in accounts)
        
        # Determine freshest balance timestamp
        latest_as_of = None
        for acc in accounts:
            if acc.balance_as_of:
                if latest_as_of is None or acc.balance_as_of > latest_as_of:
                    latest_as_of = acc.balance_as_of

        # Determine last successful connection sync
        latest_sync = None
        connections = db.query(BankConnection).filter(
            BankConnection.user_id == user_id,
            BankConnection.status.in_(["CONNECTED", "SYNCING", "PARTIALLY_AVAILABLE"])
        ).all()
        for conn in connections:
            if conn.last_successful_sync_at:
                if latest_sync is None or conn.last_successful_sync_at > latest_sync:
                    latest_sync = conn.last_successful_sync_at

        return {
            "total_balance": round(total_balance, 2),
            "accounts_count": len(accounts),
            "accounts": [acc.to_dict() for acc in accounts],
            "latest_balance_as_of": latest_as_of.isoformat() if latest_as_of else None,
            "last_synced_at": latest_sync.isoformat() if latest_sync else None,
            "has_connected_banks": len(accounts) > 0
        }

    @staticmethod
    def revoke_and_disconnect(
        db: Session,
        user_id: str,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Revoke active consent and transition connection to DISCONNECTED.
        Preserves historical transaction records for user audit trails.
        """
        conn = db.query(BankConnection).filter(
            BankConnection.id == connection_id,
            BankConnection.user_id == user_id
        ).first()

        if not conn:
            return {"success": False, "error": "Connection not found"}

        conn.status = "DISCONNECTED"
        conn.updated_at = get_utc_now()

        # Update associated consents to REVOKED
        consents = db.query(BankConsent).filter(
            BankConsent.bank_connection_id == connection_id
        ).all()
        for c in consents:
            c.status = "REVOKED"
            c.revoked_at = get_utc_now()
            c.consent_updated_at = get_utc_now()

        # Mark linked accounts as INACTIVE
        accounts = db.query(BankAccount).filter(
            BankAccount.bank_connection_id == connection_id
        ).all()
        for acc in accounts:
            acc.status = "INACTIVE"
            acc.updated_at = get_utc_now()

        db.commit()
        return {
            "success": True,
            "connection_id": connection_id,
            "status": "DISCONNECTED",
            "message": "Bank connection disconnected and consent revoked. Historical transactions preserved."
        }

    @staticmethod
    def delete_connection(
        db: Session,
        user_id: str,
        connection_id: str
    ) -> Dict[str, Any]:
        """Permanently remove connection and associated data."""
        conn = db.query(BankConnection).filter(
            BankConnection.id == connection_id,
            BankConnection.user_id == user_id
        ).first()

        if not conn:
            return {"success": False, "error": "Connection not found"}

        db.delete(conn)
        db.commit()
        return {"success": True, "message": "Bank connection removed successfully"}
