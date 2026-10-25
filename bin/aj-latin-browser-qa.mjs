import {loadAjLayer,createAjTextLoader,ajSection} from '/assets/js/dehAntiquitiesCore.js';
const normalize=s=>s.replace(/\[\s*\d+\s*\]/g,'').replace(/\s+/g,' ').trim();
const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
const text=node=>{const copy=node.cloneNode(true);copy.querySelectorAll('[data-original],.niese-correspondence-note,.structural-unavailable').forEach(n=>n.remove());return normalize(copy.textContent);};
document.querySelector('#run').addEventListener('click',async event=>{
 event.target.disabled=true;
 const report={status:'RUNNING',sections:0,coordinates:0,components:0,witness_views:0,source_corruptions_rejected:0,failures:[],userAgent:navigator.userAgent};
 try{
  const digest=async raw=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(n=>n.toString(16).padStart(2,'0')).join('');
  const expectedRaw=await fetch('/__qa__/comparison-expectations.json').then(r=>r.arrayBuffer());
  assert(await digest(expectedRaw)==='cce37e708a39e5475a0ea3b7fb02b7b5076bc90f46f7ce52418eb92344b6353a','Independent browser expectations changed');
  const expected=JSON.parse(new TextDecoder().decode(expectedRaw));
  const [concordance,certificateRaw,html]=await Promise.all([
   fetch('/assets/data/deh-josephus-concordance.json').then(r=>r.json()),
   fetch('/__qa__/certified-boundaries.json').then(r=>r.arrayBuffer()),fetch('/deh/').then(r=>r.text())]);
  const pin=new DOMParser().parseFromString(html,'text/html').querySelector('#deh-parallels').dataset.ajAlignmentSha;
  const layer=await loadAjLayer('/assets/data/deh-aj-display.v1.json',pin,concordance);
  assert(await digest(certificateRaw)===layer.reconciliation.audit_sha256,'Boundary certificate changed');
  const certificate=JSON.parse(new TextDecoder().decode(certificateRaw));
  const load=createAjTextLoader(new URL('/assets/xml/',location.href),layer);
  for(const record of layer.records){
   for(const [language,key]of [['Latin','aj_latin'],['Greek','aj_niese'],['English','aj_whiston']]){
    let sections=0;
    for(const component of record.components){
     const book=component.frozen_target.book,data=await load(key,book);
     for(const section of component.sections[language]){
      const fragment=ajSection(data,section),e=expected[`${language}:${book}:${section.number}`];
      assert(text(fragment)===e.text,`Text differs: ${record.id} ${language} ${book}.${section.number}`);
      assert((fragment.dataset.sourceAvailable!=='false')===e.available,'Witness availability changed');
      if(section.note)assert(fragment.textContent.includes(section.note),'Witness qualification omitted');
      if(language==='Latin'){
       const s=certificate.current_components.find(c=>c.id===component.component_id).sections.find(s=>s.number===section.number);
       const body=data.querySelector('tei-body');
       for(let i=0;i<section.spans.length;i++)for(const edge of ['start','end']){
        const p=section.spans[i][edge];let node=body;for(const n of p.path)node=node.children[n];
        const range=document.createRange();range.setStart(body,0);
        if(p.side==='before')range.setEndBefore(node);else if(p.side==='after')range.setEndAfter(node);
        else range.setEnd(node,p.side==='end'?node.childNodes.length:0);
        assert(range.toString().length===s.spans[i][edge].body_utf16_offset,`UTF16 coordinate differs ${component.component_id} ${section.number}`);
        assert([...range.toString()].length===s.spans[i][edge].body_codepoint_offset,'Codepoint coordinate differs');
        report.coordinates++;
       }
      }
      report.sections++;sections++;document.querySelector('#sample').replaceChildren(fragment);
     }
     report.components++;
    }
    report.witness_views++;
    const tr=document.createElement('tr');for(const s of [record.id,language,sections,'PASS']){const td=document.createElement('td');td.textContent=s;tr.append(td);}document.querySelector('#rows').append(tr);
   }
  }
  const corrupted=createAjTextLoader(new URL('/__qa__/corrupt/assets/xml/',location.href),layer);
  for(const book of [3,9,14,15,16,17,18,20]){
   let rejected=false;try{await corrupted('aj_latin',book);}catch(e){rejected=e.message.includes('differs from the AJ display authority');}
   assert(rejected,`Corrupted Latin source accepted: ${book}`);report.source_corruptions_rejected++;
  }
  assert(report.sections===420&&report.components===132&&report.witness_views===93&&report.coordinates===278,'Incomplete browser population');
  report.status='PASS';
 }catch(e){report.status='FAIL';report.failures.push(String(e));}
 document.querySelector('#qa-status').textContent=report.status;
 document.querySelector('#qa-result').textContent=JSON.stringify(report,null,2);
 document.querySelector('#qa-result').dataset.complete=report.status;
 await fetch('/__qa__/results',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(report)});
});
