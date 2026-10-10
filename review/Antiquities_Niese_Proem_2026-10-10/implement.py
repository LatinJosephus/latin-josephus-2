from prepare import *
def main():
    rows=json.loads((PACK/'DECISION_REGISTER.json').read_text(encoding='utf-8'))
    source=ROOT/'assets/xml/antiquities/Latin/preface.xml';raw=(PACK/'frozen-inputs/Latin.xml').read_bytes()
    assert source.read_bytes()==raw
    additions=[]
    for row in rows:
        n=row['number']
        if n in [1,5,10,18]:continue
        additions.append(dict(language='Latin',number=n,offset=row['Latin_start']['raw_UTF8_byte_offset'],marker=f'<milestone unit="niese" n="{n}" xml:id="niese-latin-preface-{n}"/>'))
    additions.append(dict(language='Latin',number=26,role='exclusive_narrative_end',offset=rows[-1]['Latin_end']['raw_UTF8_byte_offset'],marker='<milestone unit="niese-end" xml:id="niese-latin-preface-end26"/>'))
    for a in sorted(additions,key=lambda x:x['offset'],reverse=True):raw=raw[:a['offset']]+a['marker'].encode()+raw[a['offset']:]
    etree.fromstring(raw);source.write_bytes(raw)
    registry=dict(schema=1,book='preface',range=[1,26],label='Proem (Antiquities I.1–26)',suppressedLatinLabels=[],relatedPassage=dict(book=1,niese=27,label='Begin Book I narrative at I.27'),sections=[])
    for r in rows:
        lat=dict(available=True,correspondence='PRESENT',note=None)
        if r['number']==25:lat['note']='The future-treatise promise is not independently identifiable in the present Bamberg transcription. The surviving opening “Quod ego nunc quidem” is retained.'
        if r['number']==26:lat['note']='The present Bamberg transcription has no separately identifiable equivalent of the Greek opening verb or final transition formula; its surviving narrative text is retained.'
        registry['sections'].append(dict(number=r['number'],Latin=lat,contextTarget=r['Latin_start']['xml_id'],English=dict(contextTargets=[r['English_context_target']])))
    save(ROOT/'assets/xml/antiquities/niese/preface.json',registry)
    p=ROOT/'assets/js/renderTei.js';b=p.read_bytes();s=b.decode();changes=[]
    def replace(old,new):
        nonlocal s
        assert s.count(old)==1,(old[:90],s.count(old));s=s.replace(old,new);changes.append(dict(old=old,new=new))
    replace('      nieseIdentityBooks: {','      nieseIdentityBooks: {\n        preface: "assets/xml/antiquities/niese/preface.json",')
    replace('  const supportsNieseBook = book => Boolean(\n    activeWork.nieseBooks?.includes(Number(book))\n    || activeWork.nieseIdentityBooks?.[Number(book)]\n  );', '  // Standalone source views keep their own registry key and citation extent.\n  const nieseBookKey = book => /^\\d+$/.test(String(book)) ? Number(book) : book;\n  const supportsNieseBook = book => Boolean(\n    activeWork.nieseBooks?.includes(nieseBookKey(book))\n    || activeWork.nieseIdentityBooks?.[nieseBookKey(book)]\n  );')
    replace('  const nieseIdentityRegistry = () => nieseIdentityRegistries.get(Number(state.bookNum)) || null;', '  const nieseIdentityRegistry = () => nieseIdentityRegistries.get(nieseBookKey(state.bookNum)) || null;')
    replace('    const book = Number(state.bookNum), path = activeWork.nieseIdentityBooks?.[book];','    const book = nieseBookKey(state.bookNum), path = activeWork.nieseIdentityBooks?.[book];')
    replace('    isPreface() ? activeWork.preface.label : `Book ${state.bookNum}`','    nieseIdentityRegistry()?.label || (isPreface() ? activeWork.preface.label : `Book ${state.bookNum}`)')
    replace('    bookLabel.innerText = currentBookLabel();','    const related = nieseIdentityRegistry()?.relatedPassage;\n    if (related && (!state.nieseNum || Number(state.nieseNum) === nieseIdentityRegistry().range[1])) {\n      const note = document.createElement("p");\n      note.className = "niese-related-passage";\n      const link = document.createElement("a");\n      const url = new URL(window.location.href);\n      ["chapter", "subchapter", "bamberg", "unit", "num", "view", "niese"].forEach(key => url.searchParams.delete(key));\n      url.searchParams.set("book", related.book);\n      if (related.niese) url.searchParams.set("niese", related.niese);\n      link.href = url.href; link.textContent = related.label;\n      note.appendChild(link); latinPane.appendChild(note);\n    }\n\n    bookLabel.innerText = currentBookLabel();')
    replace('      pane.childNodes.forEach(node => {','      [...pane.childNodes].forEach(node => {')
    p.write_bytes(s.encode())
    save(PACK/'AUTHORIZED_ADDITIONS.json',additions);save(PACK/'READER_PATCH.json',changes)
    print('Inserted 22 Latin starts and one exclusive end; added standalone registry and generic source-key support.')
if __name__=='__main__':main()
