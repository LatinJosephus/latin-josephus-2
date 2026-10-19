import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {repositoryRelativeReportPath} from './report-path.mjs';

test('Windows report paths use portable separators and resolve to the original artifacts', () => {
  const root = 'C:\\Project with spaces\\Josephus';
  for (const relative of ['bin/search/corpus.json', 'bin/search/data/book-01.corpus.json',
    'assets/xml/bellum/Latin/book-01.xml', 'bin/search/évidence.json']) {
    const artifact = path.win32.resolve(root, ...relative.split('/'));
    const serialized = repositoryRelativeReportPath(root, artifact, path.win32);
    assert.equal(serialized, relative);
    assert.equal(path.win32.resolve(root, ...serialized.split('/')), artifact);
  }
});

test('POSIX report paths retain exact artifact identity', () => {
  const root = '/Project with spaces/Josephus';
  for (const relative of ['bin/search/corpus.json', 'assets/xml/bellum/Latin/book-01.xml']) {
    const artifact = path.posix.resolve(root, relative);
    const serialized = repositoryRelativeReportPath(root, artifact, path.posix);
    assert.equal(serialized, relative);
    assert.equal(path.posix.resolve(root, serialized), artifact);
  }
});

test('a literal backslash in a POSIX filename is not treated as a directory separator', () => {
  const artifact = '/repository/data/literal\\name.json';
  assert.equal(repositoryRelativeReportPath('/repository', artifact, path.posix),
    'data/literal\\name.json');
});

test('native serialized corpus evidence identifies the exact real file and SHA-256', () => {
  const root = fileURLToPath(new URL('../../../', import.meta.url));
  const artifact = fileURLToPath(new URL('../corpus.json', import.meta.url));
  const originalArgument = artifact;
  const serialized = repositoryRelativeReportPath(root, artifact);
  assert.equal(serialized, 'bin/search/corpus.json');
  const resolved = path.resolve(root, ...serialized.split('/'));
  assert.equal(resolved, path.resolve(artifact));
  const digest = file => createHash('sha256').update(readFileSync(file)).digest('hex');
  assert.equal(digest(resolved), digest(artifact));
  assert.equal(artifact, originalArgument, 'the filesystem argument is never rewritten');
});
