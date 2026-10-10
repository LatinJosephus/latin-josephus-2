"""Allow only the two unchanged literal source-quote spaces in retained packets."""
from pathlib import Path
import subprocess,re,json,hashlib
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
def verify(committed=False):
    original_path='review/Antiquities_Niese_BookXVI_2026-10-09/DECISION_XVI_351_355_356.txt'
    historical_path=original_path.replace('.txt','_HISTORICAL_PRE_IMPLEMENTATION.txt')
    checkpoint=subprocess.check_output(['git','rev-parse','302e4d5'],cwd=ROOT).decode().strip()
    original=subprocess.check_output(['git','show',checkpoint+':'+original_path],cwd=ROOT)
    assert (ROOT/historical_path).read_bytes()==original
    assert (ROOT/original_path).read_bytes().endswith(original)
    literal=[line.decode('utf8') for line in original.splitlines() if line.endswith(b' ')];assert len(literal)==2
    base=json.loads((BATCH/'BASELINE.json').read_text(encoding='utf8'))['base_commit']
    args=['git','diff','--check',base]
    args+=['HEAD'] if committed else ['--','review']
    result=subprocess.run(args,cwd=ROOT,capture_output=True);assert not result.stderr
    output=result.stdout.decode('utf8');pattern=r'([^\n]+):(\d+): trailing whitespace\.\n\+([^\n]*)\n'
    matches=re.findall(pattern,output);assert len(matches)==4 and re.sub(pattern,'',output)==''
    assert all(path in [original_path,historical_path] and quote in literal for path,line,quote in matches)
    assert sorted(quote for path,line,quote in matches)==sorted(literal*2)
    return dict(status='PASS_ONLY_UNCHANGED_LITERAL_SOURCE_QUOTE_TRAILING_SPACES',
        source_audit_checkpoint=checkpoint,original_packet_sha256=hashlib.sha256(original).hexdigest(),
        historical_packet_byte_exact=True,current_packet_preserves_original_complete_bytes=True,
        expected_literal_quote_warnings=[dict(path=p,line=int(n),literal=q) for p,n,q in matches],
        production_whitespace_check='PASS_SEPARATE_STRICT_CHECK',normalization_forbidden_to_preserve_literal_scholarly_record=True)
if __name__=='__main__':
    report=verify();(BATCH/'LITERAL_REVIEW_WHITESPACE_PROOF.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(report['status'])
