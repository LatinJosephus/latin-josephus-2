// Restore the exact hash-bound byte representation in generated output only.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyReaderCorpus, sha} from './reader-corpus-integrity.mjs';
import {verifySearchAssets} from './search/publication.mjs';
const root = path.resolve(fileURLToPath(new URL('../',import.meta.url)));
const at = process.argv.indexOf('--site');
assert(at >= 0 && process.argv[at+1], 'Specify the generated --site directory');
const site = path.resolve(process.argv[at+1]);
assert(site !== root && !root.startsWith(site+path.sep), 'Publication destination must be generated output');
const corpus = verifyReaderCorpus(root);
const rows = [];
for (const [relative, record] of Object.entries(corpus.manifest.files)) {
  const target = path.resolve(site,relative);
  assert(target.startsWith(site+path.sep));
  const current = fs.readFileSync(target);
  assert(record.allowed_worktree_sha256.includes(sha(current)), 'Generated source differs: '+relative);
  const authority = corpus.publication[relative];
  if (authority && !current.equals(authority)) fs.writeFileSync(target, authority);
  const result = fs.readFileSync(target);
  assert.equal(sha(result), authority ? sha(authority) : sha(current));
  rows.push({path:relative, source_sha256:sha(current), publication_sha256:sha(result),
    EOL_representation_restored:!current.equals(result)});
}
const search = verifySearchAssets(root, {site});
console.log(JSON.stringify({...corpus.report, generated_site:site, repository_sources_modified:false, files:rows, search},null,2));
