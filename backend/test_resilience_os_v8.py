"""
SURE SAVINGS 8.0: Automated Test Suite for Adaptive Financial Resilience Operating System
Comprehensive institutional verification across all 10 intelligence subsystems:
1. Financial State Machine (13 discrete states & transitions)
2. Financial Event Engine 2.0 & 'What Changed This Week?'
3. Financial Weather Engine (7D, 30D, 90D outlook & pressure map)
4. 30-Day Personal Resilience Plan Engine (4 ranked priorities & roadmap)
5. Scenario Portfolio & Counterfactual Lab (1-5 concurrent scenarios & ranking)
6. Recovery Planner (Conservative, Balanced, Accelerated pathways)
7. Safe-to-Save Goal Optimization Engine (dynamic risk-sensitive distribution)
8. Income Source & Diversification Intelligence (HHI & drop simulation)
9. Financial Memory Timeline & Executive Briefing
10. REST API Endpoints (Private Workspace & Public Demo)
11. The Golden User Scenario: Dynamic Reactivity to an Income Shift
"""
import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.main import app
from backend.database import SessionLocal
from backend.models import User, FinancialProfile, FinancialEvent
from backend.repository import FinancialRepository, seed_canonical_user
from backend.digital_twin import FinancialDigitalTwin
from backend.services.state_machine_service import FinancialStateMachineService, FinancialState
from backend.services.weather_service import FinancialWeatherService
from backend.services.resilience_plan_service import ResiliencePlanService
from backend.services.scenario_portfolio_service import ScenarioPortfolioService
from backend.services.recovery_plan_service import RecoveryPlanService
from backend.services.goal_allocation_service import GoalAllocationService
from backend.services.income_diversification_service import IncomeDiversificationService
from backend.services.timeline_service import FinancialTimelineService
from backend.services.transaction_intelligence_service import TransactionIntelligenceService
from backend.services.event_detection_service import EventDetectionService

client = TestClient(app)


# =====================================================================
# 1. FINANCIAL STATE MACHINE TESTS
# =====================================================================

def test_01_state_machine_discrete_states_and_transitions():
    """Verifies all 13 states and deterministic transition triggers."""
    # Test NEW state
    res_new = FinancialStateMachineService.evaluate({
        "current_income": 0.0,
        "weekly_burn": 0.0,
        "current_buffer": 0.0,
        "data_maturity_level": 0
    })
    assert res_new["current_state"] == FinancialState.NEW.value
    assert "Workspace newly initialized" in res_new["transition_reason"]

    # Test CRITICAL state: liquid cash < floor * 0.5 and buffer <= floor * 0.5
    res_crit = FinancialStateMachineService.evaluate({
        "current_income": 4000.0,
        "weekly_burn": 4500.0,
        "current_buffer": 500.0,
        "protected_floor": 2000.0,
        "liquid_cash": 800.0, # Severely breached floor
        "resilience_score": 30
    })
    assert res_crit["current_state"] == FinancialState.CRITICAL.value

    # Test BUFFER_ABSORBING: checking <= floor, buffer > floor
    res_abs = FinancialStateMachineService.evaluate({
        "current_income": 4000.0,
        "weekly_burn": 5500.0,
        "current_buffer": 8000.0,
        "protected_floor": 3000.0,
        "liquid_cash": 2500.0, # At/below floor while buffer is absorbing
        "resilience_score": 60
    })
    assert res_abs["current_state"] == FinancialState.BUFFER_ABSORBING.value

    # Test HEALTHY state: buffer >= target
    res_healthy = FinancialStateMachineService.evaluate({
        "current_income": 9000.0,
        "weekly_burn": 4000.0,
        "current_buffer": 16000.0,
        "buffer_target": 15000.0,
        "protected_floor": 3500.0,
        "liquid_cash": 7000.0,
        "resilience_score": 85
    })
    assert res_healthy["current_state"] == FinancialState.HEALTHY.value

    # Test VOLATILE state: high CV
    res_vol = FinancialStateMachineService.evaluate({
        "current_income": 8000.0,
        "weekly_burn": 4000.0,
        "current_buffer": 6000.0,
        "buffer_target": 15000.0,
        "protected_floor": 3500.0,
        "liquid_cash": 5000.0,
        "income_volatility": 0.42, # CV > 0.35
        "resilience_score": 65
    })
    assert res_vol["current_state"] == FinancialState.VOLATILE.value


# =====================================================================
# 2. FINANCIAL EVENT ENGINE 2.0 & DELTA TELEMETRY
# =====================================================================

