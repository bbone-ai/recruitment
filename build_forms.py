#!/usr/bin/env python3
"""
Generates the six OXIE recruitment application pages.

Every page is standalone: one HTML file, inlined CSS and JS, the OXIE logo as
the only external asset. Same visual language and same offline-safe submit
queue as the Quality Measurement forms, so anyone who has used those will
recognise these.

Run:  python3 build_forms.py
"""

import html
import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

APPS_SCRIPT_URL = "REPLACE_WITH_YOUR_APPS_SCRIPT_EXEC_URL"

# --------------------------------------------------------------------- css --

CSS = """
  :root{
    --ink:#1a1a1a; --paper:#ffffff; --line:#f0d9dc;
    --red:#ff0255; --red-dark:#c1013f;
    --pill:#ffffff; --pill-border:#e3b7bf;
    --pill-selected:#ff0255; --pill-selected-ink:#ffffff;
    --accent:#6b6b6b; --good:#2e6b4f; --wash:#fff5f7;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;padding:0;background:var(--paper);color:var(--ink);
    font-family:'Lato',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  body{padding:20px 16px 60px;max-width:600px;margin:0 auto;}
  .logo-wrap{text-align:center;margin-bottom:18px;}
  .logo-wrap img{height:120px;width:auto;}
  h1{font-size:24px;font-weight:700;margin:8px 0 4px;line-height:1.25;color:var(--red);}
  .sub{font-size:15px;color:var(--accent);margin:0 0 10px;line-height:1.55;}
  .meta{font-size:14px;color:var(--ink);margin:0 0 26px;line-height:1.7;
    padding:14px 16px;background:var(--wash);border-radius:10px;border:1px solid var(--line);}
  .meta strong{font-weight:700;}
  .meta div + div{margin-top:4px;}
  h2{font-size:13px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
    color:var(--red);margin:38px 0 4px;padding-bottom:8px;border-bottom:2px solid var(--line);}
  h2:first-of-type{margin-top:30px;}
  .section-note{font-size:13px;color:var(--accent);margin:10px 0 0;line-height:1.5;}
  .q{margin-top:24px;}
  .q-text{font-size:16px;font-weight:600;margin:0 0 6px;line-height:1.4;}
  .q-hint{font-size:13px;color:var(--accent);margin:0 0 10px;line-height:1.45;}
  .req{color:var(--red);font-weight:700;}
  .options{display:grid;gap:6px;}
  .options.c2{grid-template-columns:repeat(2,1fr);}
  .options.c3{grid-template-columns:repeat(3,1fr);}
  .options.c4{grid-template-columns:repeat(4,1fr);}
  .options.c1{grid-template-columns:1fr;}
  .opt{
    padding:12px 8px;text-align:center;border-radius:10px;border:1.5px solid var(--pill-border);
    background:var(--pill);font-size:13px;font-weight:500;cursor:pointer;user-select:none;
    line-height:1.35;transition:background .15s,color .15s,border-color .15s;
  }
  .options.c1 .opt{text-align:left;padding:13px 14px;}
  .opt.selected{background:var(--pill-selected);color:var(--pill-selected-ink);border-color:var(--pill-selected);}
  input[type=text],input[type=email],input[type=tel],input[type=date],select,textarea{
    width:100%;padding:13px 12px;border-radius:10px;border:1.5px solid var(--pill-border);
    font-size:16px;font-family:inherit;background:#fff;color:var(--ink);
  }
  textarea{min-height:96px;resize:vertical;line-height:1.5;}
  select{appearance:none;background-image:url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23c1013f' d='M6 8 0 0h12z'/%3E%3C/svg%3E");
    background-repeat:no-repeat;background-position:right 14px center;padding-right:36px;}
  .row{display:flex;gap:10px;}
  .row > div{flex:1;min-width:0;}
  .row label{display:block;font-size:14px;font-weight:600;margin-bottom:6px;}
  .consent{display:flex;gap:12px;align-items:flex-start;padding:14px;border-radius:10px;
    border:1.5px solid var(--pill-border);background:var(--wash);cursor:pointer;}
  .consent input{width:20px;height:20px;flex:0 0 20px;margin:2px 0 0;accent-color:var(--red);}
  .consent span{font-size:14px;line-height:1.5;}
  .conditional{display:none;margin-top:16px;padding:16px;border-radius:10px;
    background:var(--wash);border:1px solid var(--line);}
  .conditional.show{display:block;}
  .conditional .q:first-child{margin-top:0;}
  .jd{margin:0 0 26px;}
  .jd-label{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
    color:var(--accent);margin:0 0 8px;}
  .jd a{display:flex;align-items:center;gap:10px;padding:14px 16px;border-radius:10px;
    border:1.5px solid var(--pill-border);background:#fff;color:var(--red-dark);
    font-size:15px;font-weight:600;text-decoration:none;line-height:1.35;}
  .jd a + a{margin-top:8px;}
  .jd a:hover{background:var(--wash);}
  .jd a::after{content:'\\2197';margin-left:auto;font-weight:400;color:var(--accent);flex:0 0 auto;}
  .privacy{margin-top:34px;padding:16px;border-radius:10px;background:#fafafa;
    border:1px solid #ececec;font-size:13px;color:var(--accent);line-height:1.6;}
  .privacy strong{color:var(--ink);}
  .submit-btn{
    width:100%;padding:17px;border:none;border-radius:10px;background:var(--red);color:#fff;
    font-size:17px;font-weight:700;margin-top:26px;cursor:pointer;font-family:inherit;
  }
  .submit-btn:disabled{opacity:.4;}
  .status{margin-top:14px;font-size:14px;text-align:center;min-height:20px;line-height:1.5;}
  .status.error{color:var(--red-dark);font-weight:600;}
  .done-screen{display:none;text-align:center;padding:50px 16px;}
  .done-screen.show{display:block;}
  .done-screen img{height:110px;width:auto;margin-bottom:22px;}
  .done-screen h2{font-size:24px;margin:0 0 10px;color:var(--red);border:none;padding:0;
    text-transform:none;letter-spacing:0;}
  .done-screen p{font-size:15px;color:var(--accent);line-height:1.6;margin:0 auto;max-width:400px;}
  .done-screen .ref{margin-top:20px;font-size:14px;color:var(--ink);}
  .missing{outline:2px solid var(--red-dark);outline-offset:4px;border-radius:12px;}
"""

