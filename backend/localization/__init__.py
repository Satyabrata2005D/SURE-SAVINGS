"""
SURE SAVINGS: Central Localization Package
Supports English + the 22 Eighth Schedule Indian languages (23 total).
"""
from backend.localization.locale_registry import (
    SUPPORTED_LOCALES,
    DEFAULT_LOCALE,
    LocaleMetadata,
    get_locale_metadata,
    validate_locale,
    get_supported_locales_list,
)
from backend.localization.financial_glossary import (
    FINANCIAL_GLOSSARY,
    get_glossary_term,
    get_locale_glossary,
)

__all__ = [
    "SUPPORTED_LOCALES",
    "DEFAULT_LOCALE",
    "LocaleMetadata",
    "get_locale_metadata",
    "validate_locale",
    "get_supported_locales_list",
    "FINANCIAL_GLOSSARY",
    "get_glossary_term",
    "get_locale_glossary",
]
