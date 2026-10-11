import postrelease_reader as a
import subprocess,sys,os,shutil

def prepare():
    src=(a.P/'qa/critical-controls.cjs').read_text()
    src=src.split('  // Reproduce only the exact historically certified unsupported Book-I route')[0]
    src=src.replace("const P=__dirname;","const P=c.runtime;")
    src += '''  report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e}finally{report.finished=new Date().toISOString();fs.writeFileSync(path.join(P,'PROTECTED_CONTROLS.json'),JSON.stringify(report,null,2)+'\\n');await context.close();await new Promise(r=>server.close(r))}
 console.log('Protected unmodified reader',report.status,report.critical.length);
}
main().catch(e=>{console.error(e);process.exitCode=1});
'''
    (a.T/'qa/protected-controls.cjs').write_text(src,encoding='utf8',newline='\n')
    # Preserve the baseline harness; add actual URL assertions to the final replay only.
    source=(a.T/'qa/all-niese.cjs').read_text()
    source=source.replace('r.rows.push({book,n,languages:',"c.assert.equal(new URL(p.url()).searchParams.get('niese'),String(n),'Actual route number');r.rows.push({book,n,URL:p.url(),languages:")
    (a.T/'qa/all-niese-final.cjs').write_text(source,encoding='utf8',newline='\n')
    source=a.Path('postrelease_focused_test.cjs').read_text().replace("stage+'-site'","stage==='final'?'candidate-final-site':stage+'-site'")
    a.Path('postrelease_focused_test.cjs').write_text(source,encoding='utf8',newline='\n')
    print('Prepared final-only replay and protected controls; baseline harness unchanged')

jobs={
'niese':[['qa/all-niese-final.cjs','candidate-final']],
'structural':[['qa/reader-structure-crosswork.cjs','--final'],['qa/containing-real.cjs']],
'focused':[['postrelease_theme_final.cjs'],['postrelease_focused_test.cjs','final'],['postrelease_invalid_test.cjs','final'],['qa/VII1-7-source-display.cjs','candidate'],['qa/VII1-context-regression.test.cjs',str(a.T/'candidate-final-site'),'candidate'],['qa/combined-context.test.cjs'],['qa/context-guards.cjs'],['qa/targeted-ui.cjs'],['qa/VII2-6-navigation.cjs'],['qa/keyboard-full-source.cjs'],['qa/protected-controls.cjs'],['postrelease_reproduce.cjs','candidate-final']]}
def run(job):
    env={**os.environ,'PLAYWRIGHT_MODULE':a.PW,'REPAIR_RUNTIME':str(a.T),'QA_RUN_SUFFIX':'-aggregate-1'}
    results=[]
    for i,args in enumerate(jobs[job]):
        p=a.T/args[0] if args[0].startswith('qa/') else a.Path(args[0]).resolve()
        log=a.T/'logs'/f'FINAL-{job}-{i+1}.log'
        print('START',job,i+1,p.name,flush=True)
        with log.open('wb') as f:r=subprocess.run([a.NODE,str(p),*args[1:]],cwd=p.parent,env=env,stdout=f,stderr=subprocess.STDOUT)
        results.append({'script':str(p),'args':args[1:],'script_SHA256':a.sha(p.read_bytes()),'log':str(log),'exit_code':r.returncode})
        a.save(a.T/('FINAL_JOB_'+job+'.json'),{'job':job,'results':results,'status':'RUNNING'})
        print('DONE',job,i+1,'exit',r.returncode,log.read_text(errors='replace')[-600:],flush=True)
        if job=='structural' and i==0 and r.returncode==0:shutil.copy2(a.T/'qa/READER_FINAL_PRIOR_RESULTS.json',a.T/'READER_FINAL_PRIOR_RESULTS.json')
    a.save(a.T/('FINAL_JOB_'+job+'.json'),{'job':job,'results':results,'status':'PASS' if all(x['exit_code']==0 for x in results) else 'FAIL'})

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run(sys.argv[1])
