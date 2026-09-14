"""
SURE SAVINGS: Central Canonical Locale Registry
Constitutional Baseline: English + 22 Eighth Schedule Indian Languages (23 total).
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

DEFAULT_LOCALE = "en-IN"

@dataclass
class LocaleMetadata:
    id: str
    english_name: str
    native_name: str
    direction: str  # "ltr" or "rtl"
    script: str     # Primary script name
    number_locale: str
    date_locale: str
    currency_locale: str
    translation_catalog_version: str
    enabled: bool
    status: str
    unicode_ranges: List[tuple]  # (start_code, end_code) for script heuristics

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert unicode ranges to hex strings for serialization
        d["unicode_ranges"] = [f"U+{s:04X}-U+{e:04X}" for s, e in self.unicode_ranges]
        return d


SUPPORTED_LOCALES: Dict[str, LocaleMetadata] = {
    "en-IN": LocaleMetadata(
        id="en-IN",
        english_name="English",
        native_name="English",
        direction="ltr",
        script="Latin",
        number_locale="en-IN",
        date_locale="en-IN",
        currency_locale="en-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0020, 0x007E)],
    ),
    "hi-IN": LocaleMetadata(
        id="hi-IN",
        english_name="Hindi",
        native_name="हिन्दी",
        direction="ltr",
        script="Devanagari",
        number_locale="hi-IN",
        date_locale="hi-IN",
        currency_locale="hi-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "bn-IN": LocaleMetadata(
        id="bn-IN",
        english_name="Bengali",
        native_name="বাংলা",
        direction="ltr",
        script="Bengali",
        number_locale="bn-IN",
        date_locale="bn-IN",
        currency_locale="bn-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0980, 0x09FF)],
    ),
    "as-IN": LocaleMetadata(
        id="as-IN",
        english_name="Assamese",
        native_name="অসমীয়া",
        direction="ltr",
        script="Bengali",
        number_locale="as-IN",
        date_locale="as-IN",
        currency_locale="as-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0980, 0x09FF)],
    ),
    "brx-IN": LocaleMetadata(
        id="brx-IN",
        english_name="Bodo",
        native_name="बड़ो",
        direction="ltr",
        script="Devanagari",
        number_locale="brx-IN",
        date_locale="brx-IN",
        currency_locale="brx-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "doi-IN": LocaleMetadata(
        id="doi-IN",
        english_name="Dogri",
        native_name="डोगरी",
        direction="ltr",
        script="Devanagari",
        number_locale="doi-IN",
        date_locale="doi-IN",
        currency_locale="doi-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "gu-IN": LocaleMetadata(
        id="gu-IN",
        english_name="Gujarati",
        native_name="ગુજરાતી",
        direction="ltr",
        script="Gujarati",
        number_locale="gu-IN",
        date_locale="gu-IN",
        currency_locale="gu-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0A80, 0x0AFF)],
    ),
    "kn-IN": LocaleMetadata(
        id="kn-IN",
        english_name="Kannada",
        native_name="ಕನ್ನಡ",
        direction="ltr",
        script="Kannada",
        number_locale="kn-IN",
        date_locale="kn-IN",
        currency_locale="kn-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0C80, 0x0CFF)],
    ),
    "ks-IN": LocaleMetadata(
        id="ks-IN",
        english_name="Kashmiri",
        native_name="کٲشُر",
        direction="rtl",
        script="Arabic",
        number_locale="ks-Arab-IN",
        date_locale="ks-Arab-IN",
        currency_locale="ks-Arab-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0600, 0x06FF), (0x0750, 0x077F)],
    ),
    "kok-IN": LocaleMetadata(
        id="kok-IN",
        english_name="Konkani",
        native_name="कोंकणी",
        direction="ltr",
        script="Devanagari",
        number_locale="kok-IN",
        date_locale="kok-IN",
        currency_locale="kok-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "ml-IN": LocaleMetadata(
        id="ml-IN",
        english_name="Malayalam",
        native_name="മലയാളം",
        direction="ltr",
        script="Malayalam",
        number_locale="ml-IN",
        date_locale="ml-IN",
        currency_locale="ml-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0D00, 0x0D7F)],
    ),
    "mni-IN": LocaleMetadata(
        id="mni-IN",
        english_name="Manipuri",
        native_name="মৈতৈলোন্",
        direction="ltr",
        script="Bengali",
        number_locale="mni-IN",
        date_locale="mni-IN",
        currency_locale="mni-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0980, 0x09FF)],
    ),
    "mr-IN": LocaleMetadata(
        id="mr-IN",
        english_name="Marathi",
        native_name="मराठी",
        direction="ltr",
        script="Devanagari",
        number_locale="mr-IN",
        date_locale="mr-IN",
        currency_locale="mr-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "mai-IN": LocaleMetadata(
        id="mai-IN",
        english_name="Maithili",
        native_name="मैथिली",
        direction="ltr",
        script="Devanagari",
        number_locale="mai-IN",
        date_locale="mai-IN",
        currency_locale="mai-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "ne-IN": LocaleMetadata(
        id="ne-IN",
        english_name="Nepali",
        native_name="नेपाली",
        direction="ltr",
        script="Devanagari",
        number_locale="ne-IN",
        date_locale="ne-IN",
        currency_locale="ne-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "or-IN": LocaleMetadata(
        id="or-IN",
        english_name="Odia",
        native_name="ଓଡ଼ିଆ",
        direction="ltr",
        script="Odia",
        number_locale="or-IN",
        date_locale="or-IN",
        currency_locale="or-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0B00, 0x0B7F)],
    ),
    "pa-IN": LocaleMetadata(
        id="pa-IN",
        english_name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        direction="ltr",
        script="Gurmukhi",
        number_locale="pa-IN",
        date_locale="pa-IN",
        currency_locale="pa-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0A00, 0x0A7F)],
    ),
    "sa-IN": LocaleMetadata(
        id="sa-IN",
        english_name="Sanskrit",
        native_name="संस्कृतम्",
        direction="ltr",
        script="Devanagari",
        number_locale="sa-IN",
        date_locale="sa-IN",
        currency_locale="sa-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0900, 0x097F)],
    ),
    "sat-IN": LocaleMetadata(
        id="sat-IN",
        english_name="Santali",
        native_name="ᱥᱟᱱᱛᱟᱲᱤ",
        direction="ltr",
        script="Ol Chiki",
        number_locale="sat-IN",
        date_locale="sat-IN",
        currency_locale="sat-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x1C50, 0x1C7F)],
    ),
    "sd-IN": LocaleMetadata(
        id="sd-IN",
        english_name="Sindhi",
        native_name="سنڌي",
        direction="rtl",
        script="Arabic",
        number_locale="sd-Arab-IN",
        date_locale="sd-Arab-IN",
        currency_locale="sd-Arab-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0600, 0x06FF)],
    ),
    "ta-IN": LocaleMetadata(
        id="ta-IN",
        english_name="Tamil",
        native_name="தமிழ்",
        direction="ltr",
        script="Tamil",
        number_locale="ta-IN",
        date_locale="ta-IN",
        currency_locale="ta-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0B80, 0x0BFF)],
    ),
    "te-IN": LocaleMetadata(
        id="te-IN",
        english_name="Telugu",
        native_name="తెలుగు",
        direction="ltr",
        script="Telugu",
        number_locale="te-IN",
        date_locale="te-IN",
        currency_locale="te-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0C00, 0x0C7F)],
    ),
    "ur-IN": LocaleMetadata(
        id="ur-IN",
        english_name="Urdu",
        native_name="اردو",
        direction="rtl",
        script="Arabic",
        number_locale="ur-IN",
        date_locale="ur-IN",
        currency_locale="ur-IN",
        translation_catalog_version="1.0.0",
        enabled=True,
        status="GA",
        unicode_ranges=[(0x0600, 0x06FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    ),
}


def validate_locale(locale: Optional[str]) -> str:
    """
    Validates the given locale identifier against SUPPORTED_LOCALES.
    Falls back safely to DEFAULT_LOCALE (en-IN) if invalid or unsupported.
    """
    if not locale or not isinstance(locale, str):
        return DEFAULT_LOCALE

    cleaned = locale.strip()
    if cleaned in SUPPORTED_LOCALES:
        return cleaned

    # Try matching prefix, e.g. "hi" -> "hi-IN", "bn" -> "bn-IN"
    lang_code = cleaned.split("-")[0].lower()
    for loc_id in SUPPORTED_LOCALES:
        if loc_id.split("-")[0].lower() == lang_code:
            return loc_id

    return DEFAULT_LOCALE


def get_locale_metadata(locale: Optional[str]) -> LocaleMetadata:
    """Returns the metadata object for a validated locale."""
    valid_id = validate_locale(locale)
    return SUPPORTED_LOCALES[valid_id]


def get_supported_locales_list() -> List[Dict[str, Any]]:
    """Returns clean serialized list of all 23 supported locales for APIs."""
    return [meta.to_dict() for meta in SUPPORTED_LOCALES.values()]
