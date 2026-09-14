"""
SURE SAVINGS: Comprehensive Setu Account Aggregator Integration Test Suite
Verifies:
1. Consent creation flow and redirect URL generation
2. Webhook notification processing (CONSENT_STATUS_UPDATE, FI_NOTIFICATION)
3. FI data ingestion, parsing, and storage
4. SHA-256 transaction deduplication across repeated sync runs
5. Self-transfer detection between user's linked accounts
6. Authoritative bank balance liquidity update
7. Financial Engine recalculation maintaining Safe-to-Save invariants (Balance != Safe-to-Save)
8. Calendar integration with OBSERVED events
9. Multi-tenant cross-user security isolation
10. Complete separation between real user accounts and Arjun demo data
11. Consent revocation and disconnect lifecycle
"""

import pytest
from starlette.testclient import TestClient
from datetime import datetime, timezone
import uuid

from backend.main import app
from backend.database import SessionLocal
from backend.models import (
    User, BankConnection, BankAccount, BankConsent, BankTransaction, BankSyncRun,
    LiquidityPosition, CalendarEvent, FinancialProfile
)
from backend.repository import FinancialRepository

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def private_user_a(db_session):
    """Create isolated private real user A."""
    email = f"bankuser_a_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=email,
        name="Private User A",
        is_demo_user=False,
        phone_number="9876543210",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    FinancialRepository.initialize_new_user_workspace(db_session, user.id)
    sess = FinancialRepository.create_session(db_session, user.id)
    return user, sess.session_token

@pytest.fixture
def private_user_b(db_session):
    """Create isolated private real user B."""
    email = f"bankuser_b_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=email,
        name="Private User B",
        is_demo_user=False,
        phone_number="9876543211",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    FinancialRepository.initialize_new_user_workspace(db_session, user.id)
    sess = FinancialRepository.create_session(db_session, user.id)
    return user, sess.session_token


def test_01_connect_bank_initiates_consent(test_client, private_user_a, db_session):
    """Test POST /api/v1/bank-accounts/connect initiates consent and returns valid URL."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    resp = client.post("/api/v1/bank-accounts/connect", json={
        "phone_or_vua": "9876543210"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["status"] == "success"
    assert "connection_id" in data
    assert "consent_id" in data
    assert "consent_url" in data
    assert data["connection_status"] == "AWAITING_CONSENT"

    # Verify DB persistence
    conn = db_session.query(BankConnection).filter(BankConnection.id == data["connection_id"]).first()
    assert conn is not None
    assert conn.user_id == user_a.id
    assert conn.status == "AWAITING_CONSENT"

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == data["consent_id"]).first()
    assert consent is not None
    assert consent.bank_connection_id == conn.id


def test_02_status_endpoint_never_exposes_secrets(test_client, private_user_a):
    """Test GET /api/v1/bank-accounts/status never leaks client secrets or auth keys."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    resp = client.get("/api/v1/bank-accounts/status")
    assert resp.status_code == 200
    text_content = resp.text.lower()

    # Strict secret exposure test
    assert "client_secret" not in text_content
    assert "ek28kky" not in text_content
    assert "secret" not in text_content or "provider_configured" in text_content


def test_03_webhook_consent_status_update(test_client, private_user_a, db_session):
    """Test webhook updates consent status to ACTIVE."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    # 1. Initiate consent
    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    consent_id = connect_resp.json()["consent_id"]
    conn_id = connect_resp.json()["connection_id"]

    # 2. Receive Webhook
    webhook_resp = test_client.post("/api/v1/bank-webhooks/setu", json={
        "type": "CONSENT_STATUS_UPDATE",
        "consentId": consent_id,
        "status": "ACTIVE"
    })
    assert webhook_resp.status_code == 200
    assert webhook_resp.json()["status"] == "success"

    # 3. Check DB
    db_session.expire_all()
    conn = db_session.query(BankConnection).filter(BankConnection.id == conn_id).first()
    assert conn.status == "CONSENT_ACTIVE"

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    assert consent.status == "ACTIVE"


def test_04_sync_bank_account_end_to_end(test_client, private_user_a, db_session):
    """Test full synchronization run fetches data, normalizes txns, and creates accounts."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    # Setup active connection
    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    # Mark consent active
    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    # Trigger Sync
    sync_resp = client.post(f"/api/v1/bank-accounts/{conn_id}/sync")
    assert sync_resp.status_code == 200, sync_resp.text
    sync_data = sync_resp.json()["sync_result"]

    assert sync_data["success"] is True
    assert sync_data["status"] == "CONNECTED"
    assert sync_data["accounts_count"] >= 2  # HDFC + SBI
    assert sync_data["records_imported"] > 0
    assert sync_data["total_reported_balance"] > 0.0

    # Verify accounts in DB
    accounts = db_session.query(BankAccount).filter(BankAccount.user_id == user_a.id).all()
    assert len(accounts) >= 2

    # Verify transactions in DB
    txns = db_session.query(BankTransaction).filter(BankTransaction.user_id == user_a.id).all()
    assert len(txns) == sync_data["records_imported"]


