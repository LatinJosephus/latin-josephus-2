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
    assert.deepEqual([result.books, result.sections, result.tokens], [68, 25009, 1347222]);
    const bellum = baseline.catalog.collections.find(collection => collection.id === 'bellum-latin-cardwell');
    const deh = baseline.catalog.collections.find(collection => collection.id === 'deh-latin-ussani');
    assert.deepEqual([bellum.totals.books, bellum.totals.sections, bellum.totals.tokens], [7, 4001, 114794]);
    assert.deepEqual([deh.totals.books, deh.totals.sections, deh.totals.tokens], [5, 558, 87472]);
    const ca = baseline.catalog.collections.find(collection => collection.id === 'contra-apionem-latin-boysen');
    assert.deepEqual([ca.totals.books, ca.totals.sections, ca.totals.tokens], [2, 616, 21018]);
    const antiquities = baseline.catalog.collections.find(collection => collection.id === 'antiquities-latin-bamberg78');
    assert.deepEqual([antiquities.totals.books, antiquities.totals.sections, antiquities.totals.tokens], [20, 7283, 265023]);
    const whiston = baseline.catalog.collections.find(collection => collection.id === 'antiquities-english-whiston');
    assert.deepEqual([whiston.totals.books, whiston.totals.sections, whiston.totals.tokens], [20, 7376, 470938]);
    const whistonBellum = baseline.catalog.collections.find(collection => collection.id === 'bellum-english-whiston');
    assert.deepEqual([whistonBellum.totals.books, whistonBellum.totals.sections, whistonBellum.totals.tokens], [7, 4001, 215072]);
    const whistonApion = baseline.catalog.collections.find(collection => collection.id === 'contra-apionem-english-whiston');
    assert.deepEqual([whistonApion.totals.books, whistonApion.totals.sections, whistonApion.totals.tokens], [2, 616, 36853]);
    const pollardDeh = baseline.catalog.collections.find(collection => collection.id === 'deh-english-pollard');
    assert.deepEqual([pollardDeh.totals.books, pollardDeh.totals.sections, pollardDeh.totals.tokens], [5, 558, 136052]);
    assert.equal(result.sourceXML.length, 80);
    assert.equal(result.sourceXML.filter(source => source.path.includes('/English/')).length, 35);
    assert.equal(result.assets, baseline.artifacts.length + 1);
    assert.equal(baseline.manifest.browserRelease.launcher, 'launch-v1.mjs');
    assert.equal(result.sourceXML.filter(source => /\/niese\/book-(?:1[1-9]|20)\.json$/u.test(source.path)).length, 10);
  });

  await t.test('an XML change is rejected before old text can be published', () => {
    changed('assets/xml/bellum/Latin/book-01.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });

  await t.test('a De excidio source change is rejected before its old index can be published', () => {
    changed('assets/xml/deh/Latin/book-01.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });
  await t.test('an English De excidio source change is rejected before its old index can be published', () => {
    changed('assets/xml/deh/English/book-01.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });

  await t.test('a Contra Apionem source change is rejected before its old index can be published', () => {
    changed('assets/xml/contra-apionem/Latin/book-02.xml', bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
      () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
  });

  await t.test('both Antiquities narrative and separate Proem changes invalidate their indexes', () => {
    for (const relative of ['assets/xml/antiquities/Latin/book-05.xml', 'assets/xml/antiquities/Latin/book-10.xml',
      'assets/xml/antiquities/Latin/book-11.xml', 'assets/xml/antiquities/Latin/book-15.xml',
      'assets/xml/antiquities/Latin/book-16.xml', 'assets/xml/antiquities/Latin/book-20.xml',
      'assets/xml/antiquities/Latin/preface.xml']) {
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed.*XML/u));
    }
  });

  await t.test('Whiston I–XX rejects changed narrative or Proem source bytes', () => {
    for (const relative of ['assets/xml/antiquities/English/preface.xml',
      ...Array.from({length: 20}, (_, i) => i + 1).map(number => `assets/xml/antiquities/English/book-${String(number).padStart(2, '0')}.xml`)]) {
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed|Whiston source/u));
    }
  });

  await t.test('every Whiston Bellum source is protected and accepts only line-ending equivalence', () => {
    const original = verifySearchAssets(fixture);
    for (let number = 1; number <= 7; number++) {
      const relative = `assets/xml/bellum/English/book-${String(number).padStart(2, '0')}.xml`;
      changed(relative, bytes => bytes.toString('utf8').replace(/\r?\n/gu, '\r\n'), () => {
        const converted = verifySearchAssets(fixture);
        assert.equal(converted.publicationManifestSHA256, original.publicationManifestSHA256);
        const source = converted.sourceXML.find(item => item.path === relative);
        assert.equal(source.normalizedSHA256, original.sourceXML.find(item => item.path === relative).normalizedSHA256);
        assert.notEqual(source.worktreeSHA256, source.normalizedSHA256);
      });
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed|Whiston Bellum source/u));
    }
  });

  await t.test('both Whiston Contra Apionem sources accept line-ending equivalence and reject changed text', () => {
    const original = verifySearchAssets(fixture);
    for (let number = 1; number <= 2; number++) {
      const relative = `assets/xml/contra-apionem/English/book-${String(number).padStart(2, '0')}.xml`;
      changed(relative, bytes => bytes.toString('utf8').replace(/\r?\n/gu, '\r\n'), () => {
        const converted = verifySearchAssets(fixture);
        assert.equal(converted.publicationManifestSHA256, original.publicationManifestSHA256);
        const source = converted.sourceXML.find(item => item.path === relative);
        assert.equal(source.normalizedSHA256, original.sourceXML.find(item => item.path === relative).normalizedSHA256);
        assert.notEqual(source.worktreeSHA256, source.normalizedSHA256);
      });
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n<!-- source changed -->\n')]),
        () => assert.throws(() => verifySearchAssets(fixture), /Stale or changed|Whiston Contra Apionem source/u));
    }
  });

  await t.test('accepted Latin identity registry changes invalidate their indexed source spans', () => {
    for (const relative of ['assets/xml/antiquities/niese/book-11.json', 'assets/xml/antiquities/niese/book-14.json',
      'assets/xml/antiquities/niese/book-15.json', 'assets/xml/antiquities/niese/book-16.json',
      'assets/xml/antiquities/niese/book-18.json', 'assets/xml/antiquities/niese/book-20.json']) {
      changed(relative, bytes => Buffer.concat([bytes, Buffer.from('\n ')]),
        () => assert.throws(() => verifySearchAssets(fixture), error =>
          /Stale or changed/u.test(error.message) && error.message.includes(relative)));
    }
  });

  await t.test('the accepted CRLF Book XIV registry keeps its fingerprint after LF checkout conversion', () => {
    const relative = 'assets/xml/antiquities/niese/book-14.json', original = verifySearchAssets(fixture);
    changed(relative, bytes => bytes.toString('utf8').replace(/\r\n/gu, '\n'), () => {
      const converted = verifySearchAssets(fixture);
      assert.equal(converted.publicationManifestSHA256, original.publicationManifestSHA256);
      const registry = converted.sourceXML.find(source => source.path === relative);
      assert.equal(registry.normalizedSHA256, '99361742e1e0aa7fe77ee61b879b283a6ec30692fb006d953ee5700050ab06f9');
      assert.notEqual(registry.worktreeSHA256, registry.indexedSHA256);
    });
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

  for (const [number, rawSHA256, normalizedSHA256] of [
    [12, 'e28ce3914fe0e764571e049b20b5ddabfc6d3080cf6dd4537522b083be7cc83c', 'ba4808e3b5e234c2ec1bbffd3e4b662a78b2fe41c1643be3e4e7e6662d583286'],
    [17, '29a0a40375396016162920b32462f259cf3791fa6a12b4af1f6d2ed7bd41cca1', 'd6056846f61ae43003989a2d799501d5e9edb7c3b407d9292b3c89064df6a0ac'],
    [18, 'db6c960c3d27457e21b4f5cccdf5a389f6d9ecdfd927a53d1379484eeef3c67d', 'ba1529509dddf72ec82a5eda63fb95f6d0f8d88dad87c69f5cf7a431536c63fa'],
    [19, '9ce4e6116a0cbd57823e07cff97559941e9015da79d02dd0ae6b2e9c0877e129', 'e025279ffb304a08f2f960845c6dca1e09162188bffd44f541cd787ae0aaf094'],
    [20, '229c2c47f9c4f6ad19ae3b96aeb8c9fcdbe849bb4a733cf214ad0f133d28bc0e', '8f5437db04d4423b79db151603187f50400a9d41938f94394a8da744842af673'],
  ]) await t.test(`accepted CRLF Whiston Book ${number} keeps its fingerprint after LF checkout conversion`, () => {
    const relative = `assets/xml/antiquities/English/book-${number}.xml`, original = verifySearchAssets(fixture);
    const indexed = original.sourceXML.find(source => source.path === relative);
    assert.equal(indexed.indexedSHA256, rawSHA256);
    changed(relative, bytes => bytes.toString('utf8').replace(/\r\n/gu, '\n'), () => {
      const converted = verifySearchAssets(fixture);
      assert.equal(converted.publicationManifestSHA256, original.publicationManifestSHA256);
      const source = converted.sourceXML.find(item => item.path === relative);
      assert.equal(source.normalizedSHA256, normalizedSHA256);
      assert.equal(source.worktreeSHA256, source.normalizedSHA256);
      assert.notEqual(source.worktreeSHA256, source.indexedSHA256);
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
    '<link id="search-styles" rel="stylesheet" href="/assets/search/styles.css">\n' +
    '<script type="module" src="/assets/search/launch-v1.mjs"></script>\n');

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
      () => assert.throws(() => verifySearchAssets(fixture, {site}), /must load its versioned launcher/u));
  });

  await t.test('a generated page cannot add the old mutable app beside the launcher', () => {
    changed('_site/search/index.html', bytes => Buffer.concat([bytes, Buffer.from('<script type="module" src="/assets/search/app.mjs"></script>')]),
      () => assert.throws(() => verifySearchAssets(fixture, {site}), /must not load an unversioned/u));
  });
});
