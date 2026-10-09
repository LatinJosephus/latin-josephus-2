from pathlib import Path
from lxml import etree as E
import copy,json,re,hashlib
V=Path(__file__).resolve().parent;R=V.parents[1];P=V/'presentation-correction';NS='http://www.tei-c.org/ns/1.0';N={'t':NS};X='{http://www.w3.org/XML/1998/namespace}'
def t(tag):return '{'+NS+'}'+tag
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
policy=read('CAPITALIZATION_POLICY.json');proper=policy['proper_name_glossary'];con=read('ORIGINAL_DISPLAY_CONCORDANCE.json');displays={e['id']:e['display'] for e in con['entries']}
def sentence(s):
 out=re.sub(r'[^\W\d_]+',lambda x:proper.get(x.group(),x.group()),s.lower());out=re.sub(r'\b(Alexander|Herod) the great\b',r'\1 the Great',out);out=re.sub(r'\bmount (Sinai|Gerizzim)\b',r'Mount \1',out);return re.sub(r'(^|[.!?][\s]*|\.\u2014)([a-zæ])',lambda x:x.group(1)+x.group(2).upper(),out)
def projection(e):return (e.text or '')+''.join(('' if E.QName(c).localname=='note' else projection(c))+(c.tail or '') for c in e)
def chosen(e,display):
 orig=E.Element(t('orig'));orig.text=e.text
 for child in list(e):e.remove(child);orig.append(child)
 reg=copy.deepcopy(orig);reg.tag=t('reg');reg.set('resp','#lj-display');raw=projection(orig);assert raw.upper()==display.upper() and len(raw)==len(display)
 pos=0
 for n in reg.iter():
  if n.text:count=len(n.text);n.text=display[pos:pos+count];pos+=count
  if n is not reg and n.tail:count=len(n.tail);n.tail=display[pos:pos+count];pos+=count
 assert pos==len(display);e.text=None;choice=E.SubElement(e,t('choice'));choice.append(orig);choice.append(reg)
 return raw
schema=E.RelaxNG(E.parse(str(V/'authority/original-audit/sources/tei_all.rng')));outputs=[];other=[];moved=[]
note="Compiled from the chapter headings printed in the Auburn and Rochester edition of Whiston's translation (Alden & Beardsley, 1856). The arrangement as an index is editorial, not an original printed table of contents."
for b in range(1,21):
 rel=f'assets/xml/antiquities/paratext/whiston/book-{b:02}-contents.xml';src=P/'before-source'/rel;d=E.parse(str(src));root=d.xpath('//t:div[@type="contents"]',namespaces=N)[0];intro=root.find('t:note',N);intro.text=note;intro.set('subtype','provenance')
 bibl=d.xpath('//t:sourceDesc/t:bibl',namespaces=N)[0]
 for n in d.xpath('//t:body//t:note[@type="editorial"]',namespaces=N):
  if n is intro:continue
  parent=n.getparent();ref=parent.get(X+'id');moved.append({'book':b,'text':''.join(n.itertext()),'old_parent':E.QName(parent).localname,'corresp':ref});parent.remove(n);n.tail=None
  if ref:n.set('corresp','#'+ref)
  bibl.append(n)
 resp=E.SubElement(d.xpath('//t:titleStmt',namespaces=N)[0],t('respStmt'));resp.set(X+'id','lj-display');E.SubElement(resp,t('resp')).text='Editorial sentence-case presentation; original printed capitalization preserved in orig, displayed reading in reg';E.SubElement(resp,t('name')).text='LatinJosephus presentation correction, authorized by the human editor, 9 October 2026'
 enc=d.xpath('//t:encodingDesc',namespaces=N)[0];p=enc.find('t:p',N);p.text=p.text.replace('Comparisons may fold case and ae/æ; display text does not.','Comparisons may fold case and ae/æ; original source readings are retained without such folding.')
 ed=E.SubElement(enc,t('editorialDecl'));norm=E.SubElement(ed,t('normalization'));E.SubElement(norm,t('p')).text='Sentence-case presentation is an editorial layer, not a replacement transcription. Each choice retains the exact accepted 1856 text in orig and a case-only display in reg. Proper names, ligatures, punctuation, spelling, source pointers and Roman labels are preserved; common nouns are lowercased. Compiled-index CSS selects reg only, without altering other witnesses.'
 rev=d.find('t:teiHeader/t:revisionDesc',N)
 if rev is None:rev=E.SubElement(d.find('t:teiHeader',N),t('revisionDesc'))
 E.SubElement(rev,t('change'),when='2026-10-09').text='Authorized human browser-review correction: one provenance note immediately below the index title; reversible sentence-case readings and left-aligned presentation. Original 1856 readings and existing structural identities remain intact.'
 for item in root.findall('t:list/t:item',N):
  raw=chosen(item,displays[item.get(X+'id')]);assert raw==next(x['original'] for x in con['entries'] if x['id']==item.get(X+'id'))
 for pos,p in enumerate(root.findall('t:p',N),1):
  raw=projection(p);out=sentence(raw);chosen(p,out);other.append({'book':b,'kind':'interval-summary','position':pos,'original':raw,'display':out});print('SUMMARY',b,pos,out)
 bookhead=root.findall('t:head',N)[1];raw=projection(bookhead);out=raw.replace('BOOK','Book');chosen(bookhead,out);other.append({'book':b,'kind':'book-designation','original':raw,'display':out})
 schema.assertValid(d);dest=P/'candidates'/f'book-{b:02}-contents.xml';dest.parent.mkdir(exist_ok=True);d.write(str(dest),encoding='UTF-8',xml_declaration=True);outputs.append({'path':rel,'presentation_before_sha256':h(src),'presentation_after_sha256':h(dest),'schema_valid':True})
