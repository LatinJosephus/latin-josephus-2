from pathlib import Path
from lxml import etree as E
import json,re,hashlib,copy,csv
W=Path(r'C:\workspace\LatinJosephus-source-toc-navigation'); V=W/'review/Source_TOC_Navigation_2026-10-07'; D=Path(__file__).resolve().parent
P=V/'SR-061_Proposal_2026-10-08'; N={'t':'http://www.tei-c.org/ns/1.0'}; T='{'+N['t']+'}'; X='{http://www.w3.org/XML/1998/namespace}'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
before={p.relative_to(W).as_posix():sha(p) for p in W.rglob('*') if p.is_file() and not p.is_relative_to(D)}
if (D/'BEFORE.json').exists():
 assert json.loads((D/'BEFORE.json').read_text(encoding='utf-8'))==before
else: dump(D/'BEFORE.json',before)
archive=D/'prior-effective-metadata';archive.mkdir(exist_ok=True)
mutable=['REPORT.md','QA.json','FILE_MANIFEST.json','SOURCE_AUTHORITY.md','SOURCE_TOC_ELIGIBILITY_2026-10-08.json','SOURCE_TOC_ELIGIBILITY_2026-10-08.csv','VERIFIED_CONTENTS_REGISTRY_2026-10-08.json','CONTENTS_EXPECTATIONS_2026-10-08.json']
for n in mutable:(archive/n).write_bytes((V/n).read_bytes())
proposal=json.loads((P/'SEGMENTATION_PROPOSAL.json').read_text(encoding='utf-8')); rows=proposal['candidates']; source=W/'assets/xml/antiquities/Latin/book-14.xml'; raw=source.read_bytes(); root=E.fromstring(raw); c0=root.xpath('//t:div2[@n="0"]',namespaces=N)[0]
assert sha(source)==proposal['source_inputs']['worktree_latin_xiv']['sha256']
start=raw.index(b'<div2 n="0"'); end=raw.index(b'</div2>',start)+len(b'</div2>'); block=raw[start:end]
rawp=re.findall(rb'<p>(.*?)</p>',block,re.S); assert len(rawp)==19
assert b'<p>'+rawp[3]+b'</p>'==(P/'SOURCE_PARAGRAPH.xml.fragment.txt').read_bytes()
parts=[rawp[0],rawp[1],rawp[2],proposal['held_paragraph']['literal_IIII_prefix_raw_xml'].encode()[3:]]+[r['raw_xml_fragment_utf8'].encode() for r in rows]+rawp[4:]
assert len(parts)==27 and b''.join(parts)==b''.join(rawp)
labels=['I','II','III','IIII']+[r['editorial_label'] for r in rows]+proposal['current_literal_labels'][4:]
header='''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Bamberg Msc.Class.78 Antiquities XIV: source capitula with editorially supplied numerals</title>
        <respStmt xml:id="capitula-reconstruction"><resp>Approval of eight editorial contents divisions and supplied numerals [V]–[XII]</resp><name>Richard M. Pollard, 8 October 2026</name></respStmt>
      </titleStmt>
      <publicationStmt><p>LatinJosephus source paratext; approved editorial segmentation imported 2026-10-08. Contents entries are not narrative navigation identities.</p></publicationStmt>
      <notesStmt><note>The historical T-PEN export has an unexplained 1 after prelio in (historical nonempty extraction line 155). It is absent from the current source XML and has not been inserted or interpreted. That transcription discrepancy remains open.</note></notesStmt>
      <sourceDesc><listBibl>
        <bibl xml:id="bamberg78">Bamberg, Staatsbibliothek, Msc.Class.78. Current encoded contents on images sbb00000114_00330.jpg–sbb00000114_00332.jpg, folios 163v–164v; source position markers retained.</bibl>
        <bibl xml:id="current-transcription">LatinJosephus assets/xml/antiquities/Latin/book-14.xml at base 087c0bf651037d83c5156495836510d250bdcf09. SHA-256 SOURCE_HASH. Whole held paragraph SR-061 SHA-256 0284126a6164f2e4fa20deafa45af2ac8b22a394dc8366600703c0836c882725.</bibl>
        <bibl xml:id="sr061-proposal">SR-061_Proposal_2026-10-08/PROPOSAL.md; SHA-256 PROPOSAL_HASH. Exact incipits, explicits and lossless source slices documented separately.</bibl>
        <bibl xml:id="sr061-editorial-approval">Richard M. Pollard, editorial approval of all eight proposed boundaries, 8 October 2026. [V]–[XII] are modern editorial supplies, not manuscript numerals. The entire transmitted Herodian passage remains within [VII]; [XII] ends at mereretur.; [IX] has no asserted identity with narrative VIIII.</bibl>
      </listBibl></sourceDesc>
    </fileDesc>
    <encodingDesc><editorialDecl><p>Source wording, spelling, punctuation, order, literal numerals and inline apparatus are retained. Eight new supplied elements encode editorial numerals only; they are not Blatt-derived textual supplements. Source image milestones receive unit="image" in this companion to meet TEI validation; their original n values and physical order are unchanged. No narrative paragraph or source identifier has been edited.</p></editorialDecl></encodingDesc>
    <revisionDesc><change when="2026-10-08" who="#capitula-reconstruction">SR-061 contents segmentation editorially resolved after human approval. Original mixed-paragraph source encoding and original review history preserved unchanged; historical export 1 discrepancy remains open.</change></revisionDesc>
  </teiHeader>
  <text><body><div type="contents" subtype="manuscript-capitula" source="#bamberg78 #current-transcription" xml:id="bamberg78-ant-14-contents">
'''.replace('SOURCE_HASH',sha(source)).replace('PROPOSAL_HASH',sha(P/'PROPOSAL.md'))
# Preserve source prefix (image/page/column and literal heading) before the list.
prefix=block.split(b'<p>',1)[0].split(b'>',1)[1].decode('utf-8')
output=header+prefix+'<list type="capitula">\n'
inventory=[]
for i,(label,fragment) in enumerate(zip(labels,parts)):
 supplied=4<=i<12; roman=label.strip('[]'); fid='bamberg78-ant14-contents-'+roman
 editorial=f'<label><supplied reason="not-transmitted" resp="#capitula-reconstruction" source="#sr061-editorial-approval" rend="editorial-numeral">{label}</supplied></label> ' if supplied else ''
 output+=f'<item n="{roman}" xml:id="{fid}">'+editorial+fragment.decode('utf-8')+'</item>\n'
 inventory.append({'order':i+1,'id':fid,'display_label':label,'literal_manuscript_label':None if supplied else label,'label_status':'EDITORIALLY_SUPPLIED_APPROVED' if supplied else 'LITERAL_MANUSCRIPT_NUMERAL','source_fragment_sha256':hashlib.sha256(fragment).hexdigest(),'source_projection':''.join(E.fromstring(b'<audit>'+fragment+b'</audit>').itertext()),'proposal_identity':rows[i-4]['proposal_identity'] if supplied else None})
