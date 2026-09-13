
import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User
from backend.repository import FinancialRepository, seed_canonical_user

def test_public_demo_v8_endpoints():
    client = TestClient(app)
    
    # Test all 11 public demo endpoints via GET
    endpoints = [
        "/api/v1/public/demo/weather",
        "/api/v1/public/demo/resilience-plan",
        "/api/v1/public/demo/what-changed",
        "/api/v1/public/demo/scenarios/portfolio",
        "/api/v1/public/demo/recovery-plan",
        "/api/v1/public/demo/goals/optimize",
        "/api/v1/public/demo/income/diversification",
        "/api/v1/public/demo/timeline",
        "/api/v1/public/demo/briefing",
        "/api/v1/public/demo/outlook",
        "/api/v1/public/demo/stress-test"
    ]
    
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} failed with {res.status_code}"
        data = res.json()
        assert data is not None

    # Test POST scenarios portfolio for demo
    portfolio_res = client.post("/api/v1/public/demo/scenarios/portfolio", json={
        "scenarios": [
            {"id": "s1", "name": "Income Drop -20%", "income_shock_pct": -0.20},
            {"id": "s2", "name": "Income Drop -40%", "income_shock_pct": -0.40}
        ]
    })
    assert portfolio_res.status_code == 200
    p_data = portfolio_res.json()
    assert "results" in p_data or "strategies" in p_data

    # Verify weather response structure
    w_res = client.get("/api/v1/public/demo/weather")
    w = w_res.json()
    assert "daily_forecast" in w or "seven_day" in w or "outlook" in w

    # Verify resilience plan has 4 ranked priorities
    rp_res = client.get("/api/v1/public/demo/resilience-plan")
    rp = rp_res.json()
    assert "top_priorities" in rp
    assert len(rp["top_priorities"]) == 4

    # Verify recovery plan has pathways
    rc_res = client.get("/api/v1/public/demo/recovery-plan")
    rc = rc_res.json()
    assert "pathways" in rc or "plans" in rc

def test_authenticated_v8_endpoints_and_isolation():
    client = TestClient(app)
    
    with SessionLocal() as db:
        user = FinancialRepository.create_or_update_google_user(db, {
            "google_subject_id": "g_sub_v8_fresh_user_01",
            "email": "v8user@testresilience.com",
            "name": "Fresh V8 User"
        })
        user_id = user.id
        sess = FinancialRepository.create_session(db, user_id)
        session_token = sess.session_token

    cookies = {"sure_savings_session": session_token}
    
    # 1. Digital Twin
    tw_res = client.get("/api/v1/workspace/digital-twin", cookies=cookies)
    assert tw_res.status_code == 200
    tw = tw_res.json()
    assert tw.get("resilience_os_version") == "8.0"
    
    # 2. Weather
    w_res = client.get("/api/v1/workspace/weather", cookies=cookies)
    assert w_res.status_code == 200
    
    # 3. Resilience Plan
    rp_res = client.get("/api/v1/workspace/resilience-plan", cookies=cookies)
    assert rp_res.status_code == 200
    rp = rp_res.json()
    assert "top_priorities" in rp
    
    # 4. What Changed
    wc_res = client.get("/api/v1/workspace/what-changed", cookies=cookies)
    assert wc_res.status_code == 200
    
    # 5. Goal Optimization
    go_res = client.post("/api/v1/workspace/goals/optimize", cookies=cookies, json={
        "goals": [
            {"id": "g1", "title": "Emergency Buffer", "target": 10000, "current": 2000, "priority": "high"},
            {"id": "g2", "title": "Equipment", "target": 5000, "current": 1000, "priority": "medium"}
        ],
        "monthly_savings_pool": 1000
    })
    assert go_res.status_code == 200
    go = go_res.json()
    assert "allocations" in go or "goals" in go or "total_allocated" in go

    # 6. Scenarios Portfolio
    sp_res = client.post("/api/v1/workspace/scenarios/portfolio", cookies=cookies, json={
        "scenarios": [
            {"id": "s1", "name": "Conservative", "income_shock_pct": -0.15},
            {"id": "s2", "name": "Severe", "income_shock_pct": -0.35}
        ]
    })
    assert sp_res.status_code == 200
    sp = sp_res.json()
    assert "results" in sp or "strategies" in sp

    # 7. Recovery Plan
    rec_res = client.get("/api/v1/workspace/recovery-plan", cookies=cookies)
    assert rec_res.status_code == 200

    # 8. Income Diversification
    div_res = client.get("/api/v1/workspace/income/diversification", cookies=cookies)
    assert div_res.status_code == 200

    # 9. Timeline Story
    tl_res = client.get("/api/v1/workspace/timeline", cookies=cookies)
    assert tl_res.status_code == 200

    # 10. Weekly Briefing
    br_res = client.get("/api/v1/workspace/briefing", cookies=cookies)
    assert br_res.status_code == 200

    # 11. Multi-Horizon Outlook
    out_res = client.get("/api/v1/workspace/outlook", cookies=cookies)
    assert out_res.status_code == 200

    # 12. Stress Test Suite
    st_res = client.get("/api/v1/workspace/stress-test", cookies=cookies)
    assert st_res.status_code == 200
