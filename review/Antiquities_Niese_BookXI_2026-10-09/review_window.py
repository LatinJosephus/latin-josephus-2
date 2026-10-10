"""Individually reviewed tail cuts; independent physical and logical ledgers."""
from pathlib import Path
import json,re,sys
sys.dont_write_bytecode=True
from mixed_mapper import Book,digest
D=Path(__file__).resolve().parent
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    if (D/'INTERPOLATION_DECISION.json').exists() and json.loads((D/'INTERPOLATION_DECISION.json').read_text(encoding='utf8')).get('status')=='CLOSED_USER_APPROVED':
        raise RuntimeError('Historical preparation only: do not overwrite the closed user decision. Use implement_xi.py for the final complete register.')
    l=Book(D/'inputs/Latin.xml');g=Book(D/'inputs/Greek.xml')
    rows=json.loads((D/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'))
    starts={}
    def label(text):return next(x for x in l.labels if x['text']==text)
    def retained(n,text=None):
        x=label(text or f'[{n}]');starts.setdefault(n,[]).append(dict(offset=x['book_offset'],label=x,rank=1,method='REVIEWED_RETAINED_LABEL'))
    def phrase(n,pid,text):
        u=next(u for u in l.units if u['id']==pid);assert u['text'].count(text)==1,(n,text)
        at=u['book_start']+u['text'].index(text);starts.setdefault(n,[]).append(dict(offset=at,rank=1,method='REVIEWED_NEW_WORD_CUT',phrase=text))
    for n,txt in [(302,'[VII.ii.302]'),(304,'[VIII.i.304]'),(306,'[VIII.ii.306]'),(311,None),(313,'[VIII.iii.313]'),(314,None),(315,None),(316,None),(317,None),(320,None),(321,'[VIII.iv.321]'),(322,None),(323,None),(324,None),(325,None),(327,None),(328,None),(329,'[VIII.v.329]'),(330,None),(331,None),(333,None),(334,None),(335,None),(336,None),(337,None),(338,None),(339,None),(340,'[VIII.vi.340]'),(341,None),(343,'[VIII.vi.343]'),(345,None),(346,'[VIII.vii.346]')]:retained(n,txt)
    for n,pid,text in [(303,'latin-book11-num302','Audiens claram'),(305,'latin-book11-num304','Succedens uero'),(307,'latin-book11-num306','Arbitrantur enim'),(308,'latin-book11-num306','Nam extitisse'),(309,'latin-book11-num306','Principes quoque'),(310,'latin-book11-num306','Itaque anabalath'),(318,'latin-book11-num313','ne in posterum peniteret'),(319,'latin-book11-num313','Alexander incitatus'),(332,'latin-book11-num329','omnibus uero'),(344,'latin-book11-num343','sycimitas autem'),(347,'latin-book11-num346','Defunctus est autem')]:phrase(n,pid,text)
    for n,pairs in [(312,[('[312a]',1),('[VIII.ii.312b]',2)]),(326,[('[326a]',1),('[VIII.iv.326b]',2)]),(342,[('[342a]',1),('[342b]',2)])]:
        for txt,rank in pairs:
            x=label(txt);starts.setdefault(n,[]).append(dict(offset=x['book_offset'],label=x,rank=rank,method='REVIEWED_RETAINED_PORTION_LABEL'))
    sources=[]
    for suffix in ['a','b']:
        x=label(f'[BJ 4.105{suffix}]');sources.append(dict(offset=x['book_offset'],label=x,identity=f'BJ.IV.105{suffix}',rank=1,role='INTERPOLATION'))
    physical=sorted([dict(number=n,**s) for n,parts in starts.items() for s in parts]+sources,key=lambda x:x['offset'])
    for i,f in enumerate(physical):
        end=physical[i+1]['offset'] if i+1<len(physical) else len(l.stream)
        f.update(start=l.locate(f['offset']),end=l.locate(end) if end<len(l.stream) else dict(book_offset=end,kind='narrative-end'),text=l.stream[f['offset']:end],narrative_sha256=digest(l.stream[f['offset']:end].encode()),occurrence=f'Latin-XI-{f.get("number",f.get("identity"))}-{f["rank"]}')
    for r in rows[301:]:
        n=r['number'];r['Latin']['fragments']=[f for f in physical if f.get('number')==n]
        r['Latin'].update(review_status='INDIVIDUALLY_REVIEWED',correspondence='PRESENT',review_notes={318:'Latin reassurance ne in posterum peniteret is part of Greek318; inherited [318] occurs later before Cumque. Greek319 anger begins at Alexander incitatus before inherited [319].',319:'Start before Alexander incitatus; retain visible [319] within this interval.',332:'Greeting by the Jews starts omnibus uero; inherited [332] occurs within preceding approach/adulation account corresponding to Greek331.',344:'Greek343 includes the Hebrew self-identification; Greek344 begins Sidonian/Shechemite naming, paired with sycimitas autem after inherited [344].',345:'Retain transmitted interrupted prae and following anonymous paragraph; semantic correspondence survives across paragraph boundary without reconstructing wording.',347:'Greek347 adopted opening is τετελευτήκει within the line carrying marginal347, paired with Defunctus est autem. Inherited Latin [347] introduces the preceding flight-to-Shechem clause.'}.get(n,'Each full Greek section and neighbouring Latin/Greek read; retained wording and compression, no emendation.'))
        if n in [312,326,342]:r['Latin']['review_notes']='Two separated surviving portions; continuation rank a then b explicitly reviewed against the entire Greek identity.'
        r['physical_locator_status']='EXACT_FROZEN_TEXT_TAIL_AND_RAW_CANDIDATE';r['editorial_status']='ROUTINE_CUT_ADOPTED';r['implementation_approved']=True
    for f in physical:
        if f.get('role')=='INTERPOLATION':
            f.update(association_proposal=312,association_status='PENDING_USER_GRANULARITY_DECISION',traditional_affiliation='LOEB-11-Subchapter-8-2 and LOEB-11-Chapter-8-0',Antiquities_identity=False)
    save('CANDIDATE_REGISTER.json',rows);save('WINDOW_302_347_PHYSICAL_LEDGER.json',physical)
    save('INTERPOLATION_DECISION.json',dict(status='PENDING',recommendation='Attach both source passages to XI312, each immediately before its corresponding312 portion, retaining their separate identity and visible labels.',
        sources=[f for f in physical if f.get('role')=='INTERPOLATION'],
        Latin312=[f for f in physical if f.get('number')==312],
        neighbours={str(n):[f for f in physical if f.get('number')==n] for n in [311,313,341,342,343]},
        proposed_notice='Bamberg inserts two parts of Jewish War IV.105 before the two surviving portions of Antiquities XI.312. They remain separately labelled here. Antiquities XI.312 is assembled as 312a then 312b. Book view preserves Bamberg’s manuscript order.',
        alternative='Group both labelled insertions after the assembled XI312 narrative as attached source passages.',
        duplication_rule='Each declared physical occurrence is rendered once per combined selection. A reference carries no additional occurrence.'))
    print('Reviewed tail cuts and separately owned BJ insertions recorded; affiliation decision pending.')
if __name__=='__main__':main()
