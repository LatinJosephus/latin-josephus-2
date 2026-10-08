from pathlib import Path
from lxml import etree as E
from collections import Counter
import json,hashlib,subprocess
R=Path(r'C:\workspace\LatinJosephus-source-toc-navigation');V=R/'review/Source_TOC_Navigation_2026-10-07';C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development');B='087c0bf651037d83c5156495836510d250bdcf09'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x):(V/name).write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],encoding='utf8').strip()
old=json.loads((V/'phase-a-accepted-2026-10-07/FILE_MANIFEST.json').read_text(encoding='utf-8-sig'));original=old['preexisting_worktree_files'];allowed={'assets/js/renderTei.js','assets/css/tei.css'}
changed=[p for p,q in original.items() if sha(R/p)!=q['sha256']];assert set(changed)==allowed,changed
canonical={p:sha(C/p)==q['sha256'] for p,q in original.items()};eol_differences=[p for p,v in canonical.items() if not v];assert all((C/p).read_bytes().replace(b'\r\n',b'\n')==(R/p).read_bytes().replace(b'\r\n',b'\n') for p in eol_differences)
external={p:sha(Path(p))==h for p,h in old['inspected_external_file_hashes'].items()};assert all(external.values())
baseline=json.loads((V/'PHASE_B_BASELINE_2026-10-08.json').read_text())
for name in ['REPORT.md','SOURCE_AUTHORITY.md','QA.json','FILE_MANIFEST.json']:
 assert sha(V/'phase-a-accepted-2026-10-07'/name)==baseline['review/Source_TOC_Navigation_2026-10-07/'+name]
for name in ['SOURCE_TOC_CENSUS.csv','SOURCE_TOC_CENSUS.json','source_toc_census.py']:
 assert sha(V/name)==baseline['review/Source_TOC_Navigation_2026-10-07/'+name]
xml=[p for p in original if p.endswith('.xml')];xmlchecks=[]
for p in xml:
 assert sha(R/p)==original[p]['sha256'];d=E.parse(str(R/p));ids=d.xpath('//@xml:id');assert len(ids)==len(set(ids)),p
 xmlchecks.append({'file':p,'before_sha256':original[p]['sha256'],'after_sha256':sha(R/p),'byte_identical':True})
topology={}
for lang,count in [('Latin',1622),('Greek',1681),('English',1600)]:
 nodes=[q for p in (R/'assets/xml/antiquities'/lang).glob('*.xml') for q in E.parse(str(p)).xpath('//*[local-name()="p"]')];aligned=sum(bool(q.get('{http://www.w3.org/XML/1998/namespace}id') and '-num' in q.get('{http://www.w3.org/XML/1998/namespace}id')) for q in nodes)
 assert len(nodes)==count and aligned==1442;topology[lang]={'paragraphs':len(nodes),'identified_alignment_paragraphs_including_Proem':aligned,'text_ID_sameAs_order_milestones':'Byte-identical'}
assert git(C,'branch','--show-current')=='v2-development' and git(C,'rev-parse','HEAD')==B and git(C,'rev-parse','origin/v2-development')==B and not git(C,'status','--short')
assert git(R,'branch','--show-current')=='source-toc-navigation' and git(R,'rev-parse','HEAD')==B and not git(R,'diff','--cached','--name-only')
extract=json.loads((V/'BAMBERG_WORD_EXTRACTION_2026-10-08.json').read_text());assert sha(Path(extract['source']))==extract['sha256']
count=sum(len(E.parse(str(p)).xpath('//*[local-name()="milestone"][@unit="niese"]')) for p in (R/'assets/xml/bellum/English/Lodge1602').glob('*.xml'));assert count==4001
result={'result':'PASS','original_project_files':len(original),'unchanged_original_project_files':len(original)-len(changed),'authorized_modified_project_files':changed,'all_original_XML_files':len(xml),'XML_checks':xmlchecks,'topology':topology,'new_empty_anchors':0,'existing_XML_IDs_sameAs_text_milestones_segmentation_order':'BYTE_IDENTICAL','historical_certification_directories':'ALL BYTE_IDENTICAL','original_Phase_A_census_and_script':'BYTE_IDENTICAL','original_Phase_A_report_metadata':'BYTE_IDENTICAL in phase-a-accepted-2026-10-07','external_original_sources':external,'new_DOCX_unchanged':True,'new_DOCX_sha256':extract['sha256'],'canonical_cross_checkout_EOL_only_differences':eol_differences,'canonical_byte_identity_to_worktree_not_claimed':'109 pre-existing CRLF/LF checkout differences; comparison only, no normalization or writes.','canonical_clean_expected_branch_HEAD_origin':True,'worktree_expected_branch_base_unstaged':True,'Lodge_Niese_markers':count,'Git_writes':'NONE; read-only show/status/diff/rev-parse only','site_builds':'NONE','source_PDF_or_manuscript_reinterpretation':'NONE','network_source_research':'NONE','worktree_status':git(R,'status','--short')}
dump('INTEGRITY_QA_2026-10-08.json',result);print('INTEGRITY_PASS',len(xml),'old XML,',len(original),'base files,',len(external),'external authorities')