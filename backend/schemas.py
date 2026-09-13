"""
SURE SAVINGS 2.0: Pydantic v2 Request & Response Schemas
Provides strict type-safety, input validation, and clear API contracts.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class GoogleVerifyRequest(BaseModel):
    credential: str = Field(..., min_length=10, description="Google Identity Services ID Token (JWT)")

class GoogleSelectAccountRequest(BaseModel):
    email: str = Field(..., min_length=3, description="Selected Google account email")
    name: Optional[str] = Field("Google User", description="Display name for Google account")
    picture: Optional[str] = Field(None, description="Optional Google profile photo URL")

class SaveGoogleClientIdRequest(BaseModel):
    client_id: str = Field(..., min_length=10, description="Google OAuth 2.0 Web Client ID from Google Cloud Console")

class DeveloperLoginRequest(BaseModel):
    email: str = Field(..., min_length=3, description="Email address for local development sandbox")
    name: Optional[str] = Field("Sandbox User", description="Display name")
    sub: Optional[str] = Field(None, description="Optional custom Google sub identifier")

class SendOTPRequest(BaseModel):
    email: str = Field(..., min_length=5, description="Email address to receive the 6-digit OTP code")

class VerifyOTPRequest(BaseModel):
    email: str = Field(..., min_length=5, description="Email address being verified")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

class OnboardingRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, description="Full legal name of customer")
    date_of_birth: str = Field(..., min_length=4, max_length=32, description="Date of birth (YYYY-MM-DD)")
    phone_number: str = Field(..., min_length=6, max_length=32, description="Contact phone number with country code")
    country: str = Field(..., min_length=2, max_length=64, description="Country of residence")
    state: str = Field(..., min_length=2, max_length=64, description="State / Province")
    district: str = Field(..., min_length=2, max_length=64, description="District / City")
    area: str = Field(..., min_length=2, max_length=128, description="Area / Locality / Postal Code")
    occupation: Optional[str] = Field("Gig Platform Worker", description="Primary occupation or profession")

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=128, description="Full legal name of customer")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    phone_number: Optional[str] = Field(None, description="Contact phone number with country code")
    country: Optional[str] = Field(None, description="Country of residence")
    state: Optional[str] = Field(None, description="State / Province")
    district: Optional[str] = Field(None, description="District / City")
    area: Optional[str] = Field(None, description="Area / Locality / Postal Code")
    occupation: Optional[str] = Field(None, description="Primary occupation or profession")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL or path")

class ProfilePhotoUploadRequest(BaseModel):
    photo_base64: str = Field(..., description="Base64 data URL of the image (JPEG/PNG/WebP/SVG)")

class DeleteProfileRequest(BaseModel):
    confirmation: str = Field(..., description="Confirmation phrase strictly matching 'Delete profile permanently'")

class AIChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User query for the AI coach")

class SimulationRequest(BaseModel):
    amount: float = Field(..., ge=0.0, description="Amount to simulate")

class GeneralSimulationRequest(BaseModel):
    contribution_amount: float = Field(0.0, ge=0.0, description="Simulated savings contribution")
    withdrawal_amount: float = Field(0.0, ge=0.0, description="Simulated buffer withdrawal")
    shock_percentage: float = Field(0.0, ge=0.0, le=90.0, description="Simulated income drop percentage")
    scenario_type: Optional[str] = "custom"

class PublicSimulationRequest(BaseModel):
    shock_percentage: float = Field(..., ge=0.0, le=90.0, description="Simulated income shock drop percentage (0-90%)")
    contribution_amount: float = Field(0.0, ge=0.0, le=100000.0, description="Optional simulated deposit")
    withdrawal_amount: float = Field(0.0, ge=0.0, le=100000.0, description="Optional simulated withdrawal")
    scenario_preset: Optional[str] = Field("custom", description="Scenario ID (e.g. drought_20, drought_40)")

class ApproveRecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    idempotency_key: Optional[Union[str, Any]] = Field(None, description="Unique transaction idempotency key")
    amount: Optional[float] = Field(None, ge=0.0, description="Optional explicit contribution amount")

class WithdrawalRequest(BaseModel):
    user_id: Optional[str] = None
    amount: float = Field(..., gt=0.0, description="Amount to withdraw from buffer")
    reason: Optional[str] = "EMERGENCY_DRAWDOWN"

class TransactionFilterParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    category: Optional[str] = "all"
    search: Optional[str] = None
    direction: Optional[str] = None

class TransactionItem(BaseModel):
    id: str
    date: str
    description: str
    platform: str
    category: str
    type: str
    amount: str
    raw_amount: float
    status: str

class PaginatedTransactionResponse(BaseModel):
    transactions: List[TransactionItem]
    pagination: Dict[str, Any]
    summary: Dict[str, float]

class StandardResponse(BaseModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None
    meta: Optional[Dict[str, Any]] = None

# =====================================================================
# Financial Setup & Workspace Schemas (SURE SAVINGS 5.0 / 6.0)
# =====================================================================

class PersonalContextRequest(BaseModel):
    occupation: Optional[str] = Field(None, description="Primary occupation")
    income_type: Optional[str] = Field("gig", description="gig, freelance, salary, business, commission, other")
    currency: Optional[str] = Field("INR", description="Currency symbol/code")
    timezone: Optional[str] = Field("Asia/Kolkata", description="Timezone")

class QuickStartRequest(BaseModel):
    weekly_income: float = Field(..., ge=0.0, description="Average or typical weekly income")
    essential_expenses: float = Field(..., ge=0.0, description="Essential weekly expenses (rent, food, transit, EMI)")
    current_cash: float = Field(..., ge=0.0, description="Total accessible liquid cash on hand/checking")
    emergency_savings: float = Field(..., ge=0.0, description="Existing emergency savings / buffer")
    protected_floor: Optional[float] = Field(None, ge=0.0, description="Custom cash floor or None for system calculated")

class IncomeSourceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Source/Platform name (e.g. Zomato, Freelance, Salary)")
    income_type: Optional[str] = Field("gig", description="gig, freelance, salary, business, other")
    typical_amount: float = Field(..., ge=0.0, description="Typical payout amount")
    frequency: Optional[str] = Field("weekly", description="daily, weekly, biweekly, monthly, irregular")
    payout_day: Optional[str] = Field("Wednesday", description="Expected payout day or date")
    expected_delay_days: Optional[int] = Field(0, ge=0, description="Potential settlement delay in days")

class IncomeHistoryItem(BaseModel):
    week: str = Field(..., min_length=1, description="Week identifier e.g. Week 1, Sep 01 - Sep 07")
    income: float = Field(..., ge=0.0, description="Actual earned income")
    source: Optional[str] = Field("General", description="Source or platform")

class BulkIncomeHistoryRequest(BaseModel):
    records: List[IncomeHistoryItem] = Field(..., min_length=1, description="List of weekly income records")

class ExpenseItemCreateRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=128, description="Expense name e.g. Room Rent, Bike EMI, Groceries")
    amount: float = Field(..., ge=0.0, description="Expense amount")
    frequency: Optional[str] = Field("monthly", description="daily, weekly, monthly, annual, irregular")
    category: Optional[str] = Field("housing", description="housing, food, transport, utilities, communication, EMI, insurance, medical, education, subscriptions, entertainment, shopping, other")
    is_essential: Optional[bool] = Field(True, description="True for essential survival; False for discretionary")
    due_day: Optional[int] = Field(1, ge=1, le=31, description="Day of month due")
    is_recurring: Optional[bool] = Field(True, description="Recurring periodic commitment")

class LiquidityPositionRequest(BaseModel):
    checking_cash: Optional[float] = Field(0.0, ge=0.0, description="Checking / accessible digital account balance")
    savings_balance: Optional[float] = Field(0.0, ge=0.0, description="Existing savings / buffer account balance")
    physical_cash: Optional[float] = Field(0.0, ge=0.0, description="Physical cash on hand")
    protected_floor: Optional[float] = Field(None, ge=0.0, description="Protected floor balance")
    floor_preference: Optional[str] = Field("CALCULATED", description="CALCULATED or USER_DEFINED")

class BufferTargetRequest(BaseModel):
    current_emergency_savings: Optional[float] = Field(None, ge=0.0, description="Initial emergency savings")
    target_weeks: Optional[float] = Field(4.0, ge=1.0, le=52.0, description="Target coverage in weeks of essential burn")
    custom_target: Optional[float] = Field(None, ge=0.0, description="Custom monetary buffer target")

class ObligationCreateRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=128, description="Description e.g. HDFC EMI, Electricity")
    amount: float = Field(..., ge=0.0, description="Amount")
    date_str: str = Field(..., min_length=2, description="Due date (e.g. Sep 10, 2026 or 2026-09-10)")
    time_str: Optional[str] = Field("09:00 AM", description="Time of scheduled debit")
    category: Optional[str] = Field("General", description="Category")
    is_essential: Optional[bool] = Field(True, description="Whether essential")
    timing_risk: Optional[bool] = Field(False, description="Flag for potential timing risk")

class GoalCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Goal name e.g. Emergency Reserve, Rent Safety")
    target_amount: float = Field(..., gt=0.0, description="Target goal amount")
    target_date: Optional[str] = Field(None, description="Target completion date")
    priority: Optional[str] = Field("medium", description="high, medium, low")
    goal_type: Optional[str] = Field("EMERGENCY_RESERVE", description="EMERGENCY_RESERVE, RENT_PROTECTION, INCOME_GAP, VEHICLE_REPAIR, MEDICAL_RESERVE, DEBT_CUSHION, CUSTOM")

class CSVTransactionImportRow(BaseModel):
    date: str
    description: str
    amount: float
    direction: str # credit or debit
    category: Optional[str] = "General"
    platform: Optional[str] = "CSV Import"
    is_essential: Optional[bool] = False

class CSVTransactionImportRequest(BaseModel):
    transactions: List[CSVTransactionImportRow] = Field(..., min_length=1, description="Parsed CSV transaction rows")

class WhatIfSimulationRequest(BaseModel):
    scenario_name: Optional[str] = Field("Parametric Simulation", description="Human-readable scenario name")
    income_change_pct: Optional[float] = Field(0.0, description="Percentage change in income (-90 to +200%)")
    income_delta_pct: Optional[float] = Field(None, description="Alias for income_change_pct")
    expense_change_pct: Optional[float] = Field(0.0, description="Percentage change in expenses (-50 to +200%)")
    expense_delta_pct: Optional[float] = Field(None, description="Alias for expense_change_pct")
    income_delay_days: Optional[int] = Field(0, ge=0, description="Delay in days for incoming payouts")
    delayed_payout_days: Optional[int] = Field(None, description="Alias for income_delay_days")
    new_obligation_amount: Optional[float] = Field(0.0, ge=0.0, description="One-time unplanned outflow amount")
    one_off_shock: Optional[float] = Field(None, description="Alias for new_obligation_amount")
    additional_saving_weekly: Optional[float] = Field(0.0, ge=0.0, description="Additional weekly saving allocated")
    buffer_withdrawal_amount: Optional[float] = Field(0.0, ge=0.0, description="One-time withdrawal from buffer")
    duration_weeks: Optional[int] = Field(4, ge=1, le=52, description="Duration of stress simulation in weeks")
    simulation_weeks: Optional[int] = Field(None, description="Alias for duration_weeks")

class CalendarEventCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of calendar event")
    date_str: str = Field(..., description="Date in YYYY-MM-DD format e.g. 2026-09-15")
    time_str: Optional[str] = Field("09:00 AM", max_length=30, description="Time e.g. 09:00 AM")
    end_time_str: Optional[str] = Field(None, max_length=30, description="Optional end time")
    event_type: Optional[str] = Field("commitment", description="commitment, payout, sweep, buffer_release, simulation, baseline")
    direction: Optional[str] = Field("outflow", description="inflow or outflow")
    amount: float = Field(..., gt=0.0, description="Transaction amount in INR")
    category: Optional[str] = Field("General", max_length=100, description="Category e.g. Housing, Loan, Mobility, Inflow")
    description: Optional[str] = Field("", max_length=500, description="Detailed description")
    is_essential: Optional[bool] = Field(True, description="Whether essential")
    is_simulation: Optional[bool] = Field(False, description="Whether event is what-if simulation")
    recurrence: Optional[str] = Field("none", description="none, daily, weekly, biweekly, monthly, quarterly")
    status: Optional[str] = Field("EXPECTED", description="EXPECTED, ACTUAL, MISSED, DELAYED, CANCELLED")
    notes: Optional[str] = Field(None, max_length=500, description="User or system notes")

class CalendarEventUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    date_str: Optional[str] = None
    time_str: Optional[str] = None
    end_time_str: Optional[str] = None
    event_type: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0.0)
    category: Optional[str] = None
    description: Optional[str] = None
    is_essential: Optional[bool] = None
    is_simulation: Optional[bool] = None
    recurrence: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class IncomeProviderConnectRequest(BaseModel):
    provider_id: str = Field(..., min_length=1, description="Provider ID e.g. zomato, blinkit, uber, swiggy, freelance")
    typical_amount: float = Field(..., gt=0.0, description="Typical payout amount in INR")
    frequency: Optional[str] = Field("weekly", description="weekly, biweekly, monthly")
    payout_day: Optional[str] = Field("Wednesday", description="Day of week or date")
    notes: Optional[str] = Field(None, description="Optional notes")


