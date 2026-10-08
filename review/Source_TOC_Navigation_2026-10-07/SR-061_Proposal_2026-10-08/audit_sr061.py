"""Read-only SR-061 audit; --create writes only this separate proposal directory.
Recheck with bundled Python -B audit_sr061.py --verify. No Git write operations.
"""
from pathlib import Path
from lxml import etree
import csv, hashlib, io, json, re, subprocess, sys
W=Path(r'C:\workspace\LatinJosephus-source-toc-navigation')
C=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
R=Path(r'C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review')
D=Path(__file__).resolve().parent
OLD=R/'Antiquities_source_review_reconciliation_2026-09-28'
FROZEN=R/'Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06'
NS={'t':'http://www.tei-c.org/ns/1.0'}
BASE='087c0bf651037d83c5156495836510d250bdcf09'
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(p): return sha(p.read_bytes())
def git(root,*args):
 return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],text=True).strip()
def state():
 return {'canonical':{'branch':git(C,'branch','--show-current'),'head':git(C,'rev-parse','HEAD'),'origin':git(C,'rev-parse','origin/v2-development'),'status':git(C,'status','--short')},'worktree':{'branch':git(W,'branch','--show-current'),'head':git(W,'rev-parse','HEAD'),'status':git(W,'status','--short')}}
def snapshot():
 result={}
 for p in W.rglob('*'):
  if p.is_file() and not p.is_relative_to(D): result[str(p)]=digest(p)
 for folder in [OLD,FROZEN]:
  for p in folder.rglob('*'):
   if p.is_file(): result[str(p)]=digest(p)
 p=C/'assets/xml/antiquities/Latin/book-14.xml'; result[str(p)]=digest(p)
 return result
