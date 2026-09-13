"""
SURE SAVINGS 5.0 / 6.0: Automated Test Suite
Validates:
1. New user zero state (0.0 monetary amounts, INSUFFICIENT_DATA status, no demo leakage).
2. Data readiness & maturity levels.
3. Quick-Start calibration & dynamic deterministic recalculation.
4. User A vs User B strict isolation (no cross-talk or shared state).
5. Canonical Arjun demo regression (preserves ₹8,400, ₹7,100, ₹6,800, ₹900, 74, 23).
6. Cash flow intraday timing gap discovery.
7. Income analytics data maturity requirements (>=2 weeks for volatility, >=4 weeks for forecast).
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import (
    Base, User, FinancialProfile, IncomeSource, ExpenseItem,
    LiquidityPosition, WeeklyIncomeHistory, ScheduledObligation, Goal
)
from backend.financial_engine import (
    recalculate_user_workspace, compute_data_readiness
)
from backend.services.income_service import IncomeAnalyticsService
from backend.services.cash_flow_service import CashFlowTimingService


@pytest.fixture
def db_session():
    """Isolated in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_new_user_zero_state(db_session):
    """New authenticated user must start with ₹0 money and honest INSUFFICIENT_DATA statuses."""
    user = User(
        id="usr_test_new_01",
        email="newuser@example.com",
        name="Priya Sharma",
        is_onboarded=True,
        is_demo_user=False,
        setup_completed=False,
        data_maturity_level=0,
        readiness_percentage=0
    )
    profile = FinancialProfile(
        user_id=user.id,
        current_income=0.0,
        stabilized_income=0.0,
        weekly_burn=0.0,
        protected_floor=0.0,
        current_buffer=0.0,
        buffer_target=0.0,
        surplus=0.0,
        recommended_contribution=0.0,
        free_pocket_liquidity=0.0,
        safe_to_use_above_floor=0.0,
        resilience_score=0,
        risk_score=0,
        current_coverage_weeks=0.0,
        resilience_status="INSUFFICIENT_DATA",
        risk_status="DATA_INCOMPLETE",
        forecast_status="INSUFFICIENT_DATA",
        volatility_status="INSUFFICIENT_DATA",
        cash_flow_status="NO_OBLIGATIONS"
    )
    db_session.add(user)
    db_session.add(profile)
    db_session.commit()

    # Recalculate
    recalculate_user_workspace(db_session, user.id)
    updated = user.profile
    assert updated.current_income == 0.0
    assert updated.current_buffer == 0.0
    assert updated.surplus == 0.0
    assert updated.recommended_contribution == 0.0
    assert updated.resilience_status == "INSUFFICIENT_DATA"
    assert updated.risk_status == "DATA_INCOMPLETE"
    assert updated.forecast_status in ["NOT_AVAILABLE", "INSUFFICIENT_DATA"]

    readiness = compute_data_readiness(db_session, user.id)
    assert readiness["readiness_percentage"] < 30
    assert readiness["maturity_level"] == 0
    assert "income_sources" in readiness["missing_requirements"]


def test_quick_start_calibration(db_session):
    """User entering 30-second Quick Start gets dynamic, non-zero deterministic calculations."""
    user = User(
        id="usr_quick_01",
        email="quick@example.com",
        name="Rahul Verma",
        is_onboarded=True,
        is_demo_user=False
    )
    profile = FinancialProfile(
        user_id=user.id,
        current_income=0.0,
        weekly_burn=0.0,
        protected_floor=0.0,
        current_buffer=0.0
    )
    db_session.add_all([user, profile])
    db_session.commit()

    # User inputs quick start data:
    # income: 10000, burn: 6000, cash: 8000, buffer: 5000, floor: 4000
    source = IncomeSource(user_id=user.id, name="Freelance Tech", typical_amount=10000.0, frequency="weekly")
    exp = ExpenseItem(user_id=user.id, description="Essential Rent & Food", amount=6000.0, frequency="weekly", is_essential=True)
    liq = LiquidityPosition(user_id=user.id, checking_cash=8000.0, protected_floor=4000.0, savings_balance=5000.0)
    db_session.add_all([source, exp, liq])
    db_session.commit()

    recalculate_user_workspace(db_session, user.id)
    updated = user.profile

    # Surplus = 10000 - 6000 = 4000
    assert updated.current_income == 10000.0
    assert updated.weekly_burn == 6000.0
    assert updated.surplus == 4000.0
    # Safe to save 70% cap = 4000 * 0.70 = 2800
    assert updated.recommended_contribution == 2800.0
    # Free pocket cash = 4000 - 2800 = 1200
    assert updated.free_pocket_liquidity == 1200.0
    # Current buffer = 5000
    assert updated.current_buffer == 5000.0
    # Runway = 5000 / 6000 = 0.8 weeks
    assert round(updated.current_coverage_weeks, 1) == 0.8


