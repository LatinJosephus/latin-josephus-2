/**
 * Deterministic browser-only projection of the audited search sources.
 *
 * All modules stay in assets/search, so their original import.meta.url bases
 * remain valid. Only named static import specifiers and the app's one catalog
 * URL are rewritten. Canonical source modules and indexed data are untouched.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';

export const BROWSER_RELEASE_NAME = 'browser-release.json';
export const BROWSER_LAUNCHER_NAME = 'launch-v1.mjs';
export const BROWSER_MODULES = Object.freeze([
  'engine.mjs', 'ui-utils.mjs', 'collection.mjs', 'concordance.mjs', 'app.mjs',
]);
const GENERATOR = 'bin/search/browser-release.mjs';
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const jsonBytes = value => Buffer.from(JSON.stringify(value, null, 2) + '\n');
const namedImports = () => /^[ \t]*import\s*\{[^{}]*\}\s*from\s*(['"])([^'"\r\n]+)\1\s*;[ \t]*(?=\r?$)/gmu;
const moduleName = (name, sha256) => `${name.slice(0, -4)}.${sha256}.mjs`;

/**
 * Return generated artifact descriptors plus their exact bytes. Each artifact
 * retains a real canonical `source` and its independent `sourceSHA256`; its
 * ordinary `sha256` and `bytes` describe the browser output, not that source.
 * The caller must export contents.get(item.path), never blindly copy source.
 */
export function planBrowserRelease(root) {
  const sourceDirectory = path.resolve(root, 'bin/search');
  const inputs = new Map();
  const contents = new Map();
  const artifacts = [];
  const modules = new Map();
  const building = new Set();

  function source(relative) {
    if (!inputs.has(relative)) inputs.set(relative, fs.readFileSync(path.join(sourceDirectory, relative)));
    return inputs.get(relative);
  }

  function generated(relative, filename, bytes, role) {
    assert(!contents.has(filename), `Duplicate generated browser asset: ${filename}`);
    const item = {path: filename, source: `bin/search/${relative}`, sourceSHA256: digest(source(relative)),
      sha256: digest(bytes), bytes: bytes.length, role, generated: true};
    contents.set(filename, bytes);
    artifacts.push(item);
    return {path: item.path, sha256: item.sha256, bytes: item.bytes};
  }

  const catalogBytes = source('catalog.json');
  // The data contract is verified by publication.mjs; this also refuses a
  // damaged or non-JSON catalog before preparing browser URLs.
  const catalogJSON = JSON.parse(catalogBytes.toString('utf8'));
  assert(catalogJSON && typeof catalogJSON === 'object' && !Array.isArray(catalogJSON), 'Invalid browser catalog');
  const catalog = generated('catalog.json', `catalog.${digest(catalogBytes)}.json`, catalogBytes, 'browser-catalog');
  const annotationBytes = source('annotations.bundle.json');
  const annotations = generated('annotations.bundle.json', `annotations.${digest(annotationBytes)}.bundle.json`, annotationBytes, 'browser-annotations');

  function buildModule(name) {
    if (modules.has(name)) return modules.get(name);
    assert(BROWSER_MODULES.includes(name), `Unapproved browser module: ${name}`);
    assert(!building.has(name), `Cyclic browser module imports: ${name}`);
    building.add(name);
    const originalBytes = source(name);
    let code = new TextDecoder('utf-8', {fatal: true}).decode(originalBytes);
    const declarations = [...code.matchAll(namedImports())];
    const remainder = code.replace(namedImports(), '');
    // The reviewed modules use named imports only. Fail closed if a new
    // dynamic, side-effect, default, or re-export dependency is introduced.
    // import.meta is a URL base, not another module dependency.
    assert(!/\bimport\b(?!\s*\.\s*meta\b)/u.test(remainder),
      `Unsupported import syntax in browser module ${name}; review the browser generator`);
    // Export lists are deliberately unsupported, including namespace aliases
    // and comments between tokens, so no re-export can bypass the graph.
    assert(!/\bexport(?:\s|\/\*[\s\S]*?\*\/|\/\/[^\r\n]*)*[*{]/u.test(remainder),
      `Unsupported re-export in browser module ${name}; review the browser generator`);
    const replacements = new Map();
    for (const match of declarations) {
      const specifier = match[2];
      assert(/^\.\/[a-z][a-z-]*\.mjs$/u.test(specifier) && BROWSER_MODULES.includes(specifier.slice(2)),
        `Unapproved browser module dependency in ${name}: ${specifier}`);
      replacements.set(specifier, `./${buildModule(specifier.slice(2)).path}`);
    }
    code = code.replace(namedImports(), (declaration, quote, specifier) =>
      declaration.replace(`${quote}${specifier}${quote}`, `${quote}${replacements.get(specifier)}${quote}`));
    if (name === 'app.mjs') {
      let catalogReferences = 0;
      code = code.replace(/new URL\(\s*(['"])\.\/catalog\.json\1\s*,\s*import\.meta\.url\s*\)/gu, value => {
        catalogReferences++;
        return value.replace('./catalog.json', `./${catalog.path}`);
      });
      assert.equal(catalogReferences, 1, 'The browser app must have exactly one reviewed catalog URL');
      assert(!/['"]\.\/catalog\.json['"]/u.test(code), 'The browser app still references a mutable catalog URL');
      const annotationURL = "new URL('./annotations.bundle.json', import.meta.url)";
      assert.equal(code.split(annotationURL).length, 2, 'The browser app must have exactly one reviewed annotation URL');
      code = code.replace(annotationURL, `new URL('./${annotations.path}', import.meta.url)`);
    }
    const bytes = Buffer.from(code, 'utf8');
    const item = generated(name, moduleName(name, digest(bytes)), bytes, 'browser-module');
    modules.set(name, item);
    building.delete(name);
    return item;
  }

  for (const name of BROWSER_MODULES) buildModule(name);
  const css = source('styles.css');
  const stylesheet = generated('styles.css', `styles.${digest(css)}.css`, css, 'browser-stylesheet');
  const lunrBytes = source('vendor/lunr.min.js');
  const lunr = generated('vendor/lunr.min.js', `lunr.${digest(lunrBytes)}.min.js`, lunrBytes, 'browser-library');
  const descriptor = {schemaVersion: 1, generatedBy: GENERATOR, launcher: BROWSER_LAUNCHER_NAME,
    entry: modules.get('app.mjs').path,
    modules: Object.fromEntries(BROWSER_MODULES.map(name => [name, modules.get(name)])),
    catalog, stylesheet, lunr};
  const descriptorBytes = jsonBytes(descriptor);
  generated('browser-release.mjs', BROWSER_RELEASE_NAME, descriptorBytes, 'browser-release');
  artifacts.sort((a, b) => a.path.localeCompare(b.path, 'en'));
  return {descriptor, descriptorBytes, artifacts, contents};
}
