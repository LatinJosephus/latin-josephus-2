import postrelease_reader as a
import sys
def change(path,old,new):
    p=a.W/path;b=p.read_bytes();eol='\r\n' if b'\r\n' in b else '\n';s=b.decode('utf8');old=old.replace('\n',eol);new=new.replace('\n',eol);assert s.count(old)==1,(path,s.count(old));p.write_bytes(s.replace(old,new).encode('utf8'))
def A():
    change('_includes/header.html','<a id = "light-toggle">\n                  <i class="fas fa-moon"></i>\n                  <i class="fas fa-sun"></i>\n              </a>','<button id="light-toggle" type="button" aria-label="Dark mode" aria-pressed="false">\n                  <i class="fas fa-moon" aria-hidden="true"></i>\n                  <i class="fas fa-sun" aria-hidden="true"></i>\n              </button>')
    change('assets/js/theme.js','let setTheme = (theme) =>  {','let updateThemeControl = () => {\n  const control = document.getElementById("light-toggle");\n  if (control) {\n    control.setAttribute("aria-pressed", String(document.documentElement.dataset.theme === "dark"));\n  }\n};\n\nlet setTheme = (theme) =>  {')
    change('assets/js/theme.js','  localStorage.setItem("theme", theme);','  localStorage.setItem("theme", theme);\n  updateThemeControl();')
    change('assets/js/dark_mode.js','    const mode_toggle = document.getElementById("light-toggle");','    const mode_toggle = document.getElementById("light-toggle");\n    if (!mode_toggle) return;\n    updateThemeControl();')
    change('_sass/_branding.scss','/* Preserve Font Awesome glyphs in the dark-mode toggle.','/* Keep the existing icon-only appearance with native button semantics. */\n.lj-navbar #light-toggle {\n  border: 0;\n  background: transparent;\n  padding: 0;\n  color: inherit;\n  cursor: pointer;\n}\n\n.lj-navbar #light-toggle:focus-visible {\n  outline: 2px solid var(--lj-brand-accent);\n  outline-offset: 4px;\n}\n\n/* Preserve Font Awesome glyphs in the dark-mode toggle.')
def B():
    change('_includes/annotations-bar.html','id="annotations"','id="reader-annotations"')
    change('_includes/annotations-bar.html','data-mdb-parent="#annotations"','data-mdb-parent="#reader-annotations"')
    change('assets/js/renderTei.js','const annotationsPanel = document.getElementById("annotations");','const annotationsPanel = document.getElementById("reader-annotations");')
    for path in ['_sass/_antiquities.scss','_sass/_reader-ui.scss']:
        p=a.W/path;b=p.read_bytes();assert b'#annotations' in b;p.write_bytes(b.replace(b'#annotations',b'#reader-annotations'))
def D():
    change('assets/js/renderTei.js','  const activeWork = WORKS[window.location.pathname];','  const activeWork = WORKS[window.location.pathname];\n  // General site pages have no reader data contract or reader controls.\n  if (!activeWork || !bookTitle || !bookSelectMenu) return;')
if __name__=='__main__':globals()[sys.argv[1]]();print('Implemented package',sys.argv[1],'only in isolated worktree')
