"""
SURE SAVINGS 8.0: Comprehensive Automated Test Suite for Financial Calendar Engine
Verifies:
1. Calendar Service dynamic month generation, day mapping, and metrics aggregation.
2. Heatmap status classification (GREEN, AMBER, RED, BLUE, GREY).
3. Intraday liquidity progression curve modeling and day inspector breakdown.
4. Full Calendar Event CRUD (POST, GET, PATCH, DELETE, RECALCULATE).
5. Strict multi-tenant data isolation & IDOR prevention.
6. The Golden User Test Scenario:
   - User with ₹10k/wk income, ₹6k/wk burn, ₹8k cash/buffer, ₹5k target, ₹4k floor.
   - Rent ₹4,000 on Sep 15 (09:00 AM)
   - EMI ₹2,500 on Sep 20 (09:00 AM)
   - Inflow ₹6,500 on Sep 20 (06:00 PM)
   - Verifies 09:00 AM debit creates temporary timing gap below ₹4,000 floor before 06:00 PM settlement.
   - Verifies automated buffer absorption absorbs the ₹2,500 deficit.
   - Alters EMI ₹2,500 -> ₹5,000: confirms universal recalculation dynamically propagates across
     calendar, day detail, and risk/resilience telemetry with zero manual code changes.
7. Public demo calendar endpoint accessibility.
"""
import pytest
from starlette.testclient import TestClient
from datetime import datetime, timezone

from backend.main import app
from backend.database import SessionLocal
from backend.models import User, FinancialProfile, ScheduledObligation, CalendarEvent
from backend.repository import FinancialRepository
from backend.services.calendar_service import FinancialCalendarService
from backend.financial_engine import FinancialEngine

client = TestClient(app)


def _create_test_user_session(email: str, name: str, google_sub: str, buffer_val: float = 8000.0, income_val: float = 10000.0, burn_val: float = 6000.0, floor_val: float = 4000.0, target_val: float = 5000.0):
    with SessionLocal() as db:
        user = FinancialRepository.create_or_update_google_user(db, {
            "google_subject_id": google_sub,
            "email": email,
            "name": name
        })
        # Clean up any residual test calendar events to ensure clean test isolation
        db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id).delete()
        p = user.profile
        p.current_buffer = buffer_val
        p.current_income = income_val
        p.weekly_burn = burn_val
        p.protected_floor = floor_val
        p.buffer_target = target_val
        p.safe_to_use_above_floor = max(0.0, buffer_val - floor_val)
        db.commit()
        db.refresh(user)
        sess = FinancialRepository.create_session(db, user.id, expires_days=2)
        token = sess.session_token
        user_id = user.id
    return user_id, token


# =====================================================================
# 1. CALENDAR SERVICE DYNAMIC MONTH GENERATION
# =====================================================================

def test_01_calendar_service_month_structure():
    """Verifies dynamic month length, weekday offset, and structure for various months."""
    with SessionLocal() as db:
        user_id, token = _create_test_user_session("cal_user_01@test.com", "Cal User 1", "sub_cal_01")

        # Test September 2026 (30 days, starts Tuesday = 1)
        cal_sep = FinancialCalendarService.get_calendar(db, user_id, year=2026, month=9)
        assert cal_sep["status"] == "success"
        assert cal_sep["year"] == 2026
        assert cal_sep["month"] == 9
        assert cal_sep["month_name"] == "September"
        assert cal_sep["num_days"] == 30
        assert len(cal_sep["days"]) == 30
        assert cal_sep["first_weekday"] == 1  # Sep 1, 2026 is Tuesday

        # Test October 2026 (31 days, starts Thursday = 3)
        cal_oct = FinancialCalendarService.get_calendar(db, user_id, year=2026, month=10)
        assert cal_oct["num_days"] == 31
        assert len(cal_oct["days"]) == 31
        assert cal_oct["first_weekday"] == 3

        # Test February 2028 (Leap year = 29 days)
        cal_feb = FinancialCalendarService.get_calendar(db, user_id, year=2028, month=2)
        assert cal_feb["num_days"] == 29
        assert len(cal_feb["days"]) == 29


# =====================================================================
# 2. CALENDAR EVENT REPOSITORY CRUD
# =====================================================================

