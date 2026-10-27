/* Local generated-reader integration checks. No dependency is shipped to the site. */
const fs = require('node:fs'), path = require('node:path'), http = require('node:http'), assert = require('node:assert/strict');
const {chromium} = require(process.env.LJ_PLAYWRIGHT_MODULE || 'playwright');
const [baselineSite, finalSite, output] = process.argv.slice(2).map(p => path.resolve(p));
const source = require('../../assets/data/deh-annotations/annotations.json');
const records = book => source.records.filter(row => row.book === book).sort((a, b) => a.chapter - b.chapter || a.sourceRow - b.sourceRow);
fs.mkdirSync(output, {recursive: true});
const report = {status: 'RUNNING', books: [], comparisons: [], checks: [], screenshots: [], errors: []};
async function serve(root) {
  const server = http.createServer((request, response) => {
    const url = new URL(request.url, 'http://localhost');
    let file = path.resolve(root, '.' + decodeURIComponent(url.pathname));
    if (!file.startsWith(root + path.sep)) {response.writeHead(403); return response.end();}
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file)) {response.writeHead(404); return response.end();}
    response.setHeader('Content-Type', ({'.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.xml': 'application/xml', '.otf': 'font/otf', '.svg': 'image/svg+xml'})[path.extname(file)] || 'application/octet-stream');
    response.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return {server, origin: `http://127.0.0.1:${server.address().port}`};
}
async function main() {
  const baseline = await serve(baselineSite), final = await serve(finalSite);
  const browser = await chromium.launch({headless: true, executablePath: process.env.LJ_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
  const page = await context.newPage(); page.on('pageerror', error => report.errors.push(error.message));
  async function open(origin, query) {
    await page.goto(`${origin}/deh/?${query}`, {waitUntil: 'domcontentloaded'});
    await page.waitForSelector('#latin tei-p[id^="latin-deh"]'); await page.waitForSelector('#english tei-p[id]');
    if (origin === final.origin) await page.waitForFunction(() => Number(document.querySelector('#annotations-list')?.dataset.dehReadingCount) > 0);
  }
  async function narrative() {
    return page.evaluate(() => Object.fromEntries(['latin', 'english', 'french'].map(id => {
      const pane = document.getElementById(id)?.cloneNode(true);
      pane?.querySelectorAll('.text-annotations').forEach(node => node.remove());
      return [id, pane?.textContent || ''];
    })));
  }
  async function shot(name) {
    await page.locator('#reader-annotations').screenshot({path: path.join(output, name), animations: 'disabled'});
    report.screenshots.push(name);
  }
  try {
    const seen = new Set();
    for (const book of [1, 2, 3, 4, 5]) {
      await open(final.origin, `book=${book}`);
      const expected = records(book), ids = await page.locator('.annotation-deh-record').evaluateAll(nodes => nodes.map(n => n.id));
      assert.deepEqual(ids, expected.map(row => row.presentationId));
      ids.forEach(id => {assert(!seen.has(id)); seen.add(id);});
      assert.equal(await page.locator('.manuscript-annotation').count(), expected.length);
      const chapterCounts = {};
      expected.forEach(row => chapterCounts[row.locationTargetId] = (chapterCounts[row.locationTargetId] || 0) + 1);
      const links = await page.locator('#latin .text-annotations').evaluateAll(nodes => nodes.map(n => ({parent: n.parentElement.id, text: n.textContent})));
      assert.equal(links.length, Object.keys(chapterCounts).length);
      for (const link of links) assert.equal(link.text, `${chapterCounts[link.parent]} ${chapterCounts[link.parent] === 1 ? 'annotation' : 'annotations'} for this chapter`);
      report.books.push({book, records: expected.length, chapterLinks: links.length, sourceOrderWithinChapters: true});
    }
    assert.equal(seen.size, 1917); report.checks.push('all 1917 records, including repeated source rows, rendered once across the five books');
    for (const query of ['book=1&chapter=0', 'book=1&chapter=26', 'book=1&chapter=26&unit=3', 'book=3&chapter=4', 'book=5&chapter=53']) {
      await open(baseline.origin, query); const before = await narrative();
      await open(final.origin, query); assert.deepEqual(await narrative(), before, query);
      report.comparisons.push({query, LatinEnglishFrenchUnchanged: true});
    }
    let frenchSource;
    for (const origin of [baseline.origin, final.origin]) {
      await open(origin, 'book=1&chapter=26&unit=3');
      await page.locator('#display-settings-header button').click();
      await page.locator('#french-pane-select').check();
      await page.waitForSelector('#french[data-millet-ready="1"] .millet-line');
      const exactSource = await page.locator('#millet-source').textContent();
      assert(exactSource.length > 100, 'Actual French source must be displayed');
      if (origin === baseline.origin) frenchSource = exactSource;
      else assert.equal(exactSource, frenchSource);
      await page.locator('#french-pane-select').uncheck();
    }
    report.checks.push('the enabled French Millet pane displays identical actual source text in the existing and updated readers');
    await open(final.origin, 'book=1&chapter=0');
    assert.equal(await page.locator('.annotation-deh-record').count(), 1);
    assert((await page.locator('.annotation-transcription').innerText()).includes('de Iosepho'));
    assert((await page.locator('.annotation-passage').getAttribute('href')).includes('chapter=0'));
    assert.equal(await page.locator('#latin tei-p[id^="latin-deh"]').count(), 3);
    report.checks.push('the 0.1 source record is attached to the whole three-paragraph prologue');
    await open(final.origin, 'book=1&chapter=26&unit=3');
    assert.equal(await page.locator('.annotation-deh-record').count(), 5);
    assert((await page.locator('.annotation-passage').first().getAttribute('href')).includes('chapter=26'));
    assert(!(await page.locator('.annotation-passage').first().getAttribute('href')).includes('&unit='));
    assert((await page.locator('#latin .text-annotations').innerText()).includes('for this chapter'));
    await page.locator('#latin .text-annotations').click();
    assert.equal(await page.locator('#annotations-header button').getAttribute('aria-expanded'), 'true');
    await page.locator('.annotation-passage').first().click();
    await page.waitForSelector('#latin-deh1-chapter26.annotation-target');
    assert.equal(new URL(page.url()).searchParams.get('unit'), null);
    assert.equal(await page.locator('.annotation-deh-record').count(), 5);
    const settingsClosed = !await page.locator('#highlight-annotations').isVisible();
    if (settingsClosed) await page.locator('#display-settings-header button').click();
    await page.locator('#highlight-annotations').check();
    assert(await page.locator('#latin-deh1-chapter26').evaluate(node => node.classList.contains('highlight')));
    if (settingsClosed) await page.locator('#display-settings-header button').click();
    report.checks.push('subsection views retain chapter citations; both navigation directions and whole-chapter highlighting work');
    if (await page.locator('#annotations-header button').getAttribute('aria-expanded') !== 'true') await page.locator('#annotations-header button').click();
    assert((await page.locator('.annotation-transcription').first().innerText()).includes('Galileę'));
    assert((await page.locator('.annotation-meta').first().innerText()).includes('p. 33'));
    await shot('deh-chapter26-light.png');
    await page.locator('.annotation-about summary').click();
    const font = await page.locator('.annotation-about').evaluate(node => ({font: getComputedStyle(node).fontFamily,
      intro: getComputedStyle(node.querySelector('p')).fontSize, key: getComputedStyle(node.querySelector('.annotation-notation-key p')).fontSize}));
    assert(font.font.includes('Coelacanth')); assert.equal(font.intro, '16px'); assert.equal(font.key, '14px');
    await shot('deh-annotation-key.png');
    await page.locator('.annotation-about summary').click();
    await page.locator('#light-toggle').click();
    assert.equal(await page.locator('#light-toggle').getAttribute('aria-pressed'), 'true');
    await shot('deh-chapter26-dark.png');
    await page.setViewportSize({width: 390, height: 844});
    assert(await page.locator('#reader-annotations').evaluate(node => node.scrollWidth <= node.clientWidth + 1));
    await shot('deh-chapter26-mobile.png');
    await page.setViewportSize({width: 1440, height: 1000});
    await open(final.origin, 'book=1&chapter=1');
    await page.locator('#annotations-header button').click();
    const partial = page.locator('#ms-annotation-deh-csv-20261027-row-3');
    assert((await partial.innerText()).includes('[untranscribed text]'));
    await partial.locator('summary').click(); assert((await partial.locator('pre').innerText()).includes('[*]'));
    await partial.locator('summary').press('Enter');
    assert.equal(await partial.locator('details').getAttribute('open'), null);
    await shot('deh-partial-source.png');
    report.checks.push('confirmed e caudata, original notation, St. Gall page references, keyboard details, typography and mobile layout verified');
    const failurePage = await context.newPage();
    await failurePage.route('**/data/deh-annotations/annotations.json', route => route.fulfill({status: 503, body: ''}));
    await failurePage.goto(final.origin + '/deh/?book=1&chapter=26');
    await failurePage.locator('#annotations-list [role="status"]').waitFor({state: 'attached'});
    assert(!(await failurePage.locator('#reader-annotations').evaluate(node => node.hidden)));
    await failurePage.locator('#annotations-header button').click();
    await failurePage.locator('#annotations-list [role="status"]').waitFor({state: 'visible'});
    assert((await failurePage.locator('#annotations-list').innerText()).includes('could not be loaded') || (await failurePage.locator('#annotations-list').textContent()).includes('could not be loaded'));
    await failurePage.close(); report.checks.push('a failed annotation request is visible instead of silently showing an empty apparatus');
    assert.deepEqual(report.errors, []); report.status = 'PASS';
  } finally {
    fs.writeFileSync(path.join(output, 'deh-browser-qa.json'), JSON.stringify(report, null, 2) + '\n');
    await browser.close(); baseline.server.close(); final.server.close();
  }
}
main().catch(error => {console.error(error); process.exitCode = 1;});