def test_user_a_vs_user_b_isolation(db_session):
    """User A (high income, surplus) and User B (tight income, deficit) must calculate independently with zero cross-talk."""
    user_a = User(id="usr_A", email="a@example.com", name="User A", is_onboarded=True)
    prof_a = FinancialProfile(user_id="usr_A")
    src_a = IncomeSource(user_id="usr_A", name="Lead Architect", typical_amount=12000.0, frequency="weekly")
    exp_a = ExpenseItem(user_id="usr_A", description="Household Essentials", amount=7000.0, frequency="weekly", is_essential=True)
    liq_a = LiquidityPosition(user_id="usr_A", checking_cash=20000.0, protected_floor=5000.0, savings_balance=15000.0)

    user_b = User(id="usr_B", email="b@example.com", name="User B", is_onboarded=True)
    prof_b = FinancialProfile(user_id="usr_B")
    src_b = IncomeSource(user_id="usr_B", name="Gig Courier", typical_amount=6000.0, frequency="weekly")
    exp_b = ExpenseItem(user_id="usr_B", description="Rent and EMI", amount=6500.0, frequency="weekly", is_essential=True)
    liq_b = LiquidityPosition(user_id="usr_B", checking_cash=3000.0, protected_floor=2000.0, savings_balance=1000.0)

    db_session.add_all([user_a, prof_a, src_a, exp_a, liq_a, user_b, prof_b, src_b, exp_b, liq_b])
    db_session.commit()

    recalculate_user_workspace(db_session, "usr_A")
    recalculate_user_workspace(db_session, "usr_B")
    updated_a = user_a.profile
    updated_b = user_b.profile

    # User A: surplus 5000, recommended 3500, buffer 15000, runway ~2.1 wks
    assert updated_a.current_income == 12000.0
    assert updated_a.surplus == 5000.0
    assert updated_a.recommended_contribution == 3500.0
    assert updated_a.current_buffer == 15000.0
    assert updated_a.current_coverage_weeks > 2.0

    # User B: income 6000 < expense 6500 -> surplus 0, recommended 0 (protection mode)
    assert updated_b.current_income == 6000.0
    assert updated_b.surplus == 0.0
    assert updated_b.recommended_contribution == 0.0
    assert updated_b.current_buffer == 1000.0
    assert updated_b.current_coverage_weeks < 0.5

    # Verification of zero cross-contamination
    assert updated_a.current_income != updated_b.current_income
    assert updated_a.surplus != updated_b.surplus
    assert updated_a.recommended_contribution != updated_b.recommended_contribution


def test_canonical_arjun_demo_preservation(db_session):
    """Arjun K. canonical demo profile must preserve hackathon demo baseline metrics."""
    arjun = User(
        id="usr_arjun_01",
        email="arjun.demo@suresavings.in",
        name="Arjun K.",
        is_onboarded=True,
        is_demo_user=True
    )
    prof_arjun = FinancialProfile(
        user_id="usr_arjun_01",
        current_income=8400.0,
        stabilized_income=7100.0,
        weekly_burn=4400.0,
        protected_floor=3500.0,
        current_buffer=6800.0,
        buffer_target=15000.0,
        surplus=1300.0,
        recommended_contribution=900.0,
        free_pocket_liquidity=400.0,
        safe_to_use_above_floor=3300.0,
        resilience_score=74,
        risk_score=23,
        current_coverage_weeks=1.5
    )
    db_session.add_all([arjun, prof_arjun])
    db_session.commit()

    recalculate_user_workspace(db_session, "usr_arjun_01")
    updated = arjun.profile
    assert updated.current_income == 8400.0
    assert updated.stabilized_income == 7100.0
    assert updated.current_buffer == 6800.0
    assert updated.surplus == 1300.0
    assert updated.recommended_contribution == 900.0
    assert updated.resilience_score == 74
    assert updated.risk_score == 23


def test_forecast_and_volatility_thresholds():
    """Income service must require >=4 data points for forecast and >=2 for volatility."""
    # 0 data points
    res_0 = IncomeAnalyticsService.analyze_history([], current_income=0.0)
    assert res_0["volatility_status"] == "NOT_AVAILABLE"
    assert res_0["forecast_status"] == "NOT_AVAILABLE"

    # 2 data points (volatility available, forecast insufficient)
    history_2 = [
        {"week": "Wk 1", "income": 5000.0, "is_current": False, "is_forecast": False},
        {"week": "Wk 2", "income": 6000.0, "is_current": False, "is_forecast": False}
    ]
    res_2 = IncomeAnalyticsService.analyze_history(history_2, current_income=6000.0)
    assert res_2["volatility_status"] == "AVAILABLE"
    assert res_2["forecast_status"] == "INSUFFICIENT_DATA"

    # 4 data points (both volatility and forecast unlocked)
    history_4 = [
        {"week": "Wk 1", "income": 5000.0, "is_current": False, "is_forecast": False},
        {"week": "Wk 2", "income": 6000.0, "is_current": False, "is_forecast": False},
        {"week": "Wk 3", "income": 5500.0, "is_current": False, "is_forecast": False},
        {"week": "Wk 4", "income": 7000.0, "is_current": False, "is_forecast": False}
    ]
    res_4 = IncomeAnalyticsService.analyze_history(history_4, current_income=7000.0)
    assert res_4["volatility_status"] == "AVAILABLE"
    assert res_4["forecast_status"] in ["BASIC", "HIGH", "AVAILABLE"]
    assert res_4["forecast_next_week"] > 0


def test_cash_flow_intraday_timing_gap():
    """Cash flow planner discovers intraday timing gap when outflow precedes inflow."""
    obligations = [
        ScheduledObligation(
            id="ob_emi",
            user_id="usr_gap",
            date_str="September 10, 2026",
            time_str="09:00 AM",
            description="HDFC EV Two-Wheeler EMI",
            amount=4500.0,
            category="Mobility Asset",
            is_essential=True
        )
    ]
    timeline_res = CashFlowTimingService.calculate_intraday_timeline(
        target_date="September 10, 2026",
        checking_floor=3500.0,
        buffer_reserve=3300.0,
        obligations=obligations
    )
    assert timeline_res is not None
    assert len(timeline_res["timeline"]) >= 1
    assert timeline_res["has_timing_gap"] is True
