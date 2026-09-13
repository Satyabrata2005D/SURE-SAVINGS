"""
SURE SAVINGS 4.0: Comprehensive Authentication, Session & Multi-Tenant Data Isolation Test Suite
Verifies:
- Google Identity token verification & claim extraction
- Idempotent user creation & profile initialization
- Cryptographic session generation, retrieval & expiration
- Logout invalidation
- Protected endpoint rejection without session (401 AUTH_REQUIRED)
- CRITICAL: Cross-user data isolation (User A vs User B)
- IDOR (Insecure Direct Object Reference) prevention
- AI Coach context isolation
- User-scoped audit traces
- Demo Mode sandbox isolation
"""
from starlette.testclient import TestClient
from datetime import datetime, timedelta, timezone
import json

from backend.main import app
from backend.database import SessionLocal
from backend.models import User, FinancialProfile, LedgerTransaction, Recommendation, UserSession
from backend.repository import FinancialRepository, seed_canonical_user
from backend.auth import GoogleAuthService

client = TestClient(app)

def test_01_google_token_verification_mock():
    claims = GoogleAuthService.verify_credential("mock_token_999888_rahul_verma")
    assert claims["google_subject_id"] == "g_sub_999888"
    assert claims["email"] == "rahul@gmail.com"
    assert "Rahul" in claims["name"]
    assert claims["email_verified"] is True
    print("[TEST 01] test_google_token_verification_mock ........................ PASS")

def test_02_google_token_verification_rejection():
    failed = False
    try:
        GoogleAuthService.verify_credential("")
    except Exception:
        failed = True
    assert failed, "Expected empty credential to raise exception"
    print("[TEST 02] test_google_token_verification_rejection .................... PASS")

def test_03_new_user_creation_and_workspace_initialization():
    with SessionLocal() as db:
        claims = {
            "google_subject_id": "g_sub_priya_01",
            "email": "priya.sharma@gmail.com",
            "email_verified": True,
            "name": "Priya Sharma",
            "given_name": "Priya",
            "family_name": "Sharma",
            "picture": "https://api.dicebear.com/7.x/initials/svg?seed=Priya",
            "locale": "en-IN"
        }
        user = FinancialRepository.create_or_update_google_user(db, claims)
        assert user.id is not None
        assert user.email == "priya.sharma@gmail.com"
        assert user.is_demo_user is False

        # Verify isolated workspace initialized
        prof = user.profile
        assert prof is not None
        assert prof.current_buffer == 0.0
        assert prof.buffer_target == 15000.0
        assert len(user.transactions) == 0
    print("[TEST 03] test_new_user_creation_and_workspace_initialization ......... PASS")

def test_04_existing_user_idempotent_login():
    with SessionLocal() as db:
        claims = {
            "google_subject_id": "g_sub_priya_01",
            "email": "priya.sharma@gmail.com",
            "name": "Priya Sharma Updated"
        }
        user = FinancialRepository.create_or_update_google_user(db, claims)
        # Should be the same user ID, not a duplicate
        users_with_sub = db.query(User).filter(User.google_subject_id == "g_sub_priya_01").all()
        assert len(users_with_sub) == 1
        assert users_with_sub[0].name == "Priya Sharma Updated"
    print("[TEST 04] test_existing_user_idempotent_login ......................... PASS")

def test_05_session_creation_and_retrieval():
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "priya.sharma@gmail.com").first()
        sess = FinancialRepository.create_session(db, user.id, expires_days=7)
        assert sess.session_token is not None
        assert sess.is_active is True
        assert sess.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)

        # Invalidate session
        ok = FinancialRepository.invalidate_session(db, sess.session_token)
        assert ok is True
        db.refresh(sess)
        assert sess.is_active is False
    print("[TEST 05] test_session_creation_and_retrieval ......................... PASS")

def test_06_unauthenticated_protected_route_rejection():
    # Make request with no cookies
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 401
    body = res.json()
    assert "error" in body
    assert body["error"]["code"] == "AUTH_REQUIRED"

    res_tx = client.get("/api/v1/transactions")
    assert res_tx.status_code == 401
    print("[TEST 06] test_unauthenticated_protected_route_rejection .............. PASS")

def test_07_canonical_demo_login_flow():
    # Ensure canonical demo user starts with clean baseline
    with SessionLocal() as db:
        seed_canonical_user(db, force=True)

    # Call demo login
    res = client.post("/api/v1/auth/demo")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["workspace_mode"] == "DEMO ENVIRONMENT"
    assert data["user"]["name"] == "Arjun K."

    # Verify session cookie was set
    assert "sure_savings_session" in res.cookies

    # Access protected dashboard with demo session
    dash_res = client.get("/api/v1/dashboard", cookies=res.cookies)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["workspace_mode"] == "DEMO ENVIRONMENT"
    assert dash_data["profile"]["name"] == "Arjun K."
    assert dash_data["profile"]["current_income"] == 8400.0
    assert dash_data["profile"]["current_buffer"] == 6800.0
    assert dash_data["profile"]["resilience_score"] == 74
    print("[TEST 07] test_canonical_demo_login_flow .............................. PASS")