# ---------------------------------------------------------------- shared js --

JS_TEMPLATE = """
(function(){
  var APPS_SCRIPT_URL = %(url)s;
  var FORM_KEY   = %(form_key)s;
  var REQUIRED   = %(required)s;
  var PILL_KEYS  = %(pill_keys)s;
  var FIELD_KEYS = %(field_keys)s;
  var CHECK_KEYS = %(check_keys)s;

  /* ---- device token ----
     Not identity. It exists only so a duplicate submission from the same
     device can be spotted. The application itself is identified by the
     server-side reference the script returns. */
  var TOKEN_KEY = 'oxie_rec_token';
  var token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    token = (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() :
      ('t-' + Date.now() + '-' + Math.random().toString(36).slice(2));
    localStorage.setItem(TOKEN_KEY, token);
  }

  /* ---- offline-safe queue ----
     An application is saved to this device before it is sent, so a dropped
     connection on a phone in a sports hall never loses somebody's answers. */
  var QUEUE_KEY = 'oxie_rec_queue_' + FORM_KEY;
  function getQueue(){ try { return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]'); } catch(e){ return []; } }
  function setQueue(q){ try { localStorage.setItem(QUEUE_KEY, JSON.stringify(q)); } catch(e){} }
  function enqueue(p){ var q = getQueue(); q.push(p); setQueue(q); }

  function sendOne(payload, cb){
    fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload)
    }).then(function(res){ return res.json(); })
      .then(function(j){ cb(!!j.ok, j); })
      .catch(function(){ cb(false, null); });
  }

  function flushQueue(){
    var q = getQueue();
    if (!q.length) return;
    var remaining = q.slice();
    var next = remaining.shift();
    sendOne(next, function(ok, j){
      if (ok) {
        setQueue(remaining);
        if (j && j.ref) {
          var refEl = document.getElementById('refLine');
          if (refEl && !refEl.textContent) {
            refEl.textContent = 'Your reference: ' + j.ref;
          }
        }
        flushQueue();
      }
    });
  }

  flushQueue();
  window.addEventListener('online', flushQueue);
  setInterval(flushQueue, 15000);

  /* ---- pill questions ---- */
  var answers = {};
  document.querySelectorAll('.q[data-q]').forEach(function(qEl){
    var key = qEl.getAttribute('data-q');
    qEl.querySelectorAll('.opt').forEach(function(opt){
      opt.addEventListener('click', function(){
        qEl.querySelectorAll('.opt').forEach(function(o){ o.classList.remove('selected'); });
        opt.classList.add('selected');
        answers[key] = opt.getAttribute('data-val');
        qEl.classList.remove('missing');
        applyConditionals();
      });
    });
  });

  /* ---- conditional blocks ---- */
  function applyConditionals(){
    document.querySelectorAll('[data-show-when]').forEach(function(block){
      var rule = block.getAttribute('data-show-when').split('=');
      var on = answers[rule[0]] === rule[1];
      block.classList.toggle('show', on);
    });
  }
  applyConditionals();

  function isVisible(el){
    if (!el) return false;
    var block = el.closest('[data-show-when]');
    return !block || block.classList.contains('show');
  }

  function readField(key){
    var el = document.getElementById(key);
    if (!el) return '';
    if (!isVisible(el)) return '';
    return (el.value || '').trim();
  }

  /* ---- submit ---- */
  var statusEl = document.getElementById('statusMsg');
  var submitBtn = document.getElementById('submitBtn');

  submitBtn.addEventListener('click', function(){
    document.querySelectorAll('.missing').forEach(function(el){ el.classList.remove('missing'); });

    var missing = [];

    REQUIRED.forEach(function(key){
      var pillEl = document.querySelector('.q[data-q="' + key + '"]');
      if (pillEl) {
        if (!isVisible(pillEl)) return;
        if (!answers[key]) { pillEl.classList.add('missing'); missing.push(key); }
        return;
      }
      var el = document.getElementById(key);
      if (!el) return;
      if (!isVisible(el)) return;
      var wrap = el.closest('.q') || el.closest('.row') || el;
      if (el.type === 'checkbox') {
        if (!el.checked) { (el.closest('.q') || el).classList.add('missing'); missing.push(key); }
      } else if (!(el.value || '').trim()) {
        wrap.classList.add('missing'); missing.push(key);
      }
    });

    var emailEl = document.getElementById('email');
    if (emailEl && isVisible(emailEl) && emailEl.value.trim() && !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(emailEl.value.trim())) {
      (emailEl.closest('.q') || emailEl).classList.add('missing');
      if (missing.indexOf('email') === -1) missing.push('email');
    }

    if (missing.length) {
      statusEl.textContent = missing.length === 1
        ? 'One thing still to fill in — it is highlighted above.'
        : missing.length + ' things still to fill in — they are highlighted above.';
      statusEl.className = 'status error';
      var first = document.querySelector('.missing');
      if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    submitBtn.disabled = true;

    var payload = { form: FORM_KEY, token: token };
    PILL_KEYS.forEach(function(k){
      var pillEl = document.querySelector('.q[data-q="' + k + '"]');
      payload[k] = isVisible(pillEl) ? (answers[k] || '') : '';
    });
    FIELD_KEYS.forEach(function(k){ payload[k] = readField(k); });
    CHECK_KEYS.forEach(function(k){
      var el = document.getElementById(k);
      payload[k] = !!(el && isVisible(el) && el.checked);
    });

    enqueue(payload);

    document.getElementById('formScreen').style.display = 'none';
    document.getElementById('doneScreen').classList.add('show');
    window.scrollTo(0, 0);

    flushQueue();
  });
})();
"""