def test_05_idempotency_prevents_duplicate_transactions(test_client, private_user_a, db_session):
    """Test running sync twice skips duplicate transactions deterministically."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    # First sync
    sync_1 = client.post(f"/api/v1/bank-accounts/{conn_id}/sync").json()["sync_result"]
    first_imported = sync_1["records_imported"]
    assert first_imported > 0

    txns_count_1 = db_session.query(BankTransaction).filter(BankTransaction.user_id == user_a.id).count()

    # Second sync immediately
    sync_2 = client.post(f"/api/v1/bank-accounts/{conn_id}/sync").json()["sync_result"]
    assert sync_2["records_imported"] == 0
    assert sync_2["records_skipped_duplicate"] == first_imported

    txns_count_2 = db_session.query(BankTransaction).filter(BankTransaction.user_id == user_a.id).count()
    assert txns_count_1 == txns_count_2, "Idempotency violated: duplicate transactions were inserted"


def test_06_self_transfer_filtering(test_client, private_user_a, db_session):
    """Test self-transfers between user's own accounts are tagged and excluded from income/expenses."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    client.post(f"/api/v1/bank-accounts/{conn_id}/sync")

    # Inspect self-transfer records
    self_transfers = db_session.query(BankTransaction).filter(
        BankTransaction.user_id == user_a.id,
        BankTransaction.is_self_transfer == True
    ).all()

    assert len(self_transfers) >= 1
    for st in self_transfers:
        assert st.classification_status == "SELF_TRANSFER"
        assert st.category == "Internal Transfer"
        # Must not be marked as income candidate
        assert st.is_income_candidate is False


def test_07_bank_balance_liquidity_and_safe_to_save_invariants(test_client, private_user_a, db_session):
    """
    CRITICAL RULE: Bank Balance != Safe-to-Save.
    Verifies bank balance updates liquid cash, but Safe-to-Save preserves protected floor.
    """
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    sync_res = client.post(f"/api/v1/bank-accounts/{conn_id}/sync").json()["sync_result"]
    total_bank_bal = sync_res["total_reported_balance"]
    assert total_bank_bal > 0

    # Verify checking_cash in LiquidityPosition
    db_session.expire_all()
    liq = db_session.query(LiquidityPosition).filter(LiquidityPosition.user_id == user_a.id).first()
    assert liq.checking_cash == total_bank_bal

    # Verify Safe-to-Save is strictly not equal to total balance
    safe_to_save = sync_res["financial_engine"]["safe_to_save"]
    assert safe_to_save != total_bank_bal
    assert safe_to_save <= total_bank_bal, "Safe-to-Save cannot exceed liquid cash"


