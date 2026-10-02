/* DEH I.1 and V.53.1 scholarly parallels. Canonical texts remain read-only. */
document.addEventListener("DOMContentLoaded", () => {
  const panel = document.getElementById("deh-parallels");
  if (!panel) return;

  const reader = document.getElementById("pane-container");
  const settings = document.getElementById("display-settings");
  const unitMenu = document.getElementById("parallel-unit");
  const dehMenu = document.getElementById("parallel-deh-source");
  const bjMenu = document.getElementById("parallel-bj-source");
  const status = document.getElementById("parallel-status");
  const dehText = document.getElementById("parallel-deh-text");
  const bjText = document.getElementById("parallel-bj-text");
  const sources = {
    pollard: { work: "deh", language: "English", lang: "en", identity: "Pollard v1.0 — English translation of the Latin DEH." },
    ussani: { work: "deh", language: "Latin", lang: "la", identity: "Ussani (1932) — Latin DEH." },
    niese: { work: "bellum", language: "Greek", lang: "grc", identity: "Niese — Greek Bellum." },
    whiston: { work: "bellum", language: "English", lang: "en", identity: "Whiston — English translation of the Greek Bellum." },
    cardwell: { work: "bellum", language: "Latin", lang: "la", identity: "Cardwell (1837) — Latin translation of the Bellum." }
  };
  const romanBooks = ["", "I", "II", "III", "IV", "V", "VI", "VII"];
  const bellumCitation = ref => `${romanBooks[ref.book]}.${ref.section_start}${
    ref.section_end !== ref.section_start ? `–${ref.section_end}` : ""
  }`;
  const correspondenceComponents = record => record.josephus.segments.flatMap(segment => {
    // The pilot supports the inherited suffix reference in V.53.1. Keep the
    // original nested record intact; do not assign the parentheses a meaning.
    const components = [{ ref: segment.unparenthesized_reference, literal: segment.literal }];
    segment.parentheses.forEach(parenthesis => {
      if (parenthesis.placement !== "suffix" || parenthesis.kind !== "parenthetical_reference") {
        throw new Error("This notation requires editorial review before excerpt display.");
      }
      components.push({ ref: parenthesis.reference, literal: parenthesis.literal, parenthesis });
    });
    return components;
  });
  const componentCitation = component => {
    const citation = `BJ ${bellumCitation(component.ref)}`;
    return component.parenthesis ? `(${citation})` : citation;
  };
  const correspondenceLabel = record => correspondenceComponents(record)
    .map(componentCitation).join(", ");
  const tei = new CETEI();
  const textCache = new Map();
  let records = [];
  let navigation;
  let generation = 0;

  const readingUrl = (record) => {
    const url = new URL(window.location.href);
    ["num", "niese", "parallel", "deh-source", "bj-source"].forEach(key => url.searchParams.delete(key));
    url.searchParams.set("book", record.deh.book);
    url.searchParams.set("chapter", record.deh.chapter);
    url.searchParams.set("unit", record.deh.unit);
    url.hash = "";
    return url;
  };

  const comparisonUrl = (record, dehSource = "pollard", bjSource = "whiston") => {
    const url = readingUrl(record);
    url.searchParams.set("parallel", record.id);
    url.searchParams.set("deh-source", dehSource);
    url.searchParams.set("bj-source", bjSource);
    return url;
  };

  const loadText = (sourceKey, book) => {
    const key = `${sourceKey}:${book}`;
    if (!textCache.has(key)) {
      const source = sources[sourceKey];
      const filename = `book-${String(book).padStart(2, "0")}.xml`;
      const url = new URL(`${source.work}/${source.language}/${filename}`, new URL(panel.dataset.xmlBase, window.location.href));
      const promise = fetch(url).then(async response => {
        if (!response.ok) throw new Error(`Could not load ${sourceKey}.`);
        const xml = new DOMParser().parseFromString(await response.text(), "text/xml");
        if (xml.querySelector("parsererror")) throw new Error(`Invalid XML for ${sourceKey}.`);
        return tei.domToHTML5(xml);
      }).catch(error => {
        textCache.delete(key);
        throw error;
      });
      textCache.set(key, promise);
    }
    return textCache.get(key);
  };

  // Cardwell has confirmed paragraph-start [N] apparatus and internal Niese
  // milestones. Whiston uses its own milestones. Never infer Niese sections
  // from Whiston's sameAs links to Cardwell paragraph IDs.
  const bellumEntries = (data, sourceKey, book) => {
    if (sourceKey === "niese") {
      const prefix = `greek-bellum${book}-num`;
      return [...data.querySelectorAll("tei-p")]
        .filter(node => node.id.startsWith(prefix) && /^[1-9]\d*$/.test(node.id.slice(prefix.length)))
        .map(node => ({ number: Number(node.id.slice(prefix.length)), node, wholeSection: true }));
    }
    const entries = [...data.querySelectorAll('tei-milestone[unit="niese"][n]')]
      .filter(node => /^[1-9]\d*$/.test(node.getAttribute("n")))
      .map(node => ({ number: Number(node.getAttribute("n")), node, paragraph: false }));
    if (sourceKey === "cardwell") {
      const prefix = `latin-bellum${book}-num`;
      data.querySelectorAll("tei-p").forEach(node => {
        if (!node.id.startsWith(prefix)) return;
        const number = node.id.slice(prefix.length);
        if (/^[1-9]\d*$/.test(number) && new RegExp(`^\\s*\\[\\s*${number}\\s*\\]`).test(node.textContent)) {
          entries.push({ number: Number(number), node, paragraph: true });
        }
      });
    }
    return entries.sort((a, b) => a.node === b.node ? 0 : (
      a.node.compareDocumentPosition(b.node) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
    ));
  };

  const bellumSection = (entries, number) => {
    const index = entries.findIndex(entry => entry.number === number);
    const start = entries[index];
    const end = entries[index + 1];
    // Every pilot section has a checked following boundary. Fail visibly
    // rather than silently extending an excerpt over missing sections.
    if (!start || !end || end.number !== number + 1) {
      throw new Error(`BJ section ${number} lacks a complete source boundary.`);
    }
    const wrapper = document.createElement("tei-div2");
    wrapper.dataset.nieseSection = number;
    if (start.wholeSection) {
      // The canonical Greek paragraph is already one complete Niese section.
      const paragraph = start.node.cloneNode(true);
      const label = document.createElement("tei-num");
      label.className = "niese-generated";
      label.textContent = `[${number}] `;
      paragraph.prepend(label);
      wrapper.appendChild(paragraph);
      return wrapper;
    }
    const startParagraph = start.paragraph ? start.node : start.node.closest("tei-p");
    const endParagraph = end.paragraph ? end.node : end.node.closest("tei-p");
    const range = document.createRange();
    if (start.paragraph) range.setStartBefore(start.node);
    else range.setStartAfter(start.node);
    range.setEndBefore(end.node);

    if (startParagraph && startParagraph === endParagraph) {
      if (start.paragraph) range.setStart(startParagraph, 0);
      const paragraph = startParagraph.cloneNode(false);
      paragraph.appendChild(range.cloneContents());
      wrapper.appendChild(paragraph);
    } else {
      wrapper.appendChild(range.cloneContents());
    }
    wrapper.querySelectorAll("tei-p").forEach(paragraph => {
      if (!paragraph.textContent.trim() && !paragraph.querySelector("tei-milestone, tei-num")) paragraph.remove();
    });
    if (!start.paragraph) {
      const label = document.createElement("tei-num");
      label.className = "niese-generated";
      label.textContent = `[${number}] `;
      wrapper.querySelector("tei-p")?.prepend(label);
    }
    if (!wrapper.textContent.trim()) throw new Error(`BJ section ${number} is empty.`);
    return wrapper;
  };

  const namespaceIds = (fragment, prefix) => {
    const elements = [fragment, ...fragment.querySelectorAll("*")];
    const ids = new Map();
    elements.forEach(element => {
      if (element.id) {
        ids.set(element.id, `${prefix}-${element.id}`);
        element.id = ids.get(element.id);
      }
    });
    elements.forEach(element => {
      const href = element.getAttribute("href");
      if (href?.startsWith("#") && ids.has(href.slice(1))) element.setAttribute("href", `#${ids.get(href.slice(1))}`);
    });
    return fragment;
  };

  const renderComparison = async (record) => {
    const currentGeneration = ++generation;
    const dehSource = dehMenu.value;
    const bjSource = bjMenu.value;
    dehText.replaceChildren();
    bjText.replaceChildren();
    dehText.lang = sources[dehSource].lang;
    bjText.lang = sources[bjSource].lang;
    status.textContent = "Loading parallel passages…";
    document.getElementById("parallel-deh-title").textContent = `DEH ${record.deh.citation}`;
    document.getElementById("parallel-deh-identity").textContent = sources[dehSource].identity;
    document.getElementById("parallel-bj-identity").textContent = sources[bjSource].identity;
    document.getElementById("parallel-close").href = readingUrl(record);
    document.getElementById("parallel-share").href = comparisonUrl(record, dehSource, bjSource);
    try {
      const dehData = await loadText(dehSource, record.deh.book);
      const paragraphs = [...dehData.querySelectorAll("tei-p")].filter(paragraph => (
        dehSource === "ussani"
          ? paragraph.id === record.deh.xml_id
          : (paragraph.getAttribute("sameAs") || "").split(/\s+/).some(target => target.split("#").pop() === record.deh.xml_id)
      ));
      if (!paragraphs.length) throw new Error(`DEH ${record.deh.citation} is unavailable in this source.`);
      const dehFragment = document.createElement("div");
      paragraphs.forEach(paragraph => dehFragment.appendChild(paragraph.cloneNode(true)));
      if (dehSource === "ussani") dehFragment.querySelectorAll("tei-unclear:empty").forEach(marker => { marker.textContent = "†"; });

      const components = document.createElement("ol");
      components.className = "parallel-components";
      // Iterate the supplied array directly: preserve order and repeated or
      // overlapping sections in separate components, without sorting/merging.
      for (const [componentIndex, supplied] of correspondenceComponents(record).entries()) {
        const ref = supplied.ref;
        if (!ref || ref.work !== "BJ" || ref.open_ended) {
          throw new Error("This notation requires editorial review before excerpt display.");
        }
        const data = await loadText(bjSource, ref.book);
        const entries = bellumEntries(data, bjSource, ref.book);
        const component = document.createElement("li");
        component.dataset.reference = supplied.literal;
        component.dataset.book = ref.book;
        const heading = document.createElement("h4");
        heading.textContent = componentCitation(supplied);
        component.appendChild(heading);
        if (supplied.parenthesis) {
          component.dataset.parenthetical = "true";
          component.dataset.editorialMeaning = supplied.parenthesis.editorial_meaning;
          const note = document.createElement("p");
          note.className = "parallel-editorial-note";
          note.textContent = "Inherited parentheses; editorial meaning unresolved.";
          component.appendChild(note);
        }
        for (let section = ref.section_start; section <= ref.section_end; section += 1) {
          const excerpt = bellumSection(entries, section);
          component.appendChild(namespaceIds(excerpt, `parallel-bj-${componentIndex}-${section}`));
        }
        const link = document.createElement("a");
        const url = new URL(panel.dataset.bellumUrl, window.location.href);
        url.searchParams.set("book", ref.book);
        url.searchParams.set("niese", ref.section_start);
        link.href = url;
        link.textContent = `Open BJ ${romanBooks[ref.book]}.${ref.section_start} in the Bellum reader`;
        component.appendChild(link);
        components.appendChild(component);
      }
      if (generation !== currentGeneration) return;
      dehText.appendChild(namespaceIds(dehFragment, "parallel-deh"));
      bjText.appendChild(components);
      status.textContent = "";
    } catch (error) {
      if (generation !== currentGeneration) return;
      status.textContent = `Comparison unavailable: ${error.message} Use “Return to DEH reading” to continue.`;
    }
  };

  const refresh = () => {
    document.querySelectorAll(".deh-parallel-link").forEach(link => link.remove());
    records.forEach(record => {
      document.querySelectorAll("#latin tei-p, #english tei-p").forEach(paragraph => {
        const targets = (paragraph.getAttribute("sameAs") || "").split(/\s+/).map(target => target.split("#").pop());
        if (paragraph.id !== record.deh.xml_id && !targets.includes(record.deh.xml_id)) return;
        const link = document.createElement("a");
        link.className = "deh-parallel-link";
        link.href = comparisonUrl(record);
        link.textContent = `Compare DEH ${record.deh.citation} with ${correspondenceLabel(record)}`;
        paragraph.after(link);
      });
    });
    const params = new URLSearchParams(window.location.search);
    const record = records.find(record => record.id === params.get("parallel"));
    // The relation must match the renderer's resolved canonical passage.
    const matches = record && navigation?.book === record.deh.book
      && Number(navigation.chapter) === record.deh.chapter
      && Number(navigation.num) === Number(record.deh.xml_id.match(/num(\d+)$/)?.[1])
      && navigation.level === "section-level";
    panel.hidden = !matches;
    reader.hidden = Boolean(matches);
    settings.hidden = Boolean(matches);
    if (!matches) {
      generation += 1;
      return;
    }
    unitMenu.value = record.id;
    dehMenu.value = ["pollard", "ussani"].includes(params.get("deh-source")) ? params.get("deh-source") : "pollard";
    bjMenu.value = ["whiston", "cardwell", "niese"].includes(params.get("bj-source")) ? params.get("bj-source") : "whiston";
    renderComparison(record);
  };

  document.addEventListener("deh-view-rendered", event => {
    navigation = event.detail;
    refresh();
  });
  unitMenu.addEventListener("change", () => {
    const record = records.find(record => record.id === unitMenu.value);
    if (record) window.location.assign(comparisonUrl(record, dehMenu.value, bjMenu.value));
  });
  [dehMenu, bjMenu].forEach(menu => menu.addEventListener("change", () => {
    const record = records.find(record => record.id === unitMenu.value);
    if (!record) return;
    window.history.pushState({}, "", comparisonUrl(record, dehMenu.value, bjMenu.value));
    renderComparison(record);
  }));

  fetch(panel.dataset.alignmentUrl).then(async response => {
    if (!response.ok) throw new Error("Alignment data unavailable.");
    const data = await response.json();
    // Hard scope guard: no other concordance records become interface entries.
    records = data.records.filter(record => (
      (record.deh.book === 1 && record.deh.chapter === 1 && record.deh.unit >= 1 && record.deh.unit <= 10)
      || (record.id === "deh-5-53-1" && record.deh.book === 5 && record.deh.chapter === 53 && record.deh.unit === 1)
    ));
    records.forEach(record => unitMenu.add(new Option(`DEH ${record.deh.citation} → ${correspondenceLabel(record)}`, record.id)));
    refresh();
  }).catch(error => {
    if (new URLSearchParams(window.location.search).has("parallel")) {
      panel.hidden = false;
      status.textContent = `Comparison unavailable: ${error.message}`;
      document.getElementById("parallel-close").href = window.location.pathname;
    }
  });
});