# All candidates have validated before replacing any implementation companion.
for x in outputs:(R/x['path']).write_bytes((P/'candidates'/Path(x['path']).name).read_bytes())
reg=R/'assets/xml/source-contents.xml';raw=reg.read_bytes();reg_before=P/'before-source/assets/xml/source-contents.xml';assert raw==reg_before.read_bytes()
pattern=rb'(<item xml:id="contents-antiquities-whiston-\d+">[\s\S]*?<f name="note">\s*)<string>[^<]*</string>'
new,n=re.subn(pattern,lambda x:x.group(1)+b'<string/>',raw);assert n==20;schema.assertValid(E.fromstring(new));reg.write_bytes(new);outputs.append({'path':reg.relative_to(R).as_posix(),'presentation_before_sha256':h(reg_before),'presentation_after_sha256':h(reg),'Whiston_registry_notes_cleared':20,'other_records_changed':0})
css=R/'assets/css/tei.css';original=css.read_bytes();assert original==(P/'before-source/assets/css/tei.css').read_bytes();add='''
/* Whiston's compiled index: reversible editorial display, independent of source text.
   The subtype scope leaves Greek, Bamberg, Lodge and narrative typography untouched. */
#english .source-contents tei-div[subtype="editorially-compiled-chapter-index"] {
  text-align: left;
}
#english .source-contents tei-div[subtype="editorially-compiled-chapter-index"] tei-choice > tei-orig {
  display: none;
}
#english .source-contents tei-div[subtype="editorially-compiled-chapter-index"] tei-choice > tei-reg {
  display: inline;
}
#english .source-contents tei-div[subtype="editorially-compiled-chapter-index"] tei-note[subtype="provenance"] {
  font-style: normal;
}
''';nl=b'\r\n' if b'\r\n' in original else b'\n';css.write_bytes(original+add.encode().replace(b'\n',nl));outputs.append({'path':'assets/css/tei.css','presentation_before_sha256':h(P/'before-source/assets/css/tei.css'),'presentation_after_sha256':h(css),'scope':'English compiled-index subtype only; no font/color/size/spacing/loading change'})
policy['status']='COMPLETE_DISPLAY_REVIEW';policy['reviewed_heading_count']=256;policy['reviewed_books']=list(range(1,21))
for name,obj in [('CAPITALIZATION_POLICY.json',policy),('SUMMARY_DISPLAY_CONCORDANCE.json',{'rows':other,'interval_summaries':40,'book_designations':20}),('FILE_CHANGES.json',{'changes':outputs,'production_files':22,'notes_preserved_in_source_metadata':moved,'JavaScript_changes':0})]:(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PRESENTATION_IMPLEMENTED',256,'headings',40,'summaries',20,'book designations; 20+registry+CSS files; no JavaScript')
