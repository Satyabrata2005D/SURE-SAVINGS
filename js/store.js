/**
 * SURE SAVINGS 4.0: Unified Authoritative State Store
 * Multi-Tenant • User-Scoped Data Isolation • Real-Time Broadcast Sync
 * Fast, reactive state management grounded exclusively in the FastAPI backend.
 */

const INITIAL_STORE_STATE = {
  isLoading: true,
  isOnline: true,
  lastSyncTime: null,
  correlationId: null,
  auth: {
    status: "loading", // "loading" | "authenticated" | "unauthenticated" | "session_expired"
    user: null,
    workspaceMode: null // "DEMO ENVIRONMENT" | "PRIVATE WORKSPACE"
  },
  profile: null,
  resilience: null,
  risk: null,
  recommendation: null,
  buffer: null,
  weekly_variance: null,
  cash_flow: null,
  income_analytics: null,
  digitalTwin: null,
  nextBestAction: null,
  dataQuality: null,
  behaviorProfile: null,
  sourceDataVersion: 1,
  financialEvents: [],
  financialState: "STABLE",
  financialWeather: null,
  resiliencePlan: null,
  recoveryPlan: null,
  whatChanged: null,
  weeklyBriefing: null,
  multiHorizonOutlook: null,
  timelineStory: null,
  incomeDiversification: null
};

class SureSavingsStore {
  constructor() {
    this.state = JSON.parse(JSON.stringify(INITIAL_STORE_STATE));
    this.listeners = [];
    this.isOnline = true;
    this._isReady = false;
    this._readyResolve = null;
    this._initPromise = new Promise((resolve) => {
      this._readyResolve = resolve;
    });
    
    // Cross-tab synchronization
    try {
      this.channel = new BroadcastChannel("sure_savings_sync");
      this.channel.onmessage = (event) => {
        if (event.data?.type === "STATE_UPDATED") {
          this.syncFromBackend(false);
        } else if (event.data?.type === "LOGOUT") {
          this.clearUserScope();
          window.location.href = "login.html";
        }
      };
    } catch (e) {
      this.channel = null;
    }

    // Initial background sync
    this.init().finally(() => {
      this._isReady = true;
      if (this._readyResolve) this._readyResolve();
    });
  }

  isPublicRoute() {
    const path = window.location.pathname;
    return path.endsWith("landing.html") || path.endsWith("login.html") || path === "/" || path === "";
  }

  async init() {
    const path = window.location.pathname;
    const isLoginPage = path.endsWith("login.html");
    const isLandingPage = path.endsWith("landing.html");

    let user = await this.checkAuth();

    // Instant demo onboarding support for judges and evaluators (e.g. index.html?demo=1)
    if (!user && !isLoginPage && !isLandingPage) {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("demo") === "1" || urlParams.get("preview") === "1") {
        try {
          await window.sureSavingsApi.loginDemo();
          user = await this.checkAuth();
        } catch (e) {
          console.warn("Auto-demo login failed:", e);
        }
      }
    }

