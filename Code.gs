/**
 * OXIE Recruitment — application intake for six positions.
 *
 * Bind this script to the Google Sheet "OXIE_Recruitment_Responses"
 * (Extensions > Apps Script). One deployment serves all six forms.
 * Each form POSTs { form: '<key>', ...fields }.
 *
 * Forms and their tabs:
 *   df_coach          -> "Drone Football Coach"        (Head / Assistant / Junior via RoleLevel)
 *   yc_lead_windrush  -> "Youth Corner Lead - Windrush"
 *   social_lead       -> "Social Media Lead"
 *   cm_lead           -> "Critical Minds Lead"
 *   apprenticeship    -> "Youth Work Apprenticeship"
 *   yab_member        -> "Youth Advisory Board"
 *
 * Design rules baked in on purpose — do not "simplify" these away:
 *   - Append-only. No update, no delete, no overwrite of existing rows.
 *   - Server-side timestamp only. Client-sent timestamps are ignored.
 *   - No equality-monitoring data, no health data, no criminal-record detail is
 *     collected anywhere in this system. DBS is captured as a status only
 *     (holds one / on the update service / not yet) — never an offence, never a
 *     disclosure, never a certificate number. This is a deliberate data-
 *     minimisation choice: EDI monitoring and actual DBS disclosure happen
 *     offline, outside this sheet.
 *   - The "Adjustments_HUMAN_ONLY" column may contain health or disability
 *     information that an applicant volunteered in order to request a
 *     reasonable adjustment. It is stored verbatim for a human recruiter and
 *     must never be exported, summarised, or passed to any AI system. It is
 *     named the way it is so that rule is visible in the sheet itself.
 *   - The Youth Advisory Board route is for 12-25s, so its rows can concern a
 *     child. It collects the minimum needed to contact an applicant and, where
 *     the applicant is under 18, a parent or carer. Nothing more.
 *   - Free text is stored verbatim and flagged for a human if non-empty. The
 *     script never summarises, categorises, scores, or ranks an application.
 *     Shortlisting is a human decision made outside this sheet.
 */

var TABS = {
  df_coach: 'Drone Football Coach',
  yc_lead_windrush: 'Youth Corner Lead - Windrush',
  social_lead: 'Social Media Lead',
  cm_lead: 'Critical Minds Lead',
  apprenticeship: 'Youth Work Apprenticeship',
  yab_member: 'Youth Advisory Board'
};

// Shared shape for the four staff / lead roles.
var ROLE_HEADERS = [
  'Timestamp', 'Ref', 'Role', 'RoleLevel',
  'FirstName', 'LastName', 'Email', 'Phone', 'TownOrArea',
  'Experience', 'WhyThisRole', 'RelevantSkills',
  'Availability', 'EarliestStart', 'HoursPreference', 'ScheduleConfirmation',
  'RightToWork', 'DrivingLicence',
  'DBSStatus', 'SaferRecruitmentConsent',
  'Referee1Name', 'Referee1Relationship', 'Referee1Email',
  'Referee2Name', 'Referee2Relationship', 'Referee2Email',
  'PortfolioOrLink', 'HeardAbout',
  'Adjustments_HUMAN_ONLY', 'FreeText', 'FlaggedForReview'
];

// Apprenticeship: 18-25, no prior experience required, so the emphasis moves
// from track record to motivation and readiness to study.
var APPRENTICE_HEADERS = [
  'Timestamp', 'Ref', 'Role',
  'FirstName', 'LastName', 'Email', 'Phone', 'TownOrArea',
  'AgeConfirmed1825', 'DateOfBirth',
  'WhyYouthWork', 'ExperienceWithYoungPeople', 'WhatYouWantToChange',
  'FullTimeCommitment', 'EarliestStart',
  'StudyAccess', 'StudyConfidence',
  'RightToWork', 'DrivingLicence',
  'DBSStatus', 'SaferRecruitmentConsent',
  'Referee1Name', 'Referee1Relationship', 'Referee1Email',
  'HeardAbout',
  'Adjustments_HUMAN_ONLY', 'FreeText', 'FlaggedForReview'
];

