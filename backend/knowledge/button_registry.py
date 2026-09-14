"""
SURE SAVINGS: Button Action Registry (backend/knowledge/button_registry.py)
Curated catalog of every major user-facing button and control across all pages.

Security Invariants:
- All buttons are described strictly from the user's perspective.
- Documents preconditions, what happens after click, confirmation requirements, and navigation targets.
- Clarifies what buttons do NOT do (e.g., Sync Now does not transfer money; Connect Bank does not ask for netbanking password).
"""

from typing import Dict, Any, Optional, List

BUTTON_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ── Bank Accounts (bank-accounts.html) ──
    "CONNECT_BANK": {
        "button_id": "CONNECT_BANK",
        "label": "Connect Bank Account",
        "page": "bank-accounts.html",
        "purpose": "Initiates secure bank linking via RBI Account Aggregator (Setu AA).",
        "meaning": "Allows SURE SAVINGS to receive read-only transaction history and balances from your bank with your explicit consent.",
        "when_to_use": "When you want automated income verification, balance updates, and transaction categorization.",
        "preconditions": "You must have an active mobile number registered with your bank.",
        "what_happens_after_click": "Opens the Account Aggregator authorization modal. You select your bank, receive an OTP on your bank-registered mobile, and approve consent.",
        "what_it_does_not_do": "It NEVER asks for debit card PINs, UPI PINs, or netbanking passwords, and it CANNOT initiate debits or withdrawals.",
        "expected_result": "Upon authorization, your bank account displays in the connected list with an 'Active' status and current balance.",
        "possible_errors": "OTP timeout, unsupported bank, or expired consent session.",
        "confirmation_required": True,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "bank-accounts.html",
        "success_message": "Bank account connected successfully.",
        "help_text": "Connect Bank Account securely links your bank via RBI Account Aggregator. It is read-only and never accesses your password or PIN."
    },
    "SYNC_NOW": {
        "button_id": "SYNC_NOW",
        "label": "Sync Now",
        "page": "bank-accounts.html",
        "purpose": "Requests the latest available bank data through the connected bank-data provider.",
        "meaning": "Pulls recent transactions and fresh account balances since the last synchronization.",
        "when_to_use": "When you have completed gig shifts, received payouts, or want to refresh your liquidity status.",
        "preconditions": "At least one active connected bank account.",
        "what_happens_after_click": "SURE SAVINGS requests updated records from the Account Aggregator, deduplicates transactions via SHA-256 hashes, filters self-transfers, and updates your intelligence ledger.",
        "what_it_does_not_do": "It does not move funds, deposit money, or alter your bank account. It is strictly read-only synchronization.",
        "expected_result": "The 'Last Synced' timestamp updates to 'Just now', and new transactions appear in the ledger.",
        "possible_errors": "Bank server rate limit, temporary network failure, or stale consent.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "bank-accounts.html",
        "success_message": "Synchronization completed. Latest transactions imported.",
        "help_text": "Sync Now fetches the latest transactions and balance from your bank, deduplicates them, and updates your financial state."
    },
    "DISCONNECT_BANK": {
        "button_id": "DISCONNECT_BANK",
        "label": "Disconnect Bank",
        "page": "bank-accounts.html",
        "purpose": "Severs the live connection between SURE SAVINGS and your bank account.",
        "meaning": "Stops all future automated synchronization and notifies the provider to cancel active data sessions.",
        "when_to_use": "If you switch banks, close an account, or no longer wish to share data.",
        "preconditions": "An active linked bank account.",
        "what_happens_after_click": "Prompts for confirmation, then marks the connection as inactive. Past imported transactions remain in your personal ledger for record-keeping unless you delete your profile.",
        "what_it_does_not_do": "It does not close your actual bank account or affect your bank balance.",
        "expected_result": "The account is removed from the active bank list and automated sync stops.",
        "possible_errors": "Session timeout.",
        "confirmation_required": True,
        "financial_mutation": False,
        "danger_level": "low",
        "navigation_target": "bank-accounts.html",
        "success_message": "Bank disconnected successfully.",
        "help_text": "Disconnect Bank disconnects the bank feed. Historical ledger data remains available for your review."
    },
    "REVOKE_CONSENT": {
        "button_id": "REVOKE_CONSENT",
        "label": "Revoke Consent",
        "page": "bank-accounts.html",
        "purpose": "Exercises your RBI regulatory right to immediately revoke data sharing consent.",
        "meaning": "Informs the Account Aggregator network that consent is withdrawn.",
        "when_to_use": "When you want to permanently cancel data-sharing authorization.",
        "preconditions": "An active consent agreement.",
        "what_happens_after_click": "Sends a revocation command to Setu AA. Future data requests will be rejected.",
        "what_it_does_not_do": "It does not modify bank accounts or delete existing local ledger history.",
        "expected_result": "Consent status changes to 'REVOKED'.",
        "possible_errors": "Gateway communication failure.",
        "confirmation_required": True,
        "financial_mutation": False,
        "danger_level": "low",
        "navigation_target": "bank-accounts.html",
        "success_message": "Data sharing consent revoked.",
        "help_text": "Revoke Consent withdraws your data-sharing permission through the RBI Account Aggregator system."
    },
    "IMPORT_CSV": {
        "button_id": "IMPORT_CSV",
        "label": "Import Bank CSV",
        "page": "bank-accounts.html",
        "purpose": "Upload an offline bank statement in CSV format.",
        "meaning": "Allows offline ledger ingestion without an active Account Aggregator connection.",
        "when_to_use": "If your bank is not yet live on Account Aggregator or you have downloaded historical statements.",
        "preconditions": "A standard bank statement CSV file.",
        "what_happens_after_click": "Parses date, description, and debit/credit columns, normalizes categories, and deduplicates against existing records.",
        "what_it_does_not_do": "Does not alter online bank accounts.",
        "expected_result": "Imported transactions populate into your activity ledger.",
        "possible_errors": "Unsupported CSV formatting or missing headers.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "activity.html",
        "success_message": "CSV statement imported successfully.",
        "help_text": "Import Bank CSV allows you to upload offline transaction statements to update your financial intelligence."
    },

    # ── Command Center (index.html) ──
    "APPROVE_RECOMMENDATION": {
        "button_id": "APPROVE_RECOMMENDATION",
        "label": "Approve Savings / Capitalize Buffer",
        "page": "index.html",
        "purpose": "Confirms the recommended Safe-to-Save surplus deposit into your Smart Buffer vault.",
        "meaning": "Authorizes the recorded transfer of surplus earnings into protected emergency reserves.",
        "when_to_use": "When your weekly income produces a positive Safe-to-Save recommendation (e.g. ₹900).",
        "preconditions": "Safe-to-Save recommendation must be greater than ₹0.",
        "what_happens_after_click": "Generates a cryptographically signed authorization event, records the sweep in your audit trail, increases your Smart Buffer total, and recalibrates your resilience runway.",
        "what_it_does_not_do": "It does NOT initiate an automated debit from your real-world bank; you manually transfer the funds to your reserve account or envelope.",
        "expected_result": "Smart Buffer balance increases, coverage weeks expand, and recommendation resets.",
        "possible_errors": "Idempotency key collision or invalid user profile.",
        "confirmation_required": True,
        "financial_mutation": True,
        "danger_level": "safe",
        "navigation_target": "index.html",
        "success_message": "Buffer capitalization approved and recorded.",
        "help_text": "Approve Recommendation records your surplus sweep into your Smart Buffer, expanding your resilience runway."
    },
    "WITHDRAW_BUFFER": {
        "button_id": "WITHDRAW_BUFFER",
        "label": "Withdraw from Buffer",
        "page": "index.html",
        "purpose": "Allows drawing down saved emergency buffer funds back into checking liquidity.",
        "meaning": "Uses emergency reserves to cover cash deficits or bill payment pressures.",
        "when_to_use": "When checking liquidity is low, income is delayed, or an unexpected essential expense occurs.",
        "preconditions": "Smart Buffer balance must be greater than ₹0.",
        "what_happens_after_click": "Opens a drawdown modal. You enter the amount and reason. The engine validates that the drawdown preserves buffer invariants and records the event.",
        "what_it_does_not_do": "It does not move funds directly into external bank accounts; it manages your internal ledger reserves.",
        "expected_result": "Smart Buffer decreases by the specified amount and checking operational liquidity is restored.",
        "possible_errors": "Requested amount exceeds available buffer.",
        "confirmation_required": True,
        "financial_mutation": True,
        "danger_level": "medium",
        "navigation_target": "index.html",
        "success_message": "Emergency drawdown recorded.",
        "help_text": "Withdraw from Buffer unlocks emergency savings when you experience an income gap or urgent expense."
    },
    "QUICK_START": {
        "button_id": "QUICK_START",
        "label": "Quick Start Calibration",
        "page": "index.html",
        "purpose": "Instantly calibrates standard gig-worker financial baselines with a single click.",
        "meaning": "Applies sensible defaults (₹8,400 income, ₹4,400 burn, ₹3,500 floor, ₹6,800 buffer) so new users can explore full intelligence immediately.",
        "when_to_use": "When you are a new user exploring the platform before entering your exact bank numbers.",
        "preconditions": "Zero or uncalibrated financial profile.",
        "what_happens_after_click": "Populates baseline figures into your database profile and refreshes all dashboard gauges.",
        "what_it_does_not_do": "Does not connect external accounts.",
        "expected_result": "Command Center illuminates with live resilience scores, runway calculations, and Safe-to-Save recommendations.",
        "possible_errors": "None.",
        "confirmation_required": False,
        "financial_mutation": True,
        "danger_level": "safe",
        "navigation_target": "index.html",
        "success_message": "Quick Start profile calibrated.",
        "help_text": "Quick Start Calibration sets up realistic baseline figures so you can preview all features immediately."
    },
    "LAUNCH_SETUP": {
        "button_id": "LAUNCH_SETUP",
        "label": "Financial Setup Wizard",
        "page": "index.html",
        "purpose": "Opens the step-by-step financial calibration modal.",
        "meaning": "Captures your weekly earnings, essential burn rate, cash floor, and emergency reserves.",
        "when_to_use": "First-time onboarding or when your income/burn fundamentals change.",
        "preconditions": "None.",
        "what_happens_after_click": "Opens the 4-step wizard: Income -> Expenses -> Liquidity -> Buffer.",
        "what_it_does_not_do": "Does not require bank login.",
        "expected_result": "Saves your custom profile and unlocks full mathematical resilience scoring.",
        "possible_errors": "Negative expense numbers or zero income.",
        "confirmation_required": False,
        "financial_mutation": True,
        "danger_level": "safe",
        "navigation_target": "index.html",
        "success_message": "Profile updated successfully.",
        "help_text": "Financial Setup Wizard guides you through configuring your income, expenses, and safety buffer."
    },

    # ── Income Intelligence (income-intelligence.html) ──
    "RECALCULATE_BASELINE": {
        "button_id": "RECALCULATE_BASELINE",
        "label": "Recalculate Baseline",
        "page": "income-intelligence.html",
        "purpose": "Re-derives your 60/40 stabilized income baseline using the latest verified inflows.",
        "meaning": "Filters erratic gig peaks and troughs to determine your predictable weekly earning power.",
        "when_to_use": "After synchronizing new bank statements or when platform payouts change.",
        "preconditions": "At least one income entry recorded.",
        "what_happens_after_click": "Applies the 60% historical average + 40% recent cycle smoothing algorithm.",
        "what_it_does_not_do": "Does not alter raw transaction amounts.",
        "expected_result": "Updated stabilized baseline number and revised volatility coefficient.",
        "possible_errors": "Insufficient income history.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "income-intelligence.html",
        "success_message": "Stabilized income baseline recalculated.",
        "help_text": "Recalculate Baseline updates your smoothed earnings baseline by weighing past and recent income cycles."
    },

    # ── Income Calendar (calendar.html) ──
    "ADD_CASHFLOW_EVENT": {
        "button_id": "ADD_CASHFLOW_EVENT",
        "label": "Add Cash-Flow Event",
        "page": "calendar.html",
        "purpose": "Schedule an expected payout or upcoming bill commitment.",
        "meaning": "Places a calendar obligation to prevent unexpected cash crunches.",
        "when_to_use": "When you have a scheduled rent, vehicle EMI, or expected platform payout date.",
        "preconditions": "Event date, amount, and category.",
        "what_happens_after_click": "Stores the scheduled event and overlays it on your cash-flow calendar.",
        "what_it_does_not_do": "Does not initiate automatic bill payments.",
        "expected_result": "The event appears on the calendar grid with an inflow (green) or outflow (red) indicator.",
        "possible_errors": "Past dates or negative amounts.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "calendar.html",
        "success_message": "Event added to calendar.",
        "help_text": "Add Cash-Flow Event lets you track upcoming bill due dates and expected platform payouts on your calendar."
    },

    # ── Goals & Buffer Plan (goals.html) ──
    "ADD_GOAL": {
        "button_id": "ADD_GOAL",
        "label": "Create Financial Goal",
        "page": "goals.html",
        "purpose": "Define a targeted savings milestone (e.g. Emergency Runway, Bike Downpayment, Festival Buffer).",
        "meaning": "Sets a dedicated financial target with required funding amounts and target dates.",
        "when_to_use": "When you want to build structured resilience for specific life milestones.",
        "preconditions": "Goal title and target amount.",
        "what_happens_after_click": "Creates a ring-fenced goal card and computes required weekly contributions.",
        "what_it_does_not_do": "Does not lock external funds in bank accounts.",
        "expected_result": "Goal appears on your goals dashboard with progress tracking.",
        "possible_errors": "Invalid target amount.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "goals.html",
        "success_message": "Goal created.",
        "help_text": "Create Financial Goal tracks your progress toward specific emergency reserves or milestone targets."
    },

    # ── Shock Simulator (simulator.html) ──
    "SIMULATE_SHOCK": {
        "button_id": "SIMULATE_SHOCK",
        "label": "Simulate Income Shock",
        "page": "simulator.html",
        "purpose": "Stress-test your finances against sudden income drops or unexpected emergency expenses.",
        "meaning": "Calculates exactly how many weeks your Smart Buffer and cash floor survive under severe pressure.",
        "when_to_use": "To understand your financial resilience and prepare for platform slumps or medical emergencies.",
        "preconditions": "Configured weekly burn and buffer.",
        "what_happens_after_click": "Projects week-by-week cash drawdown curves across 10% to 75% income shocks.",
        "what_it_does_not_do": "Does not modify your real financial profile or account balances.",
        "expected_result": "Interactive stress graph shows buffer depletion horizon and breach warnings.",
        "possible_errors": "None; read-only simulation.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "simulator.html",
        "success_message": "Stress test simulation generated.",
        "help_text": "Simulate Income Shock tests how many weeks your buffer can survive if earnings drop unexpectedly."
    },

    # ── SURE AI Coach (coach.html) ──
    "EXPLAIN_PAGE": {
        "button_id": "EXPLAIN_PAGE",
        "label": "Explain this page",
        "page": "coach.html",
        "purpose": "Asks SURE AI to provide a comprehensive explanation of the currently active page.",
        "meaning": "Sends the active page route, visible controls, and page purpose to SURE AI.",
        "when_to_use": "When you land on an unfamiliar page and want a clear walkthrough of what to do.",
        "preconditions": "Active page context.",
        "what_happens_after_click": "SURE AI replies with the page's purpose, key metrics, available actions, and recommended next steps.",
        "what_it_does_not_do": "Does not navigate away from the page.",
        "expected_result": "A structured page explanation card appears in the chat stream.",
        "possible_errors": "None.",
        "confirmation_required": False,
        "financial_mutation": False,
        "danger_level": "safe",
        "navigation_target": "coach.html",
        "success_message": "Page explanation retrieved.",
        "help_text": "Explain this page gives you an immediate walkthrough of whatever screen you are currently viewing."
    }
}

def get_button_info(button_id: str) -> Optional[Dict[str, Any]]:
    """Lookup button specification by ID or label keyword."""
    clean = button_id.upper().replace("-", "_").replace(" ", "_")
    if clean in BUTTON_REGISTRY:
        return BUTTON_REGISTRY[clean]
    
    # Fuzzy search by label or purpose
    query = button_id.lower().replace("_", " ").replace("-", " ")
    for key, spec in BUTTON_REGISTRY.items():
        if query in spec["label"].lower() or query in spec["purpose"].lower():
            return spec
    return None

def list_buttons_for_page(page_route: str) -> List[Dict[str, Any]]:
    """List all registered buttons for a given page."""
    clean_route = page_route.lower().replace("/", "")
    return [
        spec for spec in BUTTON_REGISTRY.values()
        if clean_route in spec["page"].lower() or spec["page"].lower() in clean_route
    ]
