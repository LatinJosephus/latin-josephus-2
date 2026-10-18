import {createCollection} from './collection.mjs';
import {buildResultCards,citationFor,bookCitation,romanBook,readerURL,locationState,searchURL,mergedRanges,excerptWindows} from './ui-utils.mjs';

const root=document.getElementById('lj-search');
const $=id=>root.querySelector(`#${id}`);
const els={query:$('query'),work:$('work'),book:$('book'),scope:$('scope'),fold:$('fold'),form:$('search-form'),button:$('search-button'),status:$('status'),error:$('error'),results:$('results'),region:$('results-region'),more:$('load-more'),copy:$('copy-link'),scopeHint:$('scope-hint'),context:$('result-context')};
const readerBase=new URL(root.dataset.readerBase||'/',location.href);
const pageSize=20;
const defaultQuery='"sacerdos ex Hierosolymis"';
let collection=null,catalog=null,catalogPromise=null,cards=[],shown=0,sequence=0,activeSearch=null;

function node(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function link(text,url,className){const e=node('a',text,className);e.href=url;e.target='_blank';e.rel='noopener noreferrer';return e;}
function option(text,value){const e=node('option',text);e.value=value;return e;}
function updateScopeHint(){
  els.scopeHint.textContent=els.scope.value==='book'
    ?'Each selected book, work and edition is evaluated separately. Boolean conditions may match anywhere in that book. Exact phrases remain consecutive and can cross Niese and chapter boundaries within it.'
    :'All parts of the expression must match within the same Niese section. Choose whole-book scope to include phrases that cross section boundaries.';
}
function populateBooks(selected='all'){
  const work=els.work.value;
  const books=catalog.books.filter(b=>work==='all'||b.collectionId===work);
  els.book.replaceChildren(option(work==='all'?'All available books':'All books in this work','all'));
  for(const b of books){
    const c=catalog.collections.find(c=>c.id===b.collectionId);
    els.book.append(option(work==='all'?`${bookCitation({...c,...b})} · ${c.edition}`:`Book ${romanBook(b.number)}`,b.id));
  }
  els.book.value=selected;
  els.book.disabled=false;
}
function populateControls(){
  els.work.replaceChildren();
  els.work.append(option('All available works and editions','all'));
  for(const c of catalog.collections)els.work.append(option(`${c.label} · ${c.language} · ${c.edition}`,c.id));
  if(catalog.collections.length===1)els.work.value=catalog.collections[0].id;
  els.work.disabled=false;
  populateBooks();
  $('collection-description').textContent=catalog.collections.map(c=>`${c.label} · ${c.language} · ${c.edition}`).join(' / ');
  $('coverage').textContent=`${catalog.books.length} books · ${catalog.totals.sections.toLocaleString()} Niese sections · ${catalog.totals.tokens.toLocaleString()} words · Latin main text`;
  const included=catalog.collections.map(c=>`${c.label}, ${c.language}, ${c.edition} (${c.books.length} books)`).join('; ');
  const future=catalog.collections.some(c=>c.work==='antiquities')?'':' Antiquities will be added after its text repairs and verification are complete.';
  $('included-text').textContent=`Currently indexed: ${included}. Editorial titles, printed division labels and manuscript annotations are excluded.${future}`;
}
function applyState(state){
  els.query.value=state.query;els.work.value=state.work;populateBooks(state.book);
  els.scope.value=state.scope;els.fold.checked=state.fold;updateScopeHint();
}
function saveLocation(state){const url=searchURL(state,location.href);if(url.href!==location.href)history.pushState(null,'',url);}
function appendTextRange(parent,text,start,end,ranges){
  let cursor=start;
  for(const r of ranges){const a=Math.max(start,r.start),b=Math.min(end,r.end);if(a>=b)continue;if(a>cursor)parent.append(document.createTextNode(text.slice(cursor,a)));parent.append(node('mark',text.slice(a,b)));cursor=b;}
  if(cursor<end)parent.append(document.createTextNode(text.slice(cursor,end)));
}
function makeExcerpt(record,rawRanges,full=false,label=false){
  const p=node('p',undefined,'excerpt');p.lang='la';
  if(label)p.append(link(`§${record.section}`,readerURL(record,readerBase),'section-label'));
  const ranges=mergedRanges(rawRanges||[],record.text.length);
  const windows=full?[{start:0,end:record.text.length}]:excerptWindows(record.text,ranges);
  for(let i=0;i<windows.length;i++){
    const w=windows[i];if(w.start>0)p.append(node('span','… ','ellipsis'));
    appendTextRange(p,record.text,w.start,w.end,ranges);
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
  const chapters=[...new Set(card.records.map(r=>r.chapter))];
  const chapterLabel=chapters.length===1?(chapters[0]===0?'Proem':`Chapter ${chapters[0]}`):'Across chapters';
  header.append(node('span',`${first.language} · ${first.edition} · ${chapterLabel}`,'result-meta'));article.append(header);
  for(const r of card.records)article.append(makeExcerpt(r,card.ranges[r.id],false,card.records.length>1));
  if(card.records.some(r=>excerptWindows(r.text,card.ranges[r.id]||[]).some(w=>w.start>0||w.end<r.text.length))){
    const details=node('details');details.append(node('summary',card.records.length>1?'Read the complete sections':'Read the complete section'));
    for(const r of card.records)details.append(makeExcerpt(r,card.ranges[r.id],true,card.records.length>1));article.append(details);
  }
  return article;
}
function renderNext(){
  const next=Math.min(shown+pageSize,cards.length),fragment=document.createDocumentFragment();
  for(let i=shown;i<next;i++)fragment.append(makeCard(cards[i]));
  els.results.append(fragment);shown=next;els.more.hidden=shown>=cards.length;
  els.more.textContent=`Show ${Math.min(pageSize,cards.length-shown)} more results (${shown} of ${cards.length} shown)`;
}
function renderUnhighlightedBooks(result){
  if(result.scope!=='book')return;
  const groups=[...new Map(result.hitGroups.filter(g=>!g.hits.length).map(g=>[g.bookId,g])).values()];
  if(!groups.length)return;
  const box=node('div',undefined,'book-notice');
  box.append(node('strong',`${groups.length} ${groups.length===1?'book satisfies':'books satisfy'} this query without positive matches`));
  box.append(node('p','These books meet the Boolean conditions, but there are no positive words or phrases to highlight.'));
  const links=node('p');for(const g of groups)links.append(link(`${bookCitation(g)} · ${g.edition}`,readerURL(g,readerBase,{section:false})));box.append(links);els.results.append(box);
}
function renderEmpty(result){
  if(result.matchingUnits>0)return;
  const box=node('div',undefined,'no-results');box.append(node('h3','No matches'));
  box.append(node('p',result.scope==='section'
    ?'Try a wildcard, enable spelling equivalence, or choose whole-book scope if a phrase may cross a section boundary.'
    :'Try a wildcard or enable u/v and i/j equivalence. Exact phrases require consecutive words within the same book.'));
  els.results.append(box);
}
function summarize(result){
  const spelling=result.fold?'u/v and i/j equivalent':'source spelling';
  if(result.scope==='section'){
    const count=result.matchingUnits,books=result.matchingBooks.length;
    return `${count.toLocaleString()} matching Niese ${count===1?'section':'sections'}${books?` in ${books} ${books===1?'book':'books'}`:''} · ${spelling} · case-insensitive`;
  }
  const count=result.matchingUnits;
  return `${count} of ${result.selectedBooks.length} ${result.selectedBooks.length===1?'book matches':'books match'} · ${cards.length.toLocaleString()} cited ${cards.length===1?'excerpt':'excerpts'} · ${spelling}`;
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
  cards=[];shown=0;
  els.error.hidden=true;els.button.disabled=true;els.copy.disabled=true;els.more.hidden=true;
  els.region.setAttribute('aria-busy','true');els.results.replaceChildren();els.context.hidden=true;
  els.status.textContent=collection?'Searching…':'Loading the text catalogue…';
  try{
    const ready=await ensureCollection();if(current!==sequence)return;
    if(fromLocation){
      els.query.value=new URLSearchParams(location.search).get('q')||defaultQuery;
      applyState(locationState(location.search,catalog,defaultQuery));
    }
    if(example){
      // Validate examples through the same work/book contract as saved links.
      applyState(locationState(searchURL({query:example.query,work:example.work,book:example.book||'all',scope:example.scope||'section',fold:els.fold.checked},location.href).search,catalog,defaultQuery));
    }
    const state={query:els.query.value.trim(),work:els.work.value,book:els.book.value,scope:els.scope.value,fold:els.fold.checked};
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
    cards=buildResultCards(result,result.records);shown=0;els.results.replaceChildren();
    els.context.hidden=result.scope!=='book';
    els.context.textContent='Whole-book search: each selected book, work and edition is evaluated separately. These excerpts locate positive matches; separate Boolean terms need not occur together in each excerpt. Exact phrases always stay within one book.';
    renderUnhighlightedBooks(result);
    if(cards.length)renderNext();else{els.more.hidden=true;renderEmpty(result);}
    els.status.textContent=summarize(result);els.copy.disabled=false;
    if(writeUrl)saveLocation(state);
  }catch(error){
    if(current!==sequence)return;
    els.error.textContent=error?.message||'The search could not be completed. Please try again.';els.error.hidden=false;
    els.status.textContent=error?.name==='QueryError'?'Please check the search expression.':'The search could not be completed for all selected books. Check the selections and try Search again.';
    els.results.replaceChildren();els.more.hidden=true;els.context.hidden=true;els.copy.disabled=true;
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
root.querySelectorAll('[data-query]').forEach(button=>button.addEventListener('click',()=>search({example:button.dataset})));
els.copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);els.copy.textContent='Link copied';setTimeout(()=>els.copy.textContent='Copy search link',2000);}catch{els.copy.textContent='Copy the address bar URL';}});
window.addEventListener('popstate',()=>search({writeUrl:false,fromLocation:true}));
els.query.value=new URLSearchParams(location.search).get('q')||defaultQuery;
updateScopeHint();
await search({writeUrl:false,fromLocation:true});
