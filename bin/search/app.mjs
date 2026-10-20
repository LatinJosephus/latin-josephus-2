import {createCollection} from './collection.mjs';
import {buildResultCards,citationFor,bookCitation,romanBook,readerURL,locationState,searchURL,mergedRanges,excerptWindows,citationScheme,citationUnitLabels,excerptCitation,defaultCollection,annotatedTextSegments,passageDivisionLabel,emptySourceNote,textLanguage,spellingEquivalence} from './ui-utils.mjs';
import {buildConcordance,exportConcordance} from './concordance.mjs';

const root=document.getElementById('lj-search');
const $=id=>root.querySelector(`#${id}`);
const els={query:$('query'),work:$('work'),book:$('book'),scope:$('scope'),fold:$('fold'),form:$('search-form'),button:$('search-button'),status:$('status'),error:$('error'),results:$('results'),region:$('results-region'),more:$('load-more'),copy:$('copy-link'),scopeHint:$('scope-hint'),context:$('result-context'),passages:$('view-passages'),concordance:$('view-concordance'),download:$('download-results'),downloadStatus:$('download-status'),resultQuery:$('result-query')};
const readerBase=new URL(root.dataset.readerBase||'/',location.href);
const pageSize=20;
const defaultQuery='"sacerdos ex Hierosolymis"';
let collection=null,catalog=null,catalogPromise=null,cards=[],items=[],shown=0,sequence=0,activeSearch=null,successful=null,view='passages';

