"""Independent final marker-coordinate, interval-partition and evidence proof."""
from reconnaissance import *
from mixed_mapper import Book

def main():
    results=[]
    for b in [18,19]:
        d=packet(b);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        plan=json.loads((d/'FINAL_MARKER_PLAN.json').read_text(encoding='utf8'))
        expected=json.loads((d/'FINAL_EXPECTED_INTERVALS.json').read_text(encoding='utf8'))
        registry=json.loads((ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json').read_text(encoding='utf8'))
        frozen=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
        actual=Book(ROOT/f'assets/xml/antiquities/Latin/book-{b:02}.xml')
        markers={int(m[1]):m for m in re.finditer(rb'<milestone unit="niese" n="([1-9][0-9]*)"/>',actual.raw)}
        assert len(markers)==len(plan['markers'])
        for r in plan['markers']:
            point=actual.locate(r['locator']['book_offset'])
            assert markers[r['number']].end()==point['raw_byte'],(b,r['number'])
            assert point['stable_id']==r['locator']['stable_id'] and point['unit_offset']==r['locator']['unit_offset']
        positive=[r for r in expected if not r['unavailable']]
        assert ''.join(r['Latin'] for r in positive)==frozen.stream
        assert positive[0]['Latin_start']['book_offset']==0
        assert all(r['Latin_end']>r['Latin_start']['book_offset'] for r in positive)
        assert [r['Latin_end'] for r in positive[:-1]]==[r['Latin_start']['book_offset'] for r in positive[1:]]
        assert positive[-1]['Latin_end']==len(frozen.stream)
        assert [s['number'] for s in registry['sections']]==list(range(1,len(rows)+1))
        assert [s['number'] for s in registry['sections'] if not s['Latin']['available']]==plan['approved_unavailable_sections']
        if b==18:
            assert not ({216,217}&set(markers))
            assert expected[214]['Latin_end']==expected[217]['Latin_start']['book_offset']
            assert all(expected[n-1]['Greek'] and expected[n-1]['English'] and expected[n-1]['Latin'] is None for n in [216,217])
        for n,r in enumerate(rows,1):assert n==r['number'] and r['candidate']['approved'] and r['print_review_status']=='VISUALLY_REVIEWED'
        for language in ['Greek','English']:
            assert (ROOT/f'assets/xml/antiquities/{language}/book-{b:02}.xml').read_bytes()==(d/'frozen-inputs'/f'{language}.xml').read_bytes()
        mutable={'IDENTITIES.json','DECISION_HISTORY.json','CERTIFICATE.json','FILE_MANIFEST.json'}|{p.name for p in d.glob('CASE*')}
        history=json.loads((d/'history/pre-adjudication-1938fa0/FILE_MANIFEST.json').read_text(encoding='utf8'))
        evidence=[]
        for item in history['files']:
            p=Path(item['path'])
            if p.name in mutable:continue
            assert sha(p.read_bytes())==item['sha256'],str(p)
            evidence.append(dict(path=str(p.relative_to(ROOT)),sha256=item['sha256']))
        proof=dict(book=b,status='PASS',identities=len(rows),independent_Latin_intervals=len(positive),unavailable=plan['approved_unavailable_sections'],new_markers=len(markers),retained_numeric_starts=len(plan['retained_starts']),reused_physical_starts=len(plan['reused_physical_starts']),whole_Latin_narrative_partition_exact=True,marker_UTF8_points_independently_verified=True,Greek_English_byte_identical=True,preserved_primary_and_review_evidence=evidence,all_holds_closed=True)
        save(d/'INDEPENDENT_FINAL_LOGICAL_QA.json',proof);results.append(proof)
    archive=json.loads((PACK/'ADJUDICATION_ARCHIVE.json').read_text(encoding='utf8'))
    for item in archive['archived_files']:assert sha((ROOT/item['archive']).read_bytes())==item['sha256']
    save(PACK/'FINAL_LOGICAL_SUMMARY.json',dict(status='PASS',books=results,verbatim_HOLD_archive_verified_files=len(archive['archived_files'])))
    print('Independent final coordinates, complete Latin partition, all primary evidence and verbatim HOLD archives PASS.')

if __name__=='__main__':main()
