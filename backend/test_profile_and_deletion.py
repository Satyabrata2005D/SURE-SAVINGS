"""
Unit and Integration Tests for SURE SAVINGS Profile Management & Permanent Account Deletion.
Validates:
- GET /api/v1/auth/profile: Returns user details & calibrated baseline
- PUT /api/v1/auth/profile: Updates name, date of birth, phone, occupation, location
- POST /api/v1/auth/profile/photo: Uploads base64 image avatar and sets URL
- DELETE /api/v1/auth/profile: Rejects mismatched confirmation
- DELETE /api/v1/auth/profile: Permanently wipes out account and cascades upon exact confirmation
"""
import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User, FinancialProfile
from backend.repository import FinancialRepository
import os

client = TestClient(app)

@pytest.fixture
def test_user_session():
    """Creates a temporary test user and active session."""
    db = SessionLocal()
    import uuid
    uid = f"usr_test_{uuid.uuid4().hex[:8]}"
    user = User(
        id=uid,
        email=f"profile_test_{uuid.uuid4().hex[:6]}@example.com",
        name="Test Profile User",
        display_name="Test Profile User",
        first_name="Test",
        last_name="User",
        date_of_birth="1995-06-15",
        phone_number="+91 9876543210",
        occupation="Delivery Rider",
        country="India",
        state="Karnataka",
        district="Bengaluru",
        area="Indiranagar",
        is_onboarded=True
    )
    db.add(user)
    db.commit()

    # Seed baseline financial profile
    FinancialRepository.initialize_new_user_workspace(db, user.id)
    db.commit()

    u_id = str(user.id)
    u_email = str(user.email)
    session = FinancialRepository.create_session(db, user.id)
    s_token = str(session.session_token)
    db.close()

    return {
        "user_id": u_id,
        "email": u_email,
        "token": s_token
    }

def test_get_user_profile(test_user_session):
    cookie = {"sure_savings_session": test_user_session["token"]}
    res = client.get("/api/v1/auth/profile", cookies=cookie)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["user"]["email"] == test_user_session["email"]
    assert data["user"]["date_of_birth"] == "1995-06-15"
    assert data["user"]["phone_number"] == "+91 9876543210"
    assert data["user"]["occupation"] == "Delivery Rider"
    assert "baseline" in data
    assert data["baseline"]["typical_weekly_income"] > 0

def test_update_user_profile(test_user_session):
    cookie = {"sure_savings_session": test_user_session["token"]}
    update_payload = {
        "name": "Updated Profile Name",
        "date_of_birth": "1992-11-20",
        "phone_number": "+91 9998887776",
        "occupation": "Freelance Consultant",
        "state": "Maharashtra",
        "district": "Mumbai",
        "area": "Bandra"
    }
    res = client.put("/api/v1/auth/profile", json=update_payload, cookies=cookie)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["user"]["name"] == "Updated Profile Name"
    assert data["user"]["date_of_birth"] == "1992-11-20"
    assert data["user"]["phone_number"] == "+91 9998887776"
    assert data["user"]["occupation"] == "Freelance Consultant"

    # Verify persistence via GET
    get_res = client.get("/api/v1/auth/profile", cookies=cookie)
    assert get_res.json()["user"]["name"] == "Updated Profile Name"
    assert get_res.json()["user"]["date_of_birth"] == "1992-11-20"

def test_upload_profile_photo(test_user_session):
    cookie = {"sure_savings_session": test_user_session["token"]}
    # Minimal 1x1 valid PNG in base64
    tiny_png_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    res = client.post("/api/v1/auth/profile/photo", json={"photo_base64": tiny_png_base64}, cookies=cookie)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["avatar_url"].startswith("/uploads/avatars/")

    # Check file exists on filesystem
    file_path = data["avatar_url"].lstrip("/").split("?")[0]
    full_path = os.path.join(os.getcwd(), file_path)
    assert os.path.exists(full_path)

def test_delete_profile_requires_exact_phrase(test_user_session):
    cookie = {"sure_savings_session": test_user_session["token"]}
    # Incorrect phrase
    res = client.request("DELETE", "/api/v1/auth/profile", json={"confirmation": "delete"}, cookies=cookie)
    assert res.status_code == 400
    err_body = res.json()
    msg = err_body.get("error", {}).get("message") or err_body.get("detail", "")
    assert "Delete profile permanently" in msg

def test_delete_profile_permanently_success(test_user_session):
    cookie = {"sure_savings_session": test_user_session["token"]}
    # Correct phrase
    res = client.request("DELETE", "/api/v1/auth/profile", json={"confirmation": "Delete profile permanently"}, cookies=cookie)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["deleted_user_id"] == test_user_session["user_id"]

    # Verify user record is gone from DB
    db = SessionLocal()
    deleted_user = db.query(User).filter(User.id == test_user_session["user_id"]).first()
    deleted_profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == test_user_session["user_id"]).first()
    db.close()
    assert deleted_user is None
    assert deleted_profile is None

    # Subsequent API call with the deleted user's token should return 401
    followup_res = client.get("/api/v1/auth/me", cookies=cookie)
    assert followup_res.status_code == 401
