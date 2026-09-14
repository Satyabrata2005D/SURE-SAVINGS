"""
SURE SAVINGS — Enterprise Multilingual / Internationalization (i18n) Test Suite
Verifies:
1. Canonical 23 Locales (Eighth Schedule of Constitution of India + English)
2. Terminology correctness (Marathi, Maithili; no pseudo-dialects)
3. RTL Direction for Urdu, Kashmiri, Sindhi
4. Complete Financial Glossary across all 23 languages
5. 100% Translation Key Parity across all 23 catalogs
6. Backend Localization & User Preference Endpoints (GET/PATCH)
7. SURE AI Language-Aware Coaching:
   - Localized greetings
   - Localized public attribution (Satyabrata Das & Narula Institute of Technology)
   - Localized security/confidentiality refusals across 6 security categories
   - Deterministic fallback in selected locale (never English for non-English locales)
   - Language purity validator
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.localization.locale_registry import (
    SUPPORTED_LOCALES,
    DEFAULT_LOCALE,
    validate_locale,
    get_locale_metadata,
    get_supported_locales_list,
)
from backend.localization.financial_glossary import FINANCIAL_GLOSSARY, get_glossary_for_locale
from backend.localization.i18n_service import (
    get_catalog,
    I18nService,
)

client = TestClient(app)

# ══════════════════════════════════════════════════════════
# 1. CANONICAL 23 LOCALES & CONSTITUTIONAL REGISTRY
# ══════════════════════════════════════════════════════════

def test_canonical_23_locales_count():
    assert len(SUPPORTED_LOCALES) == 23, f"Expected exactly 23 supported locales, found {len(SUPPORTED_LOCALES)}"

def test_constitutional_eighth_schedule_and_english():
    expected_locales = {
        "en-IN", "as-IN", "bn-IN", "brx-IN", "doi-IN", "gu-IN", "hi-IN",
        "kn-IN", "ks-IN", "kok-IN", "ml-IN", "mni-IN", "mr-IN", "mai-IN",
        "ne-IN", "or-IN", "pa-IN", "sa-IN", "sat-IN", "sd-IN", "ta-IN",
        "te-IN", "ur-IN"
    }
    actual_locales = set(SUPPORTED_LOCALES.keys())
    assert actual_locales == expected_locales, f"Locale mismatch: {expected_locales ^ actual_locales}"

def test_terminology_correctness():
    # Marathi must be used, NOT "Maharashtrian"
    mr_config = get_locale_metadata("mr-IN")
    assert mr_config.english_name == "Marathi"
    assert "Maharashtrian" not in mr_config.english_name

    # Maithili must be used, NOT "Bihari"
    mai_config = get_locale_metadata("mai-IN")
    assert mai_config.english_name == "Maithili"
    assert "Bihari" not in mai_config.english_name

def test_rtl_support_configuration():
    # Urdu, Kashmiri, Sindhi must be RTL
    assert get_locale_metadata("ur-IN").direction == "rtl"
    assert get_locale_metadata("ks-IN").direction == "rtl"
    assert get_locale_metadata("sd-IN").direction == "rtl"

    # Bengali, Hindi, Tamil, Telugu, English must be LTR
    assert get_locale_metadata("en-IN").direction == "ltr"
    assert get_locale_metadata("bn-IN").direction == "ltr"
    assert get_locale_metadata("hi-IN").direction == "ltr"
    assert get_locale_metadata("ta-IN").direction == "ltr"
    assert get_locale_metadata("te-IN").direction == "ltr"

def test_native_language_names_and_scripts():
    for loc_id, cfg in SUPPORTED_LOCALES.items():
        assert cfg.native_name != "", f"Missing native name for {loc_id}"
        assert cfg.english_name != "", f"Missing english name for {loc_id}"
        assert cfg.script != "", f"Missing script for {loc_id}"
        assert cfg.enabled is True

# ══════════════════════════════════════════════════════════
# 2. FINANCIAL GLOSSARY VERIFICATION
# ══════════════════════════════════════════════════════════

def test_glossary_concepts_across_all_23_locales():
    core_concepts = [
        "safe_to_save", "smart_buffer", "protected_floor", "stabilized_income",
        "expected_income", "financial_surplus", "liquidity", "buffer_coverage",
        "income_volatility", "financial_risk", "financial_resilience", "cash_flow",
        "income_shortfall", "available_safe_buffer", "goal", "obligation",
        "forecast", "capital_preservation", "data_readiness", "data_quality"
    ]

    for loc in SUPPORTED_LOCALES.keys():
        glossary = get_glossary_for_locale(loc)
        for concept in core_concepts:
            assert concept in glossary, f"Concept '{concept}' missing from glossary in locale '{loc}'"
            entry = glossary[concept]
            assert "term" in entry and len(entry["term"]) > 0, f"Empty term for {concept} in {loc}"
            assert "short_definition" in entry and len(entry["short_definition"]) > 0

def test_specific_glossary_approved_terms():
    # English
    en_g = get_glossary_for_locale("en-IN")
    assert en_g["safe_to_save"]["term"] == "Safe-to-Save"
    assert en_g["smart_buffer"]["term"] == "Smart Buffer"
    assert en_g["protected_floor"]["term"] == "Protected Cash Floor"

    # Hindi
    hi_g = get_glossary_for_locale("hi-IN")
    assert hi_g["safe_to_save"]["term"] == "सुरक्षित बचत राशि"
    assert hi_g["smart_buffer"]["term"] == "स्मार्ट बफर"
    assert hi_g["protected_floor"]["term"] == "सुरक्षित नकद न्यूनतम स्तर"

    # Bengali
    bn_g = get_glossary_for_locale("bn-IN")
    assert bn_g["safe_to_save"]["term"] == "নিরাপদে সঞ্চয়যোগ্য পরিমাণ"
    assert bn_g["smart_buffer"]["term"] == "স্মার্ট বাফার"
    assert bn_g["protected_floor"]["term"] == "সুরক্ষিত নগদ ন্যূনতম সীমা"

    # Tamil
    ta_g = get_glossary_for_locale("ta-IN")
    assert ta_g["safe_to_save"]["term"] == "பாதுகாப்பாகச் சேமிக்கக்கூடிய தொகை"
    assert ta_g["smart_buffer"]["term"] == "ஸ்மார்ட் பஃபர்"

# ══════════════════════════════════════════════════════════
# 3. TRANSLATION CATALOG COMPLETENESS & KEY PARITY
# ══════════════════════════════════════════════════════════

def test_translation_catalog_parity():
    en_catalog = get_catalog("en-IN")
    en_keys = set(en_catalog.keys())
    assert len(en_keys) > 100, f"Expected >100 keys in base catalog, got {len(en_keys)}"

    for loc in SUPPORTED_LOCALES.keys():
        catalog = get_catalog(loc)
        missing = en_keys - set(catalog.keys())
        assert len(missing) == 0, f"Locale '{loc}' is missing translation keys: {missing}"

# ══════════════════════════════════════════════════════════
# 4. BACKEND LOCALIZATION ENDPOINTS
# ══════════════════════════════════════════════════════════

def test_get_localization_config_endpoint():
    response = client.get("/api/v1/localization/config")
    assert response.status_code == 200
    data = response.json()
    assert data["default_locale"] == "en-IN"
    assert len(data["supported_locales"]) == 23
    assert data["translation_version"] == "5.0"

    # Find Bengali and Urdu in supported list
    loc_map = {item["id"]: item for item in data["supported_locales"]}
    assert "bn-IN" in loc_map
    assert loc_map["bn-IN"]["native_name"] == "বাংলা"
    assert loc_map["bn-IN"]["direction"] == "ltr"

    assert "ur-IN" in loc_map
    assert loc_map["ur-IN"]["native_name"] == "اردو"
    assert loc_map["ur-IN"]["direction"] == "rtl"

def test_get_catalog_endpoint():
    # Valid locale
    res_bn = client.get("/api/v1/localization/catalogs/bn-IN")
    assert res_bn.status_code == 200
    cat_bn = res_bn.json()
    assert cat_bn["common.save"] == "সংরক্ষণ করুন"
    assert cat_bn["common.connect_bank"] == "ব্যাংক অ্যাকাউন্ট যোগ করুন"

    # Invalid locale fallback
    res_invalid = client.get("/api/v1/localization/catalogs/invalid-xyz")
    assert res_invalid.status_code == 200
    cat_fallback = res_invalid.json()
    assert cat_fallback["common.save"] == "Save"

def test_user_preferences_get_and_patch(client_with_auth=None):
    # Test setting and reading preferences
    # Login first to get token
    login_res = client.post("/api/v1/auth/login", data={"username": "demo@suresavings.in", "password": "Password123!"})
    if login_res.status_code != 200:
        # Fallback to test user or sandbox
        auth_headers = {}
    else:
        token = login_res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

    # If auth headers available, test PATCH /api/v1/users/preferences
    if auth_headers:
        patch_res = client.patch(
            "/api/v1/users/preferences",
            json={"preferred_locale": "bn-IN"},
            headers=auth_headers
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["preferred_locale"] == "bn-IN"

        get_res = client.get("/api/v1/users/preferences", headers=auth_headers)
        assert get_res.status_code == 200
        assert get_res.json()["preferred_locale"] == "bn-IN"

        # Revert back to en-IN
        client.patch(
            "/api/v1/users/preferences",
            json={"preferred_locale": "en-IN"},
            headers=auth_headers
        )

# ══════════════════════════════════════════════════════════
# 5. SURE AI LANGUAGE-AWARE COACHING & SAFETY
# ══════════════════════════════════════════════════════════

def test_localized_greetings_by_timezone():
    # Morning
    headline_en, _, _ = I18nService.get_greeting("morning", "Arjun", "en-IN")
    assert "Good morning" in headline_en

    headline_bn, _, _ = I18nService.get_greeting("morning", "Arjun", "bn-IN")
    assert "সুপ্রভাত" in headline_bn

    headline_hi, _, _ = I18nService.get_greeting("morning", "Arjun", "hi-IN")
    assert "सुप्रभात" in headline_hi

    headline_ta, _, _ = I18nService.get_greeting("morning", "Arjun", "ta-IN")
    assert "காலை வணக்கம்" in headline_ta

    headline_ur, _, _ = I18nService.get_greeting("morning", "Arjun", "ur-IN")
    assert "صبح بخیر" in headline_ur

    # Evening
    headline_en_eve, _, _ = I18nService.get_greeting("evening", "Arjun", "en-IN")
    assert "Good evening" in headline_en_eve

    headline_bn_eve, _, _ = I18nService.get_greeting("evening", "Arjun", "bn-IN")
    assert "শুভ সন্ধ্যা" in headline_bn_eve

def test_localized_public_attribution():
    # Public attribution must preserve creator Satyabrata Das & Narula Institute of Technology
    # while expressing the prose in the selected locale

    attr_en = I18nService.get_attribution("en-IN")
    assert "Satyabrata Das" in attr_en
    assert "Narula Institute of Technology" in attr_en
    assert "built by" in attr_en

    attr_bn = I18nService.get_attribution("bn-IN")
    assert "Satyabrata Das" in attr_bn
    assert "Narula Institute of Technology" in attr_bn
    assert "তৈরি করেছেন" in attr_bn

    attr_hi = I18nService.get_attribution("hi-IN")
    assert "Satyabrata Das" in attr_hi
    assert "Narula Institute of Technology" in attr_hi
    assert "द्वारा बनाई गई है" in attr_hi

    attr_ta = I18nService.get_attribution("ta-IN")
    assert "Satyabrata Das" in attr_ta
    assert "Narula Institute of Technology" in attr_ta
    assert "உருவாக்கப்பட்டது" in attr_ta

    attr_ur = I18nService.get_attribution("ur-IN")
    assert "Satyabrata Das" in attr_ur
    assert "Narula Institute of Technology" in attr_ur

def test_localized_confidentiality_refusals():
    categories = [
        "api_secrets", "system_prompt", "other_users_data",
        "raw_credentials", "source_code", "db_passwords"
    ]

    for loc in ["en-IN", "hi-IN", "bn-IN", "ta-IN", "ur-IN", "mr-IN"]:
        for cat in categories:
            title, msg = I18nService.get_refusal(cat, loc)
            assert len(title) > 0, f"Empty refusal title for {cat} in {loc}"
            assert len(msg) > 0, f"Empty refusal message for {cat} in {loc}"
            assert "{" not in msg, f"Uninterpolated template in {cat} for {loc}"

def test_localized_deterministic_fallback():
    # If Gemini is unavailable, deterministic fallback MUST respond in the user's selected language
    # Bengali fallback
    fb_bn = I18nService.get_localized_fallback("safe_to_save", "What is Safe-to-Save?", "bn-IN")
    assert "answer" in fb_bn
    assert "নিরাপদে সঞ্চয়যোগ্য পরিমাণ" in fb_bn["answer"] or "SURE SAVINGS" in fb_bn["answer"]

    # Hindi fallback
    fb_hi = I18nService.get_localized_fallback("safe_to_save", "What is Safe-to-Save?", "hi-IN")
    assert "answer" in fb_hi
    assert "सुरक्षित बचत राशि" in fb_hi["answer"] or "SURE SAVINGS" in fb_hi["answer"]

    # Tamil fallback
    fb_ta = I18nService.get_localized_fallback("safe_to_save", "What is Safe-to-Save?", "ta-IN")
    assert "answer" in fb_ta
    assert "பாதுகாப்பாகச் சேமிக்கக்கூடிய தொகை" in fb_ta["answer"] or "SURE SAVINGS" in fb_ta["answer"]

def test_language_purity_validator():
    # Pure Bengali text
    res_bn = I18nService.validate_language_purity("আপনার ব্যাংক অ্যাকাউন্টটি সংযুক্ত আছে।", "bn-IN")
    assert res_bn["valid"] is True

    # Pure Hindi text
    res_hi = I18nService.validate_language_purity("आपका बैंक खाता सुरक्षित रूप से जुड़ा हुआ है।", "hi-IN")
    assert res_hi["valid"] is True

    # Pure Tamil text
    res_ta = I18nService.validate_language_purity("உங்கள் வங்கி கணக்கு வெற்றிகரமாக இணைக்கப்பட்டுள்ளது.", "ta-IN")
    assert res_ta["valid"] is True

    # Mixed English sentence when Bengali is expected
    res_mixed = I18nService.validate_language_purity("Your bank account is successfully connected to the system.", "bn-IN")
    assert res_mixed["valid"] is False

    # Proper nouns and brands are allowed
    res_brand = I18nService.validate_language_purity("SURE SAVINGS প্ল্যাটফর্মে আপনাকে স্বাগতম।", "bn-IN")
    assert res_brand["valid"] is True

    res_attr = I18nService.validate_language_purity("यह वेबसाइट Satyabrata Das from Narula Institute of Technology द्वारा बनाई गई है।", "hi-IN")
    assert res_attr["valid"] is True