# ------------------------------------------------------------------ render --


def esc(t):
    return html.escape(str(t), quote=True)


def render_field(f):
    """Render one field. Returns HTML."""
    t = f["type"]

    if t == "heading":
        out = '  <h2>%s</h2>\n' % esc(f["label"])
        if f.get("note"):
            out += '  <p class="section-note">%s</p>\n' % f["note"]
        return out

    if t == "conditional_open":
        return '  <div class="conditional" data-show-when="%s">\n' % esc(f["when"])

    if t == "conditional_close":
        return "  </div>\n"

    if t == "pills":
        cols = f.get("cols", 4)
        opts = "".join(
            '\n        <div class="opt" data-val="%s">%s</div>' % (esc(o), esc(o))
            for o in f["options"]
        )
        out = '  <div class="q" data-q="%s">\n' % esc(f["key"])
        out += '    <p class="q-text">%s%s</p>\n' % (
            f["label"],
            ' <span class="req">*</span>' if f.get("required") else "",
        )
        if f.get("hint"):
            out += '    <p class="q-hint">%s</p>\n' % f["hint"]
        out += '    <div class="options c%d">%s\n    </div>\n' % (cols, opts)
        out += "  </div>\n"
        return out

    if t == "checkbox":
        out = '  <div class="q">\n'
        out += '    <label class="consent">\n'
        out += '      <input type="checkbox" id="%s">\n' % esc(f["key"])
        out += "      <span>%s%s</span>\n" % (
            f["label"],
            ' <span class="req">*</span>' if f.get("required") else "",
        )
        out += "    </label>\n  </div>\n"
        return out

    if t == "row":
        out = '  <div class="q">\n'
        if f.get("label"):
            out += '    <p class="q-text">%s%s</p>\n' % (
                f["label"],
                ' <span class="req">*</span>' if f.get("required") else "",
            )
        if f.get("hint"):
            out += '    <p class="q-hint">%s</p>\n' % f["hint"]
        out += '    <div class="row">\n'
        for sub in f["fields"]:
            out += "      <div>\n"
            out += '        <label for="%s">%s</label>\n' % (esc(sub["key"]), sub["label"])
            out += '        <input type="%s" id="%s" maxlength="%d"%s>\n' % (
                sub.get("input", "text"),
                esc(sub["key"]),
                sub.get("maxlength", 80),
                ' placeholder="%s"' % esc(sub["placeholder"]) if sub.get("placeholder") else "",
            )
            out += "      </div>\n"
        out += "    </div>\n  </div>\n"
        return out

    # text / email / tel / date / textarea / select
    out = '  <div class="q">\n'
    out += '    <p class="q-text">%s%s</p>\n' % (
        f["label"],
        ' <span class="req">*</span>' if f.get("required") else "",
    )
    if f.get("hint"):
        out += '    <p class="q-hint">%s</p>\n' % f["hint"]

    if t == "textarea":
        out += '    <textarea id="%s" maxlength="%d"%s></textarea>\n' % (
            esc(f["key"]),
            f.get("maxlength", 900),
            ' placeholder="%s"' % esc(f["placeholder"]) if f.get("placeholder") else "",
        )
    elif t == "select":
        opts = '\n      <option value="" selected disabled>%s</option>' % esc(
            f.get("placeholder", "Choose one")
        )
        opts += "".join(
            '\n      <option value="%s">%s</option>' % (esc(o), esc(o)) for o in f["options"]
        )
        out += '    <select id="%s">%s\n    </select>\n' % (esc(f["key"]), opts)
    else:
        out += '    <input type="%s" id="%s" maxlength="%d"%s>\n' % (
            t,
            esc(f["key"]),
            f.get("maxlength", 120),
            ' placeholder="%s"' % esc(f["placeholder"]) if f.get("placeholder") else "",
        )
    out += "  </div>\n"
    return out


def collect_keys(fields):
    pills, plain, checks, required = [], [], [], []
    for f in fields:
        t = f["type"]
        if t in ("heading", "conditional_open", "conditional_close"):
            continue
        if t == "row":
            for sub in f["fields"]:
                plain.append(sub["key"])
                if sub.get("required") or f.get("required"):
                    required.append(sub["key"])
            continue
        if t == "pills":
            pills.append(f["key"])
        elif t == "checkbox":
            checks.append(f["key"])
        else:
            plain.append(f["key"])
        if f.get("required"):
            required.append(f["key"])
    return pills, plain, checks, required


PRIVACY_ADULT = """
    <strong>What happens to what you write here.</strong>
    Your application goes to a private OXIE recruitment sheet that only the
    hiring team can open. We use it to shortlist, contact you, and nothing
    else. We do not ask for information about your ethnicity, religion,
    health, or any criminal record on this form — if you are offered a role,
    DBS and safer-recruitment checks happen separately and properly.
    We hold applications for six months and then delete them, unless you join
    us. You can ask us to delete yours sooner: <a href="mailto:contact@oxie.org.uk"
    style="color:#c1013f">contact@oxie.org.uk</a>.
"""

PRIVACY_YAB = """
    <strong>What happens to what you write here.</strong>
    Only the OXIE team reads this, and we only use it to get back to you about
    the Youth Advisory Board. We do not share it with your school, and we do not
    put it anywhere public. If you are under 18 we will check in with your
    parent or carer before your first meeting. If you ever want us to delete
    what you sent, just say — <a href="mailto:contact@oxie.org.uk"
    style="color:#c1013f">contact@oxie.org.uk</a>.
"""


