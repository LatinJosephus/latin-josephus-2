/**
 * Stable search launcher, protocol v1.
 *
 * Keep this filename immutable once published. A later launcher change must
 * use a new filename and update the page. The fresh descriptor selects one
 * complete, content-named module graph and its matching immutable catalog.
 */
const MODULES = Object.freeze(['engine.mjs', 'ui-utils.mjs', 'collection.mjs', 'concordance.mjs', 'app.mjs']);
const HASH = /^[a-f0-9]{64}$/u;
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);

/** Validate only same-directory, content-named public search resources. */
export function validateBrowserRelease(value) {
  const fail = () => { throw new Error('Invalid or incompatible search release descriptor'); };
  if (!object(value) || value.schemaVersion !== 1 || value.generatedBy !== 'bin/search/browser-release.mjs'
    || value.launcher !== 'launch-v1.mjs' || !object(value.modules)
    || Object.keys(value.modules).length !== MODULES.length) fail();
  function asset(item, expectedPath) {
    if (!object(item) || !HASH.test(item.sha256) || !Number.isSafeInteger(item.bytes) || item.bytes <= 0
      || item.path !== expectedPath(item.sha256)) fail();
    return item;
  }
  const modules = {};
  for (const name of MODULES) {
    modules[name] = asset(value.modules[name], hash => `${name.slice(0, -4)}.${hash}.mjs`);
  }
  if (value.entry !== modules['app.mjs'].path) fail();
  return {entry: modules['app.mjs'], modules,
    catalog: asset(value.catalog, hash => `catalog.${hash}.json`),
    stylesheet: asset(value.stylesheet, hash => `styles.${hash}.css`),
    lunr: asset(value.lunr, hash => `lunr.${hash}.min.js`)};
}

const integrity = hash => 'sha256-' + btoa(String.fromCharCode(...hash.match(/../gu).map(byte => parseInt(byte, 16))));

async function launch() {
  const root = document.getElementById('lj-search');
  if (!root) return;
  const base = new URL('./', import.meta.url);
  try {
    const response = await fetch(new URL('browser-release.json', base), {cache: 'no-store', credentials: 'same-origin'});
    if (!response.ok) throw new Error(`Search release descriptor returned HTTP ${response.status}`);
    const release = validateBrowserRelease(await response.json());

    function stylesheet() {
      return new Promise((resolve, reject) => {
        const previous = document.getElementById('search-styles');
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = new URL(release.stylesheet.path, base).href;
        link.integrity = integrity(release.stylesheet.sha256);
        link.crossOrigin = 'anonymous';
        link.onload = () => {
          if (previous?.tagName === 'LINK' && previous.rel === 'stylesheet') previous.remove();
          link.id = 'search-styles';
          resolve();
        };
        link.onerror = () => { link.remove(); reject(new Error('The versioned search stylesheet could not be loaded')); };
        document.head.append(link);
      });
    }

    function library() {
      return new Promise((resolve, reject) => {
        const previous = globalThis.lunr;
        const script = document.createElement('script');
        script.src = new URL(release.lunr.path, base).href;
        script.integrity = integrity(release.lunr.sha256);
        script.crossOrigin = 'anonymous';
        script.async = true;
        script.onload = () => typeof globalThis.lunr === 'function' && globalThis.lunr !== previous
          ? resolve() : reject(new Error('The versioned search library did not initialize'));
        script.onerror = () => { script.remove(); reject(new Error('The versioned search library could not be loaded')); };
        document.head.append(script);
      });
    }

    await Promise.all([stylesheet(), library()]);
    await import(new URL(release.entry.path, base).href);
  } catch (error) {
    console.error('Latin Josephus search startup failed:', error);
    const message = root.querySelector('#error');
    if (message) {
      message.textContent = 'The current search version could not be loaded. Reload this page and try again. On Windows, use Ctrl+F5 to obtain fresh files.';
      message.hidden = false;
    }
    const status = root.querySelector('#status');
    if (status) status.textContent = 'Search could not start. Please reload this page.';
    root.querySelector('#results-region')?.setAttribute('aria-busy', 'false');
    const button = root.querySelector('#search-button');
    if (button) button.disabled = true;
  }
}

// Importing the descriptor validator in Node tests performs no browser work.
if (typeof document !== 'undefined') await launch();
