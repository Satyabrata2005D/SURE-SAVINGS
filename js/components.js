/**
 * SURE SAVINGS 2.0: Reusable UI Component Builders
 * Information-dense, accessible, premium fintech presentation layer.
 */

const UI = {
  // 1. Metric Card Component
  renderMetricCard({ label, value, subtext = "", badge = "", badgeClass = "bg-emerald-50 text-emerald-700", icon = "" }) {
    return `
      <div class="p-5 rounded-2xl bg-white border border-stone-200/80 shadow-sm flex flex-col justify-between transition-all hover:shadow-md">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold text-stone-500 uppercase tracking-wider">${label}</span>
          ${badge ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono ${badgeClass}">${badge}</span>` : ""}
          ${icon && !badge ? `<span class="text-stone-400 text-sm">${icon}</span>` : ""}
        </div>
        <div class="my-3">
          <div class="text-2xl font-extrabold text-stone-900 tracking-tight font-mono">${value}</div>
          ${subtext ? `<p class="text-xs text-stone-500 mt-0.5">${subtext}</p>` : ""}
        </div>
      </div>
    `;
  },

  // 2. Resilience Gauge Component
  renderResilienceGauge({ score = 74, tier = "Solid • Volatility Resilient", floor = 3500, dimensions = {} }) {
    return `
      <div class="p-6 rounded-2xl bg-white border border-stone-200/80 shadow-sm relative overflow-hidden">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-xs font-bold text-stone-700 uppercase tracking-wider">Financial Resilience Index</span>
          </div>
          <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-stone-100 text-stone-600 font-mono font-bold">Deterministic v4.0</span>
        </div>
        <div class="flex flex-col sm:flex-row items-center gap-6">
          <div class="relative w-36 h-36 flex items-center justify-center shrink-0">
            <svg class="w-full h-full -rotate-90" viewBox="0 0 120 120">
              <circle class="text-stone-100 fill-none" cx="60" cy="60" r="48" stroke="currentColor" stroke-width="9"></circle>
              <circle class="text-brand-500 fill-none transition-all duration-700" cx="60" cy="60" r="48" stroke="currentColor" stroke-width="9"
                stroke-dasharray="301.6" stroke-dashoffset="${301.6 - (301.6 * score / 100)}" stroke-linecap="round"></circle>
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span class="text-3xl font-extrabold text-stone-900 font-mono leading-none">${score}</span>
              <span class="text-[10px] text-stone-400 font-semibold tracking-wider uppercase mt-1">/ 100</span>
            </div>
          </div>
          <div class="space-y-2 text-center sm:text-left">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-bold">
              ✓ ${tier}
            </span>
            <p class="text-xs text-stone-600 leading-relaxed max-w-sm">
              Current liquid buffers absorb unforeseen platform drought periods while keeping your ₹${floor.toLocaleString()} checking floor 100% intact.
            </p>
          </div>
        </div>
      </div>
    `;
  },

  // 3. Intelligent Recommendation Card with dynamic breakdown
  renderRecommendationCard({ 
    recommendedAmount = 900, 
    surplus = 1300, 
    freePocket = 400, 
    floor = 3500, 
    cycleInflow = 8400,
    baselineIncome = 7100,
    policyCapPct = 70,
    cycleLabel = "Week 36 Recommendation",
    onApprove = "openApproveTransferModal()" 
  } = {}) {
    return `
      <div class="p-6 rounded-2xl bg-gradient-to-br from-white via-amber-50/20 to-white border border-amber-200/80 shadow-sm relative overflow-hidden">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-stone-100">
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-600 text-[11px] font-bold uppercase tracking-wider">
                Surplus Safeguard Action
              </span>
              <span class="text-xs text-stone-400 font-mono">${cycleLabel}</span>
            </div>
            <h3 class="text-lg font-bold text-stone-900 mt-1">Save ₹${recommendedAmount.toLocaleString()} to Smart Buffer</h3>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="${onApprove}" class="px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold shadow-md brand-glow transition-all flex items-center gap-2">
              <span>Approve Reserve Transfer</span>
              <span>→</span>
            </button>
          </div>
        </div>

        <!-- Transparent mathematical breakdown -->
        <div class="mt-4 pt-1">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-stone-700 flex items-center gap-1.5">
              <span>🧮</span> Transparent Decision Trace (Why ₹${recommendedAmount.toLocaleString()}?):
            </span>
            <span class="text-[11px] text-stone-500 font-mono">${policyCapPct}% Policy Safeguard</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
            <div class="p-3 rounded-xl bg-stone-50 border border-stone-200/60">
              <span class="text-[10px] text-stone-500 uppercase font-semibold">1. Cycle Inflow</span>
              <div class="text-sm font-bold text-stone-900 font-mono mt-0.5">₹${cycleInflow.toLocaleString()}</div>
              <span class="text-[10px] text-stone-400">vs ₹${baselineIncome.toLocaleString()} baseline</span>
            </div>
            <div class="p-3 rounded-xl bg-stone-50 border border-stone-200/60">
              <span class="text-[10px] text-stone-500 uppercase font-semibold">2. Liquid Surplus</span>
              <div class="text-sm font-bold text-stone-900 font-mono mt-0.5">+₹${surplus.toLocaleString()}</div>
              <span class="text-[10px] text-stone-400">Above stabilized level</span>
            </div>
            <div class="p-3 rounded-xl bg-brand-50/50 border border-brand-200/80">
              <span class="text-[10px] text-brand-700 uppercase font-semibold">3. ${policyCapPct}% Safe-to-Save</span>
              <div class="text-sm font-bold text-brand-600 font-mono mt-0.5">₹${recommendedAmount.toLocaleString()}</div>
              <span class="text-[10px] text-brand-600/80">Rounded for execution</span>
            </div>
            <div class="p-3 rounded-xl bg-emerald-50/50 border border-emerald-200/80">
              <span class="text-[10px] text-emerald-800 uppercase font-semibold">4. Free Pocket Cash</span>
              <div class="text-sm font-bold text-emerald-700 font-mono mt-0.5">₹${freePocket.toLocaleString()}</div>
              <span class="text-[10px] text-emerald-700/80">Retained in checking</span>
            </div>
          </div>
          <div class="mt-3 flex items-center gap-2 text-[11px] text-stone-500">
            <span class="text-emerald-600 font-bold">✓ Non-negotiable Guarantee:</span>
            <span>Checking account floor of ₹${floor.toLocaleString()} remains 100% untouched.</span>
          </div>
        </div>
      </div>
    `;
  },

  // 4. Intraday Cash-Flow Timing Timeline Component
  renderCashFlowTimeline(data) {
    if (!data || !data.timeline) return "";
    if (data.timeline.length === 0) {
      return `
        <div class="p-6 rounded-2xl bg-white border border-stone-200/80 shadow-sm text-center py-8">
          <div class="w-12 h-12 rounded-full bg-stone-100 text-stone-500 flex items-center justify-center mx-auto mb-3 text-lg">📅</div>
          <h3 class="text-sm font-bold text-stone-900">No Scheduled Commitments Recorded</h3>
          <p class="text-xs text-stone-500 max-w-sm mx-auto mt-1">Add your upcoming rent, EMI, or utilities to let SURE SAVINGS detect intraday cash-flow timing gaps before they happen.</p>
          <button onclick="window.setupWizard?.openSetupWizardModal(8) || window.setupWizard?.openQuickStartModal()" class="mt-4 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-xl text-xs font-bold shadow-sm transition-all">
            + Add Obligation
          </button>
        </div>
      `;
    }
    return `
      <div class="p-6 rounded-2xl bg-white border border-stone-200/80 shadow-sm space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-stone-100">
          <div>
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <h3 class="text-sm font-bold text-stone-900">Intraday Timing Gap Intelligence</h3>
            </div>
            <p class="text-xs text-stone-500 mt-0.5">${data.date} • Liquidity stress model</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 rounded-full text-[11px] font-bold ${data.is_absorbable_by_buffer ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'}">
              ${data.protection_status}
            </span>
          </div>
        </div>

        <!-- Hourly Timeline Sequence -->
        <div class="relative pl-6 space-y-6 before:content-[''] before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-stone-200">
          ${data.timeline.map(node => `
            <div class="relative group">
              <div class="absolute -left-[23px] top-1.5 w-3 h-3 rounded-full bg-white border-2 border-brand-500 group-hover:scale-125 transition-transform"></div>
              <div class="p-3.5 rounded-xl bg-stone-50/80 hover:bg-stone-50 border border-stone-200/60 transition-colors">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-stone-900 font-mono">${node.time}</span>
                    <span class="text-xs font-semibold text-stone-700">${node.label}</span>
                  </div>
                  <span class="text-[10px] px-2 py-0.5 rounded-full font-bold font-mono ${node.badge_class}">${node.status}</span>
                </div>
                <p class="text-xs text-stone-500 leading-relaxed">${node.description}</p>
                <div class="mt-2 pt-2 border-t border-stone-200/40 flex items-center justify-between text-[11px] font-mono text-stone-600">
                  <span>Checking Balance: <strong>₹${node.projected_checking.toLocaleString()}</strong></span>
                  <span>Impact: <strong>${node.amount >= 0 ? '+' : ''}₹${node.amount.toLocaleString()}</strong></span>
                </div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  },

  // 5. Paginated Transaction Table Component
  renderTransactionTable({ transactions = [], pagination = {}, onPage = "changeTxPage", onCategory = "filterTxCategory" }) {
    if (!transactions.length) {
      return this.renderEmptyState("No transactions recorded", "No ledger activity matches your filter criteria.");
    }

    return `
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-stone-200/80 bg-stone-50/50 text-[11px] font-bold text-stone-500 uppercase tracking-wider">
              <th class="py-3 px-4">Date</th>
              <th class="py-3 px-4">Description / Platform</th>
              <th class="py-3 px-4">Category</th>
              <th class="py-3 px-4">Direction</th>
              <th class="py-3 px-4 text-right">Amount</th>
              <th class="py-3 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-stone-100 text-xs">
            ${transactions.map(tx => {
              const isCredit = tx.direction === "credit";
              return `
                <tr class="hover:bg-stone-50/60 transition-colors">
                  <td class="py-3 px-4 font-mono text-stone-500">${tx.date}</td>
                  <td class="py-3 px-4">
                    <div class="font-semibold text-stone-900">${tx.description}</div>
                    <div class="text-[10px] text-stone-400 font-mono">${tx.platform}</div>
                  </td>
                  <td class="py-3 px-4">
                    <span class="px-2 py-0.5 rounded text-[10px] font-medium bg-stone-100 text-stone-600">${tx.category}</span>
                  </td>
                  <td class="py-3 px-4">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isCredit ? 'bg-emerald-50 text-emerald-700' : 'bg-stone-100 text-stone-700'}">
                      ${isCredit ? 'Inflow' : 'Outflow'}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-right font-mono font-bold ${isCredit ? 'text-emerald-600' : 'text-stone-900'}">${tx.amount}</td>
                  <td class="py-3 px-4 text-right">
                    <span class="text-[10px] text-stone-400 font-medium">${tx.status}</span>
                  </td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>

      <!-- Pagination footer -->
      ${pagination.total_pages > 1 ? `
        <div class="flex items-center justify-between px-4 py-3 border-t border-stone-200/80 bg-white text-xs">
          <span class="text-stone-500">Page ${pagination.page} of ${pagination.total_pages} (${pagination.total_count} transactions)</span>
          <div class="flex items-center gap-2">
            <button onclick="${onPage}(${pagination.page - 1})" ${!pagination.has_prev ? 'disabled' : ''} class="px-3 py-1 rounded-lg border border-stone-200 disabled:opacity-40 hover:bg-stone-50 font-semibold text-stone-700">← Prev</button>
            <button onclick="${onPage}(${pagination.page + 1})" ${!pagination.has_next ? 'disabled' : ''} class="px-3 py-1 rounded-lg border border-stone-200 disabled:opacity-40 hover:bg-stone-50 font-semibold text-stone-700">Next →</button>
          </div>
        </div>
      ` : ""}
    `;
  },

  // 6. Skeleton Loader Component
  renderSkeleton(type = "card") {
    if (type === "card") {
      return `
        <div class="p-5 rounded-2xl bg-white border border-stone-200 animate-pulse space-y-3">
          <div class="h-3 w-1/3 bg-stone-200 rounded"></div>
          <div class="h-7 w-2/3 bg-stone-200 rounded"></div>
          <div class="h-3 w-1/2 bg-stone-100 rounded"></div>
        </div>
      `;
    }
    return `
      <div class="w-full h-32 bg-stone-100 rounded-2xl animate-pulse"></div>
    `;
  },

  // 7. Empty State Component
  renderEmptyState(title = "No data found", message = "There is currently no information to display.") {
    return `
      <div class="p-8 rounded-2xl bg-white border border-stone-200/80 text-center space-y-2">
        <div class="w-10 h-10 mx-auto rounded-full bg-stone-100 text-stone-400 flex items-center justify-center font-bold text-lg">∅</div>
        <h4 class="text-sm font-bold text-stone-800">${title}</h4>
        <p class="text-xs text-stone-500 max-w-sm mx-auto">${message}</p>
      </div>
    `;
  },

  // 8. Financial Weather Strip Component
  renderFinancialWeatherStrip(weather) {
    if (!weather) return "";
    const badgeColor = weather.badge_color || "emerald";
    const bgClass = badgeColor === "rose" ? "bg-rose-500/10 border-rose-500/20 text-rose-700 dark:text-rose-400" :
                    badgeColor === "amber" ? "bg-amber-500/10 border-amber-500/20 text-amber-700 dark:text-amber-400" :
                    "bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-400";
    
    const dailyForecast = weather.daily_forecast || [];

    return `
      <div class="mb-6 p-4 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm transition-all">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${bgClass} border">
              ${weather.icon || "🌤️"}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-bold uppercase tracking-wider text-stone-400">FINANCIAL WEATHER (7-DAY)</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono ${bgClass}">${weather.label || "STABLE"}</span>
              </div>
              <h4 class="text-sm font-bold text-stone-900 dark:text-stone-100 mt-0.5">${weather.main_driver || "Corridor balanced inside safety margins."}</h4>
            </div>
          </div>
          <div class="flex items-center gap-1.5 overflow-x-auto py-1">
            ${dailyForecast.map(d => `
              <div class="flex flex-col items-center px-2 py-1.5 rounded-xl border border-stone-100 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/60 min-w-[52px]">
                <span class="text-[10px] font-semibold text-stone-500 dark:text-stone-400">${d.day}</span>
                <span class="text-xs my-0.5">${d.status === "HIGH_PRESSURE" ? "🌧️" : d.status === "PRESSURED" ? "⛅" : "☀️"}</span>
                <span class="text-[9px] font-mono font-bold ${d.pressure_level === "HIGH" ? "text-rose-600" : d.pressure_level === "MODERATE" ? "text-amber-600" : "text-emerald-600"}">₹${Math.round(d.projected_checking/1000)}k</span>
              </div>
            `).join("")}
          </div>
        </div>
      </div>
    `;
  },

  // 9. What Changed This Week Component
  renderWhatChangedCard(whatChanged) {
    if (!whatChanged || !whatChanged.items) return "";
    const resDelta = whatChanged.resilience_delta || 0;
    const isUp = resDelta >= 0;

    return `
      <div class="p-6 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm mb-6">
        <div class="flex items-center justify-between pb-3 border-b border-stone-100 dark:border-stone-800 mb-4">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
            <h3 class="text-xs font-bold uppercase tracking-wider text-stone-700 dark:text-stone-300">WHAT CHANGED THIS WEEK?</h3>
          </div>
          <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded-full ${isUp ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'}">
            Resilience: ${whatChanged.resilience_before || 72} → ${whatChanged.resilience_after || 74} (${resDelta >= 0 ? '+' : ''}${resDelta} pts)
          </span>
        </div>
        <p class="text-xs text-stone-600 dark:text-stone-400 mb-4 leading-relaxed">${whatChanged.summary || "Weekly operational delta summary."}</p>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          ${whatChanged.items.map(it => `
            <div class="p-3 rounded-xl bg-stone-50 dark:bg-stone-800/60 border border-stone-100 dark:border-stone-800">
              <span class="text-[10px] uppercase font-bold text-stone-400">${it.label}</span>
              <div class="text-sm font-extrabold font-mono mt-0.5 ${it.direction === 'up' && it.label === 'Essential Spending' ? 'text-rose-600' : it.direction === 'up' ? 'text-emerald-600' : 'text-stone-700 dark:text-stone-200'}">
                ${it.delta_display}
              </div>
              <span class="text-[10px] text-stone-400 font-mono block mt-0.5">${it.detail}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  },

  // 10. The 5 Core Financial Questions Engine
  render5CoreQuestions({ twin = {}, weather = {}, plan = {} } = {}) {
    const prof = twin?.observation?.profile || twin?.profile || {};
    const currInc = prof.current_income || 0;
    const burn = prof.weekly_burn || 0;
    const currBuf = prof.current_buffer || 0;
    const targetBuf = prof.buffer_target || 15000;
    const floor = prof.protected_floor || 3500;
    const resilience = prof.resilience_score || 74;
    const coverage = prof.current_coverage_weeks || 1.5;
    const safeSave = prof.recommended_contribution || 0;

    const stateMachine = twin?.state_machine || {};
    const currentState = twin?.financial_state || stateMachine.current_state || "STABLE";
    const topAction = plan?.actions?.[0]?.action || plan?.top_priorities?.[0]?.title || `Retain ₹${safeSave.toLocaleString()} buffer contribution.`;

    const q1Status = resilience >= 70 ? "Protected" : resilience >= 50 ? "Stable with Attention" : "High Pressure";
    const q1Badge = resilience >= 70 ? "emerald" : resilience >= 50 ? "amber" : "rose";

    return `
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-extrabold uppercase tracking-wider text-stone-900 dark:text-stone-100">THE 5 CORE FINANCIAL QUESTIONS</h3>
            <p class="text-xs text-stone-500 mt-0.5">Continuous institutional state evaluation updated in real-time.</p>
          </div>
          <span class="text-[11px] font-mono px-2.5 py-1 rounded-full bg-brand-500/10 text-brand-600 font-bold">State: ${currentState}</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-5 gap-3.5">
          <!-- Q1 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm flex flex-col justify-between hover:border-brand-500/40 transition-colors">
            <div>
              <span class="text-[10px] font-bold text-brand-600 uppercase tracking-wider">1. Safety Now</span>
              <h4 class="text-xs font-bold text-stone-900 dark:text-stone-100 mt-1">How safe am I right now?</h4>
            </div>
            <div class="mt-3">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-${q1Badge}-500/10 text-${q1Badge}-600">${q1Status}</span>
              <p class="text-[11px] text-stone-500 dark:text-stone-400 mt-2 leading-relaxed">
                ${coverage} weeks runway (₹${currBuf.toLocaleString()}). Floor of ₹${floor.toLocaleString()} is intact.
              </p>
            </div>
          </div>

          <!-- Q2 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm flex flex-col justify-between hover:border-brand-500/40 transition-colors">
            <div>
              <span class="text-[10px] font-bold text-brand-600 uppercase tracking-wider">2. Change Detection</span>
              <h4 class="text-xs font-bold text-stone-900 dark:text-stone-100 mt-1">What changed recently?</h4>
            </div>
            <div class="mt-3">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-blue-500/10 text-blue-600">Active Shift Log</span>
              <p class="text-[11px] text-stone-500 dark:text-stone-400 mt-2 leading-relaxed">
                ${twin?.what_changed?.summary || "Operations stable with no adverse shocks detected."}
              </p>
            </div>
          </div>

          <!-- Q3 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm flex flex-col justify-between hover:border-brand-500/40 transition-colors">
            <div>
              <span class="text-[10px] font-bold text-brand-600 uppercase tracking-wider">3. Forward Outlook</span>
              <h4 class="text-xs font-bold text-stone-900 dark:text-stone-100 mt-1">What will happen next?</h4>
            </div>
            <div class="mt-3">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-amber-500/10 text-amber-600">${weather?.label || "Weather: Stable"}</span>
              <p class="text-[11px] text-stone-500 dark:text-stone-400 mt-2 leading-relaxed">
                ${weather?.main_driver || "Inflows absorb all scheduled rent tranches safely."}
              </p>
            </div>
          </div>

          <!-- Q4 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm flex flex-col justify-between hover:border-brand-500/40 transition-colors">
            <div>
              <span class="text-[10px] font-bold text-brand-600 uppercase tracking-wider">4. Safe Next Action</span>
              <h4 class="text-xs font-bold text-stone-900 dark:text-stone-100 mt-1">What should I do next?</h4>
            </div>
            <div class="mt-3">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-600">Rank #1 Action</span>
              <p class="text-[11px] text-stone-500 dark:text-stone-400 mt-2 leading-relaxed">
                ${topAction}
              </p>
            </div>
          </div>

          <!-- Q5 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 shadow-sm flex flex-col justify-between hover:border-brand-500/40 transition-colors">
            <div>
              <span class="text-[10px] font-bold text-brand-600 uppercase tracking-wider">5. Recovery Protocol</span>
              <h4 class="text-xs font-bold text-stone-900 dark:text-stone-100 mt-1">How do I recover?</h4>
            </div>
            <div class="mt-3">
              <a href="resilience-plan.html" class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-purple-500/10 text-purple-600 hover:underline">30-Day Plan →</a>
              <p class="text-[11px] text-stone-500 dark:text-stone-400 mt-2 leading-relaxed">
                3 pathways ready to close ₹${Math.max(0, targetBuf - currBuf).toLocaleString()} buffer gap without debt.
              </p>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  // 14. Data Trust Badge (Audit & Provenance)
  renderDataTrustBadge({ source = "Deterministic Engine", updated = "Real-time", confidence = "100%", status = "Authoritative" } = {}) {
    return `
      <div class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-mono font-medium border border-emerald-500/25 bg-emerald-50/80 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 whitespace-nowrap max-w-full overflow-hidden flex-shrink-0 shadow-xs" title="Source: ${source} | Status: ${status} | Confidence: ${confidence}">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0"></span>
        <span class="font-semibold truncate">${source}</span>
        <span class="text-emerald-400/60 dark:text-emerald-600 flex-shrink-0">•</span>
        <span class="text-stone-500 dark:text-stone-400 flex-shrink-0">${status}</span>
      </div>
    `;
  }
};

window.SURE_SAVINGS_UI = UI;
