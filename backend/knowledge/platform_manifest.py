"""
SURE SAVINGS: Comprehensive Platform Knowledge Manifest (backend/knowledge/platform_manifest.py)
Curated, user-facing product registry describing how all 15 pages and features of SURE SAVINGS work.

Security Invariants:
- Contains ONLY user-facing functional explanations.
- Never contains internal code, secrets, database schemas, or infrastructure configuration.
- Provides authoritative route allowlists, button purposes, and metric definitions for SURE AI.
"""

from typing import Dict, Any, List, Optional

# Re-export sub-registries
from backend.knowledge.attribution_registry import ATTRIBUTION_STATEMENT, is_attribution_query, get_attribution_response
from backend.knowledge.refusal_registry import REFUSAL_POLICIES, check_refusal, build_refusal_response
from backend.knowledge.button_registry import BUTTON_REGISTRY, get_button_info, list_buttons_for_page
from backend.knowledge.metric_registry import METRIC_REGISTRY, get_metric_info
from backend.knowledge.onboarding_registry import ONBOARDING_STEPS, COMPREHENSIVE_TOUR, get_onboarding_guide_text, get_full_tour_text
from backend.knowledge.intent_taxonomy import IntentClassifier

# Legacy alias for backward compatibility
ONBOARDING_GUIDE = ONBOARDING_STEPS

# ── Safe Navigation Route Allowlist (All 15 Platform Pages) ──
ALLOWED_ROUTES: Dict[str, str] = {
    "index.html": "Command Center",
    "income-intelligence.html": "Income Intelligence",
    "calendar.html": "Income Calendar",
    "planner.html": "Cash Flow Planner",
    "pipeline.html": "Decision Pipeline",
    "decision-pipeline.html": "Decision Pipeline",
    "goals.html": "Goals & Buffer Plan",
    "risk.html": "Risk & Early Warning",
    "health.html": "Financial Health",
    "activity.html": "Transactions & Activity",
    "bank-accounts.html": "Bank Accounts",
    "coach.html": "SURE AI Guide",
    "resilience-plan.html": "Resilience Plan",
    "simulator.html": "Shock Simulator",
    "landing.html": "Public Explorer",
    "login.html": "Sign In"
}

