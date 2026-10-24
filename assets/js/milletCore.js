/* Exact source coordinates, independent of native chapters and DOM decoration. */
export const MODES = new Set(['running','book','source','chapter','page','preliminary']);
export const codepoints = text => Array.from(text);
export function utf16Offset(text, cp) {
  const chars=codepoints(text);
  if (!Number.isSafeInteger(cp) || cp<0 || cp>chars.length) throw new Error('Invalid Millet codepoint offset.');
  return chars.slice(0,cp).join('').length;
}
export const canonicalIds = mapping => mapping.canonical_targets?.map(c=>c.xml_id) || [mapping.canonical.xml_id];
export function validateBook(data) {
  if (!['millet1556-reader-book/1','millet1556-reader-preliminary/1'].includes(data?.schema)) throw new Error('Unsupported Millet data.');
  const lines=new Map(), ids=new Set(), mappings=new Map();
  for (const l of data.lines) {
    if (typeof l.text_exact!=='string' || lines.has(l.TEI_line_id)) throw new Error('Invalid or duplicate Millet source line.');
    lines.set(l.TEI_line_id,l);
  }
  const check=f=>{
    const l=lines.get(f.line);
    if (!l || !Number.isSafeInteger(f.start_cp) || !Number.isSafeInteger(f.end_cp) || f.start_cp<0 || f.end_cp<=f.start_cp || f.end_cp>codepoints(l.text_exact).length
      || utf16Offset(l.text_exact,f.start_cp)!==f.start_utf16 || utf16Offset(l.text_exact,f.end_cp)!==f.end_utf16) throw new Error('Invalid Millet span or coordinate conversion.');
  };
  for (const m of data.mappings) {
    if (mappings.has(m.id) || !Array.isArray(m.fragments)) throw new Error('Duplicate or malformed Millet mapping.');
    for (const id of canonicalIds(m)) {if (!/^latin-deh[1-5]-num[1-9]\d*$/.test(id)) throw new Error('Invalid canonical Millet target.'); ids.add(id);}
    if (!m.fragments.length && m.relation!=='absent') throw new Error('Unexplained empty Millet correspondence.');
    m.fragments.forEach(check);mappings.set(m.id,m);
  }
  for (const a of data.annotations) {if(a.primary_coverage!==false) throw new Error('A secondary Millet annotation cannot become primary.'); (a.fragments||[]).forEach(check);}
  return {lines,mappings,canonicalIds:ids};
}
export function indexBook(data) {
  const checked=validateBook(data),byCanonical=new Map(),byLine=new Map();
  for (const m of data.mappings) {
    for (const id of canonicalIds(m)) {if(!byCanonical.has(id))byCanonical.set(id,[]);byCanonical.get(id).push(m);}
    for (const f of m.fragments) {if(!byLine.has(f.line))byLine.set(f.line,[]);byLine.get(f.line).push({...f,mapping:m.id});}
  }
  return {...checked,byCanonical,byLine};
}
// Atoms preserve every source character once even for overlapping/multiple links.
export function lineAtoms(line,fragments=[],annotations=[]) {
  const length=codepoints(line.text_exact).length;
  const boundaries=[...new Set([0,length,...fragments.flatMap(f=>[f.start_cp,f.end_cp]),...annotations.flatMap(f=>[f.start_cp,f.end_cp])])].sort((a,b)=>a-b);
  return boundaries.slice(0,-1).map((a,i)=>{
    const b=boundaries[i+1];
    return {start_cp:a,end_cp:b,start_utf16:utf16Offset(line.text_exact,a),end_utf16:utf16Offset(line.text_exact,b),text:codepoints(line.text_exact).slice(a,b).join(''),mappings:[...new Set(fragments.filter(f=>f.start_cp<=a&&f.end_cp>=b).map(f=>f.mapping))],annotations:[...new Set(annotations.filter(f=>f.start_cp<=a&&f.end_cp>=b).map(f=>f.annotation))]};
  });
}
export function visibleLines(data,{mode='running',chapter=null,page=null}={}) {
  if(mode==='page') return data.lines.filter(l=>l.image_number===Number(page));
  if(mode==='chapter') {
    const chapters=data.divisions.filter(d=>d.is_native_chapter),i=chapters.findIndex(d=>d.id===chapter);
    if(i<0) return [];
    const a=chapters[i].chapter_start_index,b=chapters[i+1]?.chapter_start_index??Infinity;
    return data.lines.filter(l=>l.source_index>=a&&l.source_index<b && (l.primary||l.source_region_type==='heading'));
  }
  if(mode==='source'||mode==='preliminary') return data.lines;
  const range=data.native?.narrative_image_range;
  const headingLines=new Set(data.divisions.filter(d=>d.is_native_chapter||(range&&d.image_number>=range[0]&&d.image_number<=range[1])).flatMap(d=>d.line_refs));
  return data.lines.filter(l=>l.primary||headingLines.has(l.TEI_line_id));
}
export const chapterMappings = (data,chapter) => data.mappings.filter(m=>(m.canonical_targets||[m.canonical]).some(c=>String(c.chapter)===String(chapter)));
export function readingView(data,view,navigation,canonical) {
  const lines=visibleLines(data,view);
  if(view.mode!=='running'||!['section-level','chapter-level'].includes(navigation.level))return {lines,included:null};
  const mappings=navigation.level==='chapter-level'?chapterMappings(data,navigation.chapter):data.mappings.filter(m=>canonicalIds(m).includes(canonical));
  if(!mappings.length)return {lines:[],included:new Set()};
  const ids=new Set(mappings.flatMap(m=>m.fragments.map(f=>f.line)));
  return {lines:lines.filter(l=>ids.has(l.TEI_line_id)),included:new Set(mappings.map(m=>m.id))};
}
// Reading layout is independent of frozen line coordinates. Suppressed ¬ stays
// in a hidden source span; separators are outside every source-line payload.
export function flowSeparator(previous,next) {
  return !previous || /¬\s*$/.test(previous) || /\s$/.test(previous) || /^\s/.test(next) ? '' : ' ';
}
export function readingParts(text,start=0,end=text.length) {
  const tail=text.search(/¬\s*$/);let offset=start;
  return text.slice(start,end).split(/(¬)/).map(part=>{
    const entry={text:part,hidden:part==='¬'||(tail>=0&&offset>=tail)};offset+=part.length;return entry;
  });
}
export function flowGroups(lines) {
  const groups=[];let last;
  for(const line of lines){
    const same=last&&last.source_region_type===line.source_region_type&&last.region_id===line.region_id&&last.image_number===line.image_number;
    const pageContinuation=last&&last.image_number!==line.image_number&&last.source_region_type==='paragraph'&&line.source_region_type==='paragraph';
    const continuedWord=last&&last.source_region_type===line.source_region_type&&/¬\s*$/.test(last.text_exact);
    if(!same&&!pageContinuation&&!continuedWord)groups.push({type:line.source_region_type,lines:[]});
    groups.at(-1).lines.push(line);last=line;
  }
  return groups;
}
export function folioLabels(data) {
  const labels=new Map(),headers=new Map();let preceding;
  for(const l of data.lines)if(l.source_region_type==='header')headers.set(l.image_number,(headers.get(l.image_number)||'')+' '+l.text_exact);
  for(const [i,page] of data.pages.entries()){
    const header=(headers.get(page.image_number)||'').trim();
    const number=header.match(/\b\d+\b/)?.[0];
    if(number){labels.set(page.image_number,`Folio ${number} recto`);preceding={number,image:page.image_number};}
    else if(header&&preceding&&page.image_number===preceding.image+1)labels.set(page.image_number,`Folio ${preceding.number} verso`);
    else{
      const dedication=data.native?.dedication_images||[];
      const d=dedication.indexOf(page.image_number);
      labels.set(page.image_number,d>=0?`Dedication, ${d===0?'recto':'verso'}`:data.book===1&&i<2?`Preface, ${i===0?'recto':'verso'}`:`Unnumbered leaf ${i+1}`);
      preceding=null;
    }
  }
  return labels;
}
export function locationFromUrl(url) {
  const p=new URL(url).searchParams;
  return {enabled:p.get('french')==='millet1556',mode:MODES.has(p.get('millet-view'))?p.get('millet-view'):'running',chapter:p.get('millet-chapter'),page:p.get('millet-page'),canonical:p.get('millet-unit'),alignment:p.get('millet-align')!=='0',folios:p.get('millet-folios')==='1'};
}
export function updateMilletUrl(url,state) {
  const u=new URL(url);
  for(const k of ['french','millet-view','millet-chapter','millet-page','millet-unit','millet-align','millet-folios'])u.searchParams.delete(k);
  if(!state.enabled)return u;
  u.searchParams.set('french','millet1556');
  if(state.mode!=='running')u.searchParams.set('millet-view',state.mode);
  if(state.mode==='chapter'&&state.chapter)u.searchParams.set('millet-chapter',state.chapter);
  if(state.mode==='page'&&state.page)u.searchParams.set('millet-page',state.page);
  if(state.canonical)u.searchParams.set('millet-unit',state.canonical);
  if(!state.alignment)u.searchParams.set('millet-align','0');
  if(state.folios)u.searchParams.set('millet-folios','1');
  return u;
}
export async function sha256(bytes) {
  const result=await crypto.subtle.digest('SHA-256',bytes);
  return [...new Uint8Array(result)].map(n=>n.toString(16).padStart(2,'0')).join('');
}
export function createMilletLoader(base,fetcher=fetch) {
  let manifestPromise;const cache=new Map();
  const manifest=()=>manifestPromise||=(async()=>{const r=await fetcher(new URL('manifest.json',base));if(!r.ok)throw new Error('Millet source catalogue is unavailable.');const d=await r.json();if(d.schema!=='millet1556-reader/1'||d.authority.status!=='INTEGRATION_READY')throw new Error('Millet source catalogue is uncertified.');return d;})().catch(e=>{manifestPromise=null;throw e;});
  const book=async number=>{
    const m=await manifest(),key=Number(number);
    const record=key===0?m.preliminary:m.books.find(b=>b.book===key);
    if(!record)throw new Error('This Millet book is unavailable.');
    if(!cache.has(key))cache.set(key,(async()=>{const r=await fetcher(new URL(record.path,base));if(!r.ok)throw new Error('Millet book is unavailable.');const bb=await r.arrayBuffer();if(await sha256(bb)!==record.sha256)throw new Error('Millet book integrity check failed.');const d=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bb));if(d.book!==key||d.version!==m.version)throw new Error('Stale Millet book data.');validateBook(d);return d;})().catch(e=>{cache.delete(key);throw e;}));
    return cache.get(key);
  };
  return {manifest,book};
}
