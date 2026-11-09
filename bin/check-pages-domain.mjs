import { execFileSync } from 'node:child_process';

const domain = 'www.latinjosephus.org';
const [checkout, commit] = process.argv.slice(2);

try {
  if (process.argv.length !== 4 || !/^[0-9a-f]{40}$/.test(commit)) {
    throw new Error('Usage: node bin/check-pages-domain.mjs <Pages checkout> <full commit SHA>');
  }

  const git = (...args) => execFileSync('git', ['-C', checkout, ...args], {
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  if (git('cat-file', '-t', commit).toString().trim() !== 'commit') {
    throw new Error('The Pages candidate must be a commit.');
  }

  for (const file of ['CNAME', '.nojekyll']) {
    const entry = git('ls-tree', commit, '--', file).toString();
    if (!/^100(?:644|755) blob /.test(entry)) {
      throw new Error(`The Pages commit needs a regular file named ${file} at its root.`);
    }
  }
  if (!git('cat-file', 'blob', `${commit}:CNAME`).equals(Buffer.from(domain))) {
    throw new Error(`CNAME must contain exactly ${domain}.`);
  }

  console.log(`Pages domain check passed for ${commit}.`);
} catch (error) {
  console.error(`Publication stopped. ${error.message}`);
  process.exitCode = 1;
}
