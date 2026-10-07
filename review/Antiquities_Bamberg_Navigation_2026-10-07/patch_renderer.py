from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=R/'assets/js/renderTei.js';s=p.read_bytes().decode();newline='\r\n' if '\r\n' in s else '\n';s=s.replace('\r\n','\n')
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a[:100],s.count(a));s=s.replace(a,b)
replace('  const viewingLevelSelectMenu = document.getElementById("level-select");','''  const bambergSelectForm = document.querySelector("#bamberg-select form");
  const bambergSelectMenu = document.getElementById("bamberg-selector");
  const bambergPrevious = document.getElementById("bamberg-previous");
  const bambergNext = document.getElementById("bamberg-next");
  const viewingLevelSelectMenu = document.getElementById("level-select");''')
replace('    subchapterNum: null,','    subchapterNum: null,\n    bambergId: null,')
replace('  let alignmentRangeRegistry = [];','''  let alignmentRangeRegistry = [];
  let bambergRegistry = [];
  let boundaryRegistry = [];''')
replace('        alignmentRangeRegistry = records("alignment-ranges");','''        alignmentRangeRegistry = records("alignment-ranges");
        bambergRegistry = records("bamberg-boundaries");
        boundaryRegistry = [...traditionalRegistry, ...bambergRegistry];''')
replace('  const selectAvailableTraditionalSubchapter = () => {','''  // Manuscript identity and source order are registry data, independent of labels/citations.
  const bambergRows = () => bambergRegistry.filter(row => !isPreface() && Number(row.book) === Number(state.bookNum));
  const bambergSelection = () => bambergRows().find(row => row.id === state.bambergId);
  const selectAvailableBambergDivision = () => {
    state.bambergId = bambergRows()[0]?.id || null;
    if (!state.bambergId) state.viewingLevel = "book-level";
  };
  const selectAvailableTraditionalSubchapter = () => {''')
replace('traditionalRegistry.find(row => row.id === record.end)', 'boundaryRegistry.find(row => row.id === record.end)')
replace('      nieseNum: activeWork.nieseBooks.includes(Number(bookNum)) ? positive("niese") : null,','''      nieseNum: activeWork.nieseBooks.includes(Number(bookNum)) ? positive("niese") : null,
      bambergId: bambergIdentityFromUrl(params.get("bamberg")),''')
replace('subchapterNum: location.subchapterNum, sectionNum: location.unitNum, nieseNum: location.nieseNum,','subchapterNum: location.subchapterNum, sectionNum: location.unitNum, nieseNum: location.nieseNum, bambergId: location.bambergId,')
replace('    if (state.nieseNum) {\n      state.viewingLevel = "niese-level";', '''    if (state.bambergId !== null) {
      state.viewingLevel = "bamberg-level"; state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null; state.nieseNum = null;
    } else if (state.nieseNum) {
      state.viewingLevel = "niese-level";''')
replace('["book", "chapter", "subchapter", "unit", "num", "niese"].forEach','["book", "chapter", "subchapter", "bamberg", "unit", "num", "niese"].forEach')
replace('    if (state.viewingLevel === "section-level" && state.sectionNum) url.searchParams.set("unit", state.sectionNum);','''    if (state.viewingLevel === "bamberg-level" && state.bambergId !== null) url.searchParams.set("bamberg", bambergUrlValue(state.bambergId));
    if (state.viewingLevel === "section-level" && state.sectionNum) url.searchParams.set("unit", state.sectionNum);''')
replace('      if (["chapter-level", "subchapter-level"].includes(state.viewingLevel))\n        return traditionalRangeView(language, data, traditionalSelection());','''      if (state.viewingLevel === "bamberg-level") {
        const record = bambergSelection();
        return record ? traditionalRangeView(language, data, record)
          : structuralUnavailable(language, "This book has no matching audited Bamberg division identity.");
      }
      if (["chapter-level", "subchapter-level"].includes(state.viewingLevel))
        return traditionalRangeView(language, data, traditionalSelection());''')
replace('''    const showChapter = (
      state.viewingLevel !== "book-level"
      && state.viewingLevel !== "niese-level"
      && !isPreface()
    );''','''    const showChapter = (
      state.viewingLevel !== "book-level"
      && state.viewingLevel !== "niese-level"
      && state.viewingLevel !== "bamberg-level"
      && !isPreface()
    );''')
replace('    const showSection = state.viewingLevel === "section-level";','''    const showSection = state.viewingLevel === "section-level";
    const bambergControl = document.getElementById("bamberg-level");
    const bambergAvailable = usesTraditionalStructure() && bambergRows().length > 0;
    if (bambergControl) bambergControl.disabled = !bambergAvailable;
    if (bambergSelectMenu) bambergSelectMenu.disabled = !bambergAvailable;
    bambergSelectForm?.classList.toggle("hidden", !bambergAvailable || state.viewingLevel !== "bamberg-level");''')
replace('    if (nieseSelectMenu) nieseSelectMenu.value = state.nieseNum ?? "";','''    if (nieseSelectMenu) nieseSelectMenu.value = state.nieseNum ?? "";
    if (bambergSelectMenu) bambergSelectMenu.value = state.bambergId ?? "";
    const divisions = bambergRows(), index = divisions.findIndex(row => row.id === state.bambergId);
    if (bambergPrevious) bambergPrevious.disabled = index <= 0;
    if (bambergNext) bambergNext.disabled = index < 0 || index >= divisions.length - 1;''')
