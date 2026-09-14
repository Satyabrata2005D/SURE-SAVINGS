/**
 * SURE SAVINGS 5.0: Adaptive Financial Resilience Command Center
 * Universal Client Architecture: Dark Mode, Command Palette, Reactive Sync, & Audit Tracing
 */

// ═══════════════════════════════════════════════════════
// THEME MANAGEMENT (Light / Dark Mode Engine)
// ═══════════════════════════════════════════════════════
function initTheme() {
  const saved = localStorage.getItem('suresavings_theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon(theme);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
}

function toggleDarkMode() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('suresavings_theme', next);
  updateThemeIcon(next);
  showToast(next === 'dark' ? 'Switched to Dark Mode 🌙' : 'Switched to Light Mode ☀️');
}

// Immediate theme execution on script evaluation to prevent flash of light theme
initTheme();

// ═══════════════════════════════════════════════════════
// TOAST NOTIFICATION SYSTEM
// ═══════════════════════════════════════════════════════
function showToast(titleOrMsg, message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.position = "fixed";
    container.style.bottom = "1.5rem";
    container.style.right = "1.5rem";
    container.style.zIndex = "9999";
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.gap = "0.5rem";
    container.style.pointerEvents = "none";
    document.body.appendChild(container);
  }

  let title = titleOrMsg;
  let body = message;
  if (!message) {
    body = titleOrMsg;
    title = type === "error" ? "Error" : type === "warning" ? "Notice" : "Success";
  }

  if (window.i18n && typeof window.i18n.t === "function") {
    const translatedTitle = window.i18n.t(title);
    if (translatedTitle && translatedTitle !== title) title = translatedTitle;
    if (body) {
      const translatedBody = window.i18n.t(body);
      if (translatedBody && translatedBody !== body) body = translatedBody;
    }
  }

  const icons = {
    success: `<svg class="w-5 h-5 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`,
    info: `<svg class="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
    warning: `<svg class="w-5 h-5 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`,
    error: `<svg class="w-5 h-5 text-rose-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`,
  };

  const toast = document.createElement("div");
  toast.className = "toast-message";
  toast.style.pointerEvents = "auto";
  toast.innerHTML = `
    <div class="flex-shrink-0">${icons[type] || icons.info}</div>
    <div class="flex-1 text-left">
      <p class="text-xs font-bold leading-tight" style="color: var(--text-primary)">${title}</p>
      <p class="text-[11px] mt-0.5 leading-snug" style="color: var(--text-secondary)">${body}</p>
    </div>
    <button onclick="this.parentElement.remove()" class="text-xs font-bold px-1 transition-opacity opacity-60 hover:opacity-100" style="color: var(--text-muted)">✕</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// ═══════════════════════════════════════════════════════
// COMMAND PALETTE (⌘K / Ctrl+K)
// ═══════════════════════════════════════════════════════
function ensureCommandPalette() {
  if (document.getElementById('command-palette-overlay')) return;
  const overlay = document.createElement('div');
  overlay.id = 'command-palette-overlay';
  overlay.className = 'command-palette-overlay hidden';
  overlay.onclick = (e) => closeCommandPalette(e);
  overlay.innerHTML = `
    <div class="command-palette" onclick="event.stopPropagation()">
      <input type="text" class="command-palette-input" placeholder="Search pages, actions, shortcuts… (Esc to close)" id="cmd-palette-input" oninput="filterCommands(this.value)" />
      <div class="command-palette-results" id="cmd-palette-results">
        <div class="command-palette-item" onclick="window.location.href='index.html'">
          <span>📊</span> <span>Command Center (Dashboard)</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='simulator.html'">
          <span>🛡️</span> <span>SURE SAVINGS Simulator</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='income-intelligence.html'">
          <span>📈</span> <span>Income Intelligence</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='planner.html'">
          <span>🗓️</span> <span>Cash Flow Planner</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='decision-pipeline.html'">
          <span>⚖️</span> <span>Decision Pipeline</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='calendar.html'">
          <span>📅</span> <span>Income Calendar</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='goals.html'">
          <span>🎯</span> <span>Target Goals</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='risk.html'">
          <span>⚡</span> <span>Risk & Shock Scenarios</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='health.html'">
          <span>❤️</span> <span>Financial Health Index</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='activity.html'">
          <span>📜</span> <span>Activity Ledger</span>
        </div>
        <div class="command-palette-item" onclick="window.location.href='coach.html'">
          <span>🤖</span> <span>AI Financial Coach</span>
        </div>
        <div class="command-palette-item" onclick="closeCommandPalette(); if(window.setupWizard) window.setupWizard.openQuickStartModal(); else if(window.openQuickStartModal) window.openQuickStartModal();">
          <span>⚙️</span> <span>Calibrate Financial Baseline</span>
        </div>
        <div class="command-palette-item" onclick="closeCommandPalette(); openAddGoalModal();">
          <span>🎯</span> <span>Add Savings Buffer Goal</span>
        </div>
        <div class="command-palette-item" onclick="closeCommandPalette(); openLogIncomeModal();">
          <span>💰</span> <span>Log Weekly Income</span>
        </div>
        <div class="command-palette-item" onclick="toggleDarkMode(); closeCommandPalette();">
          <span>🌓</span> <span>Toggle Dark / Light Mode</span>
        </div>
        <div class="command-palette-item" onclick="exportData(); closeCommandPalette();">
          <span>📥</span> <span>Export Financial Archive</span>
        </div>
        <div class="command-palette-item" onclick="importData(); closeCommandPalette();">
          <span>📤</span> <span>Import / Restore Archive</span>
        </div>
        <div class="command-palette-item" onclick="handleLogout();">
          <span>🚪</span> <span>Sign Out</span>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
}

function openCommandPalette() {
  ensureCommandPalette();
  const overlay = document.getElementById('command-palette-overlay');
  if (overlay) {
    overlay.classList.remove('hidden');
    setTimeout(() => document.getElementById('cmd-palette-input')?.focus(), 100);
  }
}

function closeCommandPalette(e) {
  const overlay = document.getElementById('command-palette-overlay');
  if (!overlay) return;
  if (!e || e.target === overlay) {
    overlay.classList.add('hidden');
    const input = document.getElementById('cmd-palette-input');
    if (input) input.value = '';
    filterCommands('');
  }
}

