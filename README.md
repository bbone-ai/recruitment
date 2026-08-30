# OXIE Recruitment Forms

Six application forms, one Google Sheet, one tab each. Same architecture as the
Quality Measurement forms: static HTML pages on GitHub Pages POSTing JSON to a
single Google Apps Script web app bound to a spreadsheet.

Responses land in **`Recruitment Responses`** at
*My Drive > Second Brain > OXIE > OXIE (Accelerator) > Recruitment*.

| Page | Role | Sheet tab |
|---|---|---|
| `drone-football-coach.html` | Drone Football Coach — Head / Assistant / Junior | `Drone Football Coach` |
| `youth-corner-lead-windrush.html` | Youth Corner Location Lead, Windrush | `Youth Corner Lead - Windrush` |
| `social-media-lead.html` | Social Media Marketing Lead | `Social Media Lead` |
| `critical-minds-lead.html` | Critical Minds Programme Lead | `Critical Minds Lead` |
| `youth-work-apprenticeship.html` | Youth Work Apprenticeship (18–25) | `Youth Work Apprenticeship` |
| `youth-advisory-board.html` | Youth Advisory Board member (12–25) | `Youth Advisory Board` |

The coaching levels are a single form with a level chooser, so one URL covers
Head, Assistant and Junior Coach. The level lands in the `RoleLevel` column.

---

## Setup — do this once, in order

### 1. The spreadsheet

Use the existing **`Recruitment Responses`** sheet at
**My Drive > Second Brain > OXIE > OXIE (Accelerator) > Recruitment**.

Keep it separate from `OXIE_QM_Responses`. Different data, different retention,
different audience.

### 2. Add the script

In that sheet: **Extensions > Apps Script**. Delete whatever is in `Code.gs`
and paste in the contents of `Code.gs` from this repo. Save.

Then, from the function dropdown at the top, select **`setUpAllTabs`** and run
it once. It creates all six tabs with their headers, so the sheet looks finished
before the first application arrives. You will be asked to authorise the script
the first time — that is normal.

### 3. Deploy it

**Deploy > New deployment > Web app.**

- Execute as: **Me**
- Who has access: **Anyone**

"Anyone" is required — applicants are not signed into Google, and the script
only ever appends a row. It reads nothing back out.

Copy the **Web app URL**. It looks like
`https://script.google.com/macros/s/AKfyc…/exec`.

### 4. Put the URL in the forms

Open `build_forms.py` and replace:

```python
APPS_SCRIPT_URL = "REPLACE_WITH_YOUR_APPS_SCRIPT_EXEC_URL"
```

with your deployment URL, then run:

```bash
python3 build_forms.py
```

That regenerates all six pages with the URL baked in. (You can also find-and-
replace the same placeholder directly in the six HTML files, but the generator
is the source of truth — anything edited by hand in the HTML gets overwritten
next time it runs.)

### 5. Turn on GitHub Pages

**Settings > Pages > Source: Deploy from a branch > `main` / `(root)`.**

Your URLs will be:

```
https://bbone-ai.github.io/recruitment/drone-football-coach.html
https://bbone-ai.github.io/recruitment/youth-corner-lead-windrush.html
https://bbone-ai.github.io/recruitment/social-media-lead.html
https://bbone-ai.github.io/recruitment/critical-minds-lead.html
https://bbone-ai.github.io/recruitment/youth-work-apprenticeship.html
https://bbone-ai.github.io/recruitment/youth-advisory-board.html
```

Those are the six links to point the Elementor hub page at.

### 6. Test each one

Submit a real test application through every form and check the row lands in
the right tab. Delete the test rows afterwards. Do this before the links go
anywhere public — a form that silently drops applications is worse than no form.

You can also open the web app URL directly in a browser: it returns a small JSON
health check listing the spreadsheet name and its tabs, which is the fastest way
to confirm the script is bound to the right sheet.

---

## Data handling

This system deliberately collects **no** equality-monitoring data, **no** health
or disability data as a field, and **no** criminal-record detail.

- **DBS is a status only** — holds one / on the Update Service / not yet / not
  sure. No certificate number, no offence, no disclosure content. Actual DBS
  checks happen offline through safer recruitment.
- **EDI monitoring is not on these forms.** If you need monitoring data for
  funders later, it should be a separate, anonymous, unlinked form so it can
  never be tied back to a named applicant.
- **`Adjustments_HUMAN_ONLY`** is the one column that may contain health or
  disability information, because an applicant volunteered it to request a
  reasonable adjustment. It is named that way on purpose: **that column must
  never be exported, summarised, or passed to any AI tool, including Claude.**
  Exclude it from any copy of the sheet you share.
- **The Youth Advisory Board tab concerns under-18s.** Treat it as Amber under
  the OXIE data policy: strip names and use role descriptions ("the Year 9
  applicant") before using anything from it for drafting, planning or reporting.
- Every row gets a short reference (`DF-260830-141205`, `YAB-…`) so applicants
  can be discussed by reference rather than by name.

The script never scores, ranks, categorises or summarises an application.
Shortlisting is a human decision made outside the sheet.

---

## How the pages work

- **Standalone.** One HTML file each, CSS and JS inlined. The only external
  assets are `oxie-logo-black.png` and the Lato webfont.
- **Offline-safe.** An application is written to the applicant's own device
  before it is sent. If the network drops, the page retries every 15 seconds and
  again when the device comes back online. Nobody's answers are lost to a bad
  signal in a sports hall.
- **Append-only, server-timestamped.** The script ignores any timestamp the
  browser sends and stamps rows itself.
- **Validation happens in the page.** Required fields are highlighted and the
  page scrolls to the first one. Fields inside a hidden branch — the under-18
  parent/carer block on the YAB form — are neither required nor submitted while
  hidden.

## Changing a form

Edit the spec in `build_forms.py`, not the HTML. Then:

```bash
python3 build_forms.py     # regenerate the six pages
python3 verify.py          # check every field still matches Code.gs
node test_forms.mjs        # headless browser check: validation, submit, branches
```

If you add a field, add it to the matching header list **and** the matching
`append…` function in `Code.gs`, in the same position. `verify.py` will fail if
the two ever drift apart, which is the whole reason it exists — a mismatch
otherwise shows up as a silently blank column weeks later.

Adding a column to an existing tab in a sheet that already has rows means the
old rows will not have that data. Add the column to the sheet by hand in the
same position as the header list, so new rows line up.
