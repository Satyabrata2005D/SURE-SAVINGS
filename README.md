# SURE SAVINGS — Smart Income Buffer
### VIT Chennai Hackathon • Financial Resilience for Gig & Informal Workers

> **Hackathon Problem Statement:**  
> *How might banking technology help gig workers and individuals with irregular incomes build financial resilience through intelligent savings, responsible access to credit, and personalized financial guidance?*

**SURE SAVINGS** is an institutional-grade, AI-assisted deterministic financial resilience platform designed specifically for gig workers with volatile weekly incomes (e.g. food delivery riders, quick-commerce couriers, and platform freelancers).

---

## 🎯 Canonical Demo Persona: Arjun K.

- **Profile:** Arjun K., 27 years old, Delivery & Freelance Lead (Zomato, Blinkit, Fiverr)
- **Currency:** Indian Rupee (₹ INR strictly)
- **Current Cycle:** Week 36
- **Current Week Income:** **₹8,400** (Zomato ₹4,900 + Blinkit ₹2,600 + Direct Freelance ₹900)
- **Stabilized Baseline:** **₹7,100** (`0.60 × Median [₹7,050] + 0.40 × Mean [₹7,180]`)
- **Next Week Forecast:** **₹6,900** (92% confidence corridor)
- **Income Volatility:** **31%** (12-week rolling coefficient of variation)
- **Current Liquid Buffer:** **₹6,800**
- **Buffer Target:** **₹15,000** (~4 weeks of essential runway)
- **Protected Cash Floor:** **₹3,500** (Strictly untouchable in primary checking account)
- **Weekly Fixed Essential Burn:** **₹4,400** (Rent, fuel, EV two-wheeler EMI, basic groceries)
- **Current Buffer Runway:** **1.5 weeks**
- **Calculated Surplus:** `max(0, ₹8,400 - ₹7,100)` = **₹1,300**
- **Deterministic Recommendation:** Save **₹900** (`70% × ₹1,300 = ₹910 → rounded to ₹900`)
- **Free Pocket Cash Left:** `₹1,300 - ₹900` = **₹400**
- **Financial Resilience Score:** **74 / 100** (Pillars: Stability 82, Coverage 68, Expense 75, Cash Flow 71)
- **Financial Risk Score:** **23 / 100** (Low overall)
- **Post-Approval Impact:** Buffer **₹6,800 → ₹7,700**, Runway **1.5 → 1.7 weeks**, Score **74 → 77**
- **Critical Intraday Timing Gap (Sep 10, 2026):**
  - HDFC Bike EV EMI (₹4,500) debits at 09:00 AM
  - Zomato weekly payout (+₹6,900) batches at 06:00 PM
  - Intraday gap: **-₹1,400**; absorbed smoothly by ₹3,300 safe buffer without breaching ₹3,500 checking floor.

---

## 🛡️ Core Financial Architecture & Safety Invariants

1. **Zero Fund Movement Guarantee:** The AI explanation layer is 100% read-only advisory. LLM prompts cannot execute transfers or invent numerical amounts.
2. **Protected Cash Floor Invariant:** Buffer recommendations never breach or touch the ₹3,500 cash floor.
3. **Deterministic 70% Surplus Safeguard:**
   $$\text{Recommended Allocation} = \text{round}\big(\min(\text{Surplus} \times 0.70, \text{Target} - \text{Current Buffer})\big)$$
4. **Adaptive Emergency Pause:** If weekly income falls below the stabilized baseline (₹7,100), savings recommendations automatically drop to ₹0 and the system transitions into capital preservation mode.

---

## 🖥️ 12 High-Fidelity Modules

| Module | Route | Highlights |
| :--- | :--- | :--- |
| **Command Center** | [`index.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/index.html) | Primary dashboard, Resilience Score gauge (74/100), ₹900 recommendation card, 12-week income variance baseline |
| **SURE SAVINGS** | [`simulator.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/simulator.html) | Real-time sliders (₹0–₹5,000 contribution, ₹0–₹3,300 withdrawal), 4 shock scenarios (Normal, -20%, -40%, -60%), composition gauge |
| **Income Intelligence** | [`income-intelligence.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/income-intelligence.html) | Volatility matrix (31%), platform distribution (Zomato ₹4.9k, Blinkit ₹2.6k, Direct ₹0.9k) |
| **Cash Flow Planner** | [`planner.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/planner.html) | Forward cash trajectory, 14/30/60 day horizons, scheduled debit list, CSV export |
| **Decision Pipeline** | [`decision-pipeline.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/decision-pipeline.html) | 7-step deterministic mathematical execution pipeline, "Download Audit JSON" & "Re-run Engine Check" |
| **Income Calendar** | [`calendar.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/calendar.html) | September 2026 calendar with Sep 10 intraday gap inspector pane (-₹1,400 risk analysis) |
| **Goals & Buffer Plan** | [`goals.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/goals.html) | 3 buffer sub-goals (Bike EMI, Rent cushion, Emergency reserve) |
| **Risk & Early Warning** | [`risk.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/risk.html) | Threat telemetry vectors, risk index (23/100), automated defensive adjustments |
| **Financial Health** | [`health.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/health.html) | 4 resilience pillars, historical progression (68 → 74 → 76) |
| **Transactions & Activity**| [`activity.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/activity.html) | Transaction ledger with interactive tab filters (Income, Essential, Buffer, System) & live search |
| **AI Resilience Coach** | [`coach.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/coach.html) | Grounded chat engine with preset prompt chips and refusal guardrails on fund movement commands |
| **Login & Sandbox Portal** | [`login.html`](file:///Users/satyabratadas/Documents/SURE%20SAVINGS/login.html) | Fast-fill demo access for Arjun K. with instant sandbox switching |

---

## 🚀 Running the Project Locally

### 1. Start Frontend Server (Port 3000)
```bash
# In project root:
python3 -m http.server 3000
```
Open **[http://localhost:3000](http://localhost:3000)** in any browser.

### 2. Start FastAPI Backend (Port 8000)
```bash
# In project root:
source ./venv/bin/activate
PYTHONPATH=. uvicorn backend.main:app --port 8000 --host 127.0.0.1 --reload
```
API Documentation available at: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

### 3. Run Invariant Safety Test Suite
```bash
PYTHONPATH=. ./venv/bin/python backend/test_financial_engine.py
```
Expected output:
```text
ALL 7 FINANCIAL SAFETY & INVARIANT TESTS PASSED!
```

---

## 📦 Technology Stack

- **Frontend:** HTML5 Semantic Structure, TailwindCSS, Vanilla JavaScript (Reactive Store, Interactive Sliders, Live Search/Filter, Modal Triggers)
- **Backend:** Python 3.14, FastAPI, Uvicorn, Pydantic v2, NumPy, Scikit-Learn
- **Design System:** Off-white canvas (`#FAF9F6`), Slate (`#0F172A`), Coral CTA (`#FF5B45`), Emerald Positive (`#059669`), Plus Jakarta Sans, JetBrains Mono
- **Architectural Security:** SOC-2 compliance principles, read-only AI advisory layer, deterministic mathematical rules for all financial transactions.
