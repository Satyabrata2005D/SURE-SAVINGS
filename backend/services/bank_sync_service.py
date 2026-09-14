"""
SURE SAVINGS: Bank Sync Service (BankSyncService)
Coordinates the sync lifecycle: consent validation -> data session creation ->
data fetch -> normalization & recalculation -> audit completion.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

from backend.models import (
    BankConnection, BankConsent, BankDataSession, BankSyncRun, User
)
from backend.services.setu_aa_service import setu_aa_service
from backend.services.bank_recalculation_service import BankRecalculationService

logger = logging.getLogger("sure_savings.bank_sync")

def get_utc_now():
    return datetime.now(timezone.utc)

class BankSyncService:
    """
    Manages asynchronous and on-demand synchronization runs for connected bank accounts.
    """

    @staticmethod
    def execute_sync(
        db: Session,
        user_id: str,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Execute an end-to-end synchronization run for the given connection.
        """
        conn = db.query(BankConnection).filter(
            BankConnection.id == connection_id,
            BankConnection.user_id == user_id
        ).first()

        if not conn:
            return {"success": False, "error": "Bank connection not found"}

        if conn.status in ["DISCONNECTED", "CONSENT_REVOKED"]:
            return {
                "success": False,
                "error": "Cannot sync a disconnected or revoked bank connection. Please reconnect."
            }

        # 1. Fetch active consent
        consent = db.query(BankConsent).filter(
            BankConsent.bank_connection_id == conn.id,
            BankConsent.status == "ACTIVE"
        ).order_by(BankConsent.consent_created_at.desc()).first()

        # If not active in DB, check with Setu or pending consents
        if not consent:
            pending_consent = db.query(BankConsent).filter(
                BankConsent.bank_connection_id == conn.id,
                BankConsent.status == "PENDING"
            ).order_by(BankConsent.consent_created_at.desc()).first()

            if pending_consent:
                # Check status with Setu
                status_res = setu_aa_service.get_consent_status(pending_consent.consent_id)
                new_status = status_res.get("status", "PENDING")
                pending_consent.status = new_status
                pending_consent.consent_updated_at = get_utc_now()
                db.commit()

                if new_status == "ACTIVE":
                    consent = pending_consent
                else:
                    return {
                        "success": False,
                        "error": f"Bank consent is not active yet (current status: {new_status}). Please complete approval on the bank portal.",
                        "status": new_status,
                        "consent_url": pending_consent.consent_url
                    }
            else:
                return {
                    "success": False,
                    "error": "No active consent found for this bank account. Please reconnect.",
                    "status": "NEEDS_ATTENTION"
                }

        # 2. Initialize BankSyncRun
        sync_run = BankSyncRun(
            user_id=user_id,
            connection_id=conn.id,
            started_at=get_utc_now(),
            status="RUNNING"
        )
        db.add(sync_run)
        conn.status = "SYNCING"
        db.commit()
        db.refresh(sync_run)

        try:
            # 3. Create Data Session
            session_res = setu_aa_service.create_data_session(
                consent_id=consent.consent_id,
                data_range_from=consent.data_range_from,
                data_range_to=consent.data_range_to
            )

            if not session_res.get("success"):
                raise ValueError("Failed to initiate data session with provider")

            data_session_id = session_res["session_id"]
            bds = BankDataSession(
                user_id=user_id,
                bank_connection_id=conn.id,
                consent_id=consent.consent_id,
                data_session_id=data_session_id,
                status=session_res.get("status", "PENDING"),
                requested_from=consent.data_range_from,
                requested_to=consent.data_range_to,
                created_at=get_utc_now()
            )
            db.add(bds)
            db.commit()

            # 4. Fetch FI Data
            fetch_res = setu_aa_service.fetch_fi_data(data_session_id)
            if not fetch_res.get("success"):
                raise ValueError("Failed to retrieve financial data from provider session")

            bds.status = "COMPLETED"
            bds.completed_at = get_utc_now()
            db.commit()

            # 5. Normalize, Ingest, Recalculate
            fi_payload = fetch_res.get("Payload", [])
            result = BankRecalculationService.process_fi_data_and_recalculate(
                db=db,
                connection=conn,
                fi_payload=fi_payload,
                sync_run=sync_run
            )

            return result

        except Exception as e:
            logger.error(f"Bank sync failed for connection {conn.id}: {str(e)}", exc_info=True)
            sync_run.status = "FAILED"
            sync_run.completed_at = get_utc_now()
            sync_run.error_code = "SYNC_PROCESSING_ERROR"
            sync_run.safe_error_message = "Unable to process bank data. Please try again."
            conn.status = "ERROR"
            conn.error_code = "SYNC_FAILED"
            conn.error_message_safe = "Last sync encountered an issue. You can retry."
            db.commit()

            return {
                "success": False,
                "error": "Failed to complete bank synchronization. Please try again.",
                "connection_id": conn.id,
                "status": "ERROR"
            }

setu_sync_service = BankSyncService()
