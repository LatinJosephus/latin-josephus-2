import postrelease_reader as a
import postrelease_stage as s
import shutil,sys,subprocess

files={
'A':['_includes/header.html','assets/js/theme.js','assets/js/dark_mode.js','_sass/_branding.scss'],
'B':['_includes/annotations-bar.html','assets/js/renderTei.js','_sass/_antiquities.scss','_sass/_reader-ui.scss'],
'D':['assets/js/renderTei.js'],
'E':['assets/js/renderTei.js']}
messages={'A':'Name the theme button and preserve keyboard and theme state',
'B':'Separate the annotation panel ID from preserved TEI standOff IDs',
'D':'Initialize the shared reader only on reader pages',
'E':'Reject unsupported Antiquities Niese requests without selecting substitute text'}
def package(p):
    result=a.load(a.T/('PACKAGE_'+p+'_'+p+'.json'))
    assert result['result']=='PASS',result.get('failure')
    shutil.copy2(a.T/('PACKAGE_'+p+'_'+p+'.json'),a.Q/('PACKAGE_'+p+'.json'))
    shutil.copy2(a.T/('BUILD_'+p+'.json'),a.Q/('BUILD_'+p+'.json'))
    for f in ['postrelease_package.py','postrelease_edit.py','postrelease_'+('theme' if p=='A' else 'focused')+'_test.cjs']:
        if a.Path(f).exists():shutil.copy2(f,a.Q/f)
    subprocess.run(['git','add','--',*files[p]],cwd=a.W,check=True)
    s.commit('package-'+p,messages[p])

if __name__=='__main__':package(sys.argv[1])
