"""Recompute candidate English intervals using XML text events, independently of DOM rendering."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
OLD=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
oracle={(r['book'],r['number']):r for r in json.loads((OLD/'INTERVAL_ORACLE.json').read_bytes())}
rendered={(r['book'],r['number']):r for r in json.loads((OLD/'BROWSER_QA.json').read_bytes())['sections']}
ns='{http://www.tei-c.org/ns/1.0}'
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
rows=[]
for book in json.loads((OLD/'SOURCE_INVENTORY.json').read_bytes()):
  for output in book['outputs']:
    div=ET.parse(ROOT/output['path']).find('.//'+ns+'body/'+ns+'div1')
    text=[];positions=[];offset=[0]
    def emit(s):
      if s:text.append(s);offset[0]+=len(s)
    def walk(el):
      tag=el.tag.removeprefix(ns)
      if tag=='milestone' and el.get('unit')=='niese':positions.append((int(el.get('n')),offset[0]));return
      if tag in ('num','note'):return
      emit(el.text)
      for child in el:walk(child);emit(child.tail)
    walk(div)
    assert [n for n,p in positions]==output['physical_order']
    full=''.join(text);identity='preface' if output['path'].endswith('preface.xml') else str(int(Path(output['path']).stem[-2:]))
    for i,(number,start) in enumerate(positions):
      end=positions[i+1][1] if i+1<len(positions) else offset[0]
      raw=full[start:end];value=' '.join(raw.split());expected=oracle[identity,number];actual=rendered[identity,number]
      assert raw==expected['rawText'] and value==expected['text']
      assert sha(value)==expected['sha256']==actual['renderedSHA256']
      assert value[:100]==actual['opening'] and value[-100:]==actual['closing']
      rows.append({'book':identity,'number':number,'candidate_XML_sha256':sha(value),'certified_rendered_sha256':actual['renderedSHA256'],'opening':value[:100],'closing':value[-100:],'passed':True})
assert len(rows)==3821
(PACK/'CANDIDATE_XML_INTERVAL_QA.json').write_bytes((json.dumps({'status':'PASS','independent_XML_event_intervals':3821,'all_match_certified_actual_display':True,'sections':rows},ensure_ascii=False,indent=2)+'\n').encode())
print('Independently recomputed 3821 candidate XML intervals; all actual display hashes and opening/closing boundaries match')
