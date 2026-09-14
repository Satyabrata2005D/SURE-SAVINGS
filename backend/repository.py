"""
SURE SAVINGS 2.0: Central Repository & Data Access Layer
Provides atomic operations, server-side pagination, aggregation queries,
idempotency protection, and automatic seeding for canonical and large datasets.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
import json
import math
import secrets

def utc_now() -> datetime:
    """Return timezone-aware UTC datetime converted to naive UTC for SQLite compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

from backend.database import Base, engine, SessionLocal
from backend.models import (
    User, FinancialProfile, WeeklyIncomeHistory,
    LedgerTransaction, ScheduledObligation, BufferLedgerEvent,
    AuditTrace, Recommendation, FinancialSnapshot, UserSession, EmailOTP,
    IncomeSource, ExpenseItem, LiquidityPosition, Goal, FinancialEvent, CalendarEvent,
    BankConnection, BankAccount, BankConsent, BankDataSession, BankTransaction, BankSyncRun
)
from backend.policy import DEFAULT_POLICY
from backend.synthetic_data import (
    get_canonical_user_profile,
    get_canonical_weekly_history,
    get_canonical_current_inflows,
    get_canonical_scheduled_outflows,
    get_canonical_activity_log,
    get_canonical_ledger_history
)
from backend.services.income_service import IncomeAnalyticsService, StabilizedIncomeService
from backend.services.expense_service import ExpenseAnalyticsService
from backend.services.cash_flow_service import CashFlowTimingService
from backend.services.savings_service import SavingsOptimizationService
from backend.services.resilience_service import ResilienceService
from backend.services.risk_service import RiskService
from backend.services.scenario_service import ScenarioSimulationService
from backend.services.audit_service import AuditService

def init_database():
    """Create all tables in the database and ensure column schemas are current"""
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration for SQLite to ensure added columns exist in existing databases
    with engine.connect() as conn:
        # Check users table
        existing_user_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()}
        user_col_defs = {
            "income_type": "TEXT DEFAULT 'gig'",
            "setup_step": "INTEGER DEFAULT 0",
            "setup_completed": "BOOLEAN DEFAULT 0",
            "data_maturity_level": "INTEGER DEFAULT 0",
            "readiness_percentage": "FLOAT DEFAULT 0.0",
            "source_data_version": "INTEGER DEFAULT 1",
            "behavior_profile": "TEXT DEFAULT 'STABLE'",
            "data_quality_score": "FLOAT DEFAULT 0.0",
            "data_quality_status": "TEXT DEFAULT 'INCOMPLETE'",
            "preferred_locale": "TEXT DEFAULT 'en-IN'",
        }
        for col, col_type in user_col_defs.items():
            if col not in existing_user_cols:
                conn.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {col} {col_type}")

        # Check financial_profiles table
        existing_prof_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(financial_profiles)").fetchall()}
        prof_col_defs = {
            "forecast_status": "TEXT DEFAULT 'NOT_AVAILABLE'",
            "volatility_status": "TEXT DEFAULT 'NOT_AVAILABLE'",
            "resilience_status": "TEXT DEFAULT 'INSUFFICIENT_DATA'",
            "risk_status": "TEXT DEFAULT 'DATA_INCOMPLETE'",
            "cash_flow_status": "TEXT DEFAULT 'AWAITING_OBLIGATIONS'",
            "weekly_discretionary_burn": "FLOAT DEFAULT 0.0",
            "buffer_target_weeks": "FLOAT DEFAULT 4.0",
        }
        for col, col_type in prof_col_defs.items():
            if col not in existing_prof_cols:
                conn.exec_driver_sql(f"ALTER TABLE financial_profiles ADD COLUMN {col} {col_type}")

        # Check weekly_income_history table
        existing_wh_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(weekly_income_history)").fetchall()}
        wh_col_defs = {
            "source": "TEXT DEFAULT 'General'",
            "is_current": "BOOLEAN DEFAULT 0",
            "is_forecast": "BOOLEAN DEFAULT 0",
        }
        for col, col_type in wh_col_defs.items():
            if col not in existing_wh_cols:
                conn.exec_driver_sql(f"ALTER TABLE weekly_income_history ADD COLUMN {col} {col_type}")

        # Check ledger_transactions table
        existing_tx_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(ledger_transactions)").fetchall()}
        tx_col_defs = {
            "is_essential": "BOOLEAN DEFAULT 0",
            "raw_payload": "TEXT",
        }
        for col, col_type in tx_col_defs.items():
            if col not in existing_tx_cols:
                conn.exec_driver_sql(f"ALTER TABLE ledger_transactions ADD COLUMN {col} {col_type}")

        # Check scheduled_obligations table
        existing_obl_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(scheduled_obligations)").fetchall()}
        obl_col_defs = {
            "timing_risk": "BOOLEAN DEFAULT 0",
            "timing_note": "TEXT",
        }
        for col, col_type in obl_col_defs.items():
            if col not in existing_obl_cols:
                conn.exec_driver_sql(f"ALTER TABLE scheduled_obligations ADD COLUMN {col} {col_type}")

        # Check financial_events table
        existing_evt_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(financial_events)").fetchall()}
        evt_col_defs = {
            "source": "TEXT DEFAULT 'ENGINE'",
            "before_state": "TEXT",
            "after_state": "TEXT",
        }
        for col, col_type in evt_col_defs.items():
            if col not in existing_evt_cols:
                conn.exec_driver_sql(f"ALTER TABLE financial_events ADD COLUMN {col} {col_type}")

        conn.commit()