output+='''</list>
<note type="editorial" resp="#capitula-reconstruction">Numerals [V]–[XII] are supplied by the modern editor; the manuscript contents proceeds from IIII to XIII. The transmitted Herodian passage is retained in its original position within [VII]. These contents divisions are independent of the manuscript's narrative divisions.</note>
</div></body></text></TEI>
'''
comp=E.fromstring(output.encode('utf-8'))
image_milestones=comp.xpath('//t:milestone[not(@unit)]',namespaces=N)
for e in image_milestones:e.set('unit','image')
rngpath=W/'review/Antiquities_Traditional_Navigation_2026-10-06/tei_all.rng'; rng=E.RelaxNG(E.parse(str(rngpath)))
assert rng.validate(comp),str(rng.error_log)
items=comp.xpath('//t:list[@type="capitula"]/t:item',namespaces=N); assert len(items)==27
for i,item in enumerate(items):
 copied=copy.deepcopy(item)
 if 4<=i<12:
  lab=copied.find('t:label',N); assert lab is not None and lab.tail.startswith(' '); copied.text=lab.tail[1:]; copied.remove(lab)
 assert ''.join(copied.itertext())==inventory[i]['source_projection'],i
# Concatenating source fragments reconstructs every source paragraph's contents.
assert ''.join(x['source_projection'] for x in inventory)==''.join(''.join(p.itertext()) for p in c0.findall('t:p',N))
companion=W/'assets/xml/antiquities/paratext/bamberg78/book-14-contents.xml';assert not companion.exists()
companion.write_bytes(E.tostring(comp,xml_declaration=True,encoding='UTF-8',pretty_print=False)+b'\n')
index=W/'assets/xml/source-contents.xml'; idx=E.parse(str(index)); listing=idx.xpath('//t:list[@type="source-contents"]',namespaces=N)[0]; iid='contents-antiquities-bamberg78-14'; assert not idx.xpath('//*[@xml:id=$id]',id=iid,namespaces=N)
new=E.Element(T+'item',{X+'id':iid}); fs=E.SubElement(new,T+'fs',type='source-contents')
record={'id':iid,'work':'antiquities','book':'14','language':'Latin','witness':'bamberg78','status':'VERIFIED','path':'assets/xml/antiquities/paratext/bamberg78/book-14-contents.xml','selectors':['tei-div[type="contents"]'],'note':'','authority':'Current source capitula retained; SR-061 editorial segmentation and supplied numerals [V]–[XII] approved by Richard M. Pollard, 2026-10-08. Narrative divisions are independent; historical export 1 discrepancy remains open.'}
for k,v in record.items():
 if k=='id':continue
 f=E.SubElement(fs,T+'f',name=k)
 if isinstance(v,list):
  coll=E.SubElement(f,T+'vColl',org='list')
  for s in v:E.SubElement(coll,T+'string').text=s
 else:E.SubElement(f,T+'string').text=v
