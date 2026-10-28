/** Browser release tests isolate the actual cache-boundary failure, not corpus extraction. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import test from 'node:test';
import {BROWSER_MODULES, planBrowserRelease} from '../browser-release.mjs';
import {validateBrowserRelease} from '../launch-v1.mjs';

const repository = path.resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'latin-josephus-browser-release-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  for (const relative of [...BROWSER_MODULES, 'browser-release.mjs', 'catalog.json', 'annotations.bundle.json', 'styles.css', 'vendor/lunr.min.js']) {
    const target = path.join(root, 'bin/search', relative);
    fs.mkdirSync(path.dirname(target), {recursive: true});
    fs.copyFileSync(path.join(repository, 'bin/search', relative), target);
  }
  return root;
}
function change(root, relative, transform) {
  const file = path.join(root, 'bin/search', relative);
  fs.writeFileSync(file, transform(fs.readFileSync(file, 'utf8')));
}

test('browser output pins every module import and the matching catalog to verified content names', t => {
  const root = fixture(t), result = planBrowserRelease(root), repeated = planBrowserRelease(root);
  assert.deepEqual(result, repeated, 'Planning must be deterministic and make no output writes');
  assert.equal(fs.existsSync(path.join(root, 'assets/search')), false);
  assert.equal(result.artifacts.length, 10);
  assert.equal(validateBrowserRelease(result.descriptor).entry.path, result.descriptor.entry);
  for (const item of result.artifacts) {
    const source = fs.readFileSync(path.join(root, item.source)), output = result.contents.get(item.path);
    assert.equal(hash(source), item.sourceSHA256);
    assert.equal(hash(output), item.sha256);
    assert.equal(output.length, item.bytes);
    assert.equal(item.generated, true);
  }
  for (const [name, item] of Object.entries(result.descriptor.modules)) {
    const code = result.contents.get(item.path).toString('utf8');
    assert.equal(item.path, `${name.slice(0, -4)}.${hash(code)}.mjs`);
    for (const match of code.matchAll(/\bfrom\s+['"]\.\/([^'"]+)['"]/gu)) {
      assert.ok(Object.values(result.descriptor.modules).some(module => module.path === match[1]), match[1]);
    }
    assert.doesNotMatch(code, /\bfrom\s+['"]\.\/(?:engine|ui-utils|collection|concordance)\.mjs['"]/u);
  }
  const app = result.contents.get(result.descriptor.entry).toString('utf8');
  assert.ok(app.includes(`./${result.descriptor.catalog.path}`));
  assert.match(app, /baseURL\s*:\s*new URL\(\s*['"]\.\/['"]\s*,\s*import\.meta\.url\s*\)/u,
    'Book-relative URL base stays in assets/search');
  assert.doesNotMatch(app, /['"]\.\/catalog\.json['"]/u);
  assert.deepEqual(result.contents.get(result.descriptor.catalog.path), fs.readFileSync(path.join(root, 'bin/search/catalog.json')));
  assert.deepEqual(result.contents.get(result.descriptor.stylesheet.path), fs.readFileSync(path.join(root, 'bin/search/styles.css')));
  assert.deepEqual(result.contents.get(result.descriptor.lunr.path), fs.readFileSync(path.join(root, 'bin/search/vendor/lunr.min.js')));
  const annotation = result.artifacts.find(item => item.role === 'browser-annotations');
  assert.ok(app.includes(`./${annotation.path}`));
  assert.deepEqual(result.contents.get(annotation.path), fs.readFileSync(path.join(root, 'bin/search/annotations.bundle.json')));
});

test('changed annotation data changes its content address and the app without altering main-text bundles', t => {
  const root = fixture(t), before = planBrowserRelease(root);
  change(root, 'annotations.bundle.json', value => value + '\n');
  const after = planBrowserRelease(root);
  assert.notEqual(before.descriptor.entry, after.descriptor.entry);
  assert.notEqual(before.artifacts.find(item => item.role === 'browser-annotations').path, after.artifacts.find(item => item.role === 'browser-annotations').path);
  assert.deepEqual(before.descriptor.catalog, after.descriptor.catalog);
  assert.deepEqual(before.descriptor.modules['engine.mjs'], after.descriptor.modules['engine.mjs']);
});

test('a changed engine changes both intermediate modules and the app, so cached imports cannot survive an upgrade', t => {
  const root = fixture(t), before = planBrowserRelease(root);
  change(root, 'engine.mjs', value => value + '\n// A reviewed runtime revision.\n');
  const after = planBrowserRelease(root);
  for (const name of ['engine.mjs', 'collection.mjs', 'concordance.mjs', 'app.mjs']) {
    assert.notEqual(after.descriptor.modules[name].path, before.descriptor.modules[name].path, name);
  }
  assert.deepEqual(after.descriptor.modules['ui-utils.mjs'], before.descriptor.modules['ui-utils.mjs']);
  assert.deepEqual(after.descriptor.catalog, before.descriptor.catalog);
});

test('a changed catalog receives a new address and changes its app even when query code is unchanged', t => {
  const root = fixture(t), before = planBrowserRelease(root);
  change(root, 'catalog.json', value => value + '\n');
  const after = planBrowserRelease(root);
  assert.notEqual(after.descriptor.catalog.path, before.descriptor.catalog.path);
  assert.notEqual(after.descriptor.entry, before.descriptor.entry);
  for (const name of BROWSER_MODULES.filter(name => name !== 'app.mjs')) {
    assert.deepEqual(after.descriptor.modules[name], before.descriptor.modules[name], name);
  }
  assert.ok(before.contents.get(before.descriptor.entry).toString('utf8').includes(before.descriptor.catalog.path),
    'The earlier app keeps its own catalog URL');
});

test('new dependencies and unreviewed catalog-loading syntax fail closed', async t => {
  for (const [label, relative, transform, expected] of [
    ['external dependency', 'collection.mjs', value => value.replace('./engine.mjs', 'https://example.invalid/engine.mjs'), /Unapproved browser module dependency/u],
    ['query-string dependency', 'collection.mjs', value => value.replace('./engine.mjs', './engine.mjs?v=old'), /Unapproved browser module dependency/u],
    ['unknown local module', 'collection.mjs', value => value.replace('./engine.mjs', './other.mjs'), /Unapproved browser module dependency/u],
    ['dynamic dependency', 'engine.mjs', value => value + '\nawait import("./other.mjs");\n', /Unsupported import syntax/u],
    ['side-effect dependency', 'engine.mjs', value => value + '\nimport "./other.mjs";\n', /Unsupported import syntax/u],
    ['re-export dependency', 'engine.mjs', value => value + '\nexport * from "./other.mjs";\n', /Unsupported re-export/u],
    ['namespace re-export dependency', 'engine.mjs', value => value + '\nexport * as other from "./other.mjs";\n', /Unsupported re-export/u],
    ['commented re-export dependency', 'engine.mjs', value => value + '\nexport/* comment */{other}/* comment */from "./other.mjs";\n', /Unsupported re-export/u],
    ['cycle', 'engine.mjs', value => 'import {createCollection} from "./collection.mjs";\n' + value, /Cyclic browser module imports/u],
    ['changed catalog loading', 'app.mjs', value => value.replace('./catalog.json', './another-catalog.json'), /exactly one reviewed catalog URL/u],
  ]) await t.test(label, st => {
    const root = fixture(st); change(root, relative, transform);
    assert.throws(() => planBrowserRelease(root), expected);
  });
});