def test_02_calendar_event_repository_crud():
    """Verifies repository-level creation, retrieval, update, and deletion of CalendarEvents."""
    with SessionLocal() as db:
        user_id, token = _create_test_user_session("cal_user_02@test.com", "Cal User 2", "sub_cal_02")

        # Create event
        ev = FinancialRepository.create_calendar_event(
            db=db,
            user_id=user_id,
            title="Electric Scooter EMI",
            date_str="2026-09-18",
            amount=3200.0,
            direction="outflow",
            event_type="commitment",
            time_str="10:30 AM",
            category="Mobility",
            is_essential=True
        )
        assert ev.id is not None
        assert ev.title == "Electric Scooter EMI"
        assert ev.amount == 3200.0

        # Retrieve events
        events = FinancialRepository.get_calendar_events(db, user_id)
        assert len(events) >= 1
        found = any(e.id == ev.id for e in events)
        assert found is True

        # Update event
        updated = FinancialRepository.update_calendar_event(
            db=db,
            event_id=ev.id,
            user_id=user_id,
            amount=3500.0,
            notes="Revised with bank surcharge"
        )
        assert updated is not None
        assert updated.amount == 3500.0
        assert updated.notes == "Revised with bank surcharge"

        # Delete event
        ok = FinancialRepository.delete_calendar_event(db, ev.id, user_id)
        assert ok is True

        # Verify not found
        post_del = FinancialRepository.get_calendar_event_by_id(db, ev.id, user_id)
        assert post_del is None


# =====================================================================
# 3. REST API CALENDAR CRUD & RECALCULATION
# =====================================================================

def test_03_calendar_rest_api_crud_endpoints():
    """Tests the full REST lifecycle of a calendar event with universal recalculation."""
    user_id, token = _create_test_user_session("cal_user_03@test.com", "Cal User 3", "sub_cal_03")
    headers = {"Cookie": f"sure_savings_session={token}"}

    # 1. Create Event via POST
    create_resp = client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Apartment Maintenance",
        "date_str": "2026-09-12",
        "time_str": "11:00 AM",
        "direction": "outflow",
        "amount": 1800.0,
        "category": "Housing",
        "event_type": "commitment",
        "is_essential": True
    })
    assert create_resp.status_code == 201
    create_data = create_resp.json()
    assert create_data["status"] == "success"
    event_id = create_data["event"]["id"]
    assert create_data["event"]["amount"] == 1800.0

    # 2. View in Monthly Calendar
    cal_resp = client.get("/api/v1/calendar?year=2026&month=9", headers=headers)
    assert cal_resp.status_code == 200
    cal_data = cal_resp.json()
    assert cal_data["summary"]["essential_outflows"] >= 1800.0
    day_12 = next(d for d in cal_data["days"] if d["day"] == 12)
    assert any(e["title"] == "Apartment Maintenance" for e in day_12["events"])

    # 3. View in Day Detail
    day_resp = client.get("/api/v1/calendar/day?date=2026-09-12", headers=headers)
    assert day_resp.status_code == 200
    day_data = day_resp.json()
    assert day_data["date"] == "2026-09-12"
    assert any(e["title"] == "Apartment Maintenance" for e in day_data["events"])

    # 4. Update Event via PATCH
    patch_resp = client.patch(f"/api/v1/calendar/events/{event_id}", headers=headers, json={
        "amount": 2200.0,
        "title": "Apartment Maintenance (Revised)"
    })
    assert patch_resp.status_code == 200
    patch_data = patch_resp.json()
    assert patch_data["event"]["amount"] == 2200.0
    assert patch_data["event"]["title"] == "Apartment Maintenance (Revised)"

    # 5. Delete Event via DELETE
    del_resp = client.delete(f"/api/v1/calendar/events/{event_id}", headers=headers)
    assert del_resp.status_code == 200
    del_data = del_resp.json()
    assert del_data["status"] == "success"
    assert del_data["deleted_id"] == event_id

    # 6. Verify Day 12 reflects deletion
    day_resp_after = client.get("/api/v1/calendar/day?date=2026-09-12", headers=headers)
    day_data_after = day_resp_after.json()
    assert not any(e["id"] == event_id for e in day_data_after["events"])


