import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {verifyReaderCorpus,sha} from './reader-corpus-integrity.mjs';
const args=process.argv.slice(2), option=(key,fallback)=>args.includes(key)?args[args.indexOf(key)+1]:fallback;
const root=path.resolve(option('--root',fileURLToPath(new URL('../',import.meta.url))));
const corpus=verifyReaderCorpus(root);
if(args.includes('--inventory-only')) { console.log(JSON.stringify(corpus.report)); process.exit(0); }
const fixture=fs.mkdtempSync(path.join(os.tmpdir(),'reader-corpus-negative-'));
for(const relative of ['assets/xml','assets/data/deh-josephus-concordance.json','_docs/reader-corpus-integrity.json','_docs/lodge1602-bellum-integration.json']) {
  const target=path.join(fixture,relative); fs.mkdirSync(path.dirname(target),{recursive:true});
  fs.cpSync(path.join(root,relative),target,{recursive:true});
}
const checks=[];
function rejection(relative, bytes, pattern, name) {
  const target=path.join(fixture,relative),original=fs.existsSync(target)?fs.readFileSync(target):null;
  fs.writeFileSync(target,bytes);
  try { assert.throws(()=>verifyReaderCorpus(fixture,{parse:false}),pattern); checks.push(name); }
  finally { if(original)fs.writeFileSync(target,original);else fs.unlinkSync(target); }
}
verifyReaderCorpus(fixture);
rejection('assets/xml/bellum/English/Lodge1602/unexpected.xml','<TEI xmlns="http://www.tei-c.org/ns/1.0"/>',/Unexpected or missing production XML/,'unexpected XML rejected');
const source='assets/xml/antiquities/English/book-01.xml';
rejection(source,Buffer.concat([fs.readFileSync(path.join(fixture,source)),Buffer.from('corruption')]),/Source XML differs/,'segmented English corruption rejected');
rejection('assets/xml/bellum/English/Lodge1602/book-01.xml','<malformed',/Source XML differs/,'Lodge has no hash exemption');
for(const name of ['preface','book-01','book-03','book-04','book-05','book-06','book-07','book-08','book-09','book-10','book-11','book-12','book-13','book-14','book-15','book-16','book-17','book-18','book-19','book-20']) {
  const relative=`assets/xml/antiquities/English/Lodge1602/${name}.xml`;
  rejection(relative,Buffer.concat([fs.readFileSync(path.join(fixture,relative)),Buffer.from('corruption')]),/Source XML differs/,'Frozen Lodge batch corruption rejected: '+name);
}
rejection('_docs/reader-corpus-integrity.json','{}',/manifest changed/,'manifest alteration rejected');
rejection('assets/data/deh-josephus-concordance.json','{}',/Frozen concordance changed/,'frozen concordance alteration rejected');
rejection('_docs/lodge1602-bellum-integration.json','{}',/Frozen Lodge source manifest changed/,'frozen Lodge authority alteration rejected');
const removed=path.join(fixture,source),saved=fs.readFileSync(removed);fs.unlinkSync(removed);
try { assert.throws(()=>verifyReaderCorpus(fixture,{parse:false}),/Unexpected or missing production XML/);checks.push('missing XML rejected'); }
finally {fs.writeFileSync(removed,saved);}
assert(fs.readFileSync(path.join(root,source)).equals(saved),'Original source untouched by negative tests');
const site=option('--site',null);
if(site) {
  for(const [relative,expected] of Object.entries(corpus.publication)) assert.equal(sha(fs.readFileSync(path.join(site,relative))),sha(expected),'Built frozen authority: '+relative);
  checks.push('all 38 generated frozen publication inputs match literal authority hashes');
}
console.log(JSON.stringify({...corpus.report,negative_tests:checks,source_mutation_tests_use_temporary_copies:true},null,2));