function node(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function link(text,url,className){const e=node('a',text,className);e.href=url;e.target='_blank';e.rel='noopener noreferrer';return e;}
function option(text,value){const e=node('option',text);e.value=value;return e;}
function selectedCollections(state=null){
  if(!catalog)return [];
  const work=state?.work??els.work.value,book=state?.book??els.book.value;
  const bookCollection=book&&book!=='all'?catalog.books.find(entry=>entry.id===book)?.collectionId:null;
  return catalog.collections.filter(collection=>(work==='all'||collection.id===work)&&(!bookCollection||collection.id===bookCollection));
}
function updateScopeHint(){
  const collections=selectedCollections(),labels=citationUnitLabels(collections);
  els.fold.disabled=!collections.some(collection=>collection.language==='Latin');
  if(els.fold.disabled)els.fold.checked=false;
  const withinOption=els.scope.querySelector('option[value="section"]');
  if(withinOption)withinOption.textContent=`Within each ${labels.singular}`;
  const deh=collections.some(collection=>citationScheme(collection)==='chapter-paragraph');
  const apion=collections.some(collection=>collection.work==='contra-apionem');
  els.scopeHint.textContent=els.scope.value==='book'
    ?`Each selected book, work and edition is evaluated separately. Boolean conditions may match anywhere in that book. Exact phrases remain consecutive and can cross citation and chapter boundaries within it.${deh?' The De excidio Prologue is separated from the Book I narrative; phrases do not cross that boundary.':''}`
    :`All parts of the expression must match within the same ${labels.singular}. Choose whole-book scope to include phrases that cross citation-unit boundaries.${deh?' De excidio uses the reader’s chapter and paragraph citations.':''}`;
  if(apion)els.scopeHint.textContent+=' In Contra Apionem, phrases do not cross the source’s asterisk-marked interruptions; Boolean conditions can relate words on either side.';
  if(collections.some(collection=>collection.id==='antiquities-latin-bamberg78'))els.scopeHint.textContent+=' The Bamberg Latin Antiquities includes the Proem with Book I. Phrases stop at marked gaps, empty source intervals, the documented Book IX lacuna, the delimited interruptions in XVI and XX, and the Proem’s end. Split portions of the same Niese section share Boolean scope; exact phrases follow physical source order. The two labelled Bellum insertions in Book XI are separate citation units.';
  if(collections.some(collection=>collection.id==='antiquities-english-whiston'))els.scopeHint.textContent+=' The Whiston English pilot covers the Proem and Book I only. Phrases may cross adjacent Niese sections in whole-book scope, but stop at the Proem’s end. Headings, printed citation labels and footnotes are excluded.';
}
function populateBooks(selected='all'){
  const work=els.work.value;
  const books=catalog.books.filter(b=>work==='all'||b.collectionId===work);
  els.book.replaceChildren(option(work==='all'?'All available books':'All books in this work','all'));
  for(const b of books){
    const c=catalog.collections.find(c=>c.id===b.collectionId);
    const proem=c.work==='antiquities'&&b.number===1?' (including Proem)':'';
    els.book.append(option(work==='all'?`${bookCitation({...c,...b})}${proem} · ${c.language} · ${c.edition}`:(b.label||`Book ${romanBook(b.number)}`),b.id));
  }
  els.book.value=selected;
  els.book.disabled=false;
  updateScopeHint();
}
function populateControls(){
  els.work.replaceChildren();
  els.work.append(option('All available works and editions','all'));
  for(const c of catalog.collections)els.work.append(option(`${c.label} · ${c.language} · ${c.edition}`,c.id));
  els.work.value=defaultCollection(catalog);
  els.work.disabled=false;
  populateBooks();
  $('collection-description').textContent=catalog.collections.map(c=>`${c.label} · ${c.language} · ${c.edition}`).join(' / ');
  const coverage=catalog.collections.map(collection=>{
    const count=catalog.books.filter(book=>book.collectionId===collection.id).reduce((sum,book)=>sum+(book.citationUnits??book.sections),0);
    return `${collection.citationPrefix} (${collection.language}; ${collection.edition}): ${count.toLocaleString()} ${collection.work==='antiquities'?'citation units':citationUnitLabels([collection]).plural}`;
  }).join(' · ');
  $('coverage').textContent=`${catalog.books.length} book editions · ${coverage} · ${catalog.totals.tokens.toLocaleString()} words`;
  const included=catalog.collections.map(c=>`${c.label}, ${c.language}, ${c.edition} (${c.books.length} ${c.books.length===1?'book':'books'})`).join('; ');
  const bamberg=catalog.collections.some(c=>c.id==='antiquities-latin-bamberg78')?' The Bamberg Latin Antiquities covers the Proem and all twenty books. Books XI and XVI preserve the source’s split and transposed passages; the two Bellum insertions in XI have separate citations.':'';
  const whiston=catalog.collections.some(c=>c.id==='antiquities-english-whiston')?' The Whiston English pilot covers the Proem (Niese 1–26) and Book I narrative (27–346), a total of 346 Niese sections. Whiston Books II–XX are not yet indexed.':'';
  $('included-text').textContent=`Currently indexed: ${included}. Explicitly marked titles, citation labels and annotation notes are excluded. Source additions and untagged letters within the accepted Latin passages remain searchable, including inline Roman chapter letters.${catalog.collections.some(collection=>citationScheme(collection)==='chapter-paragraph')?' De excidio includes the Prologue and follows the canonical reader’s chapter and paragraph units. Supplied and deleted letters remain searchable and are visibly marked; unresolved text is indicated by †.':''}${bamberg}${whiston}`;
}
function applyState(state){
  els.query.value=state.query;els.work.value=state.work;populateBooks(state.book);
  els.scope.value=state.scope;els.fold.checked=state.fold;view=state.view==='concordance'?'concordance':'passages';updateScopeHint();updateViewButtons();
}
function saveLocation(state){const url=searchURL(state,location.href);if(url.href!==location.href)history.pushState(null,'',url);}
function updateViewButtons(){
  els.passages.setAttribute('aria-pressed',String(view==='passages'));
  els.concordance.setAttribute('aria-pressed',String(view==='concordance'));
  els.passages.disabled=els.concordance.disabled=!successful;
}
function successfulURL(){return searchURL({...successful.state,view},location.href);}
function appendTextRange(parent,record,start,end,ranges=[]){
  const stack=[];
  const closeTo=length=>{while(stack.length>length){const item=stack.pop();if(item.mark.kind==='supplied')item.element.append(document.createTextNode(']'));}};
  for(const segment of annotatedTextSegments(record,start,end,ranges)){
    let common=0;while(common<stack.length&&common<segment.marks.length&&stack[common].mark===segment.marks[common])common++;
    closeTo(common);
    for(let i=common;i<segment.marks.length;i++){
      const mark=segment.marks[i],element=node(mark.kind==='del'?'del':'span',undefined,`editorial-${mark.kind}`);
      element.title={del:'Deleted text in the edition; retained in the searchable source',supplied:'Text supplied by the editor',unclear:'Unresolved or unclear text',add:'Text encoded as an addition in the source; retained in search'}[mark.kind];
      if(mark.kind==='supplied')element.append(document.createTextNode('['));
      (stack.at(-1)?.element||parent).append(element);stack.push({mark,element});
    }
    const destination=stack.at(-1)?.element||parent;
    destination.append(segment.highlighted?node('mark',segment.text):document.createTextNode(segment.text));
  }
  closeTo(0);
}
function makeExcerpt(record,rawRanges,full=false,label=false){
  const p=node('p',undefined,'excerpt');p.lang=textLanguage(record);
  if(label)p.append(link(excerptCitation(record),readerURL(record,readerBase),'section-label'));
  const omission=emptySourceNote(record);
  if(omission){const note=node('span',omission,'source-note');note.lang='en';p.append(note);return p;}
  const ranges=mergedRanges(rawRanges||[],record.text.length);
  const windows=full?[{start:0,end:record.text.length}]:excerptWindows(record.text,ranges);
  for(let i=0;i<windows.length;i++){
    const w=windows[i];if(w.start>0)p.append(node('span','… ','ellipsis'));
    appendTextRange(p,record,w.start,w.end,ranges);
    if(w.end<record.text.length)p.append(node('span',' …','ellipsis'));
    if(i<windows.length-1)p.append(document.createTextNode(' '));
  }
  return p;
}
function makeCard(card){
  const article=node('article',undefined,'result-card');
  const header=node('div',undefined,'result-header');
  const first=card.records[0];
  const h=node('h3',undefined,'result-title');h.append(link(citationFor(card.records),readerURL(first,readerBase)));header.append(h);
  header.append(node('span',`${first.language} · ${first.edition} · ${passageDivisionLabel(card.records)}`,'result-meta'));article.append(header);
  for(const r of card.records)article.append(makeExcerpt(r,card.ranges[r.id],false,card.records.length>1));
  appendGapNote(article,card.records);
  if(card.records.some(r=>excerptWindows(r.text,card.ranges[r.id]||[]).some(w=>w.start>0||w.end<r.text.length))){
    const unit=citationScheme(first)==='chapter-paragraph'?'citation unit':'section';
    const details=node('details');details.append(node('summary',`Read the complete ${unit}${card.records.length>1?'s':''}`));
    for(const r of card.records)details.append(makeExcerpt(r,card.ranges[r.id],true,card.records.length>1));article.append(details);
  }
  return article;
}
function appendGapNote(parent,records){
  const gaps=records.flatMap(record=>(record.textGaps||[]).filter(gap=>gap.kind==='tei-gap'&&record.text!==''));
  if(gaps.length)parent.append(node('p',`The source marks an interruption (${[...new Set(gaps.map(gap=>gap.sourceAttributes?.reason||'gap'))].join(', ')}). Search words and exact phrases cannot join across it.`,'source-note'));
}
function concordanceHeader(row){
  const header=node('div',undefined,'result-header');
  const h=node('h3',undefined,'result-title');h.append(link(row.citation,row.readerURL));header.append(h);
  header.append(node('span',`${row.language} · ${row.edition}`,'result-meta'));
  return header;
}
function makeConcordanceRow(row){
  const article=node('article',undefined,'concordance-row');article.append(concordanceHeader(row));
  const p=node('p',undefined,'concordance-line');p.lang=textLanguage(row);
  const source={text:row.left+row.match+row.right,editorialMarks:row.editorialMarks||[]};
  const matchStart=row.left.length,matchEnd=matchStart+row.match.length;
  const left=node('span',undefined,'concordance-left');
  if(row.leftTruncated)left.append(node('span','… ','ellipsis'));
  appendTextRange(left,source,0,matchStart);
  const match=node('span',undefined,'concordance-match');appendTextRange(match,source,matchStart,matchEnd,[{start:matchStart,end:matchEnd}]);
  const right=node('span',undefined,'concordance-right');appendTextRange(right,source,matchEnd,source.text.length);
  if(row.rightTruncated)right.append(node('span',' …','ellipsis'));
  p.append(left,match,right);
  article.append(p);appendGapNote(article,row.records);return article;
}
function makeMatchingUnit(unit){
  const article=node('article',undefined,'concordance-row matching-unit');article.append(concordanceHeader(unit));
  article.append(node('p',`This ${unit.scope==='book'?'book':unit.citationUnitLabel||'section'} satisfies the full query without a positive word or phrase to highlight.`));
  if(unit.scope!=='book')for(const record of unit.records){const omission=emptySourceNote(record);if(omission)article.append(node('p',omission,'source-note'));}
  return article;
}
function orderItems(entries,records){
  const order=new Map(records.map((r,i)=>[r.id,i]));
  return entries.sort((a,b)=>(order.get(a.records[0]?.id)??Infinity)-(order.get(b.records[0]?.id)??Infinity));
}
function renderNext(){
  const next=Math.min(shown+pageSize,items.length),fragment=document.createDocumentFragment();
  for(let i=shown;i<next;i++){
    const item=items[i];
    fragment.append(item.kind==='matching-unit'?makeMatchingUnit(item):view==='concordance'?makeConcordanceRow(item):makeCard(item));
  }
  els.results.append(fragment);shown=next;els.more.hidden=shown>=items.length;
  els.more.textContent=`Show ${Math.min(pageSize,items.length-shown)} more results (${shown.toLocaleString()} of ${items.length.toLocaleString()} shown)`;
}
function renderEmpty(result){
  if(result.matchingUnits>0)return;
  const box=node('div',undefined,'no-results');box.append(node('h3','No matches'));
  const latin=selectedCollections(successful.state).some(collection=>collection.language==='Latin');
  box.append(node('p',result.scope==='section'
    ?`Try a wildcard${latin?', enable Latin spelling equivalence':''}, or choose whole-book scope if a phrase may cross a section boundary.`
    :`Try a wildcard${latin?' or enable Latin u/v and i/j equivalence':''}. Exact phrases require consecutive words within the same book.`));
  els.results.append(box);
}
function summarize(result,model){
  const spelling=spellingEquivalence(result);
  const labels=citationUnitLabels(catalog.collections.filter(collection=>result.selectedCollections.includes(collection.id)));
  const parts=[];
  if(model.occurrenceCount!==null){
    const count=model.occurrenceCount;
    parts.push(`${count.toLocaleString()} ${model.countKind==='phrase'?'phrase':'word'} ${count===1?'occurrence':'occurrences'}`);
  }
  if(result.scope==='section'){
    const count=result.matchingUnits,books=result.matchingBooks.length;
    parts.push(`${count.toLocaleString()} matching ${count===1?labels.singular:labels.plural}${books?` in ${books} ${books===1?'book':'books'}`:''}`);
  }else{
    const count=result.matchingUnits;
    parts.push(`${count} of ${result.selectedBooks.length} ${result.selectedBooks.length===1?'book matches':'books match'}`);
  }
  if(view==='concordance'&&model.countKind==='evidence')parts.push(`${model.positiveCount.toLocaleString()} positive ${model.positiveCount===1?'match':'matches'}`);
  parts.push(spelling,'case-insensitive',view==='concordance'?'concordance view':'passage view');
  return parts.join(' · ');
}
function resultContext(result,model){
  const parts=[];
  const collections=catalog.collections.filter(collection=>result.selectedCollections.includes(collection.id)),labels=citationUnitLabels(collections);
  if(view==='concordance'){
    if(model.countKind==='evidence'){
      parts.push(result.scope==='book'
        ?`Concordance rows show positive words and phrases in books that satisfy the full query. Separate Boolean terms may occur in different ${labels.plural}; a row need not satisfy the full query by itself.`
        :`Concordance rows show positive words and phrases in ${labels.plural} that satisfy the full query. Different rows may show different parts of that query.`);
      parts.push('The number of positive matches is not a word frequency.');
    }else{
      parts.push(`Each row shows one ${model.countKind==='phrase'?'phrase':'word'} occurrence, with up to ten words of context on each side.`);
      if(result.scope==='book')parts.push(`A phrase spanning adjacent ${labels.plural} appears once.`);
    }
  }else if(result.scope==='book'){
    parts.push('Whole-book search: each selected book, work and edition is evaluated separately. These excerpts locate positive matches; separate Boolean terms need not occur together in each excerpt. Exact phrases always stay within one book.');
  }
  if(model.unhighlightedUnits.length){
    const count=model.unhighlightedUnits.length,unit=result.scope==='book'?(count===1?'book':'books'):(count===1?labels.singular:labels.plural);
    parts.push(`${count.toLocaleString()} matching ${unit} ${count===1?'has':'have'} no positive word or phrase to highlight. ${count===1?'Its citation is':'Their citations are'} included in the results and CSV.`);
  }
  if(collections.some(collection=>citationScheme(collection)==='chapter-paragraph'))parts.push('De excidio citations give book, chapter and paragraph (or Prol.). [Brackets] mark supplied text; struck text marks editorial deletion; † marks unresolved text. These markings are retained in the CSV’s editorial columns.');
  if(collections.some(collection=>collection.work==='contra-apionem'))parts.push('Contra Apionem uses Niese sections. Asterisks retain the source’s marked interruptions, which exact phrases cannot cross. Bold green text marks an addition in the source; the CSV’s editorial columns show it as ⟨added text⟩.');
  if(collections.some(collection=>collection.id==='antiquities-latin-bamberg78'))parts.push('Antiquities includes the Proem and Books I–XX of Bamberg Msc. Class. 78. Added, deleted and uncertain letters remain searchable: bold green text marks additions, struck text marks deletions and dotted underlining marks uncertain readings. Exact phrases stop at source gaps, empty intervals, the documented Book IX lacuna and the end of the Proem. III.240 and VII.69–99 retain their citations and encoded omissions. X.108 has a citation label but no Latin before the next Niese marker. IX.51–109 are absent from the accepted source; no records have been generated for them. The accepted maps also mark Latin unavailable at XII.248, XIII.213 and 216, XIV.238–239, XV.338 and 347, XVI.77, 123, 189–199, 359 and 395–404, XVIII.216–217, and XX.27–36 and 238; those identities have no generated records. Actual source interruptions also block phrases between XVI.188 and 200 and between XX.26 and 37. Skipped section numbers alone do not create a physical gap. Books XI and XVI retain physical source order: their split sections share Boolean scope, while exact phrases cannot jump between displaced portions. The two Bellum insertions in XI have separate, explicitly labelled citations.');
  if(collections.some(collection=>collection.id==='antiquities-english-whiston'))parts.push('Whiston English pilot: Proem (Niese 1–26) and Book I narrative (27–346). Exact phrases may cross adjacent sections in whole-book scope, but never cross the Proem’s end. Headings, printed citation labels and footnotes are excluded. Original English spelling is retained; Latin u/v and i/j equivalence does not affect English matches.');
  return parts.join(' ');
}
function renderSuccessful(){
  const {result,model}=successful;
  items=view==='concordance'
    ?orderItems([...model.rows,...model.unhighlightedUnits],result.records)
    :orderItems([...cards,...(result.scope==='book'?model.unhighlightedUnits:[])],result.records);
  shown=0;els.results.replaceChildren();
  els.context.textContent=resultContext(result,model);els.context.hidden=!els.context.textContent;
  els.resultQuery.replaceChildren(node('span','Query: '),node('code',successful.state.query));els.resultQuery.hidden=false;
  if(items.length)renderNext();else{els.more.hidden=true;renderEmpty(result);}
  els.status.textContent=summarize(result,model);els.copy.disabled=false;
  els.download.disabled=false;updateViewButtons();
}
function changeView(nextView){
  if(!successful||view===nextView)return;
  view=nextView;renderSuccessful();saveLocation({...successful.state,view});
}
async function ensureCollection(){
  if(collection)return collection;
  if(!catalogPromise)catalogPromise=(async()=>{
    const response=await fetch(new URL('./catalog.json',import.meta.url),{cache:'no-cache'});
    if(!response.ok)throw new Error(`The text catalogue could not be loaded (HTTP ${response.status}). Please try Search again.`);
    const loaded=await response.json();
    if(!globalThis.lunr)throw new Error('The search library did not load. Please reload this page.');
    const ready=createCollection(loaded,globalThis.lunr,{baseURL:new URL('./',import.meta.url)});
    catalog=loaded;populateControls();collection=ready;
    return collection;
  })().catch(error=>{catalogPromise=null;throw error;});
  return catalogPromise;
}
async function search({writeUrl=true,fromLocation=false,example=null}={}){
  const current=++sequence;
  activeSearch?.abort();activeSearch=new AbortController();
  const signal=activeSearch.signal;
  cards=[];items=[];shown=0;successful=null;updateViewButtons();
  els.error.hidden=true;els.button.disabled=true;els.copy.disabled=true;els.download.disabled=true;els.more.hidden=true;
  els.region.setAttribute('aria-busy','true');els.results.replaceChildren();els.context.hidden=true;els.resultQuery.hidden=true;els.downloadStatus.textContent='';
  els.status.textContent=collection?'Searching…':'Loading the text catalogue…';
  try{
    const ready=await ensureCollection();if(current!==sequence)return;
    if(fromLocation){
      els.query.value=new URLSearchParams(location.search).get('q')||defaultQuery;
      applyState(locationState(location.search,catalog,defaultQuery));
    }
    if(example){
      // Validate examples through the same work/book contract as saved links.
      applyState(locationState(searchURL({query:example.query,work:example.work,book:example.book||'all',scope:example.scope||'section',fold:els.fold.checked,view},location.href).search,catalog,defaultQuery));
    }
    updateScopeHint();
    const state={query:els.query.value.trim(),work:els.work.value,book:els.book.value,scope:els.scope.value,fold:els.fold.checked,view};
    if(!state.query){els.query.focus();els.status.textContent='Enter a search expression.';return;}
    const result=await ready.search(state.query,{
      collections:state.work==='all'?'all':[state.work],books:state.book==='all'?'all':[state.book],scope:state.scope,fold:state.fold,signal,
      onProgress(progress){
        if(current!==sequence)return;
        const action=progress.stage==='searching'?'Searching':'Loading';
        const book=catalog.books.find(b=>b.id===progress.bookId);
        const work=catalog.collections.find(c=>c.id===progress.collectionId);
        els.status.textContent=`${action} ${bookCitation({...work,...book})} (${Math.min(progress.completed+1,progress.total)} of ${progress.total})…`;
      }
    });
    if(current!==sequence)return;
    cards=buildResultCards(result,result.records);
    const model=buildConcordance(result,result.records,{readerBase,contextWords:10});
    successful={state:Object.freeze({...state}),result,model};renderSuccessful();
    if(writeUrl)saveLocation(state);
  }catch(error){
    if(current!==sequence)return;
    els.error.textContent=error?.message||'The search could not be completed. Please try again.';els.error.hidden=false;
    els.status.textContent=error?.name==='QueryError'?'Please check the search expression.':'The search could not be completed for all selected books. Check the selections and try Search again.';
    successful=null;cards=[];items=[];shown=0;
    els.results.replaceChildren();els.more.hidden=true;els.context.hidden=true;els.resultQuery.hidden=true;els.copy.disabled=true;els.download.disabled=true;updateViewButtons();
  }finally{
    if(current===sequence){els.button.disabled=false;els.region.setAttribute('aria-busy','false');}
  }
}
els.form.addEventListener('submit',event=>{event.preventDefault();search();});
els.work.addEventListener('change',()=>{populateBooks();search();});
els.book.addEventListener('change',()=>search());
els.scope.addEventListener('change',()=>{updateScopeHint();search();});
els.fold.addEventListener('change',()=>search());
els.more.addEventListener('click',renderNext);
els.passages.addEventListener('click',()=>changeView('passages'));
els.concordance.addEventListener('click',()=>changeView('concordance'));
root.querySelectorAll('[data-query]').forEach(button=>button.addEventListener('click',()=>search({example:button.dataset})));
els.copy.addEventListener('click',async()=>{if(!successful)return;try{await navigator.clipboard.writeText(successfulURL().href);els.copy.textContent='Link copied';setTimeout(()=>els.copy.textContent='Copy search link',2000);}catch{els.copy.textContent='Copy the address bar URL';}});
els.download.addEventListener('click',()=>{
  if(!successful)return;
  els.download.disabled=true;els.downloadStatus.textContent='Preparing all results…';
  try{
    const exported=exportConcordance(successful.model,successful.result,{catalog,searchURL:successfulURL().href,exportedAt:new Date()});
    const url=URL.createObjectURL(new Blob([exported.text],{type:exported.mimeType}));
    const a=node('a');a.href=url;a.download=exported.filename;a.hidden=true;document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),60000);
    els.downloadStatus.textContent=exported.rowCount===0
      ?'CSV prepared: no matches; search settings and source coverage are included.'
      :`CSV prepared: ${exported.rowCount.toLocaleString()} ${exported.rowCount===1?'row':'rows'} from all results for the displayed query.`;
  }catch(error){
    els.downloadStatus.textContent=error?.message||'The CSV could not be prepared. Please try the download again.';
  }finally{
    els.download.disabled=!successful;
  }
});
window.addEventListener('popstate',()=>{
  if(successful&&catalog){
    try{
      const state=locationState(location.search,catalog,defaultQuery);
      if(['query','work','book','scope','fold'].every(key=>state[key]===successful.state[key])){
        applyState(state);renderSuccessful();return;
      }
    }catch{/* The search path below reports invalid saved links consistently. */}
  }
  search({writeUrl:false,fromLocation:true});
});
els.query.value=new URLSearchParams(location.search).get('q')||defaultQuery;
updateScopeHint();
await search({writeUrl:false,fromLocation:true});