def test_08_critical_cross_user_data_isolation():
    """
    CRITICAL MULTI-TENANCY TEST:
    Create User A (Alice, buffer ₹14,000, 2 private transactions)
    Create User B (Bob, buffer ₹3,000, 1 private transaction)
    Verify Alice cannot see Bob's data, and Bob cannot see Alice's data.
    """
    with SessionLocal() as db:
        # User A: Alice
        user_a = FinancialRepository.create_or_update_google_user(db, {
            "google_subject_id": "g_sub_alice_100",
            "email": "alice@fintech.test",
            "name": "Alice Developer"
        })
        user_a.profile.current_buffer = 14000.0
        user_a.profile.current_income = 12000.0
        tx_a1 = LedgerTransaction(
            user_id=user_a.id,
            date_str="Sep 03, 2026",
            source="Alice Private Inflow",
            direction="credit",
            amount=12000.0
        )
        db.add(tx_a1)

        # User B: Bob
        user_b = FinancialRepository.create_or_update_google_user(db, {
            "google_subject_id": "g_sub_bob_200",
            "email": "bob@fintech.test",
            "name": "Bob Freelancer"
        })
        user_b.profile.current_buffer = 3000.0
        user_b.profile.current_income = 5000.0
        tx_b1 = LedgerTransaction(
            user_id=user_b.id,
            date_str="Sep 03, 2026",
            source="Bob Secret Payout",
            direction="credit",
            amount=5000.0
        )
        db.add(tx_b1)
        db.commit()

        # Create sessions
        sess_a = FinancialRepository.create_session(db, user_a.id)
        sess_b = FinancialRepository.create_session(db, user_b.id)
        token_a = sess_a.session_token
        token_b = sess_b.session_token

    # 1. Query as Alice
    cookies_a = {"sure_savings_session": token_a}
    res_dash_a = client.get("/api/v1/dashboard", cookies=cookies_a)
    assert res_dash_a.status_code == 200
    body_a = res_dash_a.json()
    assert body_a["profile"]["name"] == "Alice Developer"
    assert body_a["profile"]["current_buffer"] == 14000.0

    res_tx_a = client.get("/api/v1/transactions", cookies=cookies_a)
    assert res_tx_a.status_code == 200
    tx_items_a = res_tx_a.json()["transactions"]
    assert any("Alice Private Inflow" in t["description"] for t in tx_items_a)
    assert not any("Bob Secret Payout" in t["description"] for t in tx_items_a)

    # 2. Query as Bob
    cookies_b = {"sure_savings_session": token_b}
    res_dash_b = client.get("/api/v1/dashboard", cookies=cookies_b)
    assert res_dash_b.status_code == 200
    body_b = res_dash_b.json()
    assert body_b["profile"]["name"] == "Bob Freelancer"
    assert body_b["profile"]["current_buffer"] == 3000.0

    res_tx_b = client.get("/api/v1/transactions", cookies=cookies_b)
    assert res_tx_b.status_code == 200
    tx_items_b = res_tx_b.json()["transactions"]
    assert any("Bob Secret Payout" in t["description"] for t in tx_items_b)
    assert not any("Alice Private Inflow" in t["description"] for t in tx_items_b)

    print("[TEST 08] test_critical_cross_user_data_isolation ................... PASS")

