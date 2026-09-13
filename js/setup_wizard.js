/**
 * SURE SAVINGS 5.0 / 6.0: Personal Financial Setup Wizard & Quick Start Controller
 * Enables real authenticated users to enter their actual financial situation,
 * calibrate their baseline in 30 seconds or via full 8-step wizard,
 * and recalculates their Financial Digital Twin dynamically.
 */

const setupWizard = {
  activeStep: 1,
  totalSteps: 8,
  wizardData: {
    occupation: "",
    income_type: "gig",
    income_sources: [],
    income_history: [],
    expenses: [],
    checking_cash: 0,
    savings_balance: 0,
    physical_cash: 0,
    protected_floor: null,
    floor_preference: "CALCULATED",
    buffer_target_weeks: 4,
    custom_target: null,
    obligations: [],
    goals: []
  },

  // -------------------------------------------------------------------
  // Setup Banner on Dashboard
  // -------------------------------------------------------------------
  renderDashboardBanner() {
    const container = document.getElementById("setup-banner-container");
    if (!container) return;

    const fullState = window.sureSavingsStore?.getState() || {};
    const profile = fullState.profile || {};
    const readiness = fullState.readiness || {
      readiness_percentage: profile.readiness_percentage || 0,
      maturity_level: profile.data_maturity_level || 0,
      dimensions: {}
    };

    const isDemo = Boolean(profile.is_demo_user);

    if (isDemo) {
      container.innerHTML = `
        <div class="p-4 rounded-2xl border border-amber-200/80 bg-amber-50/70 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div class="flex items-center space-x-3">
            <span class="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse"></span>
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-bold text-amber-900 uppercase tracking-wider">Public Demo Persona • Arjun K.</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-200 text-amber-900">SAMPLE DATA</span>
              </div>
              <p class="text-[11px] text-amber-800 mt-0.5">
                Exploring simulated delivery worker resilience (₹8,400 income • ₹6,800 buffer • 74 score). Sign in with your account to build your private workspace.
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2 w-full sm:w-auto">
            <button onclick="window.setupWizard.openQuickStartModal()" class="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all whitespace-nowrap">
              Try Calibration
            </button>
          </div>
        </div>
      `;
      return;
    }

    const isSetupDone = Boolean(profile.setup_completed || (readiness.readiness_percentage && readiness.readiness_percentage >= 80));
    const readinessPct = isSetupDone ? 100 : (readiness.readiness_percentage || 0);
    const maturity = isSetupDone ? 5 : (readiness.maturity_level || 0);

    const dims = readiness.dimensions || {};
    const steps = readiness.completed_steps || [];
    const incomeDone = dims.income_sources || profile.current_income > 0 || steps.includes('income') || isSetupDone;
    const expensesDone = dims.expense_profile || profile.weekly_burn > 0 || steps.includes('expenses') || isSetupDone;
    const cashDone = dims.liquidity || (profile.protected_floor > 0 || profile.safe_to_use_above_floor > 0) || steps.includes('liquidity') || isSetupDone;
    const bufferDone = dims.buffer || profile.current_buffer > 0 || steps.includes('goals') || steps.includes('buffer') || isSetupDone;
    const obligationsDone = dims.obligations || steps.includes('obligations') || (fullState.obligations && fullState.obligations.length > 0) || isSetupDone;
    const historyDone = dims.income_history || steps.includes('history') || steps.includes('history_basic') || steps.includes('history_single') || (fullState.history && fullState.history.length > 0) || isSetupDone;
    const goalsDone = dims.goals || steps.includes('goals') || (profile.buffer_target > 0) || (fullState.goals && fullState.goals.length > 0) || isSetupDone;

    container.innerHTML = `
      <div class="p-5 rounded-2xl border ${isSetupDone ? 'border-emerald-200 bg-emerald-50/50' : 'border-stone-200/90 bg-white'} shadow-soft space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div class="flex items-center space-x-2">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold ${isSetupDone ? 'bg-emerald-100 text-emerald-800' : 'bg-brand-50 text-brand-600 border border-brand-200'} uppercase tracking-wider">
                ${isSetupDone ? '✓ Private Workspace Active' : '⚡ Financial Setup Required'}
              </span>
              <span class="text-[11px] font-semibold text-stone-500">
                Data Maturity: Level ${maturity}/5
              </span>
            </div>
            <h3 class="text-base font-bold text-stone-900 mt-1">
              ${isSetupDone ? 'Personal Financial Digital Twin Calibrated' : 'Let’s Understand Your Financial Situation'}
            </h3>
            <p class="text-xs text-stone-500">
              ${isSetupDone 
                ? 'Your engine is calculating surplus, resilience, and liquidity safeguards from your own raw financial data.' 
                : 'SURE SAVINGS doesn’t assume your finances. Enter your real baseline to unlock personalized intelligence.'}
            </p>
          </div>

          <div class="flex items-center space-x-2">
            <button onclick="window.setupWizard.openQuickStartModal()" class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-sm brand-glow transition-all flex items-center space-x-1.5">
              <span>⚡ 30-Sec Quick Start</span>
            </button>
            <button onclick="window.setupWizard.openSetupWizardModal()" class="px-3.5 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 font-semibold text-xs rounded-xl border border-stone-200 transition-all">
              ${isSetupDone ? 'Edit Setup' : 'Full Setup (8 Steps)'}
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="space-y-1.5">
          <div class="flex justify-between items-center text-xs text-stone-600">
            <span class="font-semibold">Financial Data Readiness</span>
            <span class="font-bold text-brand-600 font-mono">${readinessPct}%</span>
          </div>
          <div class="w-full h-2 bg-stone-100 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-brand-500 to-emerald-500 transition-all duration-500" style="width: ${readinessPct}%"></div>
          </div>
        </div>

        <!-- Readiness Checklist Badges -->
        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 pt-1">
          <div class="px-2.5 py-1.5 rounded-lg border ${incomeDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>Income</span>
            <span>${incomeDone ? '✓' : '○'}</span>
          </div>
          <div class="px-2.5 py-1.5 rounded-lg border ${expensesDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>Expenses</span>
            <span>${expensesDone ? '✓' : '○'}</span>
          </div>
          <div class="px-2.5 py-1.5 rounded-lg border ${cashDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>Liquidity</span>
            <span>${cashDone ? '✓' : '○'}</span>
          </div>
          <div class="px-2.5 py-1.5 rounded-lg border ${bufferDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>Buffer</span>
            <span>${bufferDone ? '✓' : '○'}</span>
          </div>
          <div class="px-2.5 py-1.5 rounded-lg border ${obligationsDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>Obligations</span>
            <span>${obligationsDone ? '✓' : '○'}</span>
          </div>
          <div class="px-2.5 py-1.5 rounded-lg border ${historyDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>History</span>
            <span>${historyDone ? '✓' : '○'}</span>
          </div>
          <div class="px-2.5 py-1.5 rounded-lg border ${goalsDone ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-stone-50 text-stone-500 border-stone-200'} text-[11px] font-medium flex items-center justify-between">
            <span>Goals</span>
            <span>${goalsDone ? '✓' : '○'}</span>
          </div>
        </div>
      </div>
    `;
  },

  // -------------------------------------------------------------------
  // Quick Start Modal (30-Second Rapid Calibration)
  // -------------------------------------------------------------------
  openQuickStartModal() {
    const existing = document.getElementById("quickStartModal");
    if (existing) existing.remove();

    const profile = window.sureSavingsStore?.getProfile() || {};
    const defaultIncome = profile.current_income > 0 ? profile.current_income : "";
    const defaultBurn = profile.weekly_burn > 0 ? profile.weekly_burn : "";
    const defaultBuffer = profile.current_buffer > 0 ? profile.current_buffer : "";
    const defaultFloor = profile.protected_floor > 0 ? profile.protected_floor : "";

    const modal = document.createElement("div");
    modal.id = "quickStartModal";
    modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-sm animate-fade-in";
    modal.innerHTML = `
      <div class="glass-modal rounded-2xl max-w-lg w-full p-6 sm:p-7 shadow-2xl border border-stone-200 space-y-5 text-left transform transition-all">
        <div class="flex items-center justify-between pb-3 border-b border-stone-100">
          <div class="flex items-center space-x-2.5">
            <div class="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-base">
              ⚡
            </div>
            <div>
              <h3 class="font-bold text-stone-900 text-sm sm:text-base">30-Second Financial Calibration</h3>
              <p class="text-[11px] text-stone-500">Provide 4 numbers to immediately generate your personal resilience intelligence</p>
            </div>
          </div>
          <button onclick="document.getElementById('quickStartModal').remove()" class="text-stone-400 hover:text-stone-600 text-base">✕</button>
        </div>

        <form id="quickStartForm" onsubmit="window.setupWizard.handleQuickStartSubmit(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">
              1. Average Weekly Income <span class="text-rose-500">*</span>
            </label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
              <input type="number" id="qs-income" required min="0" step="100" placeholder="e.g. 10000"
                value="${defaultIncome}"
                class="w-full pl-7 pr-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono">
            </div>
            <p class="text-[10px] text-stone-400 mt-1">What you typically earn per week across all platforms or clients.</p>
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">
              2. Essential Weekly Expenses <span class="text-rose-500">*</span>
            </label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
              <input type="number" id="qs-expenses" required min="0" step="100" placeholder="e.g. 6000"
                value="${defaultBurn}"
                class="w-full pl-7 pr-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono">
            </div>
            <p class="text-[10px] text-stone-400 mt-1">Unavoidable survival commitments (weekly portion of rent, groceries, transit, EMI).</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-stone-800 mb-1">
                3. Current Liquid Cash <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
                <input type="number" id="qs-cash" required min="0" step="100" placeholder="e.g. 8000"
                  class="w-full pl-7 pr-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono">
              </div>
              <p class="text-[10px] text-stone-400 mt-1">Cash in bank account or wallet ready to spend.</p>
            </div>

            <div>
              <label class="block text-xs font-bold text-stone-800 mb-1">
                4. Existing Emergency Savings <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
                <input type="number" id="qs-savings" required min="0" step="100" placeholder="e.g. 5000"
                  value="${defaultBuffer}"
                  class="w-full pl-7 pr-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono">
              </div>
              <p class="text-[10px] text-stone-400 mt-1">Dedicated rainy-day or emergency buffer.</p>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">
              5. Protected Floor <span class="text-stone-400 font-normal">(Optional)</span>
            </label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
              <input type="number" id="qs-floor" min="0" step="100" placeholder="Leave blank for automatic 80% calculation"
                value="${defaultFloor}"
                class="w-full pl-7 pr-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono">
            </div>
            <p class="text-[10px] text-stone-400 mt-1">Minimum cash never to be touched by automated savings sweeps.</p>
          </div>

          <div class="p-3 bg-stone-50 border border-stone-200 rounded-xl text-[11px] text-stone-600 space-y-1">
            <span class="font-bold text-stone-800">What happens next?</span>
            <p>Our deterministic engine will calculate your real weekly surplus, policy-safe contribution, runway coverage, and initial resilience score.</p>
          </div>

          <div class="flex items-center justify-end space-x-3 pt-2">
            <button type="button" onclick="document.getElementById('quickStartModal').remove()" class="px-4 py-2 text-xs font-semibold text-stone-600 hover:bg-stone-100 rounded-xl transition-colors">
              Cancel
            </button>
            <button type="submit" id="qs-submit-btn" class="px-5 py-2 text-xs font-bold text-white bg-brand-500 hover:bg-brand-600 rounded-xl shadow-md brand-glow transition-all">
              Activate Financial Intelligence →
            </button>
          </div>
        </form>
      </div>
    `;
    document.body.appendChild(modal);
  },

  async handleQuickStartSubmit(event) {
    event.preventDefault();
    const btn = document.getElementById("qs-submit-btn");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="animate-spin inline-block mr-1.5">⟳</span> Calculating Digital Twin...`;
    }

    const income = parseFloat(document.getElementById("qs-income").value) || 0;
    const expenses = parseFloat(document.getElementById("qs-expenses").value) || 0;
    const cash = parseFloat(document.getElementById("qs-cash").value) || 0;
    const savings = parseFloat(document.getElementById("qs-savings").value) || 0;
    const floorVal = document.getElementById("qs-floor").value;
    const floor = floorVal ? parseFloat(floorVal) : null;

    if (!window.sureSavingsApi || typeof window.sureSavingsApi.applyQuickStart !== "function") {
      const errMsg = "API Client is synchronizing with the backend. Please try again in a moment.";
      if (window.showToast) window.showToast("Syncing...", errMsg, "warning");
      else alert(errMsg);
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Activate Financial Intelligence →";
      }
      return;
    }

    try {
      const res = await window.sureSavingsApi.applyQuickStart({
        weeklyIncome: income,
        essentialExpenses: expenses,
        currentCash: cash,
        emergencySavings: savings,
        protectedFloor: floor
      });

      const surplus = res.data?.profile?.surplus ?? res.profile?.surplus ?? 0;
      if (window.showToast) {
        window.showToast("Workspace Activated", `Calibrated weekly surplus of ₹${Number(surplus).toLocaleString()} computed.`, "success");
      }

      document.getElementById("quickStartModal")?.remove();

      // Refresh store state from backend
      if (window.sureSavingsStore) {
        await window.sureSavingsStore.syncFromBackend(true);
      }

      // Re-render UI
      this.renderDashboardBanner();
      if (typeof window.updatePageMetrics === "function") {
        window.updatePageMetrics();
      }
    } catch (err) {
      if (window.showToast) {
        window.showToast("Calibration Failed", err.message || "Failed to calculate digital twin", "error");
      } else {
        alert("Calibration failed: " + err.message);
      }
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Activate Financial Intelligence →";
      }
    }
  },

  // -------------------------------------------------------------------
  // Multi-Step Guided Setup Wizard Modal
  // -------------------------------------------------------------------
  openSetupWizardModal(initialStep = 1) {
    this.activeStep = initialStep;
    const existing = document.getElementById("setupWizardModal");
    if (existing) existing.remove();

    const modal = document.createElement("div");
    modal.id = "setupWizardModal";
    modal.className = "fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-stone-900/60 backdrop-blur-sm animate-fade-in";
    modal.innerHTML = `
      <div class="glass-modal rounded-2xl max-w-2xl w-full p-5 sm:p-7 shadow-2xl border border-stone-200 space-y-5 text-left transform transition-all flex flex-col max-h-[90vh]">
        <!-- Wizard Header -->
        <div class="flex items-center justify-between pb-3 border-b border-stone-100 flex-shrink-0">
          <div>
            <div class="flex items-center space-x-2">
              <span class="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-brand-50 text-brand-600 uppercase tracking-wider">
                Financial Setup Wizard
              </span>
              <span class="text-xs font-bold text-stone-500" id="wizard-step-indicator">
                Step 1 of 8
              </span>
            </div>
            <h3 class="font-bold text-stone-900 text-sm sm:text-base mt-0.5" id="wizard-step-title">
              1. About You & Work Context
            </h3>
          </div>
          <button onclick="document.getElementById('setupWizardModal').remove()" class="text-stone-400 hover:text-stone-600 text-base">✕</button>
        </div>

        <!-- Wizard Step Body Container -->
        <div class="flex-1 overflow-y-auto space-y-4 pr-1" id="wizard-step-body">
          <!-- Dynamically populated by renderStep() -->
        </div>

        <!-- Wizard Navigation Footer -->
        <div class="flex items-center justify-between pt-3 border-t border-stone-100 flex-shrink-0">
          <button id="wizard-prev-btn" onclick="window.setupWizard.prevStep()" class="px-4 py-2 text-xs font-semibold text-stone-600 hover:bg-stone-100 rounded-xl transition-colors disabled:opacity-40 disabled:pointer-events-none">
            ← Back
          </button>
          <div class="flex items-center space-x-2">
            <button onclick="document.getElementById('setupWizardModal').remove()" class="px-3.5 py-2 text-xs font-semibold text-stone-500 hover:text-stone-700">
              Save & Exit
            </button>
            <button id="wizard-next-btn" onclick="window.setupWizard.nextStep()" class="px-5 py-2 text-xs font-bold text-white bg-brand-500 hover:bg-brand-600 rounded-xl shadow-md brand-glow transition-all">
              Save & Continue →
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    this.renderStep(this.activeStep);
  },

  renderStep(step) {
    this.activeStep = step;
    const body = document.getElementById("wizard-step-body");
    const indicator = document.getElementById("wizard-step-indicator");
    const title = document.getElementById("wizard-step-title");
    const prevBtn = document.getElementById("wizard-prev-btn");
    const nextBtn = document.getElementById("wizard-next-btn");

    if (!body) return;

    if (indicator) indicator.textContent = `Step ${step} of 8`;
    if (prevBtn) prevBtn.disabled = step === 1;
    if (nextBtn) {
      nextBtn.textContent = step === 8 ? "Finish & Recalculate ✓" : "Save & Continue →";
    }

    const titles = {
      1: "1. About You & Work Context",
      2: "2. Income Sources",
      3: "3. Income History (Past Weeks)",
      4: "4. Recurring Expenses & Burn",
      5: "5. Cash & Protected Floor",
      6: "6. Emergency Buffer & Target",
      7: "7. Scheduled Commitments & Obligations",
      8: "8. Review & Activate Digital Twin"
    };
    if (title) title.textContent = titles[step] || `Step ${step}`;

    if (step === 1) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Tell us how you earn so the engine can configure the proper volatility and cash-flow model.
          </p>
          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">Primary Income Type</label>
            <select id="w-income-type" class="w-full px-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none">
              <option value="gig">Gig Platform Work (Zomato, Swiggy, Uber, Blinkit)</option>
              <option value="freelance">Independent Freelancer / Consultant</option>
              <option value="salary">Salaried Professional</option>
              <option value="salary_plus_gig">Salary + Secondary Side Income</option>
              <option value="business">Small Business / Micro-Enterprise</option>
              <option value="multiple">Multiple Irregular Inflow Streams</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">Occupation Title</label>
            <input type="text" id="w-occupation" placeholder="e.g. Full-Stack UI Designer or Delivery Fleet Partner"
              class="w-full px-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none">
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-stone-800 mb-1">Currency</label>
              <input type="text" id="w-currency" value="INR (₹)" disabled
                class="w-full px-3 py-2 text-xs border border-stone-200 bg-stone-50 rounded-xl text-stone-500">
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-800 mb-1">Timezone</label>
              <input type="text" id="w-timezone" value="Asia/Kolkata (IST)" disabled
                class="w-full px-3 py-2 text-xs border border-stone-200 bg-stone-50 rounded-xl text-stone-500">
            </div>
          </div>
        </div>
      `;
    } else if (step === 2) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Add each client or platform you earn from. This measures your income concentration risk.
          </p>
          <div id="income-sources-list" class="space-y-2">
            <div class="p-3 bg-stone-50 border border-stone-200 rounded-xl flex items-center justify-between text-xs">
              <div>
                <p class="font-bold text-stone-900">Primary Weekly Work</p>
                <p class="text-[10px] text-stone-500">Weekly payout on Wednesday</p>
              </div>
              <div class="text-right">
                <span class="font-bold text-stone-900 font-mono">Typical Inflow</span>
              </div>
            </div>
          </div>
          <div class="p-4 border border-dashed border-stone-300 rounded-xl space-y-3 bg-stone-50/50">
            <h4 class="text-xs font-bold text-stone-800">+ Add Income Source</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <input type="text" id="new-src-name" placeholder="Source Name (e.g. Zomato, Client X)" class="px-3 py-1.5 text-xs border rounded-lg">
              <input type="number" id="new-src-amt" placeholder="Typical Payout (₹)" class="px-3 py-1.5 text-xs border rounded-lg font-mono">
            </div>
            <div class="grid grid-cols-2 gap-2">
              <select id="new-src-freq" class="px-2 py-1.5 text-xs border rounded-lg">
                <option value="weekly">Weekly</option>
                <option value="biweekly">Bi-weekly</option>
                <option value="monthly">Monthly</option>
                <option value="irregular">Irregular</option>
              </select>
              <input type="text" id="new-src-day" placeholder="Payout Day (e.g. Wed)" class="px-3 py-1.5 text-xs border rounded-lg">
            </div>
            <button type="button" onclick="window.setupWizard.handleAddIncomeSource()" class="px-3 py-1.5 bg-stone-800 hover:bg-stone-900 text-white font-semibold text-xs rounded-lg shadow-sm">
              + Save Source
            </button>
          </div>
        </div>
      `;
    } else if (step === 3) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Enter past weeks of earnings to calculate your income volatility and unlock predictive forecasting.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] font-bold text-stone-700 mb-1">Week 1 (Most Recent)</label>
              <input type="number" id="wh-1" placeholder="₹ Amount" class="w-full px-3 py-2 text-xs border rounded-xl font-mono">
            </div>
            <div>
              <label class="block text-[11px] font-bold text-stone-700 mb-1">Week 2</label>
              <input type="number" id="wh-2" placeholder="₹ Amount" class="w-full px-3 py-2 text-xs border rounded-xl font-mono">
            </div>
            <div>
              <label class="block text-[11px] font-bold text-stone-700 mb-1">Week 3</label>
              <input type="number" id="wh-3" placeholder="₹ Amount" class="w-full px-3 py-2 text-xs border rounded-xl font-mono">
            </div>
            <div>
              <label class="block text-[11px] font-bold text-stone-700 mb-1">Week 4 (Unlocks Forecasting)</label>
              <input type="number" id="wh-4" placeholder="₹ Amount" class="w-full px-3 py-2 text-xs border rounded-xl font-mono">
            </div>
          </div>
          <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-[11px] text-amber-900">
            <span class="font-bold">Confidence Tier:</span> 4+ weeks unlocks the statistical forecasting engine. 8+ weeks activates full volatility trend analysis.
          </div>
        </div>
      `;
    } else if (step === 4) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Separate essential living costs (rent, food, fuel, EMI) from discretionary spending to determine your true weekly burn.
          </p>
          <div class="p-4 border border-dashed border-stone-300 rounded-xl space-y-3 bg-stone-50/50">
            <h4 class="text-xs font-bold text-stone-800">+ Add Recurring Expense</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <input type="text" id="new-exp-desc" placeholder="Expense Name (e.g. Room Rent, Bike EMI)" class="px-3 py-1.5 text-xs border rounded-lg">
              <input type="number" id="new-exp-amt" placeholder="Amount (₹)" class="px-3 py-1.5 text-xs border rounded-lg font-mono">
            </div>
            <div class="grid grid-cols-2 gap-2">
              <select id="new-exp-cat" class="px-2 py-1.5 text-xs border rounded-lg">
                <option value="housing">Housing / Rent</option>
                <option value="food">Groceries & Food</option>
                <option value="transport">Transit & Fuel</option>
                <option value="EMI">Loan / EMI</option>
                <option value="utilities">Electricity & Utilities</option>
                <option value="medical">Medical & Health</option>
                <option value="subscriptions">Subscriptions</option>
                <option value="entertainment">Entertainment</option>
              </select>
              <select id="new-exp-freq" class="px-2 py-1.5 text-xs border rounded-lg">
                <option value="monthly">Monthly</option>
                <option value="weekly">Weekly</option>
                <option value="daily">Daily</option>
                <option value="annual">Annual</option>
              </select>
            </div>
            <div class="flex items-center space-x-2">
              <input type="checkbox" id="new-exp-ess" checked class="rounded border-stone-300 text-brand-600 focus:ring-brand-500">
              <label for="new-exp-ess" class="text-xs text-stone-700 font-medium">Essential for survival (Uncuttable baseline)</label>
            </div>
            <button type="button" onclick="window.setupWizard.handleAddExpense()" class="px-3 py-1.5 bg-stone-800 hover:bg-stone-900 text-white font-semibold text-xs rounded-lg shadow-sm">
              + Save Expense
            </button>
          </div>
        </div>
      `;
    } else if (step === 5) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Configure your accessible cash and determine your protected checking floor.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-stone-800 mb-1">Checking / Bank Balance</label>
              <div class="relative">
                <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
                <input type="number" id="w-liq-checking" placeholder="0" class="w-full pl-7 pr-3 py-2 text-xs border rounded-xl font-mono">
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-stone-800 mb-1">Physical Cash in Hand</label>
              <div class="relative">
                <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
                <input type="number" id="w-liq-cash" placeholder="0" class="w-full pl-7 pr-3 py-2 text-xs border rounded-xl font-mono">
              </div>
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">Protected Cash Floor Mode</label>
            <select id="w-floor-pref" onchange="document.getElementById('custom-floor-box').classList.toggle('hidden', this.value !== 'USER_DEFINED')" class="w-full px-3 py-2 text-xs border border-stone-300 rounded-xl focus:ring-2 focus:ring-brand-500">
              <option value="CALCULATED">Recommended: System Calculated (80% of weekly essential burn)</option>
              <option value="USER_DEFINED">Custom Floor: I want to set a fixed floor</option>
            </select>
          </div>
          <div id="custom-floor-box" class="hidden">
            <label class="block text-xs font-bold text-stone-800 mb-1">Custom Floor Amount</label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
              <input type="number" id="w-custom-floor" placeholder="e.g. 4000" class="w-full pl-7 pr-3 py-2 text-xs border rounded-xl font-mono">
            </div>
          </div>
        </div>
      `;
    } else if (step === 6) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Define your emergency buffer cushion and desired safety coverage target in weeks.
          </p>
          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">Current Emergency Savings / Vault Balance</label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-stone-400 font-semibold text-xs">₹</span>
              <input type="number" id="w-buf-current" placeholder="0" class="w-full pl-7 pr-3 py-2 text-xs border rounded-xl font-mono">
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-stone-800 mb-1">Desired Safety Runway Target</label>
            <select id="w-buf-weeks" class="w-full px-3 py-2 text-xs border border-stone-300 rounded-xl">
              <option value="2">2 Weeks of Essential Burn (Minimal Starter Buffer)</option>
              <option value="4" selected>4 Weeks of Essential Burn (Recommended Core Resilience)</option>
              <option value="6">6 Weeks of Essential Burn (Advanced Cushion)</option>
              <option value="8">8 Weeks of Essential Burn (Institutional Grade)</option>
            </select>
          </div>
        </div>
      `;
    } else if (step === 7) {
      body.innerHTML = `
        <div class="space-y-4">
          <p class="text-xs text-stone-500">
            Record scheduled commitments (rent, EMI, electricity) so the cash-flow engine detects intraday timing gaps before you get penalized.
          </p>
          <div class="p-4 border border-dashed border-stone-300 rounded-xl space-y-3 bg-stone-50/50">
            <h4 class="text-xs font-bold text-stone-800">+ Add Scheduled Obligation</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <input type="text" id="new-obl-desc" placeholder="Obligation Name (e.g. HDFC EMI, Room Rent)" class="px-3 py-1.5 text-xs border rounded-lg">
              <input type="number" id="new-obl-amt" placeholder="Debit Amount (₹)" class="px-3 py-1.5 text-xs border rounded-lg font-mono">
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input type="date" id="new-obl-date" class="px-2 py-1.5 text-xs border rounded-lg">
              <input type="time" id="new-obl-time" value="09:00" class="px-2 py-1.5 text-xs border rounded-lg">
            </div>
            <button type="button" onclick="window.setupWizard.handleAddObligation()" class="px-3 py-1.5 bg-stone-800 hover:bg-stone-900 text-white font-semibold text-xs rounded-lg shadow-sm">
              + Save Obligation
            </button>
          </div>
        </div>
      `;
    } else if (step === 8) {
      body.innerHTML = `
        <div class="space-y-4">
          <div class="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
            <h4 class="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
              <span>✓</span> Ready to Activate Your Financial Intelligence
            </h4>
            <p class="text-xs text-emerald-800 leading-relaxed">
              All raw inputs have been configured. Clicking the button below will trigger an authoritative recalculation across:
            </p>
            <ul class="text-[11px] text-emerald-700 space-y-1 list-disc list-inside">
              <li>Deterministic Stabilized Income & Surplus Baseline</li>
              <li>Safe-to-Save Policy Safeguard Cap</li>
              <li>Protected Cash Floor & Smart Buffer Gap</li>
              <li>Intraday Timing Gap Discovery & Cash-Flow Timeline</li>
              <li>Dynamic Financial Resilience & Risk Scoring</li>
            </ul>
          </div>
          <div class="p-3 bg-stone-50 border border-stone-200 rounded-xl text-xs text-stone-600 space-y-1">
            <span class="font-bold text-stone-900">Zero Demo Numbers Guarantee:</span>
            <p>Your workspace is 100% isolated. Every score and recommendation will reflect your real submitted parameters.</p>
          </div>
        </div>
      `;
    }
  },

  async handleAddIncomeSource() {
    const name = document.getElementById("new-src-name")?.value;
    const amt = parseFloat(document.getElementById("new-src-amt")?.value) || 0;
    const freq = document.getElementById("new-src-freq")?.value || "weekly";
    const day = document.getElementById("new-src-day")?.value || "Wednesday";

    if (!name || amt <= 0) {
      if (window.showToast) window.showToast("Input Required", "Please enter a valid source name and typical payout amount.", "warning");
      else alert("Please enter a valid source name and typical payout amount.");
      return;
    }

    try {
      await window.sureSavingsApi.addIncomeSource({
        name,
        typicalAmount: amt,
        frequency: freq,
        payoutDay: day
      });
      if (window.showToast) window.showToast("Income Source Added", `${name} (₹${amt}) saved.`, "success");
      document.getElementById("new-src-name").value = "";
      document.getElementById("new-src-amt").value = "";
    } catch (e) {
      if (window.showToast) window.showToast("Failed to Add Source", e.message, "error");
      else alert("Failed to add income source: " + e.message);
    }
  },

  async handleAddExpense() {
    const desc = document.getElementById("new-exp-desc")?.value;
    const amt = parseFloat(document.getElementById("new-exp-amt")?.value) || 0;
    const cat = document.getElementById("new-exp-cat")?.value || "housing";
    const freq = document.getElementById("new-exp-freq")?.value || "monthly";
    const ess = document.getElementById("new-exp-ess")?.checked ?? true;

    if (!desc || amt <= 0) {
      if (window.showToast) window.showToast("Input Required", "Please enter an expense description and amount.", "warning");
      else alert("Please enter an expense description and amount.");
      return;
    }

    try {
      await window.sureSavingsApi.addExpense({
        description: desc,
        amount: amt,
        category: cat,
        frequency: freq,
        isEssential: ess
      });
      if (window.showToast) window.showToast("Expense Saved", `${desc} (₹${amt}) recorded.`, "success");
      document.getElementById("new-exp-desc").value = "";
      document.getElementById("new-exp-amt").value = "";
    } catch (e) {
      if (window.showToast) window.showToast("Failed to Save Expense", e.message, "error");
      else alert("Failed to add expense: " + e.message);
    }
  },

  async handleAddObligation() {
    const desc = document.getElementById("new-obl-desc")?.value;
    const amt = parseFloat(document.getElementById("new-obl-amt")?.value) || 0;
    const date = document.getElementById("new-obl-date")?.value;
    const time = document.getElementById("new-obl-time")?.value || "09:00 AM";

    if (!desc || amt <= 0 || !date) {
      if (window.showToast) window.showToast("Input Required", "Please fill in description, amount, and scheduled due date.", "warning");
      else alert("Please fill in description, amount, and scheduled due date.");
      return;
    }

    try {
      await window.sureSavingsApi.addObligation({
        description: desc,
        amount: amt,
        dateStr: date,
        timeStr: time,
        isEssential: true
      });
      if (window.showToast) window.showToast("Obligation Recorded", `${desc} for ${date} saved.`, "success");
      document.getElementById("new-obl-desc").value = "";
      document.getElementById("new-obl-amt").value = "";
    } catch (e) {
      if (window.showToast) window.showToast("Failed to Record Obligation", e.message, "error");
      else alert("Failed to add obligation: " + e.message);
    }
  },

  async nextStep() {
    // Save state from active step
    if (this.activeStep === 1) {
      const occ = document.getElementById("w-occupation")?.value;
      const incType = document.getElementById("w-income-type")?.value;
      if (occ || incType) {
        try {
          await window.sureSavingsApi.updatePersonalContext({ occupation: occ, incomeType: incType });
        } catch (e) {}
      }
    } else if (this.activeStep === 3) {
      const records = [];
      for (let i = 1; i <= 4; i++) {
        const val = parseFloat(document.getElementById(`wh-${i}`)?.value);
        if (!isNaN(val) && val > 0) {
          records.push({ week: `Week ${i}`, income: val, source: "Primary Earnings" });
        }
      }
      if (records.length > 0) {
        try {
          await window.sureSavingsApi.addIncomeHistory(records);
        } catch (e) {}
      }
    } else if (this.activeStep === 5) {
      const checking = parseFloat(document.getElementById("w-liq-checking")?.value) || 0;
      const cash = parseFloat(document.getElementById("w-liq-cash")?.value) || 0;
      const pref = document.getElementById("w-floor-pref")?.value || "CALCULATED";
      const customFloor = pref === "USER_DEFINED" ? (parseFloat(document.getElementById("w-custom-floor")?.value) || 0) : null;
      try {
        await window.sureSavingsApi.updateLiquidity({
          checkingCash: checking,
          physicalCash: cash,
          floorPreference: pref,
          protectedFloor: customFloor
        });
      } catch (e) {}
    } else if (this.activeStep === 6) {
      const curSavings = parseFloat(document.getElementById("w-buf-current")?.value) || 0;
      const targetWeeks = parseFloat(document.getElementById("w-buf-weeks")?.value) || 4.0;
      try {
        await window.sureSavingsApi.updateBuffer({
          currentEmergencySavings: curSavings,
          targetWeeks: targetWeeks
        });
      } catch (e) {}
    } else if (this.activeStep === 8) {
      // Final activation step!
      try {
        const recalc = await window.sureSavingsApi.recalculateWorkspace();
        if (window.showToast) {
          window.showToast("Setup Completed!", "Your Financial Digital Twin is now fully operational.", "success");
        }
        document.getElementById("setupWizardModal")?.remove();
        if (window.sureSavingsStore) {
          await window.sureSavingsStore.syncFromBackend(true);
        }
        this.renderDashboardBanner();
        if (typeof window.updatePageMetrics === "function") {
          window.updatePageMetrics();
        }
        return;
      } catch (e) {
        if (window.showToast) window.showToast("Activation Error", e.message, "error");
        else alert("Activation error: " + e.message);
      }
    }

    if (this.activeStep < this.totalSteps) {
      this.renderStep(this.activeStep + 1);
    }
  },

  prevStep() {
    if (this.activeStep > 1) {
      this.renderStep(this.activeStep - 1);
    }
  }
};

window.setupWizard = setupWizard;
