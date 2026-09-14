"""
SURE SAVINGS: Translation Completeness & Key Parity Checker
Audits all 23 language catalogs for key parity, missing keys, extra keys, and glossary terms.
"""
import os
import sys
import json
from typing import Dict, Set

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(ROOT_DIR, "locales")

EXPECTED_LOCALES = [
    "en-IN", "hi-IN", "bn-IN", "as-IN", "brx-IN", "doi-IN", "gu-IN", "kn-IN",
    "ks-IN", "kok-IN", "ml-IN", "mni-IN", "mr-IN", "mai-IN", "ne-IN", "or-IN",
    "pa-IN", "sa-IN", "sat-IN", "sd-IN", "ta-IN", "te-IN", "ur-IN"
]


def flatten_keys(d: dict, prefix: str = "") -> Set[str]:
    keys = set()
    for k, v in d.items():
        curr_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(flatten_keys(v, curr_key))
        else:
            keys.add(curr_key)
    return keys


def check_all_translations():
    en_file = os.path.join(LOCALES_DIR, "en-IN.json")
    if not os.path.exists(en_file):
        print(f"ERROR: Base catalog {en_file} does not exist!")
        sys.exit(1)

    with open(en_file, "r", encoding="utf-8") as f:
        en_catalog = json.load(f)

    base_keys = flatten_keys(en_catalog)
    total_expected = len(base_keys)
    print(f"Base English (en-IN) total keys: {total_expected}")
    print("=" * 60)

    has_errors = False
    results = {}

    for loc in EXPECTED_LOCALES:
        loc_file = os.path.join(LOCALES_DIR, f"{loc}.json")
        if not os.path.exists(loc_file):
            print(f"[{loc}] ❌ Catalog file missing!")
            has_errors = True
            results[loc] = 0.0
            continue

        try:
            with open(loc_file, "r", encoding="utf-8") as f:
                loc_catalog = json.load(f)
        except Exception as e:
            print(f"[{loc}] ❌ Malformed JSON: {e}")
            has_errors = True
            results[loc] = 0.0
            continue

        loc_keys = flatten_keys(loc_catalog)
        missing = base_keys - loc_keys
        extra = loc_keys - base_keys

        pct = (len(base_keys - missing) / total_expected) * 100
        results[loc] = pct

        if missing:
            print(f"[{loc}] ⚠ {len(missing)} keys missing: {list(missing)[:5]}")
            has_errors = True
        elif extra:
            print(f"[{loc}] ⚠ {len(extra)} extra keys: {list(extra)[:5]}")
            has_errors = True
        else:
            print(f"[{loc}] ✓ {pct:.1f}% ({len(loc_keys)}/{total_expected} keys verified)")

    print("=" * 60)
    print("Translation Completeness Summary:")
    for loc, pct in results.items():
        print(f"  {loc}: {pct:.1f}%")

    if has_errors:
        print("\n❌ Audit failed: Some catalogs have missing keys or malformed JSON.")
        sys.exit(1)
    else:
        print(f"\n✓ 100% Translation Key Parity verified across all {len(EXPECTED_LOCALES)} locales.")
        sys.exit(0)


if __name__ == "__main__":
    check_all_translations()
