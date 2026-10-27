/* Repeatable source/interpretation checks. Browser certification is separate. */
const fs = require('node:fs'), path = require('node:path'), child = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const output = path.join(root, '_docs/annotation-display/qa');
fs.mkdirSync(output, {recursive: true});
const commands = [
  ['generated-freshness', process.env.LJ_PYTHON || 'python', ['-B', 'bin/build-annotation-citations.py', '--check']],
  ['citation-and-preservation', process.env.LJ_PYTHON || 'python', ['-B', '-m', 'unittest', 'discover', '-s', 'bin/annotations', '-p', 'test_*.py', '-v']],
  ['annotation-tests', process.execPath, ['--test', 'bin/annotations/annotation-qa.test.cjs', 'bin/annotations/editorial-english.test.cjs']],
  ['corpus-integrity', process.execPath, ['bin/reader-corpus-qa.mjs']],
  ['deh-integrity', process.execPath, ['bin/deh-parallels-integrity-qa.mjs']],
  ['search-assets', process.execPath, ['bin/search/check-assets.mjs']],
  ['notation-inventory', process.execPath, ['bin/annotations/report-qa.cjs']]
];
const report = {status: 'PASS', commands: []};
for (const [name, executable, args] of commands) {
  const run = child.spawnSync(executable, args, {cwd: root, encoding: 'utf8', timeout: 180000, maxBuffer: 8 * 1024 * 1024});
  fs.writeFileSync(path.join(output, name + '.txt'), ((run.stdout || '') + (run.stderr || '')).replace(/\r\n/g, '\n'));
  const pass = run.status === 0;
  report.commands.push({name, command: [executable === process.execPath ? 'node' : executable, ...args], status: pass ? 'PASS' : 'FAIL'});
  if (!pass) {report.status = 'FAIL'; process.exitCode = 1;}
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name}`);
}
fs.writeFileSync(path.join(output, 'checks.json'), JSON.stringify(report, null, 2) + '\n');
