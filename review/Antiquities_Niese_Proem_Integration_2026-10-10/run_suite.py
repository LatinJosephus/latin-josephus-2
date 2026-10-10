from pathlib import Path
import subprocess,json,sys,os,datetime,hashlib
P=Path(__file__).resolve().parent
RUNTIME=Path(r'C:\workspace\Antiquities-Niese-Proem-Integration-runtime-20261010')
GROUPS={
 'corpus':[['proem_browser.cjs'],['plain_browser.cjs'],['plain_final_controls.cjs'],['protected_browser.cjs','final']],
 'xi':[['reader-xi.cjs'],['xi-witness-order.cjs'],['reader-extra.cjs']],
 'crosswork':[['reader-structure-crosswork.cjs','--final'],['focused_controls.cjs'],['combined-extra.cjs'],['final_source_controls.cjs'],['interface_controls.cjs']],
 'special':[['new-books-browser.cjs'],['bookxx_browser.cjs'],['combined_cases_browser.cjs'],['closure_browser.cjs'],['xx_controls.cjs'],['prove_range_end.cjs','final']]
}
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
    name=sys.argv[1];report={'group':name,'status':'RUNNING','build':json.loads((P/'CANDIDATE_BUILD.json').read_text()),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scripts':[]}
    env=os.environ.copy();env['NIESE_QA_PORT']='8959' if name=='special' else '8956';env['NIESE_QA_PROFILE']=name
    receipt=P/('SUITE_'+name+'.json');save(receipt,report)
    for args in GROUPS[name]:
        log=RUNTIME/'logs'/('-'.join([name,args[0]])+'.log')
        print('START',name,*args,flush=True)
        with log.open('wb') as f:r=subprocess.run(['node',str(P/args[0]),*args[1:]],cwd=P,env=env,stdout=f,stderr=subprocess.STDOUT)
        row={'script':args,'exit_code':r.returncode,'script_sha256':hashlib.sha256((P/args[0]).read_bytes()).hexdigest(),'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()};report['scripts'].append(row)
        print(log.read_text(encoding='utf-8',errors='replace')[-1400:],flush=True)
        if r.returncode:report['status']='FAIL';save(receipt,report);raise SystemExit(r.returncode)
        save(receipt,report)
    report['status']='PASS';report['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(receipt,report);print('PASS SUITE',name,flush=True)
if __name__=='__main__':main()
