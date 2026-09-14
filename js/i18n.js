/**
 * SURE SAVINGS: Production Multilingual Architecture (i18n)
 * Supports English + 22 Eighth Schedule Indian Languages (23 Total).
 * Instant live DOM switching, RTL for Urdu, Intl formatting, and preference persistence.
 */

(function () {
  "use strict";

  const DEFAULT_LOCALE = "en-IN";

  const SUPPORTED_LOCALES = {
    "en-IN": { id: "en-IN", name: "English", native: "English", dir: "ltr", script: "Latin" },
    "hi-IN": { id: "hi-IN", name: "Hindi", native: "हिन्दी", dir: "ltr", script: "Devanagari" },
    "bn-IN": { id: "bn-IN", name: "Bengali", native: "বাংলা", dir: "ltr", script: "Bengali" },
    "as-IN": { id: "as-IN", name: "Assamese", native: "অসমীয়া", dir: "ltr", script: "Bengali" },
    "brx-IN": { id: "brx-IN", name: "Bodo", native: "बड़ो", dir: "ltr", script: "Devanagari" },
    "doi-IN": { id: "doi-IN", name: "Dogri", native: "डोगरी", dir: "ltr", script: "Devanagari" },
    "gu-IN": { id: "gu-IN", name: "Gujarati", native: "ગુજરાતી", dir: "ltr", script: "Gujarati" },
    "kn-IN": { id: "kn-IN", name: "Kannada", native: "ಕನ್ನಡ", dir: "ltr", script: "Kannada" },
    "ks-IN": { id: "ks-IN", name: "Kashmiri", native: "کٲشُر", dir: "rtl", script: "Arabic" },
    "kok-IN": { id: "kok-IN", name: "Konkani", native: "कोंकणी", dir: "ltr", script: "Devanagari" },
    "ml-IN": { id: "ml-IN", name: "Malayalam", native: "മലയാളം", dir: "ltr", script: "Malayalam" },
    "mni-IN": { id: "mni-IN", name: "Manipuri", native: "মৈতৈলোন্", dir: "ltr", script: "Bengali" },
    "mr-IN": { id: "mr-IN", name: "Marathi", native: "मराठी", dir: "ltr", script: "Devanagari" },
    "mai-IN": { id: "mai-IN", name: "Maithili", native: "मैथिली", dir: "ltr", script: "Devanagari" },
    "ne-IN": { id: "ne-IN", name: "Nepali", native: "नेपाली", dir: "ltr", script: "Devanagari" },
    "or-IN": { id: "or-IN", name: "Odia", native: "ଓଡ଼ିଆ", dir: "ltr", script: "Odia" },
    "pa-IN": { id: "pa-IN", name: "Punjabi", native: "ਪੰਜਾਬੀ", dir: "ltr", script: "Gurmukhi" },
    "sa-IN": { id: "sa-IN", name: "Sanskrit", native: "संस्कृतम्", dir: "ltr", script: "Devanagari" },
    "sat-IN": { id: "sat-IN", name: "Santali", native: "ᱥᱟᱱᱛᱟᱲᱤ", dir: "ltr", script: "Ol Chiki" },
    "sd-IN": { id: "sd-IN", name: "Sindhi", native: "سنڌي", dir: "rtl", script: "Arabic" },
    "ta-IN": { id: "ta-IN", name: "Tamil", native: "தமிழ்", dir: "ltr", script: "Tamil" },
    "te-IN": { id: "te-IN", name: "Telugu", native: "తెలుగు", dir: "ltr", script: "Telugu" },
    "ur-IN": { id: "ur-IN", name: "Urdu", native: "اردو", dir: "rtl", script: "Arabic" },
  };

  class I18nManager {
    constructor() {
      this.supportedLocales = SUPPORTED_LOCALES;
      this.defaultLocale = DEFAULT_LOCALE;
      this.catalogs = {};
      this.isInitialized = false;
      this.currentLocale = this._resolveInitialLocale();
      const meta = SUPPORTED_LOCALES[this.currentLocale] || SUPPORTED_LOCALES[DEFAULT_LOCALE];
      window.sureSavingsLocale = {
        locale: this.currentLocale,
        languageName: meta.name,
        nativeName: meta.native,
        direction: meta.dir,
        script: meta.script,
      };
    }

    _resolveInitialLocale() {
      // 1. Check localStorage saved preference
      try {
        const saved = localStorage.getItem("sureSavingsLocale");
        if (saved && SUPPORTED_LOCALES[saved]) {
          return saved;
        }
      } catch (e) {}

      // 2. Check browser language
      try {
        if (typeof navigator !== "undefined" && navigator.language) {
          const navLang = navigator.language;
          if (SUPPORTED_LOCALES[navLang]) return navLang;
          const prefix = navLang.split("-")[0].toLowerCase();
          for (const loc in SUPPORTED_LOCALES) {
            if (loc.split("-")[0].toLowerCase() === prefix) {
              return loc;
            }
          }
        }
      } catch (e) {}

      return DEFAULT_LOCALE;
    }

    async init() {
      if (this.isInitialized) return;

      // Load English baseline first
      await this.loadCatalog(DEFAULT_LOCALE);

      // Load active locale if different
      if (this.currentLocale !== DEFAULT_LOCALE) {
        await this.loadCatalog(this.currentLocale);
      }

      this.isInitialized = true;
      this.applyLocale(this.currentLocale);

      // Mount language selector into UI
      this.mountLanguageSelector();

      // Check if user is logged in to synchronize backend preferences
      this._syncWithBackend();
    }

    async loadCatalog(locale) {
      if (this.catalogs[locale]) return this.catalogs[locale];

      // Check localStorage cache
      try {
        const cached = localStorage.getItem(`sureSavingsCatalog_${locale}`);
        if (cached) {
          const parsed = JSON.parse(cached);
          this.catalogs[locale] = parsed;
          return parsed;
        }
      } catch (e) {}

      // Fetch from server
      try {
        const resp = await fetch(`/locales/${locale}.json`);
        if (resp.ok) {
          const data = await resp.json();
          this.catalogs[locale] = data;
          try {
            localStorage.setItem(`sureSavingsCatalog_${locale}`, JSON.stringify(data));
          } catch (e) {}
          return data;
        }
      } catch (e) {
        console.warn(`[i18n] Failed to fetch catalog for ${locale}, falling back:`, e);
      }

      // If failed and not default, return base catalog
      return this.catalogs[DEFAULT_LOCALE] || {};
    }

    t(key, params = {}) {
      if (!key) return "";

      const parts = key.split(".");
      let val = this._lookupInCatalog(this.currentLocale, parts, key);

      // Fallback to English if missing in current locale
      if (val === undefined && this.currentLocale !== DEFAULT_LOCALE) {
        val = this._lookupInCatalog(DEFAULT_LOCALE, parts, key);
      }

      if (val === undefined) {
        return key; // Return key if completely missing
      }

      // Handle interpolations, e.g. {count}, {name}
      if (typeof val === "string" && params && Object.keys(params).length > 0) {
        let str = val;
        for (const [pKey, pVal] of Object.entries(params)) {
          str = str.replace(new RegExp(`\\{${pKey}\\}`, "g"), pVal);
        }
        return str;
      }

      return val;
    }

    _lookupInCatalog(locale, parts, rawKey) {
      const cat = this.catalogs[locale];
      if (!cat) return undefined;

      // 1. Direct flat key match
      if (rawKey && rawKey in cat) {
        return cat[rawKey];
      }

      // 2. Nested property lookup
      let curr = cat;
      for (const p of parts) {
        if (curr && typeof curr === "object" && p in curr) {
          curr = curr[p];
        } else {
          return undefined;
        }
      }
      return curr;
    }

    async setLocale(newLocale) {
      if (!SUPPORTED_LOCALES[newLocale]) {
        console.warn(`[i18n] Unsupported locale: ${newLocale}`);
        return;
      }

      this.currentLocale = newLocale;
      try {
        localStorage.setItem("sureSavingsLocale", newLocale);
      } catch (e) {}

      await this.loadCatalog(newLocale);
      this.applyLocale(newLocale);

      // Sync with user profile on server if authenticated
      this._updateBackendPreference(newLocale);

      // Notify other components (calendar, charts, coach)
      const detail = {
        locale: newLocale,
        metadata: SUPPORTED_LOCALES[newLocale],
        direction: SUPPORTED_LOCALES[newLocale].dir,
      };
      window.dispatchEvent(new CustomEvent("i18n:localeChanged", { detail }));
      window.dispatchEvent(new CustomEvent("sure-savings-locale-changed", { detail }));
    }

    applyLocale(locale) {
      const meta = SUPPORTED_LOCALES[locale] || SUPPORTED_LOCALES[DEFAULT_LOCALE];
      const isRtl = meta.dir === "rtl";

      window.sureSavingsLocale = {
        locale: locale,
        languageName: meta.name,
        nativeName: meta.native,
        direction: meta.dir,
        script: meta.script,
      };

      // 1. Update HTML document direction and lang
      document.documentElement.lang = locale;
      document.documentElement.dir = isRtl ? "rtl" : "ltr";

      if (isRtl) {
        document.documentElement.classList.add("is-rtl");
        document.body.classList.add("is-rtl");
      } else {
        document.documentElement.classList.remove("is-rtl");
        document.body.classList.remove("is-rtl");
      }

      // 2. Translate DOM elements
      this.translateDOM();

      // 3. Update Language Selector button display
      this.updateSelectorButton();
    }

    translateDOM(root = document) {
      // 1. Text elements: data-i18n
      const textElems = root.querySelectorAll("[data-i18n]");
      textElems.forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (!key) return;

        const translation = this.t(key);
        // If element has nested icon SVG, update text node safely
        const textNode = Array.from(el.childNodes).find(
          (node) => node.nodeType === Node.TEXT_NODE && node.nodeValue.trim().length > 0
        );

        if (textNode) {
          textNode.nodeValue = translation;
        } else if (el.children.length === 0) {
          el.textContent = translation;
        } else {
          // If contains span with text
          const span = el.querySelector("span:not([class*='icon']):not([class*='badge'])");
          if (span) {
            span.textContent = translation;
          } else {
            el.textContent = translation;
          }
        }
      });

      // 2. Placeholders: data-i18n-placeholder
      const placeholderElems = root.querySelectorAll("[data-i18n-placeholder]");
      placeholderElems.forEach((el) => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (key) el.setAttribute("placeholder", this.t(key));
      });

      // 3. Titles: data-i18n-title
      const titleElems = root.querySelectorAll("[data-i18n-title]");
      titleElems.forEach((el) => {
        const key = el.getAttribute("data-i18n-title");
        if (key) el.setAttribute("title", this.t(key));
      });

      // 4. ARIA labels: data-i18n-aria
      const ariaElems = root.querySelectorAll("[data-i18n-aria]");
      ariaElems.forEach((el) => {
        const key = el.getAttribute("data-i18n-aria");
        if (key) el.setAttribute("aria-label", this.t(key));
      });
    }

    // ── Number & Date Formatting Helpers ──
    formatCurrency(amount, maxFractionDigits = 0) {
      try {
        return new Intl.NumberFormat(this.currentLocale, {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: maxFractionDigits,
        }).format(amount);
      } catch (e) {
        return `₹${Number(amount || 0).toLocaleString()}`;
      }
    }

    formatDate(date, options = { month: "short", day: "numeric", year: "numeric" }) {
      try {
        const d = date instanceof Date ? date : new Date(date);
        return new Intl.DateTimeFormat(this.currentLocale, options).format(d);
      } catch (e) {
        return String(date);
      }
    }

    formatNumber(num, options = {}) {
      try {
        return new Intl.NumberFormat(this.currentLocale, options).format(num);
      } catch (e) {
        return String(num);
      }
    }

    // ── Global Language Selector UI ──
    mountLanguageSelector() {
      if (document.getElementById("sure-language-selector-root")) {
        return; // Already mounted
      }

      // Create container
      const container = document.createElement("div");
      container.id = "sure-language-selector-root";
      container.className = "relative inline-block text-left language-selector-wrapper";
      container.innerHTML = `
        <button id="sure-lang-btn" type="button" aria-haspopup="listbox" aria-expanded="false" 
          class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-semibold transition-all hover:border-brand-500/40 focus:outline-none focus:ring-1 focus:ring-brand-500"
          style="background: var(--surface-sunken, #F1F0ED); border-color: var(--border-default, #E2E8F0); color: var(--text-primary, #0F172A);"
          title="Select Language">
          <span class="text-sm select-none">🌐</span>
          <span id="sure-lang-active-label" class="font-medium">English</span>
          <svg id="sure-lang-chevron" class="w-3 h-3 text-stone-400 ml-0.5 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <div id="sure-lang-dropdown" class="hidden absolute right-0 mt-1.5 w-64 rounded-xl shadow-2xl border z-50 overflow-hidden transition-all duration-200"
          style="background: var(--surface-paper, #FFFFFF); border-color: var(--border-default, #E2E8F0);"
          role="listbox" aria-label="Languages">
          
          <!-- Search box -->
          <div class="p-2 border-b" style="border-color: var(--border-default, #E2E8F0);">
            <div class="relative flex items-center">
              <span class="absolute left-2.5 text-stone-400 text-xs">🔍</span>
              <input id="sure-lang-search" type="text" placeholder="Search language..." 
                class="w-full pl-7 pr-2.5 py-1.5 text-xs rounded-lg border focus:outline-none focus:border-brand-500"
                style="background: var(--surface-sunken, #F8F7F4); border-color: var(--border-subtle, #E2E8F0); color: var(--text-primary, #0F172A);"
                autocomplete="off" />
            </div>
          </div>

          <!-- List of 23 languages -->
          <div id="sure-lang-list" class="max-h-72 overflow-y-auto py-1 divide-y divide-stone-100/50">
            ${Object.values(SUPPORTED_LOCALES)
              .map(
                (loc) => `
              <button type="button" role="option" data-locale-id="${loc.id}" 
                class="sure-lang-item w-full px-3 py-2 text-left flex items-center justify-between text-xs hover:bg-stone-50 focus:bg-stone-100 dark:focus:bg-stone-800 transition-colors focus:outline-none"
                style="color: var(--text-primary, #0F172A);">
                <div class="flex flex-col">
                  <span class="font-bold text-sm leading-tight">${loc.native}</span>
                  <span class="text-[10px] text-stone-400 leading-tight">${loc.name}</span>
                </div>
                <span class="sure-lang-check text-brand-600 font-bold ${
                  loc.id === this.currentLocale ? "" : "hidden"
                }">✓</span>
              </button>
            `
              )
              .join("")}
            <div id="sure-lang-empty" class="hidden py-4 text-center text-xs text-stone-400">No languages found</div>
          </div>
        </div>
      `;

      // Mount into the header controls next to dark-mode-toggle
      const darkModeToggle = document.querySelector(".dark-mode-toggle");
      if (darkModeToggle && darkModeToggle.parentElement) {
        darkModeToggle.parentElement.insertBefore(container, darkModeToggle);
      } else {
        const header = document.querySelector("header");
        if (header) {
          header.appendChild(container);
        } else {
          container.style.position = "fixed";
          container.style.top = "12px";
          container.style.right = "12px";
          container.style.zIndex = "9999";
          document.body.appendChild(container);
        }
      }

      this._bindSelectorEvents(container);
      this.updateSelectorButton();
    }

    _bindSelectorEvents(container) {
      const btn = container.querySelector("#sure-lang-btn");
      const dropdown = container.querySelector("#sure-lang-dropdown");
      const searchInput = container.querySelector("#sure-lang-search");
      const list = container.querySelector("#sure-lang-list");
      const chevron = container.querySelector("#sure-lang-chevron");

      const toggleDropdown = (open) => {
        const shouldOpen = open !== undefined ? open : dropdown.classList.contains("hidden");
        if (shouldOpen) {
          dropdown.classList.remove("hidden");
          btn.setAttribute("aria-expanded", "true");
          if (chevron) chevron.style.transform = "rotate(180deg)";
          searchInput.value = "";
          this._filterLanguageList("");
          setTimeout(() => searchInput.focus(), 50);
        } else {
          dropdown.classList.add("hidden");
          btn.setAttribute("aria-expanded", "false");
          if (chevron) chevron.style.transform = "rotate(0deg)";
        }
      };

      // Toggle dropdown on button click
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleDropdown();
      });

      // Search filtering
      searchInput.addEventListener("input", (e) => {
        this._filterLanguageList(e.target.value);
      });

      // Keyboard navigation helper
      const getVisibleItems = () => {
        return Array.from(list.querySelectorAll(".sure-lang-item")).filter(
          (el) => el.style.display !== "none"
        );
      };

      let activeIndex = -1;
      const highlightItem = (index) => {
        const visible = getVisibleItems();
        if (visible.length === 0) return;
        activeIndex = Math.max(0, Math.min(index, visible.length - 1));
        visible.forEach((el, i) => {
          if (i === activeIndex) {
            el.focus();
            el.scrollIntoView({ block: "nearest" });
          }
        });
      };

      searchInput.addEventListener("keydown", (e) => {
        const visible = getVisibleItems();
        if (e.key === "ArrowDown") {
          e.preventDefault();
          if (visible.length > 0) {
            highlightItem(0);
          }
        } else if (e.key === "Enter") {
          e.preventDefault();
          if (visible.length > 0) {
            visible[0].click();
          }
        } else if (e.key === "Escape") {
          toggleDropdown(false);
          btn.focus();
        }
      });

      list.addEventListener("keydown", (e) => {
        const visible = getVisibleItems();
        const currIndex = visible.indexOf(document.activeElement);
        if (e.key === "ArrowDown") {
          e.preventDefault();
          if (currIndex < visible.length - 1) {
            highlightItem(currIndex + 1);
          }
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          if (currIndex <= 0) {
            searchInput.focus();
          } else {
            highlightItem(currIndex - 1);
          }
        } else if (e.key === "Enter") {
          e.preventDefault();
          if (document.activeElement && document.activeElement.classList.contains("sure-lang-item")) {
            document.activeElement.click();
          }
        } else if (e.key === "Escape") {
          toggleDropdown(false);
          btn.focus();
        }
      });

      // Item selection
      list.addEventListener("click", (e) => {
        const item = e.target.closest(".sure-lang-item");
        if (!item) return;

        const locId = item.getAttribute("data-locale-id");
        if (locId) {
          this.setLocale(locId);
          toggleDropdown(false);
          btn.focus();
        }
      });

      // Close on outside click
      document.addEventListener("click", (e) => {
        if (!container.contains(e.target)) {
          toggleDropdown(false);
        }
      });

      // Close on Escape anywhere
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !dropdown.classList.contains("hidden")) {
          toggleDropdown(false);
          btn.focus();
        }
      });
    }

    _filterLanguageList(query) {
      const q = (query || "").trim().toLowerCase();
      const items = document.querySelectorAll(".sure-lang-item");
      const emptyState = document.getElementById("sure-lang-empty");
      let visibleCount = 0;

      items.forEach((item) => {
        const locId = item.getAttribute("data-locale-id");
        const loc = SUPPORTED_LOCALES[locId];
        if (!loc) return;

        if (!q) {
          item.style.display = "flex";
          visibleCount++;
          return;
        }

        const matches =
          loc.name.toLowerCase().includes(q) ||
          loc.native.toLowerCase().includes(q) ||
          loc.id.toLowerCase().includes(q) ||
          (loc.script && loc.script.toLowerCase().includes(q));

        if (matches) {
          item.style.display = "flex";
          visibleCount++;
        } else {
          item.style.display = "none";
        }
      });

      if (emptyState) {
        if (visibleCount === 0) {
          emptyState.classList.remove("hidden");
        } else {
          emptyState.classList.add("hidden");
        }
      }
    }

    updateSelectorButton() {
      const label = document.getElementById("sure-lang-active-label");
      if (label) {
        const meta = SUPPORTED_LOCALES[this.currentLocale] || SUPPORTED_LOCALES[DEFAULT_LOCALE];
        label.textContent = meta.native;
      }

      // Update checkmarks
      const items = document.querySelectorAll(".sure-lang-item");
      items.forEach((item) => {
        const locId = item.getAttribute("data-locale-id");
        const check = item.querySelector(".sure-lang-check");
        if (check) {
          if (locId === this.currentLocale) {
            check.classList.remove("hidden");
          } else {
            check.classList.add("hidden");
          }
        }
      });
    }

    // ── User Profile Sync ──
    async _syncWithBackend() {
      try {
        const resp = await fetch("/api/v1/users/preferences", { credentials: "include" });
        if (resp.ok) {
          const data = await resp.json();
          if (data && data.preferred_locale && data.preferred_locale !== this.currentLocale) {
            // User profile takes priority over local cache
            this.setLocale(data.preferred_locale);
          }
        }
      } catch (e) {}
    }

    async _updateBackendPreference(locale) {
      try {
        await fetch("/api/v1/users/preferences", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ preferred_locale: locale }),
        });
      } catch (e) {}
    }
  }

  // Create singleton instance
  const i18n = new I18nManager();
  window.i18n = i18n;
  window.t = (key, params) => i18n.t(key, params);

  // Initialize once DOM is loaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => i18n.init());
  } else {
    i18n.init();
  }
})();