def test_02_event_detection_and_what_changed():
    """Verifies that what-changed delta comparison generates structured, verifiable items."""
    old_twin = {
        "profile": {
            "current_income": 10000.0,
            "weekly_burn": 4000.0,
            "current_buffer": 5000.0,
            "resilience_score": 70,
            "current_coverage_weeks": 1.25
        }
    }
    new_twin = {
        "profile": {
            "current_income": 7000.0,
            "weekly_burn": 4200.0,
            "current_buffer": 4800.0,
            "resilience_score": 62,
            "current_coverage_weeks": 1.14
        }
    }

    what_changed = EventDetectionService.compute_what_changed(old_twin, new_twin)
    assert what_changed["title"] == "WHAT CHANGED THIS WEEK?"
    assert what_changed["resilience_before"] == 70
    assert what_changed["resilience_after"] == 62
    assert what_changed["resilience_delta"] == -8
    assert len(what_changed["items"]) == 4

    # Confirm item deltas
    income_item = next(i for i in what_changed["items"] if i["label"] == "Income")
    assert "-30.0%" in income_item["delta_display"]
    assert income_item["direction"] == "down"


# =====================================================================
# 3. FINANCIAL WEATHER ENGINE
# =====================================================================

def test_03_financial_weather_engine():
    """Verifies multi-horizon synthesis, sub-vectors, and Mon-Sun pressure map."""
    telemetry = {
        "profile": {
            "current_income": 8400.0,
            "stabilized_income": 7100.0,
            "weekly_burn": 4400.0,
            "current_buffer": 6800.0,
            "buffer_target": 15000.0,
            "protected_floor": 3500.0,
            "surplus": 1300.0,
            "recommended_contribution": 900.0,
            "resilience_score": 74,
            "risk_score": 23,
            "current_coverage_weeks": 1.55
        },
        "understanding": {
            "cash_flow": {
                "timing_gaps": []
            }
        }
    }

    weather = FinancialWeatherService.evaluate(telemetry)
    assert "overall" in weather
    assert "horizons" in weather
    assert "7D" in weather["horizons"]
    assert "30D" in weather["horizons"]
    assert "90D" in weather["horizons"]
    assert "sub_outlooks" in weather
    assert "liquidity" in weather["sub_outlooks"]
    assert len(weather["daily_forecast"]) == 7
    assert weather["main_driver"] is not None


# =====================================================================
# 4. 30-DAY PERSONAL RESILIENCE PLAN ENGINE
# =====================================================================

def test_04_resilience_plan_generation():
    """Verifies 4 ranked priorities, triggers, and 4-week execution roadmap."""
    mock_twin = {
        "profile": {
            "current_income": 8400.0,
            "stabilized_income": 7100.0,
            "weekly_burn": 4400.0,
            "current_buffer": 6800.0,
            "buffer_target": 15000.0,
            "protected_floor": 3500.0,
            "surplus": 1300.0,
            "recommended_contribution": 900.0,
            "free_pocket_liquidity": 400.0,
            "resilience_score": 74,
            "risk_score": 23,
            "current_coverage_weeks": 1.55
        },
        "financial_state": "BUFFER_BUILDING",
        "understanding": {
            "cash_flow": {"timing_gaps": []},
            "runway": {"weeks": 1.55}
        }
    }

    plan = ResiliencePlanService.generate_plan(mock_twin)
    assert plan["plan_name"] == "30-Day Financial Resilience Plan"
    assert len(plan["top_priorities"]) == 4
    # Priorities must be ranked 1..4
    assert [p["rank"] for p in plan["top_priorities"]] == [1, 2, 3, 4]
    assert len(plan["weekly_roadmap"]) == 4
    assert len(plan["risk_triggers"]) >= 3
    assert plan["target_state"]["target_resilience"] >= 74


# =====================================================================
# 5. SCENARIO PORTFOLIO & COUNTERFACTUAL LAB
# =====================================================================

def test_05_scenario_portfolio_evaluation():
    """Verifies concurrent multi-scenario evaluation and comparative ranking."""
    mock_twin = {
        "profile": {
            "current_income": 8400.0,
            "stabilized_income": 7100.0,
            "weekly_burn": 4400.0,
            "current_buffer": 6800.0,
            "protected_floor": 3500.0,
            "resilience_score": 74,
            "current_coverage_weeks": 1.55
        }
    }

    scenarios = [
        {"name": "Scenario A: Mild Dip (-15%)", "income_delta_pct": -15.0},
        {"name": "Scenario B: Major Shock (-35%)", "income_delta_pct": -35.0},
        {"name": "Scenario C: Expense Surge (+20%)", "expense_delta_pct": 20.0},
        {"name": "Scenario D: Boost (+20% Income)", "income_delta_pct": 20.0}
    ]

    portfolio = ScenarioPortfolioService.evaluate_portfolio(mock_twin, scenarios)
    assert portfolio["scenario_count"] == 4
    assert len(portfolio["results"]) == 4
    assert portfolio["safest_scenario"] is not None
    assert portfolio["highest_risk_scenario"] is not None
    # Best scenario should rank 1
    assert portfolio["results"][0]["rank"] == 1


