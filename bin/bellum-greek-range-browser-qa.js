/* Independent raw-XML oracle; drive actual reader native controls. */
(() => {
 const assert=(ok,label)=>{if(!ok)throw Error(label);};
 const equal=(a,b,label)=>assert(JSON.stringify(a)===JSON.stringify(b),label+" actual "+JSON.stringify(a)+" expected "+JSON.stringify(b));
 const ns="http://www.tei-c.org/ns/1.0", nodes=(d,n)=>[...d.getElementsByTagNameNS(ns,n)];
 const id=n=>n.getAttributeNS("http://www.w3.org/XML/1998/namespace","id");
 const norm=s=>s.replace(/\s+/g," ").trim();
 const visible=s=>[...document.querySelectorAll(s)].filter(n=>!n.closest("[data-original]"));
 const text=n=>{
  if(n.nodeType===Node.TEXT_NODE)return n.data;
  if(n.nodeType!==Node.ELEMENT_NODE)return "";
  if(n.matches("[data-original],tei-num.niese-generated,tei-milestone,tei-pb"))return "";
  if(n.matches("tei-note")){const o=n.querySelector("[data-original]");if(o)return o.textContent;}
  return [...n.childNodes].map(text).join("");
 };
 const paneText=s=>[...document.querySelector(s).children].filter(n=>n.tagName!=="H3").map(text).join("");
 const greek=()=>visible('#greek tei-p[id^="greek-bellum"]').map(n=>Number(n.getAttribute("n")));
 const wait=async test=>{const end=performance.now()+60000;while(!test()){assert(performance.now()<end,"Reader timeout "+location.href);await new Promise(r=>setTimeout(r,0));}await new Promise(r=>setTimeout(r,0));};
 const change=async(selector,value)=>{
  const control=document.querySelector(selector);assert(control,"Missing control "+selector);
  let rendered=false;const observer=new MutationObserver(()=>{rendered=true;observer.disconnect();});
  observer.observe(document.querySelector("#greek"),{childList:true});
  if(control.type==="radio")control.checked=true;
  else{const o=[...control.options].find(o=>o.value===String(value))||(value!==""&&[...control.options].find(o=>o.value&&Number(o.value.replaceAll(",",""))===Number(value)));assert(o,"Missing option "+selector+"="+value);control.value=o.value;}
  control.dispatchEvent(new Event("change",{bubbles:true}));await wait(()=>rendered);
 };
 const level=n=>change("#"+n+"-level");
 const load=async url=>{const r=await fetch(url);assert(r.ok,"XML fetch "+url);const d=new DOMParser().parseFromString(await r.text(),"application/xml");assert(!d.querySelector("parsererror"),"XML parse "+url);return d;};
 const source=(b,l)=>"/assets/xml/bellum/"+l+"/book-"+String(b).padStart(2,"0")+".xml";
 const oracle=async b=>{
  const [latin,g]=await Promise.all([load(source(b,"Latin")),load(source(b,"Greek"))]);
  const body=nodes(latin,"div1")[0],units=[],chapters=[],starts=[];let active=null;
  // Paint raw XML events with the running citation, independently of DOM
  // ranges or renderer helpers. Coarse-unit entry inherits an active citation.
  const visit=(node,unit,chapter)=>{
   if(node.nodeType!==Node.ELEMENT_NODE)return;
   if(node.localName==="div2"){chapter={number:Number(node.getAttribute("n")),units:[],node};chapters.push(chapter);}
   if(node.localName==="p"&&id(node)?.startsWith("latin-bellum"+b+"-num")){
    unit={id:id(node),node,numbers:new Set(),chapter:chapter.number};units.push(unit);chapter.units.push(unit);
    const label=node.textContent.match(/^\s*\[\s*([1-9]\d*)\s*\]/);
    if(label&&id(node)==="latin-bellum"+b+"-num"+label[1]){active=Number(label[1]);starts.push({number:active,node,paragraph:true});}
    if(active!==null)unit.numbers.add(active);
   }
   if(node.localName==="milestone"&&node.getAttribute("unit")==="niese"){assert(/^[1-9]\d*$/.test(node.getAttribute("n")),"Invalid milestone");active=Number(node.getAttribute("n"));starts.push({number:active,node});}
   if(unit&&active!==null)unit.numbers.add(active);
   for(const child of node.childNodes)visit(child,unit,chapter);
  };
  visit(body,null,null);
  const inventory=nodes(nodes(g,"body")[0],"p").filter(p=>id(p)?.startsWith("greek-bellum"+b+"-num"));
  const numbers=inventory.map(p=>Number(p.getAttribute("n")));
  equal(numbers,Array.from({length:[673,654,542,663,572,442,455][b-1]},(_,i)=>i+1),"Greek inventory "+b);
  equal(starts.map(s=>s.number),numbers,"Latin canonical start inventory "+b);
  const ordered=set=>numbers.filter(n=>set.has(n));
  units.forEach(u=>{u.expected=ordered(u.numbers);u.value=u.id.split("-num")[1];});
  chapters.forEach(c=>{c.expected=ordered(new Set(c.units.flatMap(u=>u.expected)));});
  const excerpt=i=>{const r=latin.createRange(),s=starts[i],e=starts[i+1];if(s.paragraph)r.setStartBefore(s.node);else r.setStartAfter(s.node);if(e)r.setEndBefore(e.node);else r.setEnd(body,body.childNodes.length);return norm(r.cloneContents().textContent);};
  return {units,chapters,numbers,inventory,starts,excerpt};
 };
 const hash=async s=>[...new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s)))].map(n=>n.toString(16).padStart(2,"0")).join("");
 window.bellumGreekRangeQA={
  async reproduce(b=1){
   const m=await oracle(b);await change("#book-selector",b);await level("chapter");
   const c=b===1?m.chapters.find(c=>c.number===4):m.chapters.find(c=>c.units.some(u=>u.node.querySelector('milestone[unit="niese"]')));
   await change("#chapter-selector",c.number);const r={book:b,chapter:c.number,actual:greek(),expected:c.expected};r.missing=r.expected.filter(n=>!r.actual.includes(n));
   await level("section");const u=b===1?m.units.find(u=>u.value==="86"):c.units.find(u=>u.node.querySelector('milestone[unit="niese"]'));
   await change("#section-selector",u.value);r.unit={id:u.id,actual:greek(),expected:u.expected};
   r.dom=visible("#greek tei-p").map(p=>({id:p.id,n:p.getAttribute("n"),sameAs:p.getAttribute("sameAs")}));
   await level("niese");await change("#niese-selector",b===1?87:r.missing[0]);r.direct=greek();return r;
  },
  async book(b,source,checkGreek=true){
   const m=await oracle(b);await change("#english-source-selector",source);await change("#book-selector",b);await level("book");
   const output=[],counts={chapters:0,subchapters:0,niese:0},split=[],safeguards=[];
   const record=key=>output.push({key,latin:document.querySelector("#latin").innerHTML,english:document.querySelector("#english").innerHTML,latinText:norm(paneText("#latin")),englishText:norm(paneText("#english")),...(key.startsWith("niese:")?{greek:document.querySelector("#greek").innerHTML}:{})});
   record("book:"+b);await level("chapter");
   equal([...document.querySelector("#chapter-selector").options].filter(o=>o.value!=="").map(o=>Number(o.value)),m.chapters.map(c=>c.number),"Chapter menu "+b);
   for(const c of m.chapters){
    await change("#chapter-selector",c.number);
    if(checkGreek)equal(greek(),c.expected,"Chapter "+b+"."+c.number);
    if(checkGreek&&b===1&&c.number===4){const a=greek(),i=a.indexOf(86);equal(a.slice(i,i+3),[86,87,88],"Explicit I.4 fixture");const p=document.querySelector("#greek #greek-bellum1-num87");assert(p&&norm(text(p))===norm(m.inventory[86].textContent),"I.87 exact canonical Greek text");}
    record("chapter:"+b+"."+c.number);counts.chapters++;
   }
   await level("section");await change("#chapter-selector","");
   equal([...document.querySelector("#section-selector").options].filter(o=>o.value!=="").map(o=>Number(o.value)),m.units.map(u=>Number(u.value)),"Sub-chapter menu "+b);
   for(let i=0;i<m.units.length;i++){
    const u=m.units[i];await change("#section-selector",u.value);if(checkGreek)equal(greek(),u.expected,"Sub-chapter "+u.id);
    if(i&&u.expected[0]===m.units[i-1].expected.at(-1))split.push({previous:m.units[i-1].id,current:u.id,niese:u.expected[0]});
    if(checkGreek&&b===1&&u.value==="86")assert(greek().includes(87),"Internal I.87 fixture");
    record("unit:"+b+"."+u.value);counts.subchapters++;
   }
   await level("niese");
   equal([...document.querySelector("#niese-selector").options].filter(o=>o.value!=="").map(o=>Number(o.value.replaceAll(",",""))),m.numbers,"Niese menu "+b);
   for(let i=0;i<m.numbers.length;i++){
    const n=m.numbers[i];await change("#niese-selector",n);
    if(checkGreek){equal(greek(),[n],"Direct Niese "+b+"."+n);assert(norm(paneText("#greek"))===norm(m.inventory[i].textContent),"Exact Greek text "+b+"."+n);assert(norm(paneText("#latin"))===m.excerpt(i),"Exact Cardwell span "+b+"."+n);}
    if([[3,3],[6,267],[6,356],[6,427],[7,26]].some(([book,section])=>book===b&&section===n)){
     const entry=m.starts[i],owner=entry.paragraph?entry.node:entry.node.closest("p"),expected=id(owner);
     assert(document.querySelector('#latin [id="'+expected+'"]'),"Safeguard owner "+b+"."+n);
     if(b===3&&n===3)equal(expected,"latin-bellum3-num1","III.3 owner");
     if(b===6&&n===427)equal(expected,"latin-bellum6-num420","VI.427 owner");
     safeguards.push({niese:n,canonicalId:expected});
    }
    record("niese:"+b+"."+n);counts.niese++;if(n%100===0)console.log("Greek range QA "+source+" book "+b+" Niese "+n);
   }
   const digests=await Promise.all(output.map(async row=>({key:row.key,hash:await hash(JSON.stringify(row))})));
   return {book:b,source,counts,split,safeguards,digests,first:m.numbers[0],final:m.numbers.at(-1)};
  },change,level,wait
 };
})();
