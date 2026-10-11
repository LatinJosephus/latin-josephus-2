"""Read-only provenance verification; assemble only commit-pinned English blobs."""
from pathlib import Path
import hashlib, json, re, subprocess, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / 'review/Whiston_I_XI_Renderer_2026-10-11'
CANON = Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
PIN = '663b8ce318f0aa247d304d8eeda5b8e76e7489c6'
ROMANS = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
NS = '{http://www.tei-c.org/ns/1.0}'
sha = lambda b: hashlib.sha256(b).hexdigest()
def git(*args, cwd=CANON):
    return subprocess.check_output(['git', *args], cwd=cwd)
def read_json(b):
    return json.loads(b)
def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

inventory = []
oracle = []
for n, roman in enumerate(ROMANS, 1):
    branch = f'pilot/whiston-antiquities-book{n:02d}-' + ('20261010' if n <= 7 else '20261011')
    if n == 9:
        branch = 'pilot/whiston-antiquities-book09-restored-20261011'
    commit = git('rev-parse', branch).decode().strip()
    if n == 9:
        assert commit == '2ce18b40ea8652e5e0d5046f10b1c39935fcdc54'
    files = git('ls-tree', '-r', '--name-only', commit, 'review').decode().splitlines()
    qa_path = ('review/BookIX_Restored_Segmentation_2026-10-11/QA.json' if n==9
        else f'review/Book{roman}_Pilot_'+('2026-10-10' if n<=7 else '2026-10-11')+'/QA.json')
    assert qa_path in files
    qa = read_json(git('show', f'{commit}:{qa_path}'))
    archive_dir = Path(f'C:/workspace/Book{roman}-Pilot-Exports-' + ('20261010' if n <= 7 else '20261011'))
    if n == 9:
        archive_dir = Path('C:/workspace/BookIX-Segmentation-Exports-20261011')
    archive_name = f'Book{roman}-D-DATA-GO-RENDERER-NO-GO.zip'
    if n == 1:
        archive_name = 'BookI-D-COMPLETE-BOOK-I-PARTIAL-NOT-CERTIFIED.zip'
    archive = archive_dir / archive_name
    raw_archive = archive.read_bytes()
    recorded_hash = re.search(r'[a-fA-F0-9]{64}', (archive.with_suffix('.zip.sha256')).read_text()).group().lower()
    assert sha(raw_archive) == recorded_hash
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names = z.namelist()
        manifests = [p for p in names if Path(p).name in ('CHECKSUMS.json','MANIFEST.json') and '/' not in p]
        verified = 0
        for manifest in manifests:
            data = read_json(z.read(manifest))
            rows = data if isinstance(data, list) else data.get('files', [])
            if isinstance(rows, dict):
                rows = [{'path': k, **(v if isinstance(v,dict) else {'sha256':v})} for k,v in rows.items()]
            for row in rows:
                path = row.get('path', row.get('file'))
                digest = row.get('sha256', row.get('SHA256'))
                if path and digest:
                    assert sha(z.read(path)) == digest, (n, path)
                    verified += 1
        outputs = []
        for filename in (['preface.xml','book-01.xml'] if n == 1 else [f'book-{n:02d}.xml']):
            rel = f'assets/xml/antiquities/English/{filename}'
            blob = git('show', f'{commit}:{rel}')
            archived = next(p for p in names if p == 'output/'+filename)
            recovery_blob = z.read(archived)
            assert blob.replace(b'\r\n',b'\n') == recovery_blob.replace(b'\r\n',b'\n'), (n, filename, 'Git/recovery differs beyond EOL')
            assert ET.tostring(ET.fromstring(blob)) == ET.tostring(ET.fromstring(recovery_blob))
            (ROOT / rel).write_bytes(blob)
            (PACK/'certified').mkdir(exist_ok=True)
            (PACK/'certified'/filename).write_bytes(blob)
            tree = ET.fromstring(blob)
            body = tree.find('.//'+NS+'body')
            div = body.find(NS+'div1')
            # Independent XML event oracle: no DOM Range or production extractor.
            text = []
            positions = []
            inline = []
            notes = []
            length = [0]
            def emit(s, stack):
                if not s:
                    return
                start = length[0]
                text.append(s)
                length[0] += len(s)
                for tag,attrs in stack:
                    if tag in ('q','hi','foreign','emph','title','ref','name','seg'):
                        inline.append({'start':start,'end':length[0],'tag':tag,'attrs':attrs,'text':s})
            def walk(el, stack=()):
                tag = el.tag.removeprefix(NS)
                if tag == 'milestone' and el.get('unit') == 'niese':
                    positions.append((int(el.get('n')),length[0]))
                    return
                if tag == 'num':
                    return  # inherited/generated citation labels checked separately
                if tag == 'note':
                    notes.append({'offset':length[0],'text':norm(''.join(el.itertext())), 'attrs':dict(el.attrib)})
                    return
                attrs = {k.removeprefix('{http://www.w3.org/XML/1998/namespace}'):v for k,v in el.attrib.items()}
                next_stack = stack + ((tag, attrs),)
                emit(el.text, next_stack)
                for child in el:
                    walk(child, next_stack)
                    emit(child.tail, next_stack)
            walk(div)
            alltext = ''.join(text)
            physical = [x[0] for x in positions]
            assert len(physical) == len(set(physical))
            expected = list(range(1,27)) if filename == 'preface.xml' else list(range(27,347)) if n == 1 else list(range(1, {2:349,3:322,4:331,5:362,6:378,7:394,8:420,9:291,10:281,11:347}[n]+1))
            assert sorted(physical) == expected, (n,len(physical))
            if n == 11:
                assert physical == list(range(1,312))+list(range(326,343))+list(range(312,326))+list(range(343,348))
            for index,(number,start) in enumerate(positions):
                end = positions[index+1][1] if index+1 < len(positions) else length[0]
                value = norm(alltext[start:end])
                parts = []
                for item in inline:
                    left,right = max(start,item['start']),min(end,item['end'])
                    if left < right:
                        fragment = norm(alltext[left:right])
                        if fragment:
                            parts.append({'tag':item['tag'],'attrs':item['attrs'],'text':fragment})
                oracle.append({'book':'preface' if filename == 'preface.xml' else str(n),'number':number,
                    'nextPhysical':positions[index+1][0] if index+1<len(positions) else None,
                    'text':value,'rawText':alltext[start:end],'sha256':sha(value.encode()),'opening':value[:100],'closing':value[-100:],
                    'inline':parts,'notes':[note for note in notes if start<=note['offset']<end]})
            outputs.append({'path':rel,'git_blob':git('rev-parse',f'{commit}:{rel}').decode().strip(),
                'sha256':sha(blob),'bytes':len(blob),'sections':len(positions),'physical_order':physical,
                'recovery_sha256':sha(recovery_blob),'recovery_bytes':len(recovery_blob),
                'recovery_byte_identical':blob==recovery_blob,
                'recovery_eol_only_difference':blob!=recovery_blob,'recovery_XML_tree_identical':True,
                'assembly_byte_identical':True})
    inventory.append({'book':roman,'branch':branch,'delivery_commit':commit,'qa_path':qa_path,
        'data_verdict':qa.get('DATA_verdict',qa.get('DATA',qa.get('data_checks'))),
        'renderer_verdict':qa.get('RENDERER_verdict','RENDERER-NO-GO'),
        'certification':qa.get('certification'), 'unexplained_changes':qa.get('unexplained_textual_changes'),
        'archive':str(archive),'archive_sha256':sha(raw_archive),'archive_entries':len(names),
        'verified_manifest_entries':verified,'archive_crc_pass':True,'outputs':outputs})
    print(roman, commit, len(positions), verified, flush=True)
assert len(oracle)==3821, len(oracle)
for name,data in [('SOURCE_INVENTORY.json',inventory),('INTERVAL_ORACLE.json',oracle)]:
    (PACK/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if (PACK/'PROTECTED_START.json').exists():
    print('All 3821 certified intervals assembled; original protection snapshot retained.')
    raise SystemExit(0)
protections = {}
for branch in ['v2-development','pilot/whiston-antiquities-book12-20261011','pilot/whiston-antiquities-book13-20261011']:
    commit = git('rev-parse',branch).decode().strip()
    worktree = CANON if branch=='v2-development' else Path('C:/workspace/LatinJosephus-Book'+('XII' if 'book12' in branch else 'XIII')+'-Pilot-20261011')
    protections[branch]={'commit':commit,'worktree':str(worktree),'status':git('status','--porcelain',cwd=worktree).decode(),
        'working_files':{p:sha((worktree/p).read_bytes()) for p in git('ls-files',cwd=worktree).decode().splitlines() if (worktree/p).is_file()}}
(PACK/'PROTECTED_START.json').write_text(json.dumps(protections,indent=2)+'\n',encoding='utf-8')
print('All 3821 certified intervals assembled; protected worktrees recorded.')
