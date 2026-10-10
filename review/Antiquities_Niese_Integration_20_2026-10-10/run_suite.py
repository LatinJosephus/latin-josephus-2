from integration_common import *
NODE=r'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt\dependencies\node\bin\node.exe'
GROUPS={
 'xx-final':[['protected_browser.cjs','final'],['bookxx_browser.cjs'],['combined_cases_browser.cjs'],['protected_controls_browser.cjs','baseline'],['protected_controls_browser.cjs','final'],['notice_visual_browser.cjs'],['closure_browser.cjs'],['prove_range_end.cjs','baseline'],['prove_range_end.cjs','final']],
 '18-19':[['final_reader.cjs','baseline'],['final_reader.cjs','final'],['final_legacy_distinct_reader.cjs'],['combined-extra.cjs'],['final_source_controls.cjs']],
 'xi-witness':[['xi-witness-order.cjs']]
}
def main():
    group=sys.argv[1];runs=[];todo=GROUPS[group]
    if '--resume-after-harness-repair' in sys.argv:
        old=read(PACK/('SUITE_'+group+'.json'));assert group=='18-19' and old['status']=='FAIL' and len(old['runs'])==3
        assert all(r['exit_code']==0 for r in old['runs'][:2]) and old['runs'][2]['args']==['final_legacy_distinct_reader.cjs']
        save(PACK/'HARNESS_OFFSET_INITIAL_ATTEMPT.json',old)
        save(PACK/'QA_HARNESS_REPAIR.json',dict(status='DOCUMENTED',failure='Copied physical-point test used qa-common18 narrative, which normalizes whitespace before counting original Unicode characters.',cause='Integration test adapter changed the imported raw narrative helper, while coordinate oracle retains original source whitespace.',repair='Restore the original final_reader.cjs raw-text helper; no production changes. Rerun all 29 legacy URLs, all six physical-point coordinates and subsequent combined/source-control checks.',initial_result=read(PACK/'LEGACY_DISTINCT_FINAL_BROWSER.json'),initial_attempt=info(PACK/'HARNESS_OFFSET_INITIAL_ATTEMPT.json'),successful_unchanged_core_gates=[info(PACK/'BASELINE_CONTAINING_BROWSER.json'),info(PACK/'FINAL_BROWSER.json')]))
        runs=old['runs'][:2];todo=todo[2:]
    for args in todo:
        result=subprocess.run([NODE,*args],cwd=PACK,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log=RUNTIME/('QA-'+group+'-'+args[0]+('-'+args[1] if len(args)>1 else '')+'.log');log.write_bytes(result.stdout)
        record=dict(args=args,exit_code=result.returncode,log=info(log));runs.append(record)
        save(PACK/('SUITE_'+group+'.json'),dict(status='RUNNING' if result.returncode==0 else 'FAIL',runs=runs))
        print(result.stdout.decode('utf-8',errors='replace')[-2500:],flush=True)
        assert result.returncode==0,args
    save(PACK/('SUITE_'+group+'.json'),dict(status='PASS',runs=runs));print('PASS suite '+group,flush=True)
if __name__=='__main__':main()
