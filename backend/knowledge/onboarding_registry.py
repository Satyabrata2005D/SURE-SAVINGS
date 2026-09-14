"""
SURE SAVINGS: Onboarding & Comprehensive Tour Registry (backend/knowledge/onboarding_registry.py)
Authoritative roadmap for new users and complete multi-section platform tour.

Security Invariants:
- Explains only user-facing functionality and safe workflows.
- Never discloses source code, system configurations, or developer internals.
"""

from typing import Dict, Any, List

# ── Structured 9-Step First-Time User Roadmap ──
ONBOARDING_STEPS: List[Dict[str, Any]] = [
    {
        "step": 1,
        "title": "Complete Financial Setup",
        "route": "index.html",
        "action": "Open Financial Setup Wizard on Command Center to calibrate your weekly earnings, essential burn, and cash floor.",
        "why": "The deterministic engine requires baseline numbers to derive your Safe-to-Save recommendations and Resilience Score."
    },
    {
        "step": 2,
        "title": "Connect Your Bank Account",
        "route": "bank-accounts.html",
        "action": "Open Bank Accounts and click 'Connect Bank Account' to link your bank securely via RBI Account Aggregator (Setu AA).",
        "why": "Enables automated transaction importing, verified income tracking, and real-time multi-bank balance aggregation."
    },
    {
        "step": 3,
        "title": "Explore Command Center",
        "route": "index.html",
        "action": "Review your central financial overview, monitor your Protected Floor, and inspect Safe-to-Save recommendations.",
        "why": "Command Center is your daily operating cockpit for managing cash reserves and liquidity."
    },
    {
        "step": 4,
        "title": "Inspect Income Intelligence",
        "route": "income-intelligence.html",
        "action": "Review your 60/40 Stabilized Income Baseline and earnings volatility across gig platforms.",
        "why": "Prevents spending spikes on temporary good weeks by anchoring recommendations to your dependable earning baseline."
    },
    {
        "step": 5,
        "title": "Review Cash Flow Planner",
        "route": "planner.html",
        "action": "Forecast upcoming cash inflows and essential commitments over the next 4 to 8 weeks.",
        "why": "Identifies impending cash deficits in advance so you can adjust spending before bills come due."
    },
    {
        "step": 6,
        "title": "Check Income Calendar",
        "route": "calendar.html",
        "action": "View scheduled platform payouts, rent dates, vehicle EMIs, and utility due dates on a daily timeline.",
        "why": "Ensures no bill or loan payment catches you off-guard."
    },
    {
        "step": 7,
        "title": "Set Goals & Buffer Targets",
        "route": "goals.html",
        "action": "Create dedicated reserve goals (e.g. 4-Week Emergency Buffer, Vehicle Maintenance, Festive Fund).",
        "why": "Provides structured milestones to track your progress toward complete financial freedom."
    },
    {
        "step": 8,
        "title": "Monitor Risk & Financial Health",
        "route": "risk.html",
        "action": "Inspect early warning telemetry and multi-factor diagnostic health checks.",
        "why": "Alerts you to consecutive down-weeks, runway depletion, or bill pressure before distress occurs."
    },
    {
        "step": 9,
        "title": "Use SURE AI",
        "route": "coach.html",
        "action": "Ask SURE AI about any page, button, metric, bank connection step, or recommended next action.",
        "why": "Provides 24/7 intelligent guidance tailored to your verified financial telemetry."
    }
]

