from pathlib import Path
from lxml import etree as E
import json,re,collections,hashlib
root=Path(r'C:\workspace\LatinJosephus-antiquities-traditional-navigation');review=root/'review/Antiquities_Traditional_Navigation_Followup_2026-10-07'
ns={'t':'http://www.tei-c.org/ns/1.0'};URI=ns['t'];XI='{http://www.w3.org/XML/1998/namespace}id'
def fields(fs):return {f.get('name'):fields(f[0]) if E.QName(f[0]).localname=='fs' else [fields(x) for x in f[0]] if E.QName(f[0]).localname=='vColl' else f[0].text or '' for f in fs}
def add(parent,name,value):
 f=E.SubElement(parent,'{'+URI+'}f',name=name)
 if isinstance(value,dict):
  fs=E.SubElement(f,'{'+URI+'}fs',type='range-boundary')
  for k,v in value.items():add(fs,k,v)
 else:E.SubElement(f,'{'+URI+'}string').text=value
 return f
p=root/'assets/xml/antiquities/structure.xml';assert hashlib.sha256(p.read_bytes()).hexdigest()==json.loads((review/'BASELINE.json').read_bytes())['files']['assets/xml/antiquities/structure.xml']['sha256'],'Run only on the recorded clean base';tree=E.parse(str(p));items=tree.xpath('//t:list[@type="traditional-boundaries"]/t:item',namespaces=ns)
docs={};prefixes={};diagnostics=[]
omit={'num','milestone','pb','lb','note','anchor'}
def projection(n):
 if E.QName(n).localname in omit:return ''
 return (n.text or '')+''.join(projection(c)+(c.tail or '') for c in n if isinstance(c.tag,str))
def key(loc):return (loc['target'],loc.get('edge',''),loc['kind'])
def point(d,loc):
 n=d.xpath('//*[@xml:id="'+loc['target']+'"]',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})[0]
 if loc['kind']=='element-edge':
  for step in loc['edge'].split('/'):
   tag,idx=step[:-1].split('[');n=n.findall('t:'+tag,ns)[int(idx)-1]
 return n
for item in items:
 row=fields(item.find('t:fs',ns))
 for lang in ['Greek','Latin','English']:
  loc=row[lang]
  if loc['available']!='true' or key(loc) in prefixes:continue
  if loc['file'] not in docs:docs[loc['file']]=E.parse(str(root/'assets/xml/antiquities'/loc['file']))
  d=docs[loc['file']];node=point(d,loc);prefix=node
  # Move only across contiguous empty markers/numerals and whitespace, never narrative text.
  while prefix.getprevious() is not None:
   prev=prefix.getprevious()
   if E.QName(prev).localname not in {'num','milestone','anchor'} or (prev.tail or '').strip():break
   prefix=prev
  para=d.xpath('//*[@xml:id="'+loc['paragraph']+'"]',namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})[0]
  at_start=prefix is para or (prefix.getparent() is para and prefix.getprevious() is None and not (para.text or '').strip())
  heading=None
  if at_start:
   prev=para.getprevious()
   # This is explicit source heading ownership, not a runtime chapter-number heuristic.
   if prev is not None and E.QName(prev).localname=='p' and not prev.get(XI) and re.match(r'^CHAPTER\s+\d+\.', ''.join(prev.itertext()).strip()):
    number=re.match(r'^CHAPTER\s+(\d+)\.', ''.join(prev.itertext()).strip()).group(1)
    assert row['scheme']=='chapter' or row['subchapter']=='1'
    assert number==row['chapter'],(item.get(XI),number,row['chapter'])
    heading=prev;prefix=prev
  if heading is not None:
   parent=prefix.getparent();assert parent.get(XI)
   idx=list(parent).index(prefix)
   assert not (parent.text or '').strip() and idx==0
   boundary={'available':'true','kind':'element-edge','target':parent.get(XI),'edge':'p[1]'}
   reason='Explicit current English chapter-heading paragraph preceding the certified first narrative paragraph.'
  elif prefix is not node:
   if at_start:boundary={'available':'true','kind':'paragraph','target':para.get(XI)}
   else:
    parent=prefix.getparent();assert parent.get(XI)
    tag=E.QName(prefix).localname;idx=list(parent.findall('t:'+tag,ns)).index(prefix)+1
    boundary={'available':'true','kind':'element-edge','target':parent.get(XI),'edge':f'{tag}[{idx}]'}
   reason='Contiguous current structural numeral/empty-marker prefix immediately before the certified text locator; no intervening narrative text.'
  else:continue
  prefixes[key(loc)]=boundary
  diagnostics.append({'identity':item.get(XI),'language':lang,'original_text_locator':loc,'range_boundary':boundary,'reason':reason,'prefix_text':''.join(prefix.itertext())[:240] if heading is not None else ''.join(c.text or '' for c in para if E.QName(c).localname=='num')[:120]})
# Identical physical points, including registered fragment endpoints, share identical prefix ownership.
updates=collections.Counter()
for item in items:
 for fs in item.xpath('.//t:fs[@type="text-locator"]',namespaces=ns):
  loc=fields(fs)
  if loc.get('available')=='true' and loc.get('target') and key(loc) in prefixes:
   add(fs,'boundary-start',prefixes[key(loc)]);updates[next(f.get('name') for f in fs.iterancestors() if E.QName(f).localname=='f' and f.get('name') in ['Greek','Latin','English'])]+=1
