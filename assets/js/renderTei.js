document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const annotationsList = document.getElementById("annotations-list");
  const annotationsPanel = document.getElementById("annotations");
  const bookLabel = document.getElementById("book-label");
  const bookSelectForm = document.querySelector("#book-select form");
  const bookSelectMenu = document.getElementById("book-selector");
  const bookTitle = document.getElementById("book-title");
  const chapterLabel = document.getElementById("chapter-label");
  const chapterSelectForm = document.querySelector("#chapter-select form");
  const chapterSelectMenu = document.getElementById("chapter-selector");
  const englishPane = document.getElementById("english");
  const englishPaneCheckbox = document.getElementById("english-pane-select");
  const lodgeNotesRow = document.getElementById("lodge-notes-select");
  const lodgeNotesCheckbox = document.getElementById("lodge-notes-visible");
  const frenchPane = document.getElementById("french");
  const frenchPaneCheckbox = document.getElementById("french-pane-select");
  const greekPane = document.getElementById("greek");
  const greekPaneCheckbox = document.getElementById("greek-pane-select");
  const highlightCheckbox = document.getElementById("highlight-annotations");
  const italianPane = document.getElementById("italian");
  const italianPaneCheckbox = document.getElementById("italian-pane-select");
  const latinPane = document.getElementById("latin");
  const latinPaneCheckbox = document.getElementById("latin-pane-select");
  const sectionLabel = document.getElementById("section-label");
  const sectionSelectForm = document.querySelector("#section-select form");
  const sectionSelectMenu = document.getElementById("section-selector");
  const nieseSelectForm = document.querySelector("#niese-select form");
  const nieseSelectMenu = document.getElementById("niese-selector");
  const subchapterSelectForm = document.querySelector("#subchapter-select form");
  const subchapterSelectMenu = document.getElementById("subchapter-selector");
  const bambergSelectForm = document.querySelector("#bamberg-select form");
  const bambergSelectMenu = document.getElementById("bamberg-selector");
  const bambergPrevious = document.getElementById("bamberg-previous");
  const bambergNext = document.getElementById("bamberg-next");
  const niesePrevious = document.getElementById("niese-previous");
  const nieseNext = document.getElementById("niese-next");
  const viewingLevelSelectMenu = document.getElementById("level-select");

  const sourceSelectMenus = {
    Latin: document.getElementById("latin-source-selector"),
    English: document.getElementById("english-source-selector"),
    Greek: document.getElementById("greek-source-selector"),
    French: document.getElementById("french-source-selector"),
    Italian: document.getElementById("italian-source-selector")
  };

  const tei = new CETEI();
  // Bust stale browser copies of XML across page reloads while keeping
  // a stable URL for repeated requests during this page session.
  const teiCacheToken = Date.now().toString();

  // CETEI's default scroll persistence is appropriate for full-page loads,
  // but this application converts TEI dynamically during navigation.
  // Disable it here so each conversion does not restore a stale page position.
  window.removeEventListener("beforeunload", CETEI.savePosition);
  window.removeEventListener("ceteiceanload", CETEI.restorePosition);

  const WORKS = {
    "/antiquities/": {
      title: "Antiquities",
      slug: "antiquities",
      bookCount: 20,
      idPrefix: "book",
      paddedBookId: true,
      traditionalStructure: "assets/xml/antiquities/structure.xml",
      alignment: {
        language: "Latin",
        source: "bamberg78"
      },
      languages: {
        Latin: {
          defaultSource: "bamberg78",
          sources: {
            bamberg78: {
              label: "Bamberg 78",
              directory: "Latin"
            }
          }
        },
        English: {
          defaultSource: "whiston",
          sources: {
            whiston: {
              label: "Whiston",
              directory: "English"
            }
          }
        },
        Greek: {
          defaultSource: "niese",
          sources: {
            niese: {
              label: "Niese",
              directory: "Greek"
            }
          }
        }
      },
      preface: {
        label: "Proem",
        value: "preface",
        filename: "preface",
        idPrefix: "preface"
      },
      // Books IX–XIV preserve reliable Josephus chapter numbers in the
      // visible <num> labels even where the recovered div2 wrappers are
      // incomplete or misnumbered.  For these books, chapter navigation is
      // reconstructed from those canonical citation labels without altering
      // the TEI files.
      citationDerivedChapterBooks: [9, 10, 11, 12, 13, 14],
      // Books XVI and XIX preserve complete chapter sequences, but some chapter
      // starts fall inside existing paragraph/alignment units. Editorial
      // <milestone unit="chapter" n="…"/> markers in each language layer
      // record those boundaries without splitting or renumbering the stable
      // paragraph IDs.
      milestoneChapterBooks: [15, 16, 17, 18, 19, 20],
      nieseBooks: [1, 2, 3, 4, 5, 6, 7],
      nieseIdentityBooks: {
        8: "assets/xml/antiquities/niese/book-08.json"
      },
      nieseRanges: {
        1: [27, 346],
        2: [1, 349],
        3: [1, 322],
        4: [1, 331],
        5: [1, 362],
        6: [1, 378],
        7: [1, 394]
      }
    },
    "/bellum-judaicum/": {
      title: "Bellum Judaicum",
      slug: "bellum",
      urlPreferences: {lodgeNotes: {stateKey: "lodgeNotesVisible", defaultValue: true, offValue: "0"}},
      bookCount: 7,
      idPrefix: "bellum",
      paddedBookId: false,
      alignment: {
        language: "Latin",
        source: "cardwell"
      },
      languages: {
        Latin: {
          defaultSource: "cardwell",
          sources: {
            cardwell: {
              label: "Cardwell (1837)",
              directory: "Latin"
            }
          }
        },
        English: {
          defaultSource: "whiston",
          sources: {
            whiston: {
              label: "Whiston",
              directory: "English"
            },
            lodge1602: {
              label: "Lodge (1602)",
              directory: "English/Lodge1602"
            }
          }
        },
        Greek: {
          defaultSource: "current",
          sources: {
            current: {
              label: "Niese",
              directory: "Greek"
            }
          }
        }
      },
      nieseBooks: [1, 2, 3, 4, 5, 6, 7]
    },
    "/contra-apionem/": {
      title: "Contra Apionem",
      slug: "contra-apionem",
      bookCount: 2,
      idPrefix: "apion",
      paddedBookId: false,
      alignment: {
        language: "Latin",
        source: "boysen"
      },
      languages: {
        Latin: {
          defaultSource: "boysen",
          sources: {
            boysen: {
              label: "Boysen (1898)",
              directory: "Latin",
              usesCanonicalIds: true
            }
          }
        },
        English: {
          defaultSource: "whiston",
          sources: {
            whiston: {
              label: "Whiston",
              directory: "English",
              usesCanonicalIds: true
            }
          }
        },
        Greek: {
          defaultSource: "niese",
          sources: {
            niese: {
              label: "Niese (1889)",
              directory: "Greek",
              usesCanonicalIds: true
            }
          }
        }
      },
      milestoneChapterBooks: [1, 2],
      includeMilestoneChapterZero: false,
      sectionMilestoneUnit: "niese"
    },
    "/deh/": {
      title: "De Excidio Hierosolymitano",
      slug: "deh",
      bookCount: 5,
      availableBooks: [1, 2, 3, 4, 5],
      idPrefix: "deh",
      paddedBookId: false,
      alignment: {
        language: "Latin",
        source: "ussani"
      },
      languages: {
        Latin: {
          defaultSource: "ussani",
          sources: {
            ussani: {
              label: "Ussani (1932)",
              directory: "Latin",
              availableBooks: [1, 2, 3, 4, 5],
              usesCanonicalIds: true
            }
          }
        },
        English: {
          defaultSource: "pollard",
          sources: {
            pollard: {
              label: "Pollard v1.0",
              directory: "English",
              availableBooks: [1, 2, 3, 4, 5]
            }
          }
        }
      },
      chapterLabels: {
        "0": "Prologue"
      },
      sectionLabelSource: "num",
      urlUnitScope: "chapter"
    }
  };

  const activeWork = WORKS[window.location.pathname];

  const languagePanes = {
    Latin: latinPane,
    English: englishPane,
    Greek: greekPane,
    French: frenchPane,
    Italian: italianPane
  };

  const languagePaneCheckboxes = {
    Latin: latinPaneCheckbox,
    English: englishPaneCheckbox,
    Greek: greekPaneCheckbox,
    French: frenchPaneCheckbox,
    Italian: italianPaneCheckbox
  };

  let annotatedParagraphs;
  let fullData = {};
  let viewData = {};
  let canonicalFullData;
  let canonicalViewData;

  const initialSources = Object.fromEntries(
    Object.entries(activeWork.languages).map(([language, config]) => [
      language,
      config.defaultSource
    ])
  );

  let state = {
    bookNum: activeWork.preface ? activeWork.preface.value : "01",
    chapterNum: null,
    subchapterNum: null,
    bambergId: null,
    sectionNum: null,
    nieseNum: null,
    viewingLevel: 'book-level',
    lodgeNotesVisible: true,
    sources: initialSources
  };


  // Source paratext is registered independently of every navigation hierarchy.
  let contentsRegistryRequest;
  let contentsRegistry = [];
  const loadContentsRegistry = async () => {
    if (!contentsRegistryRequest) contentsRegistryRequest = (async () => {
      const response = await fetch(`/assets/xml/source-contents.xml?v=${teiCacheToken}`);
      if (!response.ok) throw new Error("The source contents index could not be loaded.");
      const xml = new DOMParser().parseFromString(await response.text(), "application/xml");
      if (xml.querySelector("parsererror")) throw new Error("Invalid source contents index.");
      contentsRegistry = [...xml.getElementsByTagNameNS("http://www.tei-c.org/ns/1.0", "fs")]
        .filter(fs => fs.getAttribute("type") === "source-contents")
        .map(fs => Object.fromEntries([...fs.children].map(f => [f.getAttribute("name"),
          f.firstElementChild.localName === "vColl"
            ? [...f.firstElementChild.children].map(v => v.textContent) : f.firstElementChild.textContent])));
    })();
    await contentsRegistryRequest;
  };
  const bookContents = () => contentsRegistry.filter(row => row.status === "VERIFIED"
    && row.work === activeWork.slug && Number(row.book) === Number(state.bookNum));
  const hasSourceContents = () => bookContents().some(row =>
    sourceAvailableForBook(row.language, row.witness));
  const clearContentsLocation = () => {
    state.chapterNum = null; state.subchapterNum = null; state.bambergId = null;
    state.nieseNum = null; state.sectionNum = null; pendingUrlUnit = null;
  };
  const contentsView = async language => {
    const wrapper = document.createElement("section");
    wrapper.className = "source-contents";
    const row = bookContents().find(row => row.language === language && row.witness === state.sources[language]);
    if (!row) {
      const notice = document.createElement("p"); notice.setAttribute("role", "status");
      notice.textContent = "No source table of contents is available for this witness.";
      wrapper.appendChild(notice); return wrapper;
    }
    const heading = document.createElement("h4"); heading.textContent = "Table of contents";
    wrapper.appendChild(heading);
    if (row.note) { const note = document.createElement("p"); note.className = "source-contents-note";
      note.textContent = row.note; wrapper.appendChild(note); }
    let contents;
    // Preserve paratext verbatim: default note/list decoration may duplicate source text.
    await tei.getHTML5(`/${row.path}?v=${teiCacheToken}`, data => { contents = data; },
      node => node.setAttribute("data-processed", ""));
    for (const selector of row.selectors) {
      const matches = contents?.querySelectorAll(selector);
      if (!matches?.length) throw new Error(`Registered source contents unavailable: ${row.path}`);
      matches.forEach(node => wrapper.appendChild(node.cloneNode(true)));
    }
    // Contents are source evidence, without inferred navigation targets.
    wrapper.querySelectorAll("a").forEach(link => link.replaceWith(...link.childNodes));
    return wrapper;
  };

  // Antiquities explicitly opts into certified, source-qualified structure.
  // Other works keep their existing adapters and URL semantics.
  const usesTraditionalStructure = () => Boolean(activeWork.traditionalStructure);
  let traditionalRegistry = null;
  let alignmentRangeRegistry = [];
  let bambergRegistry = [];
  let boundaryRegistry = [];
  let traditionalRegistryRequest = null;
  const loadTraditionalRegistry = async () => {
    if (!usesTraditionalStructure()) return;
    if (!traditionalRegistryRequest) {
      traditionalRegistryRequest = (async () => {
        const response = await fetch(`/${activeWork.traditionalStructure}?v=${teiCacheToken}`);
        if (!response.ok) throw new Error("The Chapter/Subchapter registry could not be loaded.");
        const xml = new DOMParser().parseFromString(await response.text(), "application/xml");
        if (xml.querySelector("parsererror")) throw new Error("Invalid structural registry XML.");
        const valueOf = value => value.localName === "fs" ? fields(value)
          : value.localName === "vColl" ? [...value.children].map(valueOf) : value.textContent;
        const fields = fs => Object.fromEntries([...fs.children].map(f =>
          [f.getAttribute("name"), valueOf(f.firstElementChild)]));
        const items = [...xml.getElementsByTagNameNS("http://www.tei-c.org/ns/1.0", "item")];
        const records = type => items.filter(item => item.parentElement.getAttribute("type") === type)
          .map(item => ({id: item.getAttributeNS("http://www.w3.org/XML/1998/namespace", "id"),
            ...fields([...item.children].find(el => el.localName === "fs"))}));
        traditionalRegistry = records("traditional-boundaries");
        alignmentRangeRegistry = records("alignment-ranges");
        bambergRegistry = records("bamberg-boundaries");
        boundaryRegistry = [...traditionalRegistry, ...bambergRegistry];
      })();
    }
    await traditionalRegistryRequest;
  };
  const traditionalRows = (scheme, chapter = null) => (traditionalRegistry || []).filter(row =>
    row.scheme === scheme
    && (isPreface() ? row.context === "Proem" : row.context !== "Proem" && Number(row.book) === Number(state.bookNum))
    && (chapter === null || row.chapter === String(chapter))
  );
  const traditionalSelection = () => state.viewingLevel === "subchapter-level"
    ? traditionalRows("subchapter", isPreface() ? "" : state.chapterNum)
      .find(row => row.subchapter === String(state.subchapterNum))
    : traditionalRows("chapter").find(row => row.chapter === String(state.chapterNum));
  // Manuscript identity and source order are registry data, independent of labels/citations.
  const bambergRows = () => bambergRegistry.filter(row => !isPreface() && Number(row.book) === Number(state.bookNum));
  const bambergSelection = () => bambergRows().find(row => row.id === state.bambergId);
  const selectAvailableBambergDivision = () => {
    state.bambergId = bambergRows()[0]?.id || null;
    if (!state.bambergId) state.viewingLevel = "book-level";
  };
  const selectAvailableTraditionalSubchapter = () => {
    const rows = traditionalRows("subchapter", isPreface() ? "" : state.chapterNum);
    state.subchapterNum = rows[0]?.subchapter || null;
    if (!state.subchapterNum) state.viewingLevel = isPreface() ? "book-level" : "chapter-level";
  };
  const structuralUnavailable = (language, reason) => {
    const notice = document.createElement("div");
    notice.className = "alert alert-secondary structural-unavailable";
    notice.setAttribute("role", "status");
    notice.textContent = `${language}: ${reason} No nearby text has been substituted.`;
    return notice;
  };
  const traditionalPoint = (data, locator) => {
    if (!locator || locator.available !== "true") return null;
    let node = data.querySelector(`[id="${locator.target}"]`);
    if (!node) return null;
    if (locator.kind === "element-edge") {
      for (const step of locator.edge.split("/")) {
        const match = step.match(/^([\w-]+)\[(\d+)\]$/);
        if (!match) return null;
        node = [...node.children].filter(child => child.localName === `tei-${match[1]}`)[Number(match[2]) - 1];
        if (!node) return null;
      }
    }
    return {node, paragraph: node.closest("tei-p"), kind: locator.kind};
  };
  // Display boundaries can include a heading/label before the independent citation/text point.
  const traditionalRangePoint = (data, locator) => traditionalPoint(data, locator?.["boundary-start"] || locator);
  // Independent witness spans may be assembled in registered canonical order.
  // The resolver knows no book, chapter, source-number correction or transposition case.
  const traditionalRangeView = (language, data, record) => {
    if (!record) return structuralUnavailable(language, "Select a valid Chapter or Subchapter.");
    const endRecord = record.end === "BOOK_END" ? null : boundaryRegistry.find(row => row.id === record.end);
    const endLocator = record.endLocator || endRecord?.[language];
    const spans = record[language]?.spans || [{start: record[language], end: endLocator || {kind: "book-end"}}];
    const wrapper = document.createElement("tei-div");
    wrapper.setAttribute("type", record.scheme);
    wrapper.dataset.structuralIdentity = record.id;
    if (record["verification-status"]) wrapper.dataset.verificationStatus = record["verification-status"];
    if (record["canonical-niese"]) wrapper.dataset.canonicalNiese = record["canonical-niese"];
    for (const [index, span] of spans.entries()) {
      const start = traditionalRangePoint(data, span.start);
      if (!start) return structuralUnavailable(language, "This certified start has no mapped current text.");
      const end = span.end?.kind === "book-end" ? null : traditionalRangePoint(data, span.end);
      if (span.end?.kind !== "book-end" && !end)
        return structuralUnavailable(language, "The certified range end has no mapped current text.");
      if (end && (start.node === end.node || !(start.node.compareDocumentPosition(end.node) & Node.DOCUMENT_POSITION_FOLLOWING)))
        return structuralUnavailable(language, "The registered physical span is empty or reversed.");
      const range = document.createRange();
      if (start.kind === "paragraph") range.setStart(start.node, 0);
      else range.setStartBefore(start.node);
      if (end) {
        if (end.kind === "paragraph") range.setEnd(end.node, 0);
        else range.setEndBefore(end.node);
      } else {
        const body = data.querySelector("tei-body") || data;
        range.setEnd(body, body.childNodes.length);
      }
      const fragment = spans.length === 1 ? wrapper : document.createElement("tei-div");
      if (spans.length > 1) {
        fragment.setAttribute("type", "physical-fragment");
        fragment.dataset.fragmentOrdinal = String(index + 1);
        fragment.dataset.sourceStart = span.start.target;
        fragment.dataset.sourceEnd = span.end.target || "book-end";
        fragment.dataset.sourceDescription = span.label || "";
      }
      if (start.paragraph && (!end || start.paragraph === end.paragraph) && range.commonAncestorContainer === start.paragraph) {
        const shell = start.paragraph.cloneNode(false);
        shell.appendChild(range.cloneContents()); fragment.appendChild(shell);
      } else fragment.appendChild(range.cloneContents());
      // Discard only the artificial empty shell at an exclusive paragraph endpoint.
      if (end?.kind === "paragraph") fragment.querySelectorAll("tei-p").forEach(p => {
        if (p.id === end.node.id && !p.textContent && !p.children.length) p.remove();
      });
      if (spans.length > 1) wrapper.appendChild(fragment);
    }
    // A source paragraph can supply several fragments. Retain its stable identity
    // as provenance on every clone without emitting duplicate DOM IDs.
    const seen = new Set();
    wrapper.querySelectorAll("[id]").forEach(node => {
      if (seen.has(node.id)) {node.dataset.sourceId = node.id; node.removeAttribute("id");}
      else seen.add(node.id);
    });
    return wrapper;
  };
  const updateTraditionalNotice = () => {
    document.getElementById("traditional-reader-notice")?.remove();
    if (!usesTraditionalStructure() || !["chapter-level", "subchapter-level"].includes(state.viewingLevel)) return;
    const explanation = traditionalSelection()?.["reader-note"];
    const panes = document.getElementById("pane-container");
    if (!explanation || !panes) return;
    const notice = document.createElement("aside");
    notice.id = "traditional-reader-notice";
    notice.className = "alert alert-secondary";
    notice.dataset.structuralNotice = "true";
    const text = document.createElement("p"); text.textContent = explanation;
    const url = new URL(window.location.href);
    ["chapter", "subchapter", "niese", "unit", "num"].forEach(key => url.searchParams.delete(key));
    const link = document.createElement("a"); link.href = url.href; link.textContent = "See Bamberg’s manuscript order in Book view";
    notice.append(text, link); panes.before(notice);
  };
  const antiquitiesUnitView = (language, data) => {
    const canonicalId = `latin-${currentIdBase()}-num${state.sectionNum}`;
    const canonical = canonicalFullData?.querySelector(`[id="${canonicalId}"]`);
    if (!canonical) return structuralUnavailable(language, "This Alignment unit has no current target.");
    if (language === activeWork.alignment.language) return canonical;
    const binding = alignmentRangeRegistry.find(row => row["canonical-target"] === canonicalId && row.language === language);
    if (binding) return traditionalRangeView(language, data, {
      id: binding.id, scheme: "alignment-unit", [language]: binding.start,
      end: "BOOK_END", endLocator: binding.end
    });
    const exactId = canonicalId.replace(/^latin-/, `${language.toLowerCase()}-`);
    const paragraphs = [...data.querySelectorAll("tei-p")].filter(p =>
      normalizedSameAsTargets(p).includes(canonicalId) || p.id === exactId
    );
    if (!paragraphs.length) return structuralUnavailable(language, "This Alignment unit has no mapped current text.");
    const wrapper = document.createElement("tei-div");
    paragraphs.forEach(p => wrapper.appendChild(p.cloneNode(true)));
    return wrapper;
  };
  // Public URLs serialize the frozen source row, never a manuscript label.
  const bambergIdentityFromUrl = value => {
    const row = /^(?:0*)([1-9]\d*)$/.exec(value || "");
    return row ? `B78-table1-row${row[1].padStart(3, "0")}` : value;
  };
  const bambergUrlValue = identity => {
    const row = /^B78-table1-row0*([1-9]\d*)$/.exec(identity || "");
    return row ? row[1] : identity;
  };
  const readTraditionalUrl = () => {
    const params = new URLSearchParams(window.location.search);
    const rawBook = params.get("book");
    const bookNum = rawBook === "preface" ? "preface"
      : /^[1-9]\d*$/.test(rawBook || "") && Number(rawBook) <= activeWork.bookCount
        ? String(Number(rawBook)).padStart(2, "0") : defaultBookNum();
    const positive = key => /^[1-9]\d*$/.test(params.get(key) || "") ? String(Number(params.get(key))) : null;
    const sourceSelections = Object.fromEntries(Object.keys(activeWork.languages).flatMap(language => {
      const source = params.get(language.toLowerCase());
      return sourceAvailableForBook(language, source, bookNum) ? [[language, source]] : [];
    }));
    const rawUnit = params.get("unit") || params.get("num");
    return {bookNum, chapterNum: bookNum === "preface" ? null : positive("chapter"),
      subchapterNum: positive("subchapter"), unitNum: /^[1-9]\d*[a-z]*$/.test(rawUnit || "") ? rawUnit : null,
      nieseNum: supportsNieseBook(bookNum) ? positive("niese") : null,
      bambergId: bambergIdentityFromUrl(params.get("bamberg")),
      sourceSelections, hasLocationParams: params.size > 0};
  };
  const applyTraditionalUrl = () => {
    const location = readTraditionalUrl();
    Object.assign(state, {bookNum: location.bookNum, chapterNum: location.chapterNum,
      subchapterNum: location.subchapterNum, sectionNum: location.unitNum, nieseNum: location.nieseNum, bambergId: location.bambergId,
      sources: {...initialSources, ...location.sourceSelections}});
    if (state.bambergId !== null) {
      state.viewingLevel = "bamberg-level"; state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null; state.nieseNum = null;
    } else if (state.nieseNum) {
      state.viewingLevel = "niese-level"; state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null;
    } else if (state.sectionNum) {
      state.viewingLevel = "section-level"; state.chapterNum = null; state.subchapterNum = null;
    } else if (state.subchapterNum) state.viewingLevel = "subchapter-level";
    else state.viewingLevel = state.chapterNum ? "chapter-level" : "book-level";
    return location.hasLocationParams;
  };
  const syncTraditionalUrl = mode => {
    const url = new URL(window.location.href);
    if (url.searchParams.get("view") === "contents") url.searchParams.delete("view");
    ["book", "chapter", "subchapter", "bamberg", "unit", "num", "niese"].forEach(key => url.searchParams.delete(key));
    url.searchParams.set("book", isPreface() ? "preface" : String(Number(state.bookNum)));
    if (["chapter-level", "subchapter-level"].includes(state.viewingLevel) && state.chapterNum)
      url.searchParams.set("chapter", state.chapterNum);
    if (state.viewingLevel === "subchapter-level" && state.subchapterNum) url.searchParams.set("subchapter", state.subchapterNum);
    if (state.viewingLevel === "bamberg-level" && state.bambergId !== null) url.searchParams.set("bamberg", bambergUrlValue(state.bambergId));
    if (state.viewingLevel === "section-level" && state.sectionNum) url.searchParams.set("unit", state.sectionNum);
    if (state.viewingLevel === "niese-level" && state.nieseNum) url.searchParams.set("niese", state.nieseNum);
    Object.entries(activeWork.languages).forEach(([language, config]) => {
      const key = language.toLowerCase(), source = state.sources[language];
      if (source && source !== config.defaultSource) url.searchParams.set(key, source);
      else url.searchParams.delete(key);
    });
    if (url.href !== window.location.href) window.history[mode === "push" ? "pushState" : "replaceState"]({}, "", url);
  };

  const sourceAvailableForBook = (
    language,
    sourceKey,
    bookNum = state.bookNum
  ) => {
    const source = activeWork.languages[language]?.sources[sourceKey];
    if (!source) return false;

    if (
      !source.availableBooks
      || !/^\d+$/.test(String(bookNum))
    ) return true;

    return source.availableBooks.includes(parseInt(bookNum, 10));
  };

  const availableSourceEntries = (
    language,
    bookNum = state.bookNum
  ) => (
    Object.entries(activeWork.languages[language]?.sources || {})
      .filter(([sourceKey]) =>
        sourceAvailableForBook(language, sourceKey, bookNum)
      )
  );

  const normalizeSourcesForBook = () => {
    Object.entries(activeWork.languages).forEach(([language, config]) => {
      const current = state.sources[language];

      if (sourceAvailableForBook(language, current)) return;

      const available = availableSourceEntries(language);

      state.sources[language] = sourceAvailableForBook(
        language,
        config.defaultSource
      )
        ? config.defaultSource
        : (available[0]?.[0] || null);
    });
  };

  const defaultBookNum = () => (
    activeWork.preface ? activeWork.preface.value : "01"
  );

  let pendingUrlUnit = null;

  const usesChapterLocalUrlUnits = () => (
    activeWork.urlUnitScope === "chapter"
  );

  const supportsNieseBook = book => Boolean(
    activeWork.nieseBooks?.includes(Number(book))
    || activeWork.nieseIdentityBooks?.[Number(book)]
  );
  const supportsNieseSections = () => supportsNieseBook(state.bookNum);
  const nieseIdentityRegistries = new Map();
  const nieseIdentityRegistry = () => nieseIdentityRegistries.get(Number(state.bookNum)) || null;
  const loadNieseIdentityRegistry = async () => {
    const book = Number(state.bookNum), path = activeWork.nieseIdentityBooks?.[book];
    if (!path || nieseIdentityRegistries.has(book)) return;
    const response = await fetch(`/${path}?v=${teiCacheToken}`);
    if (!response.ok) throw new Error("The Niese identity registry could not be loaded.");
    const registry = await response.json();
    const [first, last] = registry.range || [];
    if (registry.schema !== 1 || registry.book !== book || !Number.isInteger(first)
      || !Number.isInteger(last) || registry.sections?.length !== last - first + 1
      || registry.sections.some((section, index) => section.number !== first + index))
      throw new Error("Invalid Niese identity registry.");
    nieseIdentityRegistries.set(book, registry);
  };

  const sectionLevelUsesNiese = () => (
    activeWork.slug === "contra-apionem"
  );

  const citationLocationFromLabel = (label) => {
    const match = String(label || "").match(
      /^\[[^.]+\.(\d+)\.(\d+)\]$/
    );

    if (!match) return null;

    return {
      chapterNum: String(parseInt(match[1], 10)),
      unitNum: String(parseInt(match[2], 10))
    };
  };

  const readNavigationFromUrl = () => {
    if (usesTraditionalStructure()) return readTraditionalUrl();
    const params = new URLSearchParams(window.location.search);

    const sourceParamKeys = Object.keys(activeWork.languages).map(
      language => language.toLowerCase()
    );

    const hasLocationParams = [
      "book",
      "chapter",
      "unit",
      "num",
      "niese",
      ...(activeWork.slug === "bellum" ? ["lodgeNotes"] : []),
      ...sourceParamKeys
    ].some(key => params.has(key));

    let bookNum = defaultBookNum();
    let explicitBookInvalid = false;

    if (params.has("book")) {
      const rawBook = params.get("book");
      const parsedBook = /^\d+$/.test(rawBook || "")
        ? parseInt(rawBook, 10)
        : NaN;

      const available = (
        Number.isInteger(parsedBook)
        && parsedBook >= 1
        && parsedBook <= activeWork.bookCount
        && (
          !activeWork.availableBooks
          || activeWork.availableBooks.includes(parsedBook)
        )
      );

      if (available) {
        bookNum = String(parsedBook).padStart(2, "0");
      } else {
        explicitBookInvalid = true;
      }
    }

    let chapterNum = null;
    let unitNum = null;
    let explicitNum = null;
    let nieseNum = null;
    const sourceSelections = {};

    if (!explicitBookInvalid) {
      const rawChapter = params.get("chapter");
      if (/^\d+$/.test(rawChapter || "")) {
        chapterNum = String(parseInt(rawChapter, 10));
      }

      const rawUnit = params.get("unit");
      if (/^[1-9]\d*$/.test(rawUnit || "")) {
        unitNum = String(parseInt(rawUnit, 10));
      }

      const rawNum = params.get("num");
      if (/^[1-9]\d*$/.test(rawNum || "")) {
        explicitNum = String(parseInt(rawNum, 10));
      }

      const rawNiese = params.get("niese");
      if (
        /^[1-9]\d*$/.test(rawNiese || "")
        && (
          sectionLevelUsesNiese()
          || supportsNieseBook(bookNum)
        )
      ) {
        nieseNum = String(parseInt(rawNiese, 10));
      }

      Object.entries(activeWork.languages).forEach(([language, config]) => {
        const paramKey = language.toLowerCase();

        if (!params.has(paramKey)) return;

        const requestedSource = params.get(paramKey);

        if (
          requestedSource
          && config.sources[requestedSource]
          && sourceAvailableForBook(
            language,
            requestedSource,
            bookNum
          )
        ) {
          sourceSelections[language] = requestedSource;
        }
      });
    }

    return {
      bookNum,
      chapterNum,
      unitNum,
      explicitNum,
      nieseNum,
      sourceSelections,
      lodgeNotesVisible: activeWork.slug !== "bellum" || params.get("lodgeNotes") !== "0",
      hasLocationParams
    };
  };

  const applyNavigationLocation = () => {
    if (usesTraditionalStructure()) return applyTraditionalUrl();
    const location = readNavigationFromUrl();

    state.bookNum = location.bookNum;
    state.chapterNum = location.chapterNum;
    state.sectionNum = null;
    state.nieseNum = null;

    state.sources = { ...initialSources };
    state.lodgeNotesVisible = location.lodgeNotesVisible;

    Object.entries(location.sourceSelections || {}).forEach(
      ([language, sourceKey]) => {
        state.sources[language] = sourceKey;
      }
    );

    normalizeSourcesForBook();
    pendingUrlUnit = null;

    if (location.nieseNum && sectionLevelUsesNiese()) {
      state.sectionNum = location.nieseNum;
      state.nieseNum = null;
      state.viewingLevel = "section-level";
    } else if (location.nieseNum && supportsNieseSections()) {
      state.nieseNum = location.nieseNum;
      state.chapterNum = null;
      state.sectionNum = null;
      state.viewingLevel = "niese-level";
    } else {
      if (location.explicitNum) {
        // Explicit compatibility route to the stable global num.
        state.sectionNum = location.explicitNum;
      } else if (location.unitNum) {
        if (
          usesChapterLocalUrlUnits()
          && state.chapterNum !== null
        ) {
          // Resolve the human-facing chapter-local unit after
          // canonical XML and the section menu have been loaded.
          pendingUrlUnit = location.unitNum;
        } else if (!usesChapterLocalUrlUnits()) {
          state.sectionNum = location.unitNum;
        }
      }

      if (state.sectionNum || pendingUrlUnit) {
        state.viewingLevel = "section-level";
      } else if (state.chapterNum !== null) {
        state.viewingLevel = "chapter-level";
      } else {
        state.viewingLevel = "book-level";
      }
    }

    return location.hasLocationParams;
  };

  const syncNavigationLocation = (mode = "replace") => {
    if (usesTraditionalStructure()) return syncTraditionalUrl(mode);
    const url = new URL(window.location.href);

    if (url.searchParams.get("view") === "contents") url.searchParams.delete("view");
    const numericBook = /^\d+$/.test(String(state.bookNum))
      ? String(parseInt(state.bookNum, 10))
      : String(state.bookNum);

    url.searchParams.set("book", numericBook);

    if (
      state.viewingLevel !== "book-level"
      && state.viewingLevel !== "niese-level"
      && state.chapterNum !== null
      && state.chapterNum !== ""
    ) {
      url.searchParams.set("chapter", String(state.chapterNum));
    } else {
      url.searchParams.delete("chapter");
    }

    if (
      state.viewingLevel === "section-level"
      && state.sectionNum
      && !sectionLevelUsesNiese()
    ) {
      let urlUnit = String(state.sectionNum);

      if (usesChapterLocalUrlUnits()) {
        const location = citationLocationFromLabel(
          sectionDisplayLabel(state.sectionNum)
        );

        if (
          location
          && state.chapterNum !== null
          && String(parseInt(location.chapterNum, 10))
            === String(parseInt(state.chapterNum, 10))
        ) {
          urlUnit = location.unitNum;
        }
      }

      url.searchParams.set("unit", urlUnit);
    } else {
      url.searchParams.delete("unit");
    }

    if (
      sectionLevelUsesNiese()
      && state.viewingLevel === "section-level"
      && state.sectionNum
    ) {
      url.searchParams.set("niese", String(state.sectionNum));
    } else if (
      state.viewingLevel === "niese-level"
      && state.nieseNum
      && supportsNieseSections()
    ) {
      url.searchParams.set("niese", String(state.nieseNum));
    } else {
      url.searchParams.delete("niese");
    }

    // num= is accepted as a compatibility input but never emitted
    // by canonical URLs.
    url.searchParams.delete("num");

    Object.entries(activeWork.languages).forEach(([language, config]) => {
      const paramKey = language.toLowerCase();
      const selectedSource = state.sources[language];

      if (
        selectedSource
        && selectedSource !== config.defaultSource
      ) {
        url.searchParams.set(paramKey, selectedSource);
      } else {
        url.searchParams.delete(paramKey);
      }
    });

    // Canonicalize parameter order for readable, stable scholarly URLs:
    // book -> chapter -> unit -> niese -> source selections -> Lodge notes.
    const knownParams = new Set([
      "book",
      "chapter",
      "unit",
      "num",
      "niese",
      ...(activeWork.slug === "bellum" ? ["lodgeNotes"] : []),
      ...Object.keys(activeWork.languages).map(
        language => language.toLowerCase()
      )
    ]);

    const extras = [...url.searchParams.entries()].filter(
      ([key]) => !knownParams.has(key)
    );

    const orderedParams = new URLSearchParams();

    orderedParams.set("book", numericBook);

    if (
      state.viewingLevel !== "book-level"
      && state.viewingLevel !== "niese-level"
      && state.chapterNum !== null
      && state.chapterNum !== ""
    ) {
      orderedParams.set("chapter", String(state.chapterNum));
    }

    if (
      state.viewingLevel === "section-level"
      && state.sectionNum
      && !sectionLevelUsesNiese()
    ) {
      let urlUnit = String(state.sectionNum);

      if (usesChapterLocalUrlUnits()) {
        const location = citationLocationFromLabel(
          sectionDisplayLabel(state.sectionNum)
        );

        if (
          location
          && state.chapterNum !== null
          && String(parseInt(location.chapterNum, 10))
            === String(parseInt(state.chapterNum, 10))
        ) {
          urlUnit = location.unitNum;
        }
      }

      orderedParams.set("unit", urlUnit);
    }

    if (
      sectionLevelUsesNiese()
      && state.viewingLevel === "section-level"
      && state.sectionNum
    ) {
      orderedParams.set("niese", String(state.sectionNum));
    } else if (
      state.viewingLevel === "niese-level"
      && state.nieseNum
      && supportsNieseSections()
    ) {
      orderedParams.set("niese", String(state.nieseNum));
    }

    Object.entries(activeWork.languages).forEach(([language, config]) => {
      const selectedSource = state.sources[language];

      if (
        selectedSource
        && selectedSource !== config.defaultSource
      ) {
        orderedParams.set(
          language.toLowerCase(),
          selectedSource
        );
      }
    });

    if (activeWork.slug === "bellum" && !state.lodgeNotesVisible) {
      orderedParams.set("lodgeNotes", "0");
    }

    extras.forEach(([key, value]) => {
      orderedParams.append(key, value);
    });

    url.search = orderedParams.toString();

    if (url.href === window.location.href) return;

    if (mode === "push") {
      window.history.pushState({}, "", url);
    } else {
      window.history.replaceState({}, "", url);
    }
  };

  const applyNavigationFromUrl = () => {
    const requested = applyNavigationLocation();
    if (new URLSearchParams(window.location.search).get("view") === "contents") {
      clearContentsLocation(); state.viewingLevel = "contents-level"; return true;
    }
    return requested;
  };
  const syncUrlFromState = (mode = "replace") => {
    if (state.viewingLevel !== "contents-level") return syncNavigationLocation(mode);
    const url = new URL(window.location.href);
    ["chapter", "subchapter", "bamberg", "niese", "unit", "num"].forEach(key => url.searchParams.delete(key));
    url.searchParams.set("book", isPreface() ? "preface" : String(Number(state.bookNum)));
    url.searchParams.set("view", "contents");
    Object.entries(activeWork.languages).forEach(([language, config]) => {
      const key = language.toLowerCase(), source = state.sources[language];
      if (source && source !== config.defaultSource) url.searchParams.set(key, source);
      else url.searchParams.delete(key);
    });
    Object.entries(activeWork.urlPreferences || {}).forEach(([key, preference]) => {
      if (state[preference.stateKey] === preference.defaultValue) url.searchParams.delete(key);
      else url.searchParams.set(key, preference.offValue);
    });
    if (url.href !== window.location.href) window.history[mode === "push" ? "pushState" : "replaceState"]({}, "", url);
  };

  const isPreface = () => (
    activeWork.preface && state.bookNum === activeWork.preface.value
  );

  const currentFilename = () => (
    isPreface() ? activeWork.preface.filename : `book-${state.bookNum}`
  );

  const currentIdBase = () => {
    if (isPreface()) return activeWork.preface.idPrefix;

    const formattedNum = activeWork.paddedBookId
      ? state.bookNum
      : parseInt(state.bookNum);

    return `${activeWork.idPrefix}${formattedNum}`;
  };

  const currentBookLabel = () => (
    isPreface() ? activeWork.preface.label : `Book ${state.bookNum}`
  );

  const chapterDisplayLabel = (chapterNum = state.chapterNum) => {
    if (
      chapterNum === null
      || chapterNum === undefined
      || chapterNum === ""
    ) return "";

    return activeWork.chapterLabels?.[String(chapterNum)]
      || `Chapter ${chapterNum}`;
  };

  const canonicalParagraphForSection = (sectionNum) => {
    if (!sectionNum) return null;

    const paragraphId = `latin-${currentIdBase()}-num${sectionNum}`;

    const inFullData = canonicalFullData?.querySelector(
      `[id="${paragraphId}"]`
    );
    if (inFullData) return inFullData;

    if (canonicalViewData?.id === paragraphId) {
      return canonicalViewData;
    }

    return document.getElementById(paragraphId);
  };

  const sectionDisplayLabel = (sectionNum = state.sectionNum) => {
    if (!sectionNum) return "";

    if (activeWork.sectionLabelSource === "num") {
      const paragraph = canonicalParagraphForSection(sectionNum);
      const numElement = paragraph?.querySelector("tei-num");
      const visibleLabel = numElement?.innerText?.trim();

      if (visibleLabel) return visibleLabel;
    }

    if (usesTraditionalStructure()) return `Alignment unit ${sectionNum}`;
    const label = ["antiquities", "bellum"].includes(activeWork.slug)
      ? "Sub-chapter"
      : "Section";
    return `${label} ${sectionNum}`;
  };

  const sourceConfig = (language, sourceKey = state.sources[language]) => (
    activeWork.languages[language]?.sources[sourceKey]
  );

  const displayedSourceUsesCanonicalIds = (language) => {
    const source = sourceConfig(language);

    return (
      (
        language === activeWork.alignment.language
        && state.sources[language] === activeWork.alignment.source
      )
      || source?.usesCanonicalIds === true
    );
  };

  const sourceUrl = (language, sourceKey, filename) => {
    const source = sourceConfig(language, sourceKey);

    if (!source) {
      throw new Error(
        `Unknown source "${sourceKey}" for ${language} in ${activeWork.title}`
      );
    }

    return `../assets/xml/${activeWork.slug}/${source.directory}/${filename}.xml?v=${teiCacheToken}`;
  };

  const fetchTei = async (language, sourceKey, filename) => {
    let result;

    await tei.getHTML5(sourceUrl(language, sourceKey, filename), (data) => {
      result = data;
    });

    return result;
  };

  const usesCitationDerivedChapters = () => (
    activeWork.citationDerivedChapterBooks?.includes(parseInt(state.bookNum))
  );

  const usesMilestoneChapters = () => (
    activeWork.milestoneChapterBooks?.includes(parseInt(state.bookNum))
  );

  const milestoneChapterMarkers = (data) => (
    data
      ? [...data.querySelectorAll('tei-milestone[unit="chapter"][n]')]
      : []
  );

  const milestoneChapterNumbers = () => {
    const chapters = milestoneChapterMarkers(canonicalFullData)
      .map(marker => parseInt(marker.getAttribute("n")))
      .filter(Number.isInteger);

    const includeZero = activeWork.includeMilestoneChapterZero !== false;
    return [
      ...(includeZero ? [0] : []),
      ...[...new Set(chapters)].sort((a, b) => a - b)
    ];
  };

  const milestoneChapterView = (
    language,
    data,
    chapterNum,
    forceCanonical = false
  ) => {
    if (!data || chapterNum === null || chapterNum === undefined || chapterNum === "") {
      return data;
    }

    if (
      !forceCanonical
      && !displayedSourceUsesCanonicalIds(language)
    ) {
      return alignedChapterView(language, data, chapterNum);
    }

    if (String(chapterNum) === "0") {
      const idBase = currentIdBase();
      const usesCanonicalIds = forceCanonical || displayedSourceUsesCanonicalIds(language);
      const selector = usesCanonicalIds
        ? `[id="latin-${idBase}-chapter0"]`
        : `[sameAs*="latin-${idBase}-chapter0"]`;
      return data.querySelector(selector);
    }

    const wantedChapter = parseInt(chapterNum);
    const markers = milestoneChapterMarkers(data);
    const startIndex = markers.findIndex(
      marker => parseInt(marker.getAttribute("n")) === wantedChapter
    );

    if (startIndex === -1) return null;

    const startMarker = markers[startIndex];
    const nextMarker = markers[startIndex + 1] || null;
    const body = startMarker.closest("tei-body") || data.querySelector("tei-body") || data;
    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "chapter");
    wrapper.setAttribute("n", String(wantedChapter));
    wrapper.dataset.syntheticChapter = "milestone-derived";

    const startParagraph = startMarker.closest("tei-p");
    const endParagraph = nextMarker?.closest("tei-p") || null;

    if (startParagraph && nextMarker && endParagraph === startParagraph) {
      // When both chapter boundaries fall inside the same aligned paragraph,
      // Range.cloneContents() returns only the paragraph's children because
      // the paragraph itself is the common ancestor. Preserve a shallow copy
      // of that paragraph so its stable xml:id / sameAs anchor remains
      // available to the section selector and section-level view.
      const paragraphWrapper = startParagraph.cloneNode(false);
      const paragraphRange = document.createRange();
      paragraphRange.setStartAfter(startMarker);
      paragraphRange.setEndBefore(nextMarker);
      paragraphWrapper.appendChild(paragraphRange.cloneContents());
      wrapper.appendChild(paragraphWrapper);
    } else {
      const range = document.createRange();
      range.setStartAfter(startMarker);

      if (nextMarker) {
        range.setEndBefore(nextMarker);
      } else {
        range.setEnd(body, body.childNodes.length);
      }

      wrapper.appendChild(range.cloneContents());
    }

    // DOM Range may preserve empty partial ancestors at the end boundary.
    // They are harmless, but removing completely empty paragraph shells keeps
    // section menus and rendered chapter views deterministic.
    wrapper.querySelectorAll("tei-p").forEach(paragraph => {
      if (
        !paragraph.textContent.trim()
        && paragraph.querySelectorAll("*").length === 0
      ) {
        paragraph.remove();
      }
    });

    return wrapper.textContent.trim() || wrapper.querySelector("tei-p, tei-div2, tei-head")
      ? wrapper
      : null;
  };

  // Contra Apionem has five Niese section starts inside printed words.
  // Preserve those zero-width anchors rather than splitting or duplicating text.
  const workLanguageIdPrefix = (language) => (
    activeWork.slug === "contra-apionem"
      ? String(language).toLowerCase()
      : "latin"
  );

  const milestoneAwareSectionAnchors = (language, data) => {
    if (!data || !activeWork.sectionMilestoneUnit) return [];

    const prefix = `${workLanguageIdPrefix(language)}-${currentIdBase()}-num`;

    return [...data.querySelectorAll(`[id^="${prefix}"]`)]
      .filter(el => (
        el.matches("tei-p")
        || (
          el.matches("tei-milestone")
          && el.getAttribute("unit") === activeWork.sectionMilestoneUnit
        )
      ));
  };

  const milestoneAwareSectionView = (language, data, sectionNum) => {
    if (!data || !sectionNum) return null;

    const wantedId = `${workLanguageIdPrefix(language)}-${currentIdBase()}-num${sectionNum}`;
    const anchors = milestoneAwareSectionAnchors(language, data);
    const startIndex = anchors.findIndex(anchor => anchor.id === wantedId);
    if (startIndex === -1) return null;

    const start = anchors[startIndex];
    const next = anchors[startIndex + 1] || null;

    // Ordinary paragraph-bounded section.
    if (start.matches("tei-p") && (!next || next.matches("tei-p"))) {
      return start.cloneNode(true);
    }

    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "section");
    wrapper.setAttribute("n", String(sectionNum));
    wrapper.dataset.syntheticSection = "milestone-derived";

    const startParagraph = start.closest("tei-p");
    const endParagraph = next?.closest("tei-p") || null;

    // Paragraph start to an internal boundary.
    if (start.matches("tei-p") && next && endParagraph === start) {
      const paragraphWrapper = start.cloneNode(false);
      const range = document.createRange();
      range.setStart(start, 0);
      range.setEndBefore(next);
      paragraphWrapper.appendChild(range.cloneContents());
      wrapper.appendChild(paragraphWrapper);
      return wrapper;
    }

    // Internal boundary to the end of its paragraph or to another internal
    // boundary in that same paragraph.
    if (start.matches("tei-milestone") && startParagraph) {
      const paragraphWrapper = startParagraph.cloneNode(false);
      const range = document.createRange();
      range.setStartAfter(start);

      if (next && endParagraph === startParagraph) {
        range.setEndBefore(next);
      } else {
        range.setEnd(startParagraph, startParagraph.childNodes.length);
      }

      paragraphWrapper.appendChild(range.cloneContents());
      wrapper.appendChild(paragraphWrapper);
      return wrapper;
    }

    return start.cloneNode(true);
  };

  const milestoneSectionView = (
    language,
    data,
    chapterNum,
    sectionNum,
    forceCanonical = false
  ) => {
    if (!sectionNum) return null;

    if (
      !forceCanonical
      && !displayedSourceUsesCanonicalIds(language)
    ) {
      return alignedSectionView(language, data, sectionNum);
    }

    const chapter = milestoneChapterView(
      language,
      data,
      chapterNum,
      forceCanonical
    );
    if (!chapter) return null;

    if (activeWork.sectionMilestoneUnit) {
      // Contra Apionem's Niese sections are independent citation units and may
      // cross an edition's chapter boundary (Boysen XVI begins inside II.156).
      // Once a section is selected, show the complete Niese section in every
      // pane. The selected chapter may filter the section menu, but must not
      // truncate the section text itself.
      return milestoneAwareSectionView(language, data, sectionNum);
    }

    const paragraphId = `latin-${currentIdBase()}-num${sectionNum}`;
    const usesCanonicalIds = forceCanonical || displayedSourceUsesCanonicalIds(language);
    const selector = usesCanonicalIds
      ? `[id="${paragraphId}"]`
      : `[sameAs*="${paragraphId}"]`;

    return chapter.querySelector(selector);
  };

  const romanToInt = (roman) => {
    if (!roman || !/^[IVXLCDM]+$/i.test(roman)) return null;

    const values = {
      I: 1,
      V: 5,
      X: 10,
      L: 50,
      C: 100,
      D: 500,
      M: 1000
    };

    let total = 0;
    let previous = 0;

    roman.toUpperCase().split("").reverse().forEach(character => {
      const value = values[character];

      if (value < previous) {
        total -= value;
      } else {
        total += value;
        previous = value;
      }
    });

    return total;
  };

  const chapterFromCitationLabel = (paragraph) => {
    const label = paragraph?.querySelector("tei-num")?.innerText?.trim();
    const match = label?.match(/^\[\s*([IVXLCDM]+)\./i);

    return match ? romanToInt(match[1]) : null;
  };

  const canonicalParagraphChapterMap = () => {
    const chapterMap = new Map();
    if (!canonicalFullData) return chapterMap;

    const paragraphPrefix = `latin-${currentIdBase()}-num`;
    const paragraphs = [...canonicalFullData.querySelectorAll("tei-p")]
      .filter(paragraph => paragraph.id?.startsWith(paragraphPrefix));
    const labelledChapters = paragraphs.map(chapterFromCitationLabel);

    paragraphs.forEach((paragraph, index) => {
      const labelledChapter = labelledChapters[index];

      if (labelledChapter !== null) {
        if (!chapterMap.has(paragraph.id)) {
          chapterMap.set(paragraph.id, labelledChapter);
        }
        return;
      }

      let previousChapter = null;
      for (let i = index - 1; i >= 0; i -= 1) {
        if (labelledChapters[i] !== null) {
          previousChapter = labelledChapters[i];
          break;
        }
      }

      let nextChapter = null;
      for (let i = index + 1; i < labelledChapters.length; i += 1) {
        if (labelledChapters[i] !== null) {
          nextChapter = labelledChapters[i];
          break;
        }
      }

      let inferredChapter = previousChapter;
      const paragraphText = paragraph.innerText?.trim() || "";

      // Antiquities IX has one explicit placeholder for the Bamberg lacuna
      // 51–109.  It lies between IV.ii.47 and VI.ii.110 and therefore stands
      // for the otherwise absent chapter V material (as well as lost VI.i).
      // Assign the placeholder to the single missing chapter so Chapter V can
      // be represented honestly as a lacuna rather than disappearing from the
      // menu.  No textual content is invented or split.
      if (
        /lacuna/i.test(paragraphText)
        && previousChapter !== null
        && nextChapter !== null
        && nextChapter === previousChapter + 2
      ) {
        inferredChapter = previousChapter + 1;
      }

      if (inferredChapter !== null && !chapterMap.has(paragraph.id)) {
        chapterMap.set(paragraph.id, inferredChapter);
      }
    });

    return chapterMap;
  };

  const normalizedSameAsTargets = (element) => {
    const sameAs = element?.getAttribute("sameAs") || "";

    return [...new Set(
      sameAs
        .split(/\s+/)
        .map(target => target.trim())
        .filter(Boolean)
        .map(target => target.includes("#")
          ? target.slice(target.lastIndexOf("#") + 1)
          : target
        )
        .filter(Boolean)
    )];
  };

  const canonicalParagraphTargetIds = (language, paragraph) => {
    if (!paragraph) return [];

    const paragraphPrefix = `latin-${currentIdBase()}-num`;

    if (displayedSourceUsesCanonicalIds(language)) {
      return paragraph.id?.startsWith(paragraphPrefix)
        ? [paragraph.id]
        : [];
    }

    const directTargets = normalizedSameAsTargets(paragraph)
      .filter(target => target.startsWith(paragraphPrefix));

    if (directTargets.length) return directTargets;

    // Legacy read-time fallback: language-layer IDs sometimes mirror the
    // canonical Latin ID even where sameAs is absent or malformed.
    const ownId = paragraph.id || "";
    const separator = ownId.indexOf("-");

    if (separator !== -1) {
      const mirroredTarget = `latin-${ownId.slice(separator + 1)}`;

      if (mirroredTarget.startsWith(paragraphPrefix)) {
        return [mirroredTarget];
      }
    }

    // Final legacy fallback: some recovered translations have no xml:id but
    // retain the canonical numeric unit in their visible <num>.
    const visibleNum = paragraph.querySelector("tei-num")?.innerText?.trim();
    const numMatch = visibleNum?.match(/^\[\s*(\d+[a-z]?)\s*\]/i);

    if (numMatch) {
      return [
        `latin-${currentIdBase()}-num${numMatch[1]}`
      ];
    }

    return [];
  };

  const alignedParagraphsForCanonicalId = (
    language,
    data,
    canonicalId
  ) => {
    if (!data || !canonicalId) return [];

    return [...data.querySelectorAll("tei-p")]
      .filter(paragraph =>
        canonicalParagraphTargetIds(language, paragraph)
          .includes(canonicalId)
      );
  };

  const wrapAlignedParagraphs = (
    paragraphs,
    kind,
    value
  ) => {
    if (!paragraphs.length) return null;

    if (paragraphs.length === 1) {
      return paragraphs[0].cloneNode(true);
    }

    const wrapper = document.createElement("tei-div2");
    wrapper.dataset.alignedView = kind;
    wrapper.setAttribute("n", String(value));

    paragraphs.forEach(paragraph => {
      wrapper.appendChild(paragraph.cloneNode(true));
    });

    return wrapper;
  };

  const canonicalChapterScope = (chapterNum) => {
    if (!canonicalFullData) return null;

    const language = activeWork.alignment.language;
    const idBase = currentIdBase();

    if (usesMilestoneChapters()) {
      return milestoneChapterView(
        language,
        canonicalFullData,
        chapterNum,
        true
      );
    }

    if (usesCitationDerivedChapters()) {
      return citationDerivedCanonicalChapterView(
        canonicalFullData,
        chapterNum
      );
    }

    return canonicalFullData.querySelector(
      `[id="latin-${idBase}-chapter${chapterNum}"]`
    );
  };

  const canonicalParagraphIdsForChapter = (chapterNum) => {
    const scope = canonicalChapterScope(chapterNum);
    if (!scope) return new Set();

    const prefix = `latin-${currentIdBase()}-num`;

    return new Set(
      [...scope.querySelectorAll("tei-p")]
        .map(paragraph => paragraph.id)
        .filter(id => id?.startsWith(prefix))
    );
  };

  const alignedChapterView = (
    language,
    data,
    chapterNum
  ) => {
    if (
      !data
      || chapterNum === null
      || chapterNum === undefined
      || chapterNum === ""
    ) {
      return data;
    }

    const canonicalIds = canonicalParagraphIdsForChapter(chapterNum);
    if (!canonicalIds.size) return null;

    const paragraphs = [...data.querySelectorAll("tei-p")]
      .filter(paragraph => {
        const targets = canonicalParagraphTargetIds(
          language,
          paragraph
        );

        return targets.some(target => canonicalIds.has(target));
      });

    if (!paragraphs.length) return null;

    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "chapter");
    wrapper.setAttribute("n", String(chapterNum));
    wrapper.dataset.syntheticChapter = "alignment-derived";

    paragraphs.forEach(paragraph => {
      wrapper.appendChild(paragraph.cloneNode(true));
    });

    return wrapper;
  };

  const alignedSectionView = (
    language,
    data,
    sectionNum
  ) => {
    if (!data || !sectionNum) return null;

    const canonicalId =
      `latin-${currentIdBase()}-num${sectionNum}`;

    const paragraphs = alignedParagraphsForCanonicalId(
      language,
      data,
      canonicalId
    );

    return wrapAlignedParagraphs(
      paragraphs,
      "section",
      sectionNum
    );
  };

  const latinNieseStartEntries = (data = canonicalFullData) => {
    if (!data || !supportsNieseSections()) return [];

    const prefix = `latin-${currentIdBase()}-num`;
    const entries = [];

    data.querySelectorAll("tei-p").forEach(paragraph => {
      if (!paragraph.id?.startsWith(prefix)) return;

      const rawNumber = paragraph.id.slice(prefix.length);
      if (!/^[1-9]\d*$/.test(rawNumber)) return;

      const number = parseInt(rawNumber, 10);
      const inheritedLabelPattern = new RegExp(
        `^\\s*\\[\\s*${number}\\s*\\]`
      );

      // Stable alignment IDs do not intrinsically establish Niese identity.
      // A legacy paragraph-start Niese anchor is accepted only when its
      // inherited visible [N] apparatus independently confirms that number.
      if (!inheritedLabelPattern.test(paragraph.textContent || "")) return;

      entries.push({
        number,
        kind: "paragraph",
        node: paragraph
      });
    });

    data.querySelectorAll('tei-milestone[unit="niese"][n]').forEach(marker => {
      const rawNumber = marker.getAttribute("n");
      if (!/^[1-9]\d*$/.test(rawNumber || "")) return;

      entries.push({
        number: parseInt(rawNumber, 10),
        kind: "milestone",
        node: marker
      });
    });

    entries.sort((a, b) => {
      if (a.node === b.node) return 0;

      const position = a.node.compareDocumentPosition(b.node);
      return position & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    });

    return entries;
  };

  const nieseEntry = (nieseNum, data = canonicalFullData) => (
    latinNieseStartEntries(data).find(
      entry => entry.number === parseInt(nieseNum, 10)
    ) || null
  );

  const makeGeneratedNieseLabel = (nieseNum) => {
    const label = document.createElement("tei-num");
    label.classList.add("niese-generated");
    label.textContent = `[${parseInt(nieseNum, 10)}]`;
    return label;
  };

  const latinNieseView = (data, nieseNum) => {
    if (!data || !nieseNum || !supportsNieseSections()) return null;

    const wanted = parseInt(nieseNum, 10);
    const entries = latinNieseStartEntries(data);
    const index = entries.findIndex(entry => entry.number === wanted);
    if (index === -1) return null;

    const start = entries[index];
    const end = entries[index + 1] || null;
    const book = start.node.closest("tei-div1") || data.querySelector("tei-div1") || data;
    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "niese-section");
    wrapper.setAttribute("n", String(wanted));
    wrapper.dataset.syntheticSection = "niese-derived";

    const startParagraph = start.kind === "paragraph"
      ? start.node
      : start.node.closest("tei-p");
    const endParagraph = end
      ? (end.kind === "paragraph" ? end.node : end.node.closest("tei-p"))
      : null;

    if (
      startParagraph
      && end
      && endParagraph === startParagraph
    ) {
      const paragraphWrapper = startParagraph.cloneNode(false);
      const range = document.createRange();

      if (start.kind === "paragraph") {
        range.setStart(startParagraph, 0);
      } else {
        range.setStartAfter(start.node);
      }

      range.setEndBefore(end.node);
      paragraphWrapper.appendChild(range.cloneContents());
      wrapper.appendChild(paragraphWrapper);
    } else {
      const range = document.createRange();

      if (start.kind === "paragraph") {
        range.setStartBefore(start.node);
      } else {
        range.setStartAfter(start.node);
      }

      if (end) {
        range.setEndBefore(end.node);
      } else {
        range.setEnd(book, book.childNodes.length);
      }

      wrapper.appendChild(range.cloneContents());
    }

    wrapper.querySelectorAll("tei-p").forEach(paragraph => {
      if (
        !paragraph.textContent.trim()
        && !paragraph.querySelector("tei-milestone, tei-num")
      ) {
        paragraph.remove();
      }
    });

    if (start.kind === "milestone") {
      const firstParagraph = wrapper.querySelector("tei-p");
      if (firstParagraph) {
        firstParagraph.insertBefore(
          makeGeneratedNieseLabel(wanted),
          firstParagraph.firstChild
        );
      }
    }

    return wrapper;
  };


  const bellumGreekRangeView = (data, scope) => {
    if (!data || !scope || !canonicalFullData) return null;

    const prefix = `latin-${currentIdBase()}-num`;
    const paragraphs = scope.matches?.("tei-p")
      ? [scope]
      : [...scope.querySelectorAll("tei-p")]
        .filter(paragraph => paragraph.id?.startsWith(prefix));
    if (!paragraphs.length) return null;

    // Use the original canonical nodes: a copied fragment has no position in
    // the full Latin book. Cardwell IDs locate ranges, never Niese identities.
    const rangeStart = document.createRange();
    rangeStart.setStartBefore(paragraphs[0]);
    rangeStart.collapse(true);
    const rangeEnd = document.createRange();
    rangeEnd.setStartAfter(paragraphs[paragraphs.length - 1]);
    rangeEnd.collapse(true);

    const entries = latinNieseStartEntries(canonicalFullData);
    const boundaries = entries.map(entry => {
      const boundary = document.createRange();
      if (entry.kind === "paragraph") boundary.setStartBefore(entry.node);
      else boundary.setStartAfter(entry.node);
      boundary.collapse(true);
      return boundary;
    });
    const numbers = new Set();

    entries.forEach((entry, index) => {
      const start = boundaries[index];
      const end = boundaries[index + 1];
      // [Niese start, next start) overlaps [Cardwell start, Cardwell end).
      // Include the citation already running at a coarse-unit boundary.
      if (
        start.compareBoundaryPoints(Range.START_TO_START, rangeEnd) < 0
        && (!end || end.compareBoundaryPoints(Range.START_TO_START, rangeStart) > 0)
      ) {
        numbers.add(entry.number);
      }
    });

    const greekParagraphs = [...data.querySelectorAll("tei-p[n]")]
      .filter(paragraph => numbers.has(Number(paragraph.getAttribute("n"))));
    return wrapAlignedParagraphs(
      greekParagraphs,
      scope.matches?.("tei-p") ? "section" : "chapter",
      scope.getAttribute("n") || state.sectionNum || state.chapterNum
    );
  };

  const greekNieseView = (data, nieseNum) => {
    if (!data || !nieseNum || !supportsNieseSections()) return null;

    const id = `greek-${currentIdBase()}-num${parseInt(nieseNum, 10)}`;
    return data.querySelector(`[id="${id}"]`);
  };

  const englishNieseStartEntries = (data) => {
    if (!data || !supportsNieseSections()) return [];
    const entries = [];
    data.querySelectorAll('tei-milestone[unit="niese"][n]').forEach(marker => {
      const rawNumber = marker.getAttribute("n");
      if (!/^[1-9]\d*$/.test(rawNumber || "")) return;
      entries.push({ number: parseInt(rawNumber, 10), kind: "milestone", node: marker });
    });
    entries.sort((a, b) => {
      if (a.node === b.node) return 0;
      const position = a.node.compareDocumentPosition(b.node);
      return position & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    });
    return entries;
  };

  const englishNieseView = (data, nieseNum) => {
    if (!data || !nieseNum || !supportsNieseSections()) return null;
    const wanted = parseInt(nieseNum, 10);
    const entries = englishNieseStartEntries(data);
    const index = entries.findIndex(entry => entry.number === wanted);
    if (index === -1) return null;

    const start = entries[index];
    const end = entries[index + 1] || null;
    const book = start.node.closest("tei-div1") || data.querySelector("tei-div1") || data;
    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "niese-section");
    wrapper.setAttribute("n", String(wanted));
    wrapper.dataset.syntheticSection = "niese-derived";

    const startParagraph = start.node.closest("tei-p");
    const endParagraph = end ? end.node.closest("tei-p") : null;

    if (startParagraph && end && endParagraph === startParagraph) {
      const paragraphWrapper = startParagraph.cloneNode(false);
      const range = document.createRange();
      range.setStartAfter(start.node);
      range.setEndBefore(end.node);
      paragraphWrapper.appendChild(range.cloneContents());
      wrapper.appendChild(paragraphWrapper);
    } else {
      const range = document.createRange();
      range.setStartAfter(start.node);
      if (end) range.setEndBefore(end.node);
      else range.setEnd(book, book.childNodes.length);
      wrapper.appendChild(range.cloneContents());
    }

    wrapper.querySelectorAll("tei-p").forEach(paragraph => {
      const lodgeOmission = activeWork.slug === "bellum"
        && state.sources.English === "lodge1602"
        && paragraph.querySelector('tei-gap[reason="omitted"][unit="niese-section"]');
      if (lodgeOmission) return;
      if (!paragraph.textContent.trim() && !paragraph.querySelector("tei-milestone, tei-num")) paragraph.remove();
    });

    const firstParagraph = wrapper.querySelector("tei-p");
    if (firstParagraph) {
      let labelContainer = firstParagraph;
      if (activeWork.slug === "bellum" && state.sources.English === "lodge1602") {
        const textWalker = document.createTreeWalker(firstParagraph, NodeFilter.SHOW_TEXT, {
          acceptNode: node => node.data.trim() && !node.parentElement.closest("tei-note, [data-original]")
            ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP
        });
        const firstText = textWalker.nextNode();
        // Keep the citation with the opening TCP block, including through inline wrappers.
        const firstBlock = firstText?.parentElement.closest(`tei-seg:is(
          [type="tcp-p"], [type="tcp-head"], [type="tcp-byline"],
          [type="tcp-argument"], [type="tcp-list"], [type="tcp-item"], [type="tcp-trailer"]
        )`);
        if (firstBlock && firstParagraph.contains(firstBlock)) labelContainer = firstBlock;
      }
      labelContainer.insertBefore(makeGeneratedNieseLabel(wanted), labelContainer.firstChild);
    }
    return wrapper;
  };

  const antiquitiesNieseLabelNumber = (num) => {
    const label = num?.textContent?.trim() || "";
    const numbers = label.match(/\d+/g);
    if (!numbers?.length) return null;

    const number = parseInt(numbers[numbers.length - 1], 10);
    return Number.isInteger(number) ? number : null;
  };

  const antiquitiesNieseRange = () => (
    nieseIdentityRegistry()?.range || activeWork.nieseRanges?.[parseInt(state.bookNum, 10)] || null
  );

  const antiquitiesNieseStartEntries = (language, data) => {
    if (
      !data
      || activeWork.slug !== "antiquities"
      || !supportsNieseSections()
    ) {
      return [];
    }

    const range = antiquitiesNieseRange();
    if (!range || range.length !== 2) return [];

    const [first, last] = range;
    const entries = [];

    data.querySelectorAll("tei-num").forEach(num => {
      // Header folio numbers and apparatus numbers are not narrative citations.
      if (!num.closest("tei-body") || !num.closest("tei-p[id]")
        || num.closest("tei-note, tei-app, tei-rdg")) return;
      if (language === "Latin" && nieseIdentityRegistry()?.suppressedLatinLabels.some(rule =>
        rule.paragraph === num.closest("tei-p")?.id && rule.label === num.textContent.trim())) return;
      const number = antiquitiesNieseLabelNumber(num);
      if (!Number.isInteger(number) || number < first || number > last) return;

      entries.push({
        number,
        kind: "num",
        node: num
      });
    });

    if (language === "Latin") {
      data.querySelectorAll('tei-milestone[unit="niese"][n]').forEach(marker => {
        if (!marker.closest("tei-body") || !marker.closest("tei-p[id]")
          || marker.closest("tei-note, tei-app, tei-rdg")) return;
        const rawNumber = marker.getAttribute("n");
        if (!/^[1-9]\d*$/.test(rawNumber || "")) return;

        const number = parseInt(rawNumber, 10);
        if (number < first || number > last) return;

        entries.push({
          number,
          kind: "milestone",
          node: marker
        });
      });
    }

    entries.sort((a, b) => {
      if (a.node === b.node) return 0;

      const position = a.node.compareDocumentPosition(b.node);
      return position & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    });

    return entries;
  };

  const antiquitiesNieseExactView = (language, data, nieseNum) => {
    if (!data || !nieseNum || !supportsNieseSections()) return null;

    const wanted = parseInt(nieseNum, 10);
    const identity = nieseIdentityRegistry()?.sections.find(section => section.number === wanted);
    if (identity?.[language]?.available === false) {
      const wrapper = document.createElement("tei-div2");
      wrapper.setAttribute("type", "niese-section"); wrapper.setAttribute("n", String(wanted));
      wrapper.dataset.syntheticSection = "niese-derived";
      wrapper.appendChild(structuralUnavailable(language, identity[language].note || "This section is unavailable in this source."));
      return wrapper;
    }
    const entries = antiquitiesNieseStartEntries(language, data);
    const index = entries.findIndex(entry => entry.number === wanted);
    if (index === -1) return null;

    const start = entries[index];
    const end = entries[index + 1] || null;
    const book = start.node.closest("tei-div1") || data.querySelector("tei-div1") || data;
    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "niese-section");
    wrapper.setAttribute("n", String(wanted));
    wrapper.dataset.syntheticSection = "niese-derived";

    const startParagraph = start.node.closest("tei-p");
    const endParagraph = end ? end.node.closest("tei-p") : null;

    const setRangeStart = range => {
      if (start.kind === "num") {
        range.setStartBefore(start.node);
      } else {
        range.setStartAfter(start.node);
      }
    };

    if (startParagraph && end && endParagraph === startParagraph) {
      const paragraphWrapper = startParagraph.cloneNode(false);
      const range = document.createRange();
      setRangeStart(range);
      range.setEndBefore(end.node);
      paragraphWrapper.appendChild(range.cloneContents());
      wrapper.appendChild(paragraphWrapper);
    } else {
      const range = document.createRange();
      setRangeStart(range);

      if (end) {
        range.setEndBefore(end.node);
      } else {
        range.setEnd(book, book.childNodes.length);
      }

      wrapper.appendChild(range.cloneContents());
    }

    wrapper.querySelectorAll("tei-p").forEach(paragraph => {
      if (
        !paragraph.textContent.trim()
        && !paragraph.querySelector(
          'tei-num, tei-milestone, tei-gap[reason="omitted"]'
        )
      ) {
        paragraph.remove();
      }
    });

    if (start.kind === "milestone") {
      const firstParagraph = wrapper.querySelector("tei-p");
      if (firstParagraph) {
        firstParagraph.insertBefore(
          makeGeneratedNieseLabel(wanted),
          firstParagraph.firstChild
        );
      }
    }

    if (identity?.[language]?.note) {
      const note = document.createElement("p");
      note.className = "alert alert-secondary niese-correspondence-note";
      note.setAttribute("role", "note"); note.textContent = identity[language].note;
      wrapper.insertBefore(note, wrapper.firstChild);
    }
    return wrapper;
  };

  const antiquitiesNieseContextView = (language, data, nieseNum) => {
    if (!data || !nieseNum || !supportsNieseSections()) return null;

    const start = antiquitiesNieseStartEntries(
      activeWork.alignment.language,
      canonicalFullData
    ).find(entry => entry.number === parseInt(nieseNum, 10));

    const canonicalParagraph = start?.node?.closest("tei-p") || null;
    const identity = nieseIdentityRegistry()?.sections.find(section => section.number === Number(nieseNum));
    const canonicalId = canonicalParagraph?.id || identity?.contextTarget || null;
    const paragraphs = canonicalId
      ? alignedParagraphsForCanonicalId(language, data, canonicalId)
      : [];

    const wrapper = paragraphs.length
      ? wrapAlignedParagraphs(paragraphs, "niese-context", nieseNum)
      : document.createElement("tei-div2");

    wrapper.setAttribute("type", "niese-context");
    wrapper.setAttribute("n", String(parseInt(nieseNum, 10)));

    const note = document.createElement("p");
    note.classList.add("niese-context-note");
    note.textContent =
      `${language} context: exact Niese-level segmentation is unavailable for this source.`;
    wrapper.insertBefore(note, wrapper.firstChild);

    return wrapper;
  };

  const antiquitiesNieseView = (language, data, nieseNum) => {
    if (language === "Latin" || language === "Greek") {
      return antiquitiesNieseExactView(language, data, nieseNum);
    }

    return antiquitiesNieseContextView(language, data, nieseNum);
  };

  const bellumNieseView = (language, data, nieseNum) => {
    if (!data || !nieseNum || !supportsNieseSections()) return null;

    if (language === "Latin") {
      return latinNieseView(data, nieseNum);
    }

    if (language === "Greek") {
      return greekNieseView(data, nieseNum);
    }

    if (language === "English") {
      return englishNieseView(data, nieseNum);
    }

    return null;
  };

  const canonicalNieseStartEntries = () => {
    if (activeWork.slug === "antiquities") {
      const entries = antiquitiesNieseStartEntries(
        activeWork.alignment.language,
        canonicalFullData
      );
      const registry = nieseIdentityRegistry();
      if (!registry) return entries;
      return registry.sections.map(section => entries.find(entry => entry.number === section.number)
        || {number: section.number, kind: "unavailable"});
    }

    return latinNieseStartEntries(canonicalFullData);
  };

  const nieseView = (language, data, nieseNum) => {
    if (activeWork.slug === "antiquities") {
      return antiquitiesNieseView(language, data, nieseNum);
    }

    return bellumNieseView(language, data, nieseNum);
  };

  const decorateNieseMarkers = (language, data) => {
    if (!data || !supportsNieseSections()) return;

    if (language === "Latin" || language === "English") {
      data.querySelectorAll('tei-milestone[unit="niese"][n]').forEach(marker => {
        const rawNumber = marker.getAttribute("n");
        if (!/^[1-9]\d*$/.test(rawNumber || "")) return;

        marker.classList.add("niese-marker");
        marker.textContent = `[${parseInt(rawNumber, 10)}]`;
        const note = nieseIdentityRegistry()?.sections.find(section => section.number === Number(rawNumber))?.[language]?.note;
        if (note) marker.title = note;
      });
      return;
    }

    if (activeWork.slug === "bellum" && language === "Greek") {
      const prefix = `greek-${currentIdBase()}-num`;
      const paragraphs = [
        ...(data.matches?.("tei-p") ? [data] : []),
        ...data.querySelectorAll("tei-p")
      ];

      paragraphs.forEach(paragraph => {
        if (!paragraph.id?.startsWith(prefix)) return;
        if (paragraph.querySelector(":scope > tei-num.niese-generated")) return;

        const rawNumber = paragraph.getAttribute("n")
          || paragraph.id.slice(prefix.length);
        if (!/^[1-9]\d*$/.test(rawNumber || "")) return;

        paragraph.insertBefore(
          makeGeneratedNieseLabel(rawNumber),
          paragraph.firstChild
        );
      });
    }
  };

  const decorateContraApionemSectionMarkers = (language, data) => {
    if (!data || activeWork.slug !== "contra-apionem") return;

    const prefix = `${String(language).toLowerCase()}-${currentIdBase()}-num`;
    const paragraphs = [
      ...(data.matches?.("tei-p") ? [data] : []),
      ...data.querySelectorAll("tei-p")
    ];

    paragraphs.forEach(paragraph => {
      if (!paragraph.id?.startsWith(prefix)) return;
      if (paragraph.querySelector(":scope > tei-num.niese-generated")) return;

      const rawNumber = paragraph.getAttribute("n")
        || paragraph.id.slice(prefix.length);
      if (!/^[1-9]\d*$/.test(rawNumber || "")) return;

      paragraph.insertBefore(
        makeGeneratedNieseLabel(rawNumber),
        paragraph.firstChild
      );
    });

    // Five Latin starts lie inside words rather than at paragraph starts.
    if (language === "Latin") {
      data.querySelectorAll('tei-milestone[unit="niese"][n]').forEach(marker => {
        const rawNumber = marker.getAttribute("n");
        if (!/^[1-9]\d*$/.test(rawNumber || "")) return;
        marker.hidden = false;
        marker.classList.add("niese-marker");
        marker.textContent = `[${parseInt(rawNumber, 10)}]`;
      });
    }
  };

  const citationDerivedChapterView = (language, data, chapterNum) => {
    if (!data || chapterNum === null || chapterNum === undefined || chapterNum === "") {
      return data;
    }

    if (displayedSourceUsesCanonicalIds(language)) {
      if (String(chapterNum) === "0") {
        const idBase = currentIdBase();

        return data.querySelector(
          `[id="latin-${idBase}-chapter0"]`
        );
      }

      return citationDerivedCanonicalChapterView(
        data,
        chapterNum
      );
    }

    return alignedChapterView(language, data, chapterNum);
  };

  const citationDerivedChapterNumbers = () => {
    const chapters = [...new Set(canonicalParagraphChapterMap().values())]
      .filter(Number.isInteger)
      .sort((a, b) => a - b);

    return [0, ...chapters];
  };

  const selectView = (language, data, idBase) => {
    if (!data) return null;
    if (usesTraditionalStructure()) {
      if (state.viewingLevel === "bamberg-level") {
        const record = bambergSelection();
        return record ? traditionalRangeView(language, data, record)
          : structuralUnavailable(language, "This book has no matching audited Bamberg division identity.");
      }
      if (["chapter-level", "subchapter-level"].includes(state.viewingLevel))
        return traditionalRangeView(language, data, traditionalSelection());
      if (state.viewingLevel === "section-level" && state.sectionNum) return antiquitiesUnitView(language, data);
      if (state.viewingLevel === "section-level") return data;
    }

    const usesCanonicalIds = displayedSourceUsesCanonicalIds(language);

    if (
      activeWork.slug === "bellum"
      && language === "Greek"
      && ["chapter-level", "section-level"].includes(state.viewingLevel)
    ) {
      const scope = state.viewingLevel === "section-level" && state.sectionNum
        ? canonicalFullData?.querySelector(
          `[id="latin-${idBase}-num${state.sectionNum}"]`
        )
        : (state.chapterNum ? canonicalChapterScope(state.chapterNum) : null);
      return scope ? bellumGreekRangeView(data, scope) : data;
    }

    switch(state.viewingLevel) {
      case "book-level":
        return data;
      case "niese-level":
        if (!state.nieseNum || !supportsNieseSections()) return data;
        return nieseView(language, data, state.nieseNum);
      case "chapter-level":
        if (!state.chapterNum) return data;

        if (usesMilestoneChapters()) {
          return milestoneChapterView(language, data, state.chapterNum);
        }

        if (usesCitationDerivedChapters()) {
          return citationDerivedChapterView(language, data, state.chapterNum);
        }

        if (!usesCanonicalIds) {
          return alignedChapterView(
            language,
            data,
            state.chapterNum
          );
        }

        return data.querySelector(
          `[id="latin-${idBase}-chapter${state.chapterNum}"]`
        );
      case "section-level":
        if (state.sectionNum) {
          if (activeWork.sectionMilestoneUnit) {
            if (usesMilestoneChapters() && state.chapterNum) {
              return milestoneSectionView(
                language,
                data,
                state.chapterNum,
                state.sectionNum
              );
            }

            return milestoneAwareSectionView(
              language,
              data,
              state.sectionNum
            );
          }

          if (usesMilestoneChapters() && state.chapterNum) {
            return milestoneSectionView(
              language,
              data,
              state.chapterNum,
              state.sectionNum
            );
          }

          if (!usesCanonicalIds) {
            return alignedSectionView(
              language,
              data,
              state.sectionNum
            );
          }

          return data.querySelector(
            `[id="latin-${idBase}-num${state.sectionNum}"]`
          );
        }

        if (state.chapterNum) {
          if (usesMilestoneChapters()) {
            return milestoneChapterView(language, data, state.chapterNum);
          }

          if (usesCitationDerivedChapters()) {
            return citationDerivedChapterView(language, data, state.chapterNum);
          }

          if (!usesCanonicalIds) {
            return alignedChapterView(
              language,
              data,
              state.chapterNum
            );
          }

          return data.querySelector(
            `[id="latin-${idBase}-chapter${state.chapterNum}"]`
          );
        }

        return data;
      default:
        return data;
    }
  };

  const citationDerivedCanonicalChapterView = (data, chapterNum) => {
    if (!data || chapterNum === null || chapterNum === undefined || chapterNum === "") {
      return data;
    }

    if (String(chapterNum) === "0") {
      return data.querySelector(`[id="latin-${currentIdBase()}-chapter0"]`);
    }

    const wantedChapter = parseInt(chapterNum);
    const chapterMap = canonicalParagraphChapterMap();
    const wrapper = document.createElement("tei-div2");
    wrapper.setAttribute("type", "chapter");
    wrapper.setAttribute("n", String(wantedChapter));
    wrapper.dataset.syntheticChapter = "citation-derived";

    const seenIds = new Set();

    data.querySelectorAll("tei-p").forEach(paragraph => {
      if (!chapterMap.has(paragraph.id)) return;
      if (chapterMap.get(paragraph.id) !== wantedChapter) return;
      if (seenIds.has(paragraph.id)) return;

      seenIds.add(paragraph.id);
      wrapper.appendChild(paragraph.cloneNode(true));
    });

    return wrapper.childElementCount ? wrapper : null;
  };

  const selectCanonicalView = (data, idBase) => {
    if (!data) return null;
    if (usesTraditionalStructure()) return selectView(activeWork.alignment.language, data, idBase);

    switch(state.viewingLevel) {
      case "book-level":
        return data;
      case "niese-level":
        if (!state.nieseNum || !supportsNieseSections()) return data;
        return nieseView(activeWork.alignment.language, data, state.nieseNum);
      case "chapter-level":
        if (!state.chapterNum) return data;

        if (usesMilestoneChapters()) {
          return milestoneChapterView(
            activeWork.alignment.language,
            data,
            state.chapterNum,
            true
          );
        }

        if (usesCitationDerivedChapters()) {
          return citationDerivedCanonicalChapterView(data, state.chapterNum);
        }

        return data.querySelector(
          `[id*="latin-${idBase}-chapter${state.chapterNum}"]`
        );
      case "section-level":
        if (state.sectionNum) {
          if (activeWork.sectionMilestoneUnit) {
            if (usesMilestoneChapters() && state.chapterNum) {
              return milestoneSectionView(
                activeWork.alignment.language,
                data,
                state.chapterNum,
                state.sectionNum,
                true
              );
            }

            return milestoneAwareSectionView(
              activeWork.alignment.language,
              data,
              state.sectionNum
            );
          }

          if (usesMilestoneChapters() && state.chapterNum) {
            return milestoneSectionView(
              activeWork.alignment.language,
              data,
              state.chapterNum,
              state.sectionNum,
              true
            );
          }

          return data.querySelector(`[id*="latin-${idBase}-num${state.sectionNum}"]`);
        }

        if (state.chapterNum) {
          if (usesMilestoneChapters()) {
            return milestoneChapterView(
              activeWork.alignment.language,
              data,
              state.chapterNum,
              true
            );
          }

          if (usesCitationDerivedChapters()) {
            return citationDerivedCanonicalChapterView(data, state.chapterNum);
          }

          return data.querySelector(
            `[id*="latin-${idBase}-chapter${state.chapterNum}"]`
          );
        }

        return data;
      default:
        return data;
    }
  };

  const updateLodgeNotesUI = () => {
    const isLodge = activeWork.slug === "bellum"
      && state.sources.English === "lodge1602";

    if (lodgeNotesRow) {
      lodgeNotesRow.hidden = !isLodge;
      lodgeNotesRow.classList.toggle("hidden", !isLodge);
    }
    if (lodgeNotesCheckbox) lodgeNotesCheckbox.checked = state.lodgeNotesVisible;
    englishPane?.classList.toggle("lodge-notes-hidden", isLodge && !state.lodgeNotesVisible);
  };

  const updateLanguageUI = () => {
    Object.entries(languagePanes).forEach(([language, pane]) => {
      if (!pane) return;

      const configured = Boolean(
        activeWork.languages[language]
        && state.sources[language]
      );

      const checkbox = languagePaneCheckboxes[language];
      const checkboxWrapper = checkbox?.closest(".form-check");
      const sourceMenu = sourceSelectMenus[language];
      const sourceWrapper = sourceMenu?.closest(".source-select-row");

      if (checkboxWrapper) {
        checkboxWrapper.hidden = !configured;
        checkboxWrapper.classList.toggle("hidden", !configured);
      }

      if (!configured) {
        if (checkbox) checkbox.checked = false;

        pane.hidden = true;
        pane.classList.add("hidden");

        if (sourceWrapper) {
          sourceWrapper.hidden = true;
          sourceWrapper.classList.add("hidden");
        }

        return;
      }

      pane.hidden = false;

      if (checkbox && !checkbox.disabled) {
        pane.classList.toggle("hidden", !checkbox.checked);
      } else {
        pane.classList.remove("hidden");
      }

      const sources = availableSourceEntries(language);
      const selectedSource = activeWork.languages[language]
        ?.sources[state.sources[language]];
      const heading = pane.querySelector("h3");

      if (heading) {
        heading.innerText = selectedSource?.label
          ? `${language}: ${selectedSource.label}`
          : language;
      }

      if (sourceMenu) {
        sourceMenu.options.length = 0;

        sources.forEach(([sourceKey, source]) => {
          sourceMenu.add(
            new Option(
              source.label,
              sourceKey,
              sourceKey === state.sources[language],
              sourceKey === state.sources[language]
            )
          );
        });

        const showSelector = sources.length > 1;

        if (sourceWrapper) {
          sourceWrapper.hidden = !showSelector;
          sourceWrapper.classList.toggle(
            "hidden",
            !showSelector
          );
        }
      }
    });
    updateLodgeNotesUI();
  };

  const updateNavigationForms = () => {
    const nieseAvailable = supportsNieseSections();
    const showChapter = (
      state.viewingLevel !== "book-level"
      && state.viewingLevel !== "niese-level"
      && state.viewingLevel !== "bamberg-level"
      && !isPreface()
    );
    const showSection = state.viewingLevel === "section-level";
    const bambergControl = document.getElementById("bamberg-level");
    const bambergAvailable = usesTraditionalStructure() && bambergRows().length > 0;
    if (bambergControl) bambergControl.disabled = !bambergAvailable;
    if (bambergSelectMenu) bambergSelectMenu.disabled = !bambergAvailable;
    bambergSelectForm?.classList.toggle("hidden", !bambergAvailable || state.viewingLevel !== "bamberg-level");
    subchapterSelectForm?.classList.toggle("hidden", !usesTraditionalStructure() || state.viewingLevel !== "subchapter-level");
    const subchapterControl = document.getElementById("subchapter-level");
    if (subchapterControl) {
      subchapterControl.closest(".form-check").hidden = !usesTraditionalStructure();
      if (usesTraditionalStructure()) {
        const available = traditionalRows("subchapter", isPreface() ? "" : state.chapterNum).length > 0;
        subchapterControl.disabled = !available;
        if (subchapterSelectMenu) subchapterSelectMenu.disabled = !available;
      }
    }
    if (usesTraditionalStructure() && state.viewingLevel === "section-level") chapterSelectForm.classList.add("hidden");
    const showNiese = state.viewingLevel === "niese-level" && nieseAvailable;

    const sectionIsNiese = sectionLevelUsesNiese();

    const sectionSelectorLabel = sectionSelectForm.querySelector(
      'label[for="section-selector"]'
    );
    if (sectionSelectorLabel) {
      sectionSelectorLabel.textContent = sectionIsNiese
        ? "Select a Niese section:"
        : (usesTraditionalStructure() ? "Select an Alignment unit:" : "Select a sub-chapter:");
    }

    const sectionLevelControl = document.getElementById("section-level");
    const sectionLevelLabel = sectionLevelControl
      ?.closest(".form-check")
      ?.querySelector('label[for="section-level"]');

    if (sectionLevelLabel) {
      sectionLevelLabel.textContent = sectionIsNiese
        ? "Niese section"
        : (usesTraditionalStructure() ? "Alignment unit" : "Sub-chapter");
    }

    chapterSelectForm.classList.toggle("hidden", !(hasSourceContents() || showChapter) || (usesTraditionalStructure() && showSection));
    sectionSelectForm.classList.toggle("hidden", !showSection);
    if (nieseSelectForm) nieseSelectForm.classList.toggle("hidden", !showNiese);

    const nieseLevelControl = document.getElementById("niese-level");
    const nieseLevelWrapper = nieseLevelControl?.closest(".form-check");
    if (nieseLevelControl) nieseLevelControl.disabled = !nieseAvailable;
    if (nieseLevelWrapper) {
      nieseLevelWrapper.hidden = !nieseAvailable;
      nieseLevelWrapper.classList.toggle("hidden", !nieseAvailable);
    }
  };

  const syncNavigationControls = () => {
    bookSelectMenu.value = state.bookNum;
    chapterSelectMenu.value = state.viewingLevel === "contents-level" ? "contents" : state.chapterNum ?? "";
    sectionSelectMenu.value = state.sectionNum ?? "";
    if (subchapterSelectMenu) subchapterSelectMenu.value = state.subchapterNum ?? "";
    if (nieseSelectMenu) nieseSelectMenu.value = state.nieseNum ?? "";
    if (bambergSelectMenu) bambergSelectMenu.value = state.bambergId ?? "";
    const divisions = bambergRows(), index = divisions.findIndex(row => row.id === state.bambergId);
    if (bambergPrevious) bambergPrevious.disabled = index <= 0;
    if (bambergNext) bambergNext.disabled = index < 0 || index >= divisions.length - 1;
    const citations = canonicalNieseStartEntries(), citationIndex = citations.findIndex(entry => entry.number === Number(state.nieseNum));
    if (niesePrevious) niesePrevious.disabled = citationIndex <= 0;
    if (nieseNext) nieseNext.disabled = citationIndex < 0 || citationIndex >= citations.length - 1;

    const levelControl = document.getElementById(state.viewingLevel);
    if (state.viewingLevel === "contents-level") viewingLevelSelectMenu.querySelectorAll("input[type=radio]").forEach(control => { control.checked = false; });
    if (levelControl) levelControl.checked = true;
  };

  const menuHasValue = (menu, value) => (
    [...menu.options].some(option => option.value === String(value))
  );

  const normalizeNavigationState = () => {
    if (usesTraditionalStructure() || state.viewingLevel === "contents-level") return false;
    let changed = false;

    if (
      state.viewingLevel === "niese-level"
      && !supportsNieseSections()
    ) {
      state.nieseNum = null;
      state.viewingLevel = "book-level";
      changed = true;
    }

    if (
      state.chapterNum !== null
      && state.chapterNum !== ""
      && !menuHasValue(chapterSelectMenu, state.chapterNum)
    ) {
      state.chapterNum = null;
      state.sectionNum = null;
      state.viewingLevel = "book-level";
      changed = true;
    }

    if (
      state.viewingLevel === "section-level"
      && state.sectionNum
      && !menuHasValue(sectionSelectMenu, state.sectionNum)
    ) {
      state.sectionNum = null;
      state.viewingLevel = state.chapterNum !== null
        ? "chapter-level"
        : "book-level";
      changed = true;
    }

    if (
      state.viewingLevel === "niese-level"
      && state.nieseNum
      && (
        !nieseSelectMenu
        || !menuHasValue(nieseSelectMenu, state.nieseNum)
      )
    ) {
      state.nieseNum = null;
      state.viewingLevel = "book-level";
      changed = true;
    }

    return changed;
  };

  const setBookSelectOptions = () => {
    let optionList = bookSelectMenu.options;
    optionList.length = 0;

    let options = [...Array(activeWork.bookCount).keys()].map(num => {
      const bookNumber = num + 1;
      const available = (
        !activeWork.availableBooks
        || activeWork.availableBooks.includes(bookNumber)
      );

      return {
        "text": bookNumber.toLocaleString(),
        "value": bookNumber.toLocaleString().padStart(2, "0"),
        "disabled": !available
      };
    });

    if (activeWork.preface) {
      options.unshift({
        "text": activeWork.preface.label,
        "value": activeWork.preface.value
      });
    }

    const selectedOption = options.find(option => option.value === state.bookNum);
    if (selectedOption) selectedOption.selected = true;

    options.forEach(option => {
      const optionElement = new Option(
        option.text,
        option.value,
        Boolean(option.selected),
        Boolean(option.selected)
      );

      optionElement.disabled = Boolean(option.disabled);
      optionList.add(optionElement);
    });
  };

  const fetchData = async () => {
    await loadTraditionalRegistry();
    await loadContentsRegistry();
    await loadNieseIdentityRegistry();
    if (state.viewingLevel === "contents-level" && !hasSourceContents()) state.viewingLevel = "book-level";
    const filename = currentFilename();
    const idBase = currentIdBase();

    normalizeSourcesForBook();

    fullData = {};
    viewData = {};

    for (const language of Object.keys(activeWork.languages)) {
      const sourceKey = state.sources[language];

      if (!sourceKey) {
        fullData[language] = null;
        continue;
      }

      fullData[language] = await fetchTei(
        language,
        sourceKey,
        filename
      );
    }

    const canonicalLanguage = activeWork.alignment.language;
    const canonicalSource = activeWork.alignment.source;

    if (
      state.sources[canonicalLanguage] === canonicalSource
      && fullData[canonicalLanguage]
    ) {
      canonicalFullData = fullData[canonicalLanguage];
    } else {
      canonicalFullData = await fetchTei(
        canonicalLanguage,
        canonicalSource,
        filename
      );
    }

    canonicalViewData = selectCanonicalView(canonicalFullData, idBase);

    Object.entries(fullData).forEach(([language, data]) => {
      viewData[language] = selectView(language, data, idBase);
    });

    if (state.viewingLevel === "contents-level") {
      for (const language of Object.keys(activeWork.languages)) viewData[language] = await contentsView(language);
    }
    setChapterSelectOptions();
    setTraditionalSubchapterOptions();
    setBambergOptions();
    setSectionSelectOptions();
    setNieseSelectOptions();
  };

  const addContraApionemTransmissionNotice = () => {
    greekPane?.querySelectorAll(".contra-apionem-lacuna-notice").forEach(el => el.remove());

    if (activeWork.slug !== "contra-apionem" || !greekPane) return;

    const greekView = viewData.Greek;
    if (!greekView) return;

    const selector = 'tei-p[type="latin-fallback"], tei-p[type="mixed-lacuna-edge"]';
    const containsFallback = (
      greekView.matches?.(selector)
      || greekView.querySelector?.(selector)
    );

    if (!containsFallback) return;

    // Suppress old-Latin fallback paragraphs in the Greek pane. The same text
    // is already available in the Boysen Latin pane; repeating it under a
    // "Greek: Niese" heading is misleading.
    greekPane.querySelectorAll('tei-p[type="latin-fallback"]').forEach(paragraph => {
      paragraph.hidden = true;
    });

    const notice = document.createElement("div");
    notice.className = "alert alert-secondary contra-apionem-lacuna-notice";
    notice.setAttribute("role", "note");
    notice.innerHTML = "<strong>Greek textual lacuna:</strong> the surviving Greek text is incomplete in Book II, §§51–113; passages for which no Greek survives are left blank in this pane.";
    greekPane.prepend(notice);
  };

  // Omission apparatus belongs to the rendered view, never the source text.
  const decorateOmittedGaps = (language, data) => {
    data.querySelectorAll('tei-gap[reason="omitted"]').forEach(gap => {
      if (gap.textContent.trim()) return;

      // Retain a source notice without adding a redundant editorial notice.
      const context = (gap.closest("tei-p") || gap.parentElement).cloneNode(true);
      context.querySelectorAll(".tei-omission-notice").forEach(notice => notice.remove());
      if (/\bomitted\s+(?:in|from)\b/i.test(context.textContent)) return;

      // Respect an established presentation, such as the Lodge CSS notice.
      const hasNotice = ["::before", "::after"].some(pseudo => {
        const content = window.getComputedStyle(gap, pseudo).content;
        return content && !["none", "normal", '""', "''"].includes(content);
      });
      if (hasNotice) return;

      const notice = document.createElement("span");
      notice.className = "tei-omission-notice";
      notice.setAttribute("role", "note");
      notice.textContent = `[Omitted in this ${language} witness]`;
      gap.appendChild(notice);
    });
  };

  const renderUI = () => {
    // Clear panes if text already loaded.
    Object.values(languagePanes).forEach(pane => {
      if (!pane) return;

      pane.childNodes.forEach(node => {
        if (node.localName !== "h3") {
          pane.removeChild(node);
        }
      });
    });

    Object.entries(viewData).forEach(([language, data]) => {
      const pane = languagePanes[language];

      if (pane && data) {
        // The canonical DEH source uses empty <unclear/> elements to encode
        // Ussani's printed crux (dagger). CETEI preserves the empty element
        // but has no visible default representation, so supply the publication
        // glyph in the site layer without changing the canonical XML.
        if (activeWork.slug === "deh" && language === "Latin") {
          data.querySelectorAll("tei-unclear:empty").forEach(marker => {
            marker.textContent = "†";
          });
        }

        // Chapter milestones are editorial structure markers, not displayed
        // text.  Hide them explicitly in book-level views as well as in the
        // synthetic chapter fragments produced above.
        if (["antiquities", "contra-apionem"].includes(activeWork.slug)) {
          data.querySelectorAll('tei-milestone[unit="chapter"]').forEach(marker => {
            marker.hidden = true;
          });
        }

        if (usesTraditionalStructure()) data.querySelectorAll('tei-anchor[type="traditional-boundary"], tei-anchor[type="bamberg-boundary"]').forEach(marker => marker.hidden = true);
        decorateNieseMarkers(language, data);
        decorateContraApionemSectionMarkers(language, data);
        pane.appendChild(data);
        decorateOmittedGaps(language, data);
      }
    });

    bookLabel.innerText = currentBookLabel();
    chapterLabel.innerText = (
      state.chapterNum !== null
      && state.chapterNum !== ""
      && state.viewingLevel !== "book-level"
    ) ? chapterDisplayLabel() : "";
    sectionLabel.innerText = (
      state.nieseNum
      && state.viewingLevel === "niese-level"
    )
      ? `Niese section ${parseInt(state.nieseNum, 10)}`
      : (
        state.sectionNum
        && state.viewingLevel === "section-level"
      )
        ? (
          sectionLevelUsesNiese()
            ? `Niese section ${parseInt(state.sectionNum, 10)}`
            : sectionDisplayLabel()
        )
        : "";

    if (usesTraditionalStructure() && state.viewingLevel === "subchapter-level")
      sectionLabel.innerText = state.subchapterNum ? `Subchapter ${state.subchapterNum}` : "";
    if (usesTraditionalStructure() && state.viewingLevel === "bamberg-level")
      sectionLabel.innerText = bambergSelection() ? `Bamberg division ${bambergSelection().display}` : "Bamberg division";
    if (state.viewingLevel === "contents-level") { chapterLabel.innerText = "Table of contents"; sectionLabel.innerText = ""; }
    updateLanguageUI();
    updateNavigationForms();
    addContraApionemTransmissionNotice();
    updateTraditionalNotice();
    syncNavigationControls();
    // Optional scholarly parallels live outside the textual alignment layer.
    if (activeWork.slug === "deh") {
      document.dispatchEvent(new CustomEvent("deh-view-rendered", {
        detail: {
          book: parseInt(state.bookNum, 10),
          chapter: state.chapterNum,
          num: state.sectionNum,
          level: state.viewingLevel
        }
      }));
    }
  };

  const displayedLatinTarget = (paragraphId) => {
    const exactTarget = document.getElementById(paragraphId);

    if (exactTarget) return exactTarget;

    return latinPane.querySelector(`[sameAs*="${paragraphId}"]`);
  };

  const parseAnnotations = () => {
    const annotations = usesTraditionalStructure()
      ? [...canonicalFullData.getElementsByTagName("tei-app")]
      : canonicalFullData.getElementsByTagName("tei-app");
    annotatedParagraphs = [];
    let htmlString = '';

    const bookIdString = activeWork.idPrefix;

    annotations.forEach(anno => {
      if (anno.children.length < 1) return;

      const paragraphTag = anno.children[0].getAttribute('source');

      if (!paragraphTag || !paragraphTag.includes(`latin-${bookIdString}`)) return;

      const paragraphId = paragraphTag.replace('#', '');

      // Only show annotations that refer to displayed canonical paragraphs.
      if (
        !canonicalViewData.querySelector(`[id*="${paragraphId}"]`)
        && !canonicalViewData.id.includes(paragraphId)
      ) return;

      annotatedParagraphs.push(paragraphId);
      htmlString += `<br /><b>${paragraphId}</b> <br />`;

      anno.children.forEach(child => {
        if (
          !child.getAttribute('source')
          || child.getAttribute('source') === ''
          || child.getAttribute('source').includes(`latin-${bookIdString}`)
        ) return;

        const witnessElement = canonicalFullData.querySelector(
          `[id*="${child.getAttribute('source').replace("#","")}"]`
        );

        const witnessText = witnessElement.innerText;

        if (child.attributes.source.value !== "#FlaviusJosephusAntiquities") {
          htmlString += `${witnessText}: <em>${child.innerText}</em> <br />`;
        }
      });
    });

    annotationsList.innerHTML = htmlString;

    // Do not present an empty annotation accordion or highlight control for
    // texts (such as DEH Book I) that contain no encoded <app> annotations.
    const hasAnnotations = annotations.length > 0;
    if (annotationsPanel) annotationsPanel.hidden = !hasAnnotations;

    const highlightWrapper = highlightCheckbox?.closest(".form-check");
    if (highlightWrapper) highlightWrapper.hidden = !hasAnnotations;
    if (!hasAnnotations && highlightCheckbox) highlightCheckbox.checked = false;

    if (highlightCheckbox.checked) {
      annotatedParagraphs.forEach(paragraphId => {
        const target = displayedLatinTarget(paragraphId);
        if (target) target.classList.add("highlight");
      });
    }
  };

  const setBambergOptions = () => {
    if (!bambergSelectMenu || !usesTraditionalStructure()) return;
    bambergSelectMenu.options.length = 0;
    bambergRows().forEach(row => bambergSelectMenu.add(new Option(row.display, row.id)));
  };
  const setTraditionalSubchapterOptions = () => {
    if (!subchapterSelectMenu || !usesTraditionalStructure()) return;
    subchapterSelectMenu.options.length = 0;
    subchapterSelectMenu.add(new Option("", ""));
    traditionalRows("subchapter", isPreface() ? "" : (state.chapterNum || ""))
      .forEach(row => subchapterSelectMenu.add(new Option(row.display, row.subchapter)));
  };
  const setChapterNavigationOptions = () => {
    if (usesTraditionalStructure()) {
      chapterSelectMenu.options.length = 0;
      chapterSelectMenu.add(new Option("", ""));
      traditionalRows("chapter").forEach(row => chapterSelectMenu.add(new Option(row.display, row.chapter)));
      return;
    }
    if (state.viewingLevel === "book-level" && !hasSourceContents()) return;

    let latinChapters = [];

    if (usesMilestoneChapters()) {
      latinChapters = milestoneChapterNumbers();
    } else if (usesCitationDerivedChapters()) {
      latinChapters = citationDerivedChapterNumbers();
    } else {
      canonicalFullData.getElementsByTagName("tei-div2").forEach(el => {
        // Null checking for chapters that are missing IDs.
        if (el.id.split("-")[2]) {
          const chapterNumber = parseInt(
            el.id.split("-")[2].replace("chapter","")
          );
          latinChapters.push(chapterNumber);
        }
      });
    }

    let optionList = chapterSelectMenu.options;
    optionList.length = 0;

    let options = latinChapters.map(num => ({
      "text": activeWork.chapterLabels?.[String(num)] || (num).toLocaleString(),
      "value": (num).toLocaleString()
    }));

    options.unshift({
      "text": '',
      "value": ''
    });

    options.forEach(option =>
      optionList.add(
        new Option(option.text, option.value, option.selected)
      )
    );
  };

  const setChapterSelectOptions = () => {
    setChapterNavigationOptions();
    [...chapterSelectMenu.options].filter(option => option.value === "contents").forEach(option => option.remove());
    if (hasSourceContents()) chapterSelectMenu.add(new Option("Table of contents", "contents"), 0);
  };

  const setSectionSelectOptions = () => {
    if (usesTraditionalStructure()) {
      sectionSelectMenu.options.length = 0;
      sectionSelectMenu.add(new Option("", ""));
      const prefix = `latin-${currentIdBase()}-num`;
      canonicalFullData.querySelectorAll("tei-p[id]").forEach(p => {
        if (!p.id.startsWith(prefix)) return;
        const suffix = p.id.slice(prefix.length);
        if (suffix) sectionSelectMenu.add(new Option(suffix, suffix));
      });
      return;
    }
    if (state.viewingLevel !== "section-level") return;
    if (activeWork.sectionMilestoneUnit) {
      // Section navigation is global by default. If a Boysen chapter has
      // already been selected, narrow the menu to that chapter; otherwise
      // expose every Niese section in the current book.
      const hasChapter = (
        state.chapterNum !== null
        && state.chapterNum !== ""
        && String(state.chapterNum) !== "0"
      );

      const scope = hasChapter
        ? (
          milestoneChapterView(
            activeWork.alignment.language,
            canonicalFullData,
            state.chapterNum,
            true
          ) || canonicalFullData
        )
        : canonicalFullData;

      const prefix = `latin-${currentIdBase()}-num`;
      const seen = new Set();
      const sections = [...scope.querySelectorAll(`[id^="${prefix}"]`)]
        .filter(el => (
          el.matches("tei-p")
          || (
            el.matches("tei-milestone")
            && el.getAttribute("unit") === activeWork.sectionMilestoneUnit
          )
        ))
        .map(el => {
          const sectionNumber = parseInt(
            el.id.split("-")[2]?.replace("num", "")
          );
          return {
            number: sectionNumber,
            label: sectionNumber.toLocaleString()
          };
        })
        .filter(section => (
          Number.isInteger(section.number)
          && !seen.has(section.number)
          && seen.add(section.number)
        ));

      const optionList = sectionSelectMenu.options;
      optionList.length = 0;
      optionList.add(new Option("", ""));
      sections.forEach(section => (
        optionList.add(new Option(section.label, String(section.number)))
      ));
      return;
    }


    let sections = [];
    let sectionParagraphs = [];

    if (
      usesMilestoneChapters()
      && state.chapterNum !== null
      && state.chapterNum !== ""
      && String(state.chapterNum) !== "0"
    ) {
      const chapterScope = milestoneChapterView(
        activeWork.alignment.language,
        canonicalFullData,
        state.chapterNum,
        true
      );

      if (chapterScope) {
        const seenIds = new Set();
        chapterScope.querySelectorAll("tei-p").forEach(paragraph => {
          if (!paragraph.id || seenIds.has(paragraph.id)) return;
          seenIds.add(paragraph.id);
          sectionParagraphs.push(paragraph);
        });
      }
    } else if (
      usesCitationDerivedChapters()
      && state.chapterNum !== null
      && state.chapterNum !== ""
      && String(state.chapterNum) !== "0"
    ) {
      const wantedChapter = parseInt(state.chapterNum);
      const chapterMap = canonicalParagraphChapterMap();
      const seenIds = new Set();

      canonicalFullData.querySelectorAll("tei-p").forEach(paragraph => {
        if (chapterMap.get(paragraph.id) !== wantedChapter) return;
        if (seenIds.has(paragraph.id)) return;

        seenIds.add(paragraph.id);
        sectionParagraphs.push(paragraph);
      });
    } else {
      let sectionScope = canonicalFullData;

      if (state.chapterNum !== null && state.chapterNum !== "") {
        const chapterId = `latin-${currentIdBase()}-chapter${state.chapterNum}`;
        const chapter = canonicalFullData.querySelector(`[id="${chapterId}"]`);

        if (chapter) sectionScope = chapter;
      }

      sectionParagraphs = [...sectionScope.getElementsByTagName("tei-p")];
    }

    sectionParagraphs.forEach(el => {
      const sectionNumber = parseInt(
        el?.id?.split("-")[2]?.replace("num","")
      );

      if (!sectionNumber) return;

      let label = sectionNumber.toLocaleString();

      if (activeWork.sectionLabelSource === "num") {
        const visibleLabel = el.querySelector("tei-num")?.innerText?.trim();
        if (visibleLabel) label = visibleLabel;
      }

      sections.push({
        number: sectionNumber,
        label
      });
    });

    let optionList = sectionSelectMenu.options;
    optionList.length = 0;

    let options = sections.map(section => ({
      "text": section.label,
      "value": section.number.toLocaleString()
    }));

    options.unshift({
      "text": '',
      "value": ''
    });

    options.forEach(option =>
      optionList.add(
        new Option(option.text, option.value, option.selected)
      )
    );
  };

  const setNieseSelectOptions = () => {
    if (!nieseSelectMenu) return;

    const optionList = nieseSelectMenu.options;
    optionList.length = 0;

    if (!supportsNieseSections()) return;

    const entries = canonicalNieseStartEntries();
    const seen = new Set();

    optionList.add(new Option("", ""));

    entries.forEach(entry => {
      if (seen.has(entry.number)) return;
      seen.add(entry.number);

      optionList.add(
        new Option(
          entry.number.toLocaleString(),
          entry.number.toLocaleString()
        )
      );
    });
  };

  const resolvePendingUrlUnit = () => {
    if (!pendingUrlUnit || !usesChapterLocalUrlUnits()) return false;

    const wantedChapter = state.chapterNum === null
      ? null
      : String(parseInt(state.chapterNum, 10));

    const wantedUnit = String(parseInt(pendingUrlUnit, 10));

    const options = [...sectionSelectMenu.options].filter(
      option => option.value !== ""
    );

    // Canonical interpretation: chapter-local citation unit.
    let match = options.find(option => {
      const location = citationLocationFromLabel(option.text);

      return (
        location
        && location.chapterNum === wantedChapter
        && location.unitNum === wantedUnit
      );
    });

    // Compatibility with the global-num unit links created during
    // development before chapter-local DEH URLs were adopted.
    if (!match) {
      match = options.find(option => option.value === wantedUnit);
    }

    pendingUrlUnit = null;

    if (!match) {
      state.sectionNum = null;
      state.viewingLevel = state.chapterNum !== null
        ? "chapter-level"
        : "book-level";
      return false;
    }

    state.sectionNum = match.value;
    return true;
  };

  const reload = async () => {
    await fetchData();

    if (resolvePendingUrlUnit()) {
      await fetchData();
    }

    if (normalizeNavigationState()) {
      await fetchData();
    }

    renderUI();
    if (state.viewingLevel === "contents-level") {
      annotatedParagraphs = [];
      annotationsList.replaceChildren();
      if (annotationsPanel) annotationsPanel.hidden = true;
      const highlightWrapper = highlightCheckbox?.closest(".form-check");
      if (highlightWrapper) highlightWrapper.hidden = true;
    }
    else parseAnnotations();
  };

  const setState = async (callback) => {
    await callback();
    await reload();
    syncUrlFromState("push");
  };

  // Add event listeners.
  const addEventListeners = () => {
    bookSelectMenu.addEventListener("change", (event) => {
      bookLabel.innerText = (activeWork.preface && event.target.value === activeWork.preface.value)
        ? activeWork.preface.label
        : `Book ${parseInt(event.target.value)}`;

      setState(() => {
        const keepContents = state.viewingLevel === "contents-level";
        state.bookNum = event.target.value;
        if (keepContents) { clearContentsLocation(); return; }
        if (usesTraditionalStructure()) {
          state.subchapterNum = null;
          if (state.viewingLevel === "bamberg-level") selectAvailableBambergDivision();
          else { state.bambergId = null; state.viewingLevel = "book-level"; }
        }
        state.chapterNum = null;
        state.sectionNum = null;
        state.nieseNum = null;
      });
    });

    chapterSelectMenu.addEventListener("change", (event) => {
      if (event.target.value === "contents") {
        setState(() => { clearContentsLocation(); state.viewingLevel = "contents-level"; }); return;
      }
      chapterLabel.innerText = chapterDisplayLabel(event.target.value);

      setState(() => {
        if (state.viewingLevel === "contents-level") state.viewingLevel = "chapter-level";
        state.chapterNum = event.target.value;
        if (usesTraditionalStructure()) {
          state.bambergId = null;
          state.subchapterNum = null;
          state.viewingLevel = state.chapterNum ? (state.viewingLevel === "subchapter-level" ? "subchapter-level" : "chapter-level") : "book-level";
          if (state.viewingLevel === "subchapter-level") selectAvailableTraditionalSubchapter();
        }
        state.sectionNum = null;
        state.nieseNum = null;
      });
    });

    sectionSelectMenu.addEventListener("change", (event) => {
      sectionLabel.innerText = sectionDisplayLabel(event.target.value);
      setState(() => {
        state.sectionNum = event.target.value;
        if (usesTraditionalStructure()) { state.bambergId = null; state.viewingLevel = "section-level"; state.chapterNum = null; state.subchapterNum = null; }
        state.nieseNum = null;
      });
    });

    subchapterSelectMenu?.addEventListener("change", event => {
      if (!usesTraditionalStructure()) return;
      setState(() => {
        state.bambergId = null;
        state.subchapterNum = event.target.value || null;
        state.viewingLevel = state.subchapterNum ? "subchapter-level" : (isPreface() ? "book-level" : "chapter-level");
        state.sectionNum = null; state.nieseNum = null;
      });
    });
    if (nieseSelectMenu) {
      nieseSelectMenu.addEventListener("change", (event) => {
        setState(() => {
          state.nieseNum = event.target.value || null;
          if (usesTraditionalStructure()) { state.bambergId = null; state.subchapterNum = null; state.viewingLevel = "niese-level"; }
          state.chapterNum = null;
          state.sectionNum = null;
        });
      });
    }

    const selectBamberg = identity => setState(() => {
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
    const advanceNiese = direction => {
      const entries = canonicalNieseStartEntries(), index = entries.findIndex(entry => entry.number === Number(state.nieseNum));
      const next = entries[index + direction];
      if (index >= 0 && next) setState(() => {
        state.nieseNum = String(next.number); state.viewingLevel = "niese-level";
        state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null; state.bambergId = null;
      });
    };
    niesePrevious?.addEventListener("click", () => advanceNiese(-1));
    nieseNext?.addEventListener("click", () => advanceNiese(1));
    viewingLevelSelectMenu.addEventListener("change", (event) => {
      setState(() => {
        const nextLevel = event.target.value;
        if (usesTraditionalStructure()) {
          state.viewingLevel = nextLevel;
          if (nextLevel === "bamberg-level") {
            state.chapterNum = null; state.subchapterNum = null; state.sectionNum = null; state.nieseNum = null;
            if (!bambergSelection()) selectAvailableBambergDivision();
            return;
          }
          state.bambergId = null;
          if (["chapter-level", "subchapter-level"].includes(nextLevel)) {
            state.sectionNum = null; state.nieseNum = null;
            if (!isPreface() && !state.chapterNum) state.chapterNum = traditionalRows("chapter")[0]?.chapter || null;
            state.subchapterNum = null;
            if (nextLevel === "subchapter-level") selectAvailableTraditionalSubchapter();
            if (isPreface() && nextLevel === "chapter-level") state.viewingLevel = "book-level";
          } else {
            state.chapterNum = null; state.subchapterNum = null;
            if (nextLevel !== "section-level") state.sectionNum = null;
            else if (!state.sectionNum) state.sectionNum = [...sectionSelectMenu.options].find(option => option.value)?.value || null;
            if (nextLevel !== "niese-level") state.nieseNum = null;
            else if (!state.nieseNum) state.nieseNum = String(canonicalNieseStartEntries()[0]?.number || "") || null;
          }
          return;
        }
        state.viewingLevel = nextLevel;

        if (nextLevel === "niese-level") {
          state.chapterNum = null;
          state.sectionNum = null;
        } else {
          state.nieseNum = null;
        }
      });
    });

    Object.entries(languagePaneCheckboxes).forEach(([language, checkbox]) => {
      const pane = languagePanes[language];

      if (
        !activeWork.languages[language]
        || !checkbox
        || !pane
        || checkbox.disabled
      ) return;

      checkbox.addEventListener("change", () => {
        pane.classList.toggle("hidden", !checkbox.checked);
      });
    });

    Object.entries(sourceSelectMenus).forEach(([language, menu]) => {
      if (!activeWork.languages[language] || !menu) return;

      menu.addEventListener("change", (event) => {
        const sourceKey = event.target.value;

        if (!sourceAvailableForBook(language, sourceKey)) return;

        setState(() => {
          state.sources[language] = sourceKey;
        });
      });
    });

    lodgeNotesCheckbox?.addEventListener("change", () => {
      if (activeWork.slug !== "bellum" || state.sources.English !== "lodge1602") return;
      state.lodgeNotesVisible = lodgeNotesCheckbox.checked;
      updateLodgeNotesUI();
      syncUrlFromState("push");
    });

    highlightCheckbox.addEventListener("change", () => {
      annotatedParagraphs.forEach(paragraphId => {
        const target = displayedLatinTarget(paragraphId);
        if (target) target.classList.toggle("highlight");
      });
    });
  };

  bookTitle.innerText = activeWork.title;

  const initialLocationRequested = applyNavigationFromUrl();

  updateLanguageUI();
  setBookSelectOptions();
  addEventListeners();

  window.addEventListener("popstate", async () => {
    const locationRequested = applyNavigationFromUrl();
    setBookSelectOptions();
    await reload();

    if (locationRequested) {
      syncUrlFromState("replace");
    }
  });

  reload().then(() => {
    if (initialLocationRequested) {
      syncUrlFromState("replace");
    }
  });
});

// var timer;
//
// $(window).scroll(function() {
//   if(timer) {
//     window.clearTimeout(timer);
//   }
//
//   timer = window.setTimeout(function() {
//     // actual callback
//     console.log( "Firing!" );
//   }, 100);
// });
