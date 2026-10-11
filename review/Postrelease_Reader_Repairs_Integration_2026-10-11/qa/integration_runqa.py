import reader_integration as a
import subprocess,os,sys,shutil

def jobs():
    return {
    'baseline':[['all-niese.cjs','baseline']],
    'niese':[['all-niese-final.cjs','candidate-final']],
    'structural':[['reader-structure-crosswork.cjs','--final'],['containing-real.cjs'],['containing-ids-real.cjs']],
    'focused':[['postrelease_theme_final.cjs'],['postrelease_focused_test.cjs','final'],['postrelease_invalid_test.cjs','final'],['VII1-7-source-display.cjs','candidate'],['VII1-context-regression.test.cjs',str(a.T/'candidate-final-site'),'candidate'],['combined-context.test.cjs'],['context-guards.cjs'],['targeted-ui.cjs'],['VII2-6-navigation.cjs'],['keyboard-full-source.cjs'],['protected-controls.cjs'],['postrelease_reproduce.cjs','candidate-final'],['postrelease_general_navigation.cjs'],['postrelease_screens.cjs']]}
def run(job):
    a.saved();env={**os.environ,'PLAYWRIGHT_MODULE':a.u.PW,'REPAIR_RUNTIME':str(a.T),'REPAIR_ROOT':str(a.W),'QA_RUN_SUFFIX':'-integration-fresh-1'}
    rows=[]
    for i,args in enumerate(jobs()[job]):
        script=a.T/'qa'/args[0];log=a.T/'logs'/('QA-'+job+'-'+str(i+1)+'.log')
        print('START',job,i+1,script.name,flush=True)
        with log.open('wb') as f:r=subprocess.run([a.u.NODE,str(script),*args[1:]],cwd=a.T/'qa',env=env,stdout=f,stderr=subprocess.STDOUT)
        rows.append({'script':str(script),'script_SHA256':a.u.sha(script.read_bytes()),'args':args[1:],'log':str(log),'exit_code':r.returncode})
        a.u.save(a.T/('QA_JOB_'+job+'.json'),{'status':'RUNNING','results':rows})
        print('DONE',job,i+1,'exit',r.returncode,log.read_text(errors='replace')[-700:],flush=True)
        if job=='structural' and i==0 and r.returncode==0:shutil.copy2(a.T/'qa/READER_FINAL_PRIOR_RESULTS.json',a.T/'READER_FINAL_PRIOR_RESULTS.json')
    a.u.save(a.T/('QA_JOB_'+job+'.json'),{'status':'PASS' if all(r['exit_code']==0 for r in rows) else 'FAIL','results':rows})

if __name__=='__main__':run(sys.argv[1])
