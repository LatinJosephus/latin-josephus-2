/* Exercises the actual built reader through its existing native controls. */
(() => {
  const assert = (condition, label) => { if (!condition) throw Error(label); };
  const pane = () => document.querySelector("#english");
  const normalize = text => text.replace(/\s+/g, " ").trim();
  const sourceText = node => {
    if (node.nodeType === Node.TEXT_NODE) return node.data;
    if (node.nodeType !== Node.ELEMENT_NODE && node.nodeType !== Node.DOCUMENT_FRAGMENT_NODE) return "";
    if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.matches('[data-original], tei-milestone, tei-pb, tei-num.niese-generated')) return "";
      if (node.matches("tei-note")) {
        const original = node.querySelector("[data-original]");
        if (original) return original.textContent;
      }
    }
    return [...node.childNodes].map(sourceText).join("");
  };
  const translated = () => [...pane().children].filter(n => n.tagName !== "H3").map(sourceText).join("");
  const ready = async (predicate, label = "") => {
    const limit = performance.now() + 60000;
    while (!predicate()) {
      assert(performance.now() < limit, "Reader did not finish rendering "+label+": "+location.href);
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    // URL synchronization follows rendering in the existing async handler.
    await new Promise(resolve => setTimeout(resolve, 0));
  };
  const change = async (selector, value) => {
    const element = document.querySelector(selector);
    assert(element, "Missing existing control "+selector);
    let rendered = false;
    const observer = new MutationObserver(() => { rendered = true; observer.disconnect(); });
    observer.observe(pane(), { childList:true });
    if (element.type === "radio") element.checked = true;
    else {
      const exact = [...element.options].find(o => o.value === String(value));
      const numeric = value !== "" && [...element.options].find(o => o.value !== "" && Number(o.value) === Number(value));
      const option = exact || numeric;
      assert(option, "Unavailable control value "+selector+"="+value);
      element.value = option.value;
    }
    element.dispatchEvent(new Event("change", { bubbles:true }));
    await ready(() => rendered, selector+"="+value);
  };
  const level = name => change("#"+name+"-level");
  const parse = text => {
    const d = new DOMParser().parseFromString(text, "application/xml");
    assert(!d.querySelector("parsererror"), "QA source XML parse error"); return d;
  };
  const nodes = (d, tag) => [...d.getElementsByTagNameNS("http://www.tei-c.org/ns/1.0",tag)];
  const id = n => n.getAttributeNS("http://www.w3.org/XML/1998/namespace","id");
  const digest = async text => [...new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text)))]
    .map(n=>n.toString(16).padStart(2,"0")).join("");
  const rawExcerpt = (d, starts, index) => {
    const range = d.createRange(); range.setStartAfter(starts[index]);
    if (starts[index+1]) range.setEndBefore(starts[index+1]);
    else { const book=nodes(d,"div1")[0]; range.setEnd(book,book.childNodes.length); }
    return range.cloneContents().textContent;
  };
  window.lodgeReaderQA = async source => {
    const isLodge = source === "lodge1602";
    const sourceSelector = document.querySelector("#english-source-selector");
    if (isLodge) {
      assert(sourceSelector.value==="whiston", "Fresh Bellum must default to Whiston");
      assert([...sourceSelector.options].some(o=>o.value==="lodge1602"&&o.text==="Lodge (1602)"),"Independent Lodge source option");
    }
    if (sourceSelector.value !== source) await change("#english-source-selector",source);
    const counts={books:0,chapters:0,coarse:0,niese:0}, content=[], fixtures=[];
    for (let b=1;b<=7;b++) {
      const path="/assets/xml/bellum/English/"+(isLodge?"Lodge1602/":"")+"book-"+String(b).padStart(2,"0")+".xml";
      const response=await fetch(path); assert(response.ok,"QA XML load "+path);
      const d=parse(await response.text());
      const body=nodes(d,"body")[0], chapters=nodes(body,"div2"), paragraphs=nodes(body,"p");
      const starts=nodes(body,"milestone").filter(n=>n.getAttribute("unit")==="niese");
      await change("#book-selector",String(b)); await level("book");
      assert(pane().querySelector('tei-div1[n="'+b+'"]'),"Correct book "+b);
      const record = (key, expected) => {
        const actual=normalize(translated());
        if (isLodge && expected!==undefined) {
          const wanted=normalize(expected);
          assert(actual===wanted,"Exact displayed source words mismatch "+key+
            "\nactual: "+actual.slice(0,220)+"\nexpected: "+wanted.slice(0,220));
        }
        content.push(key+"\n"+actual+"\n"+[...pane().querySelectorAll("tei-p[id]")].map(n=>n.id).join(","));
        return actual;
      };
      record("book:"+b,body.textContent); counts.books++;
      if (isLodge && b===1) {
        const note=[...pane().querySelectorAll('tei-note[place="margin"]')].find(n=>!n.closest("[data-original]"));
        const head=pane().querySelector('tei-seg[type="tcp-head"]');
        assert(note&&getComputedStyle(note).display==="inline","Lodge marginal note visible");
        assert(head&&getComputedStyle(head).display==="block","Lodge source heading is a block");
        assert(pane().querySelector('tei-gap[reason="illegible"]'),"Damaged TCP readings retained");
        fixtures.push("preserved source heading, marginal note and damaged reading");
      }
      await level("chapter");
      const chapterValues=[...document.querySelector("#chapter-selector").options].map(o=>o.value).filter(v=>v!=="");
      for (const c of chapterValues) {
        await change("#chapter-selector",c);
        assert(pane().querySelector("tei-div2"),"Rendered chapter "+b+"."+c);
        const chapter=chapters.find(n=>n.getAttribute("n")===c);
        if (isLodge) assert(chapter,"Registered Lodge chapter "+b+"."+c);
        record("chapter:"+b+"."+c,chapter?.textContent); counts.chapters++;
      }
      await level("section"); await change("#chapter-selector","");
      const units=[...document.querySelector("#section-selector").options].map(o=>o.value).filter(v=>v!=="");
      for (const u of units) {
        await change("#section-selector",u);
        const paragraph=paragraphs.find(p=>p.getAttribute("n")===u);
        if (isLodge) assert(paragraph,"Registered Lodge coarse unit "+b+"."+u);
        record("coarse:"+b+"."+u,paragraph?.textContent); counts.coarse++;
      }
      await level("niese");
      assert(starts.length===[673,654,542,663,572,442,455][b-1],"Source Niese count "+b);
      const menu=[...document.querySelector("#niese-selector").options].map(o=>o.value).filter(v=>v!=="");
      assert(menu.length===starts.length,"Complete canonical Niese menu "+b);
      for (let i=0;i<starts.length;i++) {
        const n=String(i+1); await change("#niese-selector",n);
        assert(pane().querySelector('tei-div2[type="niese-section"][n="'+n+'"]'),"Niese view "+b+"."+n);
        const actual=record("niese:"+b+"."+n,rawExcerpt(d,starts,i)); counts.niese++;
        if ((i+1)%100===0) console.log("Lodge QA progress "+source+" "+b+"."+n);
        if (isLodge && [[1,24],[3,3],[3,182],[3,183],[6,3],[6,267],[6,356],[6,427],[7,26]].some(([book,section])=>book===b&&section===i+1)) {
          if (b===1&&n==="24") assert(actual.startsWith("How at that instant when he retired himselfe into Aegypt"),"Accepted I.24 incipit");
          if (b===3&&n==="182") assert(actual.startsWith("so that the inhabitants were in great distresse"),"Accepted III.182 incipit");
          if (b===3&&n==="183") assert(actual.startsWith("Ioseph perceiuing there was abundance of all thinges else"),"Accepted III.183 incipit");
          if (b===3&&n==="3") assert(pane().querySelector('tei-p[sameAs$="#latin-bellum3-num1"]'),"III.3 coarse 1");
          if (b===6&&n==="427") assert(pane().querySelector('tei-p[sameAs$="#latin-bellum6-num420"]'),"VI.427 coarse 420");
          if (b===6&&n==="3") {
            const gap=pane().querySelector('tei-gap[reason="omitted"][unit="niese-section"]');
            assert(gap&&getComputedStyle(gap,"::before").content==='"[Omitted in Lodge]"',"VI.3 visible omission");
            assert(actual==="","VI.3 contains no neighbouring prose");
          }
          fixtures.push(b+"."+n);
        }
      }
      console.log("Lodge QA progress "+source+" book "+b+": "+JSON.stringify(counts));
    }
    assert(counts.books===7&&counts.chapters===111&&counts.coarse===704&&counts.niese===4001,"All canonical views exercised");
    return {counts,digest:await digest(content.join("\n")),exact_xml_source_words_verified:isLodge,
      first_and_final_sections_checked_for_each_book:true,all_canonical_book_transitions_checked:true,fixtures};
  };
  window.lodgeSourceStateQA = async () => {
    const tests=[];
    for (let b=1;b<=7;b++) {
      await change("#book-selector",String(b));
      for (const l of ["book","chapter","section","niese"]) {
        await level(l);
        if (l==="chapter"||l==="section") {
          const cs=document.querySelector("#chapter-selector");
          await change("#chapter-selector",[...cs.options].find(o=>o.value!=="").value);
        }
        if (l==="section") await change("#section-selector",[...document.querySelector("#section-selector").options].find(o=>o.value!=="").value);
        if (l==="niese") await change("#niese-selector",b===6?"3":"1");
        const before=new URL(location.href); before.searchParams.delete("english");
        for (const source of ["lodge1602","whiston"]) {
          await change("#english-source-selector",source);
          const after=new URL(location.href);
          assert((source==="lodge1602"&&after.searchParams.get("english")==="lodge1602")||
            (source==="whiston"&&!after.searchParams.has("english")),"Source URL semantics");
          after.searchParams.delete("english"); assert(after.href===before.href,"Coordinates preserved on source switch "+b+" "+l);
          assert(pane().querySelector("h3").textContent.includes(source==="lodge1602"?"Lodge (1602)":"Whiston"),"Source heading updated");
          assert(!pane().querySelector(source==="lodge1602"?'tei-p[sameAs^="#latin-bellum"]':'tei-p[id^="english-lodge1602-"]'),"No stale translation");
        }
        tests.push(b+" "+l);
      }
    }
    await change("#book-selector","3"); await level("niese"); await change("#niese-selector","182");
    await change("#english-source-selector","lodge1602");
    await change("#english-source-selector","whiston");
    history.back(); await ready(()=>document.querySelector("#english-source-selector").value==="lodge1602"&&pane().querySelector("h3").textContent.includes("Lodge"));
    assert(new URL(location.href).searchParams.get("niese")==="182","History preserves Niese");
    history.forward(); await ready(()=>document.querySelector("#english-source-selector").value==="whiston"&&pane().querySelector("h3").textContent.includes("Whiston"));
    assert(!new URL(location.href).searchParams.has("english"),"Forward removes default source parameter");
    history.back(); await ready(()=>pane().querySelector("h3").textContent.includes("Lodge"));
    window.lodgeSourceStateResult={status:"PASS",all_book_level_switches:tests,history_back_forward:true};
  };
})();
