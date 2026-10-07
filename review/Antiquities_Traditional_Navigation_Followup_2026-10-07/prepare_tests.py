from pathlib import Path
root=Path(r'C:\workspace\LatinJosephus-antiquities-traditional-navigation');review=root/'review/Antiquities_Traditional_Navigation_Followup_2026-10-07'
s=(root/'review/Antiquities_Traditional_Navigation_2026-10-06/navigation.test.cjs').read_bytes().decode().replace('\r\n','\n')
s=s.replace("const base = 'f7d9142cad998e8a005adea1a22532b9a78592db';","const base = '3d6097a0de8af11d862d5a144d6c7ad16d6e9151';")
s=s.replace("  bookTitle.innerText = activeWork.title;';", "  bookTitle.innerText = activeWork.title;';")
s=s.replace(" : '';\n source = source.replace", " : '';\n const supplemental = source.includes('const traditionalRangePoint') ? ',traditionalRangePoint' : '';\n source = source.replace")
s=s.replace('selectView${extra}, assign:', 'selectView${extra}${supplemental}, assign:')
s=s.replace(" return source.replace('  reload().then", " source = source.replaceAll('      setState(() => {', '      window.__qaPending = setState(() => {');\n return source.replace('  reload().then")
# Full projections use the inclusive display boundaries; certified narrative incipits are checked independently.
s=s.replace('const observed=projection(view);','''const observed=projection(view);
    const textPoint=q.traditionalPoint(full,row[language]);
    const textRange=document.createRange();
    if(textPoint.kind==='paragraph')textRange.setStart(textPoint.node,0);else textRange.setStartBefore(textPoint.node);
    const textBody=full.querySelector('tei-body');textRange.setEnd(textBody,textBody.childNodes.length);
    const firstText=projection(textRange.cloneContents());''')
s=s.replace('if(!norm(observed).startsWith(norm(row[language].anchor)))','if(!norm(firstText).startsWith(norm(row[language].anchor)))')
s=s.replace("    const expected=intervals.map(([a,b])=>all.slice(a,b)).join('');", "    const expected=intervals.map(([a,b])=>all.slice(a,b)).join('');\n    const prefixLength=position(textPoint)-intervals[0][0];\n    if(prefixLength<0||!norm(observed.slice(prefixLength)).startsWith(norm(row[language].anchor)))results.failures.push([row.id,language,'rendered first narrative content']);")
s=s.replace('position(q.traditionalPoint(full,s.start)),s.end.kind', 'position((q.traditionalRangePoint||q.traditionalPoint)(full,s.start)),s.end.kind')
s=s.replace('position(q.traditionalPoint(full,s.end))', 'position((q.traditionalRangePoint||q.traditionalPoint)(full,s.end))')
s=s.replace("if(intervals.length>1&&!view.querySelector('[data-structural-notice] a'))throw Error('No disclosure/witness link '+id);", "if(intervals.length>1&&!row['reader-note'])throw Error('Missing shared reader notice data '+id);")
s=s.replace("  await page.locator('#latin [data-structural-notice] summary').click();\n",'')
s=s.replace("#latin [data-structural-notice] a", "#traditional-reader-notice a")
# New follow-up tests exercise real event listeners and exact prefix ownership across the corpus.
marker=" if(process.argv.includes('--protected-source-gate')){"
new_units=r''' if(process.argv.includes('--alignment-all-gate')){
  const checks=[];
  for(const book of ['preface',...Array.from({length:20},(_,i)=>String(i+1))]){
   const snapshots=[];
   for(const baseline of [true,false]){
    await open(`/antiquities/?book=${book}${baseline?'&baseline=1':''}`);
    snapshots.push(await page.evaluate(()=>{
     const q=window.__qa,full=q.getData(),capture=()=>Object.fromEntries(Object.entries(full).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML]));
     const book=capture();q.assign({viewingLevel:'section-level',sectionNum:null});q.setSectionSelectOptions();
     const units=[...document.querySelector('#section-selector').options].filter(o=>o.value).map(o=>o.value);
     const samples=units.map(unit=>{q.assign({sectionNum:unit});return [unit,capture()];});
     return {book,samples};
    }));
   }
   if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Alignment-unit/witness Book regression '+book);
   checks.push({book,alignment_units:snapshots[1].samples.length,book_projection_and_order:'PASS',unit_DOM_and_order:'PASS',result:'PASS'});
   console.log('alignment-all',book,snapshots[1].samples.length);
  }
  fs.writeFileSync(path.join(__dirname,'ALIGNMENT_ALL_QA.json'),JSON.stringify({checks,result:'PASS'},null,2));await browser.close();server.close();return;
 }
'''
s=s.replace(marker,new_units+marker)

