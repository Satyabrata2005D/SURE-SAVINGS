"""
SURE SAVINGS 7.0: SQLAlchemy Domain Models & Persistent Schema
Optimized schema with source versioning, behavior profiles, financial events, and audit trails.
"""
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import uuid

from backend.database import Base

def generate_uuid(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def get_utc_now():
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("usr"))
    google_subject_id = Column(String(128), unique=True, index=True, nullable=True)
    email = Column(String(256), unique=True, index=True, nullable=True)
    email_verified = Column(Boolean, default=False)
    name = Column(String(128), nullable=False)
    display_name = Column(String(128), nullable=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    initials = Column(String(8), default="AK")
    occupation = Column(String(128), default="Gig Platform Worker")
    title = Column(String(128), default="Delivery & Freelance Lead")
    currency = Column(String(8), default="INR")
    timezone = Column(String(64), default="Asia/Kolkata")
    locale = Column(String(16), default="en-IN")
    preferred_locale = Column(String(16), default="en-IN")
    status = Column(String(32), default="ACTIVE")
    is_demo_user = Column(Boolean, default=False)
    phone_number = Column(String(32), nullable=True)
    date_of_birth = Column(String(32), nullable=True)
    country = Column(String(64), default="India")
    state = Column(String(64), nullable=True)
    district = Column(String(64), nullable=True)
    area = Column(String(128), nullable=True)
    is_onboarded = Column(Boolean, default=False)
    income_type = Column(String(64), default="gig")
    setup_step = Column(Integer, default=0)
    setup_completed = Column(Boolean, default=False)
    data_maturity_level = Column(Integer, default=0) # 0 to 5
    readiness_percentage = Column(Integer, default=0) # 0 to 100%

    # 7.0 Digital Twin & Intelligence Extensions
    source_data_version = Column(Integer, default=1)
    behavior_profile = Column(String(32), default="STABLE") # STABLE, GROWING, VOLATILE, BUFFER_BUILDING, etc.
    data_quality_score = Column(Float, default=0.0) # 0 to 100%
    data_quality_status = Column(String(32), default="INCOMPLETE") # EXCELLENT, GOOD, FAIR, INCOMPLETE

    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    last_login_at = Column(DateTime, default=get_utc_now)

    profile = relationship("FinancialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    income_sources = relationship("IncomeSource", back_populates="user", cascade="all, delete-orphan")
    expense_items = relationship("ExpenseItem", back_populates="user", cascade="all, delete-orphan")
    liquidity_position = relationship("LiquidityPosition", back_populates="user", uselist=False, cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("LedgerTransaction", back_populates="user", cascade="all, delete-orphan")
    weekly_history = relationship("WeeklyIncomeHistory", back_populates="user", cascade="all, delete-orphan")
    obligations = relationship("ScheduledObligation", back_populates="user", cascade="all, delete-orphan")
    buffer_events = relationship("BufferLedgerEvent", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    snapshots = relationship("FinancialSnapshot", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_traces = relationship("AuditTrace", back_populates="user", cascade="all, delete-orphan")
    financial_events = relationship("FinancialEvent", back_populates="user", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")
    bank_connections = relationship("BankConnection", back_populates="user", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("sess"))
    session_token = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(String(64), ForeignKey("users.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
    expires_at = Column(DateTime, index=True, nullable=False)
    last_accessed_at = Column(DateTime, default=get_utc_now)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")

class EmailOTP(Base):
    __tablename__ = "email_otps"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("otp"))
    email = Column(String(128), index=True, nullable=False)
    otp_code = Column(String(16), nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
    expires_at = Column(DateTime, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    ip_address = Column(String(64), nullable=True)

class IncomeSource(Base):
    __tablename__ = "income_sources"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("inc"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False) # e.g. Zomato, Blinkit, Freelance, Salary
    income_type = Column(String(64), default="gig") # gig, freelance, salary, business, commission, other
    typical_amount = Column(Float, nullable=False, default=0.0)
    frequency = Column(String(32), default="weekly") # daily, weekly, biweekly, monthly, irregular
    payout_day = Column(String(32), default="Wednesday")
    expected_delay_days = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="income_sources")

class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("exp"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    description = Column(String(128), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    frequency = Column(String(32), default="monthly") # daily, weekly, monthly, annual, irregular
    category = Column(String(64), default="housing") # housing, food, transport, utilities, communication, EMI, insurance, medical, education, subscriptions, entertainment, shopping, other
    is_essential = Column(Boolean, default=True)
    due_day = Column(Integer, default=1)
    is_recurring = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="expense_items")

class LiquidityPosition(Base):
    __tablename__ = "liquidity_positions"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("liq"))
    user_id = Column(String(64), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    checking_cash = Column(Float, default=0.0)
    savings_balance = Column(Float, default=0.0)
    physical_cash = Column(Float, default=0.0)
    total_liquid_cash = Column(Float, default=0.0)
    protected_floor = Column(Float, default=0.0)
    floor_preference = Column(String(32), default="CALCULATED") # CALCULATED or USER_DEFINED
    floor_reason = Column(String(256), nullable=True)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="liquidity_position")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("goal"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    target_amount = Column(Float, nullable=False, default=0.0)
    current_amount = Column(Float, default=0.0)
    target_date = Column(String(32), nullable=True)
    priority = Column(String(16), default="medium") # high, medium, low
    goal_type = Column(String(64), default="EMERGENCY_RESERVE")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="goals")

class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("prof"))
    user_id = Column(String(64), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    current_week = Column(String(32), default="Week 1")

    # Authoritative monetary balances (Default 0.0 for clean private workspace)
    current_income = Column(Float, default=0.0)
    stabilized_income = Column(Float, default=0.0)
    forecast_next_week = Column(Float, default=0.0)
    forecast_confidence = Column(Float, default=0.0)
    income_volatility = Column(Float, default=0.0)

    # Buffer mechanics & lifecycle state
    current_buffer = Column(Float, default=0.0)
    buffer_target = Column(Float, default=0.0)
    buffer_target_weeks = Column(Float, default=4.0)
    protected_floor = Column(Float, default=0.0)
    weekly_burn = Column(Float, default=0.0)
    weekly_discretionary_burn = Column(Float, default=0.0)
    current_coverage_weeks = Column(Float, default=0.0)
    safe_to_use_above_floor = Column(Float, default=0.0)
    buffer_state = Column(String(32), default="BUILDING")

    # Surplus & recommendation
    surplus = Column(Float, default=0.0)
    recommended_contribution = Column(Float, default=0.0)
    free_pocket_liquidity = Column(Float, default=0.0)

    # Analytical scores & status indicators
    resilience_score = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    forecast_status = Column(String(32), default="NOT_AVAILABLE") # NOT_AVAILABLE, BASIC, CONFIDENT
    volatility_status = Column(String(32), default="NOT_AVAILABLE") # NOT_AVAILABLE, AVAILABLE
    resilience_status = Column(String(32), default="INSUFFICIENT_DATA") # INSUFFICIENT_DATA, ACTIVE
    risk_status = Column(String(32), default="DATA_INCOMPLETE") # DATA_INCOMPLETE, ACTIVE
    cash_flow_status = Column(String(32), default="AWAITING_OBLIGATIONS") # AWAITING_OBLIGATIONS, ACTIVE

    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="profile")

class WeeklyIncomeHistory(Base):
    __tablename__ = "weekly_income_history"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("wh"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    week = Column(String(32), nullable=False)
    income = Column(Float, nullable=False, default=0.0)
    source = Column(String(128), default="General")
    stabilized = Column(Float, default=0.0)
    status = Column(String(64), default="Normal")
    is_current = Column(Boolean, default=False)
    is_forecast = Column(Boolean, default=False)

    user = relationship("User", back_populates="weekly_history")

class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("tx"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    date_str = Column(String(32), nullable=False)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    source = Column(String(128), nullable=False)
    platform = Column(String(64), default="Platform")
    category = Column(String(64), default="General", index=True)
    direction = Column(String(16), default="credit", index=True) # credit or debit
    amount = Column(Float, nullable=False)
    status = Column(String(64), default="Settled")
    is_essential = Column(Boolean, default=False)
    raw_payload = Column(Text, nullable=True)

    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("idx_tx_user_date", "user_id", "timestamp"),
        Index("idx_tx_user_category", "user_id", "category"),
        Index("idx_tx_user_dir", "user_id", "direction"),
    )

class ScheduledObligation(Base):
    __tablename__ = "scheduled_obligations"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("obl"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    date_str = Column(String(32), nullable=False)
    time_str = Column(String(32), default="09:00 AM")
    description = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    type = Column(String(16), default="debit")
    amount = Column(Float, nullable=False)
    is_essential = Column(Boolean, default=True)
    impact = Column(String(128), default="Safe")
    timing_risk = Column(Boolean, default=False)
    timing_note = Column(String(256), nullable=True)

    user = relationship("User", back_populates="obligations")

class BufferLedgerEvent(Base):
    __tablename__ = "buffer_ledger_events"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("ble"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    action = Column(String(32), nullable=False) # CONTRIBUTION, WITHDRAWAL, SIMULATION
    amount = Column(Float, nullable=False)
    previous_buffer = Column(Float, nullable=False)
    new_buffer = Column(Float, nullable=False)
    runway_weeks = Column(Float, nullable=False)
    resilience_score = Column(Integer, nullable=False)
    reason_codes = Column(String(256), default="SURPLUS_SAFEGUARD")
    idempotency_key = Column(String(128), nullable=True, index=True)

    user = relationship("User", back_populates="buffer_events")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("rec"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=get_utc_now)
    title = Column(String(256), nullable=False)
    recommended_amount = Column(Float, nullable=False)
    surplus = Column(Float, nullable=False)
    free_pocket_cash = Column(Float, nullable=False)
    protected_floor = Column(Float, default=3500.0)
    status = Column(String(32), default="PENDING") # PENDING, APPROVED, DISMISSED
    approved_at = Column(DateTime, nullable=True)
    idempotency_key = Column(String(128), nullable=True, index=True)

    user = relationship("User", back_populates="recommendations")

class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("snp"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    current_buffer = Column(Float, nullable=False)
    resilience_score = Column(Integer, nullable=False)
    risk_score = Column(Integer, nullable=False)
    coverage_weeks = Column(Float, nullable=False)
    actual_income = Column(Float, nullable=False)
    stabilized_income = Column(Float, nullable=False)

    user = relationship("User", back_populates="snapshots")

class AuditTrace(Base):
    __tablename__ = "audit_traces"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("aud"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    engine_version = Column(String(32), default="v7.0")
    verification_status = Column(String(32), default="PASS")
    inputs_json = Column(Text, nullable=False)
    calculation_json = Column(Text, nullable=False)
    recommendation_json = Column(Text, nullable=False)

    user = relationship("User", back_populates="audit_traces")

class FinancialEvent(Base):
    """
    Financial event stream recording authoritative telemetry triggers
    (e.g., INCOME_SPIKE, BUFFER_DEPLETION, LIQUIDITY_GAP, RISK_ESCALATION).
    """
    __tablename__ = "financial_events"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("evt"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    event_type = Column(String(64), nullable=False, index=True) # INCOME_SPIKE, INCOME_DROP, BUFFER_DEPLETION, etc.
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(32), default="INFO") # INFO, WARNING, CRITICAL, POSITIVE
    source = Column(String(64), default="FINANCIAL_ENGINE")
    before_state = Column(String(64), nullable=True)
    after_state = Column(String(64), nullable=True)
    metadata_json = Column(Text, nullable=True) # JSON payload with context and metrics
    is_read = Column(Boolean, default=False)

    user = relationship("User", back_populates="financial_events")

    __table_args__ = (
        Index("idx_evt_user_time", "user_id", "timestamp"),
    )

class CalendarEvent(Base):
    """
    Dedicated user calendar event entity for bills, EMIs, custom payouts, goals, and obligations.
    """
    __tablename__ = "calendar_events"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("cal"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    date_str = Column(String(32), nullable=False, index=True) # YYYY-MM-DD
    time_str = Column(String(32), default="09:00 AM")
    end_time_str = Column(String(32), nullable=True)
    title = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    event_type = Column(String(32), default="OBLIGATION", index=True) # INCOME, EXPENSE, OBLIGATION, BUFFER, GOAL, FORECAST, LIQUIDITY_GAP, RISK, RESILIENCE, SIMULATION, SYSTEM
    direction = Column(String(16), default="debit", index=True) # credit, debit, neutral
    amount = Column(Float, nullable=False, default=0.0)
    source = Column(String(64), default="MANUAL")
    category = Column(String(64), default="General")
    status = Column(String(32), default="EXPECTED") # EXPECTED, ACTUAL, MISSED, DELAYED, CANCELLED, SETTLED
    is_actual = Column(Boolean, default=False)
    is_expected = Column(Boolean, default=True)
    is_simulation = Column(Boolean, default=False)
    is_essential = Column(Boolean, default=True)
    recurrence = Column(String(32), default="none") # none, daily, weekly, biweekly, monthly, quarterly
    impact = Column(String(128), default="Safe")
    risk_level = Column(String(32), default="SAFE") # SAFE, ATTENTION, HIGH_RISK
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="calendar_events")

    __table_args__ = (
        Index("idx_cal_user_date", "user_id", "date_str"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date_str,
            "date_str": self.date_str,
            "time": self.time_str or "09:00 AM",
            "time_str": self.time_str or "09:00 AM",
            "end_time": self.end_time_str,
            "end_time_str": self.end_time_str,
            "title": self.title,
            "description": self.description or "",
            "type": self.event_type,
            "event_type": self.event_type,
            "direction": self.direction,
            "amount": float(self.amount),
            "source": self.source or "MANUAL",
            "category": self.category or "General",
            "status": self.status,
            "is_actual": self.is_actual,
            "is_expected": self.is_expected,
            "is_simulation": self.is_simulation,
            "is_essential": self.is_essential,
            "recurrence": self.recurrence or "none",
            "impact": self.impact or "Safe",
            "risk_level": self.risk_level or "SAFE",
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# =====================================================================
# BANK DATA INTEGRATION SUBSYSTEM (SETU ACCOUNT AGGREGATOR)
# =====================================================================

class BankConnection(Base):
    """
    Represents an Account Aggregator connection established by an authenticated user.
    Maintains status lifecycle: CONNECTING, AWAITING_CONSENT, CONSENT_ACTIVE,
    SYNCING, CONNECTED, PARTIALLY_AVAILABLE, NEEDS_ATTENTION, CONSENT_EXPIRED,
    CONSENT_REVOKED, DISCONNECTED, ERROR.
    """
    __tablename__ = "bank_connections"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("bconn"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(32), default="SETU")  # SETU, MOCK_SETU
    status = Column(String(32), default="CONNECTING")
    customer_reference = Column(String(128), nullable=True)
    phone_or_vua = Column(String(64), nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message_safe = Column(String(512), nullable=True)
    metadata_safe = Column(Text, nullable=True)  # Safe JSON string (no secrets)
    last_sync_at = Column(DateTime, nullable=True)
    last_successful_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="bank_connections")
    accounts = relationship("BankAccount", back_populates="connection", cascade="all, delete-orphan")
    consents = relationship("BankConsent", back_populates="connection", cascade="all, delete-orphan")
    sessions = relationship("BankDataSession", back_populates="connection", cascade="all, delete-orphan")
    sync_runs = relationship("BankSyncRun", back_populates="connection", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider,
            "status": self.status,
            "customer_reference": self.customer_reference,
            "phone_or_vua": self.phone_or_vua,
            "error_code": self.error_code,
            "error_message_safe": self.error_message_safe,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "last_successful_sync_at": self.last_successful_sync_at.isoformat() if self.last_successful_sync_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accounts_count": len(self.accounts) if self.accounts else 0
        }


class BankAccount(Base):
    """
    Represents an individual bank account linked via Account Aggregator.
    Stores latest reported balance, balance timestamp, and account metadata.
    """
    __tablename__ = "bank_accounts"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("bacc"))
    bank_connection_id = Column(String(64), ForeignKey("bank_connections.id"), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    fip_id = Column(String(64), default="SETU_FIP")
    institution_name = Column(String(128), default="Bank")
    masked_account_number = Column(String(32), nullable=False)
    account_type = Column(String(32), default="SAVINGS")  # SAVINGS, CURRENT
    currency = Column(String(8), default="INR")
    current_reported_balance = Column(Float, default=0.0)
    available_reported_balance_if_supported = Column(Float, nullable=True)
    balance_as_of = Column(DateTime, nullable=True)
    status = Column(String(32), default="ACTIVE")  # ACTIVE, INACTIVE, UNLINKED
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    connection = relationship("BankConnection", back_populates="accounts")
    user = relationship("User", back_populates="bank_accounts")
    transactions = relationship("BankTransaction", back_populates="bank_account", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bank_connection_id": self.bank_connection_id,
            "user_id": self.user_id,
            "fip_id": self.fip_id,
            "institution_name": self.institution_name,
            "masked_account_number": self.masked_account_number,
            "account_type": self.account_type,
            "currency": self.currency,
            "current_reported_balance": float(self.current_reported_balance or 0.0),
            "available_reported_balance": float(self.available_reported_balance_if_supported) if self.available_reported_balance_if_supported is not None else None,
            "balance_as_of": self.balance_as_of.isoformat() if self.balance_as_of else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class BankConsent(Base):
    """
    Tracks Setu consent artefacts with validity ranges, status lifecycle,
    and revocation state.
    """
    __tablename__ = "bank_consents"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("bcon"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    bank_connection_id = Column(String(64), ForeignKey("bank_connections.id"), nullable=False, index=True)
    provider = Column(String(32), default="SETU")
    consent_id = Column(String(128), unique=True, index=True, nullable=False)
    status = Column(String(32), default="PENDING")  # PENDING, ACTIVE, REJECTED, REVOKED, PAUSED, EXPIRED
    purpose_code = Column(String(32), default="101")
    purpose_text = Column(String(256), default="Wealth management and cash flow resilience planning")
    data_range_from = Column(String(32), nullable=True)
    data_range_to = Column(String(32), nullable=True)
    consent_url = Column(String(512), nullable=True)
    consent_created_at = Column(DateTime, default=get_utc_now)
    consent_updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    last_fetch_at = Column(DateTime, nullable=True)

    connection = relationship("BankConnection", back_populates="consents")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bank_connection_id": self.bank_connection_id,
            "consent_id": self.consent_id,
            "status": self.status,
            "purpose_code": self.purpose_code,
            "purpose_text": self.purpose_text,
            "data_range_from": self.data_range_from,
            "data_range_to": self.data_range_to,
            "consent_url": self.consent_url,
            "consent_created_at": self.consent_created_at.isoformat() if self.consent_created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "last_fetch_at": self.last_fetch_at.isoformat() if self.last_fetch_at else None
        }


class BankDataSession(Base):
    """
    Tracks Setu data-fetch sessions created against active consents.
    """
    __tablename__ = "bank_data_sessions"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("bds"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    bank_connection_id = Column(String(64), ForeignKey("bank_connections.id"), nullable=False, index=True)
    consent_id = Column(String(128), nullable=False, index=True)
    data_session_id = Column(String(128), unique=True, index=True, nullable=False)
    status = Column(String(32), default="PENDING")  # PENDING, PARTIAL, COMPLETED, EXPIRED, FAILED
    requested_from = Column(String(32), nullable=True)
    requested_to = Column(String(32), nullable=True)
    format = Column(String(16), default="json")
    ready_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failure_code = Column(String(64), nullable=True)
    failure_message_safe = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    connection = relationship("BankConnection", back_populates="sessions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bank_connection_id": self.bank_connection_id,
            "consent_id": self.consent_id,
            "data_session_id": self.data_session_id,
            "status": self.status,
            "requested_from": self.requested_from,
            "requested_to": self.requested_to,
            "ready_at": self.ready_at.isoformat() if self.ready_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failure_code": self.failure_code,
            "failure_message_safe": self.failure_message_safe,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class BankTransaction(Base):
    """
    Stores imported bank transactions with idempotency hashing,
    confidence classification, candidate tagging, and self-transfer detection.
    """
    __tablename__ = "bank_transactions"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("btx"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    bank_account_id = Column(String(64), ForeignKey("bank_accounts.id"), nullable=False, index=True)
    external_transaction_id_or_stable_hash = Column(String(128), nullable=False, index=True)
    transaction_date = Column(String(32), nullable=False, index=True)  # YYYY-MM-DD
    transaction_timestamp = Column(DateTime, nullable=True)
    value_date_if_available = Column(String(32), nullable=True)
    amount = Column(Float, nullable=False)
    direction = Column(String(16), nullable=False)  # credit, debit
    description = Column(Text, nullable=True)
    merchant = Column(String(128), nullable=True)
    category = Column(String(64), default="General")
    subcategory = Column(String(64), nullable=True)
    currency = Column(String(8), default="INR")
    reference = Column(String(128), nullable=True)
    balance_after_if_available = Column(Float, nullable=True)
    source = Column(String(64), default="BANK_SETU")
    raw_record_hash = Column(String(128), nullable=True)
    imported_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    classification_status = Column(String(32), default="UNCLASSIFIED")  # CONFIRMED, LIKELY, UNCERTAIN, UNCLASSIFIED, SELF_TRANSFER
    is_income_candidate = Column(Boolean, default=False)
    is_expense_candidate = Column(Boolean, default=False)
    is_recurring_candidate = Column(Boolean, default=False)
    is_self_transfer = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.5)

    bank_account = relationship("BankAccount", back_populates="transactions")

    __table_args__ = (
        Index("idx_btx_user_account", "user_id", "bank_account_id"),
        Index("idx_btx_hash_account", "bank_account_id", "external_transaction_id_or_stable_hash", unique=True),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bank_account_id": self.bank_account_id,
            "external_transaction_id_or_stable_hash": self.external_transaction_id_or_stable_hash,
            "transaction_date": self.transaction_date,
            "transaction_timestamp": self.transaction_timestamp.isoformat() if self.transaction_timestamp else None,
            "amount": float(self.amount),
            "direction": self.direction,
            "description": self.description or "",
            "merchant": self.merchant,
            "category": self.category or "General",
            "subcategory": self.subcategory,
            "currency": self.currency,
            "reference": self.reference,
            "balance_after": float(self.balance_after_if_available) if self.balance_after_if_available is not None else None,
            "source": self.source,
            "classification_status": self.classification_status,
            "is_income_candidate": self.is_income_candidate,
            "is_expense_candidate": self.is_expense_candidate,
            "is_recurring_candidate": self.is_recurring_candidate,
            "is_self_transfer": self.is_self_transfer,
            "confidence_score": float(self.confidence_score or 0.5),
            "imported_at": self.imported_at.isoformat() if self.imported_at else None
        }


class BankSyncRun(Base):
    """
    Maintains full audit trails for bank sync operations including
    counts, timestamps, and safe error diagnostics.
    """
    __tablename__ = "bank_sync_runs"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("bsync"))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    connection_id = Column(String(64), ForeignKey("bank_connections.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(32), default="RUNNING")  # RUNNING, SUCCESS, PARTIAL, FAILED
    records_received = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped_duplicate = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_code = Column(String(64), nullable=True)
    safe_error_message = Column(String(512), nullable=True)

    connection = relationship("BankConnection", back_populates="sync_runs")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "connection_id": self.connection_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "records_received": self.records_received,
            "records_imported": self.records_imported,
            "records_updated": self.records_updated,
            "records_skipped_duplicate": self.records_skipped_duplicate,
            "records_failed": self.records_failed,
            "error_code": self.error_code,
            "safe_error_message": self.safe_error_message
        }