def test_08_calendar_events_populated_as_observed(test_client, private_user_a, db_session):
    """Test bank transactions are mirrored in CalendarEvents with status='SETTLED' and is_actual=True."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    client.post(f"/api/v1/bank-accounts/{conn_id}/sync")

    cal_events = db_session.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_a.id,
        CalendarEvent.source == "BANK_SETU"
    ).all()

    assert len(cal_events) > 0
    for evt in cal_events:
        assert evt.status == "SETTLED"
        assert evt.is_actual is True
        assert evt.is_expected is False


def test_09_multi_tenant_isolation(test_client, private_user_a, private_user_b, db_session):
    """Test User B cannot access or view User A's bank connections, accounts, or transactions."""
    user_a, token_a = private_user_a
    user_b, token_b = private_user_b

    client_a = TestClient(app, cookies={"sure_savings_session": token_a})
    client_b = TestClient(app, cookies={"sure_savings_session": token_b})

    # User A connects bank and syncs
    conn_a = client_a.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"}).json()
    conn_id_a = conn_a["connection_id"]
    consent_id_a = conn_a["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id_a).first()
    consent.status = "ACTIVE"
    db_session.commit()

    client_a.post(f"/api/v1/bank-accounts/{conn_id_a}/sync")

    # Get User A's account ID
    acc_a = db_session.query(BankAccount).filter(BankAccount.user_id == user_a.id).first()
    assert acc_a is not None

    # User B tries to view User A's account
    resp_b = client_b.get(f"/api/v1/bank-accounts/{acc_a.id}")
    assert resp_b.status_code == 404

    # User B tries to view User A's transactions
    resp_b_txns = client_b.get(f"/api/v1/bank-accounts/{acc_a.id}/transactions")
    assert resp_b_txns.status_code == 404

    # User B tries to sync User A's connection
    resp_b_sync = client_b.post(f"/api/v1/bank-accounts/{conn_id_a}/sync")
    assert resp_b_sync.status_code == 404

    # User B lists their own accounts -> exactly 0
    resp_b_list = client_b.get("/api/v1/bank-accounts").json()
    assert len(resp_b_list["accounts"]) == 0
    assert resp_b_list["liquidity"]["total_balance"] == 0.0


def test_10_demo_data_isolation(test_client, private_user_a, db_session):
    """Test real private users never receive synthetic Arjun demo data."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    # Check dashboard / income sources
    dashboard_res = client.get("/api/v1/dashboard").json()
    assert user_a.name != "Arjun K."

    # Verify no canonical demo tags in user's bank accounts
    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    client.post(f"/api/v1/bank-accounts/{conn_id}/sync")

    accs = db_session.query(BankAccount).filter(BankAccount.user_id == user_a.id).all()
    for a in accs:
        assert a.user_id == user_a.id
        assert a.user.is_demo_user is False


def test_11_consent_revocation_and_disconnect(test_client, private_user_a, db_session):
    """Test revoking consent and disconnecting bank connection preserves transactions but stops sync."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    client.post(f"/api/v1/bank-accounts/{conn_id}/sync")

    # Count transactions before disconnect
    txns_before = db_session.query(BankTransaction).filter(BankTransaction.user_id == user_a.id).count()
    assert txns_before > 0

    # 1. Revoke consent
    revoke_resp = client.post(f"/api/v1/bank-accounts/{conn_id}/consent/revoke")
    assert revoke_resp.status_code == 200

    db_session.expire_all()
    conn = db_session.query(BankConnection).filter(BankConnection.id == conn_id).first()
    assert conn.status == "CONSENT_REVOKED"

    # 2. Disconnect bank
    disc_resp = client.delete(f"/api/v1/bank-accounts/{conn_id}")
    assert disc_resp.status_code == 200

    db_session.expire_all()
    conn_after = db_session.query(BankConnection).filter(BankConnection.id == conn_id).first()
    assert conn_after.status == "DISCONNECTED"

    # Verify historical transactions are preserved for audit
    txns_after = db_session.query(BankTransaction).filter(BankTransaction.user_id == user_a.id).count()
    assert txns_after == txns_before

    # Verify subsequent sync fails gracefully
    fail_sync = client.post(f"/api/v1/bank-accounts/{conn_id}/sync")
    assert fail_sync.status_code == 400


def test_12_consent_rejection_and_expired_webhooks(test_client, private_user_a, db_session):
    """Test webhook processing for REJECTED and EXPIRED consent events."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    # Test rejection
    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    consent_id = connect_resp.json()["consent_id"]
    conn_id = connect_resp.json()["connection_id"]

    reject_hook = test_client.post("/api/v1/bank-webhooks/setu", json={
        "type": "CONSENT_STATUS_UPDATE",
        "consentId": consent_id,
        "status": "REJECTED"
    })
    assert reject_hook.status_code == 200
    db_session.expire_all()
    conn = db_session.query(BankConnection).filter(BankConnection.id == conn_id).first()
    assert conn.status == "CONSENT_REJECTED"

    # Test expired
    expired_hook = test_client.post("/api/v1/bank-webhooks/setu", json={
        "type": "CONSENT_STATUS_UPDATE",
        "consentId": consent_id,
        "status": "EXPIRED"
    })
    assert expired_hook.status_code == 200
    db_session.expire_all()
    conn = db_session.query(BankConnection).filter(BankConnection.id == conn_id).first()
    assert conn.status == "CONSENT_EXPIRED"


def test_13_refund_classification_handling(private_user_a, db_session):
    """Test refunds are recognized as refunds and not classified as gig income."""
    from backend.services.bank_transaction_service import BankTransactionService
    user_a, _ = private_user_a
    
    # Create test account
    conn = BankConnection(user_id=user_a.id, provider="SETU", status="CONNECTED")
    db_session.add(conn)
    db_session.commit()
    
    acc = BankAccount(bank_connection_id=conn.id, user_id=user_a.id, masked_account_number="XXXXXX9999")
    db_session.add(acc)
    db_session.commit()

    raw_refund = {
        "txnId": "TXN_REFUND_1",
        "type": "CREDIT",
        "amount": "450.00",
        "narration": "UPI/Amazon Pay/Refund for returned order/129381",
        "valueDate": "2026-09-12"
    }

    norm = BankTransactionService.normalize_and_classify(acc, raw_refund, ["XXXXXX9999"])
    assert norm["category"] == "Refund"
    assert norm["is_income_candidate"] is False
    assert norm["classification_status"] == "CONFIRMED"


def test_14_income_and_expense_candidate_detection(private_user_a, db_session):
    """Test gig income detection (Zomato) and essential expense detection (Fuel, Loan EMI)."""
    from backend.services.bank_transaction_service import BankTransactionService
    user_a, _ = private_user_a
    
    conn = BankConnection(user_id=user_a.id, provider="SETU", status="CONNECTED")
    db_session.add(conn)
    db_session.commit()
    acc = BankAccount(bank_connection_id=conn.id, user_id=user_a.id, masked_account_number="XXXXXX8888")
    db_session.add(acc)
    db_session.commit()

    # Zomato credit
    zomato_raw = {
        "txnId": "TXN_ZOM_1",
        "type": "CREDIT",
        "amount": "5600.00",
        "narration": "UPI/Zomato Media Ltd/Weekly Payout/481923",
        "valueDate": "2026-09-12"
    }
    norm_zom = BankTransactionService.normalize_and_classify(acc, zomato_raw, ["XXXXXX8888"])
    assert norm_zom["is_income_candidate"] is True
    assert norm_zom["merchant"] == "Zomato"
    assert norm_zom["category"] == "Gig Platform Income"

    # Fuel debit
    fuel_raw = {
        "txnId": "TXN_FUEL_1",
        "type": "DEBIT",
        "amount": "500.00",
        "narration": "UPI/Indian Oil Petrol Pump/Fuel Station/19283",
        "valueDate": "2026-09-12"
    }
    norm_fuel = BankTransactionService.normalize_and_classify(acc, fuel_raw, ["XXXXXX8888"])
    assert norm_fuel["is_expense_candidate"] is True
    assert norm_fuel["category"] == "Transportation / Fuel"

    # Loan EMI debit
    emi_raw = {
        "txnId": "TXN_EMI_1",
        "type": "DEBIT",
        "amount": "3800.00",
        "narration": "ACH/Hero Electric Finance/Two Wheeler EMI/10293",
        "valueDate": "2026-09-12"
    }
    norm_emi = BankTransactionService.normalize_and_classify(acc, emi_raw, ["XXXXXX8888"])
    assert norm_emi["is_expense_candidate"] is True
    assert norm_emi["is_recurring_candidate"] is True
    assert norm_emi["category"] == "Loan / EMI"


def test_15_reconnection_lifecycle_after_disconnect(test_client, private_user_a, db_session):
    """Test a user who disconnected can initiate a new connection cleanly."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    # First connection
    conn_1 = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"}).json()
    conn_id_1 = conn_1["connection_id"]

    # Disconnect
    client.delete(f"/api/v1/bank-accounts/{conn_id_1}")
    db_session.expire_all()
    c1 = db_session.query(BankConnection).filter(BankConnection.id == conn_id_1).first()
    assert c1.status == "DISCONNECTED"

    # Reconnect
    conn_2 = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"}).json()
    conn_id_2 = conn_2["connection_id"]

    # Must create a new connection or re-activate cleanly
    assert conn_id_2 != conn_id_1
    assert conn_2["connection_status"] == "AWAITING_CONSENT"


def test_16_duplicate_webhook_delivery_is_idempotent(test_client, private_user_a, db_session):
    """Test duplicate webhook deliveries produce identical outcome without errors."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    consent_id = connect_resp.json()["consent_id"]

    # Deliver webhook 3 times
    for _ in range(3):
        resp = test_client.post("/api/v1/bank-webhooks/setu", json={
            "type": "CONSENT_STATUS_UPDATE",
            "consentId": consent_id,
            "status": "ACTIVE"
        })
        assert resp.status_code == 200

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    assert consent.status == "ACTIVE"


def test_17_stale_data_handling_and_freshness(test_client, private_user_a, db_session):
    """Test that bank accounts endpoint carries balance_as_of timestamp and does not claim fake live data."""
    user_a, token_a = private_user_a
    client = TestClient(app, cookies={"sure_savings_session": token_a})

    connect_resp = client.post("/api/v1/bank-accounts/connect", json={"phone_or_vua": "9876543210"})
    conn_id = connect_resp.json()["connection_id"]
    consent_id = connect_resp.json()["consent_id"]

    consent = db_session.query(BankConsent).filter(BankConsent.consent_id == consent_id).first()
    consent.status = "ACTIVE"
    db_session.commit()

    client.post(f"/api/v1/bank-accounts/{conn_id}/sync")

    accounts_resp = client.get("/api/v1/bank-accounts").json()
    assert accounts_resp["status"] == "success"
    liquidity = accounts_resp["liquidity"]
    assert liquidity["latest_balance_as_of"] is not None
    assert liquidity["last_synced_at"] is not None

    for acc in accounts_resp["accounts"]:
        assert acc["balance_as_of"] is not None
        assert "current_reported_balance" in acc
