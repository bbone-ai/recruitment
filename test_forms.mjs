/**
 * Headless behaviour test for the six recruitment forms.
 *
 * Checks the things that would only otherwise surface with a real applicant
 * halfway through: that validation blocks an empty submit, that a completed
 * form produces a payload with every declared key populated, and that the
 * Youth Advisory Board form's under-18 branch appears and disappears with the
 * parent/carer fields required only when it is showing.
 */

import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const HERE = path.dirname(fileURLToPath(import.meta.url));

const PAGES = [
  'drone-football-coach.html',
  'youth-corner-lead-windrush.html',
  'social-media-lead.html',
  'critical-minds-lead.html',
  'youth-work-apprenticeship.html',
  'youth-advisory-board.html',
];

const failures = [];
// The container ships a Chromium at a fixed path; the npm playwright version
// here expects a different build number, so point it at the real one.
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

async function newPage(file) {
  const page = await browser.newPage({ viewport: { width: 430, height: 932 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  // Never let a test hit the real Apps Script.
  await page.route('**/script.google.com/**', r => r.abort());
  await page.goto('file://' + path.join(HERE, file));
  return { page, errors };
}

// Fill every visible input, textarea, select and pill group on the page.
async function fillEverything(page, { underEighteen } = {}) {
  await page.evaluate((u) => {
    // Pills first — answering them is what reveals any conditional block, and
    // the inputs inside that block only exist to be filled once it is showing.
    document.querySelectorAll('.q[data-q]').forEach(q => {
      const block = q.closest('[data-show-when]');
      if (block && !block.classList.contains('show')) return;
      if (q.getAttribute('data-q') === 'underEighteen' && u !== undefined) {
        const want = [...q.querySelectorAll('.opt')].find(o => o.dataset.val === u);
        if (want) want.click();
        return;
      }
      const first = q.querySelector('.opt');
      if (first) first.click();
    });
    document.querySelectorAll('input, textarea, select').forEach(el => {
      const block = el.closest('[data-show-when]');
      if (block && !block.classList.contains('show')) return;
      if (el.type === 'checkbox') { el.checked = true; return; }
      if (el.tagName === 'SELECT') { el.selectedIndex = 1; return; }
      if (el.type === 'email') { el.value = 'test@example.com'; return; }
      if (el.type === 'date') { el.value = '2004-05-20'; return; }
      if (el.type === 'tel') { el.value = '07700900123'; return; }
      el.value = 'test value';
    });
  }, underEighteen);
}

for (const file of PAGES) {
  const { page, errors } = await newPage(file);

  // 1. Empty submit must be blocked and must highlight something.
  await page.click('#submitBtn');
  const blockedMsg = await page.textContent('#statusMsg');
  const highlighted = await page.locator('.missing').count();
  const doneShowing = await page.locator('#doneScreen.show').count();

  if (!blockedMsg || !/still to fill in/.test(blockedMsg)) {
    failures.push(`${file}: empty submit was not blocked (status: "${blockedMsg}")`);
  }
  if (highlighted === 0) failures.push(`${file}: empty submit highlighted nothing`);
  if (doneShowing !== 0) failures.push(`${file}: empty submit reached the done screen`);

  // 2. Fully completed submit must go through and queue a complete payload.
  await fillEverything(page, { underEighteen: 'Yes' });
  await page.click('#submitBtn');
  await page.waitForTimeout(150);

  const done = await page.locator('#doneScreen.show').count();
  if (done !== 1) {
    const msg = await page.textContent('#statusMsg');
    const stillMissing = await page.locator('.missing').evaluateAll(
      els => els.map(e => e.dataset.q || (e.querySelector('[id]') || {}).id || e.id).join(', ')
    );
    failures.push(`${file}: completed submit did not finish — "${msg}" (missing: ${stillMissing})`);
  }

  const payload = await page.evaluate(() => {
    const key = Object.keys(localStorage).find(k => k.startsWith('oxie_rec_queue_'));
    const q = JSON.parse(localStorage.getItem(key) || '[]');
    return q[q.length - 1] || null;
  });

  if (!payload) {
    failures.push(`${file}: nothing was queued after a completed submit`);
  } else {
    if (!payload.form) failures.push(`${file}: payload has no form key`);
    if (!payload.token) failures.push(`${file}: payload has no device token`);
    const blank = Object.entries(payload)
      .filter(([k, v]) => v === '' || v === false)
      .map(([k]) => k);
    if (blank.length) {
      failures.push(`${file}: fully-filled form still sent blank values for: ${blank.join(', ')}`);
    }
  }

  if (errors.length) failures.push(`${file}: JS errors — ${errors.join(' | ')}`);

  // 3. Screenshot the top of the form for review.
  const shotPage = (await newPage(file)).page;
  await shotPage.screenshot({
    path: path.join(HERE, '_shots', file.replace('.html', '.png')),
    fullPage: true,
  });
  await shotPage.close();
  await page.close();

  console.log(`checked ${file}`);
}

// 4. YAB-specific: the under-18 branch must toggle, and its fields must only
//    be required while it is showing.
{
  const { page } = await newPage('youth-advisory-board.html');

  const hiddenAtStart = await page.locator('[data-show-when].show').count();
  if (hiddenAtStart !== 0) failures.push('YAB: parent/carer block was visible before answering');

  await page.locator('.q[data-q="underEighteen"] .opt', { hasText: 'Yes' }).first().click();
  if (await page.locator('[data-show-when].show').count() !== 1) {
    failures.push('YAB: answering "Yes" to under 18 did not reveal the parent/carer block');
  }

  await page.locator('.q[data-q="underEighteen"] .opt', { hasText: 'No' }).first().click();
  if (await page.locator('[data-show-when].show').count() !== 0) {
    failures.push('YAB: answering "No" did not hide the parent/carer block');
  }

  // An over-18 applicant must be able to finish without parent/carer details.
  await fillEverything(page, { underEighteen: 'No' });
  await page.click('#submitBtn');
  await page.waitForTimeout(150);
  if (await page.locator('#doneScreen.show').count() !== 1) {
    failures.push('YAB: an over-18 applicant was blocked by hidden parent/carer fields');
  }
  const p = await page.evaluate(() => {
    const key = Object.keys(localStorage).find(k => k.startsWith('oxie_rec_queue_'));
    const q = JSON.parse(localStorage.getItem(key) || '[]');
    return q[q.length - 1];
  });
  if (p && (p.parentCarerName || p.parentCarerEmail || p.parentCarerConsent)) {
    failures.push('YAB: over-18 payload still carried parent/carer data');
  }
  if (p && p.underEighteen !== 'No') {
    failures.push(`YAB: underEighteen sent as ${JSON.stringify(p && p.underEighteen)}, expected "No"`);
  }
  await page.close();
  console.log('checked youth-advisory-board.html under-18 branch');
}

await browser.close();

console.log('');
if (failures.length) {
  console.log('FAILURES:');
  failures.forEach(f => console.log('  - ' + f));
  process.exit(1);
}
console.log('All six forms validate, submit, and queue a complete payload.');
console.log('YAB under-18 branch toggles correctly and stays out of over-18 submissions.');
