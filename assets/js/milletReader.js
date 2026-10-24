import {createMilletLoader,indexBook,lineAtoms,canonicalIds,locationFromUrl,updateMilletUrl,flowGroups,flowSeparator,folioLabels,readingParts,readingView} from './milletCore.js';

const start=()=>{
  const pane=document.getElementById('french'),toggle=document.getElementById('french-pane-select'),controls=document.getElementById('millet-general-controls'),controlPanel=document.getElementById('millet-controls');
  if(!pane||!toggle||location.pathname!=='/deh/')return;
  const loader=createMilletLoader(new URL('../data/deh-millet1556/',import.meta.url));
  let state=locationFromUrl(location.href),navigation={book:Number(new URL(location.href).searchParams.get('book'))||1},data,index,manifest,generation=0,concordance;
  toggle.checked=state.enabled;
  const el=(name,text,attrs={})=>{const e=document.createElement(name);if(text!==null)e.textContent=text;for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);return e;};
  const button=(text,handler)=>{const b=el('button',text,{type:'button'});b.addEventListener('click',handler);return b;};
  const label=(text,control)=>{const l=el('label',text);l.append(' ',control);return l;};
  const writeUrl=(push=false)=>{const u=updateMilletUrl(location.href,state);if(u.href!==location.href)history[push?'pushState':'replaceState']({},'',u);};
  const selectedMappings=()=>index?.byCanonical.get(state.canonical)||[];
  const selectedCanonical=()=>selectedMappings().flatMap(m=>m.canonical_targets||[m.canonical]).find(c=>c.xml_id===state.canonical);
  const canonicalLink=c=>{
    const u=updateMilletUrl(location.href,{...state,canonical:c.xml_id});
    for(const k of ['num','niese','parallel','parallel-work','deh-source','bj-source','aj-source','view'])u.searchParams.delete(k);
    u.searchParams.set('book',c.book);u.searchParams.set('chapter',c.chapter);u.searchParams.set('unit',c.unit);u.hash='';return u;
  };
  const markLatin=()=>{
    document.querySelectorAll('.millet-latin-target').forEach(e=>e.classList.remove('millet-latin-target'));
    if(state.alignment&&state.enabled&&state.canonical)document.getElementById(state.canonical)?.classList.add('millet-latin-target');
  };
  const choose=(id,locate=false)=>{
    if(!index.byCanonical.has(id))return;
    state.canonical=id;writeUrl(true);render();
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
    pane.replaceChildren(el('h3','French: Millet 1556'));
    controls.replaceChildren();controlPanel.hidden=false;
    const folios=folioLabels(data);
    const toolbar=el('div',null,{class:'millet-toolbar',lang:'en'});
    const about=el('a','About this edition, conventions and provisional status',{href:'/deh/millet-1556/'});
    const mode=el('select',null,{id:'millet-view','aria-label':'Millet viewing mode'});
    for(const[v,t]of [['running','Text — current reading view'],['book','Complete text'],['source','Complete source'],['chapter','Millet chapter'],['page','Folio'],['preliminary','Preliminary matter']])mode.add(new Option(t,v));mode.value=state.mode;
    mode.addEventListener('change',()=>{state.mode=mode.value;writeUrl(true);refresh();});
    toolbar.append(about,label('French view:',mode));
    const chapters=data.divisions.filter(d=>d.is_native_chapter);
    if(state.mode==='chapter'){
      const menu=el('select',null,{id:'millet-chapter','aria-label':'Printed French chapter'});
      for(const d of chapters)menu.add(new Option(d.label,d.id));
      if(!chapters.some(d=>d.id===state.chapter))state.chapter=chapters[0]?.id||null;
      menu.value=state.chapter||'';menu.addEventListener('change',()=>{state.chapter=menu.value;writeUrl(true);render();});toolbar.append(menu);
    }
    if(state.mode==='page'){
      const pages=data.pages.map(p=>p.image_number);if(!pages.includes(Number(state.page)))state.page=String(pages[0]);
      const menu=el('select',null,{id:'millet-page','aria-label':'Millet folio'});for(const im of pages)menu.add(new Option(folios.get(im),im));menu.value=state.page;
      const setPage=im=>{state.page=String(im);writeUrl(true);render();};
      menu.addEventListener('change',()=>setPage(menu.value));
      const prev=button('Previous leaf',()=>setPage(pages[pages.indexOf(Number(state.page))-1])),next=button('Next leaf',()=>setPage(pages[pages.indexOf(Number(state.page))+1]));
      prev.disabled=pages.indexOf(Number(state.page))===0;next.disabled=pages.indexOf(Number(state.page))===pages.length-1;toolbar.append(prev,menu,next);
    }
    const alignment=el('input',null,{type:'checkbox',id:'millet-alignment'});alignment.checked=state.alignment;
    alignment.addEventListener('change',()=>{state.alignment=alignment.checked;writeUrl(true);render();});toolbar.append(label('Millet ↔ Ussani highlighting',alignment));
    const folioToggle=el('input',null,{type:'checkbox',id:'millet-folios'});folioToggle.checked=state.folios;
    folioToggle.addEventListener('change',()=>{state.folios=folioToggle.checked;writeUrl(true);render();});toolbar.append(label('Show Millet folio numbers',folioToggle));
    if(data.book){
      const units=el('select',null,{id:'millet-ussani','aria-label':'Corresponding Ussani unit'});units.add(new Option('Select a Ussani correspondence…',''));
      for(const [id,records]of index.byCanonical){const c=(records[0].canonical_targets||[records[0].canonical]).find(c=>c.xml_id===id);units.add(new Option(c.citation,id));}
      units.value=state.canonical||'';units.addEventListener('change',()=>{if(units.value)choose(units.value,true);});toolbar.append(units);
    }
    const share=el('a','Link to this French view',{id:'millet-share',href:updateMilletUrl(location.href,state).href});toolbar.append(share);
    controls.append(toolbar);
    const status=el('details',null,{class:'millet-status',lang:'en',id:'millet-status'}),mm=selectedMappings(),mappedIds=new Set(mm.map(m=>m.id));
    status.append(el('summary','About the selected correspondence'));
    const view=readingView(data,state,navigation,state.canonical),ll=view.lines,visibleIds=new Set(ll.map(l=>l.TEI_line_id)),all=mm.flatMap(m=>m.fragments),shown=all.filter(f=>visibleIds.has(f.line));
    if(mm.length){
      const c=selectedCanonical();status.append(el('p',`Ussani ${c.citation}: ${mm.map(m=>m.relation).join(', ')}; ${shown.length}/${all.length} source intervals visible. Passage correspondence does not imply word-for-word identity.`));
      pane.append(el('p',`Ussani ${c.citation}`,{class:'millet-passage-label',lang:'en'}));
      if(!all.length)status.append(el('p','No separate French counterpart is recorded for this canonical unit.'));
      if(shown.length<all.length)status.append(button('Show all corresponding French spans',()=>{state.mode='book';writeUrl(true);refresh();}));
      const latin=el('a',`Read Ussani ${c.citation}`,{href:canonicalLink(c).href});status.append(latin);
      parallels(status,c,generation);
      for(const m of mm){
        if(m.editorial_attention)status.append(el('p','Editorial attention remains pending. This inherited flag has not been adjudicated.',{class:'millet-attention'}));
        const evidence=el('details',null),summary=el('summary',`${m.id} — ${m.certainty}`);evidence.append(summary,el('p',m.evidence_reason));
        for(const a of data.annotations.filter(a=>a.mapping_id===m.id)){
          evidence.append(el('p',`${a.kind}: ${typeof a.original==='string'?a.original:JSON.stringify(a.original)}`));
          if(a.secondary_target){const target=[...index.byCanonical.get(a.secondary_target.xml_id)||[]][0]?.canonical;if(target)evidence.append(el('a',`Locate secondary correspondence: ${target.citation}`,{href:canonicalLink(target).href}));}
        }
        status.append(evidence);
      }
    }else status.append(el('p','Select a Latin Ussani unit or a linked French passage to locate its correspondence. Unmapped source matter is retained without inferred links.'));
    controls.append(status);
    const source=el('section',null,{id:'millet-source',class:'millet-source',lang:'fr','aria-label':'Millet exact source text'});
    const secondary=new Map();
    for(const a of data.annotations)for(const f of a.fragments||[]){if(!secondary.has(f.line))secondary.set(f.line,[]);secondary.get(f.line).push({...f,annotation:a.id});}
    let previousPage=null,previousSourceLine=null;
    const primaryPositions=new Map(data.lines.filter(l=>l.primary).map((l,i)=>[l.TEI_line_id,i]));
    for(const group of flowGroups(ll)){
      if(group.type==='marginalia')source.append(el('p','Handwritten / marginal source material',{class:'millet-ancillary-label',lang:'en'}));
      const paragraph=el('div',null,{class:`millet-paragraph millet-role-${group.type}`});let previousLine=null;
      for(const l of group.lines){
      if(l.image_number!==previousPage){
        paragraph.append(el('span',null,{id:`millet-image-${l.image_number}`,class:'millet-page-anchor'}));
        if(state.folios)paragraph.append(el('span',`[${folios.get(l.image_number)}] `,{class:'millet-folio-marker',lang:'en'}));previousPage=l.image_number;
      }
      const line=el('span',null,{id:l.TEI_line_id,class:'millet-line','data-source-line':l.TEI_line_id,'data-source-image':String(l.image_number)});
      const atoms=lineAtoms(l,index.byLine.get(l.TEI_line_id)||[],secondary.get(l.TEI_line_id)||[]);
      const shownText=atoms.filter(a=>!view.included||a.mappings.some(id=>view.included.has(id))).map(a=>a.text).join('');
      const discontinuous=view.included&&previousSourceLine&&primaryPositions.get(l.TEI_line_id)>primaryPositions.get(previousSourceLine.TEI_line_id)+1;
      if(discontinuous)paragraph.append(el('span',' … ',{class:'millet-reading-gap',lang:'en','aria-label':'Noncontiguous source passages'}));
      else{const separator=flowSeparator(previousLine,shownText);if(separator)paragraph.append(el('span',separator,{class:'millet-flow-separator'}));}
      for(const atom of atoms){
        const span=el('span',null,{'data-start-cp':String(atom.start_cp),'data-end-cp':String(atom.end_cp),'data-start-utf16':String(atom.start_utf16),'data-end-utf16':String(atom.end_utf16)});
        for(const part of readingParts(l.text_exact,atom.start_utf16,atom.end_utf16))if(part.hidden)span.append(el('span',part.text,{class:'millet-division-marker','aria-hidden':'true'}));else span.append(document.createTextNode(part.text));
        if(atom.mappings.length){span.dataset.mappings=atom.mappings.join(' ');span.classList.add('millet-linked');if(state.alignment&&atom.mappings.some(id=>mappedIds.has(id)))span.classList.add('millet-selected');}
        if(view.included&&!atom.mappings.some(id=>view.included.has(id)))span.classList.add('millet-outside-view');
        if(atom.annotations.length){span.dataset.annotations=atom.annotations.join(' ');span.classList.add('millet-annotated');}
        line.append(span);
      }
      if(line.textContent!==l.text_exact)throw new Error('Millet source-to-DOM reconstruction failed.');paragraph.append(line);previousLine=shownText;previousSourceLine=l;
      }
      source.append(paragraph);
    }
    if(!ll.length)source.append(el('p',mm.some(m=>m.relation==='absent')?'No separate French counterpart is recorded for this passage.':state.mode==='page'?'This leaf is blank.':'No source text belongs to this selection.',{class:'millet-empty',lang:'en'}));
    source.addEventListener('click',e=>{
      const span=e.target.closest('[data-mappings]');if(!span||!state.alignment)return;
      const targets=[...new Set(span.dataset.mappings.split(' ').flatMap(id=>canonicalIds(index.mappings.get(id))))];
      if(targets.length===1)choose(targets[0],true);
      else{const picker=el('div',null,{class:'millet-target-picker',lang:'en'});picker.append(el('p','This span has multiple canonical correspondences:'));for(const id of targets){const m=index.byCanonical.get(id)[0],c=(m.canonical_targets||[m.canonical]).find(c=>c.xml_id===id);picker.append(button(c.citation,()=>choose(id,true)));}status.open=true;status.append(picker);}
    });
    pane.append(source);markLatin();writeUrl();share.href=location.href;
    pane.dataset.milletReady=String(data.book);pane.dataset.milletVersion=data.version;
    const hash=decodeURIComponent(location.hash.slice(1));if(hash.startsWith('millet1556-'))document.getElementById(hash)?.scrollIntoView({block:'center'});
    document.dispatchEvent(new CustomEvent('millet-view-rendered',{detail:{book:data.book,mode:state.mode,canonical:state.canonical,lines:ll.length,intervals:all.length,visibleIntervals:shown.length}}));
  }
  async function refresh(){
    const mine=++generation;if(!state.enabled){controlPanel.hidden=true;markLatin();return;}
    pane.hidden=false;pane.classList.remove('hidden');pane.replaceChildren(el('h3','French: Millet 1556'),el('p','Loading certified Millet source…',{lang:'en',role:'status'}));
    try{
      manifest=await loader.manifest();const loaded=await loader.book(state.mode==='preliminary'?0:navigation.book);if(mine!==generation)return;
      data=loaded;index=indexBook(data);
      if(navigation.num&&data.book!==0)state.canonical=`latin-deh${navigation.book}-num${navigation.num}`;
      if(state.canonical&&!index.byCanonical.has(state.canonical)&&data.book!==0)state.canonical=null;
      if(navigation.level==='chapter-level'&&selectedCanonical()&&String(selectedCanonical().chapter)!==String(navigation.chapter))state.canonical=null;
      render();
    }catch(e){if(mine!==generation)return;pane.replaceChildren(el('h3','French: Millet 1556'),el('p',e.message,{role:'alert',lang:'en'}));}
  }
  toggle.addEventListener('change',()=>{state.enabled=toggle.checked;writeUrl(true);refresh();});
  document.addEventListener('deh-view-rendered',e=>{navigation=e.detail;state.enabled=toggle.checked;refresh();});
  document.getElementById('latin').addEventListener('click',e=>{if(!state.enabled)return;const p=e.target.closest('tei-p[id^="latin-deh"]');if(p)choose(p.id);});
  window.addEventListener('popstate',()=>{state=locationFromUrl(location.href);toggle.checked=state.enabled;navigation.book=Number(new URL(location.href).searchParams.get('book'))||1;refresh();});
  if(state.enabled)refresh();
};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
