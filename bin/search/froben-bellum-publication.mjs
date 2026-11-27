/** Independent source/ownership/geometry control; never imports the extractor. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
export const FROBEN_BELLUM_SOURCE='assets/data/bellum-froben1524/reader.json';
export const FROBEN_BELLUM_SHA='7817b7bc22def4486431a29aecef7565f0d3be87e941ca5dae29726737500e5e';
const sha=value=>createHash('sha256').update(value).digest('hex');
const counts=[673,654,542,663,572,442,455];
export function validateFrobenBellumSourceProjection(corpus,report,manifest,spec,root){
  assert.equal(spec.source,FROBEN_BELLUM_SOURCE);
  const bytes=fs.readFileSync(path.join(root,FROBEN_BELLUM_SOURCE));
  assert.equal(sha(bytes),FROBEN_BELLUM_SHA,'The released Froben Bellum reader changed');
  const data=JSON.parse(bytes),rows=[],byKey=new Map();
  for(const page of data.pages)for(const row of page.rows){
    const key=page.image+':'+row.id;assert(!byKey.has(key));
    byKey.set(key,rows.length);rows.push({...row,page,chars:Array.from(row.text)});
  }
  function point(p){const i=byKey.get(p[0]+':'+p[1]);assert(i!==undefined&&Number.isInteger(p[2])&&p[2]>=0&&p[2]<=rows[i].chars.length);return [i,p[2]];}
  const compare=(a,b)=>a[0]-b[0]||a[1]-b[1];
  function parts(span,body=true){
    const [first,lo]=point(span.start),[last,hi]=point(span.end);assert(compare([first,lo],[last,hi])<0);
    const out=[];
    for(let i=first;i<last+Number(hi>0);i++){
      const row=rows[i],a=i===first?lo:0,b=i===last?hi:row.chars.length;
      if(b>a&&(!body||row.role==='paragraph'))out.push({row,i,lo:a,hi:b,text:row.chars.slice(a,b).join('')});
    }
    return out;
  }
  const units=data.niese.filter(unit=>unit.book===`latin-bellum${spec.number}`),ownership=new Map();
  assert.equal(units.length,counts[spec.number-1]);assert.equal(corpus.length,units.length);
  for(let n=0;n<units.length;n++){
    const record=corpus[n],unit=units[n],span=unit.spans[0],rawParts=parts(span),raw=rawParts.map(p=>p.text).join('');
    assert.equal(unit.spans.length,1);assert.equal(unit.number,n+1);
    assert.equal(record.id,`bellum-latin-froben1524-${spec.number}-${n+1}`);
    assert.equal(record.collectionId,'bellum-latin-froben1524');assert.equal(record.work,'bellum');assert.equal(record.language,'Latin');
    assert.equal(record.edition,'Froben 1524');assert.equal(record.book,spec.number);assert.equal(record.section,n+1);
    assert.equal(record.citationScheme,'niese');assert.equal(record.sourcePath,FROBEN_BELLUM_SOURCE);
    assert.equal(record.sourceVersion,FROBEN_BELLUM_SHA);assert.equal(record.sourceId,unit.id);
    assert.equal(record.sourceOccurrence,'bellum-latin-froben1524-'+unit.id);
    assert.deepEqual(record.readerLink,{path:'bellum-judaicum/',params:{book:spec.number,niese:n+1,froben:'1'}});
    assert.equal(record.url,`/bellum-judaicum/?book=${spec.number}&niese=${n+1}&froben=1`);
    assert.equal(record.frobenSource.nieseId,unit.id);assert.deepEqual(record.frobenSource.span,span);
    assert.equal(record.frobenSource.rawNarrativeSHA256,sha(raw));
    const expected=raw.replace(/¬\s*/gu,'').replace(/[\r\n\t]/gu,' ').trim();
    assert.equal(record.text,expected,'Froben source spelling or source order changed');
    const [a,b]=[point(span.start),point(span.end)];
    for(const [layer,key] of [['frobenBooks','printedBooks'],['divisions','printedDivisions']]){
      const related=data[layer].filter(item=>item.spans.some(s=>compare(point(s.start),b)<0&&compare(point(s.end),a)>0))
        .map(item=>({id:item.id,label:item.label,...(item.kind?{kind:item.kind}:{})}));
      assert.deepEqual(record.frobenSource[key],related,'Native Froben references changed');
    }
    const cells=[];
    for(const p of rawParts){
      const intervals=ownership.get(p.i)||[];intervals.push([p.lo,p.hi]);ownership.set(p.i,intervals);
      let source=p.row.chars.slice(0,p.lo).join('').length;
      for(let cp=p.lo;cp<p.hi;cp++){
        const value=p.row.chars[cp];cells.push({value,row:p.row,i:p.i,cp,source});source+=value.length;
      }
    }
    // Different control implementation: walk characters and explicit joins,
    // then check every retained character's exact source-to-search geometry.
    const retained=[],joins=[];let output=0;
    for(let i=0;i<cells.length;i++){
      if(cells[i].value==='¬'){
        const first=i;while(i+1<cells.length&&cells[i+1].value==='¬')i++;
        while(i+1<cells.length&&/^\s$/u.test(cells[i+1].value))i++;
        const next=cells[i+1];assert(next);
        joins.push({marker:[cells[first].row.page.image,cells[first].row.id,cells[first].cp],
          following:[next.row.page.image,next.row.id,next.cp],sourceText:cells.slice(first,i+1).map(c=>c.value).join(''),
          wordContinuation:/[\p{L}\p{M}\p{N}]/u.test(next.value)});
        continue;
      }
      retained.push({...cells[i],projected:/^[\r\n\t]$/u.test(cells[i].value)?' ':cells[i].value});
    }
    while(retained.length&&/^\s$/u.test(retained[0].projected))retained.shift();
    while(retained.length&&/^\s$/u.test(retained.at(-1).projected))retained.pop();
    assert.deepEqual(record.frobenSource.joins,joins,'Unexplained Froben word join');
    let pi=0;
    for(const cell of retained){
      while(record.sourcePieces[pi]?.recordEnd<=output)pi++;
      const piece=record.sourcePieces[pi];assert(piece,'Missing source geometry');
      assert.equal(piece.image,cell.row.page.image);assert.equal(piece.line,cell.row.id);
      assert.equal(piece.sourceStart+output-piece.recordStart,cell.source,'Source/search offset differs');
      assert.equal(piece.recordStart<=output&&piece.recordEnd>=output+cell.projected.length,true);
      output+=cell.projected.length;
    }
    assert.equal(output,record.text.length);
    let cursor=0;
    for(const piece of record.sourcePieces){
      assert.equal(piece.recordStart,cursor);assert(piece.recordEnd>cursor);
      const row=rows[byKey.get(piece.image+':'+piece.line)];assert(row?.role==='paragraph');
      assert.equal(piece.pageId,row.page.id);assert.equal(piece.pageLabel,row.page.display);assert.equal(piece.facsimile,row.page.facsimile);
      const original=row.text.slice(piece.sourceStart,piece.sourceEnd),shown=record.text.slice(piece.recordStart,piece.recordEnd);
      assert.equal(piece.textSHA256,sha(original));assert.equal(piece.sourceEnd-piece.sourceStart,piece.recordEnd-piece.recordStart);
      if(piece.projection==='literal')assert.equal(shown,original);
      else {assert.equal(piece.projection,'whitespace');assert(/^[\r\n\t]+$/u.test(original));assert.equal(shown,' '.repeat(original.length));}
      cursor=piece.recordEnd;
    }
    assert.equal(cursor,record.text.length);
  }
  const book=data.books.find(book=>book.id===`latin-bellum${spec.number}`),accounting=[];
  for(const p of parts(book.spans[0],false)){
    const owned=(ownership.get(p.i)||[]).sort((a,b)=>a[0]-b[0]);
    if(p.row.role==='paragraph'){
      let cursor=p.lo;for(const [a,b] of owned){assert.equal(a,cursor,'Duplicate or missing physical Froben text');assert(b>a);cursor=b;}assert.equal(cursor,p.hi);
    }else assert.deepEqual(owned,[]);
    accounting.push({image:p.row.page.image,line:p.row.id,role:p.row.role,startCP:p.lo,endCP:p.hi,textSHA256:sha(p.text),
      classification:p.row.role==='paragraph'?'indexed-running-text':'excluded-printed-heading'});
  }
  assert.deepEqual(report.sourceAccounting,accounting,'Froben source-row accounting differs');
  assert.equal(report.coverage.sourceIntervalsOwnedOnce,true);assert.equal(report.coverage.sectionsExactlyRestored,units.length);
  assert.deepEqual(report.source,{path:FROBEN_BELLUM_SOURCE,sha256:FROBEN_BELLUM_SHA,bytes:bytes.length});
  return {book:spec.number,sections:units.length,sourceRows:accounting.length,paragraphRows:accounting.filter(x=>x.role==='paragraph').length,
    explicitContinuations:corpus.reduce((n,r)=>n+r.frobenSource.joins.length,0)};
}
