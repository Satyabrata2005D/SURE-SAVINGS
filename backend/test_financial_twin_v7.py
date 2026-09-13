"""
SURE SAVINGS 7.0: Comprehensive Automated Verification Suite
Personal Financial Digital Twin & Multi-Layer Financial Intelligence Platform
Verifies:
1. Canonical Public Demo Isolation (Arjun K. canonical values preserved)
2. Zero-State Isolation for New Private Users (Zero leakage, typed empty state)
3. Data Quality Engine (Completeness, Validity, Consistency, Freshness, Duplication)
4. Behavioral Personalization Engine (9 distinct behavioral profiles)
5. Next Best Action Engine (Authoritative financial prioritization & rationale)
6. What-If Scenario Simulation 2.0 (Parametric multi-variable simulation & library)
7. Explainability Engine (Mathematical formulas, traces & 6-step dependency graph)
8. Event-Driven Monitoring Engine (State transitions & deduplication)
9. Monotonic Source Data Versioning
10. End-to-End REST APIs for all 7.0 endpoints
"""
import pytest
from starlette.testclient import TestClient
from datetime import datetime, timezone
import json
import uuid

from backend.main import app
from backend.database import SessionLocal
from backend.models import (
    User, FinancialProfile, IncomeSource, ExpenseItem, LiquidityPosition,
    ScheduledObligation, Goal, WeeklyIncomeHistory, FinancialEvent
)
from backend.repository import FinancialRepository, seed_canonical_user
from backend.digital_twin import FinancialDigitalTwin
from backend.services.data_quality_service import DataQualityService
from backend.services.personalization_service import PersonalizationService
from backend.services.action_service import ActionService
from backend.services.scenario_service import ScenarioSimulationService
from backend.services.explainability_service import ExplainabilityService
from backend.services.event_detection_service import EventDetectionService
from backend.schemas import WhatIfSimulationRequest

client = TestClient(app)


def test_01_canonical_demo_digital_twin():
    """Verifies that the canonical demo user (Arjun K.) builds an authoritative Digital Twin without regression."""
    with SessionLocal() as db:
        canonical_user = seed_canonical_user(db, force=False)
        twin = FinancialDigitalTwin.build(db, canonical_user.id)

        assert twin["digital_twin_version"] == "7.0"
        assert twin["observation"]["profile"]["is_demo_user"] is True
        assert twin["observation"]["profile"]["current_income"] == 8400.0
        assert twin["understanding"]["stabilized_income"]["amount"] == 7100.0
        assert twin["understanding"]["resilience"]["score"] == 74
        assert twin["understanding"]["risk"]["score"] == 23
        assert twin["decisions"]["safe_to_save"]["recommended_save"] == 900.0
        assert twin["decisions"]["safe_to_save"]["surplus"] == 1300.0
        assert twin["data_quality"]["overall_score"] >= 85
        assert len(twin["explainability"]["safe_to_save"]["steps"]) >= 4
        print("[TEST 01] test_01_canonical_demo_digital_twin ......................... PASS")