if '--seal' in sys.argv:
 baseline=json.loads((D/'INTEGRITY_BASELINE.json').read_text(encoding='utf-8'))
 current=snapshot(); assert current==baseline['pre_existing_files_sha256'],'Pre-existing file change detected'
 current_repo=state(); assert current_repo==baseline['repository_state_before'],'Repository state changed'
 qa=json.loads((D/'QA.json').read_text(encoding='utf-8'))
 qa.update({'pre_existing_files_byte_identical':len(current),'new_files_outside_proposal_directory':0,'original_review_history_unchanged':True,'prior_Phase_A_and_Phase_B_review_material_unchanged':True,'canonical_repository_clean':True,'repository_state_after':current_repo,'new_review_files_only':True})
 (D/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 manifest={'scope':'Separate SR-061 proposal only; no implementation','manifest_excludes_itself':True,'pre_existing_files_sha256':current,'proposal_files_sha256':{p.name:digest(p) for p in sorted(D.iterdir()) if p.is_file() and p.name!='FILE_MANIFEST.json'}}
 (D/'FILE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'seal':'PASS','pre_existing_files_unchanged':len(current),'proposal_files':len(manifest['proposal_files_sha256'])+1},indent=2))
 sys.exit()
if '--verify' in sys.argv:
 manifest=json.loads((D/'FILE_MANIFEST.json').read_text(encoding='utf-8'))
 failures=[p for p,h in manifest['pre_existing_files_sha256'].items() if not Path(p).is_file() or digest(Path(p))!=h]
 failures += [str(D/p) for p,h in manifest['proposal_files_sha256'].items() if not (D/p).is_file() or digest(D/p)!=h]
 assert not failures,failures
 print(json.dumps({'verification':'PASS','pre_existing_files_verified':len(manifest['pre_existing_files_sha256']),'proposal_files_verified':len(manifest['proposal_files_sha256']),'repository_state':state()},indent=2))
 sys.exit()
assert '--create' in sys.argv
assert [p.name for p in D.iterdir()]==['audit_sr061.py'],'Refusing to overwrite an existing proposal'
before=snapshot(); repo=state()
assert repo['canonical']=={'branch':'v2-development','head':BASE,'origin':BASE,'status':''},repo
assert repo['worktree']['branch']=='source-toc-navigation' and repo['worktree']['head']==BASE,repo
source=W/'assets/xml/antiquities/Latin/book-14.xml'; raw=source.read_bytes(); tree=etree.fromstring(raw)
chapter=tree.xpath('//t:div2[@n="0"]',namespaces=NS)[0]
paragraphs=chapter.findall('t:p',NS); held=paragraphs[3]; text=''.join(held.itertext())
a=raw.index(b'<p>IIII Qualiter'); z=raw.index(b'</p>',a)+4; held_raw=raw[a:z]
case=next(x for x in json.loads((OLD/'source_review_queue.json').read_text(encoding='utf-8-sig')) if x['case_id']=='SR-061')
assert sha(held_raw)==case['paragraph_sha256']=='0284126a6164f2e4fa20deafa45af2ac8b22a394dc8366600703c0836c882725'
assert case['exact_variants'][0]['exact'].encode()==held_raw
packet=(OLD/'SOURCE_REVIEW_PACKET.md').read_text(encoding='utf-8-sig')
case_md=packet.split('### SR-061 — B14-C0-P4',1)[1].split('\n## Book ',1)[0]
export=case_md.split('T-PEN passage:\n\n> ',1)[1].split('\n\n',1)[0]
export_lines={int(n):s for n,s in re.findall(r'(\d+):(.*?)(?= \| \d+:|$)',export)}
assert export_lines[77].startswith('De pompeio') and export_lines[157].startswith('Quemadmodum cum flexisset')
assert export_lines[155].endswith('in 1') and 'prelio in 1' not in text
frozen_manifest=FROZEN/'Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt'
frozen_checks=[]
for line in frozen_manifest.read_text(encoding='utf-8-sig').splitlines():
 h,name=line.split('  ',1); frozen_checks.append({'path':name,'sha256':digest(FROZEN/name),'pass':digest(FROZEN/name)==h})
assert len(frozen_checks)==8 and all(x['pass'] for x in frozen_checks)
map_path=FROZEN/'Antiquities_Bamberg_Niese_Map.csv'
all_bamberg=list(csv.DictReader(map_path.open(encoding='utf-8-sig',newline='')))
b14=[x for x in all_bamberg if x['book']=='14']; assert len(b14)==27 and len(all_bamberg)==198
registry=etree.parse(str(W/'assets/xml/antiquities/structure.xml'))
assert len(registry.xpath('//t:list[@type="bamberg-boundaries"]/t:item',namespaces=NS))==198
openings=[
 ('V','De pompeio qui cum ab armenia uenisset in damascu',77,80),
 ('VI','Quemadmodum aristobolus cum intellexisset pompei consilium',81,86),
 ('VII','Quemadmodum aristobolus cum hic timore fecisset',87,138),
 ('VIII','Qualiter irritatus pompeius aristobolum ligauit',139,143),
 ('IX','De modestia eius et religiositate',144,148),
 ('X','De scauro qui cum militiam contra petram',149,152),
 ('XI','Quemadmodum aristoboli filius alexander fugiens pompeium',153,156),
 ('XII','Quemadmodum cum flexisset alexandrum matre sua',157,160)]
positions=[text.index(s) for _,s,_,_ in openings]+[len(text)]
raw_positions=[held_raw.index(s.encode()) for _,s,_,_ in openings]+[len(held_raw)-4]
assert positions==sorted(positions) and all(text.count(s)==1 for _,s,_,_ in openings)
comparison_notes=[
 'The contents starts with Pompey arriving at Damascus; current narrative num34 already describes that arrival, before audited Bamberg V (Niese 38). The related topic is broader than the narrative division edge.',
 'Narrative VI opens with Aristobolus leaving Pompey (Niese 47); this contents summary also includes the ensuing pursuit and castle instructions. Thematic correspondence does not certify identical boundaries.',
 'The contents opens with compliance with the castle instructions and distress; audited narrative [VII] begins later at Discedens autem (Niese 52). Preserve the entire Herodian passage and the return to the siege account inside this proposed contents span.',
 'Related narrative [VIII] opens with Pompey imprisoning Aristobolus (Niese 57). The summary is thematically parallel; the frozen narrative label is supplied [VIII], not evidence of a contents numeral.',
 'Narrative label is VIIII, not IX; its start is Quas pompeius (Niese 72). [IX] is the requested editorial contents label only, with no alteration of the literal narrative numeral.',
 'Narrative X opens with Scaurus against Petra (Niese 80). This supports the topic sequence, not a source-authorized TOC-to-navigation link.',
 'Narrative XI opens with Alexander, son of Aristobolus (Niese 82). The contents preserves its own summary wording and boundaries.',
 'Narrative XII (Niese 89) concerns the siege, surrender and Alexanders mother; the release of the other sons by the senate is narrated at the end of current narrative XIII (num92). Thus the proposed contents XII summary anticipates material in narrative XIII; do not truncate or relocate it.'
]
records=[]; comparisons=[]
for i,(label,opening,first,last) in enumerate(openings):
 begin,end=positions[i:i+2]; rb,re_=raw_positions[i:i+2]; fragment=held_raw[rb:re_]; segment=text[begin:end]
 # Each cut is a text/tail position outside inline elements; all fragments retain balanced markup.
 wrapped=etree.fromstring(b'<audit>'+fragment+b'</audit>')
 assert ''.join(wrapped.itertext())==segment
 assert export_lines[first].startswith(opening) or opening.startswith(export_lines[first])
 assert export_lines[last].rstrip().endswith(segment.rstrip().split('.')[-2].split()[-1]+'.') or label in ['XI']
 prose=segment.rstrip(); closing=' '.join(prose.split()[-14:])
 entry=b14[i+4]
 note=comparison_notes[i]
 if label=='XI': note+=' Export line 155 has an extra 1 after prelio in. It remains a separately recorded transcription question; this proposal preserves current XML without importing that character.'
 record={'proposal_identity':f'SR-061-proposed-{label}','editorial_label':f'[{label}]','label_status':'PROPOSED_EDITORIAL_SUPPLY_NOT_ATTESTED_NUMERAL','approval_status':'AWAITING_HUMAN_APPROVAL','incipit':opening,'explicit':closing,'full_transcription_projection':segment,'raw_xml_fragment_utf8':fragment.decode('utf-8'),'projection_start_0_based':begin,'projection_content_end_exclusive_0_based':begin+len(prose),'projection_preservation_end_exclusive_0_based':end,'source_xml_byte_start_0_based':a+rb,'source_xml_byte_preservation_end_exclusive_0_based':a+re_,'source_xml_line_1_based':held.sourceline,'source_xml_column_1_based_unicode':len(raw[:a+rb].decode('utf-8').split('\n')[-1])+1,'source_paragraph_xpath':case['locator'],'source_paragraph_sha256':sha(held_raw),'source_image_at_start':'sbb00000114_00331.jpg','encoded_folio_at_start':'164r','encoded_column_at_start':'1/2' if i<3 else '2/2','encoded_column_at_end':'1/2' if i<2 else '2/2','historical_export_first_nonempty_line':first,'historical_export_last_nonempty_line':last,'raw_fragment_sha256':sha(fragment),'uncertainty_note':note,'manuscript_boundary_certified':False,'related_bamberg_narrative_record':entry['boundary_id'],'related_bamberg_narrative_label':entry['bamberg_chapter'],'relationship_status':'THEMATIC_COMPARISON_ONLY_NOT_IDENTITY'}
 records.append(record)
 comparisons.append({'proposed_contents_label':f'[{label}]','related_frozen_record':entry['boundary_id'],'narrative_label_as_recorded':entry['bamberg_chapter'],'narrative_niese_association_only':entry['niese_section'],'narrative_image_as_recorded':entry['image'],'narrative_incipit':entry['text_anchor'],'comparison':note,'correspondence_certified':False})
 # Exactly these frozen records must be retained; no new Bamberg identity is created.
 assert entry['boundary_id']==f'B78-table1-row{94+i:03d}'
reconstructed=held_raw[:raw_positions[0]]+b''.join(x['raw_xml_fragment_utf8'].encode() for x in records)+held_raw[-4:]
assert reconstructed==held_raw
literal_labels=[(''.join(p.itertext()).split()[0]) for p in paragraphs]
assert literal_labels==['I','II','III','IIII','XIII','XIIII','XV','XVI','XVII','XVIII','XVIIII','XX','XXI','XXII','XXIII','XXIIII','XXV','XXVI','XXVII']
# Preserve the source's full chapter-zero bytes as context, without publishing it.
c0=raw.index(b'<div2 n="0"'); c1=raw.index(b'</div2>',c0)+len(b'</div2>'); contents_raw=raw[c0:c1]
assert b'Tunc autem filiis interminatus' in records[2]['raw_xml_fragment_utf8'].encode()
assert b'Hac lite facta saloniae' in records[2]['raw_xml_fragment_utf8'].encode()
assert b'pecuniarum susceptione, hierosolimite' in records[2]['raw_xml_fragment_utf8'].encode()
herodian_text_start=text.index('Tunc autem filiis interminatus'); resumption_start=text.index('pecuniarum susceptione, hierosolimite')
assert positions[2]<herodian_text_start<resumption_start<positions[3]
inputs={'worktree_latin_xiv':{'path':str(source),'sha256':digest(source)},'canonical_latin_xiv':{'path':str(C/'assets/xml/antiquities/Latin/book-14.xml'),'sha256':digest(C/'assets/xml/antiquities/Latin/book-14.xml')},'original_sr061_packet':{'path':str(OLD/'SOURCE_REVIEW_PACKET.md'),'sha256':digest(OLD/'SOURCE_REVIEW_PACKET.md')},'original_sr061_queue':{'path':str(OLD/'source_review_queue.json'),'sha256':digest(OLD/'source_review_queue.json')},'bamberg_map':{'path':str(map_path),'sha256':digest(map_path)},'frozen_manifest':{'path':str(frozen_manifest),'sha256':digest(frozen_manifest)},'production_structure_registry':{'path':str(W/'assets/xml/antiquities/structure.xml'),'sha256':digest(W/'assets/xml/antiquities/structure.xml')}}
proposal={'case':'SR-061','date':'2026-10-08','status':'PROPOSAL_ONLY_AWAITING_EIGHT_BOUNDARY_APPROVAL','authority_update':'Human editor confirms the Herodian passage is genuinely transmitted here. Only the missing numeral sequence and editorial segmentation are under investigation.','source_inputs':inputs,'repository_state_before':repo,'offset_convention':'UTF-8 raw XML bytes; Unicode codepoint text projection including add/del contents, no whitespace collapse. Intervals are zero-based half-open. Preservation ranges include separator whitespace; content-end excludes trailing whitespace. XPath/offsets are audit locators, not new stable source identities.','original_hold':{'case_id':case['case_id'],'label':case['label'],'historical_decision':case['decision'],'historical_note':case['note'],'historical_checkpoint':'a70bb5060fdd7f95c9e6fc4baa3e0cc2241bebaf','unchanged':True},'current_literal_labels':literal_labels,'current_contents_paragraphs':len(paragraphs),'proposed_additional_entries':8,'proposed_total_contents_entries':len(paragraphs)+8,'bamberg_narrative_divisions_in_book':27,'bamberg_narrative_total':198,'existing_bamberg_labels': [x['bamberg_chapter'] for x in b14],'held_paragraph':{'raw_sha256':sha(held_raw),'raw_bytes':len(held_raw),'projection_characters':len(text),'file_byte_start':a,'file_byte_end_exclusive':z,'source_xml_line':held.sourceline,'literal_IIII_prefix_projection':text[:positions[0]],'literal_IIII_prefix_raw_xml':held_raw[:raw_positions[0]].decode('utf-8'),'trailing_page_markers':'After the final mereretur. and separator space, image 00332 / 164v / column 1/2 opens the next source page. They are retained in the last raw audit slice for byte reconstruction; no XII text is assigned to 164v by this convention.'},'candidates':records,'narrative_comparison':comparisons,'export_note':{'line_numbers_are':'One-based nonempty lines in the historical pinned RTF extraction, NOT manuscript line numbers. Reused from the original SR-061 packet; no new image inspection.','extra_1_line_155':'Present in historical T-PEN excerpt after prelio in; absent from current XML. Not a candidate numeral and not imported or repaired.','original_export_excerpt':export},'implementation_gate':'Approval required for all eight starts and preceding ends, explicitly including all Herodian content in proposed VII. No publication registry or source XML changed.'}
def write_json(name,obj): (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write_json('SEGMENTATION_PROPOSAL.json',proposal)
(D/'SOURCE_PARAGRAPH.xml.fragment.txt').write_bytes(held_raw)
(D/'SOURCE_CAPITULA.xml.fragment.txt').write_bytes(contents_raw)
cols=['editorial_label','label_status','incipit','explicit','projection_start_0_based','projection_content_end_exclusive_0_based','projection_preservation_end_exclusive_0_based','source_xml_byte_start_0_based','source_xml_byte_preservation_end_exclusive_0_based','source_xml_line_1_based','source_xml_column_1_based_unicode','source_image_at_start','encoded_folio_at_start','encoded_column_at_start','encoded_column_at_end','historical_export_first_nonempty_line','historical_export_last_nonempty_line','related_bamberg_narrative_record','related_bamberg_narrative_label','uncertainty_note']
with (D/'BOUNDARY_PROPOSAL.csv').open('w',encoding='utf-8',newline='') as f:
 dw=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');dw.writeheader();dw.writerows(records)
with (D/'BAMBERG_NARRATIVE_COMPARISON.csv').open('w',encoding='utf-8',newline='') as f:
 dw=csv.DictWriter(f,fieldnames=list(comparisons[0]));dw.writeheader();dw.writerows(comparisons)
qa={'status':'PASS_PROPOSAL_ONLY_APPROVAL_PENDING','unique_ordered_candidate_starts':8,'candidate_fragments_balanced_xml':8,'candidate_projection_checks_passed':8,'lossless_raw_paragraph_partition':True,'held_paragraph_matches_original_SR061_sha256':True,'held_paragraph_text_characters':len(text),'literal_contents_labels_preserved':literal_labels,'literal_contents_labels_count':len(literal_labels),'proposed_supplied_labels_count':8,'proposed_total_contents_entries':len(paragraphs)+8,'herodian_content_wholly_retained_in_VII':True,'no_new_boundary_at_herodian_narrative':True,'inline_markup_preserved':'2 add, 1 del, all 2 milestone / 2 pb / 3 cb elements retained in original order','frozen_manifest_entries_verified':len(frozen_checks),'frozen_manifest_checks':frozen_checks,'bamberg_registry_identities_unchanged':198,'bamberg_book14_identities_unchanged':27,'contents_index_modified':False,'publication_companion_created':False,'source_xml_modified':False,'source_text_restoration_or_correction_performed':False,'new_manuscript_or_pdf_judgment_introduced':False,'source_images_inspected':False,'browser_QA':'NOT_APPLICABLE: proposal only; no reader change','git_write_operations':0}
write_json('QA.json',qa)
# REPORT is written in a separate explicitly authorized step, then sealed by --seal.
write_json('INTEGRITY_BASELINE.json',{'repository_state_before':repo,'pre_existing_files_sha256':before})
print(json.dumps({'created_proposal_records':8,'projection_offsets':positions,'pre_existing_files_hashed':len(before),'outputs':[p.name for p in D.iterdir()]},indent=2))