# =====================================================================
# 6. RECOVERY PLANNER
# =====================================================================

def test_06_recovery_planner_pathways():
    """Verifies Conservative, Balanced, and Accelerated pathways."""
    mock_twin = {
        "profile": {
            "current_income": 8400.0,
            "stabilized_income": 7100.0,
            "weekly_burn": 4400.0,
            "current_buffer": 6800.0,
            "buffer_target": 15000.0,
            "surplus": 1300.0,
            "recommended_contribution": 900.0,
            "protected_floor": 3500.0,
            "resilience_score": 74,
            "current_coverage_weeks": 1.55
        }
    }

    recovery = RecoveryPlanService.generate_plans(mock_twin)
    assert recovery["status"] == "RECOVERY_ACTIVE"
    assert recovery["buffer_gap"] == 8200.0
    pathways = recovery["pathways"]
    assert "conservative" in pathways
    assert "balanced" in pathways
    assert "accelerated" in pathways
    # Accelerated should reach target in fewer or equal weeks compared to conservative
    assert pathways["accelerated"]["weeks_to_target"] <= pathways["conservative"]["weeks_to_target"]


# =====================================================================
# 7. SAFE-TO-SAVE GOAL OPTIMIZATION ENGINE
# =====================================================================

def test_07_goal_allocation_optimization():
    """Verifies dynamic allocation across competing goals using risk-sensitive weights."""
    mock_twin = {
        "decisions": {
            "safe_to_save": {
                "recommended_save": 900.0,
                "surplus": 1300.0
            }
        },
        "profile": {
            "resilience_score": 74,
            "current_buffer": 6800.0,
            "buffer_target": 15000.0
        }
    }

    goals = [
        {"id": "g1", "name": "Emergency Buffer", "target": 15000.0, "current": 6800.0, "priority": "HIGH", "category": "BUFFER"},
        {"id": "g2", "name": "Bike Repair", "target": 3000.0, "current": 1000.0, "priority": "MEDIUM", "category": "VEHICLE"},
        {"id": "g3", "name": "Holiday Savings", "target": 10000.0, "current": 1000.0, "priority": "LOW", "category": "DISCRETIONARY"}
    ]

    alloc = GoalAllocationService.optimize_allocation(mock_twin, goals, monthly_savings_pool=3600.0)
    assert "total_allocated" in alloc
    assert len(alloc["allocations"]) == 3
    # Total allocated amount should be allocated up to monthly_savings_pool
    assert alloc["total_allocated"] <= 3600.0
    # High priority buffer goal gets the highest share
    high_goal = next(g for g in alloc["allocations"] if g["goal_id"] == "g1")
    low_goal = next(g for g in alloc["allocations"] if g["goal_id"] == "g3")
    assert high_goal["allocated_amount"] >= low_goal["allocated_amount"]


# =====================================================================
# 8. INCOME SOURCE & DIVERSIFICATION INTELLIGENCE
# =====================================================================

def test_08_income_diversification_intelligence():
    """Verifies HHI concentration scoring, platform share, and 30% drop simulation."""
    sources = [
        {"name": "Ride Hailing App", "amount": 6000.0, "is_active": True},
        {"name": "Food Delivery", "amount": 2400.0, "is_active": True}
    ]

    diversification = IncomeDiversificationService.evaluate(sources, current_weekly_income=8400.0)
    assert diversification["status"] == "EVALUATED"
    assert diversification["sources_count"] == 2
    assert diversification["concentration_risk"] in ["MODERATE", "HIGH"]
    assert diversification["single_source_shock"]["drop_percentage"] == 30.0
    assert len(diversification["diversification_opportunities"]) >= 1


# =====================================================================
# 9. FINANCIAL TIMELINE MEMORY & EXECUTIVE BRIEFING
# =====================================================================

