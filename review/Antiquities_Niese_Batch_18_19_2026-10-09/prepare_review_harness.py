"""Build a concrete, reversible review implementation without closing human gates.

No production file or public availability is changed. Only approved secure
Latin starts enter the candidate XML. The reader prototype reuses declared
physical locators rather than manufacturing coincident anchors.
"""
from reconnaissance import *
from mixed_mapper import Book
import difflib

def main():
    site=RUNTIME/'review-site'
    if not site.exists():shutil.copytree(RUNTIME/'baseline-site',site)
    for b in [18,19]:
        d=packet(b);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        plan=json.loads((d/'APPROVED_SECURE_MARKER_PLAN.json').read_text(encoding='utf8'))
        raw=(d/'frozen-inputs/Latin.xml').read_bytes();assert sha(raw)==plan['source_sha256']
        output=raw;ops=plan['markers']
        for op in sorted(ops,key=lambda x:x['at'],reverse=True):
            output=output[:op['at']]+op['marker'].encode()+output[op['at']:]
        inverse=[];shift=0
        for op in sorted(ops,key=lambda x:x['at']):
            inverse.append(dict(number=op['number'],at=op['at']+shift,length=len(op['marker'].encode()),expected=op['marker']))
            shift+=len(op['marker'].encode())
        recovered=output
        for op in reversed(inverse):
            assert recovered[op['at']:op['at']+op['length']]==op['expected'].encode()
            recovered=recovered[:op['at']]+recovered[op['at']+op['length']:]
        assert recovered==raw
        old,new=Book(raw=raw),Book(raw=output)
        assert old.stream==new.stream
        assert old.tree.xpath('//@xml:id')==new.tree.xpath('//@xml:id')
        assert old.tree.xpath('//@sameAs')==new.tree.xpath('//@sameAs')
        outdir=d/'review-output';outdir.mkdir(exist_ok=True)
        (outdir/'Latin.xml').write_bytes(output)
        (site/f'assets/xml/antiquities/Latin/book-{b:02}.xml').write_bytes(output)
        save(d/'SECURE_REVIEW_IMPLEMENTATION.json',dict(book=b,scope='REVIEW_OUTPUT_ONLY_NOT_PRODUCTION',
            baseline=BASE,source_sha256=sha(raw),output_sha256=sha(output),recovered_sha256=sha(recovered),
            byte_exact_inverse=True,narrative_identical=True,existing_ids_sameAs_identical=True,
            new_markers=len(ops),reused_physical_starts=len(plan['reused_physical_starts']),
            retained_numeric_starts=len(plan['retained_starts']),pending_sections=plan['pending_sections'],
            operations=ops,inverse_operations=inverse,availability_enabled=False,full_book_certified=False))
        reused={r['number']:r for r in plan['reused_physical_starts']}
        expected=[];sections=[]
        models={l:Book(raw=(d/'frozen-inputs'/f'{l}.xml').read_bytes()) for l in ['Latin','Greek','English']}
        for r in rows:
            c=r['candidate'];n=r['number'];approved=c.get('approved',False);loc=c.get('locator')
            latin=dict(available=bool(approved and loc),correspondence=c['correspondence'],note=c.get('note'))
            if n in reused:latin['start']=reused[n]['physical_locator']
            if not approved:latin['note']='Editorial choice pending. This review harness makes no certified Latin availability claim.'
            section=dict(number=n,Latin=latin,contextTarget=(loc or {}).get('stable_id') or r['Latin_alignment_paragraph'])
            if n==1:section['Greek']=dict(available=True,start=dict(available='true',kind='anchor',target=r['Greek_physical_start']['target']))
            sections.append(section)
            later=next((z for z in rows[n:] if z['candidate'].get('locator')),None)
            end=later['candidate']['locator']['book_offset'] if later else len(old.stream)
            safe=bool(approved and loc and not any(not z['candidate'].get('approved') for z in rows[n:(later['number'] if later else len(rows))]))
            ctx=section['contextTarget']
            ep=[u for u in models['English'].units if u['element'].get('sameAs','')=='#'+ctx]
            expected.append(dict(number=n,safe_Latin_interval=safe,
                Latin=old.stream[loc['book_offset']:end] if safe else None,
                Greek=r['Greek_text'],English=''.join(u['text'] for u in ep),
                Latin_start=loc,Latin_end=end if safe else None,context_target=ctx,
                qualification=c.get('note'),pending=not approved))
        original_units=list(dict.fromkeys(e.get('unit') for m in models.values() for e in m.tree.xpath('//t:milestone',namespaces=NS)))
        registry=dict(schema=1,book=b,range=[1,len(rows)],status='REVIEW_HARNESS_ONLY_HUMAN_GATES_PENDING_DO_NOT_ENABLE_PRODUCTION',
                      structuralMilestoneUnits=original_units,suppressedLatinLabels=[],sections=sections)
        save(d/'REVIEW_IDENTITY_REGISTRY.json',registry);save(d/'REVIEW_EXPECTED_INTERVALS.json',expected)
        save(site/f'assets/xml/antiquities/niese/book-{b:02}.json',registry)
        print(b,'candidate XML',len(ops),'new milestones;',len(reused),'physical reuses;',sum(r['safe_Latin_interval'] for r in expected),'secure intervals for browser comparison')

    original=(ROOT/'assets/js/renderTei.js').read_bytes();s=original.decode('utf8')
    s=s.replace('        15: "assets/xml/antiquities/niese/book-15.json"',
                '        15: "assets/xml/antiquities/niese/book-15.json",\n        18: "assets/xml/antiquities/niese/book-18.json",\n        19: "assets/xml/antiquities/niese/book-19.json"')
    full=s; a=s.index('  const antiquitiesNieseStartEntries = '); z=s.index('  const antiquitiesNieseContextView = ')
    s=s[a:z]
    token='    const entries = [];\n\n    data.querySelectorAll("tei-num")'
    assert s.count(token)==1
    s=s.replace(token,'    const entries = [];\n    const declared = nieseIdentityRegistry()?.sections.filter(section => section[language]?.start) || [];\n\n    data.querySelectorAll("tei-num")')
    token='      if (!Number.isInteger(number) || number < first || number > last) return;\n\n      entries.push({'
    assert s.count(token)==1
    s=s.replace(token,'      if (!Number.isInteger(number) || number < first || number > last\n        || declared.some(section => section.number === number)) return;\n\n      entries.push({')
    token='    entries.sort((a, b) => {\n      if (a.node === b.node) return 0;\n\n      const position = a.node.compareDocumentPosition(b.node);'
    assert s.count(token)==1
    s=s.replace(token,'    declared.forEach(section => {\n      const point = traditionalPoint(data, section[language].start);\n      if (point) entries.push({number: section.number, kind: "physical", node: point.node, physicalKind: point.kind});\n    });\n\n'+token)
    token='      if (start.kind === "num") {\n        range.setStartBefore(start.node);'
    assert s.count(token)==1
    s=s.replace(token,'      if (start.kind === "physical" && start.physicalKind === "paragraph") {\n        range.setStart(start.node, 0);\n      } else if (start.kind === "num" || start.kind === "physical") {\n        range.setStartBefore(start.node);')
    token='      range.setEndBefore(end.node);\n      paragraphWrapper.appendChild'
    assert s.count(token)==1
    s=s.replace(token,'      if (end.kind === "physical" && end.physicalKind === "paragraph") range.setEnd(end.node, 0);\n      else range.setEndBefore(end.node);\n      paragraphWrapper.appendChild')
    token='        range.setEndBefore(endNode);\n      } else {'
    assert s.count(token)==1
    s=s.replace(token,'        if (end.kind === "physical" && end.physicalKind === "paragraph") range.setEnd(end.node, 0);\n        else range.setEndBefore(endNode);\n      } else {')
    token='    if (start.kind === "milestone") {\n      const firstParagraph'
    assert s.count(token)==1
    s=s.replace(token,'    if (start.kind === "milestone" || start.kind === "physical") {\n      const firstParagraph')
    s=full[:a]+s+full[z:]
    candidate=s.encode('utf8');(PACK/'REVIEW_RENDERER.js').write_bytes(candidate)
    (site/'assets/js/renderTei.js').write_bytes(candidate)
    patch=''.join(difflib.unified_diff(original.decode().splitlines(True),s.splitlines(True),fromfile='baseline/assets/js/renderTei.js',tofile='review/assets/js/renderTei.js'))
    (PACK/'REVIEW_RENDERER.patch').write_text(patch,encoding='utf8',newline='')
    save(PACK/'REVIEW_HARNESS_PROVENANCE.json',dict(scope='DISPOSABLE_REVIEW_IMPLEMENTATION_NOT_CERTIFIED_PRODUCTION',
        site=str(site),baseline_build='BASELINE_BUILD.json',production_renderer_sha256=sha(original),
        prototype_renderer_sha256=sha(candidate),changes='Generic per-language declarative start locators resolved by current traditionalPoint; review-only 18/19 registry map',
        production_files_changed=False,human_choices_applied=False,pending_choices_represented_as_uncertified_harness_notice=True))
if __name__=='__main__':main()