# ── 20-Section Comprehensive Website Tour ──
COMPREHENSIVE_TOUR: Dict[str, Any] = {
    "title": "Complete Tour of SURE SAVINGS",
    "sections": [
        {
            "section": 1,
            "title": "What SURE SAVINGS Is",
            "content": (
                "SURE SAVINGS is an intelligent financial resilience platform designed specifically for gig workers, "
                "freelancers, and variable-income earners. Unlike traditional banking apps that assume a fixed monthly salary, "
                "SURE SAVINGS smooths unpredictable cash flows, ring-fences a protected checking cash floor, and dynamically "
                "calculates Safe-to-Save recommendations so you never overdraft or fall short on rent."
            )
        },
        {
            "section": 2,
            "title": "How a New User Starts",
            "content": (
                "Start by clicking 'Financial Setup Wizard' on Command Center (or 'Quick Start Calibration' for instant defaults). "
                "Enter your estimated weekly income, essential survival expenses (rent, food, fuel, EMIs), and cash floor. "
                "This unlocks your personalized Resilience Score and activates the recommendation engine."
            )
        },
        {
            "section": 3,
            "title": "Authentication & Privacy",
            "content": (
                "SURE SAVINGS uses secure session tokens and password hashing. Each user's financial workspace is strictly "
                "isolated in the database. No user can view another user's financial information, and credentials are never disclosed."
            )
        },
        {
            "section": 4,
            "title": "Financial Setup Wizard",
            "content": (
                "Found on index.html, this 4-step wizard calibrates your income baseline, weekly burn rate, protected floor, "
                "and starting emergency buffer. You can re-open it at any time to update your baseline as your work evolves."
            )
        },
        {
            "section": 5,
            "title": "Bank Connection & RBI Account Aggregator",
            "content": (
                "Found on bank-accounts.html, this page lets you link bank accounts via Setu AA (licensed by the RBI). "
                "It is strictly read-only: it imports transactions and balances with your consent, but NEVER asks for passwords, "
                "PINs, or UPI credentials, and CANNOT move money."
            )
        },
        {
            "section": 6,
            "title": "Command Center (index.html)",
            "content": (
                "Your central financial dashboard. Displays your real-time Safe-to-Save recommendation, Protected Floor, "
                "Smart Buffer balance, and Resilience Score. Key buttons include 'Approve Recommendation' (sweeps surplus into buffer) "
                "and 'Withdraw from Buffer' (emergency liquidity drawdown)."
            )
        },
        {
            "section": 7,
            "title": "Income Intelligence (income-intelligence.html)",
            "content": (
                "Analyzes your earnings volatility across platforms (Zomato, Swiggy, Blinkit, freelance, etc.). "
                "Calculates a 60/40 Stabilized Income Baseline to prevent lucky one-week spikes from distorting your savings targets."
            )
        },
        {
            "section": 8,
            "title": "Cash Flow Planner (planner.html)",
            "content": (
                "Projects cash inflows and essential burn over upcoming weeks. Highlights liquidity pressure periods in advance "
                "so you know when to curtail discretionary spending."
            )
        },
        {
            "section": 9,
            "title": "Income Calendar (calendar.html)",
            "content": (
                "A visual calendar showing daily cash-flow timing: upcoming rent, vehicle EMIs, utility bills, and expected gig payout "
                "dates. Click 'Add Cash-Flow Event' to record custom obligations."
            )
        },
        {
            "section": 10,
            "title": "Decision Pipeline (decision-pipeline.html)",
            "content": (
                "Provides mathematical explainability and cryptographic audit logs for every recommendation. Shows exactly how "
                "surplus, floor protection, and burn rate produced the recommended Safe-to-Save amount."
            )
        },
        {
            "section": 11,
            "title": "Goals & Buffer Plan (goals.html)",
            "content": (
                "Configure savings milestones such as Emergency Runway, Vehicle Maintenance, or Festival Reserves. Tracks target amounts, "
                "target dates, and current funded weeks."
            )
        },
        {
            "section": 12,
            "title": "Risk & Early Warning (risk.html)",
            "content": (
                "Early warning radar that detects consecutive down-weeks, runway depletion, and upcoming bill pressure. "
                "If risk rises to High, Safe-to-Save is automatically clamped to ₹0 to preserve checking liquidity."
            )
        },
        {
            "section": 13,
            "title": "Financial Health (health.html)",
            "content": (
                "Comprehensive health check across liquidity, debt obligations, income volatility, and savings rate. "
                "Gives actionable diagnostic ratings (Optimal, Stable, Caution, Urgent Action)."
            )
        },
        {
            "section": 14,
            "title": "Transactions & Activity Ledger (activity.html)",
            "content": (
                "Searchable, filterable audit ledger of all bank-imported transactions, manual adjustments, and buffer sweeps. "
                "Supports CSV export for your personal accounting."
            )
        },
        {
            "section": 15,
            "title": "Shock Simulator (simulator.html)",
            "content": (
                "Interactive stress-testing workbench. Simulate severe income drops (10% to 75%) or medical emergencies to see "
                "how many weeks your Smart Buffer survives before breaching your cash floor."
            )
        },
        {
            "section": 16,
            "title": "Resilience Plan (resilience-plan.html)",
            "content": (
                "Dynamic recovery roadmap outlining step-by-step milestones to raise your resilience score from your current level "
                "to a fortress 100/100 score."
            )
        },
        {
            "section": 17,
            "title": "SURE AI (coach.html)",
            "content": (
                "Your 24/7 intelligent product guide. Answers questions about how any page or button works, explains financial metrics "
                "using your verified telemetry, and guides you on what to do next."
            )
        },
        {
            "section": 18,
            "title": "Data Readiness & States",
            "content": (
                "If you have not entered financial data, metrics display 'Setup Required' or 'INSUFFICIENT_DATA' rather than fake zeros. "
                "Completing Financial Setup or Quick Start immediately unlocks full calculations."
            )
        },
        {
            "section": 19,
            "title": "What to Do When Data Is Insufficient",
            "content": (
                "Click 'Financial Setup Wizard' on Command Center, enter your weekly income and expenses, and click Save. "
                "Alternatively, connect your bank account on bank-accounts.html and click 'Sync Now'."
            )
        },
        {
            "section": 20,
            "title": "Safe User Workflow & Core Invariants",
            "content": (
                "Key Rules to remember:\n"
                "1. Bank Balance ≠ Safe-to-Save (obligations and cash floor are always protected first).\n"
                "2. Protected Cash Floor is untouchable.\n"
                "3. SURE AI is strictly read-only and will never transfer money or alter accounts.\n"
                "4. All bank integrations use read-only RBI Account Aggregator consent."
            )
        }
    ]
}

def get_onboarding_guide_text() -> str:
    """Format the 9-step onboarding guide as readable markdown."""
    lines = ["### Welcome to SURE SAVINGS: Quick Start Guide\n"]
    for item in ONBOARDING_STEPS:
        lines.append(f"**Step {item['step']}: {item['title']}** ({item['route']})")
        lines.append(f"• Action: {item['action']}")
        lines.append(f"• Why: {item['why']}\n")
    return "\n".join(lines)

def get_full_tour_text() -> str:
    """Format the full 20-section platform tour as comprehensive markdown."""
    lines = [f"## {COMPREHENSIVE_TOUR['title']}\n"]
    for sec in COMPREHENSIVE_TOUR["sections"]:
        lines.append(f"### Section {sec['section']} — {sec['title']}")
        lines.append(f"{sec['content']}\n")
    return "\n".join(lines)