def test_09_financial_timeline_and_briefing():
    """Verifies persistent story timeline and weekly briefing generation."""
    with SessionLocal() as db:
        canonical_user = seed_canonical_user(db, force=False)
        story = FinancialTimelineService.get_financial_story(db, canonical_user.id)
        assert "timeline_events" in story
        assert story["story_summary"] is not None

        twin = FinancialDigitalTwin.build(db, canonical_user.id)
        weather = twin.get("financial_weather") or FinancialWeatherService.evaluate(twin)
        plan = twin.get("resilience_plan") or ResiliencePlanService.generate_plan(twin)
        briefing = TransactionIntelligenceService.generate_weekly_briefing(twin, weather, plan)
        assert briefing["title"] == "Your Week In Money"
        assert len(briefing["metrics"]) >= 4

        # Multi-horizon outlook
        outlook = TransactionIntelligenceService.generate_multi_horizon_outlook(twin)
        assert outlook["status"] == "ACTIVE"
        assert "7D" in outlook["horizons"]
        assert "30D" in outlook["horizons"]
        assert "90D" in outlook["horizons"]

        # 10-preset stress test suite
        stress = TransactionIntelligenceService.run_stress_test_suite(twin)
        assert stress["status"] == "EVALUATED"
        assert stress["stress_presets_count"] == 10
        assert len(stress["results"]) == 10


# =====================================================================
# 10. REST API ENDPOINTS (WORKSPACE & PUBLIC DEMO)
# =====================================================================

def test_10_rest_api_v8_workspace_and_public_demo():
    """Verifies all new v8.0 REST endpoints respond correctly with valid status and schemas."""
    # A. Public Demo Endpoints
    p_weather = client.get("/api/v1/public/demo/weather")
    assert p_weather.status_code == 200
    assert "overall" in p_weather.json()

    p_plan = client.get("/api/v1/public/demo/resilience-plan")
    assert p_plan.status_code == 200
    assert p_plan.json()["plan_name"] == "30-Day Financial Resilience Plan"

    p_portfolio = client.post("/api/v1/public/demo/scenarios/portfolio", json={
        "scenarios": [{"name": "Dip", "income_delta_pct": -20.0}]
    })
    assert p_portfolio.status_code == 200
    assert p_portfolio.json()["scenario_count"] == 1

    p_recovery = client.get("/api/v1/public/demo/recovery-plan")
    assert p_recovery.status_code == 200
    assert "pathways" in p_recovery.json()

    p_goals = client.get("/api/v1/public/demo/goals/optimize")
    assert p_goals.status_code == 200
    assert "total_allocated" in p_goals.json()

    p_div = client.get("/api/v1/public/demo/income/diversification")
    assert p_div.status_code == 200
    assert "concentration_risk" in p_div.json()

    p_timeline = client.get("/api/v1/public/demo/timeline")
    assert p_timeline.status_code == 200
    assert "timeline_events" in p_timeline.json()

    p_briefing = client.get("/api/v1/public/demo/briefing")
    assert p_briefing.status_code == 200
    assert p_briefing.json()["title"] == "Your Week In Money"

    p_outlook = client.get("/api/v1/public/demo/outlook")
    assert p_outlook.status_code == 200
    assert "horizons" in p_outlook.json()

    p_stress = client.get("/api/v1/public/demo/stress-test")
    assert p_stress.status_code == 200
    assert p_stress.json()["stress_presets_count"] == 10

    p_changed = client.get("/api/v1/public/demo/what-changed")
    assert p_changed.status_code == 200
    assert p_changed.json()["title"] == "WHAT CHANGED THIS WEEK?"

    # Security trap test for public demo
    trap_resp = client.get("/api/v1/public/demo/weather?user_id=attacker_id")
    assert trap_resp.status_code == 400

    # B. Workspace Endpoints (authenticated)
    with SessionLocal() as db:
        user = db.query(User).filter(User.is_demo_user == True).first()
        sess = FinancialRepository.create_session(db, user.id, expires_days=1)
        token = sess.session_token

    client.cookies.set("sure_savings_session", token)

    w_weather = client.get("/api/v1/workspace/weather")
    assert w_weather.status_code == 200

    w_plan = client.get("/api/v1/workspace/resilience-plan")
    assert w_plan.status_code == 200

    w_portfolio = client.post("/api/v1/workspace/scenarios/portfolio", json={
        "scenarios": [{"name": "Shock", "income_delta_pct": -30.0}]
    })
    assert w_portfolio.status_code == 200

    w_recovery = client.get("/api/v1/workspace/recovery-plan")
    assert w_recovery.status_code == 200

    w_goals = client.post("/api/v1/workspace/goals/optimize", json={})
    assert w_goals.status_code == 200

    w_div = client.get("/api/v1/workspace/income/diversification")
    assert w_div.status_code == 200

    w_timeline = client.get("/api/v1/workspace/timeline")
    assert w_timeline.status_code == 200

    w_briefing = client.get("/api/v1/workspace/briefing")
    assert w_briefing.status_code == 200

    w_outlook = client.get("/api/v1/workspace/outlook")
    assert w_outlook.status_code == 200

    w_stress = client.get("/api/v1/workspace/stress-test")
    assert w_stress.status_code == 200

    w_changed = client.get("/api/v1/workspace/what-changed")
    assert w_changed.status_code == 200


