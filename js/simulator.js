/**
 * SURE SAVINGS 7.0: What-If Scenario Engine 2.0
 * Backed by ScenarioService and unified store.
 * Multi-variable parametric simulation: income variance, expense inflation, one-off shocks,
 * timing delays, and baseline vs scenario comparative trajectories.
 */

let simState = {
  income_delta_pct: 0,
  expense_delta_pct: 0,
  one_off_shock: 0,
  delayed_payout_days: 0,
  simulation_weeks: 4,
  contribution: 900,
  withdrawal: 0
};

let scenarioLibraryCache = [];
let simDebounceTimer = null;

async function initScenarioLibrary() {
  const container = document.getElementById("scenarioLibraryButtons");
  if (!container || !window.sureSavingsApi) return;

  try {
    const res = await window.sureSavingsApi.getScenarioLibrary();
    if (res && res.scenarios && res.scenarios.length > 0) {
      scenarioLibraryCache = res.scenarios;
      container.innerHTML = res.scenarios.map(s => `
        <button onclick="applyPreset('${s.id}')" id="btn-preset-${s.id}" class="p-2.5 text-left rounded-xl border transition-all hover:border-brand-500/50 bg-stone-50 border-stone-200" type="button">
          <span class="text-[11px] font-bold block ${s.color || 'text-stone-800'}">${s.name || s.id}</span>
          <span class="text-[10px] text-stone-500 block truncate leading-tight mt-0.5">${s.description || ''}</span>
        </button>
      `).join("");
    }
  } catch (e) {
    console.warn("[SURE SAVINGS Simulator] Could not load scenario library, using pre-configured presets:", e);
  }
}

function applyPreset(presetId) {
  const preset = scenarioLibraryCache.find(s => s.id === presetId);
  const label = document.getElementById("presetActiveLabel");

  if (preset) {
    if (label) label.textContent = `Active: ${preset.name}`;
    simState.income_delta_pct = preset.income_delta_pct || 0;
    simState.expense_delta_pct = preset.expense_delta_pct || 0;
    simState.one_off_shock = preset.one_off_shock || 0;
    simState.delayed_payout_days = preset.delayed_payout_days || 0;
    simState.simulation_weeks = preset.simulation_weeks || 4;
  } else {
    // Fallbacks
    if (presetId === 'mild_drop') {
      simState.income_delta_pct = -15;
      simState.expense_delta_pct = 0;
      simState.one_off_shock = 0;
      simState.delayed_payout_days = 0;
      if (label) label.textContent = "Active: Mild Drop (-15%)";
    } else if (presetId === 'severe_shock') {
      simState.income_delta_pct = -40;
      simState.expense_delta_pct = 0;
      simState.one_off_shock = 0;
      simState.delayed_payout_days = 0;
      if (label) label.textContent = "Active: Severe Shock (-40%)";
    } else if (presetId === 'delayed_payout') {
      simState.income_delta_pct = 0;
      simState.expense_delta_pct = 0;
      simState.one_off_shock = 0;
      simState.delayed_payout_days = 7;
      if (label) label.textContent = "Active: Delayed Payout (7 days)";
    } else if (presetId === 'emergency_repair') {
      simState.income_delta_pct = 0;
      simState.expense_delta_pct = 0;
      simState.one_off_shock = 3500;
      simState.delayed_payout_days = 0;
      if (label) label.textContent = "Active: Emergency Repair (₹3,500)";
    } else if (presetId === 'aggressive_saving') {
      simState.income_delta_pct = 20;
      simState.expense_delta_pct = 0;
      simState.one_off_shock = 0;
      simState.delayed_payout_days = 0;
      if (label) label.textContent = "Active: Surplus Surge (+20%)";
    }
  }

  // Update slider UI controls
  syncSlidersFromState();

  // Highlight active preset button
  document.querySelectorAll("#scenarioLibraryButtons button").forEach(btn => {
    btn.classList.remove("border-brand-500", "bg-brand-50");
  });
  const activeBtn = document.getElementById(`btn-preset-${presetId}`);
  if (activeBtn) {
    activeBtn.classList.add("border-brand-500", "bg-brand-50");
  }

  runSimulation();
}