new.tail='\n        ';listing.append(new);assert rng.validate(idx),str(rng.error_log)
index.write_bytes(E.tostring(idx,xml_declaration=True,encoding='UTF-8',pretty_print=False)+b'\n')
records=json.loads((V/'VERIFIED_CONTENTS_REGISTRY_2026-10-08.json').read_text(encoding='utf-8'));records.append(record);assert len(records)==30;dump(V/'VERIFIED_CONTENTS_REGISTRY_2026-10-08.json',records)
expect=json.loads((V/'CONTENTS_EXPECTATIONS_2026-10-08.json').read_text(encoding='utf-8'));expect.append({**record,'texts':[''.join(comp.find('.//t:div',N).itertext())],'supplements':[r['editorial_label'] for r in rows]});dump(V/'CONTENTS_EXPECTATIONS_2026-10-08.json',expect)
elig=json.loads((V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.json').read_text(encoding='utf-8'))
row=next(r for r in elig['rows'] if r['work']=='Antiquities' and int(r['book'])==14 and r['language']=='Latin')
row.update({'source_existence':'VERIFIED_PRESENT','text_verification':'EDITORIALLY_RESOLVED_SEGMENTATION_HUMAN_APPROVED','encoded_availability':True,'publication_eligibility':'ELIGIBLE_APPROVED_EDITORIAL_SEGMENTATION','browser_integration':'PENDING_CURRENT_QA','supplements_present':True,'phase_b_recommendation':'Publish companion contents with eight explicitly supplied editorial numerals; preserve original source encoding and open export discrepancy.','SR061_decision_record':'SR-061_Implementation_2026-10-08/DECISION.md'})
dump(V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.json',elig)
with (V/'SOURCE_TOC_ELIGIBILITY_2026-10-08.csv').open('w',encoding='utf-8',newline='') as f:
 keys=list(dict.fromkeys(k for r in elig['rows'] for k in r));writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in elig['rows'])
dump(D/'ENTRY_INVENTORY.json',inventory)
dump(D/'TRANSCRIPTION_QA.json',{'result':'PASS','entries':27,'literal_manuscript_numerals':19,'editorial_numerals':[r['editorial_label'] for r in rows],'approved_boundaries_matched':8,'full_source_projection_identical_after_excluding_editorial_labels':True,'source_inline_elements_preserved':True,'new_schema_required_image_unit_attributes':len(image_milestones),'canonical_and_worktree_source_XML_writes':0,'narrative_identities_created_or_changed':0,'historical_export_1_status':'UNRESOLVED_UNCHANGED','companion_sha256':sha(companion),'index_before_sha256':before[index.relative_to(W).as_posix()],'index_after_sha256':sha(index),'source_XIV_sha256':sha(source),'schema':{'path':str(rngpath),'sha256':sha(rngpath),'companion':'PASS','contents_index':'PASS'}})
(D/'DECISION.md').write_text('''# SR-061 — approved editorial TOC segmentation

2026-10-08. Richard M. Pollard approved all eight precise boundaries in the unchanged SR-061 proposal. **The TOC segmentation is editorially resolved.** [V]–[XII] are modern supplied numerals, not attested manuscript numerals or Blatt-derived textual supplements.

The complete Herodian passage remains within [VII], ending `obstructis portis romanos excluserunt.` [XII] ends at `mereretur.` [IX] is independent of narrative VIIII. All literal contents numerals and source wording remain unchanged.

The original SR-061 record, proposal and mixed-paragraph source encoding remain unchanged. The historical T-PEN export's extra `1` after `prelio in` remains an open transcription discrepancy; it has not been imported or interpreted. No Bamberg narrative or traditional navigation identity is inferred from these contents entries.

Implementation is confined to a new source-paratext companion and a generic contents registration. The existing reader renderer and styling are unchanged by this amendment. The original 19 labelled source paragraphs yield 27 editorially organized entries: 19 literal numerals plus 8 approved supplied numerals. The complete source projection, inline apparatus and physical markers are preserved. Three source image milestones receive the schema-required unit attribute in the companion only, with their n values and order retained.

Earlier effective report/QA/index expectation metadata are preserved in prior-effective-metadata within this record. Original Phase-A census and the SR-061 proposal are untouched. This decision supersedes the earlier Latin-XIV eligibility hold for contents publication only; it does not rewrite historical records or resolve other transcription questions.
''',encoding='utf-8')
print('PASS: 27 entries, 19 literal numerals, 8 supplied numerals, exact source projection; TEI schema valid.')