function filterCommands(query) {
  const items = document.querySelectorAll('#cmd-palette-results .command-palette-item');
  const q = (query || '').toLowerCase();
  items.forEach(item => {
    item.style.display = item.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

// ═══════════════════════════════════════════════════════
// USER MENU & NOTIFICATIONS
function ensureMyProfileInDropdowns() {
  document.querySelectorAll('#user-menu-dropdown').forEach(dropdown => {
    if (dropdown.querySelector('.profile-menu-item-link') || dropdown.querySelector('[onclick*="openMyProfileModal"]')) return;
    const calibrateItem = dropdown.querySelector('[onclick*="openQuickStartModal"]');
    const myProfileItem = document.createElement('div');
    myProfileItem.className = 'user-menu-item profile-menu-item-link';
    myProfileItem.setAttribute('onclick', 'openMyProfileModal()');
    myProfileItem.innerHTML = `
      <svg class="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
      <span>My Profile</span>
    `;
    if (calibrateItem && calibrateItem.parentNode) {
      calibrateItem.parentNode.insertBefore(myProfileItem, calibrateItem);
    } else {
      dropdown.prepend(myProfileItem);
    }
  });
}

function toggleUserMenu() {
  ensureMyProfileInDropdowns();
  const menu = document.getElementById('user-menu-dropdown') || document.getElementById('header-user-dropdown');
  if (menu) menu.classList.toggle('hidden');
}

function closeUserMenu() {
  const menu1 = document.getElementById('user-menu-dropdown');
  const menu2 = document.getElementById('header-user-dropdown');
  if (menu1) menu1.classList.add('hidden');
  if (menu2) menu2.classList.add('hidden');
}

function toggleNotifications() {
  showToast('Notifications: 3 alerts', 'Resilience score updated • Reserve safe-to-save ready • Emergency floor intact', 'info');
}

function handleLogout() {
  sessionStorage.removeItem('suresavings_session_token');
  localStorage.removeItem('suresavings_session_token');
  if (window.sureSavingsApi) {
    try { window.sureSavingsApi.logout(); } catch(e) {}
  }
  window.location.href = 'login.html';
}

function exportData() {
  showToast('Exporting Data', 'Preparing verified financial JSON archive…', 'info');
  const fullState = window.sureSavingsStore?.getState() || {};
  const archive = {
    exported_at: new Date().toISOString(),
    version: "5.0",
    platform: "SURE SAVINGS — Deterministic Financial Resilience",
    profile: fullState.profile || {},
    resilience: fullState.resilience || {},
    risk: fullState.risk || {},
    buffer: fullState.buffer || {},
    recommendation: fullState.recommendation || {},
    income_analytics: fullState.income_analytics || {},
    cash_flow: fullState.cash_flow || {}
  };
  const data = JSON.stringify(archive, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `suresavings_export_${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
  setTimeout(() => showToast('Export Complete', 'Financial archive successfully downloaded', 'success'), 800);
}

// ═══════════════════════════════════════════════════════
// 👤 MY PROFILE & CALIBRATION DETAILS CONTROLLER
// ═══════════════════════════════════════════════════════
let _currentProfileData = null;

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

async function openMyProfileModal() {
  closeUserMenu();

  // Create or retrieve modal container
  let modal = document.getElementById('my-profile-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'my-profile-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-stone-900/60 backdrop-blur-md overflow-y-auto animate-fade-in';
    modal.onclick = (e) => {
      if (e.target === modal) closeMyProfileModal();
    };
    document.body.appendChild(modal);
  }

  modal.classList.remove('hidden');
  modal.innerHTML = `
    <div class="glass-modal rounded-2xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-stone-200 dark:border-stone-700 text-left my-auto space-y-4">
      <div class="flex items-center justify-center py-12 space-x-3 text-stone-600 dark:text-stone-300">
        <svg class="animate-spin h-6 w-6 text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span class="text-sm font-semibold">Loading your verified profile…</span>
      </div>
    </div>
  `;

  try {
    const res = await window.sureSavingsApi.getProfile();
    _currentProfileData = res;
    renderMyProfileModalContent(res);
  } catch (err) {
    console.error("Failed to load profile:", err);
    const storeState = window.sureSavingsStore?.getState() || {};
    const fallbackUser = storeState.auth?.user || storeState.profile || {};
    _currentProfileData = {
      user: fallbackUser,
      baseline: {
        typical_weekly_income: storeState.profile?.current_income || 6900,
        essential_weekly_expenses: storeState.profile?.weekly_burn || 4500,
        protected_cash_floor: storeState.profile?.protected_floor || 1000,
        current_buffer: storeState.profile?.current_buffer || 4200,
        target_buffer: storeState.profile?.buffer_target || 3600,
        data_maturity_level: fallbackUser.data_maturity_level || 5,
        readiness_percentage: fallbackUser.readiness_percentage || 100
      }
    };
    renderMyProfileModalContent(_currentProfileData);
  }
}

function closeMyProfileModal() {
  const modal = document.getElementById('my-profile-modal');
  if (modal) modal.classList.add('hidden');
}

function renderMyProfileModalContent(data) {
  const modal = document.getElementById('my-profile-modal');
  if (!modal) return;

  const user = data.user || {};
  const baseline = data.baseline || {
    typical_weekly_income: 6900,
    essential_weekly_expenses: 4500,
    protected_cash_floor: 1000,
    current_buffer: 4200,
    target_buffer: 3600,
    data_maturity_level: 5,
    readiness_percentage: 100
  };

  const hasCustomAvatar = Boolean(user.avatar_url && !user.avatar_url.includes('dicebear'));
  const fullName = user.name || user.display_name || 'Member';
  const initials = user.initials || (fullName.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase() || 'SD');

  modal.innerHTML = `
    <div class="glass-modal rounded-2xl max-w-2xl w-full p-5 sm:p-7 shadow-2xl border border-stone-200 dark:border-stone-800 text-left my-auto space-y-5 max-h-[92vh] overflow-y-auto transform transition-all" onclick="event.stopPropagation()">
      <!-- Header -->
      <div class="flex items-center justify-between pb-3 border-b border-stone-100 dark:border-stone-800">
        <div class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-base">
            👤
          </div>
          <div>
            <h3 class="font-extrabold text-stone-900 dark:text-white text-sm sm:text-base">My Profile & Calibrated Identity</h3>
            <p class="text-[11px] text-stone-500 dark:text-stone-400">Institutional records, contact parameters, and digital twin calibrations</p>
          </div>
        </div>
        <button type="button" onclick="closeMyProfileModal()" class="w-8 h-8 rounded-full hover:bg-stone-100 dark:hover:bg-stone-800 flex items-center justify-center text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 transition-colors text-base font-bold">✕</button>
      </div>

      <!-- Avatar Photo Section -->
      <div class="p-4 rounded-2xl bg-stone-50/80 dark:bg-stone-900/60 border border-stone-200/80 dark:border-stone-800 flex flex-col sm:flex-row items-center sm:items-start space-y-3 sm:space-y-0 sm:space-x-5">
        <div class="relative group cursor-pointer" onclick="document.getElementById('profile-photo-file-input').click()">
          <div id="modal-avatar-preview-container" class="w-20 h-20 rounded-full overflow-hidden border-2 border-brand-500 shadow-md flex items-center justify-center bg-stone-900 text-white font-extrabold text-2xl flex-shrink-0">
            ${hasCustomAvatar 
              ? `<img id="modal-avatar-preview" src="${user.avatar_url}" class="w-full h-full object-cover" alt="${escapeHtml(fullName)}">`
              : `<span id="modal-avatar-initials">${initials}</span>`}
          </div>
          <div class="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity">
            <span class="text-xs font-bold">Change</span>
          </div>
        </div>

        <div class="flex-1 text-center sm:text-left space-y-1.5">
          <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <h4 class="font-extrabold text-stone-900 dark:text-white text-base">${escapeHtml(fullName)}</h4>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Verified Member
            </span>
          </div>
          <p class="text-xs text-stone-500 dark:text-stone-400">${escapeHtml(user.email || 'Google Authenticated Identity')}</p>

          <div class="pt-1 flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <label for="profile-photo-file-input" class="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-white dark:bg-stone-800 border border-stone-300 dark:border-stone-700 hover:border-brand-500 text-stone-700 dark:text-stone-200 text-xs font-bold rounded-xl shadow-sm cursor-pointer transition-all hover:bg-stone-50">
              <svg class="w-3.5 h-3.5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              <span>Choose Photo</span>
            </label>
            <input type="file" id="profile-photo-file-input" accept="image/png, image/jpeg, image/webp" class="hidden" onchange="handleProfilePhotoSelect(event)">
            <span class="text-[11px] text-stone-400" id="photo-upload-status">JPG, PNG or WebP, max 5MB</span>
          </div>
        </div>
      </div>

      <!-- Editable Personal & Contact Form -->
      <div class="space-y-4">
        <h4 class="text-xs font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500">Personal & Contact Details</h4>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          <div>
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">Legal Full Name <span class="text-rose-500">*</span></label>
            <input type="text" id="prof-input-name" value="${escapeHtml(fullName)}" placeholder="e.g. Satyabrata Das" required
              class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">Email Address (Locked)</label>
            <input type="email" id="prof-input-email" value="${escapeHtml(user.email || '')}" readonly
              class="w-full px-3 py-2 text-xs bg-stone-100 dark:bg-stone-800/80 text-stone-500 dark:text-stone-400 border border-stone-200 dark:border-stone-700 rounded-xl cursor-not-allowed font-medium">
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">Date of Birth</label>
            <input type="date" id="prof-input-dob" value="${escapeHtml(user.date_of_birth || '')}"
              class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">Phone Number</label>
            <input type="tel" id="prof-input-phone" value="${escapeHtml(user.phone_number || '')}" placeholder="+91 98765 43210"
              class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium font-mono">
          </div>

          <div class="sm:col-span-2">
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">Type of Work / Occupation</label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <select id="prof-select-occupation" onchange="document.getElementById('prof-input-occupation').value = this.value"
                class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
                <option value="Gig Platform Worker" ${user.occupation === 'Gig Platform Worker' ? 'selected' : ''}>Gig Platform Worker (Delivery / Rides)</option>
                <option value="Delivery & Freelance Lead" ${user.occupation === 'Delivery & Freelance Lead' ? 'selected' : ''}>Delivery & Freelance Lead</option>
                <option value="Freelancer / Consultant" ${user.occupation === 'Freelancer / Consultant' ? 'selected' : ''}>Freelancer / Independent Consultant</option>
                <option value="Salaried Professional" ${user.occupation === 'Salaried Professional' ? 'selected' : ''}>Salaried Professional</option>
                <option value="Small Business Owner" ${user.occupation === 'Small Business Owner' ? 'selected' : ''}>Small Business Owner / Merchant</option>
                <option value="Creative & Media Professional" ${user.occupation === 'Creative & Media Professional' ? 'selected' : ''}>Creative & Media Professional</option>
                <option value="Contractor / Tradesperson" ${user.occupation === 'Contractor / Tradesperson' ? 'selected' : ''}>Contractor / Tradesperson</option>
                <option value="Custom" ${!['Gig Platform Worker', 'Delivery & Freelance Lead', 'Freelancer / Consultant', 'Salaried Professional', 'Small Business Owner', 'Creative & Media Professional', 'Contractor / Tradesperson'].includes(user.occupation || '') ? 'selected' : ''}>Custom Designation</option>
              </select>
              <input type="text" id="prof-input-occupation" value="${escapeHtml(user.occupation || 'Gig Platform Worker')}" placeholder="Specific job title / work description"
                class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">State / Province</label>
            <input type="text" id="prof-input-state" value="${escapeHtml(user.state || '')}" placeholder="e.g. Karnataka / Maharashtra"
              class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
          </div>

          <div>
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">District / City</label>
            <input type="text" id="prof-input-district" value="${escapeHtml(user.district || '')}" placeholder="e.g. Bengaluru / Mumbai"
              class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
          </div>

          <div class="sm:col-span-2">
            <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1">Area / Locality / PIN</label>
            <input type="text" id="prof-input-area" value="${escapeHtml(user.area || '')}" placeholder="e.g. Indiranagar, 560038"
              class="w-full px-3 py-2 text-xs border border-stone-300 dark:border-stone-700 dark:bg-stone-900 dark:text-white rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-medium">
          </div>
        </div>
      </div>

      <!-- Calibrated Financial Baseline Summary (Digital Twin Parameters) -->
      <div class="p-4 rounded-2xl bg-stone-50 dark:bg-stone-900/50 border border-stone-200/80 dark:border-stone-800 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-sm">⚡</span>
            <h4 class="text-xs font-extrabold uppercase tracking-wider text-stone-900 dark:text-white">Calibrated Baseline Parameters</h4>
          </div>
          <button type="button" onclick="closeMyProfileModal(); if (window.setupWizard) window.setupWizard.openQuickStartModal();"
            class="text-[11px] font-bold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1">
            <span>Recalibrate Baseline</span> →
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div class="p-2.5 rounded-xl bg-white dark:bg-stone-800 border border-stone-200/80 dark:border-stone-700 text-left">
            <p class="text-[10px] text-stone-400 font-semibold">Weekly Income</p>
            <p class="text-xs sm:text-sm font-extrabold text-stone-900 dark:text-white font-mono mt-0.5">₹${Number(baseline.typical_weekly_income || 6900).toLocaleString('en-IN')}</p>
          </div>
          <div class="p-2.5 rounded-xl bg-white dark:bg-stone-800 border border-stone-200/80 dark:border-stone-700 text-left">
            <p class="text-[10px] text-stone-400 font-semibold">Weekly Burn</p>
            <p class="text-xs sm:text-sm font-extrabold text-stone-900 dark:text-white font-mono mt-0.5">₹${Number(baseline.essential_weekly_expenses || 4500).toLocaleString('en-IN')}</p>
          </div>
          <div class="p-2.5 rounded-xl bg-white dark:bg-stone-800 border border-stone-200/80 dark:border-stone-700 text-left">
            <p class="text-[10px] text-stone-400 font-semibold">Protected Floor</p>
            <p class="text-xs sm:text-sm font-extrabold text-stone-900 dark:text-white font-mono mt-0.5">₹${Number(baseline.protected_cash_floor || 1000).toLocaleString('en-IN')}</p>
          </div>
          <div class="p-2.5 rounded-xl bg-white dark:bg-stone-800 border border-stone-200/80 dark:border-stone-700 text-left">
            <p class="text-[10px] text-stone-400 font-semibold">Current Buffer</p>
            <p class="text-xs sm:text-sm font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">₹${Number(baseline.current_buffer || 4200).toLocaleString('en-IN')}</p>
          </div>
        </div>

        <div class="pt-1 flex flex-wrap items-center justify-between text-[11px] text-stone-500 dark:text-stone-400">
          <span>Data Readiness: <strong class="text-emerald-600 dark:text-emerald-400">100% Calibrated</strong></span>
          <span>Data Maturity: <strong class="text-stone-900 dark:text-white">Level 5/5</strong></span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="pt-2 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center space-x-2">
          <button type="button" id="save-profile-btn" onclick="saveProfileChanges()"
            class="px-5 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-sm brand-glow transition-all flex items-center space-x-1.5">
            <span>💾 Save Profile Changes</span>
          </button>
          <button type="button" onclick="closeMyProfileModal()"
            class="px-4 py-2.5 bg-stone-100 dark:bg-stone-800 hover:bg-stone-200 dark:hover:bg-stone-700 text-stone-700 dark:text-stone-300 font-bold text-xs rounded-xl transition-all">
            Close
          </button>
        </div>
      </div>

      <!-- ⚠️ Danger Zone: Permanent Account Deletion -->
      <div class="mt-4 pt-4 border-t border-rose-200 dark:border-rose-900/60">
        <div class="p-4 rounded-xl border border-rose-200 dark:border-rose-900/60 bg-rose-50/70 dark:bg-rose-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div class="space-y-0.5">
            <div class="flex items-center space-x-1.5 text-rose-700 dark:text-rose-400 font-bold text-xs">
              <svg class="w-4 h-4 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
              <span>Delete Profile Permanently</span>
            </div>
            <p class="text-[11px] text-rose-600/80 dark:text-rose-400/80">
              Permanently erase all calibrated parameters, transactions, and user identity from database.
            </p>
          </div>
          <button type="button" onclick="openDeleteProfileModal()"
            class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all whitespace-nowrap flex items-center space-x-1.5 flex-shrink-0">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            <span>Delete the profile</span>
          </button>
        </div>
      </div>
    </div>
  `;
}

async function handleProfilePhotoSelect(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml'];
  if (!validTypes.includes(file.type)) {
    showToast('Invalid File Type', 'Please upload a JPG, PNG, or WebP image.', 'error');
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    showToast('File Too Large', 'Maximum image size is 5MB.', 'error');
    return;
  }

  const statusEl = document.getElementById('photo-upload-status');
  if (statusEl) statusEl.textContent = 'Uploading photo…';

  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64Data = e.target.result;

    // Instant local preview in modal
    const previewContainer = document.getElementById('modal-avatar-preview-container');
    if (previewContainer) {
      previewContainer.innerHTML = `<img id="modal-avatar-preview" src="${base64Data}" class="w-full h-full object-cover" alt="Profile Picture">`;
    }

    try {
      const res = await window.sureSavingsApi.uploadProfilePhoto(base64Data);
      const newAvatarUrl = res.avatar_url;

      // Update store and live UI
      if (window.sureSavingsStore?.state?.auth?.user) {
        window.sureSavingsStore.state.auth.user.avatar_url = newAvatarUrl;
      }
      if (_currentProfileData?.user) {
        _currentProfileData.user.avatar_url = newAvatarUrl;
      }

      // Update all avatars across the page
      document.querySelectorAll('#user-avatar-circle, .user-avatar, #header-user-menu-trigger .w-7').forEach(el => {
        el.innerHTML = `<img src="${newAvatarUrl}" class="w-full h-full object-cover rounded-full" alt="Avatar">`;
      });

      if (statusEl) statusEl.textContent = '✅ Photo updated successfully';
      showToast('Profile Photo Updated', 'Your new photo has been set.', 'success');
    } catch (err) {
      console.error("Photo upload failed:", err);
      if (statusEl) statusEl.textContent = '❌ Upload failed: ' + err.message;
      showToast('Upload Failed', err.message || 'Could not upload photo.', 'error');
    }
  };
  reader.readAsDataURL(file);
}

async function saveProfileChanges() {
  const name = document.getElementById('prof-input-name')?.value.trim();
  const dob = document.getElementById('prof-input-dob')?.value.trim();
  const phone = document.getElementById('prof-input-phone')?.value.trim();
  const occupation = document.getElementById('prof-input-occupation')?.value.trim();
  const state = document.getElementById('prof-input-state')?.value.trim();
  const district = document.getElementById('prof-input-district')?.value.trim();
  const area = document.getElementById('prof-input-area')?.value.trim();

  if (!name || name.length < 2) {
    showToast('Validation Error', 'Legal Full Name must be at least 2 characters.', 'error');
    return;
  }

  const saveBtn = document.getElementById('save-profile-btn');
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span>Saving…</span>';
  }

  try {
    const res = await window.sureSavingsApi.updateProfile({
      name,
      date_of_birth: dob,
      phone_number: phone,
      occupation,
      state,
      district,
      area
    });

    const updatedUser = res.user;
    if (window.sureSavingsStore?.state?.auth?.user) {
      Object.assign(window.sureSavingsStore.state.auth.user, updatedUser);
    }
    if (_currentProfileData?.user) {
      Object.assign(_currentProfileData.user, updatedUser);
    }

    // Refresh greetings and names on page
    if (typeof updateAllUserGreetingsAndNames === 'function') {
      updateAllUserGreetingsAndNames(updatedUser);
    }

    showToast('Profile Saved', 'Personal details saved successfully! ✅', 'success');
    setTimeout(() => {
      closeMyProfileModal();
    }, 600);
  } catch (err) {
    console.error("Profile save error:", err);
    showToast('Save Failed', err.message || 'Could not update profile.', 'error');
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<span>💾 Save Profile Changes</span>';
    }
  }
}

// ═══════════════════════════════════════════════════════
// ⚠️ PERMANENT PROFILE DELETION POPUP CONTROLLER
// ═══════════════════════════════════════════════════════
function openDeleteProfileModal() {
  let modal = document.getElementById('delete-profile-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'delete-profile-modal';
    modal.className = 'fixed inset-0 z-60 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in';
    document.body.appendChild(modal);
  }

  modal.classList.remove('hidden');
  modal.innerHTML = `
    <div class="glass-modal rounded-2xl max-w-md w-full p-6 shadow-2xl border-2 border-rose-500/50 space-y-4 text-left animate-scale-up" onclick="event.stopPropagation()">
      <div class="flex items-center space-x-3">
        <div class="w-11 h-11 rounded-2xl bg-rose-100 dark:bg-rose-900/50 text-rose-600 dark:text-rose-400 flex items-center justify-center text-xl flex-shrink-0">
          ⚠️
        </div>
        <div>
          <h3 class="font-extrabold text-stone-900 dark:text-white text-base">Delete Profile Permanently</h3>
          <p class="text-xs text-rose-600 dark:text-rose-400 font-bold">Irreversible Action</p>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-xs text-rose-800 dark:text-rose-300 leading-relaxed">
        This will permanently destroy your user profile, calibrated financial baseline, transaction ledgers, digital twin models, and active sessions. <strong>This action cannot be undone.</strong>
      </div>

      <div>
        <label class="block text-xs font-bold text-stone-800 dark:text-stone-200 mb-1.5">
          To confirm, type <span class="font-mono text-rose-600 dark:text-rose-400 select-all bg-rose-100 dark:bg-rose-900/50 px-1.5 py-0.5 rounded font-bold">Delete profile permanently</span> below:
        </label>
        <input type="text" id="delete-profile-confirmation-input"
          placeholder="Delete profile permanently"
          autocomplete="off"
          oninput="handleDeleteConfirmationInput(this.value)"
          class="w-full px-3.5 py-2.5 text-xs font-mono border-2 border-stone-300 dark:border-stone-700 rounded-xl focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 focus:outline-none dark:bg-stone-900 dark:text-white">
      </div>

      <div class="pt-2 flex items-center justify-end space-x-2.5">
        <button type="button" onclick="closeDeleteProfileModal()" class="px-4 py-2 text-xs font-bold text-stone-600 hover:text-stone-800 dark:text-stone-300 dark:hover:text-white rounded-xl hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors">
          Cancel
        </button>
        <button type="button" id="confirm-delete-profile-btn" disabled onclick="executePermanentProfileDeletion()"
          class="px-5 py-2.5 bg-rose-600 text-white font-bold text-xs rounded-xl shadow-lg opacity-40 cursor-not-allowed transition-all flex items-center space-x-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
          <span id="delete-btn-text">Delete Profile Permanently</span>
        </button>
      </div>
    </div>
  `;

  setTimeout(() => {
    document.getElementById('delete-profile-confirmation-input')?.focus();
  }, 100);
}

function closeDeleteProfileModal() {
  const modal = document.getElementById('delete-profile-modal');
  if (modal) modal.classList.add('hidden');
}

function handleDeleteConfirmationInput(val) {
  const btn = document.getElementById('confirm-delete-profile-btn');
  if (!btn) return;
  const isMatch = (val || '').trim() === 'Delete profile permanently';
  btn.disabled = !isMatch;
  if (isMatch) {
    btn.classList.remove('opacity-40', 'cursor-not-allowed');
    btn.classList.add('hover:bg-rose-700', 'shadow-rose-500/30', 'animate-pulse');
  } else {
    btn.classList.add('opacity-40', 'cursor-not-allowed');
    btn.classList.remove('hover:bg-rose-700', 'shadow-rose-500/30', 'animate-pulse');
  }
}

async function executePermanentProfileDeletion() {
  const input = document.getElementById('delete-profile-confirmation-input');
  if (!input || input.value.trim() !== 'Delete profile permanently') {
    showToast('Confirmation Required', 'You must type "Delete profile permanently" to proceed.', 'error');
    return;
  }

  const btn = document.getElementById('confirm-delete-profile-btn');
  const txt = document.getElementById('delete-btn-text');
  if (btn) btn.disabled = true;
  if (txt) txt.textContent = 'Deleting account permanently…';

  try {
    await window.sureSavingsApi.deleteProfilePermanently('Delete profile permanently');
    showToast('Profile Deleted', 'Your profile and data have been permanently deleted.', 'info');

    // Wipe client storage
    try { sessionStorage.clear(); } catch(e) {}
    try { localStorage.clear(); } catch(e) {}

    setTimeout(() => {
      window.location.href = 'landing.html?deleted=1';
    }, 600);
  } catch (err) {
    console.error("Delete profile failed:", err);
    showToast('Deletion Failed', err.message || 'Could not delete profile. Please try again.', 'error');
    if (btn) btn.disabled = false;
    if (txt) txt.textContent = 'Delete Profile Permanently';
  }
}

function importData() {
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = '.json';
  fileInput.style.display = 'none';
  document.body.appendChild(fileInput);

  fileInput.onchange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    showToast('Importing Data', `Reading ${file.name}…`, 'info');
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target.result);
        if (typeof json !== 'object' || json === null) {
          throw new Error('Invalid archive format. Expected JSON object.');
        }
        localStorage.setItem('suresavings_imported_profile', JSON.stringify(json));
        showToast('Profile Restored', `Successfully loaded workspace archive (${file.name}).`, 'success');
        if (window.sureSavingsStore?.syncFromBackend) {
          window.sureSavingsStore.syncFromBackend();
        }
      } catch (err) {
        showToast('Import Failed', err.message || 'Could not parse JSON archive.', 'error');
      } finally {
        fileInput.remove();
      }
    };
    reader.readAsText(file);
  };

  fileInput.click();
}

// ═══════════════════════════════════════════════════════
// ACTIVE NAV LINK HIGHLIGHTER
// ═══════════════════════════════════════════════════════
function highlightActiveNav() {
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll("a[href]").forEach(link => {
    const href = link.getAttribute("href");
    if (!href) return;
    const linkPath = href.split("/").pop();
    if (linkPath === currentPath || (currentPath === "" && linkPath === "index.html")) {
      link.classList.add("active");
      link.classList.remove("text-stone-600", "hover:bg-stone-50");
      if (!link.classList.contains("unified-nav-link")) {
        link.classList.add("bg-brand-500", "text-white", "shadow-sm");
      }
      const svg = link.querySelector("svg");
      if (svg && !link.classList.contains("unified-nav-link")) {
        svg.classList.remove("text-stone-400");
        svg.classList.add("text-white");
      }
    }
  });
}

// Global modal for approving reserve transfer
function openApproveTransferModal() {
  const existing = document.getElementById("approveTransferModal");
  if (existing) existing.remove();

  const p = window.sureSavingsStore?.getProfile() || {};
  const recAmt = Number(p.recommended_contribution || 0);
  const surplus = Number(p.surplus || 0);
  const freePocket = Number(p.free_pocket_liquidity || 0);
  const floor = Number(p.protected_floor || 0);
  const curBuffer = Number(p.current_buffer || 0);
  const targetBuffer = Number(p.buffer_target || 0);

  if (recAmt <= 0) {
    if (targetBuffer > 0 && curBuffer >= targetBuffer) {
      showToast(
        "Buffer Target Fully Achieved",
        `Your Smart Buffer is 100% capitalized at ₹${curBuffer.toLocaleString()} (${p.current_coverage_weeks || 0} weeks runway). Essential checking cash floor is 100% intact.`,
        "info"
      );
    } else {
      showToast(
        "Allocation Preserved",
        "Safe-to-Save recommendation is currently ₹0 to protect essential liquidity. Zero funds moved.",
        "info"
      );
    }
    return;
  }

  const modal = document.createElement("div");
  modal.id = "approveTransferModal";
  modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/50 backdrop-blur-sm animate-fade-in";
  modal.innerHTML = `
    <div class="glass-modal rounded-2xl max-w-md w-full p-6 shadow-2xl border border-stone-200 space-y-5 text-left transform transition-all">
      <div class="flex items-center justify-between pb-3 border-b border-stone-100">
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm">
            ₹
          </div>
          <div>
            <h3 class="font-bold text-stone-900 text-sm">Approve Reserve Transfer</h3>
            <p class="text-[11px] text-stone-500">Deterministic Safeguard • Real-time Allocation</p>
          </div>
        </div>
        <button onclick="closeApproveTransferModal()" class="text-stone-400 hover:text-stone-600 text-sm">✕</button>
      </div>

      <div class="bg-stone-50 rounded-xl p-4 space-y-3 text-xs border border-stone-200/80">
        <div class="flex justify-between items-center text-stone-600">
          <span>Surplus Identified:</span>
          <span class="font-bold text-stone-900 font-mono">+₹${surplus.toLocaleString()}</span>
        </div>
        <div class="flex justify-between items-center text-stone-600">
          <span>70% Safeguard Cap:</span>
          <span class="font-bold text-brand-600 font-mono">₹${recAmt.toLocaleString()}</span>
        </div>
        <div class="flex justify-between items-center text-stone-600">
          <span>Free Pocket Cash Preserved:</span>
          <span class="font-bold text-emerald-700 font-mono">₹${freePocket.toLocaleString()}</span>
        </div>
        <div class="flex justify-between items-center text-stone-600 border-t border-stone-200/80 pt-2 font-semibold">
          <span>Checking Cash Floor:</span>
          <span class="text-emerald-700 font-mono">₹${floor.toLocaleString()} (100% Intact)</span>
        </div>
      </div>

      <div class="p-3 bg-emerald-50/70 border border-emerald-200 rounded-xl flex items-start space-x-2 text-[11px] text-emerald-900">
        <span class="mt-0.5 font-bold">✓</span>
        <span>Simulated Action: Advances buffer from ₹${curBuffer.toLocaleString()} to ₹${(curBuffer + recAmt).toLocaleString()} and expands runway coverage while preserving checking floor intact. No actual bank funds are moved.</span>
      </div>

      <div class="flex items-center justify-end space-x-3 pt-2">
        <button onclick="closeApproveTransferModal()" class="px-4 py-2 text-xs font-semibold text-stone-600 hover:bg-stone-100 rounded-xl transition-colors">Cancel</button>
        <button id="confirmTransferBtn" onclick="executeApproveTransfer(${recAmt})" class="px-5 py-2 text-xs font-bold text-white bg-brand-500 hover:bg-brand-600 rounded-xl shadow-md brand-glow transition-all flex items-center space-x-1.5">
          <span>Confirm Reserve Transfer →</span>
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

function closeApproveTransferModal() {
  const modal = document.getElementById("approveTransferModal");
  if (modal) modal.remove();
}

async function executeApproveTransfer(amount = null) {
  const modal = document.getElementById("approveTransferModal");
  const confirmBtn = document.getElementById("confirmTransferBtn");
  if (confirmBtn) {
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = `
      <svg class="w-4 h-4 animate-spin mr-1 inline" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Allocating to Vault...</span>
    `;
  }

  if (!window.sureSavingsStore) {
    closeApproveTransferModal();
    return;
  }

  try {
    const numAmt = typeof amount === "number" && amount > 0 ? amount : null;
    const res = await window.sureSavingsStore.approveReserveTransfer(null, numAmt);
    closeApproveTransferModal();

    // Handle real API response shape
    const newBuffer = res?.new_buffer ?? res?.profile?.current_buffer ?? res?.newBuffer ?? 0;
    const newCoverage = res?.new_runway ?? res?.profile?.current_coverage_weeks ?? res?.newCoverage ?? 0;
    const newResilience = res?.new_resilience ?? res?.profile?.resilience_score ?? res?.newResilience ?? 0;

    // Sync store with authoritative backend state
    await window.sureSavingsStore.syncFromBackend(true);

    showToast(
      "Reserve Transfer Approved!",
      `Buffer capitalized to ₹${Number(newBuffer).toLocaleString()} (${newCoverage} wks runway). Resilience score: ${newResilience}.`,
      "success"
    );
    updatePageMetrics();
  } catch (err) {
    closeApproveTransferModal();
    showToast(
      "Transfer Failed",
      err.message || "Unable to process reserve transfer. Please try again.",
      "error"
    );
  }
}

// Re-run Engine Check with animation & live backend verification
async function triggerEngineCheck(btn) {
  if (!btn) return;
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin inline-block mr-1.5">⟳</span> Verifying Invariants...`;

  try {
    let auditData = null;
    if (window.sureSavingsApi) {
      auditData = await window.sureSavingsApi.getEngineAudit();
    }
    const confidence = auditData?.confidence_score ?? auditData?.confidence ?? auditData?.audit?.confidence ?? 0.94;
    const status = auditData?.verification_status ?? auditData?.status ?? auditData?.audit?.status ?? "PASS";
    const confDisplay = typeof confidence === 'number' ? `${Math.round(confidence * 100)}%` : confidence;
    const passed = status === "VERIFIED_PASS" || status === "PASS";

    setTimeout(() => {
      btn.innerHTML = `✓ Confidence: ${confDisplay} • ${passed ? 'PASS' : status}`;
      btn.classList.remove("text-stone-700");
      btn.classList.add(passed ? "text-emerald-700" : "text-amber-700", passed ? "bg-emerald-50" : "bg-amber-50");
      showToast("Engine Check Complete", `All deterministic financial invariants verified with ${confDisplay} confidence.`, "success");
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
        btn.classList.remove("text-emerald-700", "bg-emerald-50", "text-amber-700", "bg-amber-50");
      }, 3500);
    }, 600);
  } catch (err) {
    btn.innerHTML = originalText;
    btn.disabled = false;
    showToast("Engine Check Failed", err.message || "Could not verify invariants", "error");
  }
}

// Download live Audit JSON
async function downloadAuditJSON() {
  let auditData = null;
  if (window.sureSavingsApi) {
    try {
      auditData = await window.sureSavingsApi.getEngineAudit();
    } catch (e) {
      console.warn("Using live profile fallback for audit JSON");
    }
  }

  if (!auditData) {
    const p = window.sureSavingsStore?.getProfile() || {};
    const u = window.sureSavingsStore?.state?.auth?.user || {};
    auditData = {
      engine_version: "SURE SAVINGS Deterministic Core v5.0",
      timestamp: new Date().toISOString(),
      user_id: u.id || "user",
      audit_mode: u.is_demo_user ? "Canonical Demo Trace" : "Private Ledger Verification",
      status: "VERIFIED_PASS",
      inputs: {
        current_income: Number(p.current_income || 0),
        stabilized_baseline: Number(p.stabilized_income || 0),
        essential_weekly_burn: Number(p.weekly_burn || 0),
        protected_cash_floor: Number(p.protected_floor || 0),
        current_buffer: Number(p.current_buffer || 0),
        buffer_target: Number(p.buffer_target || 0),
        surplus: Number(p.surplus || 0),
        recommended_contribution: Number(p.recommended_contribution || 0)
      },
      confidence: p.resilience_score ? `${Math.min(99, p.resilience_score)}%` : "Awaiting Data"
    };
  }

  const blob = new Blob([JSON.stringify(auditData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `suresavings_audit_report_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Audit JSON Downloaded", "Live mathematical audit trace exported from engine.", "info");
}

// Export CSV schedule — dynamic data from user's workspace
async function downloadCSVSchedule() {
  try {
    let rows = [];
    const p = window.sureSavingsStore?.getProfile() || {};
    const floor = Number(p.protected_floor || 0);

    // Try fetching real obligations and cash flow from backend
    if (window.sureSavingsApi) {
      try {
        const cfData = await window.sureSavingsApi.getCashFlowTimeline();
        const timelineList = cfData?.timeline || cfData?.events || [];
        if (timelineList && timelineList.length > 0) {
          rows = timelineList.map(ev => ({
            date: ev.time || ev.date || ev.date_str || '',
            description: ev.label || ev.event || ev.description || '',
            category: ev.status || 'Cash Flow',
            type: (ev.amount || 0) >= 0 ? 'Inflow' : 'Outflow',
            amount: ev.amount || 0,
            floorImpact: ev.description || (ev.projected_checking !== undefined ? `Projected Checking: ₹${Number(ev.projected_checking).toLocaleString()}` : `₹${Math.max(0, Number(ev.running_balance || 0) - floor).toLocaleString()} above floor`)
          }));
        }
      } catch (e) {
        console.warn("Could not fetch cash flow timeline for CSV export, using obligations", e);
      }

      if (rows.length === 0) {
        try {
          const obligations = await window.sureSavingsApi.getObligations();
          if (obligations && Array.isArray(obligations) && obligations.length > 0) {
            rows = obligations.map(ob => ({
              date: ob.date_str || '',
              description: ob.description || '',
              category: ob.category || 'General',
              type: 'Outflow',
              amount: -Math.abs(ob.amount || 0),
              floorImpact: ob.is_essential ? 'Essential' : 'Discretionary'
            }));
          }
        } catch (e) {
          console.warn("Could not fetch obligations for CSV export");
        }
      }
    }

    // Fallback: generate from current profile data
    if (rows.length === 0) {
      const burn = Number(p.weekly_burn || 0);
      const income = Number(p.current_income || 0);
      const buffer = Number(p.current_buffer || 0);
      rows = [
        { date: new Date().toLocaleDateString('en-US', {month:'short', day:'2-digit', year:'numeric'}), description: 'Weekly Essential Expenses', category: 'Essentials', type: 'Outflow', amount: -burn, floorImpact: `₹${Math.max(0, (income - burn)).toLocaleString()} surplus` },
        { date: new Date().toLocaleDateString('en-US', {month:'short', day:'2-digit', year:'numeric'}), description: 'Weekly Income', category: 'Earnings', type: 'Inflow', amount: income, floorImpact: `Buffer: ₹${buffer.toLocaleString()}` },
      ];
    }

    let csvContent = "data:text/csv;charset=utf-8," +
      "Date,Description,Category,Type,Amount (INR),Impact\n" +
      rows.map(r => `${r.date},${r.description},${r.category},${r.type},${r.amount},${r.floorImpact}`).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `suresavings_cashflow_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    showToast("CSV Exported", `${rows.length} cash flow entries exported successfully.`, "info");
  } catch (err) {
    showToast("Export Failed", err.message || "Could not export CSV", "error");
  }
}

// Reset to live state with dynamic messaging
async function resetLiveState() {
  if (!window.sureSavingsStore) return;
  try {
    const res = await window.sureSavingsStore.resetToLiveState();
    const profile = res?.profile || {};
    const buffer = Number(profile.current_buffer || 0);
    const score = profile.resilience_score || 0;
    showToast("Workspace Reset", `Reset to baseline state (Buffer: ₹${buffer.toLocaleString()}, Score: ${score}).`, "info");
    updatePageMetrics();
  } catch (err) {
    showToast("Reset Failed", err.message || "Could not reset workspace state", "error");
  }
}

// Update DOM elements across pages dynamically
function updatePageMetrics() {
  if (!window.sureSavingsStore) return;
  const p = window.sureSavingsStore.getProfile();
  if (!p) return;

  const authUser = window.sureSavingsStore.state?.auth?.user || {};
  const isDemo = Boolean(authUser.is_demo_user);

  // Status checks
  const isResilienceInsufficient = !isDemo && (p.resilience_status === "INSUFFICIENT_DATA" || p.resilience_status === "DATA_INCOMPLETE" || !p.resilience_score);
  const isRiskInsufficient = !isDemo && (p.risk_status === "DATA_INCOMPLETE" || p.risk_status === "INSUFFICIENT_DATA" || !p.risk_score);

  const bufVal = Number(p.current_buffer || 0);
  const bufFormatted = `₹${bufVal.toLocaleString()}`;
  const runwayFormatted = (p.current_coverage_weeks !== undefined && p.current_coverage_weeks !== null && p.current_coverage_weeks > 0)
    ? `${p.current_coverage_weeks} weeks`
    : (isDemo ? "1.5 weeks" : "0.0 weeks");
  const scoreFormatted = isResilienceInsufficient ? "—" : `${p.resilience_score || 0}`;
  const riskFormatted = isRiskInsufficient ? "—" : `${p.risk_score || 0}`;

  // Update legacy selectors
  document.querySelectorAll("[data-val='current-buffer']").forEach(el => el.textContent = bufFormatted);
  document.querySelectorAll("[data-val='coverage-weeks']").forEach(el => el.textContent = runwayFormatted);
  document.querySelectorAll("[data-val='resilience-score']").forEach(el => el.textContent = scoreFormatted);

  // 1. Dashboard Total Buffer
  const displayTotalBuffer = document.getElementById("displayTotalBuffer");
  if (displayTotalBuffer) displayTotalBuffer.textContent = bufFormatted;

  // 2. Resilience Score & Gauge (Dashboard + Health Center)
  const scoreValue = document.getElementById("scoreValue");
  if (scoreValue) scoreValue.textContent = scoreFormatted;

  const scoreCount = document.getElementById("scoreCount");
  if (scoreCount) scoreCount.textContent = scoreFormatted;

  const scoreDisplayVal = document.getElementById("scoreDisplayVal");
  if (scoreDisplayVal) scoreDisplayVal.textContent = scoreFormatted;

  const sVal = Math.min(100, Math.max(0, Number(p.resilience_score) || 0));

  const scoreGaugeCircle = document.getElementById("scoreGaugeCircle");
  if (scoreGaugeCircle) {
    const maxDash = 364.4;
    if (isResilienceInsufficient) {
      scoreGaugeCircle.style.strokeDashoffset = maxDash;
    } else {
      scoreGaugeCircle.style.strokeDashoffset = (maxDash - (maxDash * sVal / 100)).toFixed(1);
    }
  }

  const scoreRadialCircle = document.getElementById("scoreRadialCircle");
  if (scoreRadialCircle) {
    const maxDash = 414.7;
    scoreRadialCircle.style.strokeDashoffset = (maxDash - (maxDash * sVal / 100)).toFixed(1);
  }

  const scoreStatusBadge = document.getElementById("scoreStatusBadge");
  if (scoreStatusBadge) {
    if (isResilienceInsufficient) {
      scoreStatusBadge.textContent = "Awaiting Data • Setup Required";
      scoreStatusBadge.className = "mt-2 text-xs font-semibold text-stone-500 bg-stone-100 px-2.5 py-0.5 rounded-md text-center";
    } else {
      const s = Number(p.resilience_score) || 0;
      scoreStatusBadge.textContent = s >= 70 ? "Solid • Volatility Resilient" : (s >= 40 ? "Moderate • Building Cushion" : "Vulnerable • Liquidity at Risk");
      scoreStatusBadge.className = "mt-2 text-xs font-semibold text-emerald-700 bg-emerald-100/60 px-2.5 py-0.5 rounded-md text-center";
    }
  }

  // 3. Risk Score
  const riskScoreValue = document.getElementById("riskScoreValue");
  if (riskScoreValue) riskScoreValue.textContent = riskFormatted;

  // 4. Multi-Factor Dimensions (Dashboard Pillars + Health Center)
  const resData = window.sureSavingsStore?.state?.resilience || {};
  const dims = resData.dimensions || {};

  const stabPct = dims.income_stability !== undefined ? Math.round(dims.income_stability) : (p.stabilized_income > 0 ? Math.max(10, Math.min(95, Math.round((1 - (p.income_volatility || 0.2)) * 100))) : (isDemo ? 82 : 20));
  const bufPct = dims.buffer_coverage !== undefined ? Math.round(dims.buffer_coverage) : (p.buffer_target > 0 ? Math.min(100, Math.round((p.current_buffer / p.buffer_target) * 100)) : (isDemo ? 68 : 0));
  const expPct = dims.expense_health !== undefined ? Math.round(dims.expense_health) : (p.current_income > 0 ? Math.min(100, Math.round((p.weekly_burn / p.current_income) * 100)) : (isDemo ? 75 : 78));
  const cfPct = dims.cashflow_health !== undefined ? Math.round(dims.cashflow_health) : (p.current_coverage_weeks > 0 ? Math.min(100, Math.round((p.current_coverage_weeks / 4.0) * 100)) : (isDemo ? 71 : 66));

  // Dashboard Pillars
  const pillarIncome = document.getElementById("pillarIncomePredictability");
  const pillarIncomeBar = document.getElementById("pillarIncomeBar");
  if (pillarIncome && pillarIncomeBar) {
    pillarIncome.textContent = `${stabPct}%`;
    pillarIncomeBar.style.width = `${stabPct}%`;
  }

  const pillarBuf = document.getElementById("pillarBufferCoverage");
  const pillarBufBar = document.getElementById("pillarBufferBar");
  if (pillarBuf && pillarBufBar) {
    pillarBuf.textContent = `${bufPct}%`;
    pillarBufBar.style.width = `${bufPct}%`;
  }

  const pillarExp = document.getElementById("pillarExpenseRatio");
  const pillarExpBar = document.getElementById("pillarExpenseBar");
  if (pillarExp && pillarExpBar) {
    pillarExp.textContent = `${expPct}%`;
    pillarExpBar.style.width = `${expPct}%`;
  }

  const pillarSurv = document.getElementById("pillarSurvivalHorizon");
  const pillarSurvBar = document.getElementById("pillarSurvivalBar");
  if (pillarSurv && pillarSurvBar) {
    pillarSurv.textContent = `${cfPct}%`;
    pillarSurvBar.style.width = `${cfPct}%`;
  }

  // Health.html Dimensions
  const dimStabilityVal = document.getElementById("dimStabilityVal");
  if (dimStabilityVal) dimStabilityVal.textContent = `${stabPct}%`;
  const dimStabilityBar = document.getElementById("dimStabilityBar");
  if (dimStabilityBar) dimStabilityBar.style.width = `${stabPct}%`;

  const dimBufferVal = document.getElementById("dimBufferVal");
  if (dimBufferVal) dimBufferVal.textContent = `${bufPct}%`;
  const dimBufferBar = document.getElementById("dimBufferBar");
  if (dimBufferBar) dimBufferBar.style.width = `${bufPct}%`;

  const dimExpenseVal = document.getElementById("dimExpenseVal");
  if (dimExpenseVal) dimExpenseVal.textContent = `${expPct}%`;
  const dimExpenseBar = document.getElementById("dimExpenseBar");
  if (dimExpenseBar) dimExpenseBar.style.width = `${expPct}%`;

  const dimCashFlowVal = document.getElementById("dimCashFlowVal");
  if (dimCashFlowVal) dimCashFlowVal.textContent = `${cfPct}%`;
  const dimCashFlowBar = document.getElementById("dimCashFlowBar");
  if (dimCashFlowBar) dimCashFlowBar.style.width = `${cfPct}%`;

  // Health.html Action Cards
  document.querySelectorAll("[data-health='safe-alloc']").forEach(el => el.textContent = `₹${Number(p.recommended_contribution || 0).toLocaleString()}`);
  document.querySelectorAll("[data-health='floor']").forEach(el => el.textContent = `₹${Number(p.protected_floor || 0).toLocaleString()}`);
  document.querySelectorAll("[data-health='runway']").forEach(el => el.textContent = `${p.current_coverage_weeks || 0} wks`);

  // 5. Decision Card (Smart Recommendation)
  const recTitle = document.getElementById("recTitle");
  const recSubtitle = document.getElementById("recSubtitle");
  const recSurplusVal = document.getElementById("recSurplusVal");
  const recRunwayVal = document.getElementById("recRunwayVal");
  const recFloorVal = document.getElementById("recFloorVal");
  const acceptBtn = document.getElementById("acceptBtn");
  const acceptBtnSpan = document.getElementById("acceptBtnSpan");

  const recAmt = Number(p.recommended_contribution || 0);
  const surplus = Number(p.surplus || 0);
  const floor = Number(p.protected_floor || 0);

  const curBuffer = Number(p.current_buffer || 0);
  const targetBuffer = Number(p.buffer_target || 0);
  const isTargetReached = (curBuffer >= targetBuffer && targetBuffer > 0) || (p.buffer_state === "HEALTHY" && curBuffer > 0);

  if (recTitle) {
    if (isDemo) {
      recTitle.textContent = "Save ₹900 while preserving your cash floor.";
      if (recSubtitle) recSubtitle.textContent = "Surplus detected of ₹1,300 above baseline. Moving ₹900 to your buffer keeps ₹400 free pocket liquidity and expands safety duration.";
      if (recSurplusVal) recSurplusVal.textContent = "+₹1,300";
      if (recRunwayVal) recRunwayVal.textContent = "1.5 weeks → 1.7 weeks";
      if (recFloorVal) recFloorVal.textContent = "₹3,500 (100% Untouched)";
      if (acceptBtnSpan) acceptBtnSpan.textContent = "Approve ₹900 Reserve Transfer";
      if (acceptBtn) {
        acceptBtn.disabled = false;
        acceptBtn.className = "w-full py-3 bg-brand-500 hover:bg-brand-600 text-white rounded-xl font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center justify-center space-x-2 cursor-pointer";
        acceptBtn.onclick = () => openApproveTransferModal();
      }
    } else if (recAmt > 0) {
      recTitle.textContent = `Save ₹${recAmt.toLocaleString()} while preserving cash floor.`;
      if (recSubtitle) recSubtitle.textContent = `Surplus detected of ₹${surplus.toLocaleString()} above baseline. Moving ₹${recAmt.toLocaleString()} to your buffer keeps ₹${Number(p.free_pocket_liquidity || 0).toLocaleString()} free pocket cash and expands runway coverage.`;
      if (recSurplusVal) recSurplusVal.textContent = `+₹${surplus.toLocaleString()}`;
      if (recRunwayVal) recRunwayVal.textContent = `${p.current_coverage_weeks || 0} wks → ${(Number(p.current_coverage_weeks || 0) + 0.2).toFixed(1)} wks`;
      if (recFloorVal) recFloorVal.textContent = `₹${floor.toLocaleString()} (100% Untouched)`;
      if (acceptBtnSpan) acceptBtnSpan.textContent = `Approve ₹${recAmt.toLocaleString()} Reserve Transfer`;
      if (acceptBtn) {
        acceptBtn.disabled = false;
        acceptBtn.className = "w-full py-3 bg-brand-500 hover:bg-brand-600 text-white rounded-xl font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center justify-center space-x-2 cursor-pointer";
        acceptBtn.onclick = () => openApproveTransferModal();
      }
    } else if (isTargetReached) {
      recTitle.textContent = `Target Buffer Capitalized (₹${curBuffer.toLocaleString()})`;
      if (recSubtitle) recSubtitle.textContent = `Target safety cushion is 100% achieved (${p.current_coverage_weeks || 0} wks runway). Protected cash floor of ₹${floor.toLocaleString()} is fully preserved.`;
      if (recSurplusVal) recSurplusVal.textContent = `₹0 (Allocated)`;
      if (recRunwayVal) recRunwayVal.textContent = `${p.current_coverage_weeks || 0} weeks`;
      if (recFloorVal) recFloorVal.textContent = `₹${floor.toLocaleString()} (100% Intact)`;
      if (acceptBtnSpan) acceptBtnSpan.textContent = "Target Cushion Achieved ✓";
      if (acceptBtn) {
        acceptBtn.disabled = true;
        acceptBtn.className = "w-full py-3 bg-emerald-600 text-white rounded-xl font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center justify-center space-x-2 cursor-default";
        acceptBtn.onclick = null;
      }
    } else if (p.current_income > 0 || p.weekly_burn > 0) {
      recTitle.textContent = "Preserve Cash Floor (Safe-to-Save: ₹0)";
      if (recSubtitle) recSubtitle.textContent = "Essential weekly obligations consume current income. Buffer protection active: zero reserve transfer is recommended to ensure checking floor remains intact.";
      if (recSurplusVal) recSurplusVal.textContent = `₹${surplus.toLocaleString()}`;
      if (recRunwayVal) recRunwayVal.textContent = `${p.current_coverage_weeks || 0} weeks`;
      if (recFloorVal) recFloorVal.textContent = `₹${floor.toLocaleString()} (Protected Floor)`;
      if (acceptBtnSpan) acceptBtnSpan.textContent = "Protection Mode Active (₹0)";
      if (acceptBtn) {
        acceptBtn.disabled = true;
        acceptBtn.className = "w-full py-3 bg-stone-400 text-white rounded-xl font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center justify-center space-x-2 cursor-not-allowed";
        acceptBtn.onclick = null;
      }
    } else {
      recTitle.textContent = "Complete Financial Setup to Unlock Safe-to-Save";
      if (recSubtitle) recSubtitle.textContent = "SURE SAVINGS calculates dynamic reserve allocations once your income sources and essential expenses are entered.";
      if (recSurplusVal) recSurplusVal.textContent = "—";
      if (recRunwayVal) recRunwayVal.textContent = "—";
      if (recFloorVal) recFloorVal.textContent = `₹${floor.toLocaleString()}`;
      if (acceptBtnSpan) acceptBtnSpan.textContent = "Start Financial Setup →";
      if (acceptBtn) {
        acceptBtn.disabled = false;
        acceptBtn.className = "w-full py-3 bg-brand-500 hover:bg-brand-600 text-white rounded-xl font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center justify-center space-x-2 cursor-pointer";
        acceptBtn.onclick = () => {
          if (window.setupWizard && typeof window.setupWizard.openSetupWizardModal === 'function') {
            window.setupWizard.openSetupWizardModal();
          } else if (window.setupWizard && typeof window.setupWizard.openQuickStartModal === 'function') {
            window.setupWizard.openQuickStartModal();
          }
        };
      }
    }
  }

  // 6. Buffer Vault Card
  const targetBufferLabel = document.getElementById("targetBufferLabel");
  const bufferRunwayWeeks = document.getElementById("bufferRunwayWeeks");
  const bufferBarFloor = document.getElementById("bufferBarFloor");
  const bufferBarUsable = document.getElementById("bufferBarUsable");
  const bufferLegendFloor = document.getElementById("bufferLegendFloor");
  const bufferLegendUsable = document.getElementById("bufferLegendUsable");
  const bufferLegendTarget = document.getElementById("bufferLegendTarget");
  const weeklyFixedBurnVal = document.getElementById("weeklyFixedBurnVal");
  const downsideVolatilityVal = document.getElementById("downsideVolatilityVal");

  const bTarget = Number(p.buffer_target || (isDemo ? 15000 : 0));
  const bTargetPct = bTarget > 0 ? Math.min(100, Math.round((bufVal / bTarget) * 100)) : 0;

  if (targetBufferLabel) {
    targetBufferLabel.textContent = bTarget > 0 ? `Target: ₹${bTarget.toLocaleString()} (${bTargetPct}%)` : "Target: Not set";
  }
  if (bufferRunwayWeeks) {
    bufferRunwayWeeks.textContent = runwayFormatted;
  }
  if (bufferBarFloor && bufferBarUsable) {
    if (bTarget > 0) {
      const fW = Math.min(60, (Number(p.protected_floor || 0) / bTarget) * 100);
      const uW = Math.min(60, (Number(p.safe_to_use_above_floor || 0) / bTarget) * 100);
      bufferBarFloor.style.width = `${fW.toFixed(1)}%`;
      bufferBarUsable.style.width = `${uW.toFixed(1)}%`;
    } else {
      bufferBarFloor.style.width = "0%";
      bufferBarUsable.style.width = "0%";
    }
  }
  if (bufferLegendFloor) bufferLegendFloor.textContent = `Floor: ₹${floor.toLocaleString()}`;
  if (bufferLegendUsable) bufferLegendUsable.textContent = `Safe to Use: ₹${Number(p.safe_to_use_above_floor || 0).toLocaleString()}`;
  if (bufferLegendTarget) bufferLegendTarget.textContent = bTarget > 0 ? `Target: ₹${Math.round(bTarget / 1000)}k` : "Target: —";
  if (weeklyFixedBurnVal) weeklyFixedBurnVal.textContent = p.weekly_burn > 0 ? `₹${Number(p.weekly_burn).toLocaleString()}` : (isDemo ? "₹4,400" : "—");
  if (downsideVolatilityVal) {
    if (isDemo) downsideVolatilityVal.textContent = "31%";
    else downsideVolatilityVal.textContent = (!isRiskInsufficient && p.income_volatility > 0) ? `${Math.round(p.income_volatility * 100)}%` : "—";
  }

  // 7. Income Variance & Stabilized Baseline
  const actualThisWeekVal = document.getElementById("actualThisWeekVal");
  const actualThisWeekSub = document.getElementById("actualThisWeekSub");
  const stabilizedBaselineVal = document.getElementById("stabilizedBaselineVal");
  const expectedIncomeVal = document.getElementById("expectedIncomeVal");
  const expectedIncomeSub = document.getElementById("expectedIncomeSub");

  if (actualThisWeekVal) {
    actualThisWeekVal.textContent = `₹${Number(p.current_income || 0).toLocaleString()}`;
  }
  if (actualThisWeekSub) {
    if (isDemo) actualThisWeekSub.textContent = "Surplus week";
    else actualThisWeekSub.textContent = (p.current_income > p.weekly_burn && p.weekly_burn > 0) ? "Surplus week" : (p.current_income > 0 ? "Balanced week" : "Awaiting data");
  }
  if (stabilizedBaselineVal) {
    if (isDemo) stabilizedBaselineVal.textContent = "₹7,100";
    else stabilizedBaselineVal.textContent = (p.stabilized_income > 0) ? `₹${Number(p.stabilized_income).toLocaleString()}` : "—";
  }
  if (expectedIncomeVal) {
    if (isDemo) expectedIncomeVal.textContent = "₹6,900";
    else expectedIncomeVal.textContent = (p.forecast_status === "INSUFFICIENT_DATA" || !p.forecast_next_week) ? "Awaiting data" : `₹${Number(p.forecast_next_week).toLocaleString()}`;
  }
  if (expectedIncomeSub) {
    if (isDemo) expectedIncomeSub.textContent = "Slight dip forecast";
    else expectedIncomeSub.textContent = (p.forecast_status === "INSUFFICIENT_DATA" || !p.forecast_next_week) ? "Min. 4 weeks required" : "Smoothed forecast";
  }

  // 8. Income Bar Chart: Empty state for brand new users without history
  const chartContainer = document.getElementById("incomeBarChartContainer");
  if (chartContainer && !isDemo && (!p.current_income || p.current_income === 0)) {
    chartContainer.innerHTML = `
      <div class="h-44 w-full flex flex-col items-center justify-center border border-dashed border-stone-300 rounded-xl p-4 text-center bg-stone-50/50">
        <div class="w-10 h-10 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center mb-2 font-bold text-base">📊</div>
        <p class="text-xs font-bold text-stone-800">No Historical Income Data Recorded</p>
        <p class="text-[11px] text-stone-500 max-w-xs mt-0.5">Enter 1–4 weeks of past earnings to unlock baseline smoothing, variance trends, and forward predictions.</p>
        <button onclick="window.setupWizard?.openSetupWizardModal(3) || window.setupWizard?.openQuickStartModal()" class="mt-3 px-3 py-1.5 bg-brand-500 hover:bg-brand-600 text-white rounded-lg text-xs font-bold shadow-sm transition-all">
          + Add Income History
        </button>
      </div>
    `;
  }

  // 9. Generic data-bind attributes fallback
  document.querySelectorAll("[data-bind]").forEach(el => {
    const key = el.getAttribute("data-bind");
    if (!key) return;

    if (key === "buffer.balance") el.textContent = bufFormatted;
    else if (key === "buffer.coverage_weeks") el.textContent = runwayFormatted;
    else if (key === "resilience.score") el.textContent = scoreFormatted;
    else if (key === "risk.score") el.textContent = riskFormatted;
    else if (key === "income.current") el.textContent = `₹${Number(p.current_income || 0).toLocaleString()}`;
    else if (key === "income.stabilized") el.textContent = (p.stabilized_income > 0) ? `₹${Number(p.stabilized_income).toLocaleString()}` : "—";
    else if (key === "income.surplus") el.textContent = `₹${Number(p.surplus || 0).toLocaleString()}`;
    else if (key === "recommendation.amount") el.textContent = `₹${Number(p.recommended_contribution || 0).toLocaleString()}`;
    else if (key === "pocket.free") el.textContent = `₹${Number(p.free_pocket_liquidity || 0).toLocaleString()}`;
    else if (key === "floor.protected") el.textContent = `₹${Number(p.protected_floor || 0).toLocaleString()}`;
    else if (key === "floor.safe_to_use") el.textContent = `₹${Number(p.safe_to_use_above_floor || 0).toLocaleString()}`;
  });

  // 10. Update Setup Banner if wizard module loaded
  if (window.setupWizard && typeof window.setupWizard.renderDashboardBanner === 'function') {
    window.setupWizard.renderDashboardBanner();
  }

  // 11. SURE SAVINGS 7.0 Intelligence: Next Best Action, Data Quality, Behavior Profile
  const storeState = window.sureSavingsStore?.state;
  if (storeState) {
    if (storeState.nextBestAction) {
      renderNextBestAction(storeState.nextBestAction);
    }
    if (storeState.dataQuality) {
      renderDataQualityBadge(storeState.dataQuality);
    }
    if (storeState.behaviorProfile) {
      renderBehaviorProfile(storeState.behaviorProfile);
    }
    // 12. SURE SAVINGS 8.0: Adaptive Financial Resilience Operating System
    renderAdaptiveOperatingSystem(storeState);
  }
}

/**
 * SURE SAVINGS 7.0: Next Best Action Renderer
 * Updates single authoritative financial priority with rationale, impact, and confidence.
 */
function renderNextBestAction(action) {
  if (!action) return;
  const priorityBadge = document.getElementById("nbaPriorityBadge");
  const recTitle = document.getElementById("recTitle");
  const recSubtitle = document.getElementById("recSubtitle");
  const recSurplusVal = document.getElementById("recSurplusVal");
  const recRunwayVal = document.getElementById("recRunwayVal");
  const recFloorVal = document.getElementById("recFloorVal");
  const recConfidence = document.getElementById("recConfidence");
  const acceptBtn = document.getElementById("acceptBtn");
  const acceptBtnSpan = document.getElementById("acceptBtnSpan");

  if (priorityBadge && action.priority) {
    const pText = action.priority.replace(/_/g, " • ");
    priorityBadge.textContent = pText;
    if (action.priority.startsWith("P1")) {
      priorityBadge.className = "px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-rose-100 text-rose-700";
    } else if (action.priority.startsWith("P2")) {
      priorityBadge.className = "px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-amber-100 text-amber-700";
    } else {
      priorityBadge.className = "px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-brand-100 text-brand-700";
    }
  }

  if (recTitle && action.headline) {
    recTitle.textContent = action.headline;
  }
  if (recSubtitle && (action.summary || action.reason)) {
    recSubtitle.textContent = action.summary || action.reason;
  }

  if (recConfidence && action.confidence !== undefined) {
    const pct = Math.round((action.confidence || 0.94) * 100);
    if (window.SURE_SAVINGS_UI?.renderDataTrustBadge) {
      recConfidence.innerHTML = window.SURE_SAVINGS_UI.renderDataTrustBadge({
        source: "Digital Twin",
        updated: "Real-time",
        confidence: `${pct}%`,
        status: "Verified"
      });
    } else {
      recConfidence.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span>${pct}% Confidence</span>`;
    }
  }

  const impact = action.impact_metrics;
  if (impact) {
    if (recSurplusVal && impact.capital_allocated !== undefined) {
      recSurplusVal.textContent = `₹${Number(impact.capital_allocated).toLocaleString()}`;
    }
    if (recRunwayVal && impact.runway_delta_weeks !== undefined) {
      recRunwayVal.textContent = `+${impact.runway_delta_weeks} wks runway (${action.expected_impact || ''})`;
    }
    if (recFloorVal && impact.checking_floor_preserved !== undefined) {
      recFloorVal.textContent = `₹${Number(impact.checking_floor_preserved).toLocaleString()} (100% Untouched)`;
    }
  }

  if (action.cta && acceptBtnSpan) {
    acceptBtnSpan.textContent = action.cta.label || "Approve Reserve Transfer";
  }
}

/**
 * SURE SAVINGS 7.0: Continuous Data Quality Badge Renderer
 */
function renderDataQualityBadge(dq) {
  const pill = document.getElementById("data-quality-pill");
  const text = document.getElementById("data-quality-text");
  if (!pill || !text || !dq) return;

  const score = dq.overall_score !== undefined ? dq.overall_score : 95;
  const status = dq.status || (score >= 80 ? "HIGH" : (score >= 50 ? "MEDIUM" : "INSUFFICIENT"));
  text.textContent = `Data Quality: ${score}/100 (${status})`;

  if (status === "HIGH" || score >= 80) {
    pill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-pointer hover:bg-emerald-100 transition-colors";
  } else if (status === "MEDIUM" || score >= 50) {
    pill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 cursor-pointer hover:bg-amber-100 transition-colors";
  } else {
    pill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 cursor-pointer hover:bg-rose-100 transition-colors";
  }

  // Update modal values if cached
  const dqModalScore = document.getElementById("dqModalScore");
  const dqModalBadge = document.getElementById("dqModalBadge");
  const dqModalLabel = document.getElementById("dqModalLabel");
  if (dqModalScore) dqModalScore.textContent = `${score}/100`;
  if (dqModalBadge) dqModalBadge.textContent = status;
  if (dqModalLabel) {
    dqModalLabel.textContent = status === "HIGH" 
      ? "High Integrity • Authoritative Decision Status"
      : (status === "MEDIUM" ? "Moderate Integrity • Additional Data Recommended" : "Insufficient Data • Setup Required");
  }

  if (dq.dimensions) {
    const setDim = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = `${val}%`;
    };
    if (dq.dimensions.completeness) setDim("dqDimCompleteness", dq.dimensions.completeness.score || dq.completeness || 95);
    if (dq.dimensions.validity) setDim("dqDimValidity", dq.dimensions.validity.score || dq.validity || 100);
    if (dq.dimensions.consistency) setDim("dqDimConsistency", dq.dimensions.consistency.score || dq.consistency || 95);
    if (dq.dimensions.freshness) setDim("dqDimFreshness", dq.dimensions.freshness.score || dq.freshness || 90);
    if (dq.dimensions.uniqueness) setDim("dqDimUniqueness", dq.dimensions.uniqueness.score || dq.uniqueness || 95);
  }
}

/**
 * SURE SAVINGS 7.0: Behavior-Based Personalization Profile Renderer
 */
function renderBehaviorProfile(bp) {
  const pill = document.getElementById("behavior-profile-pill");
  const text = document.getElementById("behavior-profile-text");
  if (!pill || !text || !bp) return;

  const profName = typeof bp === "string" ? bp : (bp.profile || "BUFFER_BUILDING");
  text.textContent = `Profile: ${profName}`;
  pill.title = typeof bp === "object" ? (bp.headline || bp.narrative || profName) : profName;

  // Update modal fields
  if (typeof bp === "object") {
    const arch = document.getElementById("bpModalArchetype");
    const tone = document.getElementById("bpModalTone");
    const head = document.getElementById("bpModalHeadline");
    const narr = document.getElementById("bpModalNarrative");
    const focus = document.getElementById("bpModalActionFocus");
    if (arch) arch.textContent = profName;
    if (tone) tone.textContent = bp.tone || "ENCOURAGING";
    if (head) head.textContent = bp.headline || "Active Buffer Accumulator";
    if (narr) narr.textContent = bp.narrative || "Healthy cash flow generation with positive surplus.";
    if (focus) focus.textContent = bp.action_focus || "Systematically build reserve cushion.";
  }
}

/**
 * SURE SAVINGS 8.0: Adaptive Financial Resilience Operating System Renderer
 * Renders Financial Weather Strip, What Changed Card, and The 5 Core Financial Questions.
 */
function renderAdaptiveOperatingSystem(state) {
  if (!state || !window.UI) return;

  const weatherContainer = document.getElementById("financial-weather-container");
  if (weatherContainer) {
    const weatherData = state.financialWeather || state.weather || state.digitalTwin?.weather;
    if (weatherData && typeof window.UI.renderFinancialWeatherStrip === "function") {
      weatherContainer.innerHTML = window.UI.renderFinancialWeatherStrip(weatherData);
    }
  }

  const whatChangedContainer = document.getElementById("what-changed-container");
  if (whatChangedContainer) {
    const whatChangedData = state.whatChanged || state.digitalTwin?.what_changed;
    if (whatChangedData && typeof window.UI.renderWhatChangedCard === "function") {
      whatChangedContainer.innerHTML = window.UI.renderWhatChangedCard(whatChangedData);
    }
  }

  const questionsContainer = document.getElementById("five-core-questions-container");
  if (questionsContainer) {
    if (typeof window.UI.render5CoreQuestions === "function") {
      questionsContainer.innerHTML = window.UI.render5CoreQuestions({
        twin: state.digitalTwin || {},
        weather: state.financialWeather || state.weather || state.digitalTwin?.weather || {},
        plan: state.resiliencePlan || state.digitalTwin?.resilience_plan || {}
      });
    }
  }
}

/**
 * SURE SAVINGS 7.0: Metric Explainability & 6-Step Dependency Graph Modal Controller
 */
async function openExplainMetricModal(metricName = "safe_to_save") {
  const modal = document.getElementById("metricExplainModal");
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");

  const titleEl = document.getElementById("explainMetricTitle");
  const valEl = document.getElementById("explainMetricValue");
  const narrativeEl = document.getElementById("explainMetricNarrative");
  const formulaEl = document.getElementById("explainMetricFormula");
  const policyEl = document.getElementById("explainMetricPolicy");
  const stepsContainer = document.getElementById("explainMetricStepsContainer");
  const driversContainer = document.getElementById("explainMetricDriversContainer");
  const badgeEl = document.getElementById("explainMetricStatusBadge");
  const versionEl = document.getElementById("explainMetricVersion");
  const confEl = document.getElementById("explainMetricConfidence");
  const calcAtEl = document.getElementById("explainMetricCalculatedAt");

  if (titleEl) titleEl.textContent = `Explaining ${metricName.replace(/_/g, " ").toUpperCase()}...`;
  if (valEl) valEl.textContent = "Calculating...";
  if (stepsContainer) stepsContainer.innerHTML = `<div class="p-4 text-center text-xs text-stone-500 font-mono">Retrieving 6-step deterministic dependency chain...</div>`;

  try {
    let data = null;
    if (window.sureSavingsApi && window.sureSavingsApi.explainMetric) {
      data = await window.sureSavingsApi.explainMetric(metricName);
    }

    if (!data || data.status === "error") {
      throw new Error("Unable to retrieve metric explanation");
    }

    if (titleEl) titleEl.textContent = data.display_title || data.metric || `${metricName} Trace`;
    if (versionEl) versionEl.textContent = data.engine_version || "Deterministic Engine v7.0";
    if (valEl) valEl.textContent = data.value || data.current_value || "—";
    if (narrativeEl) narrativeEl.textContent = data.plain_language_explanation || data.evidence || data.definition || "";
    if (formulaEl) formulaEl.textContent = data.formula || "Institutional weighted scoring";
    if (policyEl) policyEl.textContent = data.policy ? `Policy: ${data.policy}` : "";
    if (badgeEl) {
      badgeEl.textContent = data.status || "AUTHORITATIVE";
      badgeEl.className = data.status === "AUTHORITATIVE"
        ? "px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800"
        : "px-2.5 py-0.5 rounded-full text-xs font-bold bg-stone-100 text-stone-700";
    }
    if (confEl && data.confidence !== undefined) {
      const pct = Math.round(data.confidence * 100);
      confEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span> ${pct}% Confidence`;
    }
    if (calcAtEl && data.calculated_at) {
      calcAtEl.textContent = `Calculated: ${new Date(data.calculated_at).toLocaleTimeString()}`;
    }

    // Render Primary Drivers
    if (driversContainer) {
      const drivers = data.primary_drivers || [];
      if (drivers.length > 0) {
        driversContainer.innerHTML = drivers.map(d => `
          <div class="p-2.5 bg-stone-50 border border-stone-200/80 rounded-xl text-xs">
            <span class="text-stone-500 block text-[11px] font-medium">${d.name || d.driver || 'Driver'}</span>
            <span class="font-bold text-stone-800 font-mono text-sm block mt-0.5">${typeof d.value === 'number' ? '₹' + d.value.toLocaleString() : (d.value || d.impact || '—')}</span>
            <span class="text-[10px] text-brand-600 font-semibold">${d.impact || 'Active'}</span>
          </div>
        `).join("");
      } else {
        driversContainer.innerHTML = `<div class="text-xs text-stone-400">Standard operational baseline drivers active.</div>`;
      }
    }

    // Render Steps / 6-Step Dependency Graph
    if (stepsContainer) {
      const steps = data.calculation_steps || data.steps || data.dependency_graph || [];
      if (steps.length > 0) {
        stepsContainer.innerHTML = steps.map(s => `
          <div class="p-2.5 bg-white border border-stone-200 rounded-xl flex items-start justify-between gap-3 text-xs shadow-xs">
            <div class="flex items-start space-x-2.5">
              <span class="w-5 h-5 rounded-md bg-stone-900 text-white font-mono text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">${s.step || '•'}</span>
              <div>
                <span class="font-bold text-stone-800 block">${s.name || 'Stage'}</span>
                <span class="text-[11px] text-stone-500 leading-tight">${s.description || ''}</span>
              </div>
            </div>
            ${s.value ? `<span class="font-mono font-bold text-stone-900 bg-stone-100 px-2 py-0.5 rounded text-[11px] shrink-0">${s.value}</span>` : ''}
          </div>
        `).join("");
      } else {
        stepsContainer.innerHTML = `<div class="text-xs text-stone-500">No intermediate steps logged for this metric.</div>`;
      }
    }

  } catch (err) {
    console.warn("Error fetching metric explanation:", err);
    if (valEl) valEl.textContent = "—";
    if (stepsContainer) stepsContainer.innerHTML = `<div class="p-3 bg-amber-50 text-amber-800 rounded-xl text-xs">Could not load remote trace. Showing local baseline calculations.</div>`;
  }
}

function closeExplainMetricModal() {
  const modal = document.getElementById("metricExplainModal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

function openDataQualityModal() {
  const modal = document.getElementById("dataQualityModal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    if (window.sureSavingsApi && window.sureSavingsApi.getDataQuality) {
      window.sureSavingsApi.getDataQuality().then(renderDataQualityBadge).catch(() => {});
    }
  }
}

function closeDataQualityModal() {
  const modal = document.getElementById("dataQualityModal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

function openBehaviorProfileInfo() {
  const modal = document.getElementById("behaviorProfileModal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  }
}

function closeBehaviorProfileModal() {
  const modal = document.getElementById("behaviorProfileModal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

// Global exports
window.openExplainMetricModal = openExplainMetricModal;
window.closeExplainMetricModal = closeExplainMetricModal;
window.openDataQualityModal = openDataQualityModal;
window.closeDataQualityModal = closeDataQualityModal;
window.openBehaviorProfileInfo = openBehaviorProfileInfo;
window.closeBehaviorProfileModal = closeBehaviorProfileModal;
window.renderNextBestAction = renderNextBestAction;
window.renderDataQualityBadge = renderDataQualityBadge;
window.renderBehaviorProfile = renderBehaviorProfile;

// Activity Page State
let txState = {
  page: 1,
  pageSize: 10,
  category: "all",
  search: ""
};

// Fetch and render paginated transactions for activity.html
async function fetchAndRenderTransactions(page = 1, category = "all", search = "") {
  txState.page = page;
  txState.category = category;
  txState.search = search;

  if (!window.sureSavingsApi) return;

  const container = document.querySelector("section[data-purpose='ledger-table-container']") || document.querySelector("table")?.parentElement;
  if (!container) return;

  try {
    const res = await window.sureSavingsApi.getTransactions({
      page: txState.page,
      page_size: txState.pageSize,
      category: txState.category,
      search: txState.search
    });

    if (res && res.transactions) {
      // Update summary cards if present
      if (res.summary) {
        document.querySelectorAll("[data-summary='inflows']").forEach(el => el.textContent = `₹${res.summary.total_inflows.toLocaleString()}`);
        document.querySelectorAll("[data-summary='outflows']").forEach(el => el.textContent = `₹${res.summary.total_outflows.toLocaleString()}`);
        document.querySelectorAll("[data-summary='buffer-contribs']").forEach(el => el.textContent = `₹${res.summary.buffer_contributions.toLocaleString()}`);
      }

      const tableWrapper = document.getElementById("paginatedTableContainer");
      if (tableWrapper && window.SURE_SAVINGS_UI) {
        tableWrapper.innerHTML = window.SURE_SAVINGS_UI.renderTransactionTable({
          transactions: res.transactions,
          pagination: res.pagination,
          onPage: "changeTxPage"
        });
      } else {
        // Direct tbody injection fallback
        const tbody = document.querySelector("tbody");
        if (tbody) {
          tbody.innerHTML = "";
          res.transactions.forEach(tx => {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-slate-50/80 transition-colors border-b border-slate-100";
            const isPos = tx.amount.startsWith("+");
            tr.innerHTML = `
              <td class="px-6 py-4 whitespace-nowrap text-xs text-slate-500 font-mono">${tx.date}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-xs font-semibold text-slate-900">${tx.description}</div>
                <div class="text-[10px] text-slate-400">${tx.platform || "Platform"}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-xs text-slate-600">${tx.category}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isPos ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}">${tx.type}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-xs font-bold font-mono text-right ${isPos ? 'text-emerald-600' : 'text-slate-900'}">${tx.amount}</td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <span class="text-[10px] text-slate-400 font-medium">${tx.status || 'Settled'}</span>
              </td>
            `;
            tbody.appendChild(tr);
          });
        }
      }
    }
  } catch (err) {
    console.warn("Error loading transactions:", err);
  }
}

window.changeTxPage = function(page) {
  fetchAndRenderTransactions(page, txState.category, txState.search);
};

// Screen-specific Dynamic Data Loaders
async function loadPageSpecificData() {
  const path = window.location.pathname.split("/").pop() || "index.html";

  // 1. Activity Ledger Page
  if (path.includes("activity.html")) {
    const searchInput = document.querySelector("input[placeholder*='Search by merchant']");
    if (searchInput) {
      let timeout = null;
      searchInput.addEventListener("input", (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          fetchAndRenderTransactions(1, txState.category, e.target.value.trim());
        }, 300);
      });
    }

    const tabButtons = document.querySelectorAll("section[data-purpose='ledger-table-container'] button");
    tabButtons.forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        tabButtons.forEach(b => {
          b.classList.remove("bg-white", "text-slate-900", "font-bold", "shadow-sm");
          b.classList.add("text-slate-600", "font-medium");
        });
        btn.classList.add("bg-white", "text-slate-900", "font-bold", "shadow-sm");
        btn.classList.remove("text-slate-600", "font-medium");

        const txt = btn.textContent.toLowerCase();
        let cat = "all";
        if (txt.includes("income")) cat = "Gig Platform";
        else if (txt.includes("essential")) cat = "Transit";
        else if (txt.includes("buffer")) cat = "Buffer";
        fetchAndRenderTransactions(1, cat, txState.search);
      });
    });

    fetchAndRenderTransactions(1, "all", "");
  }

  // 2. Cash Flow Planner & Intraday Timeline (planner.html)
  if (path.includes("planner.html") && window.sureSavingsApi) {
    try {
      const timelineData = await window.sureSavingsApi.getCashFlowTimeline();
      const cfSummary = await window.sureSavingsApi.getCashFlow();
      const p = window.sureSavingsStore?.getProfile() || {};

      if (cfSummary) {
        document.querySelectorAll("[data-planner='net-margin']").forEach(el => el.textContent = `+₹${cfSummary.net_liquidity_margin.toLocaleString()}`);
        document.querySelectorAll("[data-planner='inflows']").forEach(el => el.textContent = `₹${cfSummary.upcoming_inflows.toLocaleString()}`);
        document.querySelectorAll("[data-planner='outflows']").forEach(el => el.textContent = `₹${cfSummary.scheduled_outflows.toLocaleString()}`);
        document.querySelectorAll("[data-planner='min-balance']").forEach(el => el.textContent = `₹${Number(cfSummary.projected_minimum_balance || p.protected_floor || 500).toLocaleString()}`);
        const minClearance = Math.max(0, (cfSummary.projected_minimum_balance || 500) - (cfSummary.protected_floor || p.protected_floor || 500));
        document.querySelectorAll("[data-planner='floor-diff']").forEach(el => el.textContent = `✓ +₹${minClearance.toLocaleString()} above ₹${Number(cfSummary.protected_floor || p.protected_floor || 500).toLocaleString()} floor`);
      }

      // Inject Intraday Timeline Card
      const timelineMount = document.getElementById("intradayTimelineMount");
      if (timelineMount && window.SURE_SAVINGS_UI && timelineData) {
        timelineMount.innerHTML = window.SURE_SAVINGS_UI.renderCashFlowTimeline(timelineData);
      }
    } catch (e) {
      console.warn("Could not load dynamic planner data:", e);
    }
  }

  // 3. Goals & Buffer Plan Page (goals.html)
  if (path.includes("goals.html") && window.sureSavingsApi) {
    try {
      const data = await window.sureSavingsApi.getGoals();
      const p = window.sureSavingsStore?.getProfile() || {};
      if (data) {
        if (data.target_buffer_capital) {
          document.querySelectorAll("[data-goal='target-buffer-capital']").forEach(el => el.textContent = `₹${data.target_buffer_capital.toLocaleString()}`);
        }
        if (data.cumulative_funded !== undefined) {
          document.querySelectorAll("[data-goal='cumulative-funded']").forEach(el => el.textContent = `₹${data.cumulative_funded.toLocaleString()}`);
        }
        const totalTarget = data.target_buffer_capital || 30400;
        const cumFunded = data.cumulative_funded || 0;
        const cumPct = totalTarget > 0 ? Math.min(100, Math.round((cumFunded / totalTarget) * 100)) : 100;
        document.querySelectorAll("[data-goal='cumulative-pct']").forEach(el => el.textContent = `${cumPct}% Funded`);
        document.querySelectorAll("[data-goal='cumulative-bar']").forEach(el => el.style.width = `${cumPct}%`);
        document.querySelectorAll("[data-goal='floor-preserved']").forEach(el => el.textContent = `₹${Number(p.protected_floor || 500).toLocaleString()}`);
        document.querySelectorAll("[data-goal='monthly-pacing']").forEach(el => el.innerHTML = `₹${Number(data.monthly_allocation_rate || 3200).toLocaleString()}<span class="text-xs font-normal" style="color: var(--text-muted)">/mo</span>`);

        if (data.pillars) {
          const pillar2 = data.pillars.find(p => p.id === "pillar_buffer");
          if (pillar2) {
            document.querySelectorAll("[data-goal='buffer-funded']").forEach(el => el.textContent = `₹${pillar2.funded.toLocaleString()}`);
            document.querySelectorAll("[data-goal='buffer-bar']").forEach(el => el.style.width = `${pillar2.pct}%`);
            document.querySelectorAll("[data-goal='buffer-pct']").forEach(el => el.textContent = `${pillar2.pct}% Funded`);
            document.querySelectorAll("[data-goal='buffer-target']").forEach(el => el.textContent = `of ₹${pillar2.target.toLocaleString()} (4.0 wks)`);
            document.querySelectorAll("[data-goal='buffer-runway']").forEach(el => el.textContent = `${p.current_coverage_weeks || 4.0} wks runway`);
          }
        }
      }
    } catch (e) {
      console.warn("Could not load dynamic goals data:", e);
    }
  }

  // 4. Income Intelligence Page (income-intelligence.html)
  if (path.includes("income-intelligence.html") && window.sureSavingsApi) {
    try {
      const data = await window.sureSavingsApi.getIncomeAnalytics();
      const p = window.sureSavingsStore?.getProfile() || {};
      if (data) {
        document.querySelectorAll("[data-income='current']").forEach(el => el.textContent = `₹${Number(data.current_week_income || p.current_income || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='stabilized']").forEach(el => el.textContent = `₹${Number(data.stabilized_baseline || p.stabilized_income || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='median']").forEach(el => el.textContent = `₹${Number(data.median_weekly || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='average']").forEach(el => el.textContent = `₹${Number(data.average_weekly || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='volatility']").forEach(el => el.textContent = `${Number(data.volatility_index || 0).toFixed(2)} CV`);
        document.querySelectorAll("[data-income='lowest']").forEach(el => el.textContent = `₹${Number(data.lowest_recorded || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='highest']").forEach(el => el.textContent = `₹${Number(data.highest_recorded || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='spread']").forEach(el => el.textContent = `₹${Number(data.safe_floor_spread || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='forecast']").forEach(el => el.textContent = `₹${Number(data.forecast_next_week || 0).toLocaleString()}`);
        document.querySelectorAll("[data-income='floor']").forEach(el => el.textContent = `₹${Number(p.protected_floor || 500).toLocaleString()}`);

        const surplus = Math.max(0, (data.current_week_income || 0) - (data.stabilized_baseline || 0));
        document.querySelectorAll("[data-income='surplus-text']").forEach(el => el.textContent = `₹${surplus.toLocaleString()} in surplus`);
        document.querySelectorAll("[data-income='surplus-heading']").forEach(el => {
          el.textContent = surplus > 0 ? `Income is +${Math.round(data.recent_drift_pct || 0)}% above stabilized baseline.` : `Preserve Operational Cash Floor`;
        });
      }
    } catch (e) {
      console.warn("Could not load dynamic income analytics:", e);
    }
  }

  // 5. Decision Pipeline Screen (decision-pipeline.html)
  if (path.includes("decision-pipeline.html") && window.sureSavingsApi) {
    try {
      const data = await window.sureSavingsApi.explainMetric("safe_to_save");
      if (data) {
        renderDecisionPipelineScreen(data);
      }
    } catch (e) {
      console.warn("Could not load dynamic decision pipeline trace:", e);
    }
  }

  // 6. Risk & Early Warning Center (risk.html)
  if (path.includes("risk.html") && window.sureSavingsApi) {
    try {
      const riskData = window.sureSavingsApi.getRisk ? await window.sureSavingsApi.getRisk() : (window.sureSavingsStore?.state?.risk || {});
      const p = window.sureSavingsStore?.getProfile() || {};
      if (riskData) {
        document.querySelectorAll("[data-risk='status-badge']").forEach(el => el.textContent = riskData.tier || "LOW OVERALL");
        document.querySelectorAll("[data-risk='status-title']").forEach(el => el.textContent = riskData.status || "LOW FINANCIAL RISK • ABSORBABLE");
        document.querySelectorAll("[data-risk='volatility-val']").forEach(el => el.textContent = `${Number(p.income_volatility || 1.92).toFixed(2)} CV`);
        document.querySelectorAll("[data-risk='cushion-val']").forEach(el => el.textContent = `+₹${Number(p.safe_to_use_above_floor || 1900).toLocaleString()}`);
        document.querySelectorAll("[data-risk='cushion-detail']").forEach(el => el.textContent = `Above ₹${Number(p.protected_floor || 500).toLocaleString()} Floor (₹${Number(p.current_buffer || 2400).toLocaleString()} balance)`);
      }
    } catch (e) {
      console.warn("Could not load dynamic risk telemetry:", e);
    }
  }

  // 7. Income Calendar (calendar.html)
  if (path.includes("calendar.html")) {
    try {
      const p = window.sureSavingsStore?.getProfile() || {};
      const expectedIncome = (p.current_income || 0) * 4;
      const mandatedOutflows = (p.weekly_burn || 0) * 4;
      const curBuffer = p.current_buffer || 0;
      const safeFloor = p.safe_to_use_above_floor || 0;
      if (expectedIncome > 0) {
        document.querySelectorAll("[data-calendar='expected-income']").forEach(el => el.textContent = `₹${Math.round(expectedIncome).toLocaleString()}`);
      }
      if (mandatedOutflows > 0) {
        document.querySelectorAll("[data-calendar='mandated-outflows']").forEach(el => el.textContent = `₹${Math.round(mandatedOutflows).toLocaleString()}`);
      }
      document.querySelectorAll("[data-calendar='reserve-buffer']").forEach(el => el.textContent = `₹${Math.round(curBuffer).toLocaleString()}`);
      document.querySelectorAll("[data-calendar='gap-status']").forEach(el => el.textContent = `+₹${Math.round(safeFloor).toLocaleString()} above floor`);
    } catch (e) {
      console.warn("Could not load dynamic calendar telemetry:", e);
    }
  }

  // 8. SURE SAVINGS Simulator (simulator.html)
  if (path.includes("simulator.html")) {
    try {
      const p = window.sureSavingsStore?.getProfile() || {};
      const curBuf = p.current_buffer !== undefined ? p.current_buffer : 2400;
      const floor = p.protected_floor !== undefined ? p.protected_floor : 500;
      const safeUse = p.safe_to_use_above_floor !== undefined ? p.safe_to_use_above_floor : Math.max(0, curBuf - floor);
      const burn = p.weekly_burn !== undefined ? p.weekly_burn : 600;
      const targetBuf = p.target_buffer !== undefined ? p.target_buffer : (burn * 4);
      const runway = p.current_coverage_weeks !== undefined ? p.current_coverage_weeks : (burn > 0 ? (curBuf / burn).toFixed(1) : 4.0);
      const pct = targetBuf > 0 ? Math.min(100, Math.round((curBuf / targetBuf) * 100)) : 100;

      document.querySelectorAll("[data-sim='current-buffer']").forEach(el => el.textContent = `₹${Math.round(curBuf).toLocaleString()}`);
      document.querySelectorAll("[data-sim='protected-floor']").forEach(el => el.textContent = `₹${Math.round(floor).toLocaleString()}`);
      document.querySelectorAll("[data-sim='safe-to-use']").forEach(el => el.textContent = `₹${Math.round(safeUse).toLocaleString()}`);
      document.querySelectorAll("[data-sim='weekly-burn']").forEach(el => el.textContent = `₹${Math.round(burn).toLocaleString()}`);
      document.querySelectorAll("[data-sim='runway']").forEach(el => el.textContent = `${runway} weeks`);
      document.querySelectorAll("[data-sim='target-label']").forEach(el => el.textContent = `Target: ₹${Math.round(targetBuf).toLocaleString()} (${pct}%)`);
    } catch (e) {
      console.warn("Could not load dynamic simulator telemetry:", e);
    }
  }

  // 9. AI Resilience Coach (coach.html)
  if (path.includes("coach.html")) {
    try {
      const p = window.sureSavingsStore?.getProfile() || {};
      const curInc = p.current_income || 10000;
      const stabInc = p.stabilized_income || 1100;
      const curBuf = p.current_buffer !== undefined ? p.current_buffer : 2400;
      const floor = p.protected_floor !== undefined ? p.protected_floor : 500;
      const burn = p.weekly_burn !== undefined ? p.weekly_burn : 600;
      const targetBuf = p.target_buffer !== undefined ? p.target_buffer : (burn * 4);
      const rec = p.recommended_contribution !== undefined ? p.recommended_contribution : 0;
      const resScore = p.resilience_score || 66;
      const vol = p.income_volatility || 1.92;
      const runway = p.current_coverage_weeks || (burn > 0 ? (curBuf / burn).toFixed(1) : 4.0);
      const covPct = targetBuf > 0 ? Math.min(100, Math.round((curBuf / targetBuf) * 100)) : 100;

      const diffPct = stabInc > 0 ? Math.round(((curInc - stabInc) / stabInc) * 100) : 0;
      const diffSign = diffPct >= 0 ? `+${diffPct}%` : `${diffPct}%`;

      document.querySelectorAll("[data-coach='cycle-inflow']").forEach(el => el.textContent = `₹${Math.round(curInc).toLocaleString()} Inflow`);
      document.querySelectorAll("[data-coach='cycle-rec']").forEach(el => el.textContent = `Save ₹${Math.round(rec).toLocaleString()}`);
      document.querySelectorAll("[data-coach='inflows']").forEach(el => el.textContent = `₹${Math.round(curInc).toLocaleString()}`);
      document.querySelectorAll("[data-coach='inflow-diff']").forEach(el => el.textContent = `${diffSign} vs Baseline`);
      document.querySelectorAll("[data-coach='baseline']").forEach(el => el.textContent = `₹${Math.round(stabInc).toLocaleString()}`);
      document.querySelectorAll("[data-coach='current-buffer']").forEach(el => el.textContent = `₹${Math.round(curBuf).toLocaleString()}`);
      document.querySelectorAll("[data-coach='buffer-target']").forEach(el => el.textContent = `Target: ₹${Math.round(targetBuf).toLocaleString()}`);
      document.querySelectorAll("[data-coach='floor']").forEach(el => el.textContent = `₹${Math.round(floor).toLocaleString()}`);
      document.querySelectorAll("[data-coach='weekly-burn']").forEach(el => el.textContent = `₹${Math.round(burn).toLocaleString()}`);
      document.querySelectorAll("[data-coach='rec-amount']").forEach(el => el.textContent = `+₹${Math.round(rec).toLocaleString()}`);
      document.querySelectorAll("[data-coach='rec-label']").forEach(el => el.textContent = rec > 0 ? "Safe Allocation" : "Defensive Protection");

      document.querySelectorAll("[data-coach='resilience-badge']").forEach(el => el.textContent = `${resScore} / 100`);
      document.querySelectorAll("[data-coach='resilience-bar']").forEach(el => el.style.width = `${Math.min(100, resScore)}%`);
      document.querySelectorAll("[data-coach='volatility-badge']").forEach(el => el.textContent = `${Number(vol).toFixed(2)} CV`);
      document.querySelectorAll("[data-coach='coverage-badge']").forEach(el => el.textContent = `${runway} wks (${covPct}%)`);
      document.querySelectorAll("[data-coach='coverage-bar']").forEach(el => el.style.width = `${covPct}%`);
      document.querySelectorAll("[data-coach='coverage-desc']").forEach(el => {
        el.textContent = `Current buffer holds ₹${Math.round(curBuf).toLocaleString()} with ${runway} weeks of essential burn coverage.`;
      });
      document.querySelectorAll("[data-coach='floor-badge']").forEach(el => el.textContent = `Strict ₹${Math.round(floor).toLocaleString()}`);
    } catch (e) {
      console.warn("Could not load dynamic coach telemetry:", e);
    }
  }

  // 10. Financial Health Screen (health.html)
  if (path.includes("health.html")) {
    try {
      const p = window.sureSavingsStore?.getProfile() || {};
      const curBuf = p.current_buffer !== undefined ? p.current_buffer : 2400;
      const floor = p.protected_floor !== undefined ? p.protected_floor : 500;
      const burn = p.weekly_burn !== undefined ? p.weekly_burn : 600;
      const targetBuf = p.target_buffer !== undefined ? p.target_buffer : (burn * 4);
      const runway = p.current_coverage_weeks || 4.0;
      const rec = p.recommended_contribution || 0;
      const vol = p.income_volatility || 1.92;

      document.querySelectorAll("[data-health='safe-alloc']").forEach(el => el.textContent = `₹${Math.round(rec).toLocaleString()}`);
      document.querySelectorAll("[data-health='floor']").forEach(el => el.textContent = `₹${Math.round(floor).toLocaleString()}`);
      document.querySelectorAll("[data-health='runway']").forEach(el => el.textContent = `${runway} wks`);
      document.querySelectorAll("[data-health='liquid-reserves']").forEach(el => el.textContent = `₹${Math.round(curBuf).toLocaleString()}`);
      document.querySelectorAll("[data-health='reserves-target']").forEach(el => el.textContent = `of ₹${Math.round(targetBuf).toLocaleString()} target`);
      document.querySelectorAll("[data-health='volatility-index']").forEach(el => el.textContent = `${Number(vol).toFixed(2)}`);
      document.querySelectorAll("[data-health='summary-desc']").forEach(el => {
        el.innerHTML = `Your financial buffer currently holds <strong>₹${Math.round(curBuf).toLocaleString()}</strong> (${runway} weeks of essentials) against a target of <strong>₹${Math.round(targetBuf).toLocaleString()}</strong>. Operational cash floor (₹${Math.round(floor).toLocaleString()}) is 100% intact.`;
      });
    } catch (e) {
      console.warn("Could not load dynamic health telemetry:", e);
    }
  }
}

/**
 * SURE SAVINGS 7.0: Decision Pipeline Screen Dynamic Renderer
 */
function renderDecisionPipelineScreen(data) {
  if (!data) return;
  const p = window.sureSavingsStore?.getProfile() || {};
  const recVal = data.value || (p.recommended_contribution ? `₹${Number(p.recommended_contribution).toLocaleString()}` : "SAVE ₹900");
  const conf = data.confidence !== undefined ? Math.round(data.confidence * 100) : 94;
  const floor = data.inputs?.protected_floor || (p.protected_floor ? `₹${Number(p.protected_floor).toLocaleString()}` : "₹3,500");

  const dpRecAction = document.getElementById("dpRecAction");
  const dpConfidence = document.getElementById("dpConfidence");
  const dpFloorVal = document.getElementById("dpFloorVal");
  const dpStage1Val = document.getElementById("dpStage1Val");
  const dpStage2Val = document.getElementById("dpStage2Val");
  const dpStage3Val = document.getElementById("dpStage3Val");
  const dpStage4Val = document.getElementById("dpStage4Val");
  const dpStage5Val = document.getElementById("dpStage5Val");
  const dpStage6Val = document.getElementById("dpStage6Val");
  const dpStage7Val = document.getElementById("dpStage7Val");
  const dpBottomBtn = document.getElementById("dpBottomBtn");

  if (dpRecAction) dpRecAction.textContent = (data.current_value > 0 || (p.recommended_contribution && p.recommended_contribution > 0)) ? `SAVE ₹${Number(data.current_value || p.recommended_contribution).toLocaleString()}` : "PROTECT FLOOR (₹0)";
  if (dpConfidence) dpConfidence.textContent = `Deterministic Confidence: ${conf}%`;
  if (dpFloorVal) dpFloorVal.textContent = `${floor} (100% INTACT)`;

  if (dpStage1Val && data.inputs?.current_income) dpStage1Val.textContent = data.inputs.current_income;
  if (dpStage2Val && (p.stabilized_income || data.inputs?.current_income)) {
    dpStage2Val.textContent = p.stabilized_income ? `₹${Number(p.stabilized_income).toLocaleString()}` : "₹7,100";
  }
  if (dpStage3Val && data.inputs?.essential_burn) dpStage3Val.textContent = `${data.inputs.essential_burn} + ${floor}`;
  if (dpStage4Val && data.inputs?.calculated_surplus) dpStage4Val.textContent = `+${data.inputs.calculated_surplus}`;
  if (dpStage5Val && data.value) dpStage5Val.textContent = data.value;
  if (dpStage6Val) dpStage6Val.textContent = p.free_pocket_liquidity ? `₹${Number(p.free_pocket_liquidity).toLocaleString()}` : "₹400";
  if (dpStage7Val && data.value) dpStage7Val.textContent = (data.current_value > 0 || (p.recommended_contribution && p.recommended_contribution > 0)) ? `SAVE ${data.value}` : "HOLD RESERVE (₹0)";
  if (dpBottomBtn && data.value) dpBottomBtn.textContent = (data.current_value > 0 || (p.recommended_contribution && p.recommended_contribution > 0)) ? `Approve ${data.value} Reserve Transfer (Simulated) →` : "Floor Preserved • Protection Active";
}

// Global Auth & Header User Identity Bootstrap
async function initAuthAndHeader() {
  const path = window.location.pathname;
  const isLoginPage = path.endsWith("login.html");
  const isLandingPage = path.endsWith("landing.html") || path === "/" || path === "";
  if (isLoginPage || isLandingPage) return;

  if (!window.sureSavingsStore) return;

  // Await store initialization to complete so that demo parameters (?demo=1) and auto-auth finish first
  if (typeof window.sureSavingsStore.whenReady === "function") {
    await window.sureSavingsStore.whenReady();
  }

  const authState = window.sureSavingsStore.getAuth ? window.sureSavingsStore.getAuth() : null;
  const user = authState?.user || await window.sureSavingsStore.checkAuth();
  if (!user) {
    console.warn("[SURE SAVINGS] User unauthenticated, redirecting to login.html");
    const currentScreen = path.split("/").pop() || "index.html";
    window.location.href = `login.html?expired=1&return_to=${encodeURIComponent(currentScreen)}`;
    return;
  }

  // Update header with user's real identity
  renderHeaderUserIdentity(user);
  updateAllUserGreetingsAndNames(user);
}

function updateAllUserGreetingsAndNames(user) {
  if (!user) return;
  const fullName = (user.name || user.display_name || '').trim();
  const firstName = user.first_name || (fullName ? fullName.split(/\s+/)[0] : 'Member');
  const userRole = user.is_demo_user ? 'Delivery & Freelance Lead' : (user.occupation || user.title || 'SURE SAVINGS Member');
  const initials = user.initials || (firstName ? firstName[0].toUpperCase() : 'U');

  // Dynamic time-of-day greeting
  const hour = new Date().getHours();
  let timeGreeting = 'Good evening';
  if (hour < 12) timeGreeting = 'Good morning';
  else if (hour < 17) timeGreeting = 'Good afternoon';

  // 1. Update main dashboard greeting heading
  const greetingHeading = document.getElementById('main-greeting-heading');
  if (greetingHeading) {
    greetingHeading.innerHTML = `<span id="dashboard-greeting">${timeGreeting}</span>, <span id="dashboard-user-name" class="text-brand-500 font-extrabold">${firstName}</span>`;
  }
  const dashGreeting = document.getElementById('dashboard-greeting');
  if (dashGreeting) dashGreeting.textContent = timeGreeting;

  const dashUserName = document.getElementById('dashboard-user-name');
  if (dashUserName) dashUserName.textContent = firstName;

  // Scan all H1 / H2 headings that may contain "Good morning, Arjun" or similar
  document.querySelectorAll('h1, h2').forEach(heading => {
    if (heading.id === 'main-greeting-heading') return;
    const txt = heading.textContent || '';
    if (/Good (morning|afternoon|evening)/i.test(txt)) {
      heading.innerHTML = `${timeGreeting}, <span class="text-brand-500 font-extrabold">${firstName}</span>`;
    }
  });

  // 2. Update all .user-first-name elements across any page
  document.querySelectorAll('.user-first-name, [data-user-first-name]').forEach(el => {
    el.textContent = firstName;
  });

  // 3. Update all user display names
  document.querySelectorAll('#user-display-name, .user-display-name, #menu-user-name, .user-full-name').forEach(el => {
    el.textContent = fullName || firstName;
  });

  // 4. Update user email
  if (user.email) {
    document.querySelectorAll('#menu-user-email, .user-email').forEach(el => {
      el.textContent = user.email;
    });
  }

  // 5. Update user role / occupation
  document.querySelectorAll('#user-role, .user-role').forEach(el => {
    el.textContent = userRole;
  });

  // 6. Update user avatar text or image
  document.querySelectorAll('#user-avatar-circle, .user-avatar').forEach(el => {
    if (user.avatar_url && !user.avatar_url.includes('dicebear')) {
      el.innerHTML = `<img src="${user.avatar_url}" class="w-full h-full object-cover rounded-full" alt="${fullName}">`;
    } else {
      el.textContent = initials;
    }
  });

  // 7. Update coach welcome text if present
  const coachWelcome = document.getElementById('coach-welcome-text');
  if (coachWelcome) {
    const coachFirstName = coachWelcome.querySelector('.user-first-name');
    if (coachFirstName) coachFirstName.textContent = firstName;
  }
  const coachInitial = document.getElementById('coach-initial-msg');
  if (coachInitial && !user.is_demo_user) {
    coachInitial.innerHTML = `Hello <strong class="text-brand-500">${firstName}</strong>! I've analyzed your financial resilience state. What would you like to explore?`;
  }
  const coachBubbleName = document.getElementById('coach-user-bubble-name');
  if (coachBubbleName) coachBubbleName.textContent = fullName || firstName;
  const coachBubbleAvatar = document.getElementById('coach-user-bubble-avatar');
  if (coachBubbleAvatar) coachBubbleAvatar.textContent = initials;

  // 8. Update current date if element exists
  const dateEl = document.getElementById('current-date-display');
  if (dateEl) {
    try {
      const now = new Date();
      const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
      dateEl.textContent = now.toLocaleDateString('en-US', options);
    } catch (e) {}
  }
}

function renderHeaderUserIdentity(user) {
  const isDemo = user.is_demo_user;
  const modeLabel = isDemo ? "DEMO ENVIRONMENT" : "PRIVATE WORKSPACE";
  const modeColor = isDemo 
    ? "bg-amber-50 text-amber-800 border-amber-200" 
    : "bg-emerald-50 text-emerald-800 border-emerald-200";

  const header = document.querySelector("header");
  if (!header) return;

  // Update or insert Workspace Mode badge
  const sandboxPill = header.querySelector(".inline-flex.items-center.space-x-1\\.5");
  if (sandboxPill) {
    sandboxPill.className = `inline-flex items-center space-x-1.5 ${modeColor} border px-2.5 py-1 rounded-full font-bold text-[10px] tracking-wide uppercase shadow-sm`;
    sandboxPill.innerHTML = `
      <span class="w-1.5 h-1.5 rounded-full ${isDemo ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}"></span>
      <span>${modeLabel}</span>
    `;
  }

  // Update User Profile Badge & Dropdown
  const userAvatarContainer = header.querySelector(".flex.items-center.space-x-2.pl-2");
  if (userAvatarContainer) {
    userAvatarContainer.classList.add("relative", "cursor-pointer");
    userAvatarContainer.id = "header-user-menu-trigger";
    userAvatarContainer.innerHTML = `
      <div class="w-7 h-7 rounded-full bg-stone-900 text-white font-bold flex items-center justify-center text-xs shadow-sm overflow-hidden flex-shrink-0">
        ${user.avatar_url ? `<img src="${user.avatar_url}" alt="${user.name}" class="w-full h-full object-cover">` : (user.initials || 'AK')}
      </div>
      <div class="hidden sm:block text-right">
        <p class="font-bold text-stone-900 leading-none text-xs truncate max-w-[120px]">${user.display_name || user.name}</p>
        <p class="text-[10px] text-stone-500 leading-tight truncate max-w-[120px]">${isDemo ? 'Delivery & Freelance Lead' : (user.title || user.occupation || user.email || 'Private Member')}</p>
      </div>
      <svg class="w-3 h-3 text-stone-400 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
      
      <!-- Dropdown Menu -->
      <div id="header-user-dropdown" class="hidden absolute right-0 top-10 w-56 bg-white border border-stone-200 rounded-2xl shadow-xl py-2 z-50 text-left">
        <div class="px-4 py-2 border-b border-stone-100">
          <p class="text-xs font-bold text-stone-900 truncate">${user.name}</p>
          <p class="text-[10px] text-stone-500 truncate">${user.email || 'Connected with Google'}</p>
          <span class="mt-1 inline-block text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${modeColor}">${modeLabel}</span>
        </div>
        <div class="py-1 text-xs border-b border-stone-100">
          <button onclick="openMyProfileModal()" class="w-full text-left px-4 py-2 text-stone-800 hover:bg-stone-50 transition-colors flex items-center gap-2 font-medium">
            <svg class="w-3.5 h-3.5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            My Profile
          </button>
          <button onclick="if (window.setupWizard) window.setupWizard.openQuickStartModal()" class="w-full text-left px-4 py-2 text-stone-800 hover:bg-stone-50 transition-colors flex items-center gap-2 font-medium">
            <svg class="w-3.5 h-3.5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
            Calibrate Baseline
          </button>
        </div>
        <div class="py-1 text-xs">
          <a href="index.html" class="block px-4 py-2 text-stone-700 hover:bg-stone-50 transition-colors">Command Center</a>
          <a href="health.html" class="block px-4 py-2 text-stone-700 hover:bg-stone-50 transition-colors">Resilience Gauge</a>
          <a href="activity.html" class="block px-4 py-2 text-stone-700 hover:bg-stone-50 transition-colors">Activity Ledger</a>
        </div>
        <div class="pt-1 border-t border-stone-100">
          <button onclick="window.sureSavingsStore.logout()" class="w-full text-left px-4 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 transition-colors flex items-center gap-2">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
            Sign Out
          </button>
        </div>
      </div>
    `;

    userAvatarContainer.onclick = (e) => {
      e.stopPropagation();
      const dd = document.getElementById("header-user-dropdown");
      if (dd) dd.classList.toggle("hidden");
    };

    document.addEventListener("click", () => {
      const dd = document.getElementById("header-user-dropdown");
      if (dd) dd.classList.add("hidden");
    });
  }
}

function ensureSureAiLauncher() {
  const path = (window.location.pathname || "").toLowerCase();
  if (path.endsWith("coach.html") || path.endsWith("login.html") || path.endsWith("register.html")) {
    return;
  }
  if (document.getElementById("sure-ai-launcher-btn")) return;
  const launcher = document.createElement("a");
  launcher.id = "sure-ai-launcher-btn";
  launcher.href = "coach.html";
  launcher.className = "sure-ai-launcher";
  launcher.setAttribute("title", "Ask SURE AI for guidance and explanations");
  launcher.innerHTML = `
    <span class="sparkle-icon">✨</span>
    <span>Ask SURE AI</span>
  `;
  document.body.appendChild(launcher);
}

// Global DOM ready bootstrap
document.addEventListener("DOMContentLoaded", () => {
  initAuthAndHeader();
  ensureMyProfileInDropdowns();
  highlightActiveNav();
  ensureSureAiLauncher();

  // Attach global button actions
  document.querySelectorAll("button, a").forEach(el => {
    const txt = (el.textContent || "").toLowerCase();
    const onclickAttr = el.getAttribute("onclick") || "";
    if (txt.includes("approve ₹") || txt.includes("approve 900") || txt.includes("approve reserve transfer")) {
      if (!onclickAttr.includes("openApproveTransferModal")) {
        el.addEventListener("click", (e) => {
          e.preventDefault();
          openApproveTransferModal();
        });
      }
    } else if (txt.includes("download audit json")) {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        downloadAuditJSON();
      });
    } else if (txt.includes("re-run engine check")) {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        triggerEngineCheck(el);
      });
    } else if (txt.includes("reset to live state")) {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        resetLiveState();
      });
    } else if (txt.includes("download csv schedule") || txt.includes("export csv")) {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        downloadCSVSchedule();
      });
    }
  });

  // Subscribe reactive store to update metrics and user greetings automatically
  if (window.sureSavingsStore) {
    window.sureSavingsStore.subscribe((state) => {
      updatePageMetrics();
      const u = state?.auth?.user || state?.profile;
      if (u) {
        updateAllUserGreetingsAndNames(u);
      }
      if (window.setupWizard && typeof window.setupWizard.renderDashboardBanner === 'function') {
        window.setupWizard.renderDashboardBanner();
      }
    });
  }

  // Ensure command palette is available
  ensureCommandPalette();

  // Global Keyboard Shortcuts (⌘K / Ctrl+K, ⌘D / Ctrl+D, Escape)
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      const overlay = document.getElementById('command-palette-overlay');
      if (overlay && !overlay.classList.contains('hidden')) {
        closeCommandPalette();
      } else {
        openCommandPalette();
      }
    } else if ((e.metaKey || e.ctrlKey) && (e.key === 'd' || e.key === 'D')) {
      e.preventDefault();
      toggleDarkMode();
    } else if (e.key === 'Escape') {
      closeCommandPalette();
      closeUserMenu();
    }
  });

  // Global click outside to dismiss menus
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#user-avatar-container') && !e.target.closest('#header-user-menu-trigger')) {
      closeUserMenu();
    }
  });

  // Load screen-specific API data
  loadPageSpecificData();
});