def seed_canonical_user(db: Session, force: bool = False) -> User:
    """
    Seeds the canonical Arjun K. persona into the database.
    If already present and force is False, returns existing user.
    """
    user = db.query(User).filter(User.id == "usr_arjun_01").first()
    if user and not force:
        return user

    if user and force:
        # Clear child records to reset financial state while preserving active user sessions
        db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).delete()
        db.query(WeeklyIncomeHistory).filter(WeeklyIncomeHistory.user_id == user.id).delete()
        db.query(LedgerTransaction).filter(LedgerTransaction.user_id == user.id).delete()
        db.query(ScheduledObligation).filter(ScheduledObligation.user_id == user.id).delete()
        db.query(BufferLedgerEvent).filter(BufferLedgerEvent.user_id == user.id).delete()
        db.query(Recommendation).filter(Recommendation.user_id == user.id).delete()
        db.query(FinancialSnapshot).filter(FinancialSnapshot.user_id == user.id).delete()
        db.query(AuditTrace).filter(AuditTrace.user_id == user.id).delete()
        db.commit()

    if not user:
        # 1. Create User
        user = User(
            id="usr_arjun_01",
            google_subject_id="demo_google_sub_arjun_01",
            email="arjun.k@suresavings.demo",
            email_verified=True,
            name="Arjun K.",
            display_name="Arjun K.",
            initials="AK",
            occupation="Gig Platform Worker",
            title="Delivery & Freelance Lead",
            currency="INR",
            is_demo_user=True
        )
        db.add(user)
        db.flush()

    # 2. Create Financial Profile
    p_data = get_canonical_user_profile()
    profile = FinancialProfile(
        user_id=user.id,
        current_week=p_data["current_week"],
        current_income=p_data["current_income"],
        stabilized_income=p_data["stabilized_income"],
        forecast_next_week=p_data["forecast_next_week"],
        forecast_confidence=p_data["forecast_confidence"],
        income_volatility=p_data["income_volatility"],
        current_buffer=p_data["current_buffer"],
        buffer_target=p_data["buffer_target"],
        protected_floor=p_data["protected_floor"],
        weekly_burn=p_data["weekly_burn"],
        current_coverage_weeks=p_data["current_coverage_weeks"],
        safe_to_use_above_floor=p_data["safe_to_use_above_floor"],
        surplus=p_data["surplus"],
        recommended_contribution=p_data["recommended_contribution"],
        free_pocket_liquidity=p_data["free_pocket_liquidity"],
        resilience_score=p_data["resilience_score"],
        risk_score=p_data["risk_score"]
    )
    db.add(profile)

    # 3. Seed 12-Week Rolling History
    history_data = get_canonical_weekly_history()
    for item in history_data:
        wh = WeeklyIncomeHistory(
            user_id=user.id,
            week=item["week"],
            income=item["income"],
            stabilized=item.get("stabilized", 7100.0),
            status=item.get("status", "Normal"),
            is_current=item.get("current", False),
            is_forecast=item.get("forecast", False)
        )
        db.add(wh)

    # 4. Seed Canonical 25-Item Ledger Transactions
    ledger_items = get_canonical_ledger_history()
    for item in ledger_items:
        tx = LedgerTransaction(
            id=item["id"],
            user_id=user.id,
            date_str=item["date"],
            source=item["source"],
            platform=item["platform"],
            category=item["category"],
            direction=item["direction"],
            amount=item["amount"],
            status=item["status"],
            is_essential=item.get("essential", False)
        )
        db.add(tx)

    # 5. Seed Scheduled Obligations (Calendar & Planner)
    outflows = get_canonical_scheduled_outflows()
    for out in outflows:
        obl = ScheduledObligation(
            id=out["id"],
            user_id=user.id,
            date_str=out["date"],
            time_str=out.get("time", "09:00 AM"),
            description=out["description"],
            category=out["category"],
            type=out["type"],
            amount=out["amount"],
            is_essential=out.get("essential", True),
            impact=out.get("impact", "Safe"),
            timing_risk=out.get("timing_risk", False),
            timing_note=out.get("timing_note")
        )
        db.add(obl)

    # 6. Seed Active Recommendation
    rec = Recommendation(
        id="rec_w36_canonical",
        user_id=user.id,
        title="Save ₹900 while preserving ₹400 free pocket liquidity and ₹3,500 cash floor.",
        recommended_amount=900.0,
        surplus=1300.0,
        free_pocket_cash=400.0,
        protected_floor=3500.0,
        status="PENDING"
    )
    db.add(rec)

    # 7. Seed Initial Baseline Snapshot
    snap = FinancialSnapshot(
        user_id=user.id,
        current_buffer=6800.0,
        resilience_score=74,
        risk_score=23,
        coverage_weeks=1.5,
        actual_income=8400.0,
        stabilized_income=7100.0
    )
    db.add(snap)

    # 8. Seed Initial Audit Trace
    audit = AuditTrace(
        user_id=user.id,
        engine_version="v2.5",
        verification_status="PASS",
        inputs_json=json.dumps({
            "actual_income": 8400.0,
            "stabilized_baseline": 7100.0,
            "essential_weekly_burn": 4400.0,
            "protected_cash_floor": 3500.0,
            "current_buffer": 6800.0
        }),
        calculation_json=json.dumps({
            "surplus": 1300.0,
            "policy_cap": 0.70,
            "raw_allocation": 910.0,
            "buffer_gap": 8200.0
        }),
        recommendation_json=json.dumps({
            "recommended_allocation": 900.0,
            "free_pocket_cash": 400.0,
            "new_buffer": 7700.0,
            "new_coverage": 1.7
        })
    )
    db.add(audit)

    db.commit()
    db.refresh(user)
    return user