new=r''' if(process.argv.includes('--followup-gate')){
  const availability=[];
  for(let book=1;book<=20;book++){
   await open(`/antiquities/?book=${book}&chapter=1&subchapter=1`);
   const checks=await page.evaluate(async()=>{
    const q=window.__qa,chapters=q.traditionalRows('chapter');
    const seed=chapters.find(c=>q.traditionalRows('subchapter',c.chapter).length);
    const results=[];
    for(const row of chapters){
     // Start in a valid Subchapter state, then use the ordinary Chapter-change listener.
     q.assign({chapterNum:seed.chapter,subchapterNum:q.traditionalRows('subchapter',seed.chapter)[0].subchapter,viewingLevel:'subchapter-level'});await q.reload();
     const menu=document.querySelector('#chapter-selector');menu.value=row.chapter;menu.dispatchEvent(new Event('change',{bubbles:true}));await window.__qaPending;
     const expected=q.traditionalRows('subchapter',row.chapter).map(s=>s.subchapter);
     const actual=[...document.querySelector('#subchapter-selector').options].filter(o=>o.value).map(o=>o.value);
     const state=q.getState(),radio=document.querySelector('#subchapter-level');
     if(JSON.stringify(expected)!==JSON.stringify(actual))throw Error('Invented/missing Subchapter '+row.id);
     if(!expected.length){
      if(state.viewingLevel!=='chapter-level'||state.subchapterNum!==null||!radio.disabled||!document.querySelector('#subchapter-selector').disabled)throw Error('Blank Subchapter state '+row.id);
      if(new URL(location.href).searchParams.has('subchapter'))throw Error('Stale zero-subchapter URL '+row.id);
     }else{
      if(state.viewingLevel!=='subchapter-level'||state.subchapterNum!==expected[0]||radio.disabled)throw Error('Subchapter availability '+row.id);
     }
     if(document.querySelector('.structural-unavailable')?.textContent.includes('Select a valid'))throw Error('Ordinary invalid blank selection '+row.id);
     // Re-enable automatically by returning to a chapter with actual Subchapters.
     menu.value=seed.chapter;menu.dispatchEvent(new Event('change',{bubbles:true}));await window.__qaPending;
     if(document.querySelector('#subchapter-level').disabled)throw Error('Subchapter option not restored '+row.id);
     results.push({id:row.id,registered:expected.length,labels:actual,ordinary_transition:'PASS',restored:'PASS'});
    }
    return results;
   });availability.push(...checks);console.log('availability',book,checks.length);
  }
  if(availability.length!==257||availability.filter(c=>!c.registered).length!==9)throw Error('Chapter availability counts');
  const prefixChecks=[];
  for(const book of ['preface',...Array.from({length:20},(_,i)=>String(i+1))]){
   await open(`/antiquities/?book=${book}`);
   prefixChecks.push(...await page.evaluate(()=>{
    const q=window.__qa,all=q.traditionalRegistry(),rows=q.traditionalRows('chapter').concat(q.traditionalRows('subchapter')),checks=[];
    const serialize=n=>n.outerHTML;
    for(const row of rows)for(const language of ['Greek','Latin','English']){
     const loc=row[language],b=loc['boundary-start'];if(!b)continue;
     const full=q.getData()[language],prefix=q.traditionalRangePoint(full,loc),text=q.traditionalPoint(full,loc),view=q.traditionalRangeView(language,full,row);
     if(!view.classList.contains('structural-unavailable')){
      // Exact registered prefix element must be retained by its own range.
      const tag=prefix.node.localName;
      if(tag==='tei-p'&&prefix.node.id===text.node.closest('tei-p')?.id){
       const nums=[...prefix.node.querySelectorAll(':scope > tei-num')];
       if(nums.length&&!view.textContent.includes(nums[0].textContent))throw Error('Lost current division numeral '+row.id+' '+language);
      }else if(!view.textContent.includes(prefix.node.textContent))throw Error('Lost structural prefix '+row.id+' '+language);
     }
     // The immediately preceding registered range ends before this exact prefix.
     const predecessors=all.filter(p=>p.end===row.id);
     for(const prev of predecessors){
      const old=q.traditionalRangeView(language,full,prev);
      if(old.classList.contains('structural-unavailable'))continue;
      if(prefix.node.localName==='tei-p'&&!prefix.node.id&&old.textContent.includes(prefix.node.textContent))throw Error('Heading leakage '+prev.id+' '+language);
      if(prefix.node.id&&old.querySelector(`[id="${prefix.node.id}"]`)?.textContent.trim())throw Error('Prefix element leakage '+prev.id+' '+language);
     }
     checks.push({id:row.id,language,boundary:b,text_locator_target:loc.target,previous_ranges:predecessors.length,result:'PASS'});
    }
    return checks;
   }));
  }
  const VI=[];
  for(const [chapter,subchapter]of [[12,8],[13,null],[13,1]]){
   await open(`/antiquities/?book=6&chapter=${chapter}${subchapter?`&subchapter=${subchapter}`:''}`);
   VI.push(await page.evaluate(({chapter,subchapter})=>{
    const panes=Object.fromEntries(['Latin','English','Greek'].map(l=>[l,document.getElementById(l.toLowerCase()).textContent]));
    if(chapter===12){
     if(!panes.Latin.includes('Abiathar itaque')||panes.Latin.includes('[XIII.i]'))throw Error('VI Latin leakage');
     if(!panes.English.includes('But Abiathar')||panes.English.includes('CHAPTER 13'))throw Error('VI English leakage');
     if(!panes.Greek.includes('Ὁ δ᾽ Ἀβιάθαρος')||panes.Greek.includes('Κατὰ δὲ τοῦτον'))throw Error('VI Greek leakage');
    }else{
     if(!panes.Latin.includes('[XIII.i]')||!panes.Latin.includes('Eo siquidem tempore')||panes.Latin.includes('Abiathar itaque'))throw Error('VI Latin forward prefix');
     if(!panes.English.includes('CHAPTER 13.')||!panes.English.includes('About this time')||panes.English.includes('But Abiathar'))throw Error('VI English forward heading');
     if(!panes.Greek.includes('Κατὰ δὲ τοῦτον'))throw Error('VI Greek Chapter XIII');
    }
    return {chapter,subchapter,panes:Object.fromEntries(Object.entries(panes).map(([l,t])=>[l,{first:t.slice(0,180),last:t.slice(-120)}])),result:'PASS'};
   },{chapter,subchapter}));
  }
  const noticeChecks=[];
  for(const subchapter of [4,6]){
   await open(`/antiquities/?book=11&chapter=8&subchapter=${subchapter}&extra=keep#retained`);
   const record=await page.evaluate(()=>{
    const notices=[...document.querySelectorAll('[data-structural-notice]')];
    if(notices.length!==1||notices[0].closest('.pane')||notices[0].querySelector('ol,li'))throw Error('Repeated/technical reader notice');
    if(!notices[0].textContent.includes('Bamberg 78 preserves')||notices[0].textContent.includes('XML')||notices[0].textContent.includes('fragments'))throw Error('Reader notice wording');
    return {notice_count:notices.length,wording:notices[0].querySelector('p').textContent,placement:'before pane-container',result:'PASS'};
   });
   await page.locator('#traditional-reader-notice a').click();await page.waitForFunction(()=>window.__qaReady&&window.__qa.getState().viewingLevel==='book-level');
   if(await page.locator('[data-structural-notice]').count())throw Error('Notice in Book witness view');
   if(new URL(page.url()).searchParams.get('extra')!=='keep'||!page.url().endsWith('#retained'))throw Error('Book-view link state');
   noticeChecks.push({subchapter,...record,book_view_link:'PASS'});
  }
  await open('/antiquities/?book=preface&subchapter=2');
  await page.selectOption('#subchapter-selector','');
  await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='book-level'&&!new URL(location.href).searchParams.has('subchapter'));
  if(await page.locator('.structural-unavailable').count())throw Error('Cleared Proem selection invalid');
  const URLs=[];
  for(const route of ['?book=1&chapter=9','?book=1&chapter=9&subchapter=1','?book=5&chapter=3&subchapter=2','?book=5&chapter=3&subchapter=999']){
   await open('/antiquities/'+route+'&extra=keep#retained');
   const before=await page.evaluate(()=>({state:window.__qa.getState(),missing:document.querySelectorAll('.structural-unavailable').length,url:location.href}));
   await page.reload();await page.waitForFunction(()=>window.__qaReady);
   const after=await page.evaluate(()=>({state:window.__qa.getState(),missing:document.querySelectorAll('.structural-unavailable').length,url:location.href}));
   if(JSON.stringify(before)!==JSON.stringify(after))throw Error('URL roundtrip '+route);
   const invalid=route.includes('subchapter=999')||route.includes('chapter=9&subchapter=1');
   if((invalid&&after.missing!==3)||(!invalid&&after.missing))throw Error('Manual unavailable policy '+route);
   URLs.push({route,state:after.state,unavailable_panes:after.missing,result:'PASS'});
  }
  if(report.errors.length)throw Error(JSON.stringify(report.errors));
  const result={availability,zero_subchapter_chapters:availability.filter(c=>!c.registered).map(c=>c.id),prefixChecks,VI,noticeChecks,URLs,result:'PASS'};
  fs.writeFileSync(path.join(__dirname,'FOLLOWUP_GATE_QA.json'),JSON.stringify(result,null,2));await browser.close();server.close();console.log('FOLLOWUP_GATE_PASS',availability.length,prefixChecks.length);return;
 }
'''
assert marker in s;s=s.replace(marker,new+marker)
(review/'navigation.test.cjs').write_bytes(s.encode())