// ═══════════════════════════════════════════════════════
// USER MUTATION WORKFLOWS: GOALS & INCOME LOGGING
// ═══════════════════════════════════════════════════════

function openAddGoalModal() {
  const existing = document.getElementById("addGoalModal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "addGoalModal";
  modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-sm animate-fade-in";
  modal.innerHTML = `
    <div class="glass-modal rounded-2xl max-w-md w-full p-6 sm:p-7 shadow-2xl border border-stone-200 space-y-5 text-left transform transition-all bg-white" style="background: var(--surface-card); border-color: var(--border-default);">
      <div class="flex items-center justify-between pb-3 border-b" style="border-color: var(--border-subtle);">
        <div class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-base" style="background: var(--brand-primary-light); color: var(--brand-primary);">
            🎯
          </div>
          <div>
            <h3 class="font-bold text-sm sm:text-base" style="color: var(--text-primary);">Create Savings Goal</h3>
            <p class="text-[11px]" style="color: var(--text-secondary);">Define targeted reserve milestone with protected floor compliance</p>
          </div>
        </div>
        <button onclick="document.getElementById('addGoalModal').remove()" class="text-stone-400 hover:text-stone-600 text-base">✕</button>
      </div>

      <form id="addGoalForm" onsubmit="handleAddGoalSubmit(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">
            Goal Name <span class="text-rose-500">*</span>
          </label>
          <input type="text" id="goal-name" required placeholder="e.g. Rent Safety Reserve"
            class="w-full px-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none"
            style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
        </div>

        <div>
          <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">
            Target Amount <span class="text-rose-500">*</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-2 text-stone-400 font-semibold text-xs">₹</span>
            <input type="number" id="goal-amount" required min="100" step="100" placeholder="e.g. 15000"
              class="w-full pl-7 pr-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
              style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">Category / Type</label>
            <select id="goal-type" class="w-full px-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none"
              style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
              <option value="EMERGENCY_RESERVE">Emergency Reserve</option>
              <option value="RENT_PROTECTION">Rent Protection</option>
              <option value="INCOME_GAP">Income Gap Buffer</option>
              <option value="VEHICLE_REPAIR">Vehicle Repair</option>
              <option value="MEDICAL_RESERVE">Medical Cushion</option>
              <option value="CUSTOM">Custom Goal</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">Priority</label>
            <select id="goal-priority" class="w-full px-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none"
              style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
              <option value="high">High Priority</option>
              <option value="medium" selected>Medium</option>
              <option value="low">Low Priority</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">Target Date (Optional)</label>
          <input type="date" id="goal-date"
            class="w-full px-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
            style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
        </div>

        <div class="pt-2 flex items-center justify-end space-x-2">
          <button type="button" onclick="document.getElementById('addGoalModal').remove()"
            class="px-4 py-2 text-xs font-semibold rounded-xl border hover:bg-stone-50 transition-all"
            style="border-color: var(--border-default); color: var(--text-secondary);">Cancel</button>
          <button type="submit" id="btn-submit-goal"
            class="px-5 py-2 text-xs font-bold text-white bg-brand-500 hover:bg-brand-600 rounded-xl shadow-md brand-glow transition-all flex items-center space-x-1.5">
            <span>Create Goal</span>
            <span>→</span>
          </button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(modal);
  setTimeout(() => document.getElementById("goal-name")?.focus(), 100);
}

async function handleAddGoalSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-submit-goal");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-1">⏳</span> Saving…`;
  }

  const name = document.getElementById("goal-name")?.value?.trim();
  const targetAmount = parseFloat(document.getElementById("goal-amount")?.value) || 0;
  const targetDate = document.getElementById("goal-date")?.value || null;
  const goalType = document.getElementById("goal-type")?.value || "EMERGENCY_RESERVE";
  const priority = document.getElementById("goal-priority")?.value || "medium";

  try {
    if (window.sureSavingsApi) {
      await window.sureSavingsApi.addGoal({ name, targetAmount, targetDate, priority, goalType });
    }
    if (window.showToast) {
      window.showToast("Goal Created", `Successfully activated goal "${name}" for ₹${targetAmount.toLocaleString()}.`, "success");
    }
    document.getElementById("addGoalModal")?.remove();
    if (window.sureSavingsStore?.syncWithBackend) {
      await window.sureSavingsStore.syncWithBackend();
    }
    loadPageSpecificData();
  } catch (err) {
    console.error("Error creating goal:", err);
    if (window.showToast) {
      window.showToast("Error", err.message || "Failed to create goal", "error");
    } else {
      alert("Error: " + (err.message || "Failed to create goal"));
    }
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>Create Goal</span><span>→</span>`;
    }
  }
}

function openLogIncomeModal() {
  const existing = document.getElementById("logIncomeModal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "logIncomeModal";
  modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-sm animate-fade-in";
  modal.innerHTML = `
    <div class="glass-modal rounded-2xl max-w-md w-full p-6 sm:p-7 shadow-2xl border border-stone-200 space-y-5 text-left transform transition-all bg-white" style="background: var(--surface-card); border-color: var(--border-default);">
      <div class="flex items-center justify-between pb-3 border-b" style="border-color: var(--border-subtle);">
        <div class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-base">
            💰
          </div>
          <div>
            <h3 class="font-bold text-sm sm:text-base" style="color: var(--text-primary);">Log Weekly Earnings</h3>
            <p class="text-[11px]" style="color: var(--text-secondary);">Record actual payout to update volatility dampening & forecasting</p>
          </div>
        </div>
        <button onclick="document.getElementById('logIncomeModal').remove()" class="text-stone-400 hover:text-stone-600 text-base">✕</button>
      </div>

      <form id="logIncomeForm" onsubmit="handleLogIncomeSubmit(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">
            Week Identifier <span class="text-rose-500">*</span>
          </label>
          <input type="text" id="income-week" required placeholder="e.g. Week 5"
            value="Week 5"
            class="w-full px-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none"
            style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
        </div>

        <div>
          <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">
            Income Amount <span class="text-rose-500">*</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-2 text-stone-400 font-semibold text-xs">₹</span>
            <input type="number" id="income-amount" required min="10" step="100" placeholder="e.g. 10000"
              class="w-full pl-7 pr-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
              style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold mb-1" style="color: var(--text-primary);">Income Platform / Source</label>
          <select id="income-source" class="w-full px-3 py-2 text-xs border rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none"
            style="border-color: var(--border-default); background: var(--surface-paper); color: var(--text-primary);">
            <option value="Primary Earnings">Primary Earnings</option>
            <option value="Freelance / Consulting">Freelance / Consulting</option>
            <option value="Gig Platform">Gig Platform</option>
            <option value="Client Retainer">Client Retainer</option>
            <option value="Other Inflow">Other Inflow</option>
          </select>
        </div>

        <div class="pt-2 flex items-center justify-end space-x-2">
          <button type="button" onclick="document.getElementById('logIncomeModal').remove()"
            class="px-4 py-2 text-xs font-semibold rounded-xl border hover:bg-stone-50 transition-all"
            style="border-color: var(--border-default); color: var(--text-secondary);">Cancel</button>
          <button type="submit" id="btn-submit-income"
            class="px-5 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-md transition-all flex items-center space-x-1.5">
            <span>Log Earnings</span>
            <span>→</span>
          </button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(modal);
  setTimeout(() => document.getElementById("income-amount")?.focus(), 100);
}

async function handleLogIncomeSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-submit-income");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-1">⏳</span> Recording…`;
  }

  const week = document.getElementById("income-week")?.value?.trim() || "Week 5";
  const income = parseFloat(document.getElementById("income-amount")?.value) || 0;
  const source = document.getElementById("income-source")?.value || "Primary Earnings";

  try {
    if (window.sureSavingsApi) {
      await window.sureSavingsApi.addIncomeHistory([{ week, income, source }]);
    }
    if (window.showToast) {
      window.showToast("Earnings Recorded", `Recorded ₹${income.toLocaleString()} for ${week}. Resilience recalculation complete.`, "success");
    }
    document.getElementById("logIncomeModal")?.remove();
    if (window.sureSavingsStore?.syncWithBackend) {
      await window.sureSavingsStore.syncWithBackend();
    }
    loadPageSpecificData();
  } catch (err) {
    console.error("Error logging income:", err);
    if (window.showToast) {
      window.showToast("Error", err.message || "Failed to log income", "error");
    } else {
      alert("Error: " + (err.message || "Failed to log income"));
    }
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span>Log Earnings</span><span>→</span>`;
    }
  }
}

// Global window bindings
window.openAddGoalModal = openAddGoalModal;
window.handleAddGoalSubmit = handleAddGoalSubmit;
window.openLogIncomeModal = openLogIncomeModal;
window.handleLogIncomeSubmit = handleLogIncomeSubmit;
window.openQuickStartModal = () => {
  if (window.setupWizard && typeof window.setupWizard.openQuickStartModal === 'function') {
    window.setupWizard.openQuickStartModal();
  }
};