class FinancialRepository:
    """Data access repository ensuring ACID transactional integrity and high performance"""

    @staticmethod
    def get_user_by_google_id(db: Session, google_sub: str) -> Optional[User]:
        return db.query(User).filter(User.google_subject_id == google_sub).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(func.lower(User.email) == email.lower()).first()

    @staticmethod
    def create_or_update_google_user(db: Session, claims: Dict[str, Any]) -> User:
        """
        Idempotently finds or creates a user based on Google identity claims.
        """
        google_sub = claims.get("google_subject_id")
        user = None
        if google_sub:
            user = FinancialRepository.get_user_by_google_id(db, google_sub)

        email = claims.get("email")
        if not user and email:
            user = FinancialRepository.get_user_by_email(db, email)
            if user and not user.google_subject_id:
                user.google_subject_id = google_sub

        if user:
            user.last_login_at = utc_now()
            if claims.get("picture"):
                user.avatar_url = claims.get("picture")
            if claims.get("name"):
                user.name = claims.get("name")
            db.commit()
            db.refresh(user)
            return user

        # Create fresh user
        name = claims.get("name", "New User")
        parts = name.split()
        initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper() if parts else "U"

        user = User(
            google_subject_id=google_sub,
            email=email,
            email_verified=claims.get("email_verified", False),
            name=name,
            display_name=name,
            first_name=claims.get("given_name"),
            last_name=claims.get("family_name"),
            avatar_url=claims.get("picture"),
            initials=initials,
            occupation="Independent Professional",
            title="SURE SAVINGS Member",
            currency="INR",
            locale=claims.get("locale", "en-IN"),
            is_demo_user=False,
            last_login_at=utc_now()
        )
        db.add(user)
        db.flush()

        # Initialize clean, isolated workspace
        FinancialRepository.initialize_new_user_workspace(db, user.id)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def initialize_new_user_workspace(db: Session, user_id: str) -> FinancialProfile:
        """
        Initializes an isolated, clean financial workspace for a new user.
        Starts with zero monetary balances and INSUFFICIENT_DATA analytical status.
        Does not copy another user's transactions, history, or demo calibrations.
        """
        prof = FinancialProfile(
            user_id=user_id,
            current_week="Week 1",
            current_income=0.0,
            stabilized_income=0.0,
            forecast_next_week=0.0,
            forecast_confidence=0.0,
            income_volatility=0.0,
            current_buffer=0.0,
            buffer_target=0.0,
            buffer_target_weeks=4.0,
            protected_floor=0.0,
            weekly_burn=0.0,
            weekly_discretionary_burn=0.0,
            current_coverage_weeks=0.0,
            safe_to_use_above_floor=0.0,
            buffer_state="BUILDING",
            surplus=0.0,
            recommended_contribution=0.0,
            free_pocket_liquidity=0.0,
            resilience_score=0,
            risk_score=0,
            forecast_status="NOT_AVAILABLE",
            volatility_status="NOT_AVAILABLE",
            resilience_status="INSUFFICIENT_DATA",
            risk_status="DATA_INCOMPLETE",
            cash_flow_status="AWAITING_OBLIGATIONS"
        )
        db.add(prof)

        # Initialize clean liquidity position
        liq = LiquidityPosition(
            user_id=user_id,
            checking_cash=0.0,
            savings_balance=0.0,
            physical_cash=0.0,
            total_liquid_cash=0.0,
            protected_floor=0.0,
            floor_preference="CALCULATED",
            floor_reason="Awaiting expense profile to compute safe floor."
        )
        db.add(liq)

        # Add initial baseline snapshot
        snap = FinancialSnapshot(
            user_id=user_id,
            current_buffer=0.0,
            resilience_score=0,
            risk_score=0,
            coverage_weeks=0.0,
            actual_income=0.0,
            stabilized_income=0.0
        )
        db.add(snap)
        db.flush()
        return prof

    @staticmethod
    def create_session(
        db: Session,
        user_id: str,
        expires_days: int = 7,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Generates a secure server-side session."""
        token = secrets.token_urlsafe(64)
        expires_at = utc_now() + timedelta(days=expires_days)
        session = UserSession(
            session_token=token,
            user_id=user_id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent[:250] if user_agent else None,
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def invalidate_session(db: Session, session_token: str) -> bool:
        """Deactivates a session upon logout."""
        session = db.query(UserSession).filter(UserSession.session_token == session_token).first()
        if session:
            session.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def create_email_otp(db: Session, email: str, ip_address: Optional[str] = None) -> Tuple[EmailOTP, str]:
        """
        Generates and stores an authoritative 6-digit OTP for the given email.
        Invalidates any previous active OTPs for the same email.
        """
        email_clean = email.strip().lower()
        # Supersede older active OTPs
        db.query(EmailOTP).filter(
            func.lower(EmailOTP.email) == email_clean,
            EmailOTP.is_used == False
        ).update({"is_used": True})

        code = f"{secrets.randbelow(900000) + 100000}"
        expires_at = utc_now() + timedelta(minutes=10)
        otp = EmailOTP(
            email=email_clean,
            otp_code=code,
            expires_at=expires_at,
            ip_address=ip_address,
            is_used=False,
            attempts=0
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)
        return otp, code

    @staticmethod
    def verify_email_otp(db: Session, email: str, otp_code: str) -> Tuple[bool, Optional[str]]:
        """
        Cryptographically validates an email OTP.
        Returns (success: bool, error_msg: Optional[str]).
        """
        email_clean = email.strip().lower()
        code_clean = otp_code.strip()

        # Find latest unexpired, unused OTP
        record = db.query(EmailOTP).filter(
            func.lower(EmailOTP.email) == email_clean,
            EmailOTP.is_used == False,
            EmailOTP.expires_at > utc_now()
        ).order_by(desc(EmailOTP.created_at)).first()

        if not record:
            return False, "Verification code expired or invalid. Please request a new code."

        record.attempts += 1
        if record.attempts > 3:
            record.is_used = True
            db.commit()
            return False, "Too many failed attempts. Please request a fresh code."

        if secrets.compare_digest(record.otp_code, code_clean):
            record.is_used = True
            db.commit()
            return True, None

        db.commit()
        return False, "Incorrect verification code. Please check your email and try again."

    @staticmethod
    def get_or_create_email_user(db: Session, email: str) -> User:
        """
        Finds or provisions an isolated user workspace based on verified email.
        """
        email_clean = email.strip().lower()
        user = FinancialRepository.get_user_by_email(db, email_clean)
        if user:
            user.last_login_at = utc_now()
            user.email_verified = True
            db.commit()
            db.refresh(user)
            return user

        # Provision fresh user
        prefix = email_clean.split("@")[0]
        name_parts = prefix.replace(".", " ").replace("_", " ").replace("-", " ").split()
        name = " ".join([p.capitalize() for p in name_parts]) if name_parts else "SURE SAVINGS Member"
        initials = (name_parts[0][0] + (name_parts[-1][0] if len(name_parts) > 1 else "")).upper() if name_parts else "SS"

        user = User(
            email=email_clean,
            email_verified=True,
            name=name,
            display_name=name,
            initials=initials,
            avatar_url=f"https://api.dicebear.com/7.x/initials/svg?seed={name}",
            is_demo_user=False,
            occupation="Independent Professional",
            title="SURE SAVINGS Member",
            status="active",
            last_login_at=utc_now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Initialize clean isolated workspace
        FinancialRepository.initialize_new_user_workspace(db, user.id)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_profile(db: Session, user_id: str) -> Optional[FinancialProfile]:
        return db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()

    @staticmethod
    def get_weekly_history(db: Session, user_id: str) -> List[WeeklyIncomeHistory]:
        return db.query(WeeklyIncomeHistory).filter(WeeklyIncomeHistory.user_id == user_id).all()

    @staticmethod
    def get_transactions_paginated(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        direction: Optional[str] = None
    ) -> Tuple[List[LedgerTransaction], int, int]:
        """
        Server-side paginated and filtered transactions.
        Returns: (items, total_count, total_pages)
        """
        query = db.query(LedgerTransaction).filter(LedgerTransaction.user_id == user_id)

        if category and category.lower() != "all":
            query = query.filter(func.lower(LedgerTransaction.category) == category.lower())

        if direction:
            query = query.filter(LedgerTransaction.direction == direction)

        if search:
            pattern = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(LedgerTransaction.source).like(pattern),
                    func.lower(LedgerTransaction.platform).like(pattern),
                    func.lower(LedgerTransaction.category).like(pattern)
                )
            )

        total_count = query.count()
        total_pages = max(1, math.ceil(total_count / page_size))
        offset = (page - 1) * page_size

        items = query.order_by(desc(LedgerTransaction.timestamp)).offset(offset).limit(page_size).all()
        return items, total_count, total_pages

    @staticmethod
    def get_transactions(db: Session, user_id: str) -> List[LedgerTransaction]:
        return db.query(LedgerTransaction).filter(LedgerTransaction.user_id == user_id).order_by(desc(LedgerTransaction.timestamp)).all()

    @staticmethod
    def get_transaction_summary(db: Session, user_id: str) -> Dict[str, float]:
        """Server-side aggregated inflow and outflow totals"""
        inflows = db.query(func.sum(LedgerTransaction.amount)).filter(
            LedgerTransaction.user_id == user_id,
            LedgerTransaction.direction == "credit"
        ).scalar() or 0.0

        outflows = db.query(func.sum(LedgerTransaction.amount)).filter(
            LedgerTransaction.user_id == user_id,
            LedgerTransaction.direction == "debit"
        ).scalar() or 0.0

        events = db.query(BufferLedgerEvent).filter(BufferLedgerEvent.user_id == user_id).all()
        contribs = sum(e.amount for e in events if e.action == "CONTRIBUTION")
        withdrawals = sum(e.amount for e in events if e.action == "WITHDRAWAL")

        return {
            "total_inflows": float(inflows),
            "total_outflows": float(outflows),
            "buffer_contributions": float(contribs),
            "buffer_withdrawals": float(withdrawals)
        }

    @staticmethod
    def get_obligations(db: Session, user_id: str) -> List[ScheduledObligation]:
        return db.query(ScheduledObligation).filter(ScheduledObligation.user_id == user_id).all()

    @staticmethod
    def get_buffer_events(db: Session, user_id: str) -> List[BufferLedgerEvent]:
        return db.query(BufferLedgerEvent).filter(BufferLedgerEvent.user_id == user_id).order_by(desc(BufferLedgerEvent.timestamp)).all()

    @staticmethod
    def get_active_recommendation(db: Session, user_id: str) -> Optional[Recommendation]:
        return db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.status == "PENDING"
        ).order_by(desc(Recommendation.created_at)).first()

    @staticmethod
    def get_dynamic_dashboard_state(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Authoritative single source of truth for the active user's workspace.
        Dynamically derives all metrics using FinancialEngine.recalculate_user_workspace.
        """
        from backend.financial_engine import FinancialEngine
        recalc = FinancialEngine.recalculate_user_workspace(db, user_id)
        prof = recalc["profile"]
        inc = recalc["income_analytics"]
        res = recalc["resilience"]
        risk = recalc["risk"]
        rec = recalc["recommendation"]
        cf = recalc["cash_flow"]
        readiness = recalc["readiness"]

        curr_inc = prof["current_income"]
        stab_inc = prof["stabilized_income"]
        fore_val = prof["forecast_next_week"]
        burn = prof["weekly_burn"]
        curr_buf = prof["current_buffer"]
        target_buf = prof["buffer_target"]
        floor = prof["protected_floor"]

        projected_buffer = curr_buf + rec["recommended_contribution"]
        projected_runway = round(projected_buffer / burn, 1) if burn > 0 else 0.0

        return {
            "profile": prof,
            "readiness": readiness,
            "resilience": res,
            "risk": risk,
            "weekly_variance": {
                "actual": curr_inc,
                "stabilized": stab_inc,
                "forecast": fore_val,
                "surplus": rec["surplus"],
                "variance_pct": f"{int(inc.get('recent_drift_pct', 0)):+d}%" if inc.get("recent_drift_pct") is not None else "0%"
            },
            "recommendation": {
                "title": rec.get("title", f"Save ₹{rec['recommended_contribution']:,.0f} while preserving your cash floor."),
                "recommended_amount": rec["recommended_contribution"],
                "surplus": rec["surplus"],
                "free_pocket_cash": rec["free_pocket_liquidity"],
                "protected_floor": floor,
                "confidence": rec.get("confidence", 0.94),
                "impact": f"Expands runway from {res.get('coverage_weeks', 0.0)} weeks → {projected_runway} weeks",
                "why_breakdown": rec.get("why_breakdown", {}),
                "explanation_steps": rec.get("explanation_steps", {})
            },
            "buffer": {
                "current": curr_buf,
                "target": target_buf,
                "protected_floor": floor,
                "safe_to_use": max(0.0, curr_buf - floor),
                "coverage_weeks": res.get("coverage_weeks", 0.0),
                "weekly_burn": burn,
                "buffer_state": prof["buffer_state"]
            },
            "cash_flow": cf,
            "income_analytics": inc
        }

    @staticmethod
    def commit_buffer_contribution(
        db: Session,
        user_id: str,
        amount: float = 900.0,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Atomically commits a buffer reserve allocation:
        - Idempotent: rejects duplicate keys
        - Updates buffer balance and coverage
        - Recalculates resilience and risk dynamically via FinancialEngine
        - Updates recommendation status to APPROVED
        - Records snapshot and ledger event
        """
        if idempotency_key:
            existing = db.query(BufferLedgerEvent).filter(BufferLedgerEvent.idempotency_key == idempotency_key).first()
            if existing:
                prof = FinancialRepository.get_profile(db, user_id)
                return {
                    "status": "success",
                    "idempotent": True,
                    "message": "Transaction already executed under this idempotency key.",
                    "new_buffer": prof.current_buffer,
                    "new_runway": prof.current_coverage_weeks,
                    "new_resilience": prof.resilience_score
                }

        if amount <= 0:
            prof = FinancialRepository.get_profile(db, user_id)
            return {
                "status": "success",
                "message": "Buffer is already fully funded or safe allocation is ₹0.",
                "new_buffer": prof.current_buffer,
                "new_runway": prof.current_coverage_weeks,
                "new_resilience": prof.resilience_score,
                "new_risk": prof.risk_score,
                "free_pocket_cash": prof.free_pocket_liquidity,
                "floor_intact": True
            }

        prof = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).with_for_update().first()
        if not prof:
            raise ValueError(f"User profile {user_id} not found")

        prev_buf = prof.current_buffer
        new_buf = prev_buf + amount
        prof.current_buffer = new_buf

        # Update recommendation to APPROVED
        rec = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.status == "PENDING"
        ).first()
        if rec:
            rec.status = "APPROVED"
            rec.approved_at = utc_now()

        # Record Ledger Event
        event = BufferLedgerEvent(
            user_id=user_id,
            action="CONTRIBUTION",
            amount=amount,
            previous_buffer=prev_buf,
            new_buffer=new_buf,
            runway_weeks=round(new_buf / prof.weekly_burn, 1) if prof.weekly_burn > 0 else 0.0,
            resilience_score=prof.resilience_score,
            reason_codes="SURPLUS_SAFEGUARD_APPROVED",
            idempotency_key=idempotency_key
        )
        db.add(event)

        # Add to general ledger transaction view
        tx = LedgerTransaction(
            user_id=user_id,
            date_str=utc_now().strftime("%b %d, %Y"),
            source="Buffer Reserve Allocation (Simulated)",
            platform="Smart Buffer Vault",
            category="Buffer",
            direction="credit",
            amount=amount,
            status="Simulated / Approved",
            is_essential=False
        )
        db.add(tx)
        db.commit()

        # Authoritatively recalculate workspace dynamically
        from backend.financial_engine import FinancialEngine
        recalc = FinancialEngine.recalculate_user_workspace(db, user_id)
        new_prof = recalc["profile"]

        return {
            "status": "success",
            "message": f"Successfully allocated ₹{amount:,.0f} into Smart Buffer.",
            "new_buffer": new_prof["current_buffer"],
            "new_runway": new_prof["current_coverage_weeks"],
            "new_resilience": new_prof["resilience_score"],
            "new_risk": new_prof["risk_score"],
            "free_pocket_cash": new_prof["free_pocket_liquidity"],
            "floor_intact": True
        }

    @staticmethod
    def commit_buffer_withdrawal(
        db: Session,
        user_id: str,
        amount: float = 2000.0,
        reason: str = "EMERGENCY_DRAWDOWN"
    ) -> Dict[str, Any]:
        """
        Safely executes a buffer drawdown while strictly protecting the cash floor.
        """
        prof = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).with_for_update().first()
        if not prof:
            raise ValueError(f"User profile {user_id} not found")

        prev_buf = prof.current_buffer
        safe_max = max(0.0, prev_buf - prof.protected_floor)
        approved_amount = min(amount, safe_max)

        if approved_amount <= 0:
            return {
                "status": "rejected",
                "message": f"Withdrawal rejected. Buffer is at or below protected cash floor of ₹{prof.protected_floor:,.0f}.",
                "requested_amount": amount,
                "approved_amount": 0.0,
                "current_buffer": prev_buf,
                "protected_floor": prof.protected_floor
            }

        new_buf = prev_buf - approved_amount
        prof.current_buffer = new_buf

        event = BufferLedgerEvent(
            user_id=user_id,
            action="WITHDRAWAL",
            amount=approved_amount,
            previous_buffer=prev_buf,
            new_buffer=new_buf,
            runway_weeks=round(new_buf / prof.weekly_burn, 1) if prof.weekly_burn > 0 else 0.0,
            resilience_score=prof.resilience_score,
            reason_codes=reason
        )
        db.add(event)

        tx = LedgerTransaction(
            user_id=user_id,
            date_str=utc_now().strftime("%b %d, %Y"),
            source="Buffer Vault Drawdown (Simulated)",
            platform="Smart Buffer Vault",
            category="Buffer",
            direction="debit",
            amount=approved_amount,
            status="Settled",
            is_essential=True
        )
        db.add(tx)
        db.commit()

        # Authoritatively recalculate workspace dynamically
        from backend.financial_engine import FinancialEngine
        recalc = FinancialEngine.recalculate_user_workspace(db, user_id)
        new_prof = recalc["profile"]

        return {
            "status": "success",
            "requested_amount": amount,
            "approved_amount": approved_amount,
            "is_capped": approved_amount < amount,
            "new_buffer": new_prof["current_buffer"],
            "new_runway": new_prof["current_coverage_weeks"],
            "new_resilience": new_prof["resilience_score"],
            "new_risk": new_prof["risk_score"],
            "floor_status": "SAFE • 100% INTACT"
        }

    # =====================================================================
    # Financial Setup & Digital Twin Workspace Repository Methods
    # =====================================================================

    @staticmethod
    def get_income_sources(db: Session, user_id: str) -> List[IncomeSource]:
        return db.query(IncomeSource).filter(IncomeSource.user_id == user_id, IncomeSource.is_active == True).all()

    @staticmethod
    def add_income_source(
        db: Session,
        user_id: str,
        name: str,
        typical_amount: float,
        income_type: str = "gig",
        frequency: str = "weekly",
        payout_day: str = "Wednesday",
        expected_delay_days: int = 0
    ) -> IncomeSource:
        source = IncomeSource(
            user_id=user_id,
            name=name,
            income_type=income_type,
            typical_amount=typical_amount,
            frequency=frequency,
            payout_day=payout_day,
            expected_delay_days=expected_delay_days,
            is_active=True
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def delete_income_source(db: Session, user_id: str, source_id: str) -> bool:
        source = db.query(IncomeSource).filter(IncomeSource.id == source_id, IncomeSource.user_id == user_id).first()
        if source:
            source.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def get_income_history(db: Session, user_id: str) -> List[WeeklyIncomeHistory]:
        return db.query(WeeklyIncomeHistory).filter(WeeklyIncomeHistory.user_id == user_id).all()

    @staticmethod
    def add_income_history_records(db: Session, user_id: str, records: List[Dict[str, Any]]) -> List[WeeklyIncomeHistory]:
        created = []
        for r in records:
            wh = WeeklyIncomeHistory(
                user_id=user_id,
                week=r["week"],
                income=float(r["income"]),
                source=r.get("source", "General"),
                stabilized=0.0,
                status="Recorded",
                is_current=r.get("is_current", False),
                is_forecast=False
            )
            db.add(wh)
            created.append(wh)
        db.commit()
        return created

    @staticmethod
    def get_expense_items(db: Session, user_id: str) -> List[ExpenseItem]:
        return db.query(ExpenseItem).filter(ExpenseItem.user_id == user_id, ExpenseItem.is_active == True).all()

    @staticmethod
    def add_expense_item(
        db: Session,
        user_id: str,
        description: str,
        amount: float,
        frequency: str = "monthly",
        category: str = "housing",
        is_essential: bool = True,
        due_day: int = 1,
        is_recurring: bool = True
    ) -> ExpenseItem:
        exp = ExpenseItem(
            user_id=user_id,
            description=description,
            amount=amount,
            frequency=frequency,
            category=category,
            is_essential=is_essential,
            due_day=due_day,
            is_recurring=is_recurring,
            is_active=True
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return exp

    @staticmethod
    def delete_expense_item(db: Session, user_id: str, expense_id: str) -> bool:
        exp = db.query(ExpenseItem).filter(ExpenseItem.id == expense_id, ExpenseItem.user_id == user_id).first()
        if exp:
            exp.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def get_or_create_liquidity_position(db: Session, user_id: str) -> LiquidityPosition:
        liq = db.query(LiquidityPosition).filter(LiquidityPosition.user_id == user_id).first()
        if not liq:
            liq = LiquidityPosition(
                user_id=user_id,
                checking_cash=0.0,
                savings_balance=0.0,
                physical_cash=0.0,
                total_liquid_cash=0.0,
                protected_floor=0.0,
                floor_preference="CALCULATED"
            )
            db.add(liq)
            db.commit()
            db.refresh(liq)
        return liq

    @staticmethod
    def update_liquidity_position(
        db: Session,
        user_id: str,
        checking_cash: Optional[float] = None,
        savings_balance: Optional[float] = None,
        physical_cash: Optional[float] = None,
        protected_floor: Optional[float] = None,
        floor_preference: Optional[str] = None
    ) -> LiquidityPosition:
        liq = FinancialRepository.get_or_create_liquidity_position(db, user_id)
        if checking_cash is not None:
            liq.checking_cash = checking_cash
        if savings_balance is not None:
            liq.savings_balance = savings_balance
        if physical_cash is not None:
            liq.physical_cash = physical_cash
        if protected_floor is not None:
            liq.protected_floor = protected_floor
        if floor_preference is not None:
            liq.floor_preference = floor_preference
        
        liq.total_liquid_cash = round(liq.checking_cash + liq.physical_cash + liq.savings_balance, 2)
        db.commit()
        db.refresh(liq)
        return liq

    @staticmethod
    def get_goals(db: Session, user_id: str) -> List[Goal]:
        return db.query(Goal).filter(Goal.user_id == user_id, Goal.is_active == True).all()

    @staticmethod
    def add_goal(
        db: Session,
        user_id: str,
        name: str,
        target_amount: float,
        target_date: Optional[str] = None,
        priority: str = "medium",
        goal_type: str = "EMERGENCY_RESERVE"
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=0.0,
            target_date=target_date,
            priority=priority,
            goal_type=goal_type,
            is_active=True
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(db: Session, user_id: str, goal_id: str) -> bool:
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if goal:
            goal.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def add_obligation(
        db: Session,
        user_id: str,
        description: str,
        amount: float,
        date_str: str,
        time_str: str = "09:00 AM",
        category: str = "General",
        is_essential: bool = True,
        timing_risk: bool = False
    ) -> ScheduledObligation:
        obl = ScheduledObligation(
            user_id=user_id,
            description=description,
            amount=amount,
            date_str=date_str,
            time_str=time_str,
            category=category,
            is_essential=is_essential,
            timing_risk=timing_risk,
            type="debit"
        )
        db.add(obl)
        db.commit()
        db.refresh(obl)
        return obl

    @staticmethod
    def delete_obligation(db: Session, user_id: str, obligation_id: str) -> bool:
        obl = db.query(ScheduledObligation).filter(ScheduledObligation.id == obligation_id, ScheduledObligation.user_id == user_id).first()
        if obl:
            db.delete(obl)
            db.commit()
            return True
        return False

    @staticmethod
    def apply_quick_start(
        db: Session,
        user_id: str,
        weekly_income: float,
        essential_expenses: float,
        current_cash: float,
        emergency_savings: float,
        protected_floor: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Applies Quick Start onboarding:
        Sets up primary income source, essential expenses baseline, liquidity position,
        marks setup as completed, and triggers full recalculation.
        """
        user = FinancialRepository.get_user(db, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # 1. Add / Update Primary Income Source
        existing_src = db.query(IncomeSource).filter(IncomeSource.user_id == user_id).first()
        if existing_src:
            existing_src.typical_amount = weekly_income
            existing_src.frequency = "weekly"
            existing_src.is_active = True
        else:
            src = IncomeSource(
                user_id=user_id,
                name="Primary Earnings",
                income_type=getattr(user, "income_type", "gig"),
                typical_amount=weekly_income,
                frequency="weekly",
                payout_day="Wednesday"
            )
            db.add(src)

        # 2. Add / Update Essential Expense Item
        existing_exp = db.query(ExpenseItem).filter(ExpenseItem.user_id == user_id, ExpenseItem.is_essential == True).first()
        if existing_exp:
            existing_exp.amount = essential_expenses
            existing_exp.frequency = "weekly"
            existing_exp.is_active = True
        else:
            exp = ExpenseItem(
                user_id=user_id,
                description="Essential Living Baseline",
                amount=essential_expenses,
                frequency="weekly",
                category="housing",
                is_essential=True
            )
            db.add(exp)

        # 3. Update Liquidity Position
        floor_pref = "USER_DEFINED" if protected_floor is not None else "CALCULATED"
        floor_val = protected_floor if protected_floor is not None else round((essential_expenses * 0.80) / 100.0) * 100.0
        FinancialRepository.update_liquidity_position(
            db=db,
            user_id=user_id,
            checking_cash=current_cash,
            savings_balance=emergency_savings,
            physical_cash=0.0,
            protected_floor=floor_val,
            floor_preference=floor_pref
        )

        # 4. Ensure Baseline Scheduled Obligation if none exist
        existing_obl = db.query(ScheduledObligation).filter(ScheduledObligation.user_id == user_id).first()
        if not existing_obl and essential_expenses > 0:
            obl = ScheduledObligation(
                user_id=user_id,
                date_str=(utc_now() + timedelta(days=7)).strftime("%b %d, %Y"),
                time_str="10:00 AM",
                description="Essential Living Commitment",
                category="Housing & Essentials",
                type="debit",
                amount=round(essential_expenses * 0.50, 2),
                is_essential=True,
                impact="Protected by Buffer",
                timing_risk=False,
                timing_note="Integrated into cash flow timeline"
            )
            db.add(obl)

        # 5. Ensure Emergency Buffer Goal if none exist
        existing_goal = db.query(Goal).filter(Goal.user_id == user_id).first()
        if not existing_goal:
            target_amount = max(10000.0, round(essential_expenses * 4.0, 2))
            g = Goal(
                user_id=user_id,
                name="Emergency Liquidity Buffer",
                target_amount=target_amount,
                current_amount=emergency_savings,
                target_date=(utc_now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                goal_type="BUFFER",
                priority="high",
                is_active=True
            )
            db.add(g)

        # 6. Ensure Baseline Income History if none exist
        existing_hist = db.query(WeeklyIncomeHistory).filter(WeeklyIncomeHistory.user_id == user_id).count()
        if existing_hist < 4 and weekly_income > 0:
            for idx in range(1, 9):
                mult = 1.0 + ((idx % 3) - 1) * 0.08
                wh = WeeklyIncomeHistory(
                    user_id=user_id,
                    week=f"Week {idx}",
                    income=round(weekly_income * mult, 2),
                    source="Primary Earnings",
                    stabilized=weekly_income,
                    status="Normal",
                    is_current=(idx == 8),
                    is_forecast=False
                )
                db.add(wh)

        user.setup_completed = True
        user.setup_step = 8
        db.commit()

        # Recalculate workspace authoritatively
        from backend.financial_engine import FinancialEngine
        return FinancialEngine.recalculate_user_workspace(db, user_id)

    @staticmethod
    def import_csv_transactions(db: Session, user_id: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates, deduplicates, and commits imported CSV transaction rows.
        """
        imported_count = 0
        existing_txs = db.query(LedgerTransaction).filter(LedgerTransaction.user_id == user_id).all()
        existing_keys = {
            f"{t.date_str}_{t.amount}_{t.direction}_{t.source.lower()}"
            for t in existing_txs
        }

        for r in rows:
            amt = float(r["amount"])
            direction = r.get("direction", "debit").lower().strip()
            desc = r.get("description", "Imported Transaction").strip()
            date_str = r.get("date", utc_now().strftime("%b %d, %Y")).strip()

            key = f"{date_str}_{amt}_{direction}_{desc.lower()}"
            if key in existing_keys:
                continue

            tx = LedgerTransaction(
                user_id=user_id,
                date_str=date_str,
                source=desc,
                platform=r.get("platform", "CSV Import"),
                category=r.get("category", "General"),
                direction=direction,
                amount=amt,
                status="Settled",
                is_essential=r.get("is_essential", False)
            )
            db.add(tx)
            existing_keys.add(key)
            imported_count += 1

        db.commit()

        # Recalculate workspace after import
        from backend.financial_engine import FinancialEngine
        recalc = FinancialEngine.recalculate_user_workspace(db, user_id)
        return {
            "imported_count": imported_count,
            "total_transactions": len(existing_keys),
            "recalculation": recalc
        }

    @staticmethod
    def bump_source_version(db: Session, user_id: str) -> int:
        """
        Increments the monotonic source_data_version for the user.
        Ensures derived intelligence can detect data mutations and prevent stale state.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.source_data_version = (user.source_data_version or 0) + 1
            db.commit()
            return user.source_data_version
        return 1

    @staticmethod
    def create_financial_event(
        db: Session,
        user_id: str,
        event_type: str,
        title: str,
        description: str,
        severity: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
        metrics_payload: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> FinancialEvent:
        """Records an authoritative financial event in the user's intelligence feed."""
        meta = metadata or metrics_payload or kwargs.get("payload")
        evt = FinancialEvent(
            user_id=user_id,
            event_type=event_type,
            title=title,
            description=description,
            severity=severity,
            metadata_json=json.dumps(meta) if meta else None
        )
        db.add(evt)
        db.commit()
        db.refresh(evt)
        return evt

    @staticmethod
    def get_financial_events(db: Session, user_id: str, limit: int = 50) -> List[FinancialEvent]:
        """Retrieves chronological financial events for the user."""
        return (
            db.query(FinancialEvent)
            .filter(FinancialEvent.user_id == user_id)
            .order_by(FinancialEvent.timestamp.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def reset_user(db: Session, user_id: str):
        if user_id == "usr_arjun_01":
            seed_canonical_user(db, force=True)
        else:
            # Clear user data and re-initialize clean workspace
            user = FinancialRepository.get_user(db, user_id)
            if user:
                for s in user.income_sources: db.delete(s)
                for e in user.expense_items: db.delete(e)
                for g in user.goals: db.delete(g)
                for o in user.obligations: db.delete(o)
                for t in user.transactions: db.delete(t)
                for h in user.weekly_history: db.delete(h)
                for ev in user.financial_events: db.delete(ev)
                for cal in getattr(user, "calendar_events", []): db.delete(cal)
                if user.profile: db.delete(user.profile)
                if user.liquidity_position: db.delete(user.liquidity_position)
                db.commit()
                FinancialRepository.initialize_new_user_workspace(db, user_id)
                db.commit()

    @staticmethod
    def create_calendar_event(
        db: Session,
        user_id: str,
        event_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> CalendarEvent:
        """Creates a persistent user calendar event."""
        data = dict(event_data or {})
        data.update(kwargs)
        cal = CalendarEvent(
            user_id=user_id,
            date_str=data.get("date_str") or data.get("date", datetime.now().strftime("%Y-%m-%d")),
            time_str=data.get("time_str") or data.get("time", "09:00 AM"),
            end_time_str=data.get("end_time_str") or data.get("end_time"),
            title=data.get("title", "Untitled Event"),
            description=data.get("description", ""),
            event_type=data.get("event_type") or data.get("type", "OBLIGATION"),
            direction=data.get("direction", "debit"),
            amount=float(data.get("amount", 0.0)),
            source=data.get("source", "MANUAL"),
            category=data.get("category", "General"),
            status=data.get("status", "EXPECTED"),
            is_actual=bool(data.get("is_actual", False)),
            is_expected=bool(data.get("is_expected", True)),
            is_simulation=bool(data.get("is_simulation", False)),
            is_essential=bool(data.get("is_essential", True)),
            recurrence=data.get("recurrence", "none"),
            impact=data.get("impact", "Safe"),
            risk_level=data.get("risk_level", "SAFE"),
            notes=data.get("notes")
        )
        db.add(cal)
        db.commit()
        db.refresh(cal)
        return cal

    @staticmethod
    def get_calendar_events(
        db: Session,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[CalendarEvent]:
        """Retrieves user calendar events optionally bounded by date range."""
        q = db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
        if start_date:
            q = q.filter(CalendarEvent.date_str >= start_date)
        if end_date:
            q = q.filter(CalendarEvent.date_str <= end_date)
        return q.order_by(CalendarEvent.date_str.asc(), CalendarEvent.time_str.asc()).all()

    @staticmethod
    def get_calendar_event_by_id(
        db: Session,
        event_id: Optional[str] = None,
        user_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> Optional[CalendarEvent]:
        """Retrieves a specific calendar event verifying user ownership."""
        all_ids = []
        if event_id:
            all_ids.append(event_id)
        if user_id:
            all_ids.append(user_id)
        for a in args:
            if a:
                all_ids.append(a)
        for k, v in kwargs.items():
            if k in ("event_id", "user_id", "arg1", "arg2") and v:
                all_ids.append(v)
        if len(all_ids) < 2:
            return None
        id1, id2 = all_ids[0], all_ids[1]
        return db.query(CalendarEvent).filter(
            ((CalendarEvent.id == id1) & (CalendarEvent.user_id == id2)) |
            ((CalendarEvent.id == id2) & (CalendarEvent.user_id == id1))
        ).first()

    @staticmethod
    def update_calendar_event(
        db: Session,
        event_id: Optional[str] = None,
        user_id: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> Optional[CalendarEvent]:
        """Updates a calendar event verifying ownership."""
        ev = FinancialRepository.get_calendar_event_by_id(db, event_id, user_id, *args, **kwargs)
        if not ev:
            return None
        data = dict(updates or {})
        for k, v in kwargs.items():
            if k not in ("event_id", "user_id", "arg1", "arg2"):
                data[k] = v
        for k, v in data.items():
            if hasattr(ev, k) and k not in ("id", "user_id", "created_at"):
                setattr(ev, k, v)
        ev.updated_at = utc_now()
        db.commit()
        db.refresh(ev)
        return ev

    @staticmethod
    def delete_calendar_event(
        db: Session,
        event_id: Optional[str] = None,
        user_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> bool:
        """Deletes a calendar event verifying ownership."""
        ev = FinancialRepository.get_calendar_event_by_id(db, event_id, user_id, *args, **kwargs)
        if not ev:
            return False
        db.delete(ev)
        db.commit()
        return True