function syncSlidersFromState() {
  const sInc = document.getElementById("sliderIncomeDelta");
  const vInc = document.getElementById("valIncomeDelta");
  if (sInc) sInc.value = simState.income_delta_pct;
  if (vInc) vInc.textContent = `${simState.income_delta_pct > 0 ? '+' : ''}${simState.income_delta_pct}%`;

  const sExp = document.getElementById("sliderExpenseDelta");
  const vExp = document.getElementById("valExpenseDelta");
  if (sExp) sExp.value = simState.expense_delta_pct;
  if (vExp) vExp.textContent = `${simState.expense_delta_pct > 0 ? '+' : ''}${simState.expense_delta_pct}%`;

  const iShock = document.getElementById("inputOneOffShock");
  const vShock = document.getElementById("valShockAmount");
  if (iShock) iShock.value = simState.one_off_shock;
  if (vShock) vShock.textContent = `₹${simState.one_off_shock.toLocaleString()}`;

  const sDelay = document.getElementById("sliderDelayDays");
  const vDelay = document.getElementById("valDelayDays");
  if (sDelay) sDelay.value = simState.delayed_payout_days;
  if (vDelay) vDelay.textContent = `${simState.delayed_payout_days} days`;

  const sWeeks = document.getElementById("sliderSimWeeks");
  const vWeeks = document.getElementById("valSimWeeks");
  if (sWeeks) sWeeks.value = simState.simulation_weeks;
  if (vWeeks) vWeeks.textContent = `${simState.simulation_weeks} weeks`;
}

function resetToLiveState() {
  simState = {
    income_delta_pct: 0,
    expense_delta_pct: 0,
    one_off_shock: 0,
    delayed_payout_days: 0,
    simulation_weeks: 4,
    contribution: 900,
    withdrawal: 0
  };
  const label = document.getElementById("presetActiveLabel");
  if (label) label.textContent = "Active: Baseline Live State";

  document.querySelectorAll("#scenarioLibraryButtons button").forEach(btn => {
    btn.classList.remove("border-brand-500", "bg-brand-50");
  });

  syncSlidersFromState();
  runSimulation();
}

async function runSimulation() {
  if (simDebounceTimer) clearTimeout(simDebounceTimer);

  simDebounceTimer = setTimeout(async () => {
    if (!window.sureSavingsApi) return;

    try {
      const res = await window.sureSavingsApi.runScenarioSimulation({
        income_delta_pct: simState.income_delta_pct,
        expense_delta_pct: simState.expense_delta_pct,
        one_off_shock: simState.one_off_shock,
        delayed_payout_days: simState.delayed_payout_days,
        simulation_weeks: simState.simulation_weeks,
        contribution: simState.contribution,
        withdrawal: simState.withdrawal
      });

      const r = res?.results;
      if (r) {
        renderSimulationResults(r);
      }
    } catch (err) {
      console.warn("[SURE SAVINGS Simulator] API simulation error:", err);
    }
  }, 75);
}