// Youth Advisory Board: 12-25. Deliberately short and low-barrier.
// No DBS, no right to work, no referees, no CV.
var YAB_HEADERS = [
  'Timestamp', 'Ref', 'Role',
  'FirstName', 'LastName', 'Age', 'Email', 'Phone',
  'TownOrArea', 'SchoolCollegeOrWork',
  'UnderEighteen', 'ParentCarerName', 'ParentCarerEmail', 'ParentCarerConsent',
  'WhyJoin', 'WhatWouldYouChange', 'ThingsYoureInto',
  'MeetingAvailability', 'BeenOnSomethingLikeThis',
  'Adjustments_HUMAN_ONLY', 'FreeText', 'FlaggedForReview'
];

var HEADERS_BY_FORM = {
  df_coach: ROLE_HEADERS,
  yc_lead_windrush: ROLE_HEADERS,
  social_lead: ROLE_HEADERS,
  cm_lead: ROLE_HEADERS,
  apprenticeship: APPRENTICE_HEADERS,
  yab_member: YAB_HEADERS
};

var ROLE_LABELS = {
  df_coach: 'Drone Football Coach',
  yc_lead_windrush: 'Youth Corner Location Lead - Windrush',
  social_lead: 'Social Media Marketing Lead',
  cm_lead: 'Critical Minds Programme Lead',
  apprenticeship: 'Youth Work Apprenticeship',
  yab_member: 'Youth Advisory Board Member'
};

function doGet(e) {
  var health = { ok: true, status: 'healthy', time: new Date().toISOString() };
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    health.spreadsheet = ss.getName();
    health.sheets = ss.getSheets().map(function (s) { return s.getName(); });
  } catch (err) {
    health.ok = false;
    health.error = String(err);
  }
  return json(health);
}