    if (user && !isLoginPage && !isLandingPage) {
      if (user.is_onboarded === false && !user.is_demo_user) {
        console.warn("[SURE SAVINGS] Customer profile details required. Redirecting to onboarding.");
        window.location.href = "login.html?step=onboarding";
        return;
      }
      await this.syncFromBackend();
    } else if (isLandingPage && !user) {
      // Set public explorer state
      this.state.auth.status = "public_explorer";
      this.state.auth.workspaceMode = "PUBLIC EXPLORER";
      this.state.isLoading = false;
      this.notify();
    } else if (!user && !isLoginPage) {
      // Direct unauthenticated visitors to Public Explorer so they can experience the value first
      window.location.href = "landing.html";
    } else {
      this.state.isLoading = false;
      this.notify();
    }
  }

  async checkAuth() {
    if (!window.sureSavingsApi) return null;
    try {
      const res = await window.sureSavingsApi.getCurrentUser();
      if (res && res.user) {
        this.state.auth.status = "authenticated";
        this.state.auth.user = res.user;
        this.state.auth.workspaceMode = res.workspace_mode;
        this.notify();
        return res.user;
      }
    } catch (err) {
      this.state.auth.status = "unauthenticated";
      this.state.auth.user = null;
      this.state.auth.workspaceMode = null;
      this.notify();
    }
    return null;
  }

  setUser(user, workspaceMode = "PRIVATE WORKSPACE") {
    if (user) {
      this.state.auth.status = "authenticated";
      this.state.auth.user = user;
      this.state.auth.workspaceMode = workspaceMode;
      this.notify();
      if (this.channel) {
        try {
          this.channel.postMessage({ type: "STATE_UPDATED" });
        } catch (e) {}
      }
    }
  }

  async syncFromBackend(broadcast = false) {
    if (!window.sureSavingsApi) return;
    try {
      const data = await window.sureSavingsApi.getDashboard();
      if (data && data.profile) {
        this.state.profile = data.profile;
        this.state.resilience = data.resilience;
        this.state.risk = data.risk;
        this.state.recommendation = data.recommendation;
        this.state.buffer = data.buffer;
        this.state.weekly_variance = data.weekly_variance;
        this.state.cash_flow = data.cash_flow;
        this.state.income_analytics = data.income_analytics;
        this.state.correlationId = data.correlation_id || null;
        this.state.lastSyncTime = new Date().toISOString();
        if (data.workspace_mode) {
          this.state.auth.workspaceMode = data.workspace_mode;
        }
        if (data.profile.user_id) {
          this.state.auth.status = "authenticated";
        }

        // Fetch 8.0 Digital Twin, Resilience Plan & Financial Weather asynchronously
        if (window.sureSavingsApi) {
          const isDemo = data.workspace_mode === "DEMO ENVIRONMENT";
          
          if (window.sureSavingsApi.getWorkspaceOverview) {
            window.sureSavingsApi.getWorkspaceOverview().then(ov => {
              if (ov && ov.status === "success") {
                this.state.digitalTwin = ov.digital_twin_summary;
                this.state.nextBestAction = ov.next_best_action;
                this.state.dataQuality = ov.data_quality;
                this.state.behaviorProfile = ov.behavior_profile;
                this.state.sourceDataVersion = ov.source_data_version;
                if (ov.readiness) {
                  this.state.readiness = ov.readiness;
                }
                this.notify();
              }
            }).catch(() => {});
          }

          if (window.sureSavingsApi.getFinancialWeather) {
            window.sureSavingsApi.getFinancialWeather(isDemo).then(w => {
              this.state.financialWeather = w;
              this.notify();
            }).catch(() => {});
          }

          if (window.sureSavingsApi.getWhatChanged) {
            window.sureSavingsApi.getWhatChanged(isDemo).then(c => {
              this.state.whatChanged = c;
              this.notify();
            }).catch(() => {});
          }

          if (window.sureSavingsApi.getResiliencePlan) {
            window.sureSavingsApi.getResiliencePlan(isDemo).then(p => {
              this.state.resiliencePlan = p;
              this.notify();
            }).catch(() => {});
          }

          if (window.sureSavingsApi.getWorkspaceReadiness) {
            window.sureSavingsApi.getWorkspaceReadiness().then(r => {
              if (r) {
                this.state.readiness = r;
                this.notify();
              }
            }).catch(() => {});
          }
        }

        this.state.isLoading = false;
        this.isOnline = true;
        this.notify();

        if (broadcast && this.channel) {
          this.channel.postMessage({ type: "STATE_UPDATED" });
        }
      }
    } catch (err) {
      console.warn("[SURE SAVINGS Store] Backend sync error:", err.message);
      this.isOnline = false;
      this.state.isLoading = false;
      this.notify();
    }
  }

  clearUserScope() {
    this.state = JSON.parse(JSON.stringify(INITIAL_STORE_STATE));
    this.state.isLoading = false;
    this.state.auth.status = "unauthenticated";
    this.notify();
    if (this.channel) {
      this.channel.postMessage({ type: "LOGOUT" });
    }
  }

  async logout() {
    try {
      if (window.sureSavingsApi) {
        await window.sureSavingsApi.logout();
      }
    } catch (e) {
      console.warn("Logout network issue:", e);
    }
    this.clearUserScope();
    window.location.href = "login.html";
  }

  subscribe(callback) {
    this.listeners.push(callback);
    callback(this.state);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  notify() {
    this.listeners.forEach(cb => {
      try {
        cb(this.state);
      } catch (err) {
        console.error("[SURE SAVINGS Store] Listener error:", err);
      }
    });
  }

  getState() {
    return this.state;
  }

  getProfile() {
    return this.state.profile;
  }

  getAuth() {
    return this.state.auth;
  }

  /** Returns a Promise that resolves when store initialization (auth + initial sync) is complete */
  whenReady() {
    return this._initPromise;
  }

  /** Synchronous check if store has finished its initial boot sequence */
  isReady() {
    return this._isReady;
  }

  async approveReserveTransfer(idempotencyKey = null, amount = null) {
    if (!window.sureSavingsApi) return null;
    const key = (typeof idempotencyKey === "string" && idempotencyKey.trim().length > 0) ? idempotencyKey.trim() : null;
    const numAmt = (typeof amount === "number" && !isNaN(amount) && amount > 0) ? amount : null;
    try {
      const res = await window.sureSavingsApi.approveRecommendation(key, numAmt);
      await this.syncFromBackend(true);
      return res;
    } catch (err) {
      console.error("[SURE SAVINGS Store] Approve transfer failed:", err);
      throw err;
    }
  }

  async withdrawBuffer(amount, reason = "EMERGENCY_DRAWDOWN") {
    if (!window.sureSavingsApi) return null;
    try {
      const res = await window.sureSavingsApi.withdrawBuffer(amount, reason);
      await this.syncFromBackend(true);
      return res;
    } catch (err) {
      console.error("[SURE SAVINGS Store] Buffer withdrawal failed:", err);
      throw err;
    }
  }

  async resetToLiveState() {
    if (!window.sureSavingsApi) return null;
    try {
      const res = await window.sureSavingsApi.resetState();
      await this.syncFromBackend(true);
      return res;
    } catch (err) {
      console.error("[SURE SAVINGS Store] Reset state failed:", err);
      throw err;
    }
  }
}

window.sureSavingsStore = new SureSavingsStore();
