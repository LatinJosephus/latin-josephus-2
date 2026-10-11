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

def E():
    path='assets/js/renderTei.js'
    change(path,'  let canonicalViewData;','  let canonicalViewData;\n  let invalidNieseRequest = null;\n  let unsupportedNieseBook = null;')
    change(path,'      nieseNum: supportsNieseBook(bookNum) ? positive("niese") : null,','      // Retain explicit malformed requests so they receive a notice, not unrelated text.\n      nieseNum: supportsNieseBook(bookNum) && params.has("niese")\n        ? (positive("niese") ?? params.get("niese")) : null,\n      invalidNieseBook: params.has("niese") && rawBook !== null && rawBook !== "preface"\n        && !(/^[1-9]\\d*$/.test(rawBook) && Number(rawBook) <= activeWork.bookCount) ? rawBook : null,')
    change(path,'    const location = readTraditionalUrl();\n    Object.assign(state,','    const location = readTraditionalUrl();\n    unsupportedNieseBook = location.invalidNieseBook;\n    Object.assign(state,')
    change(path,'    } else if (state.nieseNum) {\n      state.viewingLevel = "niese-level";','    } else if (state.nieseNum !== null) {\n      state.viewingLevel = "niese-level";')
    change(path,'  const syncUrlFromState = (mode = "replace") => {','  const syncUrlFromState = (mode = "replace") => {\n    if (invalidNieseRequest) return; // Keep the typed unsupported URL and history intact.')
    change(path,'    canonicalViewData = selectCanonicalView(canonicalFullData, idBase);','''    invalidNieseRequest = null;
    if (activeWork.slug === "antiquities" && state.viewingLevel === "niese-level") {
      const entries = canonicalNieseStartEntries();
      if (unsupportedNieseBook !== null || !/^[1-9]\\d*$/.test(String(state.nieseNum))
        || !Number.isSafeInteger(Number(state.nieseNum))
        || !entries.some(entry => entry.number === Number(state.nieseNum))) {
        invalidNieseRequest = {number: state.nieseNum, book: unsupportedNieseBook,
          first: entries[0]?.number, last: entries.at(-1)?.number};
      }
    }
    canonicalViewData = invalidNieseRequest ? null : selectCanonicalView(canonicalFullData, idBase);''')
    change(path,'      viewData[language] = selectView(language, data, idBase);','      viewData[language] = invalidNieseRequest ? null : selectView(language, data, idBase);')
    change(path,'  const renderUI = () => {','''  const renderInvalidNieseNotice = () => {
    document.getElementById("unsupported-niese-notice")?.remove();
    if (!invalidNieseRequest) return;
    const panes = document.getElementById("pane-container");
    const notice = document.createElement("aside");
    notice.id = "unsupported-niese-notice";
    notice.className = "alert alert-secondary";
    notice.setAttribute("role", "alert");
    const description = document.createElement("p");
    description.textContent = invalidNieseRequest.book !== null
      ? `The requested Antiquities book "${invalidNieseRequest.book}" is unsupported. No passage is displayed.`
      : `Niese section "${invalidNieseRequest.number}" is unsupported in ${currentBookLabel()}. This selection supports sections ${invalidNieseRequest.first}–${invalidNieseRequest.last}. No passage is displayed.`;
    notice.appendChild(description);
    const addLink = (book, number, label) => {
      const url = new URL(window.location.href);
      ["chapter", "subchapter", "bamberg", "unit", "num", "view", "niese"].forEach(key => url.searchParams.delete(key));
      url.searchParams.set("book", book); url.searchParams.set("niese", number);
      const link = document.createElement("a"); link.href = url.href; link.textContent = label;
      if (notice.childElementCount > 1) notice.append(" · ");
      notice.appendChild(link);
    };
    addLink("preface", "1", "Read Proem, Niese section 1");
    addLink("1", "27", "Read Book I, Niese section 27");
    panes.before(notice);
  };

  const renderUI = () => {''')
    change(path,'    const related = nieseIdentityRegistry()?.relatedPassage;','    renderInvalidNieseNotice();\n    const related = invalidNieseRequest ? null : nieseIdentityRegistry()?.relatedPassage;')
    change(path,'    updateLanguageUI();\n    updateNavigationForms();','    if (invalidNieseRequest) {\n      if (invalidNieseRequest.book !== null) bookLabel.innerText = "Unsupported Antiquities book";\n      sectionLabel.innerText = "Unsupported Niese request";\n    }\n    updateLanguageUI();\n    updateNavigationForms();')
    change(path,'    if (state.viewingLevel === "contents-level") {\n      annotatedParagraphs = [];','    if (invalidNieseRequest || state.viewingLevel === "contents-level") {\n      annotatedParagraphs = [];')
    change(path,'  const setState = async (callback) => {\n    await callback();','  const setState = async (callback) => {\n    unsupportedNieseBook = null; // An explicit reader control selects its real book.\n    await callback();')
if __name__=='__main__':globals()[sys.argv[1]]();print('Implemented package',sys.argv[1],'only in isolated worktree')
