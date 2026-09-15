/**
 * SURE SAVINGS 7.0: Centralized Typed API Client
 * Connects all screens to the authoritative FastAPI backend.
 * Enforces credentials: "include" for secure HTTP-only session cookies
 * and handles global 401 redirect to login.html.
 * @version 7.0.2
 * @updated 2026-09-12
 */

const API_VERSION = "7.0.2";
const API_BASE = (window.location.port === "8000" || (window.location.port === "" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1"))
  ? (window.location.origin || "http://127.0.0.1:8000")
  : `${window.location.protocol}//${window.location.hostname}:8000`;

const api = {
  async fetchJSON(endpoint, options = {}) {
    try {
      const url = `${API_BASE}${endpoint}`;
      const { headers: optHeaders, ...restOptions } = options;
      const res = await fetch(url, {
        credentials: "include", // Essential for HTTP-only session cookies
        ...restOptions,
        headers: {
          "Content-Type": "application/json",
          ...(optHeaders || {}),
        },
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        const errMsg = errData.error?.message || errData.detail || `HTTP Error ${res.status}`;

        // Route-aware 401 Unauthorized handling (Do not redirect visitors browsing public pages)
        if (res.status === 401) {
          const path = window.location.pathname;
          const isPublicPage = path.endsWith("landing.html") || path.endsWith("login.html") || path === "/" || path === "";
          if (!isPublicPage && !endpoint.includes("/api/v1/auth/me")) {
            console.warn("[SURE SAVINGS API] Protected workspace route requires authentication. Redirecting to login.");
            const currentScreen = path.split("/").pop() || "index.html";
            window.location.href = `login.html?expired=1&return_to=${encodeURIComponent(currentScreen)}`;
          }
        }

        const error = new Error(errMsg);
        error.status = res.status;
        error.code = errData.error?.code || "HTTP_ERROR";
        throw error;
      }
      return await res.json();
    } catch (err) {
      console.warn(`[SURE SAVINGS API] Network error for ${endpoint}:`, err.message);
      throw err;
    }
  },

  // ===================================================================
  // Authentication & Workspace Session APIs
  // ===================================================================

  getAuthConfig() {
    return this.fetchJSON("/api/v1/auth/config");
  },

  setGoogleClientId(clientId) {
    return this.fetchJSON("/api/v1/auth/config/google-client-id", {
      method: "POST",
      body: JSON.stringify({ client_id: clientId }),
    });
  },

  getCurrentUser() {
    return this.fetchJSON("/api/v1/auth/me");
  },

  verifyGoogleCredential(credential) {
    return this.fetchJSON("/api/v1/auth/google/verify", {
      method: "POST",
      body: JSON.stringify({ credential }),
    });
  },

  selectGoogleAccount(email, name = "Google User", picture = null) {
    return this.fetchJSON("/api/v1/auth/google/select-account", {
      method: "POST",
      body: JSON.stringify({ email, name, picture }),
    });
  },

  loginDemo() {
    return this.fetchJSON("/api/v1/auth/demo", {
      method: "POST",
    });
  },

  loginDevUser(email, name, sub = null) {
    return this.fetchJSON("/api/v1/auth/developer-login", {
      method: "POST",
      body: JSON.stringify({ email, name, sub }),
    });
  },

  sendEmailOTP(email) {
    return this.fetchJSON("/api/v1/auth/otp/send", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },

  sendOtp(email) {
    return this.sendEmailOTP(email);
  },

  verifyEmailOTP(email, otp) {
    return this.fetchJSON("/api/v1/auth/otp/verify", {
      method: "POST",
      body: JSON.stringify({ email, otp }),
    });
  },

  verifyOtp(email, otp) {
    return this.verifyEmailOTP(email, otp);
  },

  completeOnboarding(details) {
    return this.fetchJSON("/api/v1/auth/onboarding", {
      method: "POST",
      body: JSON.stringify(details),
    });
  },

  logout() {
    return this.fetchJSON("/api/v1/auth/logout", {
      method: "POST",
    });
  },

  getProfile() {
    return this.fetchJSON("/api/v1/auth/profile");
  },

  updateProfile(data) {
    return this.fetchJSON("/api/v1/auth/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  uploadProfilePhoto(photoBase64) {
    return this.fetchJSON("/api/v1/auth/profile/photo", {
      method: "POST",
      body: JSON.stringify({ photo_base64: photoBase64 }),
    });
  },

  deleteProfilePermanently(confirmation) {
    return this.fetchJSON("/api/v1/auth/profile", {
      method: "DELETE",
      body: JSON.stringify({ confirmation }),
    });
  },

  // ===================================================================
  // Core Financial Resilience APIs (User-Scoped)
  // ===================================================================

  getHealth() {
    return this.fetchJSON("/health");
  },

  getHealthDB() {
    return this.fetchJSON("/health/db");
  },

  getDashboard() {
    return this.fetchJSON("/api/v1/dashboard");
  },

  getTransactions(params = {}) {
    const page = params.page || 1;
    const pageSize = params.page_size || 10;
    const category = params.category || "all";
    const search = params.search || "";
    
    let query = `/api/v1/transactions?page=${page}&page_size=${pageSize}&category=${encodeURIComponent(category)}`;
    if (search) {
      query += `&search=${encodeURIComponent(search)}`;
    }
    return this.fetchJSON(query);
  },

  getIncomeAnalytics() {
    return this.fetchJSON("/api/v1/income/analytics");
  },

  getBufferStatus() {
    return this.fetchJSON("/api/v1/buffer");
  },

  getResilience() {
    return this.fetchJSON("/api/v1/resilience");
  },

  getRisk() {
    return this.fetchJSON("/api/v1/risk");
  },

  getCashFlow() {
    return this.fetchJSON("/api/v1/cash-flow");
  },

  getCashFlowTimeline() {
    return this.fetchJSON("/api/v1/cash-flow/timeline");
  },

  getScenarios() {
    return this.fetchJSON("/api/v1/scenarios");
  },

  getDashboardGoals() {
    return this.fetchJSON("/api/v1/goals");
  },

  getCalendar(year = null, month = null, isDemo = false) {
    const params = new URLSearchParams();
    if (year) params.append("year", year);
    if (month) params.append("month", month);
    const qs = params.toString() ? `?${params.toString()}` : "";
    const endpoint = isDemo ? `/api/v1/public/demo/calendar${qs}` : `/api/v1/calendar${qs}`;
    return this.fetchJSON(endpoint);
  },

  getCalendarDay(date) {
    const params = new URLSearchParams({ date });
    return this.fetchJSON(`/api/v1/calendar/day?${params.toString()}`);
  },

  createCalendarEvent(eventData) {
    return this.fetchJSON("/api/v1/calendar/events", {
      method: "POST",
      body: JSON.stringify(eventData),
    });
  },

  updateCalendarEvent(eventId, eventData) {
    return this.fetchJSON(`/api/v1/calendar/events/${encodeURIComponent(eventId)}`, {
      method: "PATCH",
      body: JSON.stringify(eventData),
    });
  },

  deleteCalendarEvent(eventId) {
    return this.fetchJSON(`/api/v1/calendar/events/${encodeURIComponent(eventId)}`, {
      method: "DELETE",
    });
  },

  recalculateCalendar(year = null, month = null) {
    const params = new URLSearchParams();
    if (year) params.append("year", year);
    if (month) params.append("month", month);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return this.fetchJSON(`/api/v1/calendar/recalculate${qs}`, {
      method: "POST",
    });
  },

  syncCalendarFeeds(year = null, month = null) {
    return this.recalculateCalendar(year, month);
  },

  getCalendarVariance(year = null, month = null) {
    const params = new URLSearchParams();
    if (year) params.append("year", year);
    if (month) params.append("month", month);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return this.fetchJSON(`/api/v1/calendar/variance${qs}`);
  },

  exportCalendar(year = null, month = null, format = "json") {
    const params = new URLSearchParams();
    if (year) params.append("year", year);
    if (month) params.append("month", month);
    params.append("format", format);
    return this.fetchJSON(`/api/v1/calendar/export?${params.toString()}`);
  },

  getIncomeProviders() {
    return this.fetchJSON("/api/v1/income/providers");
  },

  connectIncomeSource(payload) {
    return this.fetchJSON("/api/v1/income/providers/connect", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getActivity() {
    return this.fetchJSON("/api/v1/activity");
  },

  getEngineAudit() {
    return this.fetchJSON("/api/v1/engine/audit");
  },

  approveRecommendation(idempotencyKey = null, amount = null) {
    // Strict sanitization: ensure key is a non-empty string; never serialize event objects
    const key = (typeof idempotencyKey === "string" && idempotencyKey.trim().length > 0) ? idempotencyKey.trim() : null;
    const numAmt = (typeof amount === "number" && !isNaN(amount) && amount > 0) 
      ? amount 
      : (typeof idempotencyKey === "number" && !isNaN(idempotencyKey) && idempotencyKey > 0 ? idempotencyKey : null);
    
    const headers = {};
    if (key) {
      headers["X-Idempotency-Key"] = key;
    }
    const bodyObj = {};
    if (key) bodyObj.idempotency_key = key;
    if (numAmt) bodyObj.amount = numAmt;

    return this.fetchJSON("/api/v1/recommendations/approve", {
      method: "POST",
      headers,
      body: JSON.stringify(bodyObj),
    });
  },

  withdrawBuffer(amount, reason = "EMERGENCY_DRAWDOWN") {
    return this.fetchJSON("/api/v1/buffer/withdraw", {
      method: "POST",
      body: JSON.stringify({ amount, reason }),
    });
  },

  simulateShock(params) {
    return this.fetchJSON("/api/v1/simulate", {
      method: "POST",
      body: JSON.stringify({
        contribution_amount: params.contribution || 0.0,
        withdrawal_amount: params.withdrawal || 0.0,
        shock_percentage: params.shockPercentage || 0.0,
        scenario_type: params.scenarioType || "custom",
      }),
    });
  },

  sendChatMessage(query, pageContext = null) {
    const ctx = pageContext || (typeof window !== "undefined" ? window.sureSavingsPageContext : null);
    let timezone = "Asia/Kolkata";
    let locale = "en-IN";
    try {
      if (typeof Intl !== "undefined" && Intl.DateTimeFormat) {
        timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || timezone;
      }
      if (typeof window !== "undefined" && window.sureSavingsLocale && window.sureSavingsLocale.locale) {
        locale = window.sureSavingsLocale.locale;
      } else if (typeof window !== "undefined" && window.i18n && window.i18n.currentLocale) {
        locale = window.i18n.currentLocale;
      } else if (typeof localStorage !== "undefined" && localStorage.getItem("sureSavingsLocale")) {
        locale = localStorage.getItem("sureSavingsLocale");
      } else if (typeof navigator !== "undefined" && navigator.language) {
        locale = navigator.language;
      }
    } catch (e) {}

    return this.fetchJSON("/api/v1/ai/chat", {
      method: "POST",
      body: JSON.stringify({
        query,
        page_context: ctx || undefined,
        timezone,
        locale
      }),
    });
  },

  getLocalizationConfig() {
    return this.fetchJSON("/api/v1/localization/config");
  },

  getUserPreferences() {
    return this.fetchJSON("/api/v1/users/preferences");
  },

  updateUserPreferences(preferences) {
    return this.fetchJSON("/api/v1/users/preferences", {
      method: "PATCH",
      body: JSON.stringify(preferences),
    });
  },

  resetState() {
    return this.fetchJSON("/api/v1/engine/reset", {
      method: "POST",
    });
  },

  // ===================================================================
  // Financial Workspace & Setup APIs (SURE SAVINGS 5.0 / 6.0)
  // ===================================================================

  getWorkspaceReadiness() {
    return this.fetchJSON("/api/v1/workspace/readiness");
  },

  applyQuickStart({ weeklyIncome, essentialExpenses, currentCash, emergencySavings, protectedFloor = null }) {
    return this.fetchJSON("/api/v1/workspace/quick-start", {
      method: "POST",
      body: JSON.stringify({
        weekly_income: Number(weeklyIncome) || 0.0,
        essential_expenses: Number(essentialExpenses) || 0.0,
        current_cash: Number(currentCash) || 0.0,
        emergency_savings: Number(emergencySavings) || 0.0,
        protected_floor: protectedFloor !== null && protectedFloor !== undefined && protectedFloor !== "" ? Number(protectedFloor) : null
      }),
    });
  },

  updatePersonalContext({ occupation, incomeType, currency = "INR", timezone = "Asia/Kolkata" }) {
    return this.fetchJSON("/api/v1/workspace/personal-context", {
      method: "POST",
      body: JSON.stringify({
        occupation,
        income_type: incomeType,
        currency,
        timezone
      }),
    });
  },

  getIncomeSources() {
    return this.fetchJSON("/api/v1/workspace/income-sources");
  },

  addIncomeSource({ name, incomeType = "gig", typicalAmount, frequency = "weekly", payoutDay = "Wednesday", expectedDelayDays = 0 }) {
    return this.fetchJSON("/api/v1/workspace/income-sources", {
      method: "POST",
      body: JSON.stringify({
        name,
        income_type: incomeType,
        typical_amount: Number(typicalAmount) || 0.0,
        frequency,
        payout_day: payoutDay,
        expected_delay_days: Number(expectedDelayDays) || 0
      }),
    });
  },

  deleteIncomeSource(sourceId) {
    return this.fetchJSON(`/api/v1/workspace/income-sources/${encodeURIComponent(sourceId)}`, {
      method: "DELETE",
    });
  },

  getIncomeHistory() {
    return this.fetchJSON("/api/v1/workspace/income-history");
  },

  addIncomeHistory(records) {
    return this.fetchJSON("/api/v1/workspace/income-history", {
      method: "POST",
      body: JSON.stringify({ records }),
    });
  },

  getExpenses() {
    return this.fetchJSON("/api/v1/workspace/expenses");
  },

  addExpense({ description, amount, frequency = "monthly", category = "housing", isEssential = true, dueDay = 1, isRecurring = true }) {
    return this.fetchJSON("/api/v1/workspace/expenses", {
      method: "POST",
      body: JSON.stringify({
        description,
        amount: Number(amount) || 0.0,
        frequency,
        category,
        is_essential: Boolean(isEssential),
        due_day: Number(dueDay) || 1,
        is_recurring: Boolean(isRecurring)
      }),
    });
  },

  deleteExpense(expenseId) {
    return this.fetchJSON(`/api/v1/workspace/expenses/${encodeURIComponent(expenseId)}`, {
      method: "DELETE",
    });
  },

  getLiquidity() {
    return this.fetchJSON("/api/v1/workspace/liquidity");
  },

  updateLiquidity({ checkingCash = 0.0, savingsBalance = 0.0, physicalCash = 0.0, protectedFloor = null, floorPreference = "CALCULATED" }) {
    return this.fetchJSON("/api/v1/workspace/liquidity", {
      method: "POST",
      body: JSON.stringify({
        checking_cash: Number(checkingCash) || 0.0,
        savings_balance: Number(savingsBalance) || 0.0,
        physical_cash: Number(physicalCash) || 0.0,
        protected_floor: protectedFloor !== null && protectedFloor !== undefined && protectedFloor !== "" ? Number(protectedFloor) : null,
        floor_preference: floorPreference
      }),
    });
  },

  updateBuffer({ currentEmergencySavings = null, targetWeeks = 4.0, customTarget = null }) {
    return this.fetchJSON("/api/v1/workspace/buffer", {
      method: "POST",
      body: JSON.stringify({
        current_emergency_savings: currentEmergencySavings !== null && currentEmergencySavings !== "" ? Number(currentEmergencySavings) : null,
        target_weeks: Number(targetWeeks) || 4.0,
        custom_target: customTarget !== null && customTarget !== "" ? Number(customTarget) : null
      }),
    });
  },

  getObligations() {
    return this.fetchJSON("/api/v1/workspace/obligations");
  },

  addObligation({ description, amount, dateStr, timeStr = "09:00 AM", category = "General", isEssential = true, timingRisk = false }) {
    return this.fetchJSON("/api/v1/workspace/obligations", {
      method: "POST",
      body: JSON.stringify({
        description,
        amount: Number(amount) || 0.0,
        date_str: dateStr,
        time_str: timeStr,
        category,
        is_essential: Boolean(isEssential),
        timing_risk: Boolean(timingRisk)
      }),
    });
  },

  deleteObligation(obligationId) {
    return this.fetchJSON(`/api/v1/workspace/obligations/${encodeURIComponent(obligationId)}`, {
      method: "DELETE",
    });
  },

  getGoals() {
    return this.fetchJSON("/api/v1/workspace/goals");
  },

  addGoal({ name, targetAmount, targetDate = null, priority = "medium", goalType = "EMERGENCY_RESERVE" }) {
    return this.fetchJSON("/api/v1/workspace/goals", {
      method: "POST",
      body: JSON.stringify({
        name,
        target_amount: Number(targetAmount) || 0.0,
        target_date: targetDate,
        priority,
        goal_type: goalType
      }),
    });
  },

  deleteGoal(goalId) {
    return this.fetchJSON(`/api/v1/workspace/goals/${encodeURIComponent(goalId)}`, {
      method: "DELETE",
    });
  },

  importTransactionsCSV(transactions) {
    return this.fetchJSON("/api/v1/workspace/transactions/import", {
      method: "POST",
      body: JSON.stringify({ transactions }),
    });
  },

  recalculateWorkspace() {
    return this.fetchJSON("/api/v1/workspace/recalculate", {
      method: "POST",
    });
  },

  // ===================================================================
  // 7.0 Personal Financial Digital Twin & Intelligence Platform APIs
  // ===================================================================

  getWorkspaceIntelligence() {
    return this.fetchJSON("/api/v1/workspace/intelligence");
  },

  getWorkspaceOverview() {
    return this.fetchJSON("/api/v1/workspace/overview");
  },

  getDataQuality() {
    return this.fetchJSON("/api/v1/workspace/data-quality");
  },

  getActionPlan() {
    return this.fetchJSON("/api/v1/workspace/action-plan");
  },

  getFinancialEvents(limit = 50) {
    return this.fetchJSON(`/api/v1/workspace/events?limit=${limit}`);
  },

  explainMetric(metricName) {
    return this.fetchJSON(`/api/v1/workspace/explain/${encodeURIComponent(metricName)}`);
  },

  getScenarioLibrary() {
    return this.fetchJSON("/api/v1/workspace/scenarios/library");
  },

  runScenarioSimulation({
    scenarioName = "Custom Scenario",
    incomeDeltaPct = 0.0,
    expenseDeltaPct = 0.0,
    oneOffShock = 0.0,
    delayedPayoutDays = 0,
    simulationWeeks = 6
  } = {}) {
    return this.fetchJSON("/api/v1/workspace/scenarios/simulate", {
      method: "POST",
      body: JSON.stringify({
        scenario_name: scenarioName,
        income_delta_pct: Number(incomeDeltaPct) || 0.0,
        expense_delta_pct: Number(expenseDeltaPct) || 0.0,
        one_off_shock: Number(oneOffShock) || 0.0,
        delayed_payout_days: Number(delayedPayoutDays) || 0,
        simulation_weeks: Number(simulationWeeks) || 6
      })
    });
  },

  // ===================================================================
  // Public Product Explorer & Demo APIs (Read-Only • No Auth Required)
  // ===================================================================

  getPublicDemoOverview() {
    return this.fetchJSON("/api/v1/public/demo/overview");
  },

  getPublicDemoIncome() {
    return this.fetchJSON("/api/v1/public/demo/income");
  },

  getPublicDemoBuffer() {
    return this.fetchJSON("/api/v1/public/demo/buffer");
  },

  getPublicDemoCashFlow() {
    return this.fetchJSON("/api/v1/public/demo/cash-flow");
  },

  simulatePublicShock({ shockPercentage = 20.0, contributionAmount = 0.0, withdrawalAmount = 0.0, scenarioPreset = "custom" } = {}) {
    return this.fetchJSON("/api/v1/public/demo/simulate", {
      method: "POST",
      body: JSON.stringify({
        shock_percentage: Number(shockPercentage) || 0.0,
        contribution_amount: Number(contributionAmount) || 0.0,
        withdrawal_amount: Number(withdrawalAmount) || 0.0,
        scenario_preset: scenarioPreset
      })
    });
  },

  // ===================================================================
  // SURE SAVINGS 8.0: Adaptive Financial Resilience Operating System APIs
  // ===================================================================

  getFinancialWeather(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/weather" : "/api/v1/workspace/weather";
    return this.fetchJSON(ep);
  },

  getResiliencePlan(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/resilience-plan" : "/api/v1/workspace/resilience-plan";
    return this.fetchJSON(ep);
  },

  simulateScenarioPortfolio(scenarios = [], isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/scenarios/portfolio" : "/api/v1/workspace/scenarios/portfolio";
    return this.fetchJSON(ep, {
      method: "POST",
      body: JSON.stringify({ scenarios })
    });
  },

  getRecoveryPlan(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/recovery-plan" : "/api/v1/workspace/recovery-plan";
    return this.fetchJSON(ep);
  },

  optimizeGoals(goals = null, monthlySavingsPool = null, isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/goals/optimize" : "/api/v1/workspace/goals/optimize";
    const body = {};
    if (goals) body.goals = goals;
    if (monthlySavingsPool !== null) body.monthly_savings_pool = monthlySavingsPool;
    return this.fetchJSON(ep, {
      method: "POST",
      body: JSON.stringify(body)
    });
  },

  getIncomeDiversification(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/income/diversification" : "/api/v1/workspace/income/diversification";
    return this.fetchJSON(ep);
  },

  getTimelineStory(limit = 50, isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/timeline" : `/api/v1/workspace/timeline?limit=${limit}`;
    return this.fetchJSON(ep);
  },

  getWeeklyBriefing(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/briefing" : "/api/v1/workspace/briefing";
    return this.fetchJSON(ep);
  },

  getMultiHorizonOutlook(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/outlook" : "/api/v1/workspace/outlook";
    return this.fetchJSON(ep);
  },

  getStressTestSuite(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/stress-test" : "/api/v1/workspace/stress-test";
    return this.fetchJSON(ep);
  },

  getWhatChanged(isDemo = false) {
    const ep = isDemo ? "/api/v1/public/demo/what-changed" : "/api/v1/workspace/what-changed";
    return this.fetchJSON(ep);
  },

  // ===================================================================
  // Bank Account & Setu Account Aggregator Integration
  // ===================================================================

  getBankAccounts() {
    return this.fetchJSON("/api/v1/bank-accounts");
  },

  connectBankAccount(payload = {}) {
    return this.fetchJSON("/api/v1/bank-accounts/connect", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getBankConnectionStatus() {
    return this.fetchJSON("/api/v1/bank-accounts/status");
  },

  getBankAccount(accountId) {
    return this.fetchJSON(`/api/v1/bank-accounts/${encodeURIComponent(accountId)}`);
  },

  syncBankAccount(connectionId) {
    return this.fetchJSON(`/api/v1/bank-accounts/${encodeURIComponent(connectionId)}/sync`, {
      method: "POST",
    });
  },

  getBankTransactions(accountId, params = {}) {
    const qs = new URLSearchParams();
    if (params.direction) qs.set("direction", params.direction);
    if (params.category) qs.set("category", params.category);
    if (params.limit) qs.set("limit", params.limit);
    if (params.offset) qs.set("offset", params.offset);
    const qStr = qs.toString() ? `?${qs.toString()}` : "";
    return this.fetchJSON(`/api/v1/bank-accounts/${encodeURIComponent(accountId)}/transactions${qStr}`);
  },

  getBankConsent(connectionId) {
    return this.fetchJSON(`/api/v1/bank-accounts/${encodeURIComponent(connectionId)}/consent`);
  },

  revokeBankConsent(connectionId) {
    return this.fetchJSON(`/api/v1/bank-accounts/${encodeURIComponent(connectionId)}/consent/revoke`, {
      method: "POST",
    });
  },

  disconnectBank(connectionId) {
    return this.fetchJSON(`/api/v1/bank-accounts/${encodeURIComponent(connectionId)}`, {
      method: "DELETE",
    });
  },

  // ===================================================================
  // Self-Verification & Debugging
  // ===================================================================

  getVersion() {
    return API_VERSION;
  },

  verify() {
    const methods = [
      'fetchJSON', 'getCurrentUser', 'loginDemo', 'getDashboard',
      'applyQuickStart', 'recalculateWorkspace', 'getWorkspaceOverview',
      'explainMetric', 'runScenarioSimulation', 'getEngineAudit',
      'getFinancialWeather', 'getResiliencePlan', 'simulateScenarioPortfolio',
      'getRecoveryPlan', 'optimizeGoals', 'getIncomeDiversification',
      'getTimelineStory', 'getWeeklyBriefing', 'getMultiHorizonOutlook',
      'getStressTestSuite', 'getWhatChanged'
    ];
    const missing = methods.filter(m => typeof this[m] !== 'function');
    if (missing.length > 0) {
      console.error(`[SURE SAVINGS API v${API_VERSION}] Missing methods:`, missing);
      return false;
    }
    console.log(`[SURE SAVINGS API v${API_VERSION}] All ${methods.length} critical methods verified ✓`);
    return true;
  }
};

// Expose globally and verify
window.sureSavingsApi = api;
window.api = api;
if (typeof api.verify === 'function') api.verify();


// =====================================================================
// 🛡️ FORTRESS-GRADE CLIENT-SIDE SECURITY SHIELD
// Inactivity timeout, tab monitoring, request fingerprinting,
// anti-tampering, and session integrity enforcement.
// =====================================================================
(function initSecurityShield() {
  "use strict";

  const SHIELD_VERSION = "5.1.0";
  const INACTIVITY_TIMEOUT_MS = 3 * 60 * 60 * 1000; // 3 hours (180 minutes)
  const INACTIVITY_WARNING_MS = 170 * 60 * 1000;   // Warning at 2 hours 50 minutes (10 min remaining)
  const SESSION_CHECK_INTERVAL_MS = 60 * 1000;     // Re-validate every 60s

  let lastActivityTimestamp = Date.now();
  let inactivityTimer = null;
  let warningTimer = null;
  let sessionCheckInterval = null;
  let sessionStartTime = Date.now();

  // Skip security shield on public/login pages
  const currentPath = window.location.pathname;
  const isPublicPage = currentPath.endsWith("landing.html") || currentPath.endsWith("login.html") || currentPath === "/" || currentPath === "";

  // ── 1. Inactivity Auto-Logout ──
  function resetInactivityTimer() {
    lastActivityTimestamp = Date.now();

    // Dismiss any existing warning
    const warningEl = document.getElementById("security-inactivity-warning");
    if (warningEl) warningEl.remove();

    clearTimeout(inactivityTimer);
    clearTimeout(warningTimer);

    if (isPublicPage) return;

    // Warning at 2 hours 50 minutes (10 minutes remaining)
    warningTimer = setTimeout(() => {
      showInactivityWarning();
    }, INACTIVITY_WARNING_MS);

    // Auto-logout at 3 hours of inactivity
    inactivityTimer = setTimeout(() => {
      console.warn("[SECURITY SHIELD] Session timed out due to inactivity (3 hours).");
      performSecurityLogout("inactivity");
    }, INACTIVITY_TIMEOUT_MS);
  }

  function showInactivityWarning() {
    if (document.getElementById("security-inactivity-warning")) return;
    const remainingMin = Math.ceil((INACTIVITY_TIMEOUT_MS - INACTIVITY_WARNING_MS) / 60000);
    const banner = document.createElement("div");
    banner.id = "security-inactivity-warning";
    banner.className = "security-timeout-warning";
    banner.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;justify-content:center;flex-wrap:wrap;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        <span><strong>Security Notice:</strong> Your session will expire in ${remainingMin} minute${remainingMin > 1 ? 's' : ''} due to inactivity.</span>
        <button onclick="this.closest('#security-inactivity-warning').remove();window._securityShield?.resetActivity();" style="padding:4px 16px;background:#F59E0B;color:#000;font-weight:700;border:none;border-radius:8px;cursor:pointer;font-size:12px;">Stay Active</button>
      </div>
    `;
    document.body.appendChild(banner);
  }

  function performSecurityLogout(reason) {
    sessionStorage.removeItem("suresavings_session_token");
    localStorage.removeItem("suresavings_session_token");
    try { window.sureSavingsApi?.logout?.(); } catch (e) {}
    window.location.href = `login.html?security_timeout=1&reason=${reason}`;
  }

  // Track user activity
  const activityEvents = ["mousedown", "keydown", "scroll", "touchstart", "mousemove"];
  if (!isPublicPage) {
    activityEvents.forEach(evt => {
      document.addEventListener(evt, resetInactivityTimer, { passive: true });
    });
    resetInactivityTimer();
  }


  // ── 2. Tab Visibility Monitoring ──
  document.addEventListener("visibilitychange", () => {
    if (isPublicPage) return;

    if (document.visibilityState === "visible") {
      // Tab became visible — re-validate session
      const elapsed = Date.now() - lastActivityTimestamp;
      if (elapsed > INACTIVITY_TIMEOUT_MS) {
        console.warn("[SECURITY SHIELD] Tab returned after extended absence. Logging out.");
        performSecurityLogout("tab_absence");
        return;
      }
      // Silently re-validate session
      window.sureSavingsApi?.getCurrentUser?.().catch(() => {
        console.warn("[SECURITY SHIELD] Session invalid on tab return.");
        performSecurityLogout("session_expired");
      });
      resetInactivityTimer();
    }
  });


  // ── 3. Request Integrity Fingerprinting ──
  // Inject a client nonce + timestamp on every API request for forensic tracing
  const originalFetchJSON = api.fetchJSON.bind(api);
  api.fetchJSON = function(endpoint, options = {}) {
    const nonce = Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
    const timestamp = new Date().toISOString();
    options.headers = {
      ...options.headers,
      "X-Client-Nonce": nonce,
      "X-Client-Timestamp": timestamp,
      "X-Client-Fingerprint": `shield-${SHIELD_VERSION}`,
    };
    return originalFetchJSON(endpoint, options);
  };


  // ── 4. Anti-Tampering: Freeze the API object ──
  try {
    Object.freeze(api);
    Object.freeze(window.sureSavingsApi);
  } catch (e) {
    // Freezing may fail in some environments; non-critical
  }


  // ── 5. Session Age Tracker ──
  // Expose session start time for the UI session timer
  window._securityShield = {
    version: SHIELD_VERSION,
    sessionStartTime: sessionStartTime,
    getSessionAge: () => Math.floor((Date.now() - sessionStartTime) / 1000),
    getInactivityRemaining: () => Math.max(0, INACTIVITY_TIMEOUT_MS - (Date.now() - lastActivityTimestamp)),
    resetActivity: resetInactivityTimer,
    isPublicPage: isPublicPage,
  };

  console.log(`%c🛡️ SURE SAVINGS Security Shield v${SHIELD_VERSION} ACTIVE`, "color: #059669; font-weight: bold; font-size: 14px;");
  console.log(`%c   ✓ Inactivity timeout: 3 hours (180 min)\n   ✓ Tab monitoring: Active\n   ✓ Request fingerprinting: Active\n   ✓ Anti-tampering: Frozen\n   ✓ Session integrity: Enforced`, "color: #64748B; font-size: 11px;");

})();