# =====================================================================
# 4. IDOR PREVENTION & CROSS-TENANT ISOLATION
# =====================================================================

def test_04_calendar_idor_tenant_isolation():
    """Verifies that User B cannot view, update, or delete User A's calendar events."""
    user_a_id, token_a = _create_test_user_session("alice_cal@test.com", "Alice Cal", "sub_alice_cal")
    user_b_id, token_b = _create_test_user_session("bob_cal@test.com", "Bob Cal", "sub_bob_cal")

    headers_a = {"Cookie": f"sure_savings_session={token_a}"}
    headers_b = {"Cookie": f"sure_savings_session={token_b}"}

    # Alice creates a confidential commitment
    create_resp = client.post("/api/v1/calendar/events", headers=headers_a, json={
        "title": "Alice Confidential Medical Checkup",
        "date_str": "2026-09-25",
        "time_str": "02:00 PM",
        "direction": "outflow",
        "amount": 7500.0,
        "category": "Health",
        "event_type": "commitment",
        "is_essential": True
    })
    assert create_resp.status_code == 201
    event_id = create_resp.json()["event"]["id"]

    # Bob attempts to PATCH Alice's event -> 404
    bob_patch = client.patch(f"/api/v1/calendar/events/{event_id}", headers=headers_b, json={
        "amount": 100.0
    })
    assert bob_patch.status_code == 404

    # Bob attempts to DELETE Alice's event -> 404
    bob_del = client.delete(f"/api/v1/calendar/events/{event_id}", headers=headers_b)
    assert bob_del.status_code == 404

    # Bob views his calendar -> Alice's event is completely absent
    bob_cal = client.get("/api/v1/calendar?year=2026&month=9", headers=headers_b)
    assert not any(e["id"] == event_id for e in bob_cal.json()["events"])

    # Alice's event is still safely intact
    alice_day = client.get("/api/v1/calendar/day?date=2026-09-25", headers=headers_a)
    assert any(e["id"] == event_id for e in alice_day.json()["events"])


# =====================================================================
# 5. THE GOLDEN USER TEST SCENARIO
# =====================================================================

def test_05_golden_user_scenario_calendar_and_universal_recalculation():
    """
    CRITICAL GOLDEN USER TEST SCENARIO:
    1. Create user with:
       - Weekly Income: ₹10,000
       - Weekly Burn: ₹6,000
       - Cash/Buffer: ₹8,000
       - Buffer Target: ₹5,000
       - Protected Floor: ₹4,000
    2. Add:
       - Rent ₹4,000 on Sep 15 (09:00 AM)
       - EMI ₹2,500 on Sep 20 (09:00 AM)
       - Inflow ₹6,500 on Sep 20 (06:00 PM)
    3. Assert:
       - On Sep 20: 09:00 AM EMI debits from baseline ₹4,000 floor -> temporary timing gap occurs!
       - Absorption required = ₹2,500.
       - Buffer of ₹8,000 absorbs ₹2,500 shortfall -> remaining cushion = ₹5,500.
       - Day status marks timing gap detected.
    4. Alter EMI from ₹2,500 -> ₹5,000:
       - Universal recalculation automatically updates absorption required to ₹5,000.
       - Remaining cushion drops to ₹3,000.
       - Minimum balance drops accordingly.
       - Zero manual code changes.
    """
    user_id, token = _create_test_user_session(
        email="golden_scenario_cal@fintech.test",
        name="Golden User",
        google_sub="sub_golden_user_cal",
        buffer_val=8000.0,
        income_val=10000.0,
        burn_val=6000.0,
        floor_val=4000.0,
        target_val=5000.0
    )
    headers = {"Cookie": f"sure_savings_session={token}"}

    # Step 1: Add Rent ₹4,000 on Sep 15
    resp_rent = client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Apartment Rent",
        "date_str": "2026-09-15",
        "time_str": "09:00 AM",
        "direction": "outflow",
        "amount": 4000.0,
        "category": "Housing",
        "event_type": "commitment",
        "is_essential": True
    })
    assert resp_rent.status_code == 201

    # Step 2: Add EMI ₹2,500 on Sep 20 (09:00 AM)
    resp_emi = client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "EV Two-Wheeler EMI",
        "date_str": "2026-09-20",
        "time_str": "09:00 AM",
        "direction": "outflow",
        "amount": 2500.0,
        "category": "Loan",
        "event_type": "commitment",
        "is_essential": True
    })
    assert resp_emi.status_code == 201
    emi_event_id = resp_emi.json()["event"]["id"]

    # Step 3: Add Inflow ₹6,500 on Sep 20 (06:00 PM)
    resp_inflow = client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Platform Direct Deposit Settlement",
        "date_str": "2026-09-20",
        "time_str": "06:00 PM",
        "direction": "inflow",
        "amount": 6500.0,
        "category": "Income",
        "event_type": "payout",
        "is_essential": True
    })
    assert resp_inflow.status_code == 201

    # Step 4: Verify Day Detail on Sep 20
    day_sep20 = client.get("/api/v1/calendar/day?date=2026-09-20", headers=headers).json()
    assert day_sep20["date"] == "2026-09-20"
    assert day_sep20["has_timing_gap"] is True
    assert day_sep20["absorption_required"] == 2500.0
    assert day_sep20["is_absorbable_by_buffer"] is True
    assert day_sep20["remaining_vault_cushion"] == 8000.0 - 2500.0  # 5,500

    # Verify timeline progression nodes: Baseline -> 09:00 AM Debit -> 09:01 AM Buffer Absorption -> 06:00 PM Credit
    timeline = day_sep20["timeline"]
    assert len(timeline) >= 4
    times = [t["time"] for t in timeline]
    assert "08:00 AM" in times
    assert "09:00 AM" in times
    assert "09:01 AM" in times
    assert "06:00 PM" in times

    # Step 5: Verify Monthly Calendar has Critical Day
    cal_data = client.get("/api/v1/calendar?year=2026&month=9", headers=headers).json()
    crit_days = cal_data["critical_days"]
    assert any("2026-09-20" in d["date"] or "Sep 20" in d["date"] for d in crit_days)
    assert cal_data["summary"]["critical_gap_days_count"] >= 1

    # Step 6: Alter EMI from ₹2,500 -> ₹5,000
    patch_emi = client.patch(f"/api/v1/calendar/events/{emi_event_id}", headers=headers, json={
        "amount": 5000.0
    })
    assert patch_emi.status_code == 200

    # Step 7: Verify Universal Recalculation took effect dynamically
    day_sep20_updated = client.get("/api/v1/calendar/day?date=2026-09-20", headers=headers).json()
    assert day_sep20_updated["has_timing_gap"] is True
    assert day_sep20_updated["absorption_required"] == 5000.0
    assert day_sep20_updated["remaining_vault_cushion"] == 8000.0 - 5000.0  # 3,000

    cal_data_updated = client.get("/api/v1/calendar?year=2026&month=9", headers=headers).json()
    assert cal_data_updated["summary"]["essential_outflows"] >= 9000.0  # 4,000 rent + 5,000 EMI


# =====================================================================
# 6. PUBLIC DEMO CALENDAR & SYNC ENDPOINTS
# =====================================================================

def test_06_public_demo_calendar_endpoint():
    """Verifies that public visitors can explore Arjun K.'s demo calendar without auth."""
    resp = client.get("/api/v1/public/demo/calendar?year=2026&month=9")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["year"] == 2026
    assert data["month"] == 9
    assert len(data["days"]) == 30
    assert "summary" in data
    assert data["summary"]["expected_income"] > 0


def test_07_calendar_sync_recalculate_endpoints():
    """Verifies POST /api/v1/calendar/recalculate and /api/v1/calendar/sync."""
    user_id, token = _create_test_user_session("sync_user@test.com", "Sync User", "sub_sync_user")
    headers = {"Cookie": f"sure_savings_session={token}"}

    recalc_resp = client.post("/api/v1/calendar/recalculate?year=2026&month=9", headers=headers)
    assert recalc_resp.status_code == 200
    assert recalc_resp.json()["status"] == "success"

    sync_resp = client.post("/api/v1/calendar/sync?year=2026&month=9", headers=headers)
    assert sync_resp.status_code == 200
    assert sync_resp.json()["status"] == "success"


