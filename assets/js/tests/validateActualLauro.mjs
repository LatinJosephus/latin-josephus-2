/* Read-only compatibility check for the newly generated local Lauro book data. */
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const source = await readFile(new URL('../lauroCore.js', import.meta.url), 'utf8');
const {validateBook, canonicalIds} = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const base = new URL('../../data/deh-lauro1544/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('manifest.json', base), 'utf8'));
assert.equal(manifest.schema, 'lauro1544-reader/1');
assert(['LOCAL_PREVIEW_READY', 'INTEGRATION_READY'].includes(manifest.authority.status));
assert.equal(manifest.books.length, 5);
const seen = new Set(), results = [];
for (const record of manifest.books) {
  const bytes = await readFile(new URL(record.path, base));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), record.sha256);
  const book = JSON.parse(bytes.toString('utf8'));
  assert.equal(book.book, record.book);
  assert.equal(book.version, manifest.version);
  validateBook(book);
  book.mappings.forEach(mapping => canonicalIds(mapping).forEach(id => seen.add(id)));
  results.push({book: book.book, lines: book.lines.length, mappings: book.mappings.length,
    nativeChapters: book.divisions.filter(d => d.is_native_chapter).length,
    annotations: book.annotations.length, sha256: record.sha256});
}
assert.equal(seen.size, 558);
console.log(JSON.stringify({status: 'PASS', canonicalUnits: seen.size, version: manifest.version, books: results}, null, 2));