test('the launcher rejects descriptor paths outside the exact generated release graph', async t => {
  const root = fixture(t), baseline = planBrowserRelease(root).descriptor;
  for (const [label, mutate] of [
    ['schema', value => { value.schemaVersion = 2; }],
    ['launcher', value => { value.launcher = 'launch-v2.mjs'; }],
    ['external app', value => { value.entry = 'https://example.invalid/app.mjs'; }],
    ['missing imported module', value => { delete value.modules['engine.mjs']; }],
    ['unapproved module', value => { value.modules['extra.mjs'] = value.modules['engine.mjs']; }],
    ['mismatched hash name', value => { value.modules['engine.mjs'].sha256 = '0'.repeat(64); }],
    ['mutable catalog', value => { value.catalog.path = 'catalog.json'; }],
    ['parent stylesheet', value => { value.stylesheet.path = '../styles.css'; }],
    ['unversioned library', value => { value.lunr.path = 'vendor/lunr.min.js'; }],
    ['query URL', value => { value.catalog.path += '?v=old'; }],
    ['invalid byte count', value => { value.stylesheet.bytes = -1; }],
  ]) await t.test(label, () => {
    const changed = structuredClone(baseline); mutate(changed);
    assert.throws(() => validateBrowserRelease(changed), /Invalid or incompatible search release descriptor/u);
  });
});
