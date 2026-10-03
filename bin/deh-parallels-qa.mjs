#!/usr/bin/env node
// Local, read-only browser QA host. bin is excluded from the Jekyll publication.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const frozen = await readFile(resolve(root, 'assets/data/deh-josephus-concordance.json'));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
if (sha(frozen) !== 'c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c') {
  throw new Error('Frozen concordance SHA differs. Stop for editorial review.');
}
for (const [path, expected] of Object.entries(JSON.parse(frozen).canonical_xml_sha256)) {
  if (!path.startsWith('assets/xml/') || sha(await readFile(resolve(root, path))) !== expected) {
    throw new Error(`Canonical XML differs: ${path}`);
  }
}
const html = `<!doctype html><html lang="en"><meta charset="utf-8">
<title>DEH–Bellum full publication QA</title><h1>DEH–Bellum full publication QA</h1>
<p>This local test uses the production excerpt module and canonical XML.</p>
<button id="run">Run full concordance QA</button><p id="qa-status" role="status">Ready</p>
<pre id="qa-result"></pre><script src="/assets/js/CETEI.js"></script>
<script type="module" src="/bin/deh-parallels-browser-qa.js"></script></html>`;
const allowed = /^(?:assets\/(?:js\/(?:CETEI|dehParallelsCore)\.js|data\/deh-josephus-concordance\.json|xml\/(?:deh|bellum)\/(?:Latin|English|Greek)\/book-\d\d\.xml)|bin\/deh-parallels-browser-qa\.js)$/;
const server = createServer(async (request, response) => {
  try {
    const path = new URL(request.url, 'http://127.0.0.1').pathname.slice(1);
    if (!path) {
      response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      response.end(html);
    } else if (allowed.test(path)) {
      const type = path.endsWith('.js') ? 'text/javascript' : path.endsWith('.json') ? 'application/json' : 'application/xml';
      response.writeHead(200, { 'Content-Type': `${type}; charset=utf-8` });
      response.end(await readFile(resolve(root, path)));
    } else {
      response.writeHead(404);
      response.end();
    }
  } catch {
    response.writeHead(500);
    response.end('QA asset unavailable');
  }
});
server.listen(Number(process.argv[2] || 4001), '127.0.0.1', () => {
  console.log(`Read-only QA: http://127.0.0.1:${server.address().port}/ (100 XML hashes verified)`);
});
