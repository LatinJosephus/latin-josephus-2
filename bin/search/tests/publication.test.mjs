/** Exercise publication failures in temporary copies; never mutate repository or scholarly sources. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {publicationPlan, exportSearchAssets, verifySearchAssets} from '../publication.mjs';

const repository = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));

test('search publication preserves current inputs and refuses stale or incomplete exports', async t => {
  const baseline = publicationPlan(repository);
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'latin-josephus-search-publication-'));
  t.after(() => fs.rmSync(fixture, {recursive: true, force: true}));
  const copied = new Set([...baseline.manifest.inputs.map(item => item.path),
    ...baseline.artifacts.map(item => item.source)]);
  for (const relative of copied) {
    const target = path.join(fixture, relative);
    fs.mkdirSync(path.dirname(target), {recursive: true});
    fs.copyFileSync(path.join(repository, relative), target);
  }
  exportSearchAssets(fixture);

  function changed(relative, transform, verify) {
    const filename = path.join(fixture, relative), original = fs.readFileSync(filename);
    fs.writeFileSync(filename, transform(original));
    try { verify(); } finally { fs.writeFileSync(filename, original); }
  }

  await t.test('an unchanged source and asset set passes', () => {
    const result = verifySearchAssets(fixture);
    assert.equal(result.status, 'PASS');
    assert.deepEqual([result.books, result.sections, result.tokens], [24, 8590, 361142]);
    const bellum = baseline.catalog.collections.find(collection => collection.id === 'bellum-latin-cardwell');
    const deh = baseline.catalog.collections.find(collection => collection.id === 'deh-latin-ussani');
    assert.deepEqual([bellum.totals.books, bellum.totals.sections, bellum.totals.tokens], [7, 4001, 114794]);
    assert.deepEqual([deh.totals.books, deh.totals.sections, deh.totals.tokens], [5, 558, 87472]);
    const ca = baseline.catalog.collections.find(collection => collection.id === 'contra-apionem-latin-boysen');
    assert.deepEqual([ca.totals.books, ca.totals.sections, ca.totals.tokens], [2, 616, 21018]);
    const antiquities = baseline.catalog.collections.find(collection => collection.id === 'antiquities-latin-bamberg78');
    assert.deepEqual([antiquities.totals.books, antiquities.totals.sections, antiquities.totals.tokens], [10, 3415, 137858]);
    assert.equal(result.sourceXML.length, 25);
  });

  await t.test('an XML change is rejected before old text can be published', () => {
    changed('assets/xml/bellum/Latin/book-01.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });

  await t.test('a De excidio source change is rejected before its old index can be published', () => {
    changed('assets/xml/deh/Latin/book-01.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });

  await t.test('a Contra Apionem source change is rejected before its old index can be published', () => {
    changed('assets/xml/contra-apionem/Latin/book-02.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });

  await t.test('both Antiquities narrative and separate Proem changes invalidate their indexes', () => {
    for (const relative of ['assets/xml/antiquities/Latin/book-05.xml', 'assets/xml/antiquities/Latin/book-10.xml', 'assets/xml/antiquities/Latin/preface.xml']) {
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
    }
  });

  await t.test('the separate Antiquities Proem permits only line-ending equivalence', () => {
    const relative = 'assets/xml/antiquities/Latin/preface.xml', original = verifySearchAssets(fixture);
    changed(relative, bytes => bytes.toString('utf8').replace(/\r?\n/gu, '\r\n'), () => {
      const converted = verifySearchAssets(fixture);
      assert.equal(converted.publicationManifestSHA256, original.publicationManifestSHA256);
      const proem = converted.sourceXML.find(source => source.path === relative);
      assert.equal(proem.hashMode, 'crlf-to-lf');
      assert.notEqual(proem.worktreeSHA256, proem.normalizedSHA256);
    });
  });

  await t.test('a CRLF source checkout passes with deterministic inputs and exact raw provenance', () => {
    const relative = 'assets/xml/bellum/Latin/book-01.xml';
    const original = verifySearchAssets(fixture);
    changed(relative, bytes => bytes.toString('utf8').replace(/\r?\n/gu, '\r\n'), () => {
      const converted = verifySearchAssets(fixture);
      assert.equal(converted.status, 'PASS');
      assert.equal(converted.publicationManifestSHA256, original.publicationManifestSHA256);
      assert.equal(converted.sourceXML[0].hashMode, 'crlf-to-lf');
      assert.equal(converted.sourceXML[0].indexedSHA256, original.sourceXML[0].indexedSHA256);
      assert.equal(converted.sourceXML[0].normalizedSHA256, original.sourceXML[0].normalizedSHA256);
      assert.notEqual(converted.sourceXML[0].worktreeSHA256, original.sourceXML[0].worktreeSHA256);
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('<!-- real source edit -->\r\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
    });
  });

  await t.test('runtime and Jekyll component edits require a fresh export', () => {
    for (const relative of ['bin/search/app.mjs', '_includes/search-interface.html']) {
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Search export is stale/u));
    }
  });

  await t.test('adding a source module invalidates the source inventory', () => {
    const filename = path.join(fixture, 'bin/search/future-helper.mjs');
    fs.writeFileSync(filename, '// New dependency must be included in a reviewed rebuild.\n');
    try { assert.throws(() => verifySearchAssets(fixture), /Search export is stale/u); }
    finally { fs.unlinkSync(filename); }
  });

  await t.test('a damaged exported bundle is rejected', () => {
    const relative = `assets/search/${baseline.catalog.books[0].path}`;
    changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed exported search asset/u));
  });

  await t.test('unmanaged export files are reported and are not deleted', () => {
    const filename = path.join(fixture, 'assets/search/unmanaged.txt');
    fs.writeFileSync(filename, 'Do not overwrite or remove without review.\n');
    try {
      assert.throws(() => verifySearchAssets(fixture), /inventory has missing or extra files/u);
      assert.throws(() => exportSearchAssets(fixture), /Unmanaged file/u);
      assert.equal(fs.readFileSync(filename, 'utf8'), 'Do not overwrite or remove without review.\n');
    } finally { fs.unlinkSync(filename); }
  });

  await t.test('an extra collection needs an explicit source and QA adapter', () => {
    const registryPath = 'bin/search/config/collections.json';
    const manifestPath = path.join(fixture, 'bin/search/config/unapproved.json');
    const manifest = {...baseline.collections[0].manifest, id: 'unapproved-collection'};
    fs.writeFileSync(manifestPath, JSON.stringify(manifest));
    try {
      changed(registryPath, bytes => {
        const registry = JSON.parse(bytes.toString('utf8'));
        registry.collections.push('unapproved.json');
        return JSON.stringify(registry);
      }, () => assert.throws(() => verifySearchAssets(fixture), /No approved extraction\/QA adapter/u));
    } finally { fs.unlinkSync(manifestPath); }
  });

  await t.test('unrelated reader changes do not invalidate the search input gate', () => {
    const filename = path.join(fixture, 'assets/js/renderTei.js');
    fs.mkdirSync(path.dirname(filename), {recursive: true});
    fs.writeFileSync(filename, '// Historical reader evidence is deliberately not an active search input.\n');
    assert.equal(verifySearchAssets(fixture).status, 'PASS');
  });

  const site = path.join(fixture, '_site');
  fs.cpSync(path.join(fixture, 'assets/search'), path.join(site, 'assets/search'), {recursive: true});
  for (const source of baseline.sources) {
    const target = path.join(site, source.path);
    fs.mkdirSync(path.dirname(target), {recursive: true});
    fs.copyFileSync(path.join(fixture, source.path), target);
  }
  fs.mkdirSync(path.join(site, 'search'), {recursive: true});
  fs.writeFileSync(path.join(site, 'search/index.html'), '<main id="lj-search"></main>\n' +
    '<link rel="stylesheet" href="/assets/search/styles.css">\n' +
    '<script src="/assets/search/vendor/lunr.min.js" defer></script>\n' +
    '<script type="module" src="/assets/search/app.mjs"></script>\n');

  await t.test('generated XML permits line-ending representation changes only', () => {
    assert.equal(verifySearchAssets(fixture, {site}).status, 'PASS');
    const relative = '_site/assets/xml/bellum/Latin/book-01.xml';
    changed(relative, bytes => bytes.toString('utf8').replace(/\r?\n/gu, '\r\n'), () => {
      const result = verifySearchAssets(fixture, {site});
      assert.equal(result.status, 'PASS');
      assert.equal(result.generatedXML[0].lineEndingRepresentationOnly, true);
    });
    changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n<!-- different text -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture, {site}), /Generated indexed XML text differs/u));
  });

  await t.test('an incomplete generated search page fails publication', () => {
    changed('_site/search/index.html', () => '<main id="lj-search"></main>',
      () => assert.throws(() => verifySearchAssets(fixture, {site}), /must load its search module/u));
  });
});
