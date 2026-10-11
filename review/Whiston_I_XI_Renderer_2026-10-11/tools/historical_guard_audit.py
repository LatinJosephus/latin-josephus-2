from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[3];PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
rows=[]
reasons={
 'deh-parallels-qa.mjs':'Corpus-wide historical hash guard includes Antiquities files intentionally assembled from certified deliveries; the DEH/Bellum production inputs and full extraction harness are checked separately.',
 'bellum-greek-range-qa.mjs':'Launcher hardcodes 107 tracked XML files; pinned canonical already has 286. It exits before browser tests.',
 'lodge1602-bellum-qa.mjs':'Launcher expects its historical 100-file corpus inventory; pinned canonical now includes later paratext and registry additions. It exits before browser tests.'}
for name,reason in reasons.items():
    run=subprocess.run(['node','bin/'+name],cwd=ROOT,capture_output=True,timeout=30)
    output=run.stdout+run.stderr
    (PACK/(name+'.log')).write_bytes(output)
    assert run.returncode!=0,name
    current=(ROOT/'bin'/name).read_bytes()
    before=subprocess.check_output(['git','show','663b8ce:bin/'+name],cwd=ROOT)
    assert current.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n')
    rows.append({'launcher':name,'exit_code':run.returncode,'reason':reason,'launcher_unchanged_from_pin':True,'output_sha256':hashlib.sha256(output).hexdigest()})
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only','663b8ce'],cwd=ROOT).decode().splitlines()
(PACK/'HISTORICAL_GUARD_AUDIT.json').write_bytes((json.dumps({'historical_launchers':rows,'pinned_tracked_XML_files':len([p for p in tracked if p.endswith('.xml')]),'replacement_checks':'REGRESSION_QA.json, AUXILIARY_QA.json, SOURCE_PRESERVATION_QA.json','production_guard_functions_and_frozen_concordance_unchanged':True},indent=2)+'\n').encode())
print('Three historical launcher guards documented; current production-input and browser gates retained.')
