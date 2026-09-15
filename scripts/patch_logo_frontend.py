#!/usr/bin/env python3
"""
Patch SURE SAVINGS logo and favicons across all HTML pages and JS components.
"""

import re
import os

FAVICON_HEAD_TAGS = """  <!-- Favicon & Brand Icons -->
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/images/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/images/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/images/apple-touch-icon.png">
  <link rel="icon" type="image/svg+xml" href="assets/images/favicon.svg">"""

DASHBOARD_LOGO_IMG = '<img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-8 h-8 object-contain shrink-0" width="32" height="32">'
LANDING_LOGO_IMG = '<img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-10 h-10 object-contain group-hover:scale-105 transition-transform shrink-0" width="40" height="40">'
LOGIN_LOGO_IMG = '<img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-11 h-11 object-contain shadow-sm shrink-0" width="44" height="44">'
COACH_AVATAR_IMG = '<img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-9 h-9 object-contain shrink-0" width="36" height="36">'

HTML_FILES = [
    'index.html',
    'landing.html',
    'login.html',
    'activity.html',
    'bank-accounts.html',
    'calendar.html',
    'coach.html',
    'decision-pipeline.html',
    'goals.html',
    'health.html',
    'income-intelligence.html',
    'pipeline.html',
    'planner.html',
    'resilience-plan.html',
    'risk.html',
    'simulator.html'
]

# 1. Update HTML files
for filename in HTML_FILES:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject Favicons into <head> if not already present
    if 'rel="icon"' not in content:
        # Insert right before </head>
        content = content.replace('</head>', f'{FAVICON_HEAD_TAGS}\n</head>')
        print(f'Added favicon tags to {filename}')

    # Replace dashboard header placeholder
    # Pattern: <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center font-bold text-white text-sm shadow-md">\s*S\s*</div>
    pattern_w8 = re.compile(r'<div class="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center font-bold text-white text-sm shadow-md">\s*S\s*</div>')
    if pattern_w8.search(content):
        content = pattern_w8.sub(DASHBOARD_LOGO_IMG, content)
        print(f'Replaced w-8 logo mark in {filename}')

    # Replace landing.html logo mark
    pattern_landing = re.compile(r'<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-black text-lg shadow-md group-hover:scale-105 transition-transform">\s*S\s*</div>')
    if pattern_landing.search(content):
        content = pattern_landing.sub(LANDING_LOGO_IMG, content)
        print(f'Replaced landing logo mark in {filename}')

    # Replace login.html logo mark
    pattern_login = re.compile(r'<div class="w-11 h-11 bg-gradient-to-br from-brand-500 to-brand-700 rounded-xl flex items-center justify-center font-bold text-xl text-white shadow-md">\s*S\s*</div>')
    if pattern_login.search(content):
        content = pattern_login.sub(LOGIN_LOGO_IMG, content)
        print(f'Replaced login logo mark in {filename}')

    # Replace coach.html initial message avatar
    pattern_coach = re.compile(r'<div class="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-bold text-sm shadow-md flex-shrink-0">\s*S\s*</div>')
    if pattern_coach.search(content):
        content = pattern_coach.sub(f'<div class="w-9 h-9 rounded-xl flex items-center justify-center shadow-md flex-shrink-0">{COACH_AVATAR_IMG}</div>', content)
        print(f'Replaced coach message avatar in {filename}')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# 2. Update js/coach.js
coach_js_path = 'js/coach.js'
with open(coach_js_path, 'r', encoding='utf-8') as f:
    coach_content = f.read()

# Typing bubble avatar
old_typing_avatar = """    <div class="relative w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-bold text-sm shadow-sm flex-shrink-0">
      S
      <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-teal-400 border-2 border-white"></span>
    </div>"""

new_typing_avatar = """    <div class="relative w-9 h-9 rounded-xl flex items-center justify-center shadow-sm flex-shrink-0">
      <img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-9 h-9 object-contain" width="36" height="36">
      <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-teal-400 border-2 border-white"></span>
    </div>"""

if old_typing_avatar in coach_content:
    coach_content = coach_content.replace(old_typing_avatar, new_typing_avatar)
    print("Updated coach typing indicator in js/coach.js")

# Bot reply bubble avatar
old_bot_avatar = """      <div class="relative w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-bold text-sm shadow-md flex-shrink-0">
        S
        <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ${isLiveGemini ? 'bg-teal-400' : 'bg-emerald-400'} border-2 border-white"></span>
      </div>"""

new_bot_avatar = """      <div class="relative w-9 h-9 rounded-xl flex items-center justify-center shadow-md flex-shrink-0">
        <img src="assets/images/sure-savings-logo.png" alt="SURE SAVINGS" class="w-9 h-9 object-contain" width="36" height="36">
        <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ${isLiveGemini ? 'bg-teal-400' : 'bg-emerald-400'} border-2 border-white"></span>
      </div>"""

if old_bot_avatar in coach_content:
    coach_content = coach_content.replace(old_bot_avatar, new_bot_avatar)
    print("Updated coach reply bubble in js/coach.js")

with open(coach_js_path, 'w', encoding='utf-8') as f:
    f.write(coach_content)

print("All frontend files successfully patched with SURE SAVINGS logo and favicon!")
