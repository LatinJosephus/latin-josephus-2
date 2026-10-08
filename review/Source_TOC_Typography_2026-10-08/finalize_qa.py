import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
R=Path(__file__).resolve().parent
CAN=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
OLD=Path(r'C:\workspace\LatinJosephus-source-toc-navigation')
BASE='1cf003beeb03f7b0acf2c42057ace062cdb7ebff'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(p,*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=p,text=True).strip()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
b=json.loads((R/'BASELINE.json').read_text());q=json.loads((R/'BROWSER_QA.json').read_text())
assert q['result']=='PASS' and q['contents_scenarios']==16 and q['ordinary_unchanged_comparisons']==16
assert git(CAN,'rev-parse','HEAD')==git(CAN,'rev-parse','origin/v2-development')==BASE
assert git(CAN,'branch','--show-current')=='v2-development' and git(CAN,'status','--porcelain=v1')==''
assert git(ROOT,'rev-parse','HEAD')==BASE and git(ROOT,'branch','--show-current')=='codex/source-toc-typography'
assert git(ROOT,'diff','--cached','--name-only')=='' and git(ROOT,'diff','--name-only')=='assets/css/tei.css'
changed=[f for f,h in b['worktree_files'].items() if sha(ROOT/f)!=h]
can_changed=[f for f,h in b['canonical_files'].items() if sha(CAN/f)!=h]
assert changed==['assets/css/tei.css'] and can_changed==[],(changed,can_changed)
assert git(OLD,'status','--porcelain=v1')==b['completed_TOC_worktree_status']==''
assert sha(OLD/'assets/css/tei.css')==b['completed_TOC_worktree_CSS']
assert sha(Path(b['compiled_main_css_path']))==b['compiled_main_css_sha256']
before=(R/'BEFORE_tei.css').read_bytes();after=(ROOT/'assets/css/tei.css').read_bytes()
addition=b'.source-contents {\n  font-family: var(--lj-font-text);\n}\n'
assert after.count(addition)==1 and after.replace(addition,b'',1)==before
assert sha(R/'BEFORE_tei.css')==b['worktree_files']['assets/css/tei.css']
records=[];counts={};contrast=[]
def luminance(s):
 c=[float(x)/255 for x in re.findall(r'[\d.]+',s)[:3]]
 return sum(y*w for y,w in zip([x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c],[.2126,.7152,.0722]))
for s in q['snapshots']:
 for lang,d in s['languages'].items():
  for role,v in d['samples'].items():
   if v:records.append(dict(case=s['case'],theme=s['theme'],version=s['version'],language=lang,role=role,tag=v['tag'],text=v['text'],computed=v['styles'],actual_fonts=v['platformFonts']))
  if s['version']=='after':
   a=luminance(d['samples']['entry']['styles']['color']);z=luminance(d['background'])
   contrast.append(dict(case=s['case'],language=lang,theme=s['theme'],foreground=d['samples']['entry']['styles']['color'],background=d['background'],ratio=round((max(a,z)+.05)/(min(a,z)+.05),2)))
   if s['theme']=='light':counts[s['case']+'/'+lang]=len(d['italicSpans'])