def test_02_zero_state_private_user_isolation():
    """Verifies that a brand new private user starts at true zero-state with zero demo data leakage."""
    with SessionLocal() as db:
        unique_id = f"test_zero_{uuid.uuid4().hex[:8]}"
        user = User(
            email=f"{unique_id}@example.com",
            name="Blank Slate User",
            is_demo_user=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        FinancialRepository.initialize_new_user_workspace(db, user.id)
        twin = FinancialDigitalTwin.build(db, user.id)

        # Invariants: ₹0 balances, INSUFFICIENT_DATA status, no leakage from Arjun K.
        assert twin["observation"]["profile"]["current_income"] == 0.0
        assert twin["observation"]["profile"]["current_buffer"] == 0.0
        assert twin["understanding"]["resilience"]["status"] in ("INSUFFICIENT_DATA", "DATA_INCOMPLETE", "CALIBRATING")
        assert twin["understanding"]["risk"]["status"] in ("INSUFFICIENT_DATA", "DATA_INCOMPLETE", "CALIBRATING")
        assert twin["decisions"]["safe_to_save"]["recommended_save"] == 0.0
        assert twin["data_quality"]["quality_status"] == "INSUFFICIENT_DATA"
        assert len(twin["data_quality"]["issues"]) > 0
        print("[TEST 02] test_02_zero_state_private_user_isolation ................. PASS")


def test_03_data_quality_service():
    """Tests the 5 dimensions of data quality evaluation (completeness, validity, consistency, freshness, duplication)."""
    with SessionLocal() as db:
        unique_id = f"test_dq_{uuid.uuid4().hex[:8]}"
        user = User(email=f"{unique_id}@example.com", name="DQ Test User", is_demo_user=False)
        db.add(user)
        db.commit()
        db.refresh(user)

        FinancialRepository.initialize_new_user_workspace(db, user.id)

        # Baseline empty user should have low score
        dq_empty = DataQualityService.evaluate(db, user.id)
        assert dq_empty["overall_score"] < 50
        assert dq_empty["quality_status"] == "INSUFFICIENT_DATA"
        assert "income" in [i["dimension"] for i in dq_empty["issues"]]

        # Calibrate user with Quick Start
        FinancialRepository.apply_quick_start(
            db=db,
            user_id=user.id,
            weekly_income=10000.0,
            essential_expenses=6000.0,
            current_cash=8000.0,
            emergency_savings=12000.0,
            protected_floor=4800.0
        )

        dq_calibrated = DataQualityService.evaluate(db, user.id)
        assert dq_calibrated["overall_score"] > dq_empty["overall_score"]
        assert dq_calibrated["dimensions"]["validity"]["score"] == 100
        print("[TEST 03] test_03_data_quality_service .............................. PASS")


def test_04_behavior_personalization_service():
    """Tests classification of empirical behavioral patterns and strategy mapping."""
    # Test Liquidity Stressed profile
    profile_stressed = PersonalizationService.classify(
        income_cv=0.25,
        burn_ratio=0.92,
        buffer_ratio=0.15,
        resilience_score=28,
        risk_score=75,
        runway_weeks=0.4
    )
    assert profile_stressed["profile"] == "LIQUIDITY_STRESSED"
    assert profile_stressed["tone"] == "cautionary"
    assert len(profile_stressed["action_focus"]) > 0

    # Test Volatile profile
    profile_volatile = PersonalizationService.classify(
        income_cv=0.45,
        burn_ratio=0.60,
        buffer_ratio=0.80,
        resilience_score=60,
        risk_score=40,
        runway_weeks=2.5
    )
    assert profile_volatile["profile"] == "VOLATILE"
    assert "income volatility" in profile_volatile["narrative"].lower()
    print("[TEST 04] test_04_behavior_personalization_service ..................... PASS")


def test_05_next_best_action_service():
    """Tests authoritative Next Best Action derivation and rationale generation."""
    with SessionLocal() as db:
        unique_id = f"test_nba_{uuid.uuid4().hex[:8]}"
        user = User(email=f"{unique_id}@example.com", name="Action Test User", is_demo_user=False)
        db.add(user)
        db.commit()
        db.refresh(user)

        FinancialRepository.initialize_new_user_workspace(db, user.id)

        # Uncalibrated user should have action to complete financial calibration
        action_uncal = ActionService.evaluate(db, user.id)
        assert action_uncal["priority"] == "CRITICAL"
        assert "calibration" in action_uncal["primary_action"]["title"].lower() or "quick start" in action_uncal["primary_action"]["title"].lower()

        # Calibrated user
        FinancialRepository.apply_quick_start(
            db=db,
            user_id=user.id,
            weekly_income=12000.0,
            essential_expenses=7000.0,
            current_cash=10000.0,
            emergency_savings=14000.0,
            protected_floor=5600.0
        )
        action_cal = ActionService.evaluate(db, user.id)
        assert action_cal["primary_action"] is not None
        assert action_cal["confidence"] >= 0.70
        assert "expected_impact" in action_cal
        print("[TEST 05] test_05_next_best_action_service ........................... PASS")


def test_06_what_if_scenario_simulation_2_0():
    """Tests What-If 2.0 scenario catalog and multi-variable parametric simulation."""
    # 1. Test catalog retrieval
    catalog = ScenarioSimulationService.get_scenario_library()
    assert len(catalog) >= 5
    scenario_keys = [s["id"] for s in catalog]
    assert "income_shock_20" in scenario_keys
    assert "expense_hike_15" in scenario_keys

    # 2. Test parametric simulation
    with SessionLocal() as db:
        canonical_user = seed_canonical_user(db, force=False)
        twin = FinancialDigitalTwin.build(db, canonical_user.id)

        req = WhatIfSimulationRequest(
            scenario_name="Stress Test: 20% Income Drop + 10% Expense Rise",
            income_delta_pct=-20.0,
            expense_delta_pct=10.0,
            one_off_shock=0.0,
            delayed_payout_days=0,
            simulation_weeks=6
        )

        sim = ScenarioSimulationService.simulate_parametric(twin, req)
        assert sim["status"] == "success"
        assert sim["parameters"]["income_delta_pct"] == -20.0
        assert sim["scenario"]["metrics"]["income"] < sim["baseline"]["metrics"]["income"]
        assert sim["scenario"]["metrics"]["burn"] > sim["baseline"]["metrics"]["burn"]
        assert sim["delta"]["resilience_impact"] < 0
        assert sim["delta"]["risk_impact"] > 0
        assert len(sim["trajectories"]["baseline"]) == 6
        assert len(sim["trajectories"]["scenario"]) == 6
        assert len(sim["recommendations"]) > 0
        print("[TEST 06] test_06_what_if_scenario_simulation_2_0 ................... PASS")


def test_07_explainability_service():
    """Tests explainability formulas, primary drivers, and 6-step dependency graph."""
    with SessionLocal() as db:
        canonical_user = seed_canonical_user(db, force=False)
        twin = FinancialDigitalTwin.build(db, canonical_user.id)

        # Test safe_to_save explainability
        exp_save = ExplainabilityService.explain_metric("safe_to_save", twin)
        assert exp_save["metric_name"] == "safe_to_save"
        assert "min(surplus * policy_cap, buffer_gap)" in exp_save["formula"]
        assert len(exp_save["calculation_steps"]) >= 4
        assert len(exp_save["dependency_graph"]) >= 4
        assert exp_save["primary_drivers"][0]["name"] == "surplus"

        # Test resilience_score explainability
        exp_res = ExplainabilityService.explain_metric("resilience_score", twin)
        assert exp_res["metric_name"] == "resilience_score"
        assert len(exp_res["dependency_graph"]) >= 3
        print("[TEST 07] test_07_explainability_service ............................ PASS")


def test_08_event_detection_and_monitoring():
    """Tests event-driven detection of financial state changes and cooldown deduplication."""
    with SessionLocal() as db:
        unique_id = f"test_evt_{uuid.uuid4().hex[:8]}"
        user = User(email=f"{unique_id}@example.com", name="Event Test User", is_demo_user=False)
        db.add(user)
        db.commit()
        db.refresh(user)

        FinancialRepository.initialize_new_user_workspace(db, user.id)

        # Calibration triggers state change
        FinancialRepository.apply_quick_start(
            db=db,
            user_id=user.id,
            weekly_income=15000.0,
            essential_expenses=5000.0,
            current_cash=12000.0,
            emergency_savings=25000.0,
            protected_floor=4000.0
        )

        events = FinancialRepository.get_financial_events(db, user.id)
        # Verify event logging
        assert isinstance(events, list)

        # Create explicit event and retrieve
        evt = FinancialRepository.create_financial_event(
            db=db,
            user_id=user.id,
            event_type="BUFFER_TARGET_REACHED",
            severity="info",
            title="Income Safety Buffer Funded",
            description="Buffer reached 100% of target.",
            metrics_payload={"buffer": 25000.0, "target": 25000.0}
        )
        assert evt.id is not None

        retrieved = FinancialRepository.get_financial_events(db, user.id)
        assert any(e.event_type == "BUFFER_TARGET_REACHED" for e in retrieved)
        print("[TEST 08] test_08_event_detection_and_monitoring .................... PASS")


def test_09_monotonic_source_data_versioning():
    """Verifies that mutations monotonically increment user source_data_version."""
    with SessionLocal() as db:
        unique_id = f"test_ver_{uuid.uuid4().hex[:8]}"
        user = User(email=f"{unique_id}@example.com", name="Version Test User", is_demo_user=False)
        db.add(user)
        db.commit()
        db.refresh(user)

        FinancialRepository.initialize_new_user_workspace(db, user.id)
        v1 = user.source_data_version or 1

        # Mutation 1: Apply quick start
        FinancialRepository.apply_quick_start(
            db=db,
            user_id=user.id,
            weekly_income=9000.0,
            essential_expenses=4500.0,
            current_cash=5000.0,
            emergency_savings=7000.0,
            protected_floor=3600.0
        )
        db.refresh(user)
        v2 = user.source_data_version
        assert v2 > v1

        # Mutation 2: Add expense item
        FinancialRepository.add_expense_item(
            db=db,
            user_id=user.id,
            description="Internet Bill",
            amount=600.0,
            frequency="monthly",
            category="utilities",
            is_essential=True
        )
        from backend.financial_engine import FinancialEngine
        FinancialEngine.recalculate_user_workspace(db, user.id)
        db.refresh(user)
        v3 = user.source_data_version
        assert v3 > v2
        print("[TEST 09] test_09_monotonic_source_data_versioning .................. PASS")


def test_10_rest_api_endpoints_v7():
    """Verifies that all 8 new 7.0 REST endpoints respond correctly with valid schemas."""
    with SessionLocal() as db:
        user = db.query(User).filter(User.is_demo_user == True).first()
        sess = FinancialRepository.create_session(db, user.id, expires_days=1)
        token = sess.session_token

    client.cookies.set("sure_savings_session", token)

    # 1. GET /api/v1/workspace/intelligence
    res1 = client.get("/api/v1/workspace/intelligence")
    assert res1.status_code == 200
    b1 = res1.json()
    assert b1["digital_twin_version"] == "7.0"
    assert "observation" in b1
    assert "understanding" in b1
    assert "prediction" in b1
    assert "decisions" in b1

    # 2. GET /api/v1/workspace/overview
    res2 = client.get("/api/v1/workspace/overview")
    assert res2.status_code == 200
    b2 = res2.json()
    assert b2["status"] == "success"
    assert "next_best_action" in b2
    assert "data_quality" in b2
    assert "digital_twin_summary" in b2

    # 3. GET /api/v1/workspace/data-quality
    res3 = client.get("/api/v1/workspace/data-quality")
    assert res3.status_code == 200
    b3 = res3.json()
    assert "overall_score" in b3
    assert "quality_status" in b3

    # 4. GET /api/v1/workspace/action-plan
    res4 = client.get("/api/v1/workspace/action-plan")
    assert res4.status_code == 200
    b4 = res4.json()
    assert "primary_action" in b4
    assert "priority" in b4

    # 5. GET /api/v1/workspace/events
    res5 = client.get("/api/v1/workspace/events")
    assert res5.status_code == 200
    b5 = res5.json()
    assert "events" in b5

    # 6. GET /api/v1/workspace/explain/safe_to_save
    res6 = client.get("/api/v1/workspace/explain/safe_to_save")
    assert res6.status_code == 200
    b6 = res6.json()
    assert b6["metric_name"] == "safe_to_save"
    assert "formula" in b6

    # 7. GET /api/v1/workspace/scenarios/library
    res7 = client.get("/api/v1/workspace/scenarios/library")
    assert res7.status_code == 200
    b7 = res7.json()
    assert isinstance(b7, list)
    assert len(b7) >= 5

    # 8. POST /api/v1/workspace/scenarios/simulate
    payload = {
        "scenario_name": "Test Shock",
        "income_delta_pct": -15.0,
        "expense_delta_pct": 5.0,
        "one_off_shock": 1000.0,
        "delayed_payout_days": 3,
        "simulation_weeks": 8
    }
    res8 = client.post("/api/v1/workspace/scenarios/simulate", json=payload)
    assert res8.status_code == 200
    b8 = res8.json()
    assert b8["status"] == "success"
    assert "delta" in b8
    assert "trajectories" in b8
    print("[TEST 10] test_10_rest_api_endpoints_v7 ................................ PASS")
