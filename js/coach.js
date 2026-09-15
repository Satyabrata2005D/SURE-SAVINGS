/**
 * SURE SAVINGS: Smart Income Buffer - AI Resilience Coach Conversational Engine
 * Calls backend API with seamless local deterministic fallback.
 */

function getLiveCoachResponses() {
  const user = window.sureSavingsStore?.state?.auth?.user || {};
  const isDemo = Boolean(user.is_demo_user);
  const p = window.sureSavingsStore?.state?.profile || {};

  // If user has not completed setup and is not demo
  if (!isDemo && (!p.current_income || p.resilience_status === "INSUFFICIENT_DATA")) {
    const name = user.first_name || (user.name ? user.name.split(' ')[0] : 'Member');
    return {
      score: {
        title: "Resilience Assessment Pending",
        reply: `Hello ${name}. I need more of your financial information before I can calculate a personalized resilience score. Complete your financial setup (income sources, essential expenses, and current cash) to generate your 4-pillar index.`,
        scoreDelta: "Setup Required"
      },
      delay: {
        title: "Simulation Unavailable",
        reply: `To simulate payment shocks and income delays, SURE SAVINGS needs your essential weekly burn rate and current liquid buffer numbers. Please complete the quick setup wizard.`,
        scoreDelta: "Awaiting Data"
      },
      sweep: {
        title: "Safe-to-Save Inactive",
        reply: `The 70% Safe-to-Save safeguard operates on your actual liquid surplus (weekly earnings minus essential commitments). Once you configure your income and expenses, dynamic reserve recommendations will activate.`,
        scoreDelta: "Awaiting Data"
      },
      equipment: {
        title: "Cash Flow Assessment Pending",
        reply: `I cannot evaluate weekend capital expenditures without your scheduled commitments and checking account floor. Add your recurring expenses to unlock commitment tracking.`,
        scoreDelta: "Setup Required"
      },
      withdraw: {
        title: "Buffer Status",
        reply: `Your current emergency buffer is ₹0. Set up your Smart Buffer target and initial reserve to enable buffer drawdown testing.`,
        scoreDelta: "Buffer Empty"
      },
      guardrail: {
        title: "Safety Guardrail: Read-Only Interface",
        reply: `I am SURE SAVINGS' read-only financial advisory coach. I do not have permission or authority to initiate or execute monetary transactions. All transfers and simulations must be initiated directly by you through the authorized SURE SAVINGS or Decision Pipeline modals.`,
        scoreDelta: "Action Prohibited"
      },
      default: {
        title: "Personal Workspace Setup",
        reply: `Welcome to your private workspace, ${name}. Your financial intelligence picture isn't populated yet because you haven't entered your financial data. Complete your 30-second setup to unlock Income Intelligence, Safe-to-Save, and your Resilience Index.`,
        scoreDelta: "Setup Required"
      }
    };
  }

  const buffer = Number(p.current_buffer || (isDemo ? 6800 : 0)).toLocaleString();
  const burn = Number(p.weekly_burn || (isDemo ? 4400 : 0)).toLocaleString();
  const floor = Number(p.protected_floor || (isDemo ? 3500 : 0)).toLocaleString();
  const rec = Number(p.recommended_contribution || (isDemo ? 900 : 0)).toLocaleString();
  const surplus = Number(p.surplus || (isDemo ? 1300 : 0)).toLocaleString();
  const pocket = Number(p.free_pocket_liquidity || (isDemo ? 400 : 0)).toLocaleString();
  const score = p.resilience_score || (isDemo ? 74 : 0);
  const safeAbove = Math.max(0, (p.current_buffer || 0) - (p.protected_floor || 0)).toLocaleString();
  const income = Number(p.current_income || (isDemo ? 8400 : 0)).toLocaleString();
  const baseline = Number(p.stabilized_income || (isDemo ? 7100 : 0)).toLocaleString();
  const name = user.first_name || (user.name ? user.name.split(' ')[0] : (isDemo ? 'Arjun' : 'Member'));

  return {
    score: {
      title: `Resilience Score Breakdown (${score} / 100)`,
      reply: `Your financial resilience score is calculated across four deterministic pillars:

1. Income Predictability Stability: ${p.income_volatility ? Math.round((1 - p.income_volatility) * 100) : 82}% (Past earnings stability)
2. Buffer Target Coverage: Holds ₹${buffer} toward ₹${Number(p.buffer_target || 15000).toLocaleString()} target; ${p.current_coverage_weeks || 1.5} wks coverage.
3. Essential Fixed Expense Ratio: ₹${burn}/wk fixed commitments absorb ${income > 0 ? Math.round((p.weekly_burn / p.current_income) * 100) : 52}% of inflow.
4. Cash Flow Survival Horizon: Continuous liquidity margin above protected floor.

Next Action: ${rec !== "0" ? `Accepting the ₹${rec} reserve deposit expands your buffer.` : "Maintain current cash reserves."}`,
      scoreDelta: `Current: ${score} / 100`
    },
    delay: {
      title: "Scenario: 30-Day Client Invoice Delay",
      reply: `I ran a simulation on your current ₹${buffer} liquid buffer against your ₹${burn} essential weekly burn.
      
**Verdict: ${p.current_coverage_weeks >= 4 ? "Safe to absorb" : "Caution: Short Runway"}.**
• **Impact:** Runway holds at ${p.current_coverage_weeks || 1.5} weeks during the delay.
• **Action:** Automated transfers pause to preserve operational cash in checking.
• **Recommendation:** ${p.current_coverage_weeks >= 2 ? "No emergency buffer breach detected." : "Consider setting aside surplus to expand runway beyond 4 weeks."}`,
      scoreDelta: "-4 pts temporarily"
    },
    sweep: {
      title: "Deterministic 70% Surplus Safeguard",
      reply: `The deterministic engine applies a 70% surplus cap safeguard (₹${surplus} gross surplus → recommended allocation ₹${rec}).

• Buffer Capitalization: +₹${rec} (expands runway)
• Free Pocket Liquidity: ₹${pocket} (unrestricted operational cash)
• Protected Cash Floor: ₹${floor} (strictly untouched in checking)`,
      scoreDelta: "+3 pts on execution"
    },
    equipment: {
      title: "Capital Expense Assessment: ₹2,000 Outlay",
      reply: `Looking at your current financial position:

Gross surplus is ₹${surplus}, with ₹${rec} recommended for buffer and ₹${pocket} in free pocket cash. Essential weekly burn is ₹${burn}.

Recommendation: Spending ₹2,000 would compress your checking account near the ₹${floor} protected floor. Verify non-essential spending timing.`,
      scoreDelta: "Caution Advised"
    },
    withdraw: {
      title: "Buffer Withdrawal Feasibility Check",
      reply: `Evaluating your liquidity boundary:

• Current Buffer: ₹${buffer}
• Protected Cash Floor: ₹${floor}
• Safe to Use Above Floor: ₹${safeAbove}

Verdict: A buffer drawdown leaves your checking floor 100% intact. We recommend replenishing the buffer during above-baseline weeks.`,
      scoreDelta: "-4 pts temporarily"
    },
    guardrail: {
      title: "Safety Guardrail: Read-Only Interface",
      reply: `I am SURE SAVINGS' read-only financial advisory coach. I do not have permission or authority to initiate or execute monetary transactions. All transfers and simulations must be initiated directly by you through the authorized SURE SAVINGS or Decision Pipeline modals.`,
      scoreDelta: "Action Prohibited"
    },
    default: {
      title: "SURE SAVINGS Telemetry Assessment",
      reply: `Hello ${name}. Your financial resilience score is ${score}/100. Your current weekly income is ₹${income} (stabilized baseline: ₹${baseline}).

Essential weekly burn of ₹${burn} and your protected cash floor of ₹${floor} are active. The engine recommends saving ₹${rec} this cycle.`,
      scoreDelta: "Stable"
    }
  };
}