assert min(c['ratio'] for c in contrast)>=4.5
assert any(f['postScriptName']=='Coelacanth-It' for x in records if x['version']=='after' and x['role']=='italic' for f in x['actual_fonts'])
write('COMPUTED_FONTS.json',records)
xml=[f for f in b['worktree_files'] if f.endswith('.xml')];fonts=[f for f in b['worktree_files'] if f.startswith('assets/fonts/')];history=[f for f in b['worktree_files'] if f.startswith('review/')]
source=dict(path='assets/css/tei.css',before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest(),before_bytes=len(before),after_bytes=len(after),lines_added=3)
integrity=dict(tracked_baseline=len(b['worktree_files']),modified_tracked_files=changed,other_tracked_files_byte_identical=len(b['worktree_files'])-1,XML_files_unchanged=len(xml),font_files_unchanged=len(fonts),historical_review_files_unchanged=len(history),canonical_files_byte_identical=len(b['canonical_files']),canonical_clean=True,completed_TOC_worktree_clean=True,compiled_main_CSS_unchanged=True,JS_XML_registry_Sass_templates_unchanged=True,IDs_sameAs_text_segmentation_unchanged=True,font_loading_unchanged=True,no_site_build=True,no_staging_commit_merge_push_or_Git_config_change=True)
result=dict(result='PASS',date='2026-10-08',base_commit=BASE,branch='codex/source-toc-typography',worktree=str(ROOT),changed_file=source,integrity=integrity,browser=dict(contents_scenarios=16,before_after_pairs=8,ordinary_view_comparisons=16,ordinary_pixel_identical_comparisons=sum(x['screenshotHashEqual'] for x in q['ordinary']),themes=['light','dark'],viewport='1600 x 1050',font_stack_matches_narrative=True,actual_regular_and_italic_Coelacanth_confirmed=True,italic_nodes_by_display=counts,source_text_equal=True,preserved_style_properties=['fontStyle','fontWeight','fontSize','lineHeight','letterSpacing','wordSpacing','textIndent','textAlign','marginTop','marginBottom','marginLeft','paddingLeft','color','backgroundColor'],overflow=False,page_errors=q['pageErrors'],failed_requests=q['requestFailures'],contrast=contrast,test_environment=q['test_environment']),recommendation='GO for human browser review. Unstaged and uncommitted.')
write('QA.json',result)
rows=[]
for s in q['snapshots']:
 if s['version']=='after' and s['theme']=='light':
  for lang,d in s['languages'].items():
   old=next(x for x in q['snapshots'] if x['case']==s['case'] and x['version']=='before' and x['theme']=='light')['languages'][lang]
   normal=next(x for x in q['ordinary'] if x['case']==s['case'] and x['theme']=='light' and x['view']=='chapter')['computed']['languages'][lang]['styles']['fontFamily']
   rows.append('| '+s['case']+' / '+lang+' | `'+old['samples']['entry']['styles']['fontFamily']+'` | `'+d['samples']['entry']['styles']['fontFamily']+'` | `'+normal+'` |')