# ── Comprehensive Platform Features (15 Pages + Setup) ──
PLATFORM_FEATURES: Dict[str, Dict[str, Any]] = {
    "command_center": {
        "name": "Command Center",
        "route": "index.html",
        "purpose": "Central financial cockpit displaying real-time liquidity, Safe-to-Save recommendations, emergency buffer status, and quick calibration actions.",
        "audience": "All users managing their day-to-day cash flow and emergency buffer.",
        "when_to_use": "Daily or weekly to check your cash position and approve surplus savings sweeps.",
        "how_to_open": "Click 'Command Center' on the sidebar or open index.html.",
        "key_metrics": ["Safe-to-Save", "Protected Cash Floor", "Smart Buffer", "Resilience Score", "Weekly Burn"],
        "available_actions": [
            "Review Safe-to-Save recommendation",
            "Approve buffer capitalization ('Approve Savings')",
            "Emergency buffer withdrawal ('Withdraw from Buffer')",
            "Launch Financial Setup Wizard or Quick Start"
        ],
        "prerequisites": "Complete Financial Setup or Quick Start to view calibrated recommendations.",
        "next_recommended_step": "If Safe-to-Save shows a positive surplus, approve the recommendation to reinforce your emergency buffer."
    },
    "income_intelligence": {
        "name": "Income Intelligence",
        "route": "income-intelligence.html",
        "purpose": "Analyzes gig earnings volatility, income source diversification, and establishes your 60/40 stabilized income baseline.",
        "audience": "Gig workers and freelancers with variable earnings across multiple platforms.",
        "when_to_use": "After completing work cycles or payouts from Zomato, Swiggy, Blinkit, or client invoices.",
        "how_to_open": "Click 'Income Intelligence' on the sidebar.",
        "key_metrics": ["Current Cycle Inflow", "Stabilized Baseline", "Volatility Coefficient", "Active Sources"],
        "available_actions": [
            "Inspect weekly earnings trends",
            "Filter income sources by platform",
            "Recalculate stabilized baseline"
        ],
        "prerequisites": "At least one income entry recorded or bank account synchronized.",
        "next_recommended_step": "Check your volatility coefficient; if above 40%, the engine automatically expands your buffer target."
    },
    "income_calendar": {
        "name": "Income Calendar",
        "route": "calendar.html",
        "purpose": "Displays expected and observed cash-flow events, upcoming bill commitments (rent, vehicle EMI, utilities), and platform payouts on a daily timeline.",
        "audience": "Users tracking cash-flow timing to prevent bills from bouncing.",
        "when_to_use": "Weekly to inspect upcoming bill clusters and align with expected payout days.",
        "how_to_open": "Click 'Income Calendar' on the sidebar.",
        "key_metrics": ["Upcoming Commitments", "Expected Inflow Days", "Cash Gap Alerts"],
        "available_actions": [
            "View daily timeline of cash obligations",
            "Filter by Inflows vs Outflows",
            "Add custom scheduled cash-flow events"
        ],
        "prerequisites": "None. Populates automatically from setup and connected bank accounts.",
        "next_recommended_step": "Look for upcoming red clusters indicating cash-outflow pressure days."
    },
    "cash_flow_planner": {
        "name": "Cash Flow Planner",
        "route": "planner.html",
        "purpose": "Multi-week predictive cash-flow forecasting modeling upcoming income cycles against non-discretionary survival burn.",
        "audience": "Users planning expenses over the next 4 to 8 weeks.",
        "when_to_use": "Before making major financial commitments or during low-earning seasons.",
        "how_to_open": "Click 'Cash Flow Planner' on the sidebar.",
        "key_metrics": ["4-Week Projected Deficit/Surplus", "Runway Depletion Timeline", "Liquidity Margin"],
        "available_actions": [
            "Run 4-week forecast simulation",
            "Adjust expense stress levels",
            "Inspect predicted floor breach dates"
        ],
        "prerequisites": "Configured weekly income and burn rate.",
        "next_recommended_step": "If the forecast shows an upcoming deficit, reduce non-essential expenses or plan extra gig shifts."
    },
    "decision_pipeline": {
        "name": "Decision Pipeline",
        "route": "decision-pipeline.html",
        "purpose": "Mathematical explainability engine providing cryptographic audit traces for every recommendation and calculation.",
        "audience": "Users seeking complete transparency into how their numbers are derived.",
        "when_to_use": "When you want to understand exactly why Safe-to-Save recommended a specific amount.",
        "how_to_open": "Click 'Decision Pipeline' on the sidebar or open decision-pipeline.html.",
        "key_metrics": ["Audit Trace ID", "Floor Invariant Status", "Surplus Dampening Ratio"],
        "available_actions": [
            "Inspect mathematical calculation breakdown",
            "Verify cryptographic hash trace",
            "Review reason codes for clamped recommendations"
        ],
        "prerequisites": "Completed setup or active recommendations.",
        "next_recommended_step": "Review the reason codes to see which safety constraints are currently active."
    },
    "goals_buffer": {
        "name": "Goals & Buffer Plan",
        "route": "goals.html",
        "purpose": "Configure target savings goals (Emergency Runway, Vehicle Downpayment, Festive Buffer) and allocate protected reserves.",
        "audience": "Users building long-term financial security and milestone savings.",
        "when_to_use": "When setting up new savings targets or checking progress toward your 4-week buffer goal.",
        "how_to_open": "Click 'Goals & Buffer Plan' on the sidebar.",
        "key_metrics": ["Buffer Target", "Current Funded Weeks", "Goal Completion %"],
        "available_actions": [
            "Create new financial goal",
            "Set target amount and target date",
            "Adjust target buffer weeks (default: 4 weeks of burn)"
        ],
        "prerequisites": "Setup completed with weekly burn rate defined.",
        "next_recommended_step": "Maintain at least 4 weeks of essential expenses in your emergency buffer before funding long-term goals."
    },
    "risk_early_warning": {
        "name": "Risk & Early Warning",
        "route": "risk.html",
        "purpose": "Early warning telemetry detecting impending cash gaps, consecutive down-week trends, and buffer depletion risks.",
        "audience": "Users wanting advance notice of financial vulnerability.",
        "when_to_use": "Weekly to check if any risk telemetry flags are triggered.",
        "how_to_open": "Click 'Risk & Early Warning' on the sidebar.",
        "key_metrics": ["Risk Level (Low/Moderate/High)", "Runway Days", "Down-Week Sensitivity"],
        "available_actions": [
            "Review active telemetry flags",
            "Simulate severe earnings drop",
            "Inspect timing gap risk triggers"
        ],
        "prerequisites": "Financial Setup completed.",
        "next_recommended_step": "If risk level is elevated, the engine automatically clamps Safe-to-Save to zero to protect checking liquidity."
    },
    "financial_health": {
        "name": "Financial Health",
        "route": "health.html",
        "purpose": "Multi-pillar diagnostic assessment measuring liquidity margin, debt-to-income ratio, volatility dampening, and savings adherence.",
        "audience": "Users conducting an overall financial checkup.",
        "when_to_use": "Monthly or after significant changes in income or debt.",
        "how_to_open": "Click 'Financial Health' on the sidebar.",
        "key_metrics": ["Health Diagnostic Rating", "Debt Service Ratio", "Savings Consistency Score"],
        "available_actions": [
            "Run full financial diagnostic check",
            "Review pillar-by-pillar ratings",
            "Export financial health report"
        ],
        "prerequisites": "Active financial profile with expense records.",
        "next_recommended_step": "Focus on improving the lowest-scoring health pillar."
    },
    "transactions_activity": {
        "name": "Transactions & Activity Ledger",
        "route": "activity.html",
        "purpose": "Normalized, deduplicated ledger of all bank transactions, manual adjustments, and buffer sweeps with search and CSV export.",
        "audience": "Users reviewing their financial transactions and audit history.",
        "when_to_use": "To verify imported bank data or export records for tax and accounting purposes.",
        "how_to_open": "Click 'Transactions & Activity' on the sidebar.",
        "key_metrics": ["Total Transactions Count", "Deduplicated Records", "Net Monthly Cash Flow"],
        "available_actions": [
            "Filter transactions by category or date",
            "Search transaction descriptions",
            "Export activity ledger to CSV"
        ],
        "prerequisites": "At least one synchronized bank account or imported CSV statement.",
        "next_recommended_step": "Verify categorized transactions to ensure income and expenses are correctly identified."
    },
    "bank_accounts": {
        "name": "Bank Accounts",
        "route": "bank-accounts.html",
        "purpose": "Connect and manage bank accounts securely via RBI-licensed Account Aggregator (Setu AA) for read-only balance and transaction synchronization.",
        "audience": "Users wanting automated, live bank data without manual entry.",
        "when_to_use": "When initially linking your bank account or manually triggering a data refresh.",
        "how_to_open": "Click 'Bank Accounts' on the sidebar or navigate to bank-accounts.html.",
        "key_metrics": ["Total Connected Balance", "Linked Accounts Count", "Last Synced At", "Freshness Status"],
        "available_actions": [
            "Connect bank account via Account Aggregator ('Connect Bank Account')",
            "Sync latest transactions and balances ('Sync Now')",
            "Inspect deduplicated ledger records",
            "Manage or revoke consent ('Revoke Consent')",
            "Disconnect bank connection ('Disconnect Bank')",
            "Upload offline bank statement ('Import Bank CSV')"
        ],
        "prerequisites": "Mobile number registered with your bank.",
        "next_recommended_step": "After connecting, click 'Sync Now' to pull recent transaction history into your intelligence ledger."
    },
    "sure_ai_coach": {
        "name": "SURE AI Guide",
        "route": "coach.html",
        "purpose": "Conversational product guidance, navigation assistant, and financial explanation companion.",
        "audience": "All users seeking guidance, explanation of numbers, button walkthroughs, or next steps.",
        "when_to_use": "Whenever you have questions about how SURE SAVINGS works or why a metric has a certain value.",
        "how_to_open": "Click 'SURE AI' on the sidebar or open coach.html.",
        "key_metrics": ["Resilience Score", "Verified Telemetry Status", "Active Page Context"],
        "available_actions": [
            "Ask questions about any page, button, or metric",
            "Request step-by-step onboarding walkthrough",
            "Learn how to connect bank accounts",
            "Click prompt chips for quick explanations"
        ],
        "prerequisites": "None. Accessible to all users in both demo and private workspaces.",
        "next_recommended_step": "Ask 'How does SURE SAVINGS work?' or 'What should I do next?'"
    },
    "shock_simulator": {
        "name": "Shock Simulator",
        "route": "simulator.html",
        "purpose": "Stress-test your financial resilience against simulated real-world shocks (e.g. 40% income collapse, medical emergency, fuel surge).",
        "audience": "Users testing whether their emergency buffer is strong enough to survive severe emergencies.",
        "when_to_use": "When setting buffer targets or evaluating financial safety margins.",
        "how_to_open": "Click 'Shock Simulator' on the sidebar.",
        "key_metrics": ["Survival Weeks Under Shock", "Buffer Drawdown Rate", "Floor Breach Risk"],
        "available_actions": [
            "Adjust shock percentage slider (10% to 75%)",
            "Toggle medical emergency expense shock",
            "Inspect buffer depletion curve"
        ],
        "prerequisites": "Setup completed.",
        "next_recommended_step": "Test whether your current buffer survives at least 4 weeks of a 50% income drop."
    },
    "resilience_plan": {
        "name": "Resilience Plan",
        "route": "resilience-plan.html",
        "purpose": "Holistic financial recovery and preparedness roadmap detailing step-by-step pathways to achieve a 100/100 resilience rating.",
        "audience": "Users seeking structured guidance to systematically strengthen their finances.",
        "when_to_use": "When reviewing weekly progress and identifying the highest-impact action.",
        "how_to_open": "Click 'Resilience Plan' on the sidebar.",
        "key_metrics": ["Readiness Level", "Active Resilience Actions", "Recovery Pathways"],
        "available_actions": [
            "Review dynamic step-by-step checklist",
            "Simulate recovery outcomes",
            "Track resilience milestones"
        ],
        "prerequisites": "Setup completed.",
        "next_recommended_step": "Follow the highlighted highest-impact action in your resilience pathway."
    },
    "public_explorer": {
        "name": "Public Explorer",
        "route": "landing.html",
        "purpose": "Public landing page explaining SURE SAVINGS features, philosophy, and interactive public shock simulation.",
        "audience": "Prospective users exploring SURE SAVINGS before signing up.",
        "when_to_use": "First landing on the website.",
        "how_to_open": "Navigate to landing.html.",
        "key_metrics": ["Public Simulation Presets", "Platform Resilience Architecture"],
        "available_actions": [
            "Test public stress simulator",
            "Explore platform features and philosophy",
            "Click 'Sign In' or 'Get Started' to create an account"
        ],
        "prerequisites": "None; public access.",
        "next_recommended_step": "Click 'Get Started' to create your account and unlock personalized intelligence."
    },
    "authentication": {
        "name": "Sign In & Registration",
        "route": "login.html",
        "purpose": "Secure authentication portal for logging into existing workspaces or registering a new account.",
        "audience": "Users entering their personal workspace or demo account.",
        "when_to_use": "When starting a session or switching accounts.",
        "how_to_open": "Navigate to login.html.",
        "key_metrics": ["Session Security Status"],
        "available_actions": [
            "Sign in with email and password",
            "Register a new account",
            "Enter instant Demo Mode"
        ],
        "prerequisites": "None.",
        "next_recommended_step": "Sign in to access your private financial workspace."
    },
    "financial_setup": {
        "name": "Financial Setup Wizard",
        "route": "index.html#setup",
        "purpose": "Initial calibration wizard to capture your weekly earnings baseline, essential burn rate, existing savings, and checking account floor.",
        "audience": "New users or users updating their foundational numbers.",
        "when_to_use": "First step after creating an account or when income/expenses shift.",
        "how_to_open": "Click 'Complete Setup' or 'Financial Setup Wizard' on Command Center.",
        "key_metrics": ["Profile Completion %", "Calibrated Floor", "Calibrated Burn"],
        "available_actions": [
            "Enter weekly income estimate",
            "Record essential expenses (rent, groceries, transit, EMIs)",
            "Set protected cash floor",
            "Enter starting emergency buffer"
        ],
        "prerequisites": "None. This is the very first step for every new user.",
        "next_recommended_step": "Complete the 4 wizard steps, then connect your bank account for automated updates."
    }
}

def get_page_info(page_name: str) -> Optional[Dict[str, Any]]:
    """Lookup platform knowledge by page name or route."""
    clean = page_name.lower().replace("/", "").replace(".html", "")
    for key, feat in PLATFORM_FEATURES.items():
        if key in clean or clean in feat["route"].lower():
            return feat
    return None