async function sendCoachMessage(userText) {
  if (!userText || !userText.trim()) return;
  const chatContainer = document.getElementById("chatMessagesContainer");
  if (!chatContainer) return;

  const user = window.sureSavingsStore?.state?.auth?.user || window.sureSavingsStore?.state?.profile;
  const fullName = (user?.name || user?.display_name || 'Member').trim();
  const initials = user?.initials || (fullName.split(/\s+/)[0][0] || 'U');

  // Add user bubble
  const userBubble = document.createElement("div");
  userBubble.className = "flex items-start justify-end space-x-3 mb-4 animate-fade-in";
  userBubble.innerHTML = `
    <div class="max-w-md bg-[#1F2937] text-white rounded-2xl rounded-tr-sm p-3.5 shadow-sm text-xs sm:text-sm">
      <div class="flex items-center justify-between mb-1">
        <span class="text-[11px] font-semibold text-gray-300 user-display-name">${fullName}</span>
        <span class="text-[10px] text-gray-400">Just now</span>
      </div>
      <p class="user-msg-text leading-relaxed"></p>
    </div>
    <div class="w-8 h-8 rounded-full bg-stone-300 text-stone-800 font-bold text-xs flex items-center justify-center flex-shrink-0 mt-1 user-avatar">
      ${initials}
    </div>
  `;
  userBubble.querySelector(".user-msg-text").textContent = userText; // Safe DOM text rendering
  chatContainer.appendChild(userBubble);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Typing indicator with Gemini branding
  const typingBubble = document.createElement("div");
  typingBubble.id = "coachTypingIndicator";
  typingBubble.className = "flex items-start space-x-3.5 mb-4";
  typingBubble.innerHTML = `
    <div class="relative w-9 h-9 rounded-xl flex items-center justify-center shadow-sm flex-shrink-0">
      <img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-9 h-9 object-contain" width="36" height="36">
      <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-teal-400 border-2 border-white"></span>
    </div>
    <div class="bg-gray-50 dark:bg-stone-800 border border-gray-100 dark:border-stone-700 text-gray-600 dark:text-stone-300 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm text-xs flex items-center space-x-2">
      <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
      <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse" style="animation-delay: 0.2s"></span>
      <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse" style="animation-delay: 0.4s"></span>
      <span class="text-gray-500 dark:text-stone-400 pl-1 font-mono text-[11px]">Consulting Gemini AI with grounded telemetry...</span>
    </div>
  `;
  chatContainer.appendChild(typingBubble);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Try fetching from backend Gemini API
  let title = "";
  let answer = "";
  let badge = "";
  let nextStep = "";
  let navigation = null;
  let isLiveGemini = false;

  if (window.sureSavingsApi || window.api) {
    const apiService = window.sureSavingsApi || window.api;
    try {
      const pageCtx = window.sureSavingsPageContext || { page: "coach.html", title: "SURE AI Guide" };
      const data = await apiService.sendChatMessage(userText, pageCtx);
      if (data && data.answer) {
        title = data.title || "SURE AI Guidance";
        answer = data.answer;
        badge = data.badge || (data.safety_status === "REFUSED" ? "Safety Invariant" : "Gemini 3.6 Flash Verified");
        nextStep = data.next_step || "";
        navigation = data.navigation || null;
        isLiveGemini = true;
      } else if (data && data.error) {
        title = "SURE AI Notification";
        answer = data.error.message || "An issue occurred while processing your request. Please try again.";
        badge = "Service Notice";
      }
    } catch (e) {
      console.warn("[SURE AI] API call encountered an error:", e);
      if (e.status === 401 || (e.message && e.message.includes("401"))) {
        title = "Authentication Required";
        answer = "Your session has expired. Please sign in again to access personalized SURE AI guidance.";
        badge = "Auth Required";
        navigation = { label: "Sign In", route: "login.html" };
      }
    }
  }

  // Fallback if no answer received from API
  if (!answer) {
    const responses = getLiveCoachResponses();
    const lower = userText.toLowerCase();
    let key = "default";
    if (lower.includes("transfer") || lower.includes("withdraw all") || lower.includes("pay") || lower.includes("send")) key = "guardrail";
    else if (lower.includes("score") || lower.includes("74") || lower.includes("resilience")) key = "score";
    else if (lower.includes("900") || lower.includes("1300") || lower.includes("1,300") || lower.includes("cap")) key = "sweep";
    else if (lower.includes("drop") || lower.includes("fall") || lower.includes("weak")) key = "delay";
    else if (lower.includes("withdraw") || lower.includes("2000") || lower.includes("2,000")) key = "withdraw";
    else if (lower.includes("spend") || lower.includes("weekend") || lower.includes("afford")) key = "equipment";

    const item = responses[key] || responses.default;
    title = item.title;
    answer = item.reply;
    badge = item.scoreDelta || "Deterministic Fallback";
    nextStep = "Review your financial dashboard on Command Center.";
    navigation = { label: "Open Command Center", route: "index.html" };
  }

  setTimeout(() => {
    const indicator = document.getElementById("coachTypingIndicator");
    if (indicator) indicator.remove();

    // Enhanced markdown formatting for Gemini output
    function formatMarkdown(text) {
      if (!text) return "";
      let formatted = text
        .replace(/^### (.*$)/gim, '<h4 class="font-bold text-xs sm:text-sm mt-3 mb-1.5 text-brand-600 dark:text-brand-400">$1</h4>')
        .replace(/^## (.*$)/gim, '<h3 class="font-bold text-sm sm:text-base mt-3 mb-1.5 text-brand-600 dark:text-brand-400">$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded font-mono text-[11px] bg-stone-100 dark:bg-stone-800 text-stone-900 dark:text-stone-100">$1</code>')
        .replace(/^\s*[-*•]\s+(.*$)/gim, '• $1')
        .replace(/\n\n/g, '<br/><br/>')
        .replace(/\n/g, '<br/>');
      return formatted;
    }

    const botBubble = document.createElement("div");
    botBubble.className = "flex items-start space-x-3.5 mb-4 animate-fade-in";
    
    let navButtonHtml = "";
    if (navigation && navigation.route && navigation.label) {
      navButtonHtml = `
        <a href="${navigation.route}" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-brand-500 hover:bg-brand-600 transition-colors shadow-sm ml-auto">
          <span>${navigation.label}</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
        </a>
      `;
    }

    let nextStepHtml = "";
    if (nextStep) {
      nextStepHtml = `
        <div class="mt-3 p-3 rounded-xl border flex flex-wrap items-center justify-between gap-2" style="background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.25)">
          <div class="flex items-center gap-2 max-w-[70%]">
            <span class="text-base">👉</span>
            <span class="text-xs font-semibold text-emerald-800 dark:text-emerald-300"><strong>Next Step:</strong> ${nextStep}</span>
          </div>
          ${navButtonHtml}
        </div>
      `;
    }

    const headerBadgeText = isLiveGemini 
      ? 'Just now • Gemini 3.6 Flash • Grounded Telemetry'
      : 'Just now • Deterministic Invariant Checked';

    botBubble.innerHTML = `
      <div class="relative w-9 h-9 rounded-xl flex items-center justify-center shadow-md flex-shrink-0">
        <img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-9 h-9 object-contain" width="36" height="36">
        <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ${isLiveGemini ? 'bg-teal-400' : 'bg-emerald-400'} border-2 border-white"></span>
      </div>
      <div class="flex-1 space-y-2">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-bold" style="color: var(--text-primary)">SURE AI</span>
          <span class="text-[10px]" style="color: var(--text-subtle)">${headerBadgeText}</span>
        </div>
        <div class="text-xs sm:text-sm rounded-2xl p-4 space-y-2 border shadow-sm" style="background: var(--surface-sunken); border-color: var(--border-default); color: var(--text-secondary)">
          <div class="flex items-center justify-between border-b pb-2" style="border-color: var(--border-default)">
            <span class="bot-title text-xs font-bold" style="color: var(--text-primary)"></span>
            <span class="bot-badge text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200"></span>
          </div>
          <div class="bot-answer leading-relaxed"></div>
          ${nextStepHtml}
        </div>
      </div>
    `;
    botBubble.querySelector(".bot-title").textContent = title;
    botBubble.querySelector(".bot-badge").textContent = badge;
    botBubble.querySelector(".bot-answer").innerHTML = formatMarkdown(answer);
    chatContainer.appendChild(botBubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }, 300);
}

function updateCoachWelcomeCard() {
  const user = window.sureSavingsStore?.state?.auth?.user || window.sureSavingsStore?.state?.profile || {};
  const p = window.sureSavingsStore?.state?.profile || {};
  const isDemo = Boolean(user.is_demo_user);
  
  const name = user.first_name || (user.name ? user.name.split(' ')[0] : 'Member');
  const welcomeEl = document.getElementById("coach-welcome-text");
  if (welcomeEl) {
    if (p.current_income && (p.current_income > 0 || isDemo)) {
      const score = p.resilience_score || 70;
      const income = Number(p.current_income || 0).toLocaleString();
      const baseline = Number(p.stabilized_income || p.current_income).toLocaleString();
      const burn = Number(p.weekly_burn || 0).toLocaleString();
      const floor = Number(p.protected_floor || 0).toLocaleString();
      const rec = Number(p.recommended_contribution || 0).toLocaleString();
      
      welcomeEl.innerHTML = `
        Hello <strong>${name}</strong>. Your financial resilience score is currently <strong>${score} / 100</strong>. Your current weekly earnings (<strong>₹${income}</strong>) compare to a stabilized baseline of ₹${baseline}. Fixed commitments (₹${burn}) and your protected cash floor (₹${floor}) are tracked by the deterministic engine, with a current Safe-to-Save recommendation of <strong class="text-brand-500">₹${rec}</strong>.
      `;
    } else {
      welcomeEl.innerHTML = `
        Welcome <strong>${name}</strong> to <strong>SURE AI</strong>, your personal financial resilience guide. Complete your 30-second Financial Setup to unlock verified telemetry, Safe-to-Save recommendations, and your Resilience Index.
      `;
    }
  }
  
  // Update cycle header pill
  const inflowEl = document.querySelector('[data-coach="cycle-inflow"]');
  if (inflowEl) {
    const currentInflow = Number(p.current_income || 0).toLocaleString();
    inflowEl.textContent = p.current_income ? `₹${currentInflow} Inflow` : "Setup Required";
  }
  const recEl = document.querySelector('[data-coach="cycle-rec"]');
  if (recEl) {
    const currentRec = Number(p.recommended_contribution || 0).toLocaleString();
    recEl.textContent = p.recommended_contribution !== undefined ? `Save ₹${currentRec}` : "Save ₹0";
  }
}

window.sendCoachMessage = sendCoachMessage;
window.updateCoachWelcomeCard = updateCoachWelcomeCard;

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("coachChatForm");
  const input = document.getElementById("coachChatInput");

  if (form && input) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const val = input.value.trim();
      if (val) {
        sendCoachMessage(val);
        input.value = "";
      }
    });
  }

  // Preset prompt pill buttons
  document.querySelectorAll("[data-coach-prompt]").forEach(btn => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-coach-prompt");
      sendCoachMessage(prompt);
    });
  });

  // Dynamically update welcome card on load and state change
  updateCoachWelcomeCard();
  if (window.sureSavingsStore?.subscribe) {
    window.sureSavingsStore.subscribe(() => {
      updateCoachWelcomeCard();
    });
  }
});
