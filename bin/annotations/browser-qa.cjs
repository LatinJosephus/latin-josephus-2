/* Actual generated-site regression checks. No browser dependency is added to the site.
   Set LJ_PLAYWRIGHT_MODULE to an installed Playwright package path if necessary.
   node bin/annotations/browser-qa.cjs BASELINE_SITE FINAL_SITE OUTPUT_DIRECTORY
*/
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const assert = require('node:assert/strict'), crypto = require('node:crypto');
const {chromium} = require(process.env.LJ_PLAYWRIGHT_MODULE || 'playwright');
const [baselineSite, finalSite, output] = process.argv.slice(2).map(p => path.resolve(p));
fs.mkdirSync(output, {recursive: true});
const report = {status: 'RUNNING', views: [], corpus: [], interactions: [], baselineErrors: [], finalErrors: [], screenshots: []};
const inventory = require('../../_docs/annotation-source-inventory.json');
function instrument(source, mode) {
  source = source.replace('  bookTitle.innerText = activeWork.title;',
    '  window.__annotationQA={state:()=>({...state}), canonical:()=>canonicalFullData, ready:false};\n  bookTitle.innerText = activeWork.title;');
  if (mode === 'final') source = source.replace('    else await parseAnnotations();', '    else await parseAnnotations();\n    window.__annotationQA.ready=true;');
  else source = source.replace('    else parseAnnotations();', '    else {try {parseAnnotations();} finally {window.__annotationQA.ready=true;}}');
  return source;
}
function serve(site, mode) {
  const server = http.createServer((req, res) => {
    let target = path.resolve(site, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
    if (!target.startsWith(site + path.sep)) {res.writeHead(403); return res.end();}
    if (fs.existsSync(target) && fs.statSync(target).isDirectory()) target = path.join(target, 'index.html');
    if (!fs.existsSync(target)) {res.writeHead(404); return res.end();}
    const ext = path.extname(target), types = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.xml': 'application/xml', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png'};
    let bytes = fs.readFileSync(target);
    if (target.endsWith('renderTei.js')) bytes = Buffer.from(instrument(bytes.toString(), mode));
    res.setHeader('Content-Type', types[ext] || 'application/octet-stream'); res.end(bytes);
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve({server, origin: `http://127.0.0.1:${server.address().port}`})));
}
const sha = text => crypto.createHash('sha256').update(text).digest('hex');
async function main() {
  const servers = {baseline: await serve(baselineSite, 'baseline'), final: await serve(finalSite, 'final')};
  const browser = await chromium.launch({headless: true, executablePath: process.env.LJ_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
  const page = await context.newPage(); let mode = 'final';
  page.on('pageerror', error => report[mode + 'Errors'].push({url: page.url(), error: error.message}));
  async function open(which, work, query) {
    mode = which;
    await page.goto(servers[which].origin + `/${work === 'bellum' ? 'bellum-judaicum' : work}/?${query}`, {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => window.__annotationQA?.ready, {timeout: 60000});
  }
  async function narrative() {
    return page.evaluate(() => Object.fromEntries(['latin', 'greek', 'english'].map(language => {
      const pane = document.querySelector('#' + language).cloneNode(true);
      pane.querySelectorAll('.text-annotations').forEach(n => n.remove());
      return [language, pane.textContent];
    })));
  }
  async function screenshot(name, selector) {
    const target = selector ? page.locator(selector) : page;
    await target.screenshot({path: path.join(output, name), animations: 'disabled'}); report.screenshots.push(name);
  }
  try {
    const views = [
      ['antiquities', 'book=1&unit=27'], ['antiquities', 'book=1&chapter=1'], ['antiquities', 'book=1&niese=28'],
      ['antiquities', 'book=preface'], ['antiquities', 'book=11&unit=321'], ['antiquities', 'book=20&unit=266'],
      ['bellum', 'book=1&unit=1'], ['bellum', 'book=1&chapter=1'], ['bellum', 'book=1&niese=32'],
      ['bellum', 'book=7&unit=454'], ['deh', 'book=1&chapter=26&unit=3'], ['deh', 'book=2&chapter=10&unit=5'],
      ['contra-apionem', 'book=1&unit=1']
    ];
    for (const [work, query] of views) {
      await open('baseline', work, query); const before = await narrative();
      await open('final', work, query); const after = await narrative();
      assert.deepEqual(after, before, `Narrative changed: ${work} ${query}`);
      report.views.push({work, query, unchanged: true, hashes: Object.fromEntries(Object.entries(after).map(([k, v]) => [k, sha(v)]))});
      console.log('Unchanged reader:', work, query);
    }
    // Every source record must appear exactly once in its source-book panel,
    // including unlocated records and the one folio-only record.
    for (const work of ['antiquities', 'bellum']) {
      for (let book = 1; book <= (work === 'antiquities' ? 20 : 7); book++) {
        await open('final', work, 'book=' + book);
        const actual = await page.evaluate(() => [...document.querySelectorAll('.annotation-source-record')].map(node => ({
          anchor: node.id, notation: node.querySelector('pre')?.textContent,
          parts: node.querySelectorAll('.manuscript-annotation').length
        })));
        const expected = inventory.records.filter(r => r.work === work && r.sourceBook === book);
        assert.equal(actual.length, expected.length, `${work} ${book}: source record count`);
        assert.deepEqual(actual.map(r => r.notation), expected.map(r => r.notation), `${work} ${book}: source order/notation`);
        assert.equal(new Set(actual.map(r => r.anchor)).size, actual.length, 'Duplicate display anchor');
        report.corpus.push({work, book, records: actual.length, parts: actual.reduce((n, r) => n + r.parts, 0)});
        console.log('Source records preserved:', work, book, actual.length);
      }
    }
    await open('final', 'antiquities', 'book=1&unit=27');
    assert((await page.locator('.manuscript-annotation h4').first().innerText()).includes('Niese §§27–33'));
    await page.locator('#annotations-header button').click();
    assert.equal(await page.locator('#annotations-header button').getAttribute('aria-expanded'), 'true');
    const summary = page.locator('.annotation-details summary').first(); await summary.focus(); await page.keyboard.press('Enter');
    assert.equal(await summary.evaluate(n => n.parentNode.open), true); await page.keyboard.press('Enter');
    report.interactions.push('native details keyboard open/close');
    await page.locator('.text-annotations').first().click();
    assert((await page.locator('#annotations-header button').getAttribute('aria-expanded')) === 'true');
    assert((await page.evaluate(() => document.activeElement.classList.contains('manuscript-annotation'))));
    report.interactions.push('text to annotation focuses stable source anchor and opens panel');
    const passage = page.locator('.annotation-passage').first();
    await passage.click(); await page.waitForFunction(() => document.querySelector('#latin .annotation-target'));
    assert.equal(await page.locator('#latin .annotation-target').first().getAttribute('id'), 'latin-book01-num27');
    report.interactions.push('annotation to whole alignment unit');
    await page.evaluate(() => document.querySelector('#collapse-settings')?.classList.add('show'));
    await page.locator('#highlight-annotations').check({force: true});
    assert(await page.locator('#latin .highlight').count());
    await page.locator('#highlight-annotations').uncheck({force: true});
    assert.equal(await page.locator('#latin .highlight').count(), 0);
    report.interactions.push('existing highlighting on/off');
    const permanent = page.url(); await page.reload({waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => window.__annotationQA?.ready);
    assert.equal(page.url(), permanent); assert(await page.locator('#latin .annotation-target').count());
    report.interactions.push('permanent passage link reload');
    // Screenshot sets exercise actual source examples in both works.
    for (const [name, work, query] of [
      ['antiquities-hands', 'antiquities', 'book=1&unit=27'],
      ['antiquities-multiple-folios', 'antiquities', 'book=1&unit=37'],
      ['antiquities-hand3', 'antiquities', 'book=1&unit=67'],
      ['antiquities-hand5', 'antiquities', 'book=1&unit=34'],
      ['antiquities-hand6', 'antiquities', 'book=2&unit=120'],
      ['antiquities-hand8', 'antiquities', 'book=3&unit=153'],
      ['bellum-hand8', 'bellum', 'book=7&unit=5'],
      ['bellum-untranscribable', 'bellum', 'book=1&unit=7'],
      ['bellum-symbolic', 'bellum', 'book=1&unit=9'],
      ['bellum-abbreviated', 'bellum', 'book=1&unit=31']
    ]) {
      await open('baseline', work, query);
      await page.evaluate(() => document.querySelector('#collapse-annotations').classList.add('show'));
      await screenshot(name + '-before.png', '#reader-annotations');
      await open('final', work, query);
      await page.locator('#annotations-header button').click();
      const hand = name.match(/-hand(\d)$/)?.[1];
      const focusSelector = hand ? '.annotation-hand' : name === 'bellum-abbreviated' ? '.annotation-status' : null;
      const focusText = hand ? `Hand ${hand}` : 'Transcription abbreviated';
      if (focusSelector) await page.locator(focusSelector).filter({hasText: focusText}).first().evaluate(node => node.closest('article').scrollIntoView({block: 'center'}));
      if (hand && Number(hand) > 3) {
        assert((await page.locator('.annotation-hand').allTextContents()).includes(`Hand ${hand}`));
        report.interactions.push(`${work} ${query}: confirmed Hand ${hand} label`);
      }
      if (name === 'antiquities-hand8') {
        const parts = await page.locator('[data-source-siglum="ColognyBodmer98"] .annotation-transcription').allTextContents();
        assert.deepEqual(parts, ['secumdum', 'de uestibus sacerdotum', 'tertium', 'yo']);
        report.interactions.push('Bodmer 98 Hand 8 annotation is separate from tertium in source order');
      }
      await screenshot(name + '-after.png', '#reader-annotations');
      if (name === 'antiquities-hands') {
        await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
        await screenshot(name + '-dark.png', '#reader-annotations');
        await page.setViewportSize({width: 390, height: 844});
        await screenshot(name + '-mobile.png');
        assert(await page.locator('#reader-annotations').evaluate(n => n.scrollWidth <= n.clientWidth + 1));
        await page.setViewportSize({width: 1440, height: 1000});
      }
    }
    await open('final', 'deh', 'book=1&chapter=26&unit=3');
    assert(!await page.locator('#reader-annotations').evaluate(n => n.hidden));
    assert.equal(await page.locator('.annotation-deh-record').count(), 5);
    assert(await page.locator('#deh-parallels').count() || await page.locator('[id*="parallels"]').count());
    report.interactions.push('DEH shows five chapter-level annotations with parallels controls present');
    assert.deepEqual(report.finalErrors, [], 'Final reader JavaScript errors');
    report.status = 'PASS';
  } finally {
    fs.writeFileSync(path.join(output, 'browser-qa.json'), JSON.stringify(report, null, 2) + '\n');
    await browser.close(); for (const {server} of Object.values(servers)) server.close();
  }
}
main().catch(error => {console.error(error); process.exitCode = 1;});
