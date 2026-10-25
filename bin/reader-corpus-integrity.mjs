// Acceptance guards for the reviewed reader corpus, independent of frozen DEH references.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
export const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const manifestSHA = 'd78cdad76b4722782c609a7e02e8db499010fd45431a873f19353739df13fa05';
const frozenSHA = 'c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c';
function files(directory, prefix = 'assets/xml') {
  return fs.readdirSync(directory, {withFileTypes:true}).flatMap(entry => {
    const relative = prefix + '/' + entry.name;
    return entry.isDirectory() ? files(path.join(directory, entry.name), relative)
      : entry.name.endsWith('.xml') ? [relative] : [];
  }).sort();
}
export function verifyReaderCorpus(root, {parse = true, pwsh = 'pwsh'} = {}) {
  const bytes = fs.readFileSync(path.join(root, '_docs/reader-corpus-integrity.json'));
  assert.equal(sha(bytes), manifestSHA, 'Reviewed corpus manifest changed');
  const manifest = JSON.parse(bytes);
  assert.deepEqual(files(path.join(root, 'assets/xml')), Object.keys(manifest.files).sort(), 'Unexpected or missing production XML');
  const checked = {};
  for (const [relative, record] of Object.entries(manifest.files)) {
    const body = fs.readFileSync(path.join(root, relative));
    const actual = sha(body);
    assert(record.allowed_worktree_sha256.includes(actual), 'Source XML differs from reviewed authority: ' + relative);
    checked[relative] = actual;
  }
  const frozenBytes = fs.readFileSync(path.join(root, 'assets/data/deh-josephus-concordance.json'));
  assert.equal(sha(frozenBytes), frozenSHA, 'Frozen concordance changed');
  const frozen = JSON.parse(frozenBytes).canonical_xml_sha256;
  const lodgeBytes = fs.readFileSync(path.join(root, '_docs/lodge1602-bellum-integration.json'));
  assert.equal(sha(lodgeBytes), manifest.lodge_manifest_sha256, 'Frozen Lodge source manifest changed');
  const lodge = JSON.parse(lodgeBytes);
  const publicationHashes = Object.fromEntries(Object.entries(frozen).filter(([relative]) => /^assets\/xml\/(deh|bellum)\//.test(relative)));
  // The concordance remains a frozen historical source. Only the five explicitly
  // adjudicated Pollard v1.1 files supersede its English publication bytes.
  const editorialEnglish = Array.from({length:5}, (_, i) => `assets/xml/deh/English/book-${String(i+1).padStart(2,'0')}.xml`);
  for (const relative of editorialEnglish) {
    const record = manifest.files[relative];
    assert.equal(record.authority_revision, 'deh-pollard-millet-editorial-20261025-v1.1');
    assert(record.previous_authority.allowed_worktree_sha256.includes(frozen[relative]), 'Historical Pollard authority changed');
    publicationHashes[relative] = record.pinned_canonical_sha256;
  }
  for (const book of lodge.books) publicationHashes[`assets/xml/bellum/English/Lodge1602/book-${String(book.book).padStart(2,'0')}.xml`] = book.production_sha256;
  const publication = {};
  for (const [relative, expected] of Object.entries(publicationHashes)) {
    const body = fs.readFileSync(path.join(root, relative));
    const candidate = sha(body) === expected ? body : Buffer.from(body.toString('utf8').replace(/\r?\n/g, '\r\n'));
    assert.equal(sha(candidate), expected, 'Frozen publication authority differs: ' + relative);
    publication[relative] = candidate;
  }
  if (parse) {
    const script = '$ErrorActionPreference="Stop"; $settings=[System.Xml.XmlReaderSettings]::new(); $settings.DtdProcessing=[System.Xml.DtdProcessing]::Prohibit; $settings.XmlResolver=$null; foreach($file in Get-ChildItem -LiteralPath $args[0] -Filter *.xml -Recurse -File) { $reader=[System.Xml.XmlReader]::Create($file.FullName,$settings); try { $doc=[System.Xml.XmlDocument]::new(); $doc.XmlResolver=$null; $doc.Load($reader); if($doc.DocumentElement.NamespaceURI -cne "http://www.tei-c.org/ns/1.0"){throw "Unexpected TEI namespace"} } finally {$reader.Dispose()} }';
    // Use a literal environment path so spaces never become executable shell text.
    execFileSync(pwsh, ['-NoProfile', '-Command', script.replace('$args[0]', '$env:READER_QA_XML_ROOT')],
      {env:{...process.env, READER_QA_XML_ROOT:path.join(root,'assets/xml')}, stdio:'pipe'});
  }
  return {manifest, checked, publication, report:{status:'PASS', production_XML:Object.keys(checked).length,
    all_production_XML_parsed:parse, publication_inputs:Object.keys(publication).length,
    frozen_publication_inputs:Object.keys(publication).length-editorialEnglish.length,
    approved_editorial_revision_inputs:editorialEnglish.length,
    publication_xml_sha256:Object.fromEntries(Object.entries(publication).map(([relative,bytes])=>[relative,sha(bytes)])),
    frozen_concordance_sha256:sha(frozenBytes), manifest_sha256:sha(bytes)}};
}