function renderSimulationResults(r) {
  const elBaseBuffer = document.getElementById("simBaselineBuffer");
  const elEndingBuffer = document.getElementById("simEndingBuffer");
  const elBufferDelta = document.getElementById("simBufferDelta");
  const elMinBuffer = document.getElementById("simMinBuffer");
  const elRunway = document.getElementById("simRunway");
  const elRunwayDelta = document.getElementById("simRunwayDelta");
  const elScore = document.getElementById("simScore");
  const elScoreDelta = document.getElementById("simScoreDelta");
  const elDaysToFloor = document.getElementById("simDaysToFloor");
  const elFloorStatusBadge = document.getElementById("simFloorStatusBadge");
  const elScenarioNote = document.getElementById("simScenarioNote");
  const elImpactBadge = document.getElementById("simImpactBadge");

  const prof = window.sureSavingsStore?.getProfile() || {};
  const baseBuf = r.baseline_ending_buffer !== undefined ? r.baseline_ending_buffer : (prof.current_buffer || 2400);
  const endBuf = r.scenario_ending_buffer !== undefined ? r.scenario_ending_buffer : (r.simulated_buffer !== undefined ? r.simulated_buffer : baseBuf);
  const deltaBuf = r.buffer_delta !== undefined ? r.buffer_delta : (endBuf - baseBuf);
  const activeFloor = prof.protected_floor || 500;

  if (elBaseBuffer) elBaseBuffer.textContent = `₹${Math.round(baseBuf).toLocaleString()}`;
  if (elEndingBuffer) elEndingBuffer.textContent = `₹${Math.round(endBuf).toLocaleString()}`;
  if (elBufferDelta) {
    elBufferDelta.textContent = deltaBuf >= 0 ? `+₹${Math.round(deltaBuf).toLocaleString()}` : `-₹${Math.round(Math.abs(deltaBuf)).toLocaleString()}`;
    elBufferDelta.className = deltaBuf >= 0
      ? "text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700"
      : "text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-100 text-rose-700";
  }

  if (elMinBuffer) {
    elMinBuffer.textContent = `₹${Math.round(r.min_buffer_reached !== undefined ? r.min_buffer_reached : endBuf).toLocaleString()}`;
  }
  const elMinFloor = document.getElementById("simMinFloorText");
  if (elMinFloor) {
    const clearance = (r.min_buffer_reached !== undefined ? r.min_buffer_reached : endBuf) - activeFloor;
    elMinFloor.textContent = clearance >= 0 ? `Above ₹${activeFloor.toLocaleString()} Floor` : `Below ₹${activeFloor.toLocaleString()} Floor`;
  }

  if (elRunway) elRunway.textContent = `${r.runway_weeks} weeks`;
  if (elRunwayDelta) {
    const rwDelta = r.runway_delta !== undefined ? r.runway_delta : +(r.runway_weeks - 1.5).toFixed(1);
    elRunwayDelta.textContent = rwDelta >= 0 ? `+${rwDelta} wks` : `${rwDelta} wks`;
    elRunwayDelta.className = rwDelta >= 0
      ? "text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700"
      : "text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-100 text-rose-700";
  }

  if (elScore) elScore.textContent = `${r.resilience_score}/100`;
  if (elScoreDelta) {
    const sDelta = r.resilience_delta || 0;
    elScoreDelta.textContent = sDelta >= 0 ? `+${sDelta} pts` : `${sDelta} pts`;
    elScoreDelta.className = sDelta >= 0
      ? "text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700"
      : "text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-100 text-rose-700";
  }

  if (elDaysToFloor) {
    if (r.days_to_breach_floor !== null && r.days_to_breach_floor !== undefined) {
      elDaysToFloor.textContent = `Breached in ${r.days_to_breach_floor} days`;
      elDaysToFloor.className = "text-xs font-black font-mono text-rose-600";
    } else {
      elDaysToFloor.textContent = "Infinite (Safe)";
      elDaysToFloor.className = "text-xs font-black font-mono text-emerald-700";
    }
  }

  if (elFloorStatusBadge) {
    if (r.breached_floor) {
      elFloorStatusBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500 mr-1.5 animate-pulse"></span> Floor Breached`;
      elFloorStatusBadge.className = "text-[11px] font-bold text-rose-600 flex items-center";
    } else {
      elFloorStatusBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span> Floor Protected`;
      elFloorStatusBadge.className = "text-[11px] font-bold text-emerald-600 flex items-center";
    }
  }

  if (elScenarioNote && r.defensive_action) {
    elScenarioNote.textContent = r.defensive_action;
  }

  if (elImpactBadge) {
    const activeShocks = [];
    if (simState.income_delta_pct !== 0) activeShocks.push(`Income ${simState.income_delta_pct > 0 ? '+' : ''}${simState.income_delta_pct}%`);
    if (simState.expense_delta_pct !== 0) activeShocks.push(`Expense ${simState.expense_delta_pct > 0 ? '+' : ''}${simState.expense_delta_pct}%`);
    if (simState.one_off_shock > 0) activeShocks.push(`Shock ₹${simState.one_off_shock}`);
    if (simState.delayed_payout_days > 0) activeShocks.push(`Delay ${simState.delayed_payout_days}d`);
    elImpactBadge.textContent = activeShocks.length > 0 ? activeShocks.join(" • ") : "Baseline Live State";
  }

  // Render Trajectory Table
  renderTrajectoryTable(r.trajectory || []);
}

function renderTrajectoryTable(trajectory) {
  const tbody = document.getElementById("trajectoryTableBody");
  if (!tbody) return;

  if (!trajectory || trajectory.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-4 text-center text-stone-400 text-xs">Awaiting trajectory projection.</td></tr>`;
    return;
  }

  const activeFloor = window.sureSavingsStore?.getProfile()?.protected_floor || 500;
  tbody.innerHTML = trajectory.map(t => {
    const delta = (t.scenario_buffer !== undefined && t.baseline_buffer !== undefined)
      ? (t.scenario_buffer - t.baseline_buffer)
      : (t.buffer_delta || 0);

    const isBreach = t.breached_floor || (t.scenario_buffer !== undefined && t.scenario_buffer < activeFloor);
    const cushion = (t.scenario_buffer || 0) - activeFloor;
    const cushionText = cushion >= 0 ? `₹${Math.round(cushion).toLocaleString()} Above Floor` : `₹${Math.round(Math.abs(cushion)).toLocaleString()} Below Floor`;

    return `
      <tr class="hover:opacity-80 transition-opacity ${isBreach ? 'bg-rose-500/5' : ''}">
        <td class="py-3 px-3 font-bold flex items-center space-x-2 ${isBreach ? 'text-rose-600' : 'text-stone-900'}">
          <span class="w-2 h-2 rounded-full ${isBreach ? 'bg-rose-500' : 'bg-emerald-500'}"></span>
          <span>Week ${t.week}</span>
        </td>
        <td class="py-3 px-3 font-mono text-stone-600">₹${Math.round(t.baseline_buffer || 0).toLocaleString()}</td>
        <td class="py-3 px-3 font-mono font-bold ${isBreach ? 'text-rose-600' : 'text-stone-900'}">₹${Math.round(t.scenario_buffer || 0).toLocaleString()}</td>
        <td class="py-3 px-3 font-mono font-bold ${delta >= 0 ? 'text-emerald-600' : 'text-rose-600'}">
          ${delta >= 0 ? '+' : ''}₹${Math.round(delta).toLocaleString()}
        </td>
        <td class="py-3 px-3 font-bold ${cushion >= 0 ? 'text-emerald-600' : 'text-rose-600'}">
          ${cushionText}
        </td>
        <td class="py-3 px-3 text-right ${isBreach ? 'text-rose-600 font-bold' : 'text-stone-500'}">
          ${isBreach ? 'Emergency Pause Active' : (delta >= 0 ? 'Normal Micro-Sweeps' : 'Deficit Smoothing')}
        </td>
      </tr>
    `;
  }).join("");
}

function applySimulatedSave() {
  if (window.showToast) {
    window.showToast(
      "Scenario Applied to Sandbox",
      `Simulation active across ${simState.simulation_weeks} weeks. Parameters reflected in sandbox memory.`,
      "success"
    );
  } else {
    alert(`Simulation applied to sandbox across ${simState.simulation_weeks} weeks.`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize presets from scenario library
  initScenarioLibrary();

  // 2. Attach parametric slider listeners
  const sInc = document.getElementById("sliderIncomeDelta");
  if (sInc) {
    sInc.addEventListener("input", (e) => {
      simState.income_delta_pct = parseInt(e.target.value) || 0;
      const v = document.getElementById("valIncomeDelta");
      if (v) v.textContent = `${simState.income_delta_pct > 0 ? '+' : ''}${simState.income_delta_pct}%`;
      runSimulation();
    });
  }

  const sExp = document.getElementById("sliderExpenseDelta");
  if (sExp) {
    sExp.addEventListener("input", (e) => {
      simState.expense_delta_pct = parseInt(e.target.value) || 0;
      const v = document.getElementById("valExpenseDelta");
      if (v) v.textContent = `${simState.expense_delta_pct > 0 ? '+' : ''}${simState.expense_delta_pct}%`;
      runSimulation();
    });
  }

  const iShock = document.getElementById("inputOneOffShock");
  if (iShock) {
    iShock.addEventListener("input", (e) => {
      simState.one_off_shock = parseInt(e.target.value) || 0;
      const v = document.getElementById("valShockAmount");
      if (v) v.textContent = `₹${simState.one_off_shock.toLocaleString()}`;
      runSimulation();
    });
  }

  const sDelay = document.getElementById("sliderDelayDays");
  if (sDelay) {
    sDelay.addEventListener("input", (e) => {
      simState.delayed_payout_days = parseInt(e.target.value) || 0;
      const v = document.getElementById("valDelayDays");
      if (v) v.textContent = `${simState.delayed_payout_days} days`;
      runSimulation();
    });
  }

  const sWeeks = document.getElementById("sliderSimWeeks");
  if (sWeeks) {
    sWeeks.addEventListener("input", (e) => {
      simState.simulation_weeks = parseInt(e.target.value) || 4;
      const v = document.getElementById("valSimWeeks");
      if (v) v.textContent = `${simState.simulation_weeks} weeks`;
      runSimulation();
    });
  }

  const btnReset = document.getElementById("btnResetSimulator");
  if (btnReset) {
    btnReset.addEventListener("click", resetToLiveState);
  }

  // Run initial simulation
  runSimulation();
});

// Global exports
window.applyPreset = applyPreset;
window.resetToLiveState = resetToLiveState;
window.applySimulatedSave = applySimulatedSave;
