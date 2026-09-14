"""
SURE SAVINGS: Automated HTML Internationalization Patcher
Injects js/i18n.js script tag and standard data-i18n attributes across all 15 repository pages.
"""
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HTML_FILES = [
    "landing.html",
    "login.html",
    "index.html",
    "bank-accounts.html",
    "income-intelligence.html",
    "calendar.html",
    "planner.html",
    "decision-pipeline.html",
    "goals.html",
    "risk.html",
    "health.html",
    "activity.html",
    "simulator.html",
    "coach.html",
    "resilience-plan.html"
]

# Patterns to tag with data-i18n
TAG_REPLACEMENTS = [
    # Navigation items
    (r'(<span>Command Center</span>)', r'<span data-i18n="navigation.command_center">Command Center</span>'),
    (r'(<span class="flex-1">Bank Accounts</span>)', r'<span class="flex-1" data-i18n="navigation.bank_accounts">Bank Accounts</span>'),
    (r'(<span>Bank Accounts</span>)', r'<span data-i18n="navigation.bank_accounts">Bank Accounts</span>'),
    (r'(<span class="flex-1">Resilience Plan</span>)', r'<span class="flex-1" data-i18n="navigation.resilience_plan">Resilience Plan</span>'),
    (r'(<span>Resilience Plan</span>)', r'<span data-i18n="navigation.resilience_plan">Resilience Plan</span>'),
    (r'(<span>Income Intelligence</span>)', r'<span data-i18n="navigation.income_intelligence">Income Intelligence</span>'),
    (r'(<span>Cash Flow Planner</span>)', r'<span data-i18n="navigation.cash_flow_planner">Cash Flow Planner</span>'),
    (r'(<span>Decision Pipeline</span>)', r'<span data-i18n="navigation.decision_pipeline">Decision Pipeline</span>'),
    (r'(<span>Income Calendar</span>)', r'<span data-i18n="navigation.income_calendar">Income Calendar</span>'),
    (r'(<span>Goals & Buffer Plan</span>)', r'<span data-i18n="navigation.goals_buffer">Goals & Buffer Plan</span>'),
    (r'(<span>Goals &amp; Buffer Plan</span>)', r'<span data-i18n="navigation.goals_buffer">Goals & Buffer Plan</span>'),
    (r'(<span>Goals & Buffer</span>)', r'<span data-i18n="navigation.goals_buffer">Goals & Buffer</span>'),
    (r'(<span>Goals &amp; Buffer</span>)', r'<span data-i18n="navigation.goals_buffer">Goals & Buffer</span>'),
    (r'(<span>Risk & Early Warning</span>)', r'<span data-i18n="navigation.risk_early_warning">Risk & Early Warning</span>'),
    (r'(<span>Risk &amp; Early Warning</span>)', r'<span data-i18n="navigation.risk_early_warning">Risk & Early Warning</span>'),
    (r'(<span>Financial Health</span>)', r'<span data-i18n="navigation.financial_health">Financial Health</span>'),
    (r'(<span>Transactions & Activity</span>)', r'<span data-i18n="navigation.transactions_activity">Transactions & Activity</span>'),
    (r'(<span>Transactions &amp; Activity</span>)', r'<span data-i18n="navigation.transactions_activity">Transactions & Activity</span>'),
    (r'(<span>SURE AI Guide</span>)', r'<span data-i18n="navigation.sure_ai_coach">SURE AI Guide</span>'),
    (r'(<span>SURE AI Guidance</span>)', r'<span data-i18n="navigation.sure_ai_coach">SURE AI Guidance</span>'),
    (r'(<span>Calibrate Baseline</span>)', r'<span data-i18n="navigation.calibrate_baseline">Calibrate Baseline</span>'),
    (r'(<span>Export Data</span>)', r'<span data-i18n="navigation.export_data">Export Data</span>'),
    (r'(<span>Sign Out</span>)', r'<span data-i18n="navigation.sign_out">Sign Out</span>'),
    (r'(<span>🌐 Public Explorer</span>)', r'<span data-i18n="navigation.public_explorer">🌐 Public Explorer</span>'),
    (r'(<span>Liquidity Intelligence</span>)', r'<span data-i18n="navigation.brand_subtitle">Liquidity Intelligence</span>'),
    (r'(<span class="font-medium">SOC-2 Type II Vault</span>)', r'<span class="font-medium" data-i18n="navigation.soc2_badge">SOC-2 Type II Vault</span>'),
    (r'(<span>256-bit TLS Encrypted</span>)', r'<span data-i18n="navigation.encryption_badge">256-bit TLS Encrypted</span>'),
    
    # Common buttons
    (r'(<span>Approve Reserve Transfer</span>)', r'<span data-i18n="dashboard.approve_transfer_btn">Approve Reserve Transfer</span>'),
    (r'(<span>Sync Now</span>)', r'<span data-i18n="common.sync_now">Sync Now</span>'),
    (r'(<span>Connect Bank Account</span>)', r'<span data-i18n="common.connect_bank">Connect Bank Account</span>'),
    (r'(<span>Disconnect</span>)', r'<span data-i18n="bank.disconnect">Disconnect</span>'),
    (r'(<span>Revoke Consent</span>)', r'<span data-i18n="bank.revoke_consent">Revoke Consent</span>'),
    (r'(<span>Add Scheduled Event</span>)', r'<span data-i18n="calendar.add_event">Add Scheduled Event</span>'),
    (r'(<span>Create New Goal</span>)', r'<span data-i18n="goals.add_goal">Create New Goal</span>'),
    (r'(<span>Execute Stress Simulation</span>)', r'<span data-i18n="simulator.simulate_run">Execute Stress Simulation</span>'),
    
    # Dashboard and Metric headers
    (r'(<h2 class="text-xs font-bold uppercase tracking-wider"[^>]*>Navigation</h2>)', r'<h2 class="text-xs font-bold uppercase tracking-wider" style="color: var(--text-subtle)" data-i18n="navigation.command_center">Navigation</h2>'),
]


def patch_html_files():
    count_patched = 0
    for filename in HTML_FILES:
        filepath = os.path.join(ROOT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Skipping missing file: {filename}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # 1. Ensure <script src="js/i18n.js"></script> is included before js/api.js
        if "js/i18n.js" not in content:
            # Find first <script src="js/api.js
            match = re.search(r'(<script src="js/api\.js[^"]*"></script>)', content)
            if match:
                content = content[:match.start()] + '<script src="js/i18n.js"></script>\n' + content[match.start():]
            else:
                # Place before </body>
                body_close = content.rfind("</body>")
                if body_close != -1:
                    content = content[:body_close] + '<script src="js/i18n.js"></script>\n' + content[body_close:]

        # 2. Apply data-i18n tags
        for pattern, replacement in TAG_REPLACEMENTS:
            # Avoid duplicate tagging
            if 'data-i18n' not in pattern:
                content = re.sub(pattern, replacement, content)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Patched i18n into {filename}")
            count_patched += 1
        else:
            print(f"  Already up to date: {filename}")

    print(f"\nCompleted patching {count_patched} HTML files with i18n support.")


if __name__ == "__main__":
    patch_html_files()
