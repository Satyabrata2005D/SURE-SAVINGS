"""
SURE SAVINGS 4.0: Automated Test Suite for Public Explorer, Input Bounds, & Security Boundary Isolation
Verifies:
1. Public endpoints are fully accessible without authentication (read-only).
2. Public endpoints reject client-supplied user identifiers (tamper resistance).
3. Public shock simulator is bounded, non-persistent, and never mutates database state.
4. Private endpoints strictly enforce 401 Unauthorized for unauthenticated requests.
5. Three-tier isolation: Public Visitor vs User A vs User B boundaries remain impermeable.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.database import get_db, SessionLocal
from backend.models import User, FinancialProfile, LedgerTransaction, AuditTrace
from backend.repository import seed_canonical_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


# =====================================================================
# 1. PUBLIC EXPLORER ENDPOINT TESTS (NO AUTH REQUIRED)
# =====================================================================

def test_public_overview_success_without_auth(client):
    """Verifies public visitors can view canonical model without credentials."""
    resp = client.get("/api/v1/public/demo/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["mode"] == "PUBLIC EXPLORER"
    assert data["is_public_demo"] is True
    assert data["persona"]["name"] == "Arjun K."
    assert data["metrics"]["current_income"] == 8400.0
    assert data["metrics"]["current_buffer"] == 6800.0
    assert data["metrics"]["resilience_score"] == 74
    assert data["metrics"]["recommended_contribution"] == 900.0


def test_public_income_history_success_without_auth(client):
    """Verifies public visitors can view 12-week income trends."""
    resp = client.get("/api/v1/public/demo/income")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["stabilized_baseline"] == 7100.0
    assert len(data["history"]) >= 12
    assert "insights" in data


def test_public_buffer_architecture_success_without_auth(client):
    """Verifies public buffer target, floor, and runway breakdown."""
    resp = client.get("/api/v1/public/demo/buffer")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["protected_floor"] == 3500.0
    assert data["target"] == 15000.0
    assert data["runway_weeks"] == 1.5
    assert len(data["pillars"]) == 3


def test_public_cash_flow_timing_gap_success_without_auth(client):
    """Verifies public intraday timing gap case study."""
    resp = client.get("/api/v1/public/demo/cash-flow")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "case_study" in data
    assert data["case_study"]["morning_debit"]["amount"] == 4500.0
    assert data["case_study"]["evening_credit"]["amount"] == 6900.0


# =====================================================================
# 2. PUBLIC SHOCK SIMULATOR TESTS & BOUNDS VALIDATION
# =====================================================================

def test_public_simulator_valid_shock_percentages(client):
    """Verifies public simulator calculates shocks deterministically."""
    for drop in [0.0, 10.0, 20.0, 40.0, 60.0]:
        resp = client.post("/api/v1/public/demo/simulate", json={
            "shock_percentage": drop,
            "scenario_preset": f"preset_{int(drop)}"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["simulation"]["drop_percentage"] == drop
        assert data["simulation"]["projected_weekly_income"] == round(8400.0 * (1 - drop / 100.0), 2)
        assert data["simulation"]["protected_floor"] == 3500.0
        assert "disclaimer" in data


def test_public_simulator_rejects_out_of_bounds(client):
    """Verifies strict Pydantic input bounds (rejects >90% or negative drops)."""
    # Over 90%
    resp = client.post("/api/v1/public/demo/simulate", json={"shock_percentage": 95.0})
    assert resp.status_code == 422

    # Negative drop
    resp = client.post("/api/v1/public/demo/simulate", json={"shock_percentage": -5.0})
    assert resp.status_code == 422


# =====================================================================
# 3. SECURITY TRAPS: PUBLIC ENDPOINTS REJECT USER_ID / SESSION_ID
# =====================================================================

def test_public_overview_rejects_user_id_tampering(client):
    """Verifies public overview rejects arbitrary user_id parameter."""
    resp = client.get("/api/v1/public/demo/overview?user_id=usr_attacker_01")
    assert resp.status_code == 400
    assert "Public demo endpoints are strictly immutable" in resp.json()["error"]["message"]


def test_public_overview_rejects_session_id_tampering(client):
    """Verifies public overview rejects arbitrary session_id parameter."""
    resp = client.get("/api/v1/public/demo/overview?session_id=sess_fake_token")
    assert resp.status_code == 400


def test_public_income_rejects_user_id_tampering(client):
    """Verifies public income rejects client-supplied user identifiers."""
    resp = client.get("/api/v1/public/demo/income?user_id=usr_attacker_01")
    assert resp.status_code == 400


def test_public_buffer_rejects_user_id_tampering(client):
    """Verifies public buffer rejects client-supplied user identifiers."""
    resp = client.get("/api/v1/public/demo/buffer?user_id=usr_attacker_01")
    assert resp.status_code == 400


def test_public_cash_flow_rejects_user_id_tampering(client):
    """Verifies public cash-flow rejects client-supplied user identifiers."""
    resp = client.get("/api/v1/public/demo/cash-flow?user_id=usr_attacker_01")
    assert resp.status_code == 400


# =====================================================================
# 4. DATABASE IMMUTABILITY VERIFICATION
# =====================================================================

def test_public_simulation_does_not_mutate_database(client, db):
    """Ensures repeated public simulations never insert or modify DB records."""
    user_count_before = db.query(User).count()
    tx_count_before = db.query(LedgerTransaction).count()
    audit_count_before = db.query(AuditTrace).count()

    # Execute 5 public simulations
    for drop in [10.0, 20.0, 30.0, 40.0, 50.0]:
        resp = client.post("/api/v1/public/demo/simulate", json={
            "shock_percentage": drop,
            "contribution_amount": 500.0,
            "withdrawal_amount": 200.0
        })
        assert resp.status_code == 200

    # Verify counts in DB are 100% unchanged
    assert db.query(User).count() == user_count_before
    assert db.query(LedgerTransaction).count() == tx_count_before
    assert db.query(AuditTrace).count() == audit_count_before


# =====================================================================
# 5. STRICT PRIVATE WORKSPACE PROTECTION (401 UNAUTHORIZED)
# =====================================================================

def test_private_endpoints_reject_unauthenticated_requests(client):
    """Ensures all private endpoints return 401 without an active session."""
    protected_endpoints = [
        ("GET", "/api/v1/dashboard"),
        ("GET", "/api/v1/income/analytics"),
        ("GET", "/api/v1/buffer"),
        ("GET", "/api/v1/cash-flow"),
        ("GET", "/api/v1/transactions"),
        ("GET", "/api/v1/engine/audit"),
        ("POST", "/api/v1/recommendations/approve"),
        ("POST", "/api/v1/buffer/withdraw")
    ]

    for method, path in protected_endpoints:
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json={})
        assert resp.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {resp.status_code}"


# =====================================================================
# 6. THREE-TIER ISOLATION: PUBLIC VISITOR VS USER A VS USER B
# =====================================================================

def test_three_tier_isolation(client):
    """
    Validates impermeable isolation:
    - Public visitor can only see canonical sample model.
    - User A (Alice) gets private session and cannot see User B's workspace.
    - User B (Bob) gets private session and cannot see User A's workspace.
    """
    # 1. Public visitor check
    pub_resp = client.get("/api/v1/public/demo/overview")
    assert pub_resp.status_code == 200
    assert pub_resp.json()["persona"]["name"] == "Arjun K."

    # 2. Alice signs in
    client_alice = TestClient(app)
    alice_login = client_alice.post("/api/v1/auth/developer-login", json={
        "email": "alice.isolated@example.com",
        "name": "Alice Developer"
    })
    assert alice_login.status_code == 200
    alice_user = alice_login.json()["user"]

    alice_overview = client_alice.get("/api/v1/dashboard")
    assert alice_overview.status_code == 200
    assert alice_overview.json()["profile"]["user_id"] == alice_user["id"]

    # 3. Bob signs in
    client_bob = TestClient(app)
    bob_login = client_bob.post("/api/v1/auth/developer-login", json={
        "email": "bob.isolated@example.com",
        "name": "Bob Freelancer"
    })
    assert bob_login.status_code == 200
    bob_user = bob_login.json()["user"]

    bob_overview = client_bob.get("/api/v1/dashboard")
    assert bob_overview.status_code == 200
    assert bob_overview.json()["profile"]["user_id"] == bob_user["id"]

    # Verify Alice != Bob
    assert alice_user["id"] != bob_user["id"]

    # 4. Attempt IDOR: Bob sends Alice's user_id in query params
    bob_attempt = client_bob.get(f"/api/v1/dashboard?user_id={alice_user['id']}")
    assert bob_attempt.status_code == 200
    # Server MUST strictly return Bob's data, ignoring query parameter!
    assert bob_attempt.json()["profile"]["user_id"] == bob_user["id"]