function doPost(e) {
  try {
    if (!e.postData || !e.postData.contents) {
      return json({ ok: false, error: 'No POST body received.' });
    }
    var data = JSON.parse(e.postData.contents);
    var form = data.form;

    if (!TABS[form]) {
      return json({
        ok: false,
        error: "Unknown form type: '" + form + "'. Expected one of: " +
          Object.keys(TABS).join(', ') + '.'
      });
    }

    if (form === 'yab_member') return json(appendYab(data));
    if (form === 'apprenticeship') return json(appendApprentice(data));
    return json(appendRoleApplication(form, data));

  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

/* ---------------------------------------------------------------- routes -- */

function appendRoleApplication(form, data) {
  var sheet = getOrCreateSheet(TABS[form], ROLE_HEADERS);

  var adjustments = s(data.adjustments);
  var freeText = s(data.freeText);
  var flagged = (adjustments.length > 0) || (freeText.length > 0);

  var ref = makeRef(form);

  sheet.appendRow([
    new Date(),                       // server-side timestamp, never the client's
    ref,
    ROLE_LABELS[form],
    s(data.roleLevel),                // only Drone Football sends this
    s(data.firstName), s(data.lastName), s(data.email), s(data.phone), s(data.townOrArea),
    s(data.experience), s(data.whyThisRole), s(data.relevantSkills),
    s(data.availability), s(data.earliestStart), s(data.hoursPreference),
    // Only sent by roles with a fixed, published schedule (currently Drone
    // Football's Monday training block). Blank for the rest, like RoleLevel.
    s(data.scheduleConfirmation),
    s(data.rightToWork), s(data.drivingLicence),
    s(data.dbsStatus),
    data.saferRecruitmentConsent ? 'Y' : 'N',
    s(data.referee1Name), s(data.referee1Relationship), s(data.referee1Email),
    s(data.referee2Name), s(data.referee2Relationship), s(data.referee2Email),
    s(data.portfolio), s(data.heardAbout),
    adjustments, freeText,
    flagged ? 'Y' : 'N'
  ]);

  return { ok: true, form: form, ref: ref };
}

function appendApprentice(data) {
  var sheet = getOrCreateSheet(TABS.apprenticeship, APPRENTICE_HEADERS);

  var adjustments = s(data.adjustments);
  var freeText = s(data.freeText);
  var flagged = (adjustments.length > 0) || (freeText.length > 0);

  var ref = makeRef('apprenticeship');

  sheet.appendRow([
    new Date(),
    ref,
    ROLE_LABELS.apprenticeship,
    s(data.firstName), s(data.lastName), s(data.email), s(data.phone), s(data.townOrArea),
    data.ageConfirmed ? 'Y' : 'N', s(data.dateOfBirth),
    s(data.whyYouthWork), s(data.experienceWithYoungPeople), s(data.whatYouWantToChange),
    s(data.fullTimeCommitment), s(data.earliestStart),
    s(data.studyAccess), s(data.studyConfidence),
    s(data.rightToWork), s(data.drivingLicence),
    s(data.dbsStatus),
    data.saferRecruitmentConsent ? 'Y' : 'N',
    s(data.referee1Name), s(data.referee1Relationship), s(data.referee1Email),
    s(data.heardAbout),
    adjustments, freeText,
    flagged ? 'Y' : 'N'
  ]);

  return { ok: true, form: 'apprenticeship', ref: ref };
}

function appendYab(data) {
  var sheet = getOrCreateSheet(TABS.yab_member, YAB_HEADERS);

  var adjustments = s(data.adjustments);
  var freeText = s(data.freeText);
  var flagged = (adjustments.length > 0) || (freeText.length > 0);

  var ref = makeRef('yab_member');

  sheet.appendRow([
    new Date(),
    ref,
    ROLE_LABELS.yab_member,
    s(data.firstName), s(data.lastName), s(data.age), s(data.email), s(data.phone),
    s(data.townOrArea), s(data.schoolCollegeOrWork),
    // Sent as the literal 'Yes'/'No' the applicant tapped, so compare it —
    // a bare truthiness test would read the string 'No' as true.
    (s(data.underEighteen) === 'Yes') ? 'Y' : 'N',
    s(data.parentCarerName), s(data.parentCarerEmail),
    data.parentCarerConsent ? 'Y' : 'N',
    s(data.whyJoin), s(data.whatWouldYouChange), s(data.thingsYoureInto),
    s(data.meetingAvailability), s(data.beenOnSomethingLikeThis),
    adjustments, freeText,
    flagged ? 'Y' : 'N'
  ]);

  return { ok: true, form: 'yab_member', ref: ref };
}

/* --------------------------------------------------------------- helpers -- */

function s(v) {
  return String(v === null || v === undefined ? '' : v).trim();
}

// Short human-quotable reference so an applicant can be discussed by ref
// rather than by name — useful for the YAB route in particular.
function makeRef(form) {
  var prefix = {
    df_coach: 'DF',
    yc_lead_windrush: 'YC',
    social_lead: 'SM',
    cm_lead: 'CM',
    apprenticeship: 'AP',
    yab_member: 'YAB'
  }[form] || 'OX';
  var d = new Date();
  var stamp = Utilities.formatDate(d, 'Europe/London', 'yyMMdd-HHmmss');
  return prefix + '-' + stamp;
}

function getOrCreateSheet(name, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.appendRow(headers);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  } else if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  }
  return sheet;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Run once by hand from the Apps Script editor to create all six tabs with
 * their headers up front, so the sheet looks finished before the first
 * application lands. Safe to re-run — it never touches an existing tab that
 * already has a header row.
 */
function setUpAllTabs() {
  Object.keys(TABS).forEach(function (form) {
    getOrCreateSheet(TABS[form], HEADERS_BY_FORM[form]);
  });
}
