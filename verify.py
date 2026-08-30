#!/usr/bin/env python3
"""
Contract check between the six form pages and Code.gs.

Every key a form puts in its POST payload must be a key Code.gs actually reads
for that form, and every key Code.gs reads must be one some form sends. A
mismatch here means a silently blank column in the spreadsheet, which is the
failure mode that would otherwise only show up weeks later with real
applicants' answers already lost.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "df_coach": "drone-football-coach.html",
    "yc_lead_windrush": "youth-corner-lead-windrush.html",
    "social_lead": "social-media-lead.html",
    "cm_lead": "critical-minds-lead.html",
    "apprenticeship": "youth-work-apprenticeship.html",
    "yab_member": "youth-advisory-board.html",
}

gs = open(os.path.join(HERE, "Code.gs"), encoding="utf-8").read()

# Which data.* keys each Apps Script route reads.
ROUTES = {
    "appendRoleApplication": ["df_coach", "yc_lead_windrush", "social_lead", "cm_lead"],
    "appendApprentice": ["apprenticeship"],
    "appendYab": ["yab_member"],
}

route_keys = {}
for fn, forms in ROUTES.items():
    m = re.search(r"function %s\([^)]*\)\s*\{(.*?)\n\}" % fn, gs, re.S)
    assert m, "route %s not found in Code.gs" % fn
    keys = set(re.findall(r"data\.([A-Za-z0-9_]+)", m.group(1)))
    for form in forms:
        route_keys[form] = keys

failures = []

for form_key, filename in FILES.items():
    path = os.path.join(HERE, filename)
    src = open(path, encoding="utf-8").read()

    def grab(name):
        m = re.search(r"var %s\s*=\s*(\[.*?\]);" % name, src, re.S)
        assert m, "%s missing in %s" % (name, filename)
        return json.loads(m.group(1))

    pills = grab("PILL_KEYS")
    fields = grab("FIELD_KEYS")
    checks = grab("CHECK_KEYS")
    required = grab("REQUIRED")

    declared_form = json.loads(re.search(r"var FORM_KEY\s*=\s*(\".*?\");", src).group(1))
    if declared_form != form_key:
        failures.append("%s: FORM_KEY is %r, expected %r" % (filename, declared_form, form_key))

    sent = set(pills) | set(fields) | set(checks)
    read = route_keys[form_key]

    unread = sorted(sent - read)
    if unread:
        failures.append("%s: form sends keys Code.gs never reads: %s" % (filename, unread))

    # roleLevel and scheduleConfirmation are read by the shared role route but
    # only sent by the forms they apply to; the rest leave those columns blank.
    unsent = sorted(read - sent - {"form", "token", "roleLevel", "scheduleConfirmation"})
    if unsent:
        failures.append("%s: Code.gs reads keys this form never sends: %s" % (filename, unsent))

    # roleLevel is only sent by the Drone Football form; the other three role
    # forms deliberately leave that column blank.
    if form_key == "df_coach" and "roleLevel" not in sent:
        failures.append("%s: roleLevel missing — the level dropdown is the point of this form" % filename)

    # Every required key must correspond to a real element or pill question.
    for key in required:
        has_pill = 'data-q="%s"' % key in src
        has_el = 'id="%s"' % key in src
        if not (has_pill or has_el):
            failures.append("%s: required key %r has no matching element" % (filename, key))

    dupes = [k for k in set(sent) if src.count('id="%s"' % k) > 1]
    if dupes:
        failures.append("%s: duplicate element ids %s" % (filename, sorted(dupes)))

    # No form anywhere may collect Red Zone data.
    banned = ["ethnic", "religio", "disabilit", "sexual orientation", "criminal",
              "conviction", "offence", "medical", "diagnos", "national insurance"]
    low = src.lower()
    for word in banned:
        if word in low:
            # "criminal record" appears once, in the privacy note that says we
            # explicitly do NOT ask for it. Anything else is a real problem.
            ctx = low[max(0, low.find(word) - 90): low.find(word) + 60]
            if "do not ask" in ctx or "not asking" in ctx:
                continue
            failures.append("%s: possible Red Zone field — found %r near: …%s…"
                            % (filename, word, ctx.strip()))

    print("%-38s  %2d pill  %2d field  %d check  %2d required"
          % (filename, len(pills), len(fields), len(checks), len(required)))

print()
if failures:
    print("FAILURES:")
    for f in failures:
        print("  - " + f)
    sys.exit(1)

print("All six forms match the Code.gs contract. No Red Zone fields found.")