def build(spec):
    fields = spec["fields"]
    pills, plain, checks, required = collect_keys(fields)

    body = "".join(render_field(f) for f in fields)

    js = JS_TEMPLATE % {
        "url": json.dumps(APPS_SCRIPT_URL),
        "form_key": json.dumps(spec["form_key"]),
        "required": json.dumps(required),
        "pill_keys": json.dumps(pills),
        "field_keys": json.dumps(plain),
        "check_keys": json.dumps(checks),
    }

    meta = ""
    if spec.get("meta"):
        meta = '  <div class="meta">\n' + "".join(
            "    <div>%s</div>\n" % line for line in spec["meta"]
        ) + "  </div>\n"

    # Job descriptions sit above the first question, so nobody starts filling
    # in a form for a role they have not read about. Opens in a new tab so a
    # part-completed application is never lost to a navigation.
    if spec.get("jd"):
        label = "Read the full role description" if len(spec["jd"]) == 1 \
            else "Read the full role descriptions"
        meta += '  <div class="jd">\n    <p class="jd-label">%s</p>\n' % label
        for item in spec["jd"]:
            meta += '    <a href="%s" target="_blank" rel="noopener">%s</a>\n' % (
                esc(item["url"]),
                esc(item["label"]),
            )
        meta += "  </div>\n"

    page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>%(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;600;700&display=swap" rel="stylesheet">
<style>%(css)s</style>
</head>
<body>

<div id="formScreen">
  <div class="logo-wrap"><img src="oxie-logo-black.png" alt="OXIE"></div>
  <h1>%(h1)s</h1>
  <p class="sub">%(sub)s</p>
%(meta)s%(body)s
  <div class="privacy">%(privacy)s</div>

  <button class="submit-btn" id="submitBtn">%(cta)s</button>
  <div class="status" id="statusMsg"></div>
</div>

<div class="done-screen" id="doneScreen">
  <img src="oxie-logo-black.png" alt="OXIE">
  <h2>%(done_h)s</h2>
  <p>%(done_p)s</p>
  <p class="ref" id="refLine"></p>
</div>

<script>%(js)s</script>
</body>
</html>
""" % {
        "title": esc(spec["title"]),
        "css": CSS,
        "h1": spec["h1"],
        "sub": spec["sub"],
        "meta": meta,
        "body": body,
        "privacy": spec.get("privacy", PRIVACY_ADULT),
        "cta": esc(spec.get("cta", "Send my application")),
        "done_h": spec["done_h"],
        "done_p": spec["done_p"],
        "js": js,
    }

    path = os.path.join(OUT_DIR, spec["filename"])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path, len(required)


# ------------------------------------------------------- reusable sections --


def about_you(include_phone=True):
    out = [
        {"type": "heading", "label": "About you"},
        {
            "type": "row",
            "label": "Your name",
            "required": True,
            "fields": [
                {"key": "firstName", "label": "First name", "maxlength": 50},
                {"key": "lastName", "label": "Last name", "maxlength": 50},
            ],
        },
        {
            "type": "email",
            "key": "email",
            "label": "Email",
            "required": True,
            "placeholder": "you@example.com",
        },
    ]
    if include_phone:
        out.append(
            {
                "type": "tel",
                "key": "phone",
                "label": "Phone",
                "required": True,
                "maxlength": 30,
                "placeholder": "07…",
            }
        )
    out.append(
        {
            "type": "text",
            "key": "townOrArea",
            "label": "Town or area you live in",
            "required": True,
            "hint": "Just the town or area — we do not need your full address at this stage.",
            "maxlength": 80,
        }
    )
    return out


def checks_section():
    return [
        {"type": "heading", "label": "Practical checks"},
        {
            "type": "pills",
            "key": "rightToWork",
            "label": "Do you have the right to work in the UK?",
            "required": True,
            "cols": 3,
            "options": ["Yes", "Not yet", "I would need sponsorship"],
        },
        {
            "type": "pills",
            "key": "drivingLicence",
            "label": "Do you drive?",
            "hint": "Useful for kit transport, not essential for most roles.",
            "cols": 3,
            "options": ["Yes, with a car", "Yes, no car", "No"],
        },
        {
            "type": "pills",
            "key": "dbsStatus",
            "label": "Do you currently hold an enhanced DBS certificate?",
            "required": True,
            "hint": "Status only. We are not asking you to disclose anything that is on it, and there is no wrong answer — we arrange DBS checks for people who do not have one.",
            "cols": 1,
            "options": [
                "Yes, and it is on the DBS Update Service",
                "Yes, but not on the Update Service",
                "No, not yet",
                "Not sure",
            ],
        },
        {
            "type": "checkbox",
            "key": "saferRecruitmentConsent",
            "label": "I understand this role is subject to OXIE's safer recruitment process, including an enhanced DBS check and references, and I am happy to go through it.",
            "required": True,
        },
    ]


def referees_section(two=True):
    out = [
        {
            "type": "heading",
            "label": "References",
            "note": "We will not contact anyone without telling you first.",
        },
        {
            "type": "row",
            "label": "Referee 1",
            "required": True,
            "fields": [
                {"key": "referee1Name", "label": "Name", "maxlength": 80},
                {
                    "key": "referee1Relationship",
                    "label": "How they know you",
                    "maxlength": 80,
                    "placeholder": "e.g. former manager",
                },
            ],
        },
        {
            "type": "email",
            "key": "referee1Email",
            "label": "Referee 1 email",
            "required": True,
            "maxlength": 120,
        },
    ]
    if two:
        out += [
            {
                "type": "row",
                "label": "Referee 2",
                "required": True,
                "fields": [
                    {"key": "referee2Name", "label": "Name", "maxlength": 80},
                    {
                        "key": "referee2Relationship",
                        "label": "How they know you",
                        "maxlength": 80,
                        "placeholder": "e.g. course tutor",
                    },
                ],
            },
            {
                "type": "email",
                "key": "referee2Email",
                "label": "Referee 2 email",
                "required": True,
                "maxlength": 120,
            },
        ]
    return out


def closing_section(adjustments_hint=None):
    return [
        {"type": "heading", "label": "Anything else"},
        {
            "type": "textarea",
            "key": "adjustments",
            "label": "Is there anything we can do to make the application or interview work better for you?",
            "hint": adjustments_hint
            or "Interview format, timing, access, or anything else. A person reads this — it is never used to score your application.",
            "maxlength": 600,
        },
        {
            "type": "select",
            "key": "heardAbout",
            "label": "How did you hear about this role?",
            "placeholder": "Choose one",
            "options": [
                "OXIE website",
                "Instagram",
                "LinkedIn",
                "Facebook",
                "Someone at OXIE told me",
                "A friend or colleague",
                "A school, college or university",
                "A jobs board",
                "At an event",
                "Somewhere else",
            ],
        },
        {
            "type": "textarea",
            "key": "freeText",
            "label": "Anything else you want us to know? (optional)",
            "maxlength": 800,
        },
    ]


AVAILABILITY_HEADING = {"type": "heading", "label": "Availability"}


def availability_section(hours_options, availability_hint, schedule=None):
    """`schedule` pins a published, non-negotiable commitment — a fixed training
    block, say — and asks the applicant to confirm it outright rather than
    leaving it to be discovered at interview."""
    out = [
        AVAILABILITY_HEADING,
        {
            "type": "pills",
            "key": "hoursPreference",
            "label": "What are you looking for?",
            "required": True,
            "cols": len(hours_options) if len(hours_options) <= 3 else 2,
            "options": hours_options,
        },
    ]
    if schedule:
        out.append(
            {
                "type": "pills",
                "key": "scheduleConfirmation",
                "label": schedule["label"],
                "hint": schedule.get("hint"),
                "required": True,
                "cols": 1,
                "options": schedule["options"],
            }
        )
    out += [
        {
            "type": "textarea",
            "key": "availability",
            "label": "Which days and times could you usually work?",
            "required": True,
            "hint": availability_hint,
            "maxlength": 500,
        },
        {
            "type": "text",
            "key": "earliestStart",
            "label": "Earliest date you could start",
            "required": True,
            "maxlength": 60,
            "placeholder": "e.g. immediately, or mid-October",
        },
    ]
    return out


# -------------------------------------------------------------------- specs --

SPECS = []

# 1 — Drone Football Coach ----------------------------------------------------
SPECS.append(
    {
        "filename": "drone-football-coach.html",
        "form_key": "df_coach",
        "title": "Drone Football Coach — OXIE application",
        "h1": "Drone Football Coach",
        "sub": "Head Coach, Assistant Coach and Junior Coach. One form — tell us which "
        "one you are applying for and we will take it from there.",
        "meta": [
            "<strong>Where:</strong> Oxford and Oxfordshire, at schools, community venues and events",
            "<strong>Coach training:</strong> Mondays 6:00–7:30pm, 14 September – 14 December 2026",
            "<strong>Hours:</strong> Sessional, with more hours available around bootcamps and competitions",
            "<strong>Who we are looking for:</strong> people who can hold a room of young people, "
            "learn the kit, and keep a session safe and fun. Drone experience is welcome but not required — "
            "we train coaches.",
        ],
        "jd": [
            {
                "label": "Head Coach",
                "url": "https://docs.google.com/document/d/1DYZ_dgNJhEoLhWX7spNF6kc-NSTl7kIsluPH912tkW4/preview?tab=t.0",
            },
            {
                "label": "Assistant Coach",
                "url": "https://docs.google.com/document/d/1YGCi_2R4eo4k_ahFNjJG5xvFCiAyW4koeRAdGc4mAUE/preview?tab=t.0",
            },
        ],
        "fields": about_you()
        + [
            {"type": "heading", "label": "The role"},
            {
                "type": "pills",
                "key": "roleLevel",
                "label": "Which coaching role are you applying for?",
                "required": True,
                "cols": 1,
                "options": [
                    "Head Coach — leads sessions, holds the plan, responsible for the group",
                    "Assistant Coach — supports the Head Coach, runs small groups",
                    "Junior Coach — a young person supporting sessions, with training and mentoring",
                ],
            },
            {
                "type": "textarea",
                "key": "experience",
                "label": "Tell us about your experience working with young people.",
                "required": True,
                "hint": "Paid, voluntary or informal all count — coaching, teaching, youth work, "
                "scouts, a club you help run. If you have not done this before, say what you have "
                "done that is close to it.",
                "maxlength": 1200,
            },
            {
                "type": "textarea",
                "key": "whyThisRole",
                "label": "Why Drone Football, and why now?",
                "required": True,
                "maxlength": 900,
            },
            {
                "type": "textarea",
                "key": "relevantSkills",
                "label": "Anything technical, sporting or coaching-related we should know?",
                "hint": "Drones, RC, esports, refereeing, first aid, coaching badges, STEM teaching — "
                "whatever is relevant. Not essential.",
                "maxlength": 700,
            },
            {
                "type": "text",
                "key": "portfolio",
                "label": "A link, if you have one (optional)",
                "hint": "LinkedIn, a coaching profile, a video of you running something.",
                "maxlength": 200,
                "placeholder": "https://",
            },
        ]
        + availability_section(
            ["A few hours a week", "Regular part-time", "As much as is going"],
            "Beyond the Monday training block. Bootcamps run in school holidays; "
            "term-time sessions are usually after school and at weekends.",
            schedule={
                "label": "Coach training runs <strong>Mondays, 6:00–7:30pm, "
                "from 14 September to 14 December 2026</strong>. Can you commit to that?",
                "hint": "It is the same block for every coaching level, and it is how you "
                "learn the kit. Be straight with us — we would rather know now.",
                "options": [
                    "Yes — I can make all of it",
                    "Yes — I would miss one or two",
                    "No — Monday evenings do not work for me",
                ],
            },
        )
        + checks_section()
        + referees_section()
        + closing_section(),
        "done_h": "Thanks — your application is in.",
        "done_p": "We read every application ourselves. You will hear from us either way, "
        "and we aim to come back to you within two weeks.",
    }
)

# 2 — Youth Corner Location Lead, Windrush ------------------------------------
SPECS.append(
    {
        "filename": "youth-corner-lead-windrush.html",
        "form_key": "yc_lead_windrush",
        "title": "Youth Corner Location Lead, Windrush — OXIE application",
        "h1": "Youth Corner Location Lead",
        "sub": "Windrush. You would be the person young people at this location know by "
        "name — running the space, holding the relationships, and keeping it somewhere "
        "they want to be.",
        "meta": [
            "<strong>Where:</strong> Windrush",
            "<strong>Reports to:</strong> Youth Corner COO",
            "<strong>Who we are looking for:</strong> someone steady and warm who can run a "
            "location day to day, work with the young people who use it, and keep records "
            "and safeguarding tight.",
        ],
        "fields": about_you()
        + [
            {"type": "heading", "label": "The role"},
            {
                "type": "textarea",
                "key": "experience",
                "label": "Tell us about your experience working with young people.",
                "required": True,
                "hint": "Youth work, community work, teaching, mentoring, sports, faith settings — "
                "paid or voluntary. Tell us the setting, the age group, and what you were "
                "responsible for.",
                "maxlength": 1200,
            },
            {
                "type": "textarea",
                "key": "whyThisRole",
                "label": "Why this role, and why Windrush?",
                "required": True,
                "hint": "If you know the area or the community, tell us.",
                "maxlength": 900,
            },
            {
                "type": "textarea",
                "key": "relevantSkills",
                "label": "What would you bring to running a space day to day?",
                "hint": "Anything from safeguarding training and first aid to knowing how to "
                "get a quiet young person talking.",
                "maxlength": 900,
            },
            {
                "type": "text",
                "key": "portfolio",
                "label": "A link, if you have one (optional)",
                "maxlength": 200,
                "placeholder": "https://",
            },
        ]
        + availability_section(
            ["Part-time", "Full-time", "Either"],
            "Youth Corner sessions run after school and at weekends. Tell us what you could commit to.",
        )
        + checks_section()
        + referees_section()
        + closing_section(),
        "done_h": "Thanks — your application is in.",
        "done_p": "We read every application ourselves. You will hear from us either way, "
        "and we aim to come back to you within two weeks.",
    }
)

# 3 — Social Media Marketing Lead ---------------------------------------------
SPECS.append(
    {
        "filename": "social-media-lead.html",
        "form_key": "social_lead",
        "title": "Social Media Marketing Lead — OXIE application",
        "h1": "Social Media Marketing Lead",
        "sub": "You would own how OXIE sounds and looks in public — across all six of our "
        "ventures, to young people, parents, schools, funders and partners at the same time.",
        "meta": [
            "<strong>Where:</strong> Oxford, with flexibility",
            "<strong>Who we are looking for:</strong> someone who can write, shoot and edit, "
            "hold a brand steady across very different audiences, and turn a session in a "
            "sports hall into something worth watching.",
        ],
        "fields": about_you()
        + [
            {"type": "heading", "label": "The role"},
            {
                "type": "textarea",
                "key": "experience",
                "label": "Tell us about the social media and marketing work you have done.",
                "required": True,
                "hint": "Accounts you have run, campaigns you have shipped, what actually moved. "
                "Numbers are welcome but a good story about one post beats a spreadsheet.",
                "maxlength": 1200,
            },
            {
                "type": "textarea",
                "key": "whyThisRole",
                "label": "Why OXIE?",
                "required": True,
                "hint": "We would rather hear what you think we are getting wrong than a list of compliments.",
                "maxlength": 900,
            },
            {
                "type": "textarea",
                "key": "relevantSkills",
                "label": "What can you do yourself, without needing anyone else?",
                "required": True,
                "hint": "Copy, design, photography, video, editing, paid social, email, "
                "analytics, community management — be honest about the gaps too.",
                "maxlength": 900,
            },
            {
                "type": "text",
                "key": "portfolio",
                "label": "Portfolio, showreel, or an account you have run",
                "required": True,
                "hint": "The single most useful thing on this form. A link to work beats any description of it.",
                "maxlength": 300,
                "placeholder": "https://",
            },
        ]
        + availability_section(
            ["Part-time", "Full-time", "Freelance / contract"],
            "Some evening and weekend work around events and sessions — tell us how that sits with you.",
        )
        + checks_section()
        + referees_section()
        + closing_section(),
        "done_h": "Thanks — your application is in.",
        "done_p": "We read every application ourselves, and we will look at your work. "
        "You will hear from us either way, and we aim to come back to you within two weeks.",
    }
)

# 4 — Critical Minds Programme Lead -------------------------------------------
SPECS.append(
    {
        "filename": "critical-minds-lead.html",
        "form_key": "cm_lead",
        "title": "Critical Minds Programme Lead — OXIE application",
        "h1": "Critical Minds Programme Lead",
        "sub": "Our AI literacy curriculum, delivered in schools. You would take it into "
        "classrooms, hold the relationships with teachers and MATs, and keep the quality high "
        "as it scales.",
        "meta": [
            "<strong>Where:</strong> Oxford and partner schools",
            "<strong>Reports to:</strong> Critical Minds COO",
            "<strong>Who we are looking for:</strong> someone who is credible in a staffroom "
            "and genuinely good in front of a class — with enough grip on AI to teach it honestly, "
            "and enough organisation to run a programme across several schools at once.",
        ],
        "fields": about_you()
        + [
            {"type": "heading", "label": "The role"},
            {
                "type": "textarea",
                "key": "experience",
                "label": "Tell us about your experience delivering programmes or teaching.",
                "required": True,
                "hint": "Classroom teaching, workshop facilitation, training, curriculum design, "
                "programme management. Tell us the age groups and the settings.",
                "maxlength": 1200,
            },
            {
                "type": "textarea",
                "key": "whyThisRole",
                "label": "Why Critical Minds?",
                "required": True,
                "hint": "What do you think young people actually need to understand about AI, "
                "and what do most people get wrong about teaching it?",
                "maxlength": 900,
            },
            {
                "type": "textarea",
                "key": "relevantSkills",
                "label": "What is your relationship with AI and technology?",
                "required": True,
                "hint": "You do not need to be an engineer. We need to know you can teach this "
                "subject accurately and without hype — tell us where your understanding comes from.",
                "maxlength": 900,
            },
            {
                "type": "pills",
                "key": "portfolio",
                "label": "Have you worked with schools or MATs before?",
                "required": True,
                "cols": 2,
                "options": [
                    "Yes, I have worked inside a school",
                    "Yes, as an external provider",
                    "Some contact, not sustained",
                    "Not yet",
                ],
            },
        ]
        + availability_section(
            ["Part-time", "Full-time", "Either"],
            "Delivery is mostly in the school day during term time. Tell us what you could commit to.",
        )
        + checks_section()
        + referees_section()
        + closing_section(),
        "done_h": "Thanks — your application is in.",
        "done_p": "We read every application ourselves. You will hear from us either way, "
        "and we aim to come back to you within two weeks.",
    }
)

# 5 — Youth Work Apprenticeship ------------------------------------------------
SPECS.append(
    {
        "filename": "youth-work-apprenticeship.html",
        "form_key": "apprenticeship",
        "title": "Youth Work Apprenticeship — OXIE application",
        "h1": "Youth Work Apprenticeship",
        "sub": "Three years, full-time, fully funded. You work with young people at OXIE and "
        "come out the other side with a BA (Hons) in Youth Work — studied online through the "
        "University of Rochester — and no student debt.",
        "meta": [
            "<strong>Length:</strong> 3 years, full-time",
            "<strong>Cost to you:</strong> none — the apprenticeship is fully funded",
            "<strong>You finish with:</strong> an online BA (Hons) in Youth Work, University of Rochester",
            "<strong>Open to:</strong> anyone aged 18–25",
            "<strong>Experience needed:</strong> none. We are looking for the person, not the CV.",
        ],
        "jd": [
            {
                "label": "Youth Work Apprenticeship",
                "url": "https://docs.google.com/document/d/1K2tfi8_qpIiTP4p7d0_y88f1KCDsjfh2yGc1CeovKTU/preview?tab=t.0",
            },
        ],
        "fields": about_you()
        + [
            {"type": "heading", "label": "Eligibility"},
            {
                "type": "checkbox",
                "key": "ageConfirmed",
                "label": "I am aged between 18 and 25.",
                "required": True,
            },
            {
                "type": "date",
                "key": "dateOfBirth",
                "label": "Date of birth",
                "required": True,
                "hint": "The funding for this apprenticeship is age-restricted, so we do have to ask.",
            },
            {"type": "heading", "label": "You and this work"},
            {
                "type": "textarea",
                "key": "whyYouthWork",
                "label": "Why do you want to work with young people?",
                "required": True,
                "hint": "There is no right answer here and we are not looking for a personal statement. "
                "Tell us honestly.",
                "maxlength": 1200,
            },
            {
                "type": "textarea",
                "key": "experienceWithYoungPeople",
                "label": "Have you spent time around young people before?",
                "required": True,
                "hint": "Paid, voluntary, or just informal — helping at a club, coaching a team, "
                "looking after younger siblings or cousins, running something at school. "
                "If the answer is no, say so. It will not count against you.",
                "maxlength": 1000,
            },
            {
                "type": "textarea",
                "key": "whatYouWantToChange",
                "label": "What is one thing you would change for young people where you live?",
                "required": True,
                "maxlength": 800,
            },
            {"type": "heading", "label": "The practical side"},
            {
                "type": "pills",
                "key": "fullTimeCommitment",
                "label": "This is full-time for three years, combining work and study. Can you commit to that?",
                "required": True,
                "cols": 3,
                "options": ["Yes", "Yes, with some flexibility needed", "I want to talk it through"],
            },
            {
                "type": "text",
                "key": "earliestStart",
                "label": "Earliest date you could start",
                "required": True,
                "maxlength": 60,
                "placeholder": "e.g. immediately, or September",
            },
            {
                "type": "pills",
                "key": "studyAccess",
                "label": "The degree is studied online. Do you have reliable internet and a device to study on?",
                "required": True,
                "hint": "If not, tell us — it is a problem we can usually solve, not a reason to say no.",
                "cols": 3,
                "options": ["Yes", "Sometimes", "Not at the moment"],
            },
            {
                "type": "pills",
                "key": "studyConfidence",
                "label": "How do you feel about going back to studying?",
                "required": True,
                "cols": 2,
                "options": [
                    "Confident — I like studying",
                    "Fine, with some support",
                    "Nervous but up for it",
                    "It is the bit that worries me",
                ],
            },
        ]
        + checks_section()
        + referees_section(two=False)
        + closing_section(
            adjustments_hint="Interview format, timing, access, or anything about how you learn. "
            "A person reads this — it is never used to score your application."
        ),
        "done_h": "Thanks — your application is in.",
        "done_p": "This one matters to us, so we read every application properly. "
        "You will hear from us either way, and we aim to come back to you within two weeks.",
    }
)

# 6 — Youth Advisory Board ----------------------------------------------------
SPECS.append(
    {
        "filename": "youth-advisory-board.html",
        "form_key": "yab_member",
        "title": "Youth Advisory Board — OXIE",
        "h1": "Join the Youth Advisory Board",
        "sub": "For 12 to 25 year olds. You help decide what OXIE actually does — what we build, "
        "who it is for, and when we have got it wrong. This form is short on purpose.",
        "cta": "Send it",
        "privacy": PRIVACY_YAB,
        "meta": [
            "<strong>Age:</strong> 12–25",
            "<strong>When:</strong> first Thursday of the month, 7:30–8:30pm",
            "<strong>Where:</strong> Charlbury Memorial Hall, or online on Google Meet",
            "<strong>Experience needed:</strong> none at all",
        ],
        "jd": [
            {
                "label": "What being on the board involves",
                "url": "https://docs.google.com/document/d/1jpCwpyfsgC0HlUQylgIow1ij-K515DzXEC6rcCew4xM/preview?tab=t.0",
            },
        ],
        "fields": [
            {"type": "heading", "label": "About you"},
            {
                "type": "row",
                "label": "Your name",
                "required": True,
                "fields": [
                    {"key": "firstName", "label": "First name", "maxlength": 50},
                    {"key": "lastName", "label": "Last name", "maxlength": 50},
                ],
            },
            {
                "type": "text",
                "key": "age",
                "label": "How old are you?",
                "required": True,
                "maxlength": 3,
                "placeholder": "e.g. 15",
            },
            {
                "type": "email",
                "key": "email",
                "label": "Your email",
                "required": True,
                "placeholder": "you@example.com",
            },
            {
                "type": "tel",
                "key": "phone",
                "label": "Your phone (optional)",
                "maxlength": 30,
            },
            {
                "type": "text",
                "key": "townOrArea",
                "label": "Where do you live?",
                "required": True,
                "hint": "Just the town or area — we do not need your address.",
                "maxlength": 80,
            },
            {
                "type": "text",
                "key": "schoolCollegeOrWork",
                "label": "School, college, uni or work (optional)",
                "maxlength": 120,
            },
            {
                "type": "pills",
                "key": "underEighteen",
                "label": "Are you under 18?",
                "required": True,
                "cols": 2,
                "options": ["Yes", "No"],
            },
            {"type": "conditional_open", "when": "underEighteen=Yes"},
            {
                "type": "row",
                "label": "A parent or carer we can check in with",
                "required": True,
                "hint": "We will let them know you have applied before your first meeting. That is all.",
                "fields": [
                    {"key": "parentCarerName", "label": "Their name", "maxlength": 80},
                ],
            },
            {
                "type": "email",
                "key": "parentCarerEmail",
                "label": "Their email",
                "required": True,
                "maxlength": 120,
            },
            {
                "type": "checkbox",
                "key": "parentCarerConsent",
                "label": "My parent or carer knows I am applying and is happy for us to contact them.",
                "required": True,
            },
            {"type": "conditional_close"},
            {"type": "heading", "label": "The bit we actually care about"},
            {
                "type": "textarea",
                "key": "whyJoin",
                "label": "Why do you want to be on the board?",
                "required": True,
                "hint": "A few sentences is plenty. Say it how you would say it out loud.",
                "maxlength": 800,
            },
            {
                "type": "textarea",
                "key": "whatWouldYouChange",
                "label": "What is one thing you would change for young people where you live?",
                "required": True,
                "maxlength": 800,
            },
            {
                "type": "textarea",
                "key": "thingsYoureInto",
                "label": "What are you into? (optional)",
                "hint": "Gaming, football, art, coding, music, drones, none of the above — "
                "we just like knowing who is in the room.",
                "maxlength": 500,
            },
            {"type": "heading", "label": "Practical stuff"},
            {
                "type": "pills",
                "key": "meetingAvailability",
                "label": "The board meets on the <strong>first Thursday of every month, "
                "7:30–8:30pm</strong> — in person at Charlbury Memorial Hall, or online. "
                "Can you make that?",
                "hint": "One hour a month. If you can only do some months, that is still a yes.",
                "required": True,
                "cols": 1,
                "options": [
                    "Yes — I would come in person at Charlbury",
                    "Yes — I would join online",
                    "Yes — either works for me",
                    "Most months, but not every one",
                    "No — Thursday evenings do not work for me",
                ],
            },
            {
                "type": "pills",
                "key": "beenOnSomethingLikeThis",
                "label": "Have you been part of something like this before?",
                "required": True,
                "hint": "School council, youth parliament, a committee — or nothing at all. "
                "Both answers are completely fine.",
                "cols": 2,
                "options": ["Yes", "No, this would be my first"],
            },
            {
                "type": "textarea",
                "key": "adjustments",
                "label": "Is there anything we should know to make this work for you? (optional)",
                "hint": "Getting to meetings, how meetings are run, anything that would make it "
                "easier for you to take part. A person reads this.",
                "maxlength": 600,
            },
            {
                "type": "textarea",
                "key": "freeText",
                "label": "Anything else? (optional)",
                "maxlength": 600,
            },
        ],
        "done_h": "Got it — thanks.",
        "done_p": "Someone from OXIE will email you about what happens next. "
        "If you are under 18, we will drop your parent or carer a line too.",
    }
)


if __name__ == "__main__":
    for spec in SPECS:
        path, n = build(spec)
        print("built %-40s (%d required fields)" % (os.path.basename(path), n))