reader_note="Bamberg 78 preserves this passage in an unusual order. Levenson and Martin show that, in this part of Book XI, its manuscript family transposes sections 311–347 and also inserts material from Jewish War 4.105. Chapter and Subchapter views therefore gather the corresponding passages and display them in the order used by Niese and Loeb. Choose Book view to see Bamberg’s manuscript order."
notes=0
for item in items:
 fs=item.find('t:fs',ns);row=fields(fs)
 if any('presentation-note' in row[lang] for lang in ['Greek','Latin','English']):add(fs,'reader-note',reader_note);notes+=1
# Indent only newly inserted feature nodes, preserving existing whitespace and all source strings.
for f in tree.xpath('//t:f[@name="boundary-start" or @name="reader-note"]',namespaces=ns):
 parent=f.getparent();previous=f.getprevious();parent_depth=len(list(parent.iterancestors()))
 indent='  '*(parent_depth+1)
 if previous is not None:previous.tail='\n'+indent
 E.indent(f,space='  ',level=parent_depth+1);f.tail='\n'+'  '*parent_depth
p.write_bytes(E.tostring(tree,encoding='UTF-8',xml_declaration=True,pretty_print=False))
(review/'PREFIX_LOCATOR_ADJUDICATION.json').write_bytes(json.dumps({'unique_prefix_locations':len(prefixes),'locator_fields_updated':dict(updates),'shared_reader_note_identities':notes,'diagnostics':diagnostics},ensure_ascii=False,indent=2).encode())
# Renderer: availability is derived from registry data and normalized only for ordinary interaction.
p=root/'assets/js/renderTei.js';s=p.read_bytes().decode();newline='\r\n' if '\r\n' in s else '\n';s=s.replace('\r\n','\n')
def replace(a,b):
 global s
 assert a in s,a[:90]
 s=s.replace(a,b,1)
replace('  const structuralUnavailable = (language, reason) => {','''  const selectAvailableTraditionalSubchapter = () => {
    const rows = traditionalRows("subchapter", isPreface() ? "" : state.chapterNum);
    state.subchapterNum = rows[0]?.subchapter || null;
    if (!state.subchapterNum) state.viewingLevel = isPreface() ? "book-level" : "chapter-level";
  };
  const structuralUnavailable = (language, reason) => {''')
replace('  // Independent witness spans may be assembled in registered canonical order.','''  // Display boundaries can include a heading/label before the independent citation/text point.
  const traditionalRangePoint = (data, locator) => traditionalPoint(data, locator?.["boundary-start"] || locator);
  // Independent witness spans may be assembled in registered canonical order.''')
replace('const start = traditionalPoint(data, span.start);','const start = traditionalRangePoint(data, span.start);')
replace('null : traditionalPoint(data, span.end);','null : traditionalRangePoint(data, span.end);')
a=s.index('    const disclosure = record[language]?.["presentation-note"];');b=s.index('    return wrapper;',a);s=s[:a]+s[b:]
replace('  const antiquitiesUnitView = (language, data) => {','''  const updateTraditionalNotice = () => {
    document.getElementById("traditional-reader-notice")?.remove();
    if (!usesTraditionalStructure() || !["chapter-level", "subchapter-level"].includes(state.viewingLevel)) return;
    const explanation = traditionalSelection()?.["reader-note"];
    const panes = document.getElementById("pane-container");
    if (!explanation || !panes) return;
    const notice = document.createElement("aside");
    notice.id = "traditional-reader-notice";
    notice.className = "alert alert-secondary";
    notice.dataset.structuralNotice = "true";
    const text = document.createElement("p"); text.textContent = explanation;
    const url = new URL(window.location.href);
    ["chapter", "subchapter", "niese", "unit", "num"].forEach(key => url.searchParams.delete(key));
    const link = document.createElement("a"); link.href = url.href; link.textContent = "See Bamberg’s manuscript order in Book view";
    notice.append(text, link); panes.before(notice);
  };
  const antiquitiesUnitView = (language, data) => {''')
replace('    if (subchapterControl) subchapterControl.closest(".form-check").hidden = !usesTraditionalStructure();','''    if (subchapterControl) {
      subchapterControl.closest(".form-check").hidden = !usesTraditionalStructure();
      if (usesTraditionalStructure()) {
        const available = traditionalRows("subchapter", isPreface() ? "" : state.chapterNum).length > 0;
        subchapterControl.disabled = !available;
        if (subchapterSelectMenu) subchapterSelectMenu.disabled = !available;
      }
    }''')
replace('    addContraApionemTransmissionNotice();','    addContraApionemTransmissionNotice();\n    updateTraditionalNotice();')
replace('if (state.viewingLevel === "subchapter-level") state.subchapterNum = traditionalRows("subchapter", state.chapterNum)[0]?.subchapter || null;','if (state.viewingLevel === "subchapter-level") selectAvailableTraditionalSubchapter();')
replace('''            state.subchapterNum = nextLevel === "subchapter-level"
              ? traditionalRows("subchapter", isPreface() ? "" : state.chapterNum)[0]?.subchapter || null : null;''','''            state.subchapterNum = null;
            if (nextLevel === "subchapter-level") selectAvailableTraditionalSubchapter();''')
s=s.replace('state.viewingLevel = state.subchapterNum ? \"subchapter-level\" : \"chapter-level\";', 'state.viewingLevel = state.subchapterNum ? \"subchapter-level\" : (isPreface() ? \"book-level\" : \"chapter-level\");', 1)
p.write_bytes(s.replace('\n',newline).encode())
print(json.dumps({'prefix_locations':len(prefixes),'locator_fields_updated':dict(updates),'shared_notice_identities':notes,'new_anchors':0}))