def test_09_idor_attack_prevention():
    """
    Verify that Alice cannot approve or withdraw on Bob's account
    by tampering with request payloads.
    """
    with SessionLocal() as db:
        user_a = db.query(User).filter(User.email == "alice@fintech.test").first()
        user_b = db.query(User).filter(User.email == "bob@fintech.test").first()
        sess_a = FinancialRepository.create_session(db, user_a.id)
        user_b_id = user_b.id
        token_a = sess_a.session_token

    cookies_a = {"sure_savings_session": token_a}

    # Attempt IDOR approval
    res = client.post(
        "/api/v1/recommendations/approve",
        json={"user_id": user_b_id, "idempotency_key": "hack_attempt"},
        cookies=cookies_a
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"

    # Attempt IDOR withdrawal
    res_w = client.post(
        "/api/v1/buffer/withdraw",
        json={"user_id": user_b_id, "amount": 1000.0},
        cookies=cookies_a
    )
    assert res_w.status_code == 403
    assert res_w.json()["error"]["code"] == "FORBIDDEN"
    print("[TEST 09] test_idor_attack_prevention ................................ PASS")

def test_10_ai_coach_context_isolation():
    """
    Verify that AI coach answers strictly ground in the authenticated user's telemetry.
    """
    with SessionLocal() as db:
        user_a = db.query(User).filter(User.email == "alice@fintech.test").first()
        sess_a = FinancialRepository.create_session(db, user_a.id)
        token_a = sess_a.session_token

    cookies_a = {"sure_savings_session": token_a}
    res = client.post(
        "/api/v1/ai/chat",
        json={"query": "What is my current buffer?"},
        cookies=cookies_a
    )
    assert res.status_code == 200
    answer = res.json().get("answer", "")
    assert "14,000" in answer or "14000" in answer
    # Must NOT mention Arjun's ₹6,800
    assert "6,800" not in answer and "6800" not in answer
    print("[TEST 10] test_ai_coach_context_isolation ............................ PASS")

def test_11_logout_invalidation_flow():
    """
    Verify that after logout, subsequent calls return 401.
    """
    # 1. Login via developer login
    res = client.post("/api/v1/auth/developer-login", json={"email": "logout.test@user.io", "name": "Logout Tester"})
    assert res.status_code == 200
    cookies = res.cookies

    # 2. Check dashboard works
    assert client.get("/api/v1/dashboard", cookies=cookies).status_code == 200

    # 3. Call logout
    logout_res = client.post("/api/v1/auth/logout", cookies=cookies)
    assert logout_res.status_code == 200

    # 4. Attempt accessing dashboard with old cookies
    post_logout_res = client.get("/api/v1/dashboard", cookies=cookies)
    assert post_logout_res.status_code == 401
    print("[TEST 11] test_logout_invalidation_flow ............................... PASS")

def test_12_audit_trace_user_scoping():
    """
    Verify that audit traces are saved and returned with the current user's ID.
    """
    with SessionLocal() as db:
        user_a = db.query(User).filter(User.email == "alice@fintech.test").first()
        sess_a = FinancialRepository.create_session(db, user_a.id)
        token_a = sess_a.session_token
        user_a_id = user_a.id

    cookies_a = {"sure_savings_session": token_a}
    res = client.get("/api/v1/engine/audit", cookies=cookies_a)
    assert res.status_code == 200
    audit_data = res.json()
    assert audit_data["user_id"] == user_a_id
    assert audit_data["verification_status"] == "PASS"
    print("[TEST 12] test_audit_trace_user_scoping ............................... PASS")

def test_13_email_otp_generation():
    """
    Test 13: Verify Email OTP generation and response contract.
    """
    res = client.post("/api/v1/auth/otp/send", json={"email": "satyabrata.test@gmail.com"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["email"] == "satyabrata.test@gmail.com"
    assert data["expires_in_minutes"] == 10
    assert "dev_otp" in data or "Verification code sent" in data["message"]
    print("[TEST 13] test_email_otp_generation ................................. PASS")

def test_14_email_otp_verification_failure():
    """
    Test 14: Verify that wrong OTP codes are rejected with 400 Bad Request.
    """
    res = client.post("/api/v1/auth/otp/verify", json={
        "email": "satyabrata.test@gmail.com",
        "otp": "999999"
    })
    assert res.status_code == 400
    err = res.json()["error"]
    assert err["code"] == "INVALID_OTP"
    print("[TEST 14] test_email_otp_verification_failure ....................... PASS")

def test_15_email_otp_successful_auth_and_workspace():
    """
    Test 15: Verify that correct OTP code provisions user, establishes session,
    and opens an isolated private workspace.
    """
    with SessionLocal() as db:
        _, code = FinancialRepository.create_email_otp(db, "satyabrata.test@gmail.com")

    res = client.post("/api/v1/auth/otp/verify", json={
        "email": "satyabrata.test@gmail.com",
        "otp": code
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["workspace_mode"] == "PRIVATE WORKSPACE"
    assert data["user"]["email"] == "satyabrata.test@gmail.com"
    assert "sure_savings_session" in res.cookies

    # Verify session can access private dashboard
    dash_res = client.get("/api/v1/dashboard", cookies={"sure_savings_session": res.cookies["sure_savings_session"]})
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["workspace_mode"] == "PRIVATE WORKSPACE"
    assert dash_data["profile"]["email"] == "satyabrata.test@gmail.com"

    # Verify OTP cannot be reused
    reuse_res = client.post("/api/v1/auth/otp/verify", json={
        "email": "satyabrata.test@gmail.com",
        "otp": code
    })
    assert reuse_res.status_code == 400
    print("[TEST 15] test_email_otp_successful_auth_and_workspace ............. PASS")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING COMPREHENSIVE AUTHENTICATION & MULTI-TENANT ISOLATION TESTS")
    print("="*80)
    test_01_google_token_verification_mock()
    test_02_google_token_verification_rejection()
    test_03_new_user_creation_and_workspace_initialization()
    test_04_existing_user_idempotent_login()
    test_05_session_creation_and_retrieval()
    test_06_unauthenticated_protected_route_rejection()
    test_07_canonical_demo_login_flow()
    test_08_critical_cross_user_data_isolation()
    test_09_idor_attack_prevention()
    test_10_ai_coach_context_isolation()
    test_11_logout_invalidation_flow()
    test_12_audit_trace_user_scoping()
    test_13_email_otp_generation()
    test_14_email_otp_verification_failure()
    test_15_email_otp_successful_auth_and_workspace()
    print("="*80)
    print("ALL 15 AUTHENTICATION, OTP & MULTI-TENANT USER ISOLATION TESTS PASSED!")
    print("="*80 + "\n")
