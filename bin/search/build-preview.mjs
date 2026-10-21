/** Reuse the canonical Jekyll component in the private standalone preview. */
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const here=new URL('./',import.meta.url);
const component=readFileSync(new URL('../../_includes/search-interface.html',here),'utf8');
const readerBase='https://latinjosephus.github.io/';
const body=component.replaceAll('{{ include.reader_base }}',readerBase);
if(body.includes('{{')||body.includes('{%'))throw new Error('The search component contains unsupported Liquid markup; update the preview builder explicitly.');
const html=`<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta name="description" content="Search the Latin Josephus texts and Whiston English Antiquities I–X with exact phrases, Boolean logic, wildcards, and a concordance.">
  <title>Search preview · Latin Josephus</title>
  <link rel="stylesheet" href="./styles.css">
  <style>
    body{margin:0;background:#faf9f6;color:#262524;padding:0 24px;font-family:system-ui,sans-serif}
    .preview-header{max-width:1080px;margin:auto;padding:24px 0;border-bottom:1px solid #ddd9d1;display:flex;align-items:center;justify-content:space-between;gap:16px}
    .preview-header a{color:#7b2c37;text-decoration:none;font:600 24px Georgia,serif}
    .preview-header span{font-size:12px;color:#65615b}
    @media(max-width:700px){body{padding:0 16px}.preview-header a{font-size:21px}}
  </style>
  <script src="./vendor/lunr.min.js" defer></script>
  <script type="module" src="./app.mjs"></script>
</head>
<body>
  <header class="preview-header"><a href="${readerBase}">Latin Josephus</a><span>Search preview · Latin texts and Whiston English</span></header>
${body}
</body>
</html>
`;
const output=new URL('index.html',here);
writeFileSync(output,html);
console.log(`Wrote ${fileURLToPath(output)} from the canonical search component.`);
