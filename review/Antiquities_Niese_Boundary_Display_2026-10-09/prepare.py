import hashlib,json,subprocess
from pathlib import Path
from lxml import etree
ROOT=Path('C:/workspace/LatinJosephus-antiquities-niese-boundary-display-20261009')
TASK=Path('C:/workspace/Antiquities-Niese-Boundary-Display-QA-20261009')
PACKET=ROOT/'review/Antiquities_Niese_Boundary_Display_2026-10-09'
BASE='81126ce116045433cb5cf22945cc3711701ac3ca'
SITE=Path('C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009/site')
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not TASK.exists() and not (PACKET/'BASELINE.json').exists()
TASK.mkdir();PACKET.mkdir(exist_ok=True)
assert git('rev-parse','HEAD').decode().strip()==BASE
assert git('diff','--name-only').decode().strip()=='assets/js/renderTei.js'
assert all(p.startswith('review/') for p in git('diff','--name-only','4ccc89a862b63e7ffb8ac7d2c66d1f52a486c512',BASE).decode().splitlines())
inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (ROOT/'assets').rglob('*') if p.is_file()}
old_js=git('show',BASE+':assets/js/renderTei.js')
assert sha((SITE/'assets/js/renderTei.js').read_bytes())==sha(old_js)
for rel in inputs:
    if rel.startswith('assets/xml/'):
        assert sha((SITE/rel).read_bytes())==inputs[rel],rel
record={'base':BASE,'branch':'antiquities-niese-boundary-display','worktree':str(ROOT),'runtime':str(TASK),'baseline_site':str(SITE),'reused_baseline_site_source':'4ccc89a862b63e7ffb8ac7d2c66d1f52a486c512; only review changes to current HEAD','baseline_assets_XML_and_renderer_match_current_source':True,'production_scope':['assets/js/renderTei.js'],'baseline_renderer_sha256':sha(old_js),'candidate_renderer_sha256':inputs['assets/js/renderTei.js'],'assets_pinned':inputs,'XML_pinned':{p:h for p,h in inputs.items() if p.startswith('assets/xml/')}}
(PACKET/'BASELINE.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
ns={'t':'http://www.tei-c.org/ns/1.0'};xml=etree.parse(str(ROOT/'assets/xml/antiquities/Latin/book-10.xml'))
paragraph=xml.xpath('//*[@xml:id="latin-book10-num108"]',namespaces=ns)[0]
label=paragraph.find('t:num',ns);marker=paragraph.find('t:milestone',ns)
raw=(ROOT/'assets/xml/antiquities/Latin/book-10.xml').read_bytes();token=b'<num>[VII.iii.108]</num>';offset=raw.index(token)
origin={'path':'assets/xml/antiquities/Latin/book-10.xml','sha256':sha(raw),'line':label.sourceline,'XML_xpath':'/t:TEI/t:text/t:body/t:div1/t:div2[@n="10"]/t:p[@xml:id="latin-book10-num108"]/t:num','paragraph_ID':paragraph.get('{http://www.w3.org/XML/1998/namespace}id'),'XML_chapter_wrapper_n':paragraph.getparent().get('n'),'traditional_locator':'VII.iii; transmitted label [VII.iii.108]','label':label.text,'label_UTF8_byte_start':offset,'label_UTF8_byte_end_exclusive':offset+len(token),'next_Niese_start':{'unit':marker.get('unit'),'n':marker.get('n'),'text':marker.tail[:180]},'paragraph_opening':etree.tostring(paragraph,encoding='unicode')[:420],'preceding_paragraph_ID':'latin-book10-num103','section107_start':'eo quod','section107_tail':'quae tamen oportunius declarauimus.','section108_Latin':'Explicitly unavailable; no identity or wording change','reason':'Range endpoint is before milestone109, after next paragraph citation label. Its label-only prefix is cloned into107 and retained by paragraph cleanup because it contains tei-num.','preservation':'Original num and its paragraph stay untouched; its suppressed executable claim remains suppressed; chapter/subchapter/alignment display preserved.'}
(PACKET/'XML_ORIGIN.json').write_text(json.dumps(origin,indent=2)+'\n',encoding='utf-8')
(TASK/'task.json').write_text(json.dumps({'root':str(ROOT),'packet':str(PACKET),'base':BASE,'baseline_site':str(SITE)},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'base':BASE,'XML_origin':origin,'XML_assets_unchanged':len(record['XML_pinned'])},indent=2))
