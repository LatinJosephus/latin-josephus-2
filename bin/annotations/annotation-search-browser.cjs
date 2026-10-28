/* Generated-site integration checks for the shared annotation search. No browser dependency is shipped. */
const fs = require('node:fs'), path = require('node:path'), http = require('node:http'), assert = require('node:assert/strict');
const {chromium} = require(process.env.LJ_PLAYWRIGHT_MODULE || 'playwright');
const [site, output] = process.argv.slice(2).map(value => path.resolve(value));
fs.mkdirSync(output, {recursive: true});
const report = {status: 'RUNNING', checks: [], errors: []};
const server = http.createServer((request, response) => {
  let file = path.resolve(site, '.' + decodeURIComponent(new URL(request.url, 'http://localhost').pathname));
  if (!file.startsWith(site + path.sep)) {response.writeHead(403); return response.end();}
  try {
    if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    response.setHeader('Content-Type', ({'.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.xml': 'application/xml'})[path.extname(file)] || 'application/octet-stream');
    response.end(fs.readFileSync(file));
  } catch {response.writeHead(404); response.end();}
});
async function main() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({headless: true, executablePath: process.env.LJ_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 1100}, acceptDownloads: true});
    const page = await context.newPage(); page.on('pageerror', error => report.errors.push(error.message));
    async function ready() {await page.waitForFunction(() => document.querySelector('#results-region')?.getAttribute('aria-busy') === 'false');}
    async function visit(query, extra = '') {
      await page.goto(`${origin}/search/?content=annotations&q=${encodeURIComponent(query)}${extra}`); await ready();
      assert.equal(await page.locator('#error').isVisible(), false, await page.locator('#error').textContent());
    }
    await visit('david', '&work=antiquities');
    const bern = page.locator('.annotation-search-result').filter({hasText: 'david [uncertain text] dicit'});
    assert.equal(await bern.count(), 1);
    assert((await bern.textContent()).includes('Niese §§34–36'));
    assert((await bern.textContent()).includes('fol. 2v'));
    assert(!(await bern.textContent()).includes('Hand'));
    await bern.scrollIntoViewIfNeeded(); await page.screenshot({path: path.join(output, 'annotation-search-antiquities.png')});
    const popupPromise = page.waitForEvent('popup'); await bern.getByText('View annotation in reader').click();
    const reader = await popupPromise;
    await reader.waitForSelector('#ms-annotation-antiquities-1-latin-book01-num34-BernBBMs118-1-at-6');
    assert((await reader.locator('#ms-annotation-antiquities-1-latin-book01-num34-BernBBMs118-1-at-6').textContent()).includes('david'));
    await reader.close(); report.checks.push('Reviewed reading, verified range, manuscript folio and stable reader anchor');

    await visit('"nota NT"', '&work=antiquities&type=symbolic');
    assert(await page.locator('.annotation-search-result').count() > 0);
    assert((await page.locator('.annotation-search-result').first().textContent()).includes('Symbolic annotation: nota NT'));
    assert(await page.locator('.annotation-search-result mark').count() > 0);
    report.checks.push('Symbolic annotation descriptions, category filter and exact-phrase highlighting');

    await visit('"de Iosepho"', '&work=deh');
    const prologue = page.locator('.annotation-search-result').filter({hasText: 'Cherbourg-en-Cotentin'}).filter({hasText: 'Prologue'});
    assert.equal(await prologue.count(), 1);
    const href = await prologue.getByText('View annotation in reader').getAttribute('href');
    assert(href.includes('/deh/?book=1&chapter=0#ms-annotation-deh-csv-20261027-row-2-at-0'));
    assert((await prologue.textContent()).includes('Hand 2'));
    const chapterPopup = page.waitForEvent('popup'); await prologue.getByText('View annotation in reader').click();
    const chapter = await chapterPopup; await chapter.waitForSelector('#ms-annotation-deh-csv-20261027-row-2-at-0');
    await chapter.close(); report.checks.push('DEH whole-Prologue association and reader navigation');

    await visit('de', '&work=deh&book=deh:1');
    const total = Number((await page.locator('#status').textContent()).match(/[\d,]+/u)[0].replaceAll(',', ''));
    assert(total > 20); assert.equal(await page.locator('.annotation-search-result').count(), 20);
    await page.locator('#load-more').click(); assert.equal(await page.locator('.annotation-search-result').count(), 40);
    const downloadPromise = page.waitForEvent('download'); await page.locator('#download-results').click();
    const download = await downloadPromise; const csv = fs.readFileSync(await download.path(), 'utf8');
    assert.equal(csv.split('\r\n').filter(line => line.startsWith('"de",')).length, total);
    assert(csv.includes('"original_notation"')); assert(csv.includes('"reader_url"'));
    report.checks.push(`Pagination and CSV export of all ${total} matching notes, including unseen results`);
    await page.locator('#query').fill('Iudęorum'); await page.locator('#query').press('Enter'); await ready();
    assert(await page.locator('.annotation-search-result').count() > 0);
    assert(await page.locator('mark').filter({hasText: 'Iudęorum'}).count() > 0);
    await page.screenshot({path: path.join(output, 'annotation-search-deh.png')});
    const witness = await page.locator('#manuscript option').nth(1).getAttribute('value');
    await page.locator('#manuscript').selectOption(witness); await ready();
    assert(new URL(page.url()).searchParams.get('manuscript') === witness);
    await page.goBack(); await ready(); assert.equal(await page.locator('#manuscript').inputValue(), 'all');
    report.checks.push('Unicode e caudata, keyboard submission, manuscript filtering and saved-state Back navigation');

    await visit('', '&work=deh&type=untranscribable');
    assert((await page.locator('#status').textContent()).includes('21 matching annotations'));
    assert((await page.locator('.annotation-search-result').first().textContent()).includes('Cannot be transcribed'));
    await page.locator('#query').fill('('); await page.locator('#search-button').click(); await ready();
    assert(await page.locator('#error').isVisible()); assert(await page.locator('#download-results').isDisabled());
    assert.equal(await page.locator('.annotation-search-result').count(), 0);
    report.checks.push('Distinct untranscribable notes and clear malformed-query failure without stale results');

    await visit('Iud*', '&work=deh');
    await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
    await page.screenshot({path: path.join(output, 'annotation-search-dark.png')});
    await page.setViewportSize({width: 390, height: 844});
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.screenshot({path: path.join(output, 'annotation-search-mobile.png')});
    report.checks.push('Desktop, dark mode and 390px mobile without horizontal overflow');
    await page.setViewportSize({width: 1440, height: 1100});

    const retry = await context.newPage();
    let fail = true;
    await retry.route('**/annotations.*.bundle.json', route => fail ? route.fulfill({status: 503, body: 'Unavailable'}) : route.continue());
    await retry.goto(`${origin}/search/?content=annotations&q=Iosepho&work=deh`);
    await retry.waitForFunction(() => document.querySelector('#results-region').getAttribute('aria-busy') === 'false');
    assert(await retry.locator('#error').isVisible());
    fail = false; await retry.locator('#search-button').click();
    await retry.waitForFunction(() => document.querySelector('#results-region').getAttribute('aria-busy') === 'false');
    assert(!(await retry.locator('#error').isVisible())); assert(await retry.locator('.annotation-search-result').count() > 0);
    await retry.close(); report.checks.push('Missing index displays an error and can be retried successfully');

    const cached = await context.newPage();
    await cached.route('**/search/?*', route => {
      if (!route.request().isNavigationRequest()) return route.continue();
      const oldHTML = fs.readFileSync(path.join(site, 'search/index.html'), 'utf8')
        .replace(/<div class="content-option">[\s\S]*?<\/div>/u, '')
        .replace(/<div id="manuscript-control"[\s\S]*?<\/div>/u, '');
      return route.fulfill({contentType: 'text/html', body: oldHTML});
    });
    await cached.goto(`${origin}/search/?content=annotations&q=Iosepho&work=deh`);
    await cached.waitForFunction(() => document.querySelector('#results-region').getAttribute('aria-busy') === 'false');
    assert.equal(await cached.locator('#content').inputValue(), 'annotations');
    assert(await cached.locator('#manuscript').isVisible());
    assert(await cached.locator('.annotation-search-result').count() > 0);
    await cached.close(); report.checks.push('Older cached HTML receives the current annotation controls');

    await page.goto(`${origin}/search/?q=%22sacerdos%20ex%20Hierosolymis%22&work=bellum-latin-cardwell`); await ready();
    assert(await page.locator('#error').isHidden()); assert.equal(await page.locator('#content').inputValue(), 'texts');
    assert(await page.locator('#results .result-card').count() > 0);
    await page.locator('#view-concordance').click(); assert(await page.locator('#results article').count() > 0);
    report.checks.push('Existing main-text search, result links and concordance remain functional');
    assert.deepEqual(report.errors, []);
    report.status = 'PASS';
  } finally {await browser.close();}
}
main().catch(error => {report.status = 'FAIL'; report.errors.push(error.stack); process.exitCode = 1;}).finally(() => {
  server.close(); fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2)); console.log(JSON.stringify(report));
});
