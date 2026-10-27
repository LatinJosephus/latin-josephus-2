/* Final actual-UI checks for search links, parallels and sparse annotation data. */
const fs = require('node:fs'), path = require('node:path'), http = require('node:http'), assert = require('node:assert/strict');
const {chromium} = require(process.env.LJ_PLAYWRIGHT_MODULE || 'playwright');
const site = path.resolve(process.argv[2]), output = path.resolve(process.argv[3]);
const results = {status: 'RUNNING', checks: [], errors: []};
async function main() {
  const server = http.createServer((request, response) => {
    let file = path.resolve(site, '.' + decodeURIComponent(new URL(request.url, 'http://localhost').pathname));
    if (!file.startsWith(site + path.sep)) {response.writeHead(403); return response.end();}
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file)) {response.writeHead(404); return response.end();}
    response.setHeader('Content-Type', ({'.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.css': 'text/css', '.json': 'application/json', '.xml': 'application/xml', '.svg': 'image/svg+xml'})[path.extname(file)] || 'application/octet-stream');
    response.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({headless: true, executablePath: process.env.LJ_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page = await browser.newPage(); page.on('pageerror', error => results.errors.push(error.message));
  try {
    await page.goto(origin + '/search/', {waitUntil: 'domcontentloaded'});
    await page.waitForSelector('#search-button:enabled');
    await page.locator('#query').fill('"sacerdos ex Hierosolymis"');
    await page.locator('#search-button').click();
    const link = page.locator('#results a[href*="/bellum-judaicum/"]').first(); await link.waitFor();
    const readerUrl = await link.getAttribute('href'), savedUrl = page.url();
    await page.reload({waitUntil: 'domcontentloaded'}); await link.waitFor();
    assert.equal(await link.getAttribute('href'), readerUrl); assert.equal(page.url(), savedUrl);
    results.checks.push('actual search query and saved URL return the same reader passage');
    await page.goto(new URL(readerUrl, origin).href, {waitUntil: 'domcontentloaded'});
    await page.waitForSelector('#latin tei-p');
    results.checks.push('search result opens the existing Bellum reader');
    await page.goto(origin + '/antiquities/?book=1&unit=72', {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => document.querySelector('#annotations-list')?.textContent.includes('No transcription recorded'));
    assert((await page.locator('.annotation-hand').allTextContents()).includes('Hand 2'));
    results.checks.push('hand-only source description retains Hand 2 with no invented transcription category');
    await page.goto(origin + '/antiquities/?book=1&unit=27', {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => document.querySelector('.annotation-description')?.textContent.includes('correction with a sign'));
    assert.equal(await page.locator('.annotation-transcription').first().innerText(), 'lucem');
    assert((await page.locator('.annotation-details pre').first().textContent()).includes('correction avec signe'));
    await page.locator('#annotations-header button').click();
    await page.locator('#reader-annotations').screenshot({path: path.join(path.dirname(output), '../screenshots/english-editorial-correction.png'), animations: 'disabled'});
    results.checks.push('English correction description preserves original French in scholarly details and the Latin lucem');
    await page.goto(origin + '/antiquities/?book=1&unit=37', {waitUntil: 'domcontentloaded'});
    await page.waitForSelector('.annotation-editorial-note', {state: 'attached'});
    assert((await page.locator('.annotation-editorial-note').allTextContents()).includes('(erased word?)'));
    assert((await page.locator('.annotation-transcription').allTextContents()).includes('de pacto ad * (erased word?)'));
    await page.locator('#annotations-header button').click();
    await page.locator('.annotation-editorial-note').first().evaluate(node => node.closest('article').scrollIntoView({block: 'center'}));
    await page.locator('#reader-annotations').screenshot({path: path.join(path.dirname(output), '../screenshots/english-editorial-mixed.png'), animations: 'disabled'});
    results.checks.push('English inline editorial comment leaves the surrounding Latin unchanged');
    await page.goto(origin + '/antiquities/?book=1&unit=34#ms-annotation-antiquities-1-latin-book01-num34-BernBBMs118-1', {waitUntil: 'domcontentloaded'});
    await page.waitForSelector('.annotation-category', {state: 'attached'});
    const bern = page.locator('#ms-annotation-antiquities-1-latin-book01-num34-BernBBMs118-1');
    await page.waitForFunction(() => document.querySelector('#annotations-list')?.textContent.includes('david [uncertain text] dicit'));
    assert.equal(await bern.locator('.annotation-transcription').first().innerText(), 'david [uncertain text] dicit (provisional reading)');
    assert(!(await bern.innerText()).includes('Partly transcribed'));
    assert(!(await bern.innerText()).includes('The editor confirms'));
    assert((await bern.locator('.annotation-details').first().textContent()).includes('The editor confirms that untranscribed material precedes the surviving word dicit.'));
    assert((await bern.locator('pre').first().textContent()).includes('[¤2v] (§) dicit (@1) issa (#2 nota NT)'));
    assert.equal(await page.locator('#annotations-header button').getAttribute('aria-expanded'), 'true');
    const symbolic = bern.locator('article').nth(2);
    assert.equal(await symbolic.locator('.annotation-category').innerText(), 'Symbolic annotation: nota NT');
    assert.equal(await symbolic.locator('.annotation-description').count(), 0);
    assert.equal(await symbolic.locator('.annotation-wording').innerText(), 'nota NT');
    results.checks.push('symbolic entry uses one category line with its supplied description and no duplicate editorial-note label');
    assert.equal(await page.locator('.annotation-supplemental-record').count(), 2);
    const bodmer = page.locator('#ms-annotation-worksheet-bodmer98-e11-3');
    assert((await bodmer.locator('.annotation-transcription').innerText()).includes('issa si a uiro diuisa'));
    assert(!(await bodmer.innerText()).includes('si remains uncertain'));
    assert((await bodmer.locator('.annotation-details').textContent()).includes('si remains uncertain'));
    assert((await bodmer.locator('pre').textContent()).includes('issa si a uira diuisat'));
    await page.locator('#reader-annotations').screenshot({path: path.join(path.dirname(output), '../screenshots/bern-partial-after.png'), animations: 'disabled'});
    results.checks.push('Bern shows one provisional reading; partial-transcription explanation and original notation remain in scholarly details');
    await page.addStyleTag({content: '*, *::before, *::after {transition: none !important; animation: none !important;}'});
    for (const theme of ['light', 'dark']) {
      await page.evaluate(theme => document.documentElement.setAttribute('data-theme', theme), theme);
      const colours = await page.evaluate(() => {
        const panel = document.querySelector('#reader-annotations');
        const reading = document.querySelector('.annotation-transcription');
        return {reading: getComputedStyle(reading).color, background: getComputedStyle(panel).backgroundColor,
          accent: getComputedStyle(document.querySelector('.annotation-passage')).color,
          metadata: getComputedStyle(document.querySelector('.annotation-meta')).color,
          status: getComputedStyle(document.querySelector('.annotation-reading-status')).color,
          allReadings: [...document.querySelectorAll('.annotation-transcription, .annotation-wording')].map(n => getComputedStyle(n).color)};
      });
      assert.equal(colours.reading, colours.accent); assert.notEqual(colours.reading, colours.metadata);
      assert.equal(colours.status, colours.metadata); assert(colours.allReadings.every(c => c === colours.reading));
      const luminance = colour => colour.match(/[\d.]+/g).slice(0,3).map(v => Number(v)/255)
        .map(v => v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4).reduce((n,v,i) => n+v*[.2126,.7152,.0722][i],0);
      const a = luminance(colours.reading), b = luminance(colours.background);
      assert((Math.max(a,b)+.05)/(Math.min(a,b)+.05) >= 4.5, `${theme}: annotation contrast`);
      await page.locator('#reader-annotations').screenshot({path: path.join(path.dirname(output), `../screenshots/bern-clean-${theme}.png`), animations: 'disabled'});
    }
    results.checks.push('annotation words use the site accent in both themes, with neutral qualifiers and text contrast above 4.5:1');
    await page.setViewportSize({width:390,height:844});
    assert(await page.locator('#reader-annotations').evaluate(n => n.scrollWidth <= n.clientWidth + 1));
    await page.screenshot({path:path.join(path.dirname(output),'../screenshots/bern-clean-mobile.png'),animations:'disabled'});
    await page.setViewportSize({width:1280,height:720});
    await page.evaluate(() => document.documentElement.setAttribute('data-theme','light'));
    results.checks.push('compact provisional reading wraps without horizontal panel overflow at 390 pixels');
    await symbolic.evaluate(node => node.scrollIntoView({block:'center'}));
    await page.locator('#reader-annotations').screenshot({path:path.join(path.dirname(output),'../screenshots/symbolic-clean-after.png'),animations:'disabled'});
    await bodmer.locator('article').evaluate(node => node.scrollIntoView({block: 'center'}));
    await page.locator('#reader-annotations').screenshot({path: path.join(path.dirname(output), '../screenshots/bodmer-reviewed-after.png'), animations: 'disabled'});
    await bodmer.locator('.annotation-passage').click();
    await page.waitForSelector('#latin .annotation-target');
    assert.equal(await page.locator('#latin .annotation-target').first().getAttribute('id'), 'latin-book01-num34');
    results.checks.push('recovered Bodmer reading retains its worksheet evidence and navigates to the whole §§34–36 unit');
    await page.goto(origin + '/antiquities/?book=1&unit=27', {waitUntil: 'domcontentloaded'});
    await page.waitForSelector('.annotation-supplemental-record', {state: 'attached'});
    assert.equal(await page.locator('.annotation-supplemental-record').count(), 1);
    assert((await page.locator('.annotation-supplemental-record .annotation-transcription').innerText()).includes('.d significe. sabatum'));
    assert((await page.locator('.annotation-supplemental-record h4').innerText()).includes('Niese §§27–33'));
    results.checks.push('Sabbath supplement appears once in the §§27–33 alignment unit');
    await page.goto(origin + '/antiquities/?book=1', {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => document.querySelectorAll('.annotation-supplemental-record').length === 3);
    assert.equal(await page.locator('.annotation-source-record').count(), 203);
    assert.equal(new Set(await page.locator('.manuscript-annotation .annotation-number').allTextContents()).size,
      await page.locator('.manuscript-annotation').count());
    results.checks.push('Book I preserves all 203 canonical reading records and adds exactly three uniquely numbered worksheet annotations');
    await page.goto(origin + '/deh/?book=1', {waitUntil: 'domcontentloaded'});
    const compare = page.locator('.deh-parallel-link').first(); await compare.waitFor(); await compare.click();
    await page.waitForFunction(() => !!document.querySelector('#parallel-bj-text')?.textContent.trim() && !document.querySelector('#parallel-status')?.textContent.includes('Loading'));
    assert(!(await page.locator('#parallel-status').innerText()).includes('unavailable'));
    results.checks.push('existing DEH comparison opens and loads Josephus parallel text');
    assert.deepEqual(results.errors, []); results.status = 'PASS';
  } finally {
    fs.mkdirSync(path.dirname(output), {recursive: true}); fs.writeFileSync(output, JSON.stringify(results, null, 2) + '\n');
    await browser.close(); server.close();
  }
}
main().catch(error => {console.error(error); process.exitCode = 1;});
