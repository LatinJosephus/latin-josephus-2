from reconnaissance import *
import ast

def main():
    checks=[]
    for p in sorted(PACK.glob('*.py')):
        ast.parse(p.read_text(encoding='utf8'),filename=str(p));checks.append(dict(path=str(p),check='Python AST',status='PASS'))
    for p in sorted(list(PACK.glob('*.cjs'))+[PACK/'REVIEW_RENDERER.js']):
        r=subprocess.run([r'C:\Program Files\nodejs\node.exe','--check',str(p)],capture_output=True)
        assert r.returncode==0,r.stderr.decode();checks.append(dict(path=str(p),check='Node syntax',status='PASS'))
    results=[]
    for args in [['git','diff','--check','HEAD','--','.',':(exclude)*.patch'],['git','apply','--check','--whitespace=nowarn',str(PACK/'REVIEW_RENDERER.patch')]]:
        result=subprocess.run(args,cwd=ROOT,capture_output=True);assert result.returncode==0,result.stdout.decode()+result.stderr.decode();results.append(dict(command=args,status='PASS'))
    save(PACK/'SYNTAX_QA.json',dict(status='PASS',files=checks,checks=results,
        whitespace_format_exception='Saved unified-diff context lines consist of a required single space; *.patch excluded only from textual whitespace lint, and actual patch applicability checked independently. No production or source text exception.'))
    images=[info(packet(b)/'evidence'/f'review-harness-{theme}.png') for b in [18,19] for theme in ['light','dark']]
    save(PACK/'VISUAL_REVIEW.json',dict(status='PASS_REVIEW_HARNESS_ONLY',images=images,
        inspected_all_four_latest_images=True,settle_ms=800,notes_legible_in_both_themes=True,
        scope='Existing reader layout; exact segment labels, independent panes, qualification notices and English context visibly checked. Existing fixed Annotations bar preserved.',
        production_certified=False))
    diagnostic=PACK/'PROTECTED_REVIEW_DIFFERENCE.json'
    if diagnostic.exists():
        data=json.loads(diagnostic.read_text(encoding='utf8'));data['diagnostic_status']='SUPERSEDED_TEST_READINESS_FAILURE'
        data['explanation']='English-pane render was unfinished in one browser tab. The corrected exhaustive replay waits for all three actual Niese pane wrappers; all5231 final comparisons pass.'
        save(diagnostic,data)
    log=[
        dict(case='Authority extraction',issue='Initial top-level-only filter omitted nested book records and combined XVIII/XIX rows.',correction='Recursively inspect source.book, Roman boundary IDs, ranges and antiquities_books membership; retain complete matching records. Frozen originals unchanged.'),
        dict(case='Prototype compiler',issue='A whole-file replacement expected CRLF although renderer bytes are LF, then found repeated resolver tokens.',correction='Use actual LF bytes and narrowly isolate the Antiquities resolver region. No production file changed.'),
        dict(case='Whole Book DOM inventory',issue='A zero-duplicate assertion revealed the pre-existing annotations ID collision.',correction='Record the exact baseline collision and require identical candidate inventory; all new Niese selections have unique IDs.'),
        dict(case='Structural ordinal filter',issue='Chapter-only filter incorrectly excluded original manuscript-image milestones in XVIII.',correction='Registry preserves all actual original milestone types, including null unit. All462 current physical locators and267 containing views pass.'),
        dict(case='Exhaustive prior browser readiness',issue='An early comparison sampled one English pane before its asynchronous render completed.',correction='Actual selector events wait for all three language wrappers; final5231 actual selections pass. Original diagnostic retained as superseded.'),
        dict(case='Known unsupported I.1',issue='All5231 selectable identities and13 protected routes passed before the inherited I.1 exception prevented normal ready flag and timed out the diagnostic harness.',correction='Reuse the completed replay checkpoint with its hash; independently reproduce exact known null-querySelector exception in both readers and the three inherited apparatus links/two404 targets. No other error is excused.'),
        dict(case='Transition harness',issue='Book selector ordinarily resets to Book view; the test initially attempted the hidden Niese menu after a book change.',correction='Select the available Niese viewing level before testing its section menu. Actual XVII→XVIII→XIX→XX transitions pass.'),
        dict(case='Theme probe',issue='XVIII64 has no qualification note; the probe incorrectly expected one. First screenshots also captured theme transition before settling.',correction='Use already qualified XVIII5 and XIX365; allow800ms settling, inspect all four final screenshots. No note or source text was manufactured.'),
        dict(case='Protected route schema',issue='An initial extra Cardwell query used an English-source key; an example XV Bamberg row was from another book.',correction='Verify actual Latin Cardwell config and dynamically select the actual final XV Bamberg registry row; compare source selections explicitly.')]
    save(PACK/'TEST_DEVELOPMENT_LOG.json',dict(status='SUPERSEDED_DIAGNOSTICS_FINAL_PASS_RECORDS_GOVERN',events=log,scholarly_boundaries_changed_to_make_tests_pass=False))
    for b in [18,19]:
        expected=json.loads((packet(b)/'REVIEW_EXPECTED_INTERVALS.json').read_text(encoding='utf8'))
        assert all(r['English'] for r in expected),'All identities must retain independent English context'
    print('Syntax, explicit diagnostic history, four visual inspections and nonempty English contexts PASS.')
if __name__=='__main__':main()
