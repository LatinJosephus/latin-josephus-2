#!/usr/bin/env node
// Exact serialization acceptance and corruption rejection; production XML is read-only.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyReaderCorpus,sha} from './reader-corpus-integrity.mjs';
import {createTextLoader,loadConcordance,sources,sourceIntegrityPolicy} from '../assets/js/dehParallelsCore.js';
const root=fileURLToPath(new URL('../',import.meta.url));
const corpus=verifyReaderCorpus(root);
const frozenBytes=fs.readFileSync(path.join(root,'assets/data/deh-josephus-concordance.json'));
const frozen=JSON.parse(frozenBytes), checks=[];
// Stubs stop after byte verification: this guard does not emulate XML extraction.
globalThis.CETEI=class {domToHTML5(xml){return xml;}};
globalThis.DOMParser=class {parseFromString(text){return {text,querySelector(){return null;}};}};
const originalFetch=globalThis.fetch;
async function load(source,book,body,hashes=frozen.canonical_xml_sha256){
 globalThis.fetch=async()=>new Response(body);
 return createTextLoader(new URL('https://fixture.invalid/assets/xml/'),hashes)(source,book);
}
try {
 assert.equal(sourceIntegrityPolicy,'reviewed-crlf-or-exact-lf-v1');
 for(const [source,identity] of Object.entries(sources))for(let book=1;book<=(identity.work==='deh'?5:7);book++){
  const relative=`assets/xml/${identity.work}/${identity.language}/book-${String(book).padStart(2,'0')}.xml`;
  const literal=corpus.publication[relative],lf=Buffer.from(literal.toString('utf8').replace(/\r\n/g,'\n'));
  assert.equal(sha(literal),frozen.canonical_xml_sha256[relative]);
  assert(!lf.includes(13));assert(!literal.equals(lf),'Fixture lacks nonvacuous line-ending difference');
  const original=await load(source,book,literal),checkout=await load(source,book,lf);
  assert.equal(checkout.text.replace(/\n/g,'\r\n'),original.text);
  checks.push({source,book,relative,reviewed_sha256:sha(literal),LF_sha256:sha(lf),literal_accepted:true,LF_accepted:true});
  const changedText=Buffer.from(lf.toString().replace(/<body>/,'<body>corruption'));
  const changedId=Buffer.from(lf.toString().replace('xml:id=','xml:id="changed" old-id='));
  const mutations=[['text',changedText],['IDs',changedId],['extra whitespace',Buffer.concat([lf,Buffer.from(' ')])],
   ['BOM',Buffer.concat([Buffer.from([239,187,191]),lf])],['truncation',lf.subarray(0,lf.length-1)],
   ['mixed line endings',Buffer.from(lf.toString().replace('\n','\r\n'))],['bare CR',Buffer.concat([lf,Buffer.from('\r')])]];
  for(const [label,bytes] of mutations){assert(!bytes.equals(lf),'Vacuous mutation: '+label);await assert.rejects(load(source,book,bytes),/differs from the frozen reviewed authority/);}
  await assert.rejects(load(source,book,lf,{}),/differs from the frozen reviewed authority/);
  await assert.rejects(load(source,book,lf,{...frozen.canonical_xml_sha256,[relative]:'0'.repeat(64)}),/differs from the frozen reviewed authority/);
  checks.at(-1).rejected_mutations=mutations.map(([label])=>label).concat('missing hash','wrong hash');
 }
 const changedConcordance=Buffer.from(frozenBytes.toString().replace(/\r?\n/g,'\r\n'));
 globalThis.fetch=async()=>new Response(changedConcordance);
 // Concordance remains literal-byte-only, even when XML line-ending acceptance is enabled.
 assert.notEqual(sha(changedConcordance),sha(frozenBytes));
 await assert.rejects(loadConcordance('https://fixture.invalid/concordance'),/differs from the frozen reviewed authority/);
 const literal=corpus.publication['assets/xml/deh/Latin/book-01.xml'];
 let response=new Response('corrupt');globalThis.fetch=async()=>response;
 const retry=createTextLoader(new URL('https://fixture.invalid/assets/xml/'),frozen.canonical_xml_sha256);
 await assert.rejects(retry('ussani',1),/differs from the frozen reviewed authority/);
 response=new Response(literal);assert.equal((await retry('ussani',1)).text,literal.toString());
 globalThis.fetch=async()=>new Response('not found',{status:404});
 await assert.rejects(createTextLoader(new URL('https://fixture.invalid/assets/xml/'),frozen.canonical_xml_sha256)('ussani',1),/Could not load ussani Book 1/);
 console.log(JSON.stringify({status:'PASS',policy:sourceIntegrityPolicy,sources:checks.length,accepted:checks.length*2,
  rejected_source_mutations:checks.length*9,concordance_serialization_change_rejected:true,failed_cache_entry_evicted:true,HTTP_failure_rejected:true,checks},null,2));
}finally{globalThis.fetch=originalFetch;}
