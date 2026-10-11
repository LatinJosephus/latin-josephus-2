import postrelease_reader as a
import postrelease_stage as s
import xml.etree.ElementTree as E
import shutil

def record():
    rel='assets/xml/antiquities/Latin/book-01.xml';raw=(a.W/rel).read_bytes();text=raw.decode('utf8');tree=E.fromstring(raw);ns={'t':'http://www.tei-c.org/ns/1.0'}
    targets=['note_837e454f963d4cd5b8428a0b985d64a8','note_1848bd9ae426435f94ce4bf1ed09c961','note_5e738419cb1e4ad3a8b566ed1ed83808']
    locations=[]
    for lineno,line in enumerate(text.splitlines(),1):
        import re
        for match in re.finditer(r'<ref\b[^>]*target="([^"]+)"[^>]*>(.*?)</ref>',line):
            if any(t in match.group(1) for t in targets):locations.append({'file':rel,'line':lineno,'column':match.start()+1,'source_paragraph':'latin-book01-num34','original_markup':match.group(0),'targets':match.group(1).split(),'label':match.group(2)})
    assert len(locations)==3
    history=[]
    for target in targets:
        output=a.gt('log','--all','--format=%H %s','-G',r'xml:id=["\x27]'+target,'--','assets/xml/',repo=a.W)
        history.append({'target':target,'search':'all locally available Git refs; added/removed xml:id definitions under assets/xml','matches':output.splitlines()})
    candidates=[]
    for node in tree.iter():
        if node.tag.endswith('}p') and node.attrib.get('{http://www.w3.org/XML/1998/namespace}id')=='latin-book01-num34':
            for note in node.findall('.//t:note',ns):candidates.append({'context':'inline notes in Latin I.34','attributes':note.attrib,'exact_note_markup':E.tostring(note,encoding='unicode')})
        if node.tag.endswith('}app') and any(ch.attrib.get('source')=='#latin-book01-num34' for ch in node):
            candidates.append({'context':'standOff apparatus for Latin I.34','exact_app_markup':E.tostring(node,encoding='unicode')})
    evidence={'UTC':a.now(),'status':'EDITORIAL HOLD — NOT REPAIRED / NOT PASSED','human_decision':'Keep original references unchanged; no unverified redirection or unresolved-reference UI is authorized. This hold does not block A/B/D/E completion.','source_commit':a.F,'public_preview_commit':a.V,'source_file':rel,'source_SHA256':a.sha(raw),'references':locations,'current_corpus_search':a.load(a.T/'APPARATUS_SOURCE_TRACE.json'),'historical_search':history,'surviving_candidates':candidates,'limitations':['No target definition is present in the 143 current scholarly XML files.','Locally available Git history contains no matching added/removed target ID definitions.','Surviving paragraph notes and standOff readings do not provide a documented UUID mapping.','No new facsimile or original-edition inspection was made; existing audit evidence is the provenance of the defect.','A fourth empty ref is separately noted by the source trace and is not silently treated as one of the three visible links.'],'future_evidence_requirement':'An original edition, earlier XML version or authoritative apparatus record establishing the exact UUID-to-note mapping; present a focused packet for editorial approval before implementation.'}
    a.save(a.Q/'UNRESOLVED_REFERENCES.json',evidence)
    md=['# Package C — permanent unresolved-reference register','','Status: **EDITORIAL HOLD; not repaired and not passed.** The user explicitly accepted this disposition on 11 October 2026. The hold does not block completion of A/B/D/E.','',f'Frozen source: {a.F}. Public reproduction: {a.V}. Source: `{rel}`, SHA-256 `{a.sha(raw)}`.','', '| Source location | Original reference targets |','|---|---|']
    md += [f"| Line {x['line']}, column {x['column']}, Latin I.34 | {' '.join(x['targets'])} |" for x in locations]
    md += ['','The exact raw markup, all current corpus searches, individual Git-history searches, and full surviving candidate note/apparatus markup are preserved in UNRESOLVED_REFERENCES.json. No secure correspondence links the missing UUIDs to those candidates. No note was invented, renumbered, substituted, disabled or redirected. Scholarly XML is unchanged.','', 'The three links still reproduce in `/antiquities/?book=1&bamberg=5`; they generate two distinct malformed 404 destinations, documented in FIVE_DEFECTS_baseline.json and FIVE_DEFECTS_live.json. A correct source mapping requires editorial evidence. Adding a fragment marker to a nonexistent ID is not a repair.','', 'Future disposition: recover authoritative target evidence, then submit a focused packet for editorial approval. A qualified unresolved-reference UI is a possible separate task; it is not authorized here.','']
    (a.Q/'UNRESOLVED_REFERENCES.md').write_text('\n'.join(md),encoding='utf8',newline='\n')
    decisions=(a.Q/'DECISIONS.md').read_text();decisions=decisions.replace('C: EDITORIAL HOLD pending the requested narrow disposition.','C: EDITORIAL HOLD explicitly confirmed by the user on 11 October 2026; original references retained. A/B/D/E may proceed independently.')
    (a.Q/'DECISIONS.md').write_text(decisions,encoding='utf8',newline='\n')
    shutil.copy2('postrelease_hold.py',a.Q/'postrelease_hold.py')
    s.commit('package-C-hold','Preserve missing Book-I note references on explicit editorial hold')

if __name__=='__main__':record()
