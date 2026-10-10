"""Disposable transposition rehearsal; never promotes an editorial decision."""
from pathlib import Path
import json,re,sys,subprocess,tarfile,io,shutil
sys.dont_write_bytecode=True
from mixed_mapper import Book,digest
D=Path(__file__).resolve().parent;ROOT=D.parents[1];RUNTIME=Path('C:/workspace/Antiquities-Niese-11-runtime-20261009')
BASE='65b3256fe202a06e33a59aa2d1dcbd7107358271'
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    bs={lang:Book(D/'inputs'/f'{lang}.xml') for lang in ['Latin','Greek','English']}
    rows=json.loads((D/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'));physical=json.loads((D/'WINDOW_302_347_PHYSICAL_LEDGER.json').read_text(encoding='utf8'))
    assert all(r['implementation_approved'] for r in rows[301:])
    added=[];raw=bs['Latin'].raw
    for f in physical:
        if not f.get('label'):
            n=f['number'];anchor=f'latin-book11-niese-{n}';tag=f'<milestone unit="niese" n="{n}" xml:id="{anchor}"/>'
            f['new_anchor']=anchor;added.append(dict(offset=f['start']['raw_byte'],addition=tag,number=n))
    for op in sorted(added,key=lambda x:x['offset'],reverse=True):raw=raw[:op['offset']]+op['addition'].encode()+raw[op['offset']:]
    assert re.sub(rb'<milestone unit="niese" n="\d+" xml:id="latin-book11-niese-\d+"/>',b'',raw)==bs['Latin'].raw
    def point(lang,offset,label=None,new_anchor=None,end=False):
        b=bs[lang]
        if offset==len(b.stream):
            u=next(u for u in reversed(b.units) if u['text']);return dict(available='true',target=u['id'],kind='paragraph-end')
        if new_anchor:return dict(available='true',target=new_anchor,kind='element')
        if label:
            u=b.units[label['unit']-1];nums=u['element'].xpath('./t:num',namespaces={'t':'http://www.tei-c.org/ns/1.0'})
            ordinal=next(i+1 for i,n in enumerate(nums) if ''.join(n.itertext())==label['text'])
            return dict(available='true',target=u['id'],kind='element-edge',edge=f'num[{ordinal}]')
        u=b.units[b.locate(b.first_content(offset))['paragraph']-1]
        assert offset==u['book_start'],(lang,offset,u['book_start'])
        return dict(available='true',target=u['id'],kind='paragraph')
    LatinSpans={}
    for i,f in enumerate(physical):
        nxt=physical[i+1] if i+1<len(physical) else None
        span=dict(start=point('Latin',f['offset'],f.get('label'),f.get('new_anchor')),
            end=point('Latin',nxt['offset'],nxt.get('label'),nxt.get('new_anchor')) if nxt else point('Latin',len(bs['Latin'].stream)),
            occurrence=f['occurrence'],role='interpolation' if f.get('role') else 'primary',continuationRank=f['rank'],label=f.get('identity') or f'Antiquities XI.{f["number"]} portion{f["rank"]}')
        f['runtime_span']=span
        if not f.get('role'):LatinSpans.setdefault(f['number'],[]).append(span)
    for spans in LatinSpans.values():spans.sort(key=lambda x:x['continuationRank'])
    sources=[f for f in physical if f.get('role')]
    # Candidate recommendation for model proof only. Final affiliation remains pending.
    LatinSpans[312]=[sources[0]['runtime_span'],LatinSpans[312][0],sources[1]['runtime_span'],LatinSpans[312][1]]
    g=bs['Greek'];labels=[x for x in g.labels if re.fullmatch(r'\[\d+\]',x['text'])];gphysical=[dict(number=1,book_offset=0)]+[dict(number=int(x['text'][1:-1]),book_offset=x['book_offset'],label=x) for x in labels]
    GreekSpans={}
    for i,x in enumerate(gphysical):
        nxt=gphysical[i+1] if i+1<len(gphysical) else None
        GreekSpans[x['number']]=[dict(start=point('Greek',x['book_offset'],x.get('label')),end=point('Greek',nxt['book_offset'],nxt.get('label')) if nxt else point('Greek',len(g.stream)),occurrence=f'Greek-XI-{x["number"]}',role='primary',continuationRank=1)]
    notes={n:rows[n-1]['Latin']['review_notes'] for n in [318,319,332,344,345,347]}
    notice='Canonical order from separate witness fragments. Book view preserves Bamberg’s manuscript order.'
    interpolation=json.loads((D/'INTERPOLATION_DECISION.json').read_text(encoding='utf8'))['proposed_notice']
    sections=[];expected={}
    for r in rows:
        n=r['number'];pid=r['Greek']['start']['stable_id'];engpid=pid.replace('greek-','english-')
        eu=next(u for u in bs['English'].units if u['id']==engpid)
        sections.append(dict(number=n,Latin=dict(available=n>=302,correspondence='MODEL_REHEARSAL_ONLY',spans=LatinSpans[n],note=notes.get(n),fragmentNotice=interpolation if n==312 else notice if n in [326,342] else None) if n>=302 else dict(available=False,note='Unreviewed remainder: model rehearsal only.'),Greek=dict(available=True,spans=GreekSpans[n]),English=dict(contextTargets=[engpid]),contextTarget=r['Latin']['alignment_window']))
        if n>=302:
            ps=sorted([f for f in physical if f.get('number')==n],key=lambda f:f['rank'])
            display=([sources[0],ps[0],sources[1],ps[1]] if n==312 else ps)
            expected[str(n)]=dict(Latin=''.join(f['text'] for f in display),Latin_primary=''.join(f['text'] for f in ps),Greek=r['Greek']['text'],English=eu['text'],occurrences=[f['occurrence'] for f in display])
    suppressed=[dict(paragraph=x['id'],label=x['text']) for x in bs['Latin'].labels if x['text'] in ['[318]','[319]','[332]','[344]','[347]','[BJ 4.105a]','[BJ 4.105b]']]
    registry=dict(schema=1,book=11,range=[1,347],suppressedLatinLabels=suppressed,sections=sections,sourcePassages=[dict(identity=f['identity'],occurrence=f['occurrence'],AntiquitiesIdentity=False,span=f['runtime_span'],association=312,editorialStatus='MODEL_RECOMMENDATION_PENDING') for f in sources])
    for name in ['baseline-source','model-source']:
        target=RUNTIME/name
        if target.exists():assert not any(target.iterdir()),'Only an empty failed assignment preparation may resume'
        else:target.mkdir()
        archive=subprocess.check_output(['git','archive',BASE],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                if member.name.startswith('review/'):continue
                parts=member.name.split('/')
                assert not member.name.startswith('/') and '..' not in parts and ':' not in member.name
                p=target.joinpath(*parts)
                if member.isdir():p.mkdir(parents=True,exist_ok=True)
                elif member.isfile():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(member).read())
                else:raise ValueError('Unexpected non-file archive member: '+member.name)
    model=RUNTIME/'model-source';(model/'assets/js/renderTei.js').write_bytes((ROOT/'assets/js/renderTei.js').read_bytes());(model/'assets/xml/antiquities/Latin/book-11.xml').write_bytes(raw)
    save(model/'assets/xml/antiquities/niese/book-11.json',registry)
    save(D/'MODEL_EXPECTED_INTERVALS.json',expected);save(D/'MODEL_IDENTITY_REGISTRY.json',registry)
    save(D/'MODEL_MARKER_ADDITIONS.json',added);save(D/'MODEL_SOURCE_PROOF.json',dict(scope='302-347 MODEL ONLY',base=BASE,source_raw_sha256=digest(bs['Latin'].raw),candidate_raw_sha256=digest(raw),inverse_recovery=True,unreviewed_remainder=True,interpolation_decision_pending=True))
    print('Isolated302-347 candidate and archived baseline prepared; no corpus bulk insertion.')
if __name__=='__main__':main()
