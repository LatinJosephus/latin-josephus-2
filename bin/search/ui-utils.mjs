/** View helpers use offsets into the original text; no user input is HTML. */
export function mergedRanges(ranges, length) {
  const valid = ranges.filter(r => Number.isInteger(r.start) && Number.isInteger(r.end) && r.start >= 0 && r.end > r.start && r.end <= length).map(r => ({start:r.start,end:r.end})).sort((a,b) => a.start-b.start || a.end-b.end);
  const out=[];
  for(const r of valid){const last=out.at(-1);if(last && r.start<=last.end)last.end=Math.max(last.end,r.end);else out.push(r);}
  return out;
}
export function excerptWindows(text, ranges, context=90) {
  const matches=mergedRanges(ranges,text.length);
  if(!matches.length)return [{start:0,end:Math.min(text.length,280)}];
  const windows=[];
  for(const hit of matches){let start=Math.max(0,hit.start-context),end=Math.min(text.length,hit.end+context);while(start>0 && start<hit.start && /[\p{L}\p{M}\p{N}]/u.test(text[start-1]))start--;while(end<text.length && /[\p{L}\p{M}\p{N}]/u.test(text[end]))end++;const last=windows.at(-1);if(last && start<=last.end+25)last.end=Math.max(last.end,end);else windows.push({start,end});}
  return windows;
}
export function buildResultCards(result, records) {
  const byId=new Map(records.map(r=>[r.id,r]));
  const cards=new Map();
  function add(recordIds,hits,unitLabel){const ids=[...new Set(recordIds)].filter(id=>byId.has(id)).sort((a,b)=>(byId.get(a).resultOrder??byId.get(a).order)-(byId.get(b).resultOrder??byId.get(b).order));if(!ids.length)return;const key=ids.join('|');let card=cards.get(key);if(!card){card={key,records:ids.map(id=>byId.get(id)),ranges:{},hitCount:0,unitLabel};cards.set(key,card);}for(const hit of hits){card.hitCount++;for(const span of hit.spans){if(!byId.has(span.recordId))continue;(card.ranges[span.recordId]??=[]).push({start:span.start,end:span.end});}}}
  for(const group of result.hitGroups){if(result.scope==='section'){add(group.recordIds,group.hits,group.unitLabel);}else{for(const hit of group.hits)add(hit.spans.map(s=>s.recordId),[hit],group.unitLabel);}}
  return [...cards.values()].sort((a,b)=>(a.records[0].resultOrder??a.records[0].order)-(b.records[0].resultOrder??b.records[0].order) || a.records.length-b.records.length);
}
export function romanBook(number) {
  let n=Number(number);
  if(!Number.isInteger(n)||n<1||n>3999)return String(number);
  let result='';
  for(const [value,symbol] of [[1000,'M'],[900,'CM'],[500,'D'],[400,'CD'],[100,'C'],[90,'XC'],[50,'L'],[40,'XL'],[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']]){
    while(n>=value){result+=symbol;n-=value;}
  }
  return result;
}
export function workLabel(record) {
  return record.citationPrefix || ({bellum:'Bellum',antiquities:'Antiquities'}[record.work]) || record.work || 'Bellum';
}
export function bookCitation(record) {return `${workLabel(record)} ${romanBook(record.book??record.number)}`;}
export function citationFor(records) {
  const first=records[0],last=records.at(-1);
  if(!first)return '';
  const start=`${bookCitation(first)}.${first.section}`;
  if(first.book!==last.book||first.work!==last.work||first.collectionId!==last.collectionId)return `${start}–${bookCitation(last)}.${last.section}`;
  return first.section===last.section?start:`${start}–${last.section}`;
}
export function readerURL(record,baseURL,{section=true}={}) {
  const readerPath=record.readerPath||({bellum:'bellum-judaicum/',antiquities:'antiquities/'}[record.work])||'bellum-judaicum/';
  const url=new URL(readerPath,baseURL);
  url.searchParams.set('book',record.book??record.number);
  if(section&&record.section!==undefined)url.searchParams.set('niese',record.section);
  return url.href;
}
export function locationState(search,catalog,defaultQuery) {
  const p=new URLSearchParams(search);
  const legacy=!p.has('work')&&p.has('q');
  const fallback=catalog.collections.length===1?catalog.collections[0].id:'all';
  const work=p.get('work')||(legacy?'bellum-latin-cardwell':fallback);
  if(work!=='all'&&!catalog.collections.some(c=>c.id===work))throw new Error('The work in this search link is not available. Choose an available work and search again.');
  let book=p.get('book')||(legacy?'1':'all');
  if(/^\d+$/.test(book)){
    if(work==='all')throw new Error('This search link needs a work for its book number. Choose a work and book, then search again.');
    book=`${work}:${Number(book)}`;
  }
  if(book!=='all'&&!catalog.books.some(b=>b.id===book&&(work==='all'||b.collectionId===work)))throw new Error('The book in this search link is not available. Choose an available book and search again.');
  return {query:p.get('q')||defaultQuery,work,book,scope:p.get('scope')==='book'?'book':'section',fold:p.get('fold')==='1',view:p.get('view')==='concordance'?'concordance':'passages'};
}
export function searchURL(state,currentURL) {
  const url=new URL(currentURL);url.search='';
  url.searchParams.set('q',state.query);url.searchParams.set('work',state.work);url.searchParams.set('book',state.book);
  if(state.scope==='book')url.searchParams.set('scope','book');
  if(state.fold)url.searchParams.set('fold','1');
  if(state.view==='concordance')url.searchParams.set('view','concordance');
  return url;
}
