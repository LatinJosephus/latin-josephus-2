/* Isolated extension of reviewed DEH correspondences to both Josephus works. */
import {
  sources, romanBooks, bjTargets, componentCitation, publicationRecords,
  loadConcordance, createTextLoader, dehParagraphs, bellumIndex, bellumSection, namespaceIds
} from "./dehParallelsCore.js?v=20261025-pollard-v1.1";

import {ajSources, ajTargets, loadAjLayer, createAjTextLoader, ajSection} from "./dehAntiquitiesCore.js?v=20261014-aj-v1";
const initialize = () => {
  const panel = document.getElementById("deh-parallels");
  if (!panel) return;
  const reader = document.getElementById("pane-container");
  const settings = document.getElementById("display-settings");
  const bookMenu = document.getElementById("parallel-book");
  const chapterMenu = document.getElementById("parallel-chapter");
  const unitMenu = document.getElementById("parallel-unit");
  const dehMenu = document.getElementById("parallel-deh-source");
  const workMenu = document.getElementById("parallel-work");
  const allSources = {...sources,...ajSources};
  let concordance, ajPromise;
  const getAj = () => ajPromise ||= loadAjLayer(panel.dataset.ajAlignmentUrl,panel.dataset.ajAlignmentSha,concordance).then(layer => ({layer,load:createAjTextLoader(new URL(panel.dataset.xmlBase,window.location.href),layer)})).catch(e => {ajPromise=null;throw e;});
  const bjMenu = document.getElementById("parallel-bj-source");
  const status = document.getElementById("parallel-status");
  const dehText = document.getElementById("parallel-deh-text");
  const bjText = document.getElementById("parallel-bj-text");
  const indexes = new WeakMap();
  let records = [], byId = new Map(), byCanonicalId = new Map();
  let navigation, loadText;
  let generation = 0;

  const readingUrl = record => {
    const url = new URL(window.location.href);
    ["num", "niese", "parallel", "deh-source", "bj-source", "parallel-work", "aj-source"].forEach(key => url.searchParams.delete(key));
    url.searchParams.set("book", record.deh.book);
    url.searchParams.set("chapter", record.deh.chapter);
    url.searchParams.set("unit", record.deh.unit);
    url.hash = "";
    return url;
  };
  const comparisonUrl = (record, dehSource = "pollard", bjSource = "whiston", work = bjTargets(record).length ? "BJ" : "AJ") => {
    const url = readingUrl(record);
    url.searchParams.set("parallel", record.id);
    url.searchParams.set("deh-source", dehSource);
    if (work === "AJ") {url.searchParams.set("parallel-work","AJ");url.searchParams.set("aj-source",ajSources[bjSource] ? bjSource : "aj_whiston");}
    else url.searchParams.set("bj-source", sources[bjSource]?.work === "bellum" ? bjSource : "whiston");
    return url;
  };
  const fillMenu = (menu, options, selected) => {
    menu.replaceChildren(...options.map(([label, value]) => new Option(label, String(value))));
    menu.value = String(selected);
  };
  const selectRecord = record => {
    fillMenu(bookMenu, [...new Set(records.map(entry => entry.deh.book))]
      .map(book => [`Book ${romanBooks[book]}`, book]), record.deh.book);
    fillMenu(chapterMenu, [...new Set(records.filter(entry => entry.deh.book === record.deh.book)
      .map(entry => entry.deh.chapter))].map(chapter => [`Chapter ${chapter}`, chapter]), record.deh.chapter);
    fillMenu(unitMenu, records.filter(entry => entry.deh.book === record.deh.book && entry.deh.chapter === record.deh.chapter)
      .map(entry => [`DEH ${entry.deh.citation}`, entry.id]), record.id);
  };
  const renderComparison = async record => {
    const currentGeneration = ++generation;
    const dehSource = dehMenu.value, bjSource = bjMenu.value, work = workMenu.value;
    dehText.replaceChildren();
    bjText.replaceChildren();
    dehText.lang = sources[dehSource].lang;
    bjText.lang = allSources[bjSource].lang;
    status.textContent = "Loading parallel passages…";
    document.getElementById("parallel-deh-title").textContent = `DEH ${record.deh.citation}`;
    document.getElementById("parallel-deh-identity").textContent = sources[dehSource].identity;
    document.getElementById("parallel-bj-identity").textContent = allSources[bjSource].identity;
    document.getElementById("parallel-close").href = readingUrl(record);
    document.getElementById("parallel-share").href = comparisonUrl(record, dehSource, bjSource, work);
    try {
      // Verify the selected canonical target before showing either source.
      const canonical = await loadText("ussani", record.deh.book);
      if (dehParagraphs(canonical, record, "ussani").length !== 1) throw new Error(`Canonical DEH ${record.deh.citation} is unavailable.`);
      const paragraphs = dehParagraphs(await loadText(dehSource, record.deh.book), record, dehSource);
      if (!paragraphs.length) throw new Error(`DEH ${record.deh.citation} is unavailable in this source.`);
      const fragment = document.createElement("div");
      paragraphs.forEach(paragraph => fragment.appendChild(paragraph.cloneNode(true)));
      if (dehSource === "ussani") fragment.querySelectorAll("tei-unclear:empty").forEach(marker => { marker.textContent = "†"; });
      const components = document.createElement("ol");
      components.className = "parallel-components";
      if (work === "AJ") {
        const aj = await getAj();
        const entry = aj.layer.records.find(r => r.id === record.id);
        if (!entry) throw new Error("No AJ correspondence recorded for this unit.");
        const romans = ["","I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX"];
        for (const [i,c] of entry.components.entries()) {
          const ref=c.frozen_target, item=document.createElement("li");item.dataset.order=ref.order;item.dataset.book=ref.book;item.dataset.componentId=c.component_id;
          const heading=document.createElement("h4");heading.textContent=`AJ ${romans[ref.book]}.${ref.section_start}${ref.section_end!==ref.section_start?`–${ref.section_end}`:""}`;item.append(heading);
          if (c.display_note) {const note=document.createElement("p");note.className="parallel-editorial-note";note.textContent=c.display_note;item.append(note);}
          for (const a of c.annotations) {const note=document.createElement("p");note.className="parallel-editorial-note";note.textContent=`${a.raw_token} — ${a.interpretation} (${a.editorial_decision})`;item.append(note);}
          const data=await aj.load(bjSource,ref.book);
          for (const section of c.sections[ajSources[bjSource].language]) item.append(namespaceIds(ajSection(data,section),`parallel-aj-${i}-${section.number}`));
          const link=document.createElement("a"),url=new URL(panel.dataset.antiquitiesUrl,window.location.href);
          url.searchParams.set("book",ref.book);url.searchParams.set("niese",ref.section_start);url.searchParams.set(ajSources[bjSource].language.toLowerCase(),ajSources[bjSource].readerKey);
          link.href=url;link.textContent=`Open AJ ${romans[ref.book]}.${ref.section_start} in the Antiquities reader`;item.append(link);components.append(item);
        }
      }
      // Filter BJ without sorting, merging or deduplicating authoritative targets.
      for (const [componentIndex, ref] of (work === "BJ" ? bjTargets(record) : []).entries()) {
        const data = await loadText(bjSource, ref.book);
        if (!indexes.has(data)) indexes.set(data, bellumIndex(data, bjSource, ref.book));
        const component = document.createElement("li");
        component.dataset.order = ref.order;
        component.dataset.book = ref.book;
        component.dataset.relationshipRole = ref.relationship_role;
        const heading = document.createElement("h4");
        heading.textContent = componentCitation(ref);
        component.appendChild(heading);
        if (ref.relationship_role === "supplementary_parallel") {
          const note = document.createElement("p");
          note.className = "parallel-editorial-note";
          note.textContent = "Supplementary parallel";
          component.appendChild(note);
        }
        for (let section = ref.section_start; section <= ref.section_end; section += 1) {
          component.appendChild(namespaceIds(bellumSection(indexes.get(data), section), `parallel-bj-${componentIndex}-${section}`));
        }
        const link = document.createElement("a");
        const url = new URL(panel.dataset.bellumUrl, window.location.href);
        url.searchParams.set("book", ref.book);
        url.searchParams.set("niese", ref.section_start);
        // The ordinary Bellum reader retains its existing Greek source key.
        url.searchParams.set(allSources[bjSource].language.toLowerCase(), bjSource === "niese" ? "current" : bjSource);
        link.href = url;
        link.textContent = `Open BJ ${romanBooks[ref.book]}.${ref.section_start} in the Bellum reader`;
        component.appendChild(link);
        components.appendChild(component);
      }
      if (generation !== currentGeneration) return;
      dehText.appendChild(namespaceIds(fragment, "parallel-deh"));
      bjText.appendChild(components);
      status.textContent = "";
    } catch (error) {
      if (generation !== currentGeneration) return;
      status.textContent = `Comparison unavailable: ${error.message} Use “Return to DEH reading” to continue.`;
    }
  };
  const refresh = () => {
    document.querySelectorAll(".deh-parallel-link").forEach(link => link.remove());
    // One reader traversal instead of one scan for every concordance record.
    const canonicalIds = new Set([...document.querySelectorAll("#latin tei-p[id]")].map(paragraph => paragraph.id));
    document.querySelectorAll("#latin tei-p, #english tei-p").forEach(paragraph => {
      const targets = [paragraph.id, ...(paragraph.getAttribute("sameAs") || "").split(/\s+/).map(target => target.split("#").pop())];
      const record = targets.map(target => byCanonicalId.get(target)).find(Boolean);
      if (!record || !canonicalIds.has(record.deh.xml_id)) return;
      const link = document.createElement("a");
      link.className = "deh-parallel-link";
      link.href = comparisonUrl(record, paragraph.closest("#latin") ? "ussani" : "pollard");
      link.textContent = ajTargets(record).length ? (bjTargets(record).length ? "Compare with Josephus" : "Compare with Antiquities") : "Compare with Bellum";
      link.setAttribute("aria-label", `Compare DEH ${record.deh.citation} with ${ajTargets(record).length ? "Josephus" : "Bellum"}`);
      paragraph.after(link);
    });
    const params = new URLSearchParams(window.location.search);
    const record = byId.get(params.get("parallel"));
    const matches = record && canonicalIds.has(record.deh.xml_id) && navigation?.book === record.deh.book
      && Number(navigation.chapter) === record.deh.chapter
      && Number(navigation.num) === Number(record.deh.xml_id.match(/num(\d+)$/)?.[1])
      && navigation.level === "section-level";
    panel.hidden = !matches;
    reader.hidden = Boolean(matches);
    settings.hidden = Boolean(matches);
    if (!matches) {
      generation += 1;
      dehText.replaceChildren();
      bjText.replaceChildren();
      status.textContent = "";
      return;
    }
    selectRecord(record);
    dehMenu.value = ["pollard", "ussani"].includes(params.get("deh-source")) ? params.get("deh-source") : "pollard";
    const works=[...(bjTargets(record).length?["BJ"]:[]),...(ajTargets(record).length?["AJ"]:[])];
    fillMenu(workMenu,works.map(w=>[w==="BJ"?"Bellum Judaicum":"Antiquitates Judaicae",w]),works.includes(params.get("parallel-work"))?params.get("parallel-work"):works[0]);
    configureWitness(params);
    renderComparison(record);
  };
  const configureWitness = params => {
    const aj=workMenu.value==="AJ";
    document.getElementById("parallel-bj-title").textContent=aj?"Antiquitates Judaicae":"Bellum Judaicum";
    document.getElementById("parallel-josephus-source-label").textContent=aj?"Antiquities language / source:":"Bellum language / source:";
    const options=aj?[["Greek — Niese","aj_niese"],["Latin — Antiquities (Bamberg 78)","aj_latin"],["English — Whiston","aj_whiston"]]:[["Greek — Niese","niese"],["Latin — Cardwell (1837)","cardwell"],["English — Whiston","whiston"]];
    const value=params?.get(aj?"aj-source":"bj-source");fillMenu(bjMenu,options,options.some(o=>o[1]===value)?value:aj?"aj_whiston":"whiston");
  };
  document.addEventListener("deh-view-rendered", event => { navigation = event.detail; refresh(); });
  const navigate = record => {
    if (record) window.location.assign(comparisonUrl(record, dehMenu.value, bjMenu.value, (workMenu.value === "AJ" && ajTargets(record).length) ? "AJ" : bjTargets(record).length ? "BJ" : "AJ"));
  };
  bookMenu.addEventListener("change", () => navigate(records.find(record => record.deh.book === Number(bookMenu.value))));
  chapterMenu.addEventListener("change", () => navigate(records.find(record => record.deh.book === Number(bookMenu.value)
    && record.deh.chapter === Number(chapterMenu.value))));
  unitMenu.addEventListener("change", () => navigate(byId.get(unitMenu.value)));
  workMenu.addEventListener("change", () => {configureWitness();const record=byId.get(unitMenu.value);window.history.pushState({},"",comparisonUrl(record,dehMenu.value,bjMenu.value,workMenu.value));renderComparison(record);});
  [dehMenu, bjMenu].forEach(menu => menu.addEventListener("change", () => {
    const record = byId.get(unitMenu.value);
    if (!record) return;
    window.history.pushState({}, "", comparisonUrl(record, dehMenu.value, bjMenu.value, (workMenu.value === "AJ" && ajTargets(record).length) ? "AJ" : bjTargets(record).length ? "BJ" : "AJ"));
    renderComparison(record);
  }));
  loadConcordance(panel.dataset.alignmentUrl).then(data => {
    publicationRecords(data);
    concordance=data;
    records = data.records.filter(r=>bjTargets(r).length || ajTargets(r).length);
    byId = new Map(records.map(record => [record.id, record]));
    byCanonicalId = new Map(records.map(record => [record.deh.xml_id, record]));
    loadText = createTextLoader(new URL(panel.dataset.xmlBase, window.location.href), data.canonical_xml_sha256);
    panel.dataset.reviewedRecords = data.records.length;
    panel.dataset.eligibleRecords = records.length;
    refresh();
  }).catch(error => {
    if (new URLSearchParams(window.location.search).has("parallel")) {
      panel.hidden = false;
      status.textContent = `Comparison unavailable: ${error.message}`;
      const url = new URL(window.location.href);
      ["parallel", "deh-source", "bj-source", "parallel-work", "aj-source"].forEach(key => url.searchParams.delete(key));
      document.getElementById("parallel-close").href = url;
    }
  });
};
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
else initialize();
