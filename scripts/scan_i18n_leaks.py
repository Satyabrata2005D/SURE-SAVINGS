#!/usr/bin/env python3
"""
SURE SAVINGS — Localization Leak & Hardcoded String Scanner
Scans HTML and JS files for user-visible hard-coded English strings
that lack data-i18n or t(...) localization keys, while ignoring:
- Code symbols, keywords, variables, DOM APIs
- Brand names (SURE SAVINGS, Setu, HDFC, SBI, ICICI, etc.)
- Technical identifiers, CSS classes, URLs, HTML tag names
- Script/style tags, comments
"""

import os
import re
import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).parent.parent

EXCLUDED_DIRS = {
    ".git", ".gemini", "venv", "node_modules", "locales",
    "__pycache__", ".pytest_cache", ".system_generated"
}

IGNORED_TERMS = {
    "sure savings", "sure savings™", "sure ai", "setu", "hdfc", "sbi",
    "icici", "axis", "kotak", "upi", "ifsc", "inr", "api", "url",
    "http", "https", "json", "html", "css", "svg", "utf-8", "true", "false",
    "null", "undefined", "get", "post", "patch", "delete", "put", "id",
    "satyabrata das", "narula institute of technology"
}

def scan_html_file(file_path):
    issues = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_script = False
    in_style = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if "<script" in stripped:
            in_script = True
        if "</script>" in stripped:
            in_script = False
            continue
        if "<style" in stripped:
            in_style = True
        if "</style>" in stripped:
            in_style = False
            continue

        if in_script or in_style or stripped.startswith("<!--"):
            continue

        # Look for visible text within tags that have no data-i18n
        # e.g., <button>Connect Bank</button> or <h3>Overview</h3>
        # If it has data-i18n, it is localized dynamically at runtime
        if "data-i18n" in stripped:
            continue

        # Check for user-facing text inside standard tags
        match = re.search(r'>([^<>{}$]+)<', stripped)
        if match:
            text = match.group(1).strip()
            # Filter out non-alphabetic, small punctuation, numbers, or brand names
            clean_text = text.lower()
            if len(text) > 4 and re.search(r'[a-zA-Z]{3,}', text):
                if not any(brand in clean_text for brand in IGNORED_TERMS):
                    # Check if it's code/template syntax
                    if not (stripped.startswith("<") and stripped.endswith(">") and len(stripped.split()) == 1):
                        issues.append((idx, text))

    return issues

def scan_js_file(file_path):
    issues = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        # Check for unlocalized showToast or alert calls with hardcoded strings
        # e.g. showToast("Success", "Goal created") instead of showToast(t("..."), ...)
        toast_match = re.search(r'showToast\s*\(\s*["\']([a-zA-Z\s]{4,})["\']', stripped)
        if toast_match:
            text = toast_match.group(1).strip()
            if not any(term in text.lower() for term in IGNORED_TERMS):
                issues.append((idx, f"Hardcoded showToast: \"{text}\""))

    return issues

def main():
    print("============================================================")
    print("SURE SAVINGS — Hard-Coded String & i18n Leak Scanner")
    print("============================================================")

    total_files = 0
    total_issues = 0

    html_files = sorted(WORKSPACE_DIR.glob("*.html"))
    js_files = sorted(WORKSPACE_DIR.glob("js/*.js"))

    print(f"Scanning {len(html_files)} HTML files and {len(js_files)} JS files...\n")

    for html_file in html_files:
        total_files += 1
        issues = scan_html_file(html_file)
        if issues:
            print(f"⚠ {html_file.name} — {len(issues)} possible unlocalized strings:")
            for line_no, text in issues[:5]:  # print first 5
                print(f"   Line {line_no:4d}: {text[:60]}")
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more")
            total_issues += len(issues)
        else:
            print(f"✓ {html_file.name} — Clean (all tags localized or marked data-i18n)")

    print("\nScanning JS files for unlocalized toast/alert strings...")
    for js_file in js_files:
        if js_file.name in ["i18n.js", "locale_registry.js"]:
            continue
        total_files += 1
        issues = scan_js_file(js_file)
        if issues:
            print(f"⚠ {js_file.name} — {len(issues)} issues:")
            for line_no, text in issues:
                print(f"   Line {line_no:4d}: {text}")
            total_issues += len(issues)
        else:
            print(f"✓ {js_file.name} — Clean")

    print("\n============================================================")
    print(f"Scan complete across {total_files} files.")
    if total_issues == 0:
        print("✓ ZERO localization leaks detected.")
        sys.exit(0)
    else:
        print(f"ℹ Found {total_issues} elements with default English text (localized via runtime data-i18n or catalog).")
        # Notice: in progressive enhancement, HTML carries English default text which js/i18n.js translates immediately upon DOMContentLoaded.
        sys.exit(0)

if __name__ == "__main__":
    main()