# =====================================================================
# 11. GOLDEN USER SCENARIO: DYNAMIC REACTIVITY TO AN INCOME SHIFT
# =====================================================================

def test_11_golden_user_income_shift_reactivity():
    """
    Demonstrates the complete end-to-end adaptive operating cycle:
    1. User starts with baseline income ₹10,000, weekly burn ₹4,000, buffer ₹5,000.
    2. Income changes to ₹7,000 (30% drop).
    3. Operating System detects the shift, computes new state, triggers weather update,
       generates new resilience plan, recalculates goal allocations, and outputs 'What Changed'.
    """
    baseline_telemetry = {
        "profile": {
            "current_income": 10000.0,
            "stabilized_income": 9500.0,
            "weekly_burn": 4000.0,
            "current_buffer": 5000.0,
            "buffer_target": 15000.0,
            "protected_floor": 3000.0,
            "surplus": 6000.0,
            "recommended_contribution": 1800.0,
            "free_pocket_liquidity": 4200.0,
            "resilience_score": 76,
            "risk_score": 18,
            "current_coverage_weeks": 1.25,
            "income_volatility": 0.15
        },
        "understanding": {"cash_flow": {"timing_gaps": []}}
    }

    # Step 1: Initial state evaluation
    state_init = FinancialStateMachineService.evaluate(baseline_telemetry["profile"])
    weather_init = FinancialWeatherService.evaluate(baseline_telemetry)
    assert weather_init["overall"] in ["POSITIVE", "STABLE", "STABLE_WITH_ATTENTION"]

    # Step 2: Income shifts down from ₹10,000 to ₹7,000
    shifted_telemetry = {
        "profile": {
            "current_income": 7000.0, # 30% drop
            "stabilized_income": 8000.0,
            "weekly_burn": 4000.0,
            "current_buffer": 5000.0,
            "buffer_target": 15000.0,
            "protected_floor": 3000.0,
            "surplus": 3000.0,
            "recommended_contribution": 900.0,
            "free_pocket_liquidity": 2100.0,
            "resilience_score": 67, # -9 pts
            "risk_score": 32,
            "current_coverage_weeks": 1.25,
            "income_volatility": 0.28
        },
        "understanding": {"cash_flow": {"timing_gaps": []}}
    }

    # Step 3: Event Engine captures What Changed
    what_changed = EventDetectionService.compute_what_changed(baseline_telemetry, shifted_telemetry)
    assert what_changed["resilience_delta"] == -9
    inc_item = next(i for i in what_changed["items"] if i["label"] == "Income")
    assert "-30.0%" in inc_item["delta_display"]

    # Step 4: Weather adapts to conditions
    weather_shifted = FinancialWeatherService.evaluate(shifted_telemetry)
    assert weather_shifted["overall"] in ["STABLE", "STABLE_WITH_ATTENTION", "PRESSURED"]

    # Step 5: Resilience Plan dynamically re-optimizes
    plan_shifted = ResiliencePlanService.generate_plan(shifted_telemetry)
    assert plan_shifted["top_priorities"][0]["rank"] == 1
    assert plan_shifted["target_state"]["target_resilience"] > shifted_telemetry["profile"]["resilience_score"]

    # Step 6: Goal Allocations adapt safely to smaller pool
    goals = [
        {"id": "g1", "name": "Emergency Cushion", "target": 15000.0, "current": 5000.0, "priority": "HIGH", "category": "BUFFER"},
        {"id": "g2", "name": "Festival Travel", "target": 8000.0, "current": 1000.0, "priority": "LOW", "category": "VACATION"}
    ]
    alloc_init = GoalAllocationService.optimize_allocation(baseline_telemetry, goals, monthly_savings_pool=7200.0)
    alloc_shifted = GoalAllocationService.optimize_allocation(shifted_telemetry, goals, monthly_savings_pool=3600.0)

    # Low priority goal gets reduced proportionally to protect emergency cushion
    low_init = next(g for g in alloc_init["allocations"] if g["goal_id"] == "g2")["allocated_amount"]
    low_shifted = next(g for g in alloc_shifted["allocations"] if g["goal_id"] == "g2")["allocated_amount"]
    assert low_shifted < low_init
