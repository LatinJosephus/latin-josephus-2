#!/usr/bin/env node
/** Explicitly rebuild and audit the source-derived search assets before committing them. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {
  SOURCE_DIRECTORY, loadPublicationConfig, inside, sourceInputs, unitTestCommands,
  validateSearchSources, validateQaReport, publicationPlan, exportSearchAssets,
} from './publication.mjs';

const root = path.resolve(fileURLToPath(new URL('../../', import.meta.url)));
// The accepted Book XII Git blob itself uses CRLF. Preserve its exact bytes;
// this pin is not permission to regenerate from an arbitrary CRLF checkout.
const acceptedCRLF = new Map([
  ['assets/xml/antiquities/English/book-12.xml', 'e28ce3914fe0e764571e049b20b5ddabfc6d3080cf6dd4537522b083be7cc83c'],
]);

function options(arguments_) {
  const result = {python: process.env.SEARCH_PYTHON || 'python3', forceQA: false};
  for (let i = 0; i < arguments_.length; i++) {
    const flag = arguments_[i];
    if (flag === '--force-qa') result.forceQA = true;
    else if (flag === '--python' || flag === '--expected-reader-sha256') {
      assert(arguments_[i + 1] && !arguments_[i + 1].startsWith('--'), `${flag} needs a value`);
      if (flag === '--python') result.python = arguments_[++i];
      else {
        result.expectedReaderSHA256 = arguments_[++i];
        assert(/^[a-f0-9]{64}$/u.test(result.expectedReaderSHA256), 'Expected reader hash must be 64 lowercase hex characters');
      }
    } else throw new Error(`Unknown option: ${flag}`);
  }
  return result;
}

async function run(runtime, arguments_, label) {
  process.stdout.write(`Search build: ${label}\n`);
  await new Promise((resolve, reject) => {
    const child = spawn(runtime, arguments_, {cwd: root, stdio: 'inherit'});
    child.once('error', reject);
    child.once('exit', (code, signal) => code === 0 ? resolve() :
      reject(new Error(`${label} failed (${signal || `exit ${code}`})`)));
  });
}

async function main() {
  const args = options(process.argv.slice(2));
  const initial = sourceInputs(root);
  const {base, collections} = loadPublicationConfig(root);
  for (const relative of collections.flatMap(c => c.adapter.sources)) {
    const bytes = fs.readFileSync(inside(root, relative));
    // Accepted registry JSON can itself contain CRLF; its normalized content
    // is pinned without rewriting the canonical source file.
    const acceptedSource = acceptedCRLF.get(relative) === createHash('sha256').update(bytes).digest('hex');
    assert(!relative.endsWith('.xml') || !bytes.includes(Buffer.from('\r\n')) || acceptedSource,
      `Source rebuilds require a clean LF checkout: ${relative} contains CRLF. Use an isolated clone with core.autocrlf=false; no files have been written.`);
  }
  const extractionRuns = new Set();
  for (const {manifest, adapter} of collections) {
    const key = `${adapter.extractor}\0${adapter.outputDirectory}`;
    if (extractionRuns.has(key)) continue;
    extractionRuns.add(key);
    await run(args.python, [inside(base, adapter.extractor), '--source-root', root,
      '--output-dir', inside(base, adapter.outputDirectory, {directory: true})], `extract ${manifest.id}`);
  }
  await run(process.execPath, [`${SOURCE_DIRECTORY}/build-index.mjs`], 'build collection indexes');
  const validation = validateSearchSources(root, {qa: false});
  const qaRuns = [];
  for (const configured of validation.collections) {
    const collection = validation.catalog.collections.find(c => c.id === configured.manifest.id);
    const report = JSON.parse(fs.readFileSync(inside(base, collection.extractionReportPath), 'utf8'));
    let fresh = false;
    if (!args.forceQA && !args.expectedReaderSHA256) {
      try {
        validateQaReport(root, {catalog: validation.catalog, collection, configured, report});
        fresh = true;
      } catch (error) {
        process.stdout.write(`Search build: independent QA needs a current run (${error.message.split('\n')[0]}).\n`);
      }
    }
    if (fresh) process.stdout.write(`Search build: reuse current PASS independent QA for ${collection.id}.\n`);
    else {
      const parameters = [`${SOURCE_DIRECTORY}/${configured.adapter.verifier}`];
      if (args.expectedReaderSHA256) parameters.push('--expected-reader-sha256', args.expectedReaderSHA256);
      await run(process.execPath, parameters, `independent corpus QA for ${collection.id}`);
    }
    qaRuns.push({collection: collection.id, reusedCurrentReport: fresh});
  }
  // Publication fixtures use the current independently audited inputs in isolated temporary copies.
  for (const test of unitTestCommands(root)) {
    await run(test.runtime === 'python3' ? args.python : process.execPath, test.arguments,
      `${test.runtime} unit tests`);
  }
  assert.deepEqual(sourceInputs(root), initial, 'A search source changed during the build. Rebuild after source edits finish.');
  const plan = publicationPlan(root);
  const exported = exportSearchAssets(root, plan);
  process.stdout.write(JSON.stringify({...exported, independentQA: qaRuns,
    nextStep: 'Review and commit the source and assets/search changes together; bin/cibuild verifies freshness.'}, null, 2) + '\n');
}

try { await main(); }
catch (error) {
  process.stderr.write(`Search build refused: ${error.message}\n`);
  process.exitCode = 1;
}
