import {createLauroLoader,indexBook,lineAtoms,canonicalIds,locationFromUrl,updateLauroUrl,flowGroups,flowSeparator,folioLabels,readingParts,readingView,chapterMappings,readerText,editorialLabel} from './lauroCore.js';

const start=()=>{
  const pane=document.getElementById('italian'),toggle=document.getElementById('italian-pane-select');
  if(!pane||!toggle||location.pathname!=='/deh/')return;
  const loader=createLauroLoader(new URL('../data/deh-lauro1544/',import.meta.url));
  let state=locationFromUrl(location.href),navigation={book:Number(new URL(location.href).searchParams.get('book'))||1},data,index,manifest,generation=0,concordance;
  let unitOverride=new URL(location.href).searchParams.get('lauro-select')==='unit';
  const disclosures=new Set();
  toggle.checked=state.enabled;
  const el=(name,text,attrs={})=>{const e=document.createElement(name);if(text!==null)e.textContent=text;for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);return e;};
  const button=(text,handler)=>{const b=el('button',text,{type:'button'});b.addEventListener('click',handler);return b;};
  const label=(text,control)=>{const l=el('label',text);l.append(' ',control);return l;};
  const annotationLabel=editorialLabel;
  const disclosure=(id,title)=>{
    const d=el('details',null,{id,lang:'en'});d.open=disclosures.has(id);
    d.append(el('summary',title));
    d.addEventListener('toggle',()=>{if(d.isConnected){if(d.open)disclosures.add(id);else disclosures.delete(id);}});
    return d;
  };
  // Keep focus on the same control when a display preference rerenders the pane.
  const rerender=()=>{const id=pane.contains(document.activeElement)?document.activeElement.id:null;render();if(id)document.getElementById(id)?.focus({preventScroll:true});};
  const writeUrl=(push=false)=>{const u=updateLauroUrl(location.href,state);u.searchParams.delete('lauro-select');if(state.enabled&&unitOverride&&chapterNavigation())u.searchParams.set('lauro-select','unit');if(u.href!==location.href)history[push?'pushState':'replaceState']({},'',u);};
  const chapterNavigation=()=>navigation.chapter!=null&&(navigation.level==='chapter-level'||navigation.level==='section-level'&&!navigation.num);
  const chapterSelected=()=>!unitOverride&&chapterNavigation();
  const selectedMappings=()=>chapterSelected()&&data?chapterMappings(data,navigation.chapter):index?.byCanonical.get(state.canonical)||[];
  const selectedCanonical=()=>selectedMappings().flatMap(m=>m.canonical_targets||[m.canonical]).find(c=>c.xml_id===state.canonical);
  const selectionLabel=()=>chapterSelected()?String(navigation.chapter)==='0'?'Prologue':`${['','I','II','III','IV','V'][navigation.book]}.${navigation.chapter}`:selectedCanonical()?.citation;
  const canonicalLink=c=>{
    const u=updateLauroUrl(location.href,{...state,canonical:c.xml_id});
    for(const k of ['num','niese','parallel','parallel-work','deh-source','bj-source','aj-source','view','lauro-select'])u.searchParams.delete(k);
    u.searchParams.set('book',c.book);u.searchParams.set('chapter',c.chapter);u.searchParams.set('unit',c.unit);u.hash='';return u;
  };
  const markLatin=()=>{
    document.querySelectorAll('.lauro-latin-target').forEach(e=>e.classList.remove('lauro-latin-target'));
    if(state.alignment&&state.enabled)for(const m of selectedMappings())for(const c of m.canonical_targets||[m.canonical])if(!chapterSelected()||String(c.chapter)===String(navigation.chapter))document.getElementById(c.xml_id)?.classList.add('lauro-latin-target');
  };
  const choose=(id,locate=false)=>{
    if(!index.byCanonical.has(id))return;
    unitOverride=true;state.canonical=id;writeUrl(true);rerender();
    const target=document.getElementById(id);
    if(locate&&target)target.scrollIntoView({block:'center',behavior:'smooth'});
    else if(locate){const c=selectedCanonical();if(c)document.dispatchEvent(new CustomEvent('deh-select-canonical',{detail:c}));}
  };
  async function parallels(container,c,currentGeneration){
    try{
      concordance||=fetch(new URL('../data/deh-josephus-concordance.json',import.meta.url)).then(r=>{if(!r.ok)throw new Error('Parallel catalogue unavailable.');return r.json();});
      const d=await concordance;if(currentGeneration!==generation)return;
      const r=d.records.find(r=>r.deh.xml_id===c.xml_id);
      if(!r){container.append(el('p','No Josephus parallel is recorded for this Ussani unit.'));return;}
      // Navigate through the established concordance, never duplicate its targets.
      const u=canonicalLink(c);u.searchParams.set('parallel',r.id);u.searchParams.set('deh-source','ussani');
      container.append(el('a','Open existing DEH ↔ Josephus parallels',{href:u.href}));
    }catch(e){container.append(el('p',e.message));}
  }
  function render(){
    if(!data||!index)return;
    pane.replaceChildren(el('h3','Italian: Lauro 1544'));
    const folios=folioLabels(data);
    const controls=el('div',null,{id:'lauro-controls',lang:'en','aria-label':'Italian reading controls'});
    const toolbar=el('div',null,{class:'lauro-toolbar'});
    const about=el('a','About',{href:manifest.about_url||'/texts/lauro-1544/',title:'About this edition and transcription conventions','aria-label':'About this edition: Lauro 1544'});
    const settings=disclosure('lauro-settings','Settings');
    const options=el('div',null,{class:'lauro-options'});settings.append(options);
    const mode=el('select',null,{id:'lauro-view','aria-label':'Lauro viewing mode'});
    for(const[v,t]of [['running','Text — current reading view'],['book','Complete Italian text'],['source','Source lines'],['chapter','Lauro chapter'],['page','Folio']])mode.add(new Option(t,v));mode.value=state.mode;
    mode.addEventListener('change',()=>{state.mode=mode.value;writeUrl(true);refresh();});
    options.append(label('Italian display:',mode));
    const chapters=data.divisions.filter(d=>d.is_native_chapter);
    if(state.mode==='chapter'){
      const menu=el('select',null,{id:'lauro-chapter','aria-label':'Printed Italian chapter'});
      for(const d of chapters)menu.add(new Option(readerText(d.label),d.id));
      if(!chapters.some(d=>d.id===state.chapter))state.chapter=chapters[0]?.id||null;
      menu.value=state.chapter||'';menu.addEventListener('change',()=>{state.chapter=menu.value;writeUrl(true);rerender();});options.append(label('Printed chapter:',menu));
    }
    if(state.mode==='page'){
      const pages=data.pages.map(p=>p.image_number);if(!pages.includes(Number(state.page)))state.page=String(pages[0]);
      const menu=el('select',null,{id:'lauro-page','aria-label':'Lauro folio'});for(const im of pages)menu.add(new Option(folios.get(im),im));menu.value=state.page;
      const setPage=im=>{state.page=String(im);writeUrl(true);rerender();};
      menu.addEventListener('change',()=>setPage(menu.value));
      const prev=button('Previous page',()=>setPage(pages[pages.indexOf(Number(state.page))-1])),next=button('Next page',()=>setPage(pages[pages.indexOf(Number(state.page))+1]));
      prev.disabled=pages.indexOf(Number(state.page))===0;next.disabled=pages.indexOf(Number(state.page))===pages.length-1;options.append(label('Folio:',menu),prev,next);
    }
    const alignment=el('input',null,{type:'checkbox',id:'lauro-alignment'});alignment.checked=state.alignment;
    alignment.addEventListener('change',()=>{state.alignment=alignment.checked;writeUrl(true);rerender();});
    const highlight=label('Highlight correspondences',alignment);highlight.className='lauro-highlight-control';highlight.title='Highlight corresponding Lauro and Ussani passages';toolbar.append(highlight);
    const folioToggle=el('input',null,{type:'checkbox',id:'lauro-folios'});folioToggle.checked=state.folios;
    folioToggle.addEventListener('change',()=>{state.folios=folioToggle.checked;writeUrl(true);rerender();});options.append(label('Show folio labels',folioToggle));
    if(data.book){
      const units=el('select',null,{id:'lauro-ussani','aria-label':'Aligned passage (Ussani)',title:'Select any correspondence in this book, independently of the global sub-chapter selector'});units.add(new Option(chapterNavigation()?'Whole Ussani chapter':'Select a correspondence…',''));
      for(const [id,records]of index.byCanonical){const c=(records[0].canonical_targets||[records[0].canonical]).find(c=>c.xml_id===id);units.add(new Option(c.citation,id));}
      units.value=state.canonical||'';units.addEventListener('change',()=>{if(units.value)choose(units.value,true);else if(chapterNavigation()){unitOverride=false;state.canonical=null;writeUrl(true);rerender();}});options.append(label('Aligned passage:',units));
    }
    const share=el('a','Link',{id:'lauro-share',href:updateLauroUrl(location.href,state).href,title:'Link to this Italian view','aria-label':'Link to this Italian view'});toolbar.append(about,settings,share);
    controls.append(toolbar);
    const status=disclosure('lauro-status','Correspondence'),mm=selectedMappings(),mappedIds=new Set(mm.map(m=>m.id));status.className='lauro-status';
    status.firstElementChild.title='About the selected Lauro–Ussani correspondence';
    const view=readingView(data,state,chapterSelected()?{...navigation,level:'chapter-level'}:navigation,state.canonical),ll=view.lines,visibleIds=new Set(ll.map(l=>l.TEI_line_id)),all=mm.flatMap(m=>m.fragments),shown=all.filter(f=>visibleIds.has(f.line));
    if(mm.length){
      const c=selectedCanonical();status.append(el('p',`Ussani ${selectionLabel()}: ${chapterSelected()?`${mm.length} sub-chapter correspondences`:mm.map(m=>m.relation).join(', ')}; ${shown.length}/${all.length} source intervals visible. Passage correspondence does not imply word-for-word identity.`));
      if(!all.length)status.append(el('p','No separate Italian counterpart is recorded for this canonical unit.'));
      if(shown.length<all.length)status.append(button('Show all corresponding Italian spans',()=>{state.mode='book';writeUrl(true);refresh();}));
      if(c){status.append(el('a',`Read Ussani ${c.citation}`,{href:canonicalLink(c).href}));parallels(status,c,generation);}
      for(const m of mm){
        if(m.editorial_attention)status.append(el('p','This correspondence retains an editorial qualification; see the evidence below.',{class:'lauro-attention'}));
        const evidence=el('details',null),summary=el('summary',`${chapterSelected()?`[${m.canonical.citation}] — `:''}${m.id} — ${m.certainty}`);evidence.append(summary,el('p',m.evidence_reason));
        if(chapterSelected()){evidence.append(el('a',`Read Ussani ${m.canonical.citation}`,{href:canonicalLink(m.canonical).href}));parallels(evidence,m.canonical,generation);}
        for(const a of data.annotations.filter(a=>a.mapping_id===m.id)){
          evidence.append(el('p',annotationLabel(a)));
          if(a.secondary_target){const target=[...index.byCanonical.get(a.secondary_target.xml_id)||[]][0]?.canonical;if(target)evidence.append(el('a',`Locate secondary correspondence: ${target.citation}`,{href:canonicalLink(target).href}));}
        }
        status.append(evidence);
      }
    }else status.append(el('p','Select a Latin Ussani unit or a linked Italian passage to locate its correspondence. Unmapped source matter is retained without inferred links.'));
    toolbar.append(status);pane.append(controls);
    const diplomatic=state.mode==='source'||state.mode==='page';
    const source=el('section',null,{id:'lauro-source',class:`lauro-source${diplomatic?' lauro-diplomatic':''}`,lang:'it','aria-label':'Lauro Italian transcription'});
    const secondary=new Map();
    for(const a of data.annotations)for(const f of a.fragments||[]){if(!secondary.has(f.line))secondary.set(f.line,[]);secondary.get(f.line).push({...f,annotation:a.id});}
    const displayedAnnotationIds=new Set();
    const additionalSupplyLabels=new Set();
    let previousPage=null,previousSourceLine=null;
    const primaryPositions=new Map(data.lines.filter(l=>l.primary).map((l,i)=>[l.TEI_line_id,i]));
    for(const group of flowGroups(ll)){
      if(group.type==='marginalia')source.append(el('p','Marginal text',{class:'lauro-ancillary-label',lang:'en'}));
      const paragraph=el('div',null,{class:`lauro-paragraph lauro-role-${group.type}`});let previousLine=null;
      for(const l of group.lines){
      if(l.image_number!==previousPage){
        paragraph.append(el('span',null,{id:`lauro-image-${l.image_number}`,class:'lauro-page-anchor'}));
        if(state.folios)paragraph.append(el('span',`[${folios.get(l.image_number)}] `,{class:'lauro-folio-marker',lang:'en'}));previousPage=l.image_number;
      }
      const line=el('span',null,{id:l.TEI_line_id,class:'lauro-line','data-source-line':l.TEI_line_id,'data-source-image':String(l.image_number)});
      const atoms=lineAtoms(l,index.byLine.get(l.TEI_line_id)||[],secondary.get(l.TEI_line_id)||[]);
      if(!view.included)for(const note of l.editorial_annotations||[])if(/suppl/i.test(note.kind||note.annotation_kind||''))additionalSupplyLabels.add(annotationLabel(note));
      const shownText=atoms.filter(a=>!view.included||a.mappings.some(id=>view.included.has(id))).map(a=>a.text).join('');
      const discontinuous=view.included&&previousSourceLine&&primaryPositions.get(l.TEI_line_id)>primaryPositions.get(previousSourceLine.TEI_line_id)+1;
      if(!diplomatic&&discontinuous)paragraph.append(el('span',' … ',{class:'lauro-reading-gap',lang:'en','aria-label':'Noncontiguous source passages'}));
      else if(!diplomatic){const separator=flowSeparator(previousLine,shownText);if(separator)paragraph.append(el('span',separator,{class:'lauro-flow-separator'}));}
      for(const atom of atoms){
        const span=el('span',null,{'data-start-cp':String(atom.start_cp),'data-end-cp':String(atom.end_cp),'data-start-utf16':String(atom.start_utf16),'data-end-utf16':String(atom.end_utf16)});
        if(diplomatic)span.append(document.createTextNode(readerText(atom.text)));
        else for(const part of readingParts(l.text_exact,atom.start_utf16,atom.end_utf16))if(part.hidden)span.append(el('span',part.text,{class:'lauro-division-marker','aria-hidden':'true'}));else span.append(document.createTextNode(readerText(part.text)));
        if(atom.mappings.length){span.dataset.mappings=atom.mappings.join(' ');span.classList.add('lauro-linked');if(state.alignment&&atom.mappings.some(id=>mappedIds.has(id)))span.classList.add('lauro-selected');}
        if(view.included&&!atom.mappings.some(id=>view.included.has(id)))span.classList.add('lauro-outside-view');
        if(atom.annotations.length){
          span.dataset.annotations=atom.annotations.join(' ');span.classList.add('lauro-annotated');
          const notes=data.annotations.filter(a=>atom.annotations.includes(a.id));
          span.title=notes.map(annotationLabel).join('\n');
          if(notes.some(a=>/suppl/i.test(a.kind||'')))span.classList.add('lauro-editorial-supply');
          if(!view.included||atom.mappings.some(id=>view.included.has(id)))for(const id of atom.annotations)displayedAnnotationIds.add(id);
        }
        line.append(span);
      }
      if(line.textContent!==readerText(l.text_exact))throw new Error('Lauro source-to-display reconstruction failed.');paragraph.append(line);previousLine=shownText;previousSourceLine=l;
      }
      source.append(paragraph);
    }
    if(!ll.length)source.append(el('p',mm.some(m=>m.relation==='absent')?'No separate Italian counterpart is recorded for this passage.':state.mode==='page'?'No transcribed text is available for this page.':'No source text belongs to this selection.',{class:'lauro-empty',lang:'en'}));
    source.addEventListener('click',e=>{
      const span=e.target.closest('[data-mappings]');if(!span||!state.alignment)return;
      const targets=[...new Set(span.dataset.mappings.split(' ').flatMap(id=>canonicalIds(index.mappings.get(id))))];
      if(targets.length===1)choose(targets[0],true);
      else{const picker=el('div',null,{class:'lauro-target-picker',lang:'en'});picker.append(el('p','This span has multiple canonical correspondences:'));for(const id of targets){const m=index.byCanonical.get(id)[0],c=(m.canonical_targets||[m.canonical]).find(c=>c.xml_id===id);picker.append(button(c.citation,()=>choose(id,true)));}status.open=true;status.append(picker);}
    });
    // Interface citations remain outside exact source-line/offset nodes. In a
    // larger view, identify the selected correspondence rather than labelling
    // the start of the whole Italian book with an unrelated selected unit.
    if(mm.length){
      const citation=selectedCanonical()?.citation_label_exact||`[${selectionLabel()}]`;
      if(view.included?.size===1&&mappedIds.has([...view.included][0])&&source.querySelector('.lauro-paragraph'))source.querySelector('.lauro-paragraph').prepend(el('span',citation,{class:'lauro-passage-label',lang:'en'}));
      else status.firstElementChild.append(` ${citation}`);
    }
    const supplyLabels=new Set([...additionalSupplyLabels,...data.annotations.filter(a=>displayedAnnotationIds.has(a.id)&&/suppl/i.test(a.kind||'')).map(annotationLabel)]);
    for(const text of supplyLabels)controls.append(el('p',text,{class:'lauro-source-qualification',lang:'en',role:'note'}));
    pane.append(source);markLatin();writeUrl();share.href=location.href;
    pane.dataset.lauroReady=String(data.book);pane.dataset.lauroVersion=data.version;
    const hash=decodeURIComponent(location.hash.slice(1));if(hash.startsWith('lauro1544-'))document.getElementById(hash)?.scrollIntoView({block:'center'});
    document.dispatchEvent(new CustomEvent('lauro-view-rendered',{detail:{book:data.book,mode:state.mode,canonical:state.canonical,lines:ll.length,intervals:all.length,visibleIntervals:shown.length}}));
  }
  async function refresh(){
    const focus=pane.contains(document.activeElement)?document.activeElement.id:null;
    const mine=++generation;if(!state.enabled){pane.hidden=true;pane.classList.add('hidden');markLatin();return;}
    pane.hidden=false;pane.classList.remove('hidden');pane.replaceChildren(el('h3','Italian: Lauro 1544'),el('p','Loading Lauro text…',{lang:'en',role:'status'}));
    try{
      manifest=await loader.manifest();const loaded=await loader.book(navigation.book);if(mine!==generation)return;
      data=loaded;index=indexBook(data);
      if(chapterSelected())state.canonical=null;
      else if(navigation.num&&data.book!==0&&!(unitOverride&&chapterNavigation()))state.canonical=`latin-deh${navigation.book}-num${navigation.num}`;
      if(state.canonical&&!index.byCanonical.has(state.canonical)&&data.book!==0)state.canonical=null;
      if(navigation.level==='chapter-level'&&selectedCanonical()&&String(selectedCanonical().chapter)!==String(navigation.chapter))state.canonical=null;
      render();if(focus)document.getElementById(focus)?.focus({preventScroll:true});
    }catch(e){if(mine!==generation)return;pane.replaceChildren(el('h3','Italian: Lauro 1544'),el('p',e.message,{role:'alert',lang:'en'}));}
  }
  toggle.addEventListener('change',()=>{state.enabled=toggle.checked;writeUrl(true);refresh();});
  document.addEventListener('deh-view-rendered',e=>{if(navigation.level&&['book','chapter','num','level'].some(k=>String(navigation[k])!==String(e.detail[k])))unitOverride=false;navigation=e.detail;state.enabled=toggle.checked;refresh();});
  document.getElementById('latin').addEventListener('click',e=>{if(!state.enabled)return;const p=e.target.closest('tei-p[id^="latin-deh"]');if(p)choose(p.id);});
  window.addEventListener('popstate',()=>{state=locationFromUrl(location.href);unitOverride=new URL(location.href).searchParams.get('lauro-select')==='unit';toggle.checked=state.enabled;navigation={book:Number(new URL(location.href).searchParams.get('book'))||1};refresh();});
  if(state.enabled)refresh();
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
