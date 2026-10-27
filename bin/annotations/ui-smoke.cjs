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
