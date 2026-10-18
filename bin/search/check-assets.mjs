#!/usr/bin/env node
/** Read-only source/export gate; --site additionally checks Jekyll's generated publication. */
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifySearchAssets} from './publication.mjs';

const root = path.resolve(fileURLToPath(new URL('../../', import.meta.url)));
try {
  const arguments_ = process.argv.slice(2);
  let site;
  if (arguments_.length) {
    assert(arguments_.length === 2 && arguments_[0] === '--site', 'Usage: node bin/search/check-assets.mjs [--site <directory>]');
    site = path.resolve(arguments_[1]);
  }
  console.log(JSON.stringify(verifySearchAssets(root, {site}), null, 2));
} catch (error) {
  console.error(`Search publication refused: ${error.message.split('\n')[0]}`);
  console.error('Run node bin/search/build-search.mjs after reviewing source changes; commit generated assets with their sources.');
  process.exitCode = 1;
}