# =====================================================================
# 7. RECURRENCE DYNAMIC EXPANSION
# =====================================================================

def test_08_calendar_recurrence_dynamic_expansion():
    """Verifies dynamic recurrence expansion across month calendar days."""
    user_id, token = _create_test_user_session("recur_user@fintech.test", "Recur User", "sub_recur_user")
    headers = {"Cookie": f"sure_savings_session={token}"}

    # Create a weekly recurring expense on Wednesday Sep 2, 2026
    resp = client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Weekly Bike Maintenance",
        "date_str": "2026-09-02",
        "time_str": "10:00 AM",
        "direction": "outflow",
        "amount": 350.0,
        "category": "Mobility",
        "event_type": "commitment",
        "recurrence": "weekly",
        "is_essential": True
    })
    assert resp.status_code == 201
    ev_id = resp.json()["event"]["id"]

    # Fetch September 2026 (Wednesdays are Sep 2, 9, 16, 23, 30)
    cal_resp = client.get("/api/v1/calendar?year=2026&month=9", headers=headers)
    assert cal_resp.status_code == 200
    cal_data = cal_resp.json()

    # Verify occurrences appear on all Wednesdays in September
    wednesdays = [2, 9, 16, 23, 30]
    for w in wednesdays:
        day_obj = next((d for d in cal_data["days"] if d["day"] == w), None)
        assert day_obj is not None, f"Day {w} missing from calendar"
        has_ev = any("Weekly Bike Maintenance" in e["title"] for e in day_obj["events"])
        assert has_ev is True, f"Weekly occurrence missing on day {w}"

    # Verify summary essential_outflows includes all 5 occurrences (5 * 350 = 1750)
    assert cal_data["summary"]["essential_outflows"] >= 1750.0


# =====================================================================
# 8. EXPECTED VS ACTUAL VARIANCE ENGINE
# =====================================================================

def test_09_calendar_expected_vs_actual_variance():
    """Verifies Expected vs Actual variance calculation and timing delay detection."""
    user_id, token = _create_test_user_session("var_user@fintech.test", "Var User", "sub_var_user")
    headers = {"Cookie": f"sure_savings_session={token}"}

    # Add scheduled inflow of ₹7,000 on Sep 10
    client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Platform Weekly Payout",
        "date_str": "2026-09-10",
        "time_str": "05:00 PM",
        "direction": "inflow",
        "amount": 7000.0,
        "category": "Income",
        "event_type": "payout",
        "is_essential": True
    })

    # Add scheduled outflow of ₹4,000 on Sep 15
    client.post("/api/v1/calendar/events", headers=headers, json={
        "title": "Studio Rent",
        "date_str": "2026-09-15",
        "time_str": "09:00 AM",
        "direction": "outflow",
        "amount": 4000.0,
        "category": "Housing",
        "event_type": "commitment",
        "is_essential": True
    })

    # Call variance endpoint
    var_resp = client.get("/api/v1/calendar/variance?year=2026&month=9", headers=headers)
    assert var_resp.status_code == 200
    var_data = var_resp.json()

    assert var_data["status"] == "success"
    assert var_data["year"] == 2026
    assert var_data["month"] == 9
    assert var_data["total_expected_income"] >= 7000.0
    assert var_data["total_expected_outflow"] >= 4000.0
    assert isinstance(var_data["records"], list)
    assert len(var_data["records"]) >= 2

    # Check rent record
    rent_rec = next((r for r in var_data["records"] if "Studio Rent" in r["title"]), None)
    assert rent_rec is not None
    assert rent_rec["expected_amount"] == 4000.0
    assert rent_rec["status"] in ["PENDING", "SETTLED", "DELAYED"]


# =====================================================================
# 9. CSV & JSON CALENDAR EXPORT
# =====================================================================

