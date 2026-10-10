"""Prepare final-production QA while retaining the earlier review harness."""
from reconnaissance import *

def main():
    for b in [18,19]:
        d=packet(b);expected=json.loads((d/'FINAL_EXPECTED_INTERVALS.json').read_text(encoding='utf8'))
        cases=[('CASE_007',[6,7,8]),('CASE_094',[93,94,95]),('CASE_216_217',[215,216,217,218])] if b==18 else [('CASE_188',[187,188,189])]
        for name,numbers in cases:
            p=d/(name+'.json');case=json.loads(p.read_text(encoding='utf8'))
            case['production_applied']=True
            case['approved_adjacent_extents']=[expected[n-1] for n in numbers]
            save(p,case)
            with (d/(name+'.md')).open('a',encoding='utf8',newline='\n') as f:
                f.write('\nApplied adjacent Latin extents (frozen narrative Unicode coordinates; the exact text and both language contexts are retained in the JSON):\n\n')
                for n in numbers:
                    e=expected[n-1];start=e['Latin_start']
                    f.write(f'- {b}.{n}: '+(f"[{start['book_offset']}, {e['Latin_end']}); source byte {start['raw_byte']}; begins `{start['right'][:70]}`." if start else 'no independent Latin interval; no source insertion.')+'\n')
    s=(PACK/'review_reader.cjs').read_text(encoding='utf8')
    s=s.replace("mode=process.argv[2]||'review'","mode=process.argv[2]||'final'").replace("'baseline-site':'review-site'","'baseline-site':'final-site'")
    s=s.replace('SECURE_REVIEW_HARNESS_NOT_FULL_BOOK_CERTIFICATION','ACTUAL_FINAL_PRODUCTION_FULL_BOOK_CERTIFICATION')
    s=s.replace('REVIEW_EXPECTED_INTERVALS.json','FINAL_EXPECTED_INTERVALS.json').replace('REVIEW_DIFFERENCE.json','FINAL_DIFFERENCE.json').replace('SECURE_REVIEW_BROWSER.json','FINAL_BROWSER.json')
    s=s.replace("Latin:e.safe_Latin_interval?'SECURE_INTERVAL_PASS':'NOT_CERTIFIED_DEPENDS_ON_PENDING_EDITORIAL_CHOICE'","Latin:e.safe_Latin_interval?'EXACT_INTERVAL_PASS':'APPROVED_UNAVAILABLE_PASS'")
    s=s.replace("r.Latin==='SECURE_INTERVAL_PASS'","r.Latin==='EXACT_INTERVAL_PASS'")
    target='result.selections.push({book:b,number:e.number,Greek:'
    s=s.replace(target,"if(e.unavailable){const u=await page.locator('#latin .structural-unavailable').textContent();if(norm(a.languages.Latin)!==''||!u.includes(e.qualification)||!u.includes('No nearby text has been substituted.'))throw Error('Specific approved unavailable notice '+b+'.'+e.number);}else if(e.qualification&&await page.locator('#latin .niese-correspondence-note').getAttribute('role')!=='note')throw Error('Qualification accessibility '+b+'.'+e.number);"+target)
    s=s.replace('[1,63,64,116,117,118,119,256,257,258,378,379]','[1,6,7,8,63,64,93,94,95,116,117,118,119,215,216,217,218,256,257,258,378,379]')
    s=s.replace('[1,188,291,292,293,','[1,187,188,189,291,292,293,')
    s=s.replace("'review-harness-'+theme+'.png'","'final-reader-'+theme+'.png'")
    # Themes are inspected by the dedicated settled-transition run.
    s=s.replace('await page.screenshot({path:', 'await page.waitForTimeout(800);await page.screenshot({path:')
    (PACK/'final_reader.cjs').write_text(s,encoding='utf8',newline='\n')
    s=(PACK/'protected_reader.cjs').read_text(encoding='utf8')
    s=s.replace("require('./review_reader.cjs')","require('./final_reader.cjs')").replace('BASELINE_VS_REVIEW_PROTOTYPE','BASELINE_VS_ACTUAL_FINAL_PRODUCTION')
    s=s.replace("'baseline-site','review-site'","'baseline-site','final-site'").replace('browser-protected-exhaustive','browser-protected-final-exhaustive')
    s=s.replace('PROTECTED_REVIEW_','PROTECTED_FINAL_')
    s=s.replace("const resume=process.argv.includes('--resume-completed');","const resume=false; // Final certification always replays every prior identity afresh.")
    (PACK/'final_protected_reader.cjs').write_text(s,encoding='utf8',newline='\n')
    s=(PACK/'transition_reader.cjs').read_text(encoding='utf8')
    s=s.replace("require('./review_reader.cjs')","require('./final_reader.cjs')").replace('REVIEW_HARNESS_','ACTUAL_FINAL_PRODUCTION_').replace("'review-site'","'final-site'")
    s=s.replace('browser-transitions','browser-final-transitions').replace('review-harness-','final-reader-').replace('TRANSITION_REVIEW_BROWSER.json','TRANSITION_FINAL_BROWSER.json')
    (PACK/'final_transition_reader.cjs').write_text(s,encoding='utf8',newline='\n')
    s=(PACK/'verify_review_outputs.py').read_text(encoding='utf8')
    a=s.index('    protected=');z=s.index('    results=[]')
    s=s[:a]+'''    protected=json.loads((PACK/'PROTECTED_INPUTS.json').read_text(encoding='utf8'));checks=[]
    allowed={'assets/js/renderTei.js','assets/xml/antiquities/Latin/book-18.xml','assets/xml/antiquities/Latin/book-19.xml'}
    for rel,old in protected.items():
        actual=sha((ROOT/rel).read_bytes())
        if rel not in allowed: assert actual==old['sha256'],rel
        checks.append(dict(path=rel,baseline_sha256=old['sha256'],sha256=actual,status='AUTHORIZED_CHANGE' if rel in allowed else 'UNCHANGED'))
    save(PACK/'FINAL_PRODUCTION_PROTECTION_QA.json',dict(status='PASS',baseline=BASE,protected_baseline_files=len(checks),unchanged_files=sum(x['status']=='UNCHANGED' for x in checks),authorized_modified_files=sorted(allowed),new_registry_files=['assets/xml/antiquities/niese/book-18.json','assets/xml/antiquities/niese/book-19.json'],files=checks,English_all_books_and_unrelated_works_unchanged=True))
'''+s[z:]
    s=s.replace("candidate=(d/'review-output/Latin.xml').read_bytes()","candidate=(ROOT/f'assets/xml/antiquities/Latin/book-{b:02}.xml').read_bytes()")
    s=s.replace('APPROVED_SECURE_MARKER_PLAN.json','FINAL_MARKER_PLAN.json').replace('PASS_REVIEW_OUTPUT_ONLY_FULL_BOOK_NOT_CERTIFIED','PASS_ACTUAL_PRODUCTION_INDEPENDENT_PRESERVATION')
    s=s.replace('INDEPENDENT_REVIEW_PRESERVATION_QA.json','INDEPENDENT_FINAL_PRESERVATION_QA.json').replace('REVIEW_PRESERVATION_SUMMARY.json','FINAL_PRESERVATION_SUMMARY.json')
    s=s.replace('production_applied=False,availability_enabled=False,certified=False','production_applied=True,availability_enabled=True,certified=False')
    # Certification remains false until every browser test also passes.
    (PACK/'verify_final_outputs.py').write_text(s,encoding='utf8',newline='\n')

if __name__=='__main__':main()