report=f'''# Source TOC typography refinement — 8 October 2026

GO for human browser review. The production patch adds three lines to `assets/css/tei.css`. All other {len(b['worktree_files'])-1} tracked files remain byte-identical to the worktree baseline.

## Isolation and cause

Base: `{BASE}`. Branch: `codex/source-toc-typography`. Worktree: `{ROOT}`. Canonical `v2-development` and `origin/v2-development` still equal the base, and canonical is clean. The completed TOC worktree and historical reviews remain unchanged.

`_sass/_typography.scss` registers existing local regular, italic and bold fonts as `"LJ Coelacanth"` and defines `--lj-font-text: "LJ Coelacanth", Georgia, "Times New Roman", serif`. Ordinary `tei-p` and `tei-head` explicitly use that stack. Greek narrative uses this same existing stack and its Unicode fallbacks; no separate Greek-only font is registered.

The book layout loads MDB after the main stylesheet. MDB sets the body font to `Roboto, sans-serif`. Contents fragments sit outside `tei-text`, so list entries and Lodge TCP headings inherited this sans-serif body font. Some TEI paragraphs/headings already had the explicit reader-font rule, producing mixed typography.

## Scoped correction

```css
.source-contents {{
  font-family: var(--lj-font-text);
}}
```

This sets the existing reader font on the contents wrapper and its inheriting descendants. No font files, font loading, JavaScript, XML, registry, source numeral, ID, sameAs, segmentation, Sass, template or navigation code changed. Existing italic selectors remain untouched; Chrome confirms the actual `Coelacanth-It` face for supplied passages.

Only font family is set. Font sizes, spacing, indentation, weights, colours and theme behaviour are preserved. Different line wrapping follows naturally from the requested typeface; no extra layout adjustment was required.

## Computed fonts

Full computed styles and actual platform-font records for representative source headings, entries, numerals and supplements are in `COMPUTED_FONTS.json` and `BROWSER_QA.json`. The following entry samples are representative. Both themes produce the same font families.

| Source sample | Before | After | Ordinary Chapter text |
| --- | --- | --- | --- |
{chr(10).join(rows)}

Latin III/XIV TEI headings already used Coelacanth. Lodge's source heading changes from Roboto to Coelacanth. Greek source headings are first paragraphs, and their existing reading stack remains unchanged. Source numerals inherit the reader stack. Latin III's {counts['antiquities-III/Latin']} italic nodes and XIV's {counts['antiquities-XIV/Latin']} supplied numeral nodes remain italic in both themes. These are display-node counts, not a fresh source adjudication; XIV editorial numerals remain distinct from Blatt supplements. Latin/English contents keep 16px text and Greek paragraphs keep 18px.

## QA

- 16/16 contents scenarios pass: the four requested cases, in light and dark themes, before and after; eight before/after pairs. Antiquities V/XIV include Latin and Greek checks.
- 16/16 ordinary Book/Chapter comparisons pass: exact pane HTML, text, computed styles, actual font usage and navigation-control fonts match. {result['browser']['ordinary_pixel_identical_comparisons']}/16 final visible reading-area pixel hashes also match.
- Source contents text is identical. Genuine italics and Blatt supplements remain visibly distinguished; XIV supplied numerals retain brackets.
- All eight final after views were visually inspected. No horizontal overflow or illegible text was observed at 1600 x 1050. Colours are unchanged; measured entry contrast ranges from {min(x['ratio'] for x in contrast):.2f}:1 to {max(x['ratio'] for x in contrast):.2f}:1, exceeding WCAG AA's 4.5:1 normal-text threshold.
- No browser page errors or failed requests in the final run.
- All {len(xml)} XML files, {len(fonts)} font assets and {len(history)} historical review files are byte-identical. All {len(b['canonical_files'])} canonical tracked files match their own preflight hashes.

The reproducible browser test uses the actual renderer and XML in a local fixture with the existing compiled main stylesheet, local fonts and the existing layout's MDB/Roboto URLs. It compares the exact before stylesheet against the patched stylesheet. Readiness/state instrumentation is in memory only. No site build or deployment was performed. Initial fixture diagnostics are preserved separately; final results are in `BROWSER_QA.json`.

## Before/after screenshots

| Case | Light | Dark |
| --- | --- | --- |
| Antiquities III | [Before](antiquities-III_light_before.png) · [After](antiquities-III_light_after.png) | [Before](antiquities-III_dark_before.png) · [After](antiquities-III_dark_after.png) |
| Antiquities V | [Before](antiquities-V_light_before.png) · [After](antiquities-V_light_after.png) | [Before](antiquities-V_dark_before.png) · [After](antiquities-V_dark_after.png) |
| Antiquities XIV | [Before](antiquities-XIV_light_before.png) · [After](antiquities-XIV_light_after.png) | [Before](antiquities-XIV_dark_before.png) · [After](antiquities-XIV_dark_after.png) |
| Bellum I, Lodge | [Before](bellum-Lodge-I_light_before.png) · [After](bellum-Lodge-I_light_after.png) | [Before](bellum-Lodge-I_dark_before.png) · [After](bellum-Lodge-I_dark_after.png) |

## Changed-file SHA-256

`assets/css/tei.css`:

- Before: `{source['before_sha256']}` ({len(before):,} bytes).
- After: `{source['after_sha256']}` ({len(after):,} bytes).

`FILE_MANIFEST.json` hashes the production edit and all new review artifacts except itself. Changes remain unstaged and uncommitted. No merge, push or Git configuration change occurred.
'''
(R/'REPORT.md').write_text(report,encoding='utf-8',newline='\n')
write('FILE_MANIFEST.json',dict(base_commit=BASE,worktree=str(ROOT),source_changes=[source],new_review_files=[dict(path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(R.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json'],self_exclusion='Manifest excludes itself to avoid recursive hashing.',protected_integrity=integrity))
print(json.dumps(dict(result='PASS',source_change=source,integrity=integrity,review=str(R)),indent=2))