replace('    setTraditionalSubchapterOptions();\n    setSectionSelectOptions();','    setTraditionalSubchapterOptions();\n    setBambergOptions();\n    setSectionSelectOptions();')
replace('''if (usesTraditionalStructure()) data.querySelectorAll('tei-anchor[type="traditional-boundary"]').forEach(marker => marker.hidden = true);''','''if (usesTraditionalStructure()) data.querySelectorAll('tei-anchor[type="traditional-boundary"], tei-anchor[type="bamberg-boundary"]').forEach(marker => marker.hidden = true);''')
replace('    updateLanguageUI();\n    updateNavigationForms();','''    if (usesTraditionalStructure() && state.viewingLevel === "bamberg-level")
      sectionLabel.innerText = bambergSelection() ? `Bamberg division ${bambergSelection().display}` : "Bamberg division";
    updateLanguageUI();
    updateNavigationForms();''')
replace('  const setTraditionalSubchapterOptions = () => {','''  const setBambergOptions = () => {
    if (!bambergSelectMenu || !usesTraditionalStructure()) return;
    bambergSelectMenu.options.length = 0;
    bambergRows().forEach(row => bambergSelectMenu.add(new Option(row.display, row.id)));
  };
  const setTraditionalSubchapterOptions = () => {''')
replace('        if (usesTraditionalStructure()) { state.subchapterNum = null; state.viewingLevel = "book-level"; }','''        if (usesTraditionalStructure()) {
          state.subchapterNum = null;
          if (state.viewingLevel === "bamberg-level") selectAvailableBambergDivision();
          else { state.bambergId = null; state.viewingLevel = "book-level"; }
        }''')
replace('''        if (usesTraditionalStructure()) {
          state.subchapterNum = null;
          state.viewingLevel = state.chapterNum ?''','''        if (usesTraditionalStructure()) {
          state.bambergId = null;
          state.subchapterNum = null;
          state.viewingLevel = state.chapterNum ?''')
replace('if (usesTraditionalStructure()) { state.viewingLevel = "section-level"; state.chapterNum = null; state.subchapterNum = null; }','if (usesTraditionalStructure()) { state.bambergId = null; state.viewingLevel = "section-level"; state.chapterNum = null; state.subchapterNum = null; }')
replace('        state.subchapterNum = event.target.value || null;','        state.bambergId = null;\n        state.subchapterNum = event.target.value || null;')
replace('if (usesTraditionalStructure()) { state.subchapterNum = null; state.viewingLevel = "niese-level"; }','if (usesTraditionalStructure()) { state.bambergId = null; state.subchapterNum = null; state.viewingLevel = "niese-level"; }')
replace('    viewingLevelSelectMenu.addEventListener("change", (event) => {','''    const selectBamberg = identity => setState(() => {
      state.bambergId = identity; state.viewingLevel = "bamberg-level";
      state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null; state.nieseNum = null;
    });
    bambergSelectMenu?.addEventListener("change", event => selectBamberg(event.target.value));
    const advanceBamberg = direction => {
      const rows = bambergRows(), index = rows.findIndex(row => row.id === state.bambergId);
      const next = rows[index + direction];
      if (index >= 0 && next) selectBamberg(next.id);
    };
    bambergPrevious?.addEventListener("click", () => advanceBamberg(-1));
    bambergNext?.addEventListener("click", () => advanceBamberg(1));
    viewingLevelSelectMenu.addEventListener("change", (event) => {''')
replace('''        if (usesTraditionalStructure()) {
          state.viewingLevel = nextLevel;
          if (["chapter-level", "subchapter-level"].includes(nextLevel)) {''','''        if (usesTraditionalStructure()) {
          state.viewingLevel = nextLevel;
          if (nextLevel === "bamberg-level") {
            state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null; state.nieseNum = null;
            if (!bambergSelection()) selectAvailableBambergDivision();
            return;
          }
          state.bambergId = null;
          if (["chapter-level", "subchapter-level"].includes(nextLevel)) {''')
replace('  const readTraditionalUrl = () => {','  // Public URLs serialize the frozen source row, never a manuscript label.\n  const bambergIdentityFromUrl = value => {\n    const row = /^(?:0*)([1-9]\\d*)$/.exec(value || "");\n    return row ? `B78-table1-row${row[1].padStart(3, "0")}` : value;\n  };\n  const bambergUrlValue = identity => {\n    const row = /^B78-table1-row0*([1-9]\\d*)$/.exec(identity || "");\n    return row ? row[1] : identity;\n  };\n  const readTraditionalUrl = () => {')
p.write_bytes(s.replace('\n',newline).encode())
p=R/'_includes/display-settings.html';s=p.read_bytes().decode();newline='\r\n' if '\r\n' in s else '\n';s=s.replace('\r\n','\n')
new='''        {% if page.permalink == "/antiquities/" %}
        <div id="bamberg-select">
          <form class="accordion-row hidden">
            <label for="bamberg-selector">Select a Bamberg division:</label>
            <select id="bamberg-selector"></select>
            <button type="button" id="bamberg-previous" aria-label="Previous Bamberg division">Previous</button>
            <button type="button" id="bamberg-next" aria-label="Next Bamberg division">Next</button>
          </form>
        </div>
        {% endif %}

''';assert s.count('        <div id="niese-select">')==1;s=s.replace('        <div id="niese-select">',new+'        <div id="niese-select">')
new='''            {% if page.permalink == "/antiquities/" %}
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="level-options" id="bamberg-level" value="bamberg-level" />
              <label class="form-check-label" for="bamberg-level">Bamberg division</label>
            </div>
            {% endif %}

''';needle='''            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="level-options" id="niese-level"''';assert s.count(needle)==1;s=s.replace(needle,new+needle);p.write_bytes(s.replace('\n',newline).encode());print('Registry-driven Bamberg controls and generic resolver connected.')