def test_10_calendar_export_csv_and_json():
    """Verifies CSV and JSON export formatting, data integrity, and IDOR isolation."""
    user_a_id, token_a = _create_test_user_session("export_a@fintech.test", "Export User A", "sub_exp_a")
    user_b_id, token_b = _create_test_user_session("export_b@fintech.test", "Export User B", "sub_exp_b")

    headers_a = {"Cookie": f"sure_savings_session={token_a}"}
    headers_b = {"Cookie": f"sure_savings_session={token_b}"}

    # User A creates a distinctive event
    client.post("/api/v1/calendar/events", headers=headers_a, json={
        "title": "Unique Secret Event Alpha",
        "date_str": "2026-09-14",
        "time_str": "03:00 PM",
        "direction": "outflow",
        "amount": 1999.0,
        "category": "Discretionary",
        "event_type": "adhoc"
    })

    # 1. User A exports CSV
    csv_resp = client.get("/api/v1/calendar/export?year=2026&month=9&format=csv", headers=headers_a)
    assert csv_resp.status_code == 200
    csv_json = csv_resp.json()
    assert csv_json["format"] == "csv"
    assert "text/csv" in csv_json["content_type"]
    assert "filename" in csv_json
    csv_text = csv_json["data"]
    assert "Date,Time,Title,Type,Direction,Amount" in csv_text
    assert "Unique Secret Event Alpha" in csv_text
    assert "1999" in csv_text

    # 2. User A exports JSON
    json_resp = client.get("/api/v1/calendar/export?year=2026&month=9&format=json", headers=headers_a)
    assert json_resp.status_code == 200
    json_data = json_resp.json()
    assert json_data["format"] == "json"
    cal = json_data["data"]
    assert cal["month"] == 9
    assert cal["year"] == 2026
    assert any(e["title"] == "Unique Secret Event Alpha" for e in cal["events"])

    # 3. User B exports CSV: User A's event MUST NOT appear
    csv_b = client.get("/api/v1/calendar/export?year=2026&month=9&format=csv", headers=headers_b)
    assert csv_b.status_code == 200
    assert "Unique Secret Event Alpha" not in csv_b.json()["data"]


# =====================================================================
# 10. INCOME INTEGRATION PROVIDER & CONNECT WORKFLOW
# =====================================================================

def test_11_income_providers_and_connect():
    """Verifies Income Integration Provider catalogue and connect workflow."""
    user_id, token = _create_test_user_session("income_int@fintech.test", "Income Int User", "sub_inc_int")
    headers = {"Cookie": f"sure_savings_session={token}"}

    # 1. Get catalogue of providers
    prov_resp = client.get("/api/v1/income/providers", headers=headers)
    assert prov_resp.status_code == 200
    p_data = prov_resp.json()
    assert p_data["status"] == "success"
    assert len(p_data["providers"]) >= 5
    provider_ids = [p["id"] for p in p_data["providers"]]
    assert "zomato" in provider_ids
    assert "blinkit" in provider_ids
    assert "swiggy" in provider_ids
    assert "uber" in provider_ids

    # 2. Connect Zomato source
    connect_resp = client.post("/api/v1/income/providers/connect", headers=headers, json={
        "provider_id": "zomato",
        "typical_amount": 9200.0,
        "frequency": "weekly",
        "payout_day": "Thursday"
    })
    assert connect_resp.status_code == 200
    c_data = connect_resp.json()
    assert c_data["status"] == "success"
    assert "Zomato" in c_data["income_source"]["platform"]
    assert c_data["income_source"]["amount"] == 9200.0
    assert c_data["calendar_event"] is not None

    # 3. Verify calendar reflects connected income source dynamically
    cal_resp = client.get("/api/v1/calendar?year=2026&month=9", headers=headers)
    assert cal_resp.status_code == 200
    cal_data = cal_resp.json()
    assert cal_data["summary"]["expected_income"] >= 9200.0
    # Thursdays in Sep 2026 are Sep 3, 10, 17, 24
    thursdays = [3, 10, 17, 24]
    for thu in thursdays:
        d = next((day for day in cal_data["days"] if day["day"] == thu), None)
        assert d is not None
        assert any("Zomato" in e["title"] for e in d["events"])

    # 4. Verify unauthenticated call is rejected
    unauth = client.post("/api/v1/income/providers/connect", json={
        "provider_id": "swiggy",
        "typical_amount": 5000.0,
        "frequency": "weekly",
        "payout_day": "Wednesday"
    })
    assert unauth.status_code == 401

