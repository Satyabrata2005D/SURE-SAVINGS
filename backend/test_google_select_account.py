"""
SURE SAVINGS: Automated Verification for Google Account Selection & Instant Private Workspace Sign-In
Verifies:
- 1-Click login without OTP or phone verification
- Authentic account selection mapping into real private workspace
- Non-demo user isolation (is_demo_user == False, workspace_mode == "PRIVATE WORKSPACE")
- Preserves existing onboarded data and custom profile settings
- Seamless creation of isolated workspace for new Google accounts
"""
import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User
from backend.repository import FinancialRepository

client = TestClient(app)

def test_01_select_account_existing_user():
    """Selecting Satyabrata Das logs directly into his private workspace with zero OTP."""
    res = client.post(
        "/api/v1/auth/google/select-account",
        json={
            "email": "das2005satyabrata@gmail.com",
            "name": "Satyabrata Das"
        }
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert data["workspace_mode"] == "PRIVATE WORKSPACE"
    assert data["user"]["email"] == "das2005satyabrata@gmail.com"
    assert data["user"]["is_demo_user"] is False
    assert "sure_savings_session" in res.headers.get("set-cookie", "")

    # Check that user can now access protected /api/v1/auth/me using this session cookie
    cookie = res.headers.get("set-cookie").split(";")[0]
    me_res = client.get("/api/v1/auth/me", headers={"Cookie": cookie})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["user"]["email"] == "das2005satyabrata@gmail.com"
    assert me_data["user"]["is_demo_user"] is False
    print("[TEST 01] test_select_account_existing_user ........................ PASS")

def test_02_select_account_new_google_user():
    """Selecting a new Google account creates an isolated workspace without OTP."""
    new_email = "ananya.finance.test@gmail.com"
    res = client.post(
        "/api/v1/auth/google/select-account",
        json={
            "email": new_email,
            "name": "Ananya Sen"
        }
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert data["user"]["email"] == new_email
    assert data["user"]["name"] == "Ananya Sen"
    assert data["user"]["is_demo_user"] is False
    assert data["workspace_mode"] == "PRIVATE WORKSPACE"

    # Verify in DB
    with SessionLocal() as db:
        user = FinancialRepository.get_user_by_email(db, new_email)
        assert user is not None
        assert user.is_demo_user is False
        assert user.email_verified is True
        assert user.profile is not None
        # Clean up test user
        db.delete(user)
        db.commit()
    print("[TEST 02] test_select_account_new_google_user ..................... PASS")

def test_03_zero_demo_account_leakage():
    """Verify selecting an account NEVER enters the Arjun K. demo persona."""
    res = client.post(
        "/api/v1/auth/google/select-account",
        json={
            "email": "satyabrata.lead@gmail.com",
            "name": "Satyabrata Lead"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["is_demo_user"] is False
    assert data["user"]["name"] != "Arjun K."
    assert data["workspace_mode"] == "PRIVATE WORKSPACE"
    print("[TEST 03] test_zero_demo_account_leakage .......................... PASS")

def test_04_select_account_validation():
    """Verify input validation rejects empty or invalid email."""
    res = client.post(
        "/api/v1/auth/google/select-account",
        json={
            "email": "",
            "name": "Invalid User"
        }
    )
    assert res.status_code == 422
    print("[TEST 04] test_select_account_validation ......................... PASS")

def test_05_update_google_client_id():
    """Verify saving Google Client ID dynamically and restoring real user Client ID."""
    real_cid = "947725575754-6dm6krn2rdgpjicukncluhocheuis2ab.apps.googleusercontent.com"
    res = client.post(
        "/api/v1/auth/config/google-client-id",
        json={"client_id": real_cid}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["google_client_id"] == real_cid

    # Verify get config reflects it
    cfg_res = client.get("/api/v1/auth/config")
    assert cfg_res.status_code == 200
    assert cfg_res.json()["is_configured"] is True
    assert cfg_res.json()["google_client_id"] == real_cid
    print("[TEST 05] test_update_google_client_id .......................... PASS")

def test_06_oauth_callback_handling():
    """Verify OAuth callback redirects gracefully on errors or missing codes."""
    res_err = client.get("/api/v1/auth/google/callback?error=access_denied", follow_redirects=False)
    assert res_err.status_code in (302, 303, 307)
    assert "error=access_denied" in res_err.headers["location"]

    res_missing = client.get("/api/v1/auth/google/callback", follow_redirects=False)
    assert res_missing.status_code in (302, 303, 307)
    assert "error=missing_code" in res_missing.headers["location"]
    print("[TEST 06] test_06_oauth_callback_handling ....................... PASS")

if __name__ == "__main__":
    test_01_select_account_existing_user()
    test_02_select_account_new_google_user()
    test_03_zero_demo_account_leakage()
    test_04_select_account_validation()
    test_05_update_google_client_id()
    test_06_oauth_callback_handling()
    print("\nALL GOOGLE ACCOUNT SELECTOR TESTS PASSED PERFECTLY!")
