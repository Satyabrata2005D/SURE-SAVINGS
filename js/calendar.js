/**
 * SURE SAVINGS 8.0: Authoritative Financial Calendar & Liquidity Heatmap Controller
 * Full user-driven event orchestration, intraday liquidity inspector, and reactive recalculation.
 */

class FinancialCalendarController {
  constructor() {
    this.currentYear = 2026;
    this.currentMonth = 9; // September default or system current
    this.calendarData = null;
    this.selectedDate = null;
    this.editingEventId = null;
    this.isLoading = false;
    this.activeFilter = "all";
    this.searchQuery = "";
  }

  init() {
    // Determine initial date
    const now = new Date();
    const urlParams = new URLSearchParams(window.location.search);
    const paramYear = parseInt(urlParams.get("year"));
    const paramMonth = parseInt(urlParams.get("month"));

    if (paramYear && paramYear >= 2000 && paramYear <= 2100) {
      this.currentYear = paramYear;
    } else {
      this.currentYear = 2026;
    }

    if (paramMonth && paramMonth >= 1 && paramMonth <= 12) {
      this.currentMonth = paramMonth;
    } else {
      this.currentMonth = 9; // Default to September 2026
    }

    this.bindEvents();
    this.loadCalendar();
  }

  bindEvents() {
    // Navigation buttons
    const prevBtn = document.getElementById("calPrevMonth");
    if (prevBtn) prevBtn.addEventListener("click", () => this.navigateMonth(-1));

    const nextBtn = document.getElementById("calNextMonth");
    if (nextBtn) nextBtn.addEventListener("click", () => this.navigateMonth(1));

    const todayBtn = document.getElementById("calTodayBtn");
    if (todayBtn) todayBtn.addEventListener("click", () => this.jumpToToday());

    // Sync button
    const syncBtn = document.getElementById("calSyncBtn");
    if (syncBtn) syncBtn.addEventListener("click", () => this.syncCalendar());

    // Add event button
    const addBtn = document.getElementById("calAddEventBtn");
    if (addBtn) addBtn.addEventListener("click", () => this.openAddEventModal());

    // Modal close buttons
    const modalClose = document.getElementById("closeEventModal");
    if (modalClose) modalClose.addEventListener("click", () => this.closeEventModal());

    const modalCancel = document.getElementById("cancelEventBtn");
    if (modalCancel) modalCancel.addEventListener("click", () => this.closeEventModal());

    // Event form submission
    const eventForm = document.getElementById("calendarEventForm");
    if (eventForm) {
      eventForm.addEventListener("submit", (e) => this.handleEventFormSubmit(e));
    }

    // Filter tabs
    const filterBtns = document.querySelectorAll("#calFilterGroup .cal-filter-btn");
    filterBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        filterBtns.forEach(b => {
          b.classList.remove("border-brand-500", "bg-brand-50", "text-brand-600", "dark:bg-brand-950/60", "dark:text-brand-300");
          b.classList.add("border-stone-200", "dark:border-stone-800", "text-stone-600", "dark:text-stone-300");
        });
        btn.classList.remove("border-stone-200", "dark:border-stone-800", "text-stone-600", "dark:text-stone-300");
        btn.classList.add("border-brand-500", "bg-brand-50", "text-brand-600", "dark:bg-brand-950/60", "dark:text-brand-300");
        this.activeFilter = btn.getAttribute("data-filter") || "all";
        this.renderCalendarGrid();
      });
    });

    // Search input
    const searchInput = document.getElementById("calSearchInput");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.searchQuery = (e.target.value || "").trim().toLowerCase();
        this.renderCalendarGrid();
      });
    }

    // Connect Income Source
    const connectIncomeBtn = document.getElementById("connectIncomeBtn");
    if (connectIncomeBtn) connectIncomeBtn.addEventListener("click", () => this.openConnectIncomeModal());

    const closeIncomeModal = document.getElementById("closeIncomeModal");
    if (closeIncomeModal) closeIncomeModal.addEventListener("click", () => this.closeConnectIncomeModal());

    const cancelIncomeBtn = document.getElementById("cancelIncomeBtn");
    if (cancelIncomeBtn) cancelIncomeBtn.addEventListener("click", () => this.closeConnectIncomeModal());

    const connectIncomeForm = document.getElementById("connectIncomeForm");
    if (connectIncomeForm) connectIncomeForm.addEventListener("submit", (e) => this.handleConnectIncomeSubmit(e));

    // Variance
    const varianceBtn = document.getElementById("calVarianceBtn");
    if (varianceBtn) varianceBtn.addEventListener("click", () => this.openVarianceModal());

    const closeVarianceModal = document.getElementById("closeVarianceModal");
    if (closeVarianceModal) closeVarianceModal.addEventListener("click", () => this.closeVarianceModal());

    // Exports
    const exportCsvBtn = document.getElementById("calExportCsvBtn");
    if (exportCsvBtn) exportCsvBtn.addEventListener("click", () => this.exportCalendar("csv"));

    const exportJsonBtn = document.getElementById("calExportJsonBtn");
    if (exportJsonBtn) exportJsonBtn.addEventListener("click", () => this.exportCalendar("json"));
  }

  navigateMonth(delta) {
    this.currentMonth += delta;
    if (this.currentMonth < 1) {
      this.currentMonth = 12;
      this.currentYear -= 1;
    } else if (this.currentMonth > 12) {
      this.currentMonth = 1;
      this.currentYear += 1;
    }
    this.loadCalendar();
  }

  jumpToToday() {
    this.currentYear = 2026;
    this.currentMonth = 9;
    this.loadCalendar();
  }

  async loadCalendar() {
    this.isLoading = true;
    const syncIcon = document.getElementById("calSyncIcon");
    if (syncIcon) syncIcon.classList.add("animate-spin");

    try {
      const isDemo = window.location.pathname.includes("landing.html") || false;
      const data = await window.api.getCalendar(this.currentYear, this.currentMonth, isDemo);
      this.calendarData = data;
      this.renderHeader();
      this.renderSummaryStats();
      this.renderCalendarGrid();
    } catch (err) {
      console.error("[Calendar] Failed to load calendar data:", err);
      if (window.showToast) {
        window.showToast("Could not retrieve calendar feed. Using active local cache.", "error");
      }
    } finally {
      this.isLoading = false;
      if (syncIcon) syncIcon.classList.remove("animate-spin");
    }
  }

  renderHeader() {
    const titleEl = document.getElementById("calendarMonthTitle");
    const subTitleEl = document.getElementById("calendarMonthSubtitle");
    if (titleEl && this.calendarData) {
      titleEl.textContent = `${this.calendarData.month_name} ${this.calendarData.year}`;
    }
    if (subTitleEl && this.calendarData) {
      const daysCount = this.calendarData.num_days || 30;
      subTitleEl.textContent = `Comprehensive 30-day liquidity heatmap • ${daysCount} Days Paced`;
    }
  }

  renderSummaryStats() {
    if (!this.calendarData || !this.calendarData.summary) return;
    const s = this.calendarData.summary;

    const expIncomeEl = document.querySelector("[data-calendar='expected-income']");
    if (expIncomeEl) expIncomeEl.textContent = `₹${Math.round(s.expected_income).toLocaleString()}`;

    const mandOutflowsEl = document.querySelector("[data-calendar='mandated-outflows']");
    if (mandOutflowsEl) mandOutflowsEl.textContent = `₹${Math.round(s.essential_outflows).toLocaleString()}`;

    const critGapEl = document.querySelector("[data-calendar='critical-gap']");
    const gapStatusEl = document.querySelector("[data-calendar='gap-status']");
    if (critGapEl) {
      if (this.calendarData.critical_days && this.calendarData.critical_days.length > 0) {
        const firstGap = this.calendarData.critical_days[0];
        critGapEl.textContent = firstGap.date;
        critGapEl.className = "text-lg font-black font-mono text-amber-500";
        if (gapStatusEl) {
          gapStatusEl.textContent = `Gap ₹${Math.round(firstGap.gap_amount).toLocaleString()} • Buffer absorbed`;
          gapStatusEl.className = "text-[10px] text-amber-600 font-bold";
        }
      } else {
        critGapEl.textContent = "None • Safe";
        critGapEl.className = "text-lg font-black font-mono text-emerald-600";
        if (gapStatusEl) {
          gapStatusEl.textContent = "Floor 100% Protected";
          gapStatusEl.className = "text-[10px] text-emerald-600 font-bold";
        }
      }
    }

    const resBufferEl = document.querySelector("[data-calendar='reserve-buffer']");
    if (resBufferEl) {
      resBufferEl.textContent = `₹${Math.round(s.vault_buffer_available).toLocaleString()}`;
    }
  }

  renderCalendarGrid() {
    const grid = document.getElementById("calendarGridContainer");
    if (!grid || !this.calendarData) return;

    grid.innerHTML = "";

    const firstWeekday = this.calendarData.first_weekday || 0; // 0 = Monday, 6 = Sunday
    const days = this.calendarData.days || [];
    const prevMonthDaysCount = 31; // Aesthetic filler

    // 1. Padding days from previous month
    for (let i = 0; i < firstWeekday; i++) {
      const padDayNum = prevMonthDaysCount - firstWeekday + i + 1;
      const padCell = document.createElement("div");
      padCell.className = "p-2 rounded-xl border min-h-[100px] opacity-35 flex flex-col justify-between cursor-not-allowed select-none";
      padCell.style.background = "var(--surface-sunken)";
      padCell.style.borderColor = "var(--border-default)";
      padCell.innerHTML = `
        <span class="font-bold text-xs" style="color: var(--text-subtle);">${padDayNum}</span>
        <span class="text-[9px]" style="color: var(--text-subtle);">Prior Cycle</span>
      `;
      grid.appendChild(padCell);
    }

    // 2. Current month days
    days.forEach((d) => {
      const cell = document.createElement("div");
      const isToday = (this.currentMonth === 9 && d.day === 10); // Or today's date
      const isCriticalGap = d.has_timing_gap;

      // Status Styling
      let borderStyle = "border-color: var(--border-default);";
      let bgStyle = "background: var(--surface-sunken);";
      let badgeHtml = "";

      if (isCriticalGap) {
        borderStyle = "border-color: #f59e0b; border-width: 2px;";
        bgStyle = "background: rgba(245, 158, 11, 0.05);";
        badgeHtml = `<span class="text-[8px] font-black uppercase tracking-wider text-amber-600 bg-amber-100 dark:bg-amber-950/60 px-1 py-0.5 rounded shadow-sm">⚠️ GAP</span>`;
      } else if (d.status === "RED") {
        borderStyle = "border-color: #f43f5e; border-width: 2px;";
        bgStyle = "background: rgba(244, 63, 94, 0.05);";
        badgeHtml = `<span class="text-[8px] font-black uppercase tracking-wider text-rose-600 bg-rose-100 dark:bg-rose-950/60 px-1 py-0.5 rounded">DEFICIT</span>`;
      } else if (d.status === "AMBER") {
        borderStyle = "border-color: #fbbf24;";
        badgeHtml = `<span class="text-[8px] font-bold text-amber-600 bg-amber-50 dark:bg-amber-950/40 px-1 py-0.5 rounded">NEAR FLOOR</span>`;
      } else if (d.status === "BLUE") {
        borderStyle = "border-color: #3b82f6;";
        badgeHtml = `<span class="text-[8px] font-bold text-blue-600 bg-blue-50 dark:bg-blue-950/40 px-1 py-0.5 rounded">SWEEP</span>`;
      } else if (d.status === "GREEN") {
        badgeHtml = `<span class="text-[8px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-1 py-0.5 rounded">SURPLUS</span>`;
      }

      // Events chips preview with active filter and search query
      let filteredEvents = d.events || [];
      if (this.activeFilter === "inflow") {
        filteredEvents = filteredEvents.filter(e => e.direction === "credit");
      } else if (this.activeFilter === "outflow") {
        filteredEvents = filteredEvents.filter(e => e.direction === "debit");
      } else if (this.activeFilter === "obligation") {
        filteredEvents = filteredEvents.filter(e => e.type === "OBLIGATION");
      } else if (this.activeFilter === "buffer") {
        filteredEvents = filteredEvents.filter(e => e.type === "BUFFER");
      }

      if (this.searchQuery) {
        filteredEvents = filteredEvents.filter(e =>
          (e.title && e.title.toLowerCase().includes(this.searchQuery)) ||
          (e.category && e.category.toLowerCase().includes(this.searchQuery)) ||
          (e.description && e.description.toLowerCase().includes(this.searchQuery))
        );
      }

      const isFilterActive = this.activeFilter !== "all" || this.searchQuery.length > 0;
      let matchesFilter = true;
      if (isFilterActive) {
        if (this.activeFilter === "critical") {
          matchesFilter = isCriticalGap;
        } else {
          matchesFilter = filteredEvents.length > 0;
        }
      }

      const dimClass = (isFilterActive && !matchesFilter) ? "opacity-25 grayscale hover:opacity-100 hover:grayscale-0" : "";
      cell.className = `cursor-pointer p-2.5 rounded-xl border min-h-[105px] flex flex-col justify-between transition-all hover:border-brand-500 hover:scale-[1.02] ${todayClasses} ${dimClass}`;
      cell.style = `${bgStyle} ${borderStyle}`;
      cell.setAttribute("data-date", d.date);

      let eventsHtml = `<div class="space-y-1 mt-1">`;
      const previewEvents = (isFilterActive ? filteredEvents : d.events).slice(0, 2);
      previewEvents.forEach((ev) => {
        const isCredit = ev.direction === "credit";
        const colorClass = isCredit ? "text-emerald-600 font-bold" : (ev.is_simulation ? "text-purple-600 italic" : "text-rose-600 font-medium");
        const prefix = isCredit ? "+" : "-";
        const titleTrimmed = ev.title.length > 14 ? ev.title.slice(0, 13) + "…" : ev.title;
        eventsHtml += `
          <div class="text-[10px] font-mono leading-tight flex items-center justify-between gap-1 ${colorClass}">
            <span class="truncate">${titleTrimmed}</span>
            <span class="shrink-0 font-bold">${prefix}₹${Math.round(ev.amount).toLocaleString()}</span>
          </div>
        `;
      });

      const totalMatching = isFilterActive ? filteredEvents.length : d.events.length;
      if (totalMatching > 2) {
        eventsHtml += `<div class="text-[9px] text-stone-400 font-semibold">+${totalMatching - 2} more</div>`;
      } else if (totalMatching === 0) {
        eventsHtml += `<div class="text-[9px]" style="color: var(--text-subtle);">${isFilterActive ? 'No Matches' : 'Rest Day'}</div>`;
      }
      eventsHtml += `</div>`;

      // Liquidity Balance Footer
      const balanceHtml = `
        <div class="pt-1 border-t flex items-center justify-between text-[9px]" style="border-color: var(--border-default)">
          <span style="color: var(--text-muted)">Closing</span>
          <span class="font-mono font-bold ${d.closing_balance < d.floor ? 'text-rose-500' : 'text-stone-700 dark:text-stone-300'}">₹${Math.round(d.closing_balance).toLocaleString()}</span>
        </div>
      `;

      cell.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-black text-xs ${isToday ? 'w-5 h-5 rounded-full bg-brand-500 text-white flex items-center justify-center' : ''}" style="color: ${isToday ? '#fff' : 'var(--text-primary)'};">${d.day}</span>
          ${badgeHtml}
        </div>
        ${eventsHtml}
        ${balanceHtml}
      `;

      cell.addEventListener("click", () => this.selectDay(d.date));
      grid.appendChild(cell);
    });

    // 3. Trailing days to complete standard 35 or 42 grid cells
    const totalRendered = firstWeekday + days.length;
    const totalSlots = totalRendered > 35 ? 42 : 35;
    const trailingCount = totalSlots - totalRendered;
    for (let j = 1; j <= trailingCount; j++) {
      const nextCell = document.createElement("div");
      nextCell.className = "p-2 rounded-xl border min-h-[100px] opacity-35 flex flex-col justify-between cursor-not-allowed select-none";
      nextCell.style.background = "var(--surface-sunken)";
      nextCell.style.borderColor = "var(--border-default)";
      nextCell.innerHTML = `
        <span class="font-bold text-xs" style="color: var(--text-subtle);">${j}</span>
        <span class="text-[9px]" style="color: var(--text-subtle);">Next Cycle</span>
      `;
      grid.appendChild(nextCell);
    }
  }

  async selectDay(dateStr) {
    this.selectedDate = dateStr;
    const inspector = document.getElementById("dayInspector");
    if (!inspector) return;

    inspector.classList.remove("hidden");
    inspector.scrollIntoView({ behavior: "smooth", block: "nearest" });

    // Show loading state in inspector
    const titleEl = document.getElementById("inspectorTitle");
    const bodyEl = document.getElementById("inspectorBody");
    if (titleEl) titleEl.textContent = `Loading ${dateStr}…`;
    if (bodyEl) bodyEl.innerHTML = `<div class="p-6 text-center text-xs text-stone-400">Loading intraday liquidity intelligence…</div>`;

    try {
      const detail = await window.api.getCalendarDay(dateStr);
      this.renderDayDetail(detail);
    } catch (err) {
      console.error("[Calendar] Failed to load day details:", err);
      if (bodyEl) {
        bodyEl.innerHTML = `<div class="p-4 text-xs text-rose-500">Failed to load detailed timeline for ${dateStr}.</div>`;
      }
    }
  }

  renderDayDetail(detail) {
    const titleEl = document.getElementById("inspectorTitle");
    const bodyEl = document.getElementById("inspectorBody");
    if (!detail || !bodyEl) return;

    if (titleEl) {
      titleEl.innerHTML = `
        <span>${detail.day_of_week}, ${detail.date}</span>
        <span class="ml-2 text-xs px-2 py-0.5 rounded font-mono font-bold ${
          detail.has_timing_gap ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
        }">${detail.status}</span>
      `;
    }

    // Diagnostics Alert Banner
    let bannerHtml = "";
    if (detail.has_timing_gap) {
      bannerHtml = `
        <div class="p-3.5 rounded-xl border border-amber-300 bg-amber-50 dark:bg-amber-950/40 dark:border-amber-800 space-y-1 mb-4">
          <div class="flex items-center gap-2 text-xs font-black text-amber-800 dark:text-amber-300">
            <svg class="w-4 h-4 text-amber-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            <span>TIMING GAP DETECTED: Shortfall of ₹${Math.round(detail.intraday_gap_amount).toLocaleString()}</span>
          </div>
          <p class="text-[11px] text-amber-700 dark:text-amber-400 leading-relaxed">
            ${detail.risk_reason || "Scheduled commitments debit before incoming settlements are cleared."}
            Automated vault buffer absorption of ₹${Math.round(detail.absorption_required).toLocaleString()} prevents checking account breach.
          </p>
        </div>
      `;
    }

    // Top KPI Bar
    const kpiHtml = `
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-2.5 mb-4 text-center">
        <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
          <span class="text-[10px] text-stone-500 uppercase font-bold">Opening</span>
          <div class="font-mono font-bold text-sm" style="color: var(--text-primary)">₹${Math.round(detail.opening_balance).toLocaleString()}</div>
        </div>
        <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
          <span class="text-[10px] text-stone-500 uppercase font-bold">Inflows</span>
          <div class="font-mono font-bold text-sm text-emerald-600">+₹${Math.round(detail.total_inflow).toLocaleString()}</div>
        </div>
        <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
          <span class="text-[10px] text-stone-500 uppercase font-bold">Outflows</span>
          <div class="font-mono font-bold text-sm text-rose-500">-₹${Math.round(detail.total_outflow).toLocaleString()}</div>
        </div>
        <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
          <span class="text-[10px] text-stone-500 uppercase font-bold">Min Intraday</span>
          <div class="font-mono font-bold text-sm ${detail.lowest_intraday_balance < detail.floor ? 'text-amber-500' : 'text-stone-700 dark:text-stone-300'}">₹${Math.round(detail.lowest_intraday_balance).toLocaleString()}</div>
        </div>
        <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
          <span class="text-[10px] text-stone-500 uppercase font-bold">Closing</span>
          <div class="font-mono font-bold text-sm text-brand-500">₹${Math.round(detail.closing_balance).toLocaleString()}</div>
        </div>
      </div>
    `;

    // Intraday Liquidity Progression Curve
    let timelineHtml = `
      <div class="mb-5">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-xs font-black uppercase tracking-wider" style="color: var(--text-primary)">Intraday Liquidity Progression Curve</h4>
          <span class="text-[10px] font-mono text-stone-400">Protected Floor: ₹${Math.round(detail.floor).toLocaleString()}</span>
        </div>
        <div class="space-y-2 border-l-2 border-brand-500/40 ml-3 pl-3 py-1">
    `;

    detail.timeline.forEach((node) => {
      const isNegative = node.amount < 0;
      const isPositive = node.amount > 0;
      const amtColor = isNegative ? "text-rose-500" : (isPositive ? "text-emerald-600" : "text-stone-400");
      const sign = isPositive ? "+" : (isNegative ? "" : "");

      timelineHtml += `
        <div class="relative group">
          <div class="absolute -left-[19px] top-1.5 w-2.5 h-2.5 rounded-full bg-brand-500 border-2 border-white dark:border-stone-900"></div>
          <div class="p-2.5 rounded-xl border text-xs" style="background: var(--surface-sunken); border-color: var(--border-default)">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <span class="font-mono font-bold text-brand-500 text-[11px]">${node.time}</span>
                <span class="font-extrabold" style="color: var(--text-primary)">${node.event}</span>
              </div>
              <div class="flex items-center gap-2 font-mono">
                ${node.amount !== 0 ? `<span class="font-bold ${amtColor}">${sign}₹${Math.round(node.amount).toLocaleString()}</span>` : ''}
                <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${node.projected_checking < detail.floor ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">Checking: ₹${Math.round(node.projected_checking).toLocaleString()}</span>
              </div>
            </div>
            <p class="text-[11px] text-stone-500 mt-1">${node.description}</p>
          </div>
        </div>
      `;
    });

    timelineHtml += `
        </div>
      </div>
    `;

    // Events Table / List
    let eventsListHtml = `
      <div>
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-xs font-black uppercase tracking-wider" style="color: var(--text-primary)">Scheduled Events (${detail.events.length})</h4>
          <button onclick="window.calendarController.openAddEventModal('${detail.date}')" class="text-xs text-brand-500 hover:text-brand-600 font-bold flex items-center gap-1">
            <span>+ Add to this day</span>
          </button>
        </div>
        <div class="space-y-2">
    `;

    if (detail.events.length === 0) {
      eventsListHtml += `<p class="text-xs text-stone-400 py-3">No specific commitments recorded for this day.</p>`;
    } else {
      detail.events.forEach((ev) => {
        const isUserEvent = ev.id && !ev.id.startsWith("obl_") && !ev.id.startsWith("tx_") && !ev.id.startsWith("sub_");
        eventsListHtml += `
          <div class="p-3 rounded-xl border flex items-center justify-between gap-3 text-xs" style="background: var(--surface-sunken); border-color: var(--border-default)">
            <div class="flex items-center gap-2.5">
              <span class="text-base">${ev.direction === 'credit' ? '🟢' : (ev.is_simulation ? '⚡' : '🔴')}</span>
              <div>
                <p class="font-bold text-xs" style="color: var(--text-primary)">${ev.title}</p>
                <p class="text-[10px] text-stone-400">${ev.time} • ${ev.category} • ${ev.is_essential ? 'Essential' : 'Discretionary'}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-mono font-bold text-sm ${ev.direction === 'credit' ? 'text-emerald-600' : 'text-rose-500'}">
                ${ev.direction === 'credit' ? '+' : '-'}₹${Math.round(ev.amount).toLocaleString()}
              </span>
              ${isUserEvent ? `
                <div class="flex items-center gap-1">
                  <button onclick="window.calendarController.editEvent('${ev.id}')" class="p-1 rounded text-stone-400 hover:text-brand-500 hover:bg-stone-100 dark:hover:bg-stone-800" title="Edit Event">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                  </button>
                  <button onclick="window.calendarController.deleteEvent('${ev.id}')" class="p-1 rounded text-stone-400 hover:text-rose-500 hover:bg-stone-100 dark:hover:bg-stone-800" title="Delete Event">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </button>
                </div>
              ` : `
                <span class="text-[9px] text-stone-400 font-mono">System</span>
              `}
            </div>
          </div>
        `;
      });
    }

    eventsListHtml += `
        </div>
      </div>
    `;

    bodyEl.innerHTML = `
      ${bannerHtml}
      ${kpiHtml}
      ${timelineHtml}
      ${eventsListHtml}
    `;
  }

  openAddEventModal(prefilledDate = null) {
    this.editingEventId = null;
    const modal = document.getElementById("calendarEventModal");
    const form = document.getElementById("calendarEventForm");
    const modalTitle = document.getElementById("eventModalTitle");

    if (modalTitle) modalTitle.textContent = "Schedule Financial Event";
    if (form) {
      form.reset();
      const dateInput = document.getElementById("eventDateInput");
      if (dateInput) {
        dateInput.value = prefilledDate || `${this.currentYear}-${String(this.currentMonth).padStart(2, '0')}-15`;
      }
      const timeInput = document.getElementById("eventTimeInput");
      if (timeInput) timeInput.value = "09:00 AM";
      const recInput = document.getElementById("eventRecurrenceInput");
      if (recInput) recInput.value = "none";
      const statusInput = document.getElementById("eventStatusInput");
      if (statusInput) statusInput.value = "EXPECTED";
    }

    if (modal) modal.classList.remove("hidden");
  }

  editEvent(eventId) {
    const ev = (this.calendarData?.events || []).find((e) => e.id === eventId);
    if (!ev) return;

    this.editingEventId = eventId;
    const modal = document.getElementById("calendarEventModal");
    const modalTitle = document.getElementById("eventModalTitle");

    if (modalTitle) modalTitle.textContent = `Edit Event: ${ev.title}`;

    document.getElementById("eventTitleInput").value = ev.title;
    document.getElementById("eventAmountInput").value = ev.amount;
    document.getElementById("eventDateInput").value = ev.date;
    document.getElementById("eventTimeInput").value = ev.time || "09:00 AM";
    document.getElementById("eventDirectionInput").value = ev.direction || "outflow";
    document.getElementById("eventCategoryInput").value = ev.category || "General";
    document.getElementById("eventTypeInput").value = ev.type || "commitment";
    document.getElementById("eventEssentialInput").checked = ev.is_essential !== false;
    document.getElementById("eventSimulationInput").checked = ev.is_simulation === true;
    document.getElementById("eventNotesInput").value = ev.notes || "";

    const recInput = document.getElementById("eventRecurrenceInput");
    if (recInput) recInput.value = ev.recurrence || "none";

    const statusInput = document.getElementById("eventStatusInput");
    if (statusInput) statusInput.value = ev.status || "EXPECTED";

    if (modal) modal.classList.remove("hidden");
  }

  closeEventModal() {
    const modal = document.getElementById("calendarEventModal");
    if (modal) modal.classList.add("hidden");
    this.editingEventId = null;
  }

  async handleEventFormSubmit(e) {
    e.preventDefault();
    const title = document.getElementById("eventTitleInput").value.trim();
    const amount = parseFloat(document.getElementById("eventAmountInput").value);
    const dateStr = document.getElementById("eventDateInput").value;
    const timeStr = document.getElementById("eventTimeInput").value || "09:00 AM";
    const direction = document.getElementById("eventDirectionInput").value;
    const category = document.getElementById("eventCategoryInput").value;
    const eventType = document.getElementById("eventTypeInput").value;
    const isEssential = document.getElementById("eventEssentialInput").checked;
    const isSimulation = document.getElementById("eventSimulationInput").checked;
    const recurrence = document.getElementById("eventRecurrenceInput")?.value || "none";
    const status = document.getElementById("eventStatusInput")?.value || "EXPECTED";
    const notes = document.getElementById("eventNotesInput").value.trim();

    if (!title || isNaN(amount) || amount <= 0 || !dateStr) {
      if (window.showToast) window.showToast("Please fill all required fields with valid amounts.", "error");
      return;
    }

    const payload = {
      title,
      amount,
      date_str: dateStr,
      time_str: timeStr,
      direction,
      category,
      event_type: eventType,
      is_essential: isEssential,
      is_simulation: isSimulation,
      recurrence: recurrence,
      status: status,
      notes: notes || null
    };

    const submitBtn = document.getElementById("saveEventBtn");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Saving…";
    }

    try {
      const api = window.api || window.sureSavingsApi;
      if (this.editingEventId) {
        await api.updateCalendarEvent(this.editingEventId, payload);
        if (window.showToast) window.showToast(`Updated '${title}' successfully.`, "success");
      } else {
        await api.createCalendarEvent(payload);
        if (window.showToast) window.showToast(`Added '${title}' to calendar.`, "success");
      }
      this.closeEventModal();
      await this.loadCalendar();
      if (this.selectedDate) {
        await this.selectDay(this.selectedDate);
      }
    } catch (err) {
      console.error("[Calendar] Event save error:", err);
      if (window.showToast) window.showToast(`Failed to save event: ${err.message}`, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Event";
      }
    }
  }

  // Connect Income Source Modal handlers
  openConnectIncomeModal() {
    const modal = document.getElementById("connectIncomeModal");
    if (modal) modal.classList.remove("hidden");
  }

  closeConnectIncomeModal() {
    const modal = document.getElementById("connectIncomeModal");
    if (modal) modal.classList.add("hidden");
  }

  async handleConnectIncomeSubmit(e) {
    e.preventDefault();
    const providerId = document.getElementById("incomeProviderSelect").value;
    const amount = parseFloat(document.getElementById("incomeAmountInput").value);
    const frequency = document.getElementById("incomeFrequencySelect").value;
    const payoutDay = document.getElementById("incomeDaySelect").value;

    if (isNaN(amount) || amount <= 0) {
      if (window.showToast) window.showToast("Please enter a valid typical payout amount.", "error");
      return;
    }

    const saveBtn = document.getElementById("saveIncomeBtn");
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.textContent = "Connecting…";
    }

    try {
      const api = window.api || window.sureSavingsApi;
      const res = await api.connectIncomeSource({
        provider_id: providerId,
        typical_amount: amount,
        frequency: frequency,
        payout_day: payoutDay
      });
      if (window.showToast) {
        window.showToast(res.message || "Income source connected!", "success");
      }
      this.closeConnectIncomeModal();
      await this.loadCalendar();
    } catch (err) {
      console.error("[Calendar] Connect income source error:", err);
      if (window.showToast) window.showToast(`Failed to connect income: ${err.message}`, "error");
    } finally {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.textContent = "Connect & Recalculate";
      }
    }
  }

  // Variance Analysis Modal handlers
  async openVarianceModal() {
    const modal = document.getElementById("calVarianceModal");
    const body = document.getElementById("varianceModalBody");
    if (modal) modal.classList.remove("hidden");
    if (!body) return;

    body.innerHTML = `<div class="p-6 text-center text-xs text-stone-400">Analyzing expected vs actual variance…</div>`;

    try {
      const api = window.api || window.sureSavingsApi;
      const data = await api.getCalendarVariance(this.currentYear, this.currentMonth);
      if (!data || !data.records) {
        body.innerHTML = `<div class="p-4 text-xs text-stone-400">No variance records available for this month.</div>`;
        return;
      }

      let html = `
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 text-center">
          <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
            <span class="text-[10px] text-stone-500 uppercase font-bold">Expected Inflow</span>
            <div class="font-mono font-bold text-sm text-emerald-600">₹${Math.round(data.total_expected_income).toLocaleString()}</div>
          </div>
          <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
            <span class="text-[10px] text-stone-500 uppercase font-bold">Actual Inflow</span>
            <div class="font-mono font-bold text-sm text-emerald-600">₹${Math.round(data.total_actual_income).toLocaleString()}</div>
          </div>
          <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
            <span class="text-[10px] text-stone-500 uppercase font-bold">Expected Outflow</span>
            <div class="font-mono font-bold text-sm text-rose-500">₹${Math.round(data.total_expected_outflow).toLocaleString()}</div>
          </div>
          <div class="p-2.5 rounded-xl border" style="background: var(--surface-sunken); border-color: var(--border-default)">
            <span class="text-[10px] text-stone-500 uppercase font-bold">Actual Outflow</span>
            <div class="font-mono font-bold text-sm text-rose-500">₹${Math.round(data.total_actual_outflow).toLocaleString()}</div>
          </div>
        </div>

        <div class="space-y-2">
          <h4 class="font-bold text-xs" style="color: var(--text-primary)">Variance Telemetry (${data.records.length} items tracked)</h4>
      `;

      if (data.records.length === 0) {
        html += `<p class="text-xs text-stone-400 py-3">No scheduled items to compare against settled ledger entries this cycle.</p>`;
      } else {
        data.records.forEach((rec) => {
          const isSettled = rec.status === "SETTLED";
          const isDelayed = rec.status === "DELAYED";
          const badgeColor = isSettled ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300" : (isDelayed ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300" : "bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300");
          html += `
            <div class="p-3 rounded-xl border flex items-center justify-between gap-3 text-xs" style="background: var(--surface-sunken); border-color: var(--border-default)">
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-bold" style="color: var(--text-primary)">${rec.title}</span>
                  <span class="px-1.5 py-0.5 rounded text-[9px] font-bold ${badgeColor}">${rec.status}</span>
                </div>
                <p class="text-[11px] text-stone-500 mt-0.5">${rec.explanation}</p>
              </div>
              <div class="text-right font-mono">
                <div class="font-bold ${rec.amount_variance >= 0 ? 'text-emerald-600' : 'text-rose-500'}">
                  ${rec.amount_variance >= 0 ? '+' : ''}₹${Math.round(rec.amount_variance).toLocaleString()}
                </div>
                ${rec.timing_delay_days !== 0 ? `<div class="text-[10px] text-stone-400">${rec.timing_delay_days > 0 ? '+' : ''}${rec.timing_delay_days}d delay</div>` : ''}
              </div>
            </div>
          `;
        });
      }

      html += `</div>`;
      body.innerHTML = html;
    } catch (err) {
      console.error("[Calendar] Variance error:", err);
      body.innerHTML = `<div class="p-4 text-xs text-rose-500">Failed to calculate variance: ${err.message}</div>`;
    }
  }

  closeVarianceModal() {
    const modal = document.getElementById("calVarianceModal");
    if (modal) modal.classList.add("hidden");
  }

  // Export Calendar (CSV / JSON)
  async exportCalendar(format = "csv") {
    try {
      const api = window.api || window.sureSavingsApi;
      const res = await api.exportCalendar(this.currentYear, this.currentMonth, format);
      if (!res || !res.data) throw new Error("Empty export response");

      let blob;
      if (format === "csv") {
        blob = new Blob([res.data], { type: "text/csv;charset=utf-8;" });
      } else {
        blob = new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" });
      }

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", res.filename || `calendar_${this.currentYear}_${this.currentMonth}.${format}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      if (window.showToast) {
        window.showToast(`Downloaded ${format.toUpperCase()} export successfully.`, "success");
      }
    } catch (err) {
      console.error("[Calendar] Export error:", err);
      if (window.showToast) window.showToast(`Export failed: ${err.message}`, "error");
    }
  }

  async deleteEvent(eventId) {
    if (!confirm("Are you sure you want to remove this event from your calendar? All projections will recalculate.")) {
      return;
    }

    try {
      await window.api.deleteCalendarEvent(eventId);
      if (window.showToast) window.showToast("Event removed and financial engine recalculated.", "success");
      await this.loadCalendar();
      if (this.selectedDate) {
        await this.selectDay(this.selectedDate);
      }
    } catch (err) {
      console.error("[Calendar] Event deletion error:", err);
      if (window.showToast) window.showToast(`Failed to delete event: ${err.message}`, "error");
    }
  }

  async syncCalendar() {
    const syncIcon = document.getElementById("calSyncIcon");
    const syncBtn = document.getElementById("calSyncBtn");
    if (syncIcon) syncIcon.classList.add("animate-spin");
    if (syncBtn) syncBtn.disabled = true;

    try {
      const data = await window.api.recalculateCalendar(this.currentYear, this.currentMonth);
      this.calendarData = data;
      this.renderHeader();
      this.renderSummaryStats();
      this.renderCalendarGrid();
      if (this.selectedDate) {
        await this.selectDay(this.selectedDate);
      }
      if (window.showToast) {
        window.showToast("Calendar synchronized and universal cash-flow projections recalculated.", "success");
      }
    } catch (err) {
      console.error("[Calendar] Sync error:", err);
      if (window.showToast) window.showToast("Failed to synchronize calendar feeds.", "error");
    } finally {
      if (syncIcon) syncIcon.classList.remove("animate-spin");
      if (syncBtn) syncBtn.disabled = false;
    }
  }
}

// Global initialization
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("calendarGridContainer")) {
    window.calendarController = new FinancialCalendarController();
    window.calendarController.init();
  }
});
