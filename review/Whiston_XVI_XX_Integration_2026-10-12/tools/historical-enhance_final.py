import pathlib
ROOT=pathlib.Path(__file__).parent/'candidate';PACK=ROOT/'review/Whiston_XVI_XX_Integration_2026-10-12';f=PACK/'tools/browser_qa.cjs'
s=f.read_text(encoding='utf-8')
s=s.replace('const result={state:window.__qa.state(),languages:{}};', 'const result={state:window.__qa.state(),url:location.search,controls:{previous:document.querySelector("#niese-previous")?.disabled,next:document.querySelector("#niese-next")?.disabled},languages:{}};')
s=s.replace('const s=actual.languages.english;\n assert(!s.allVisible', '''const s=actual.languages.english;
 assert(actual.state.viewingLevel==='niese-level'&&Number(actual.state.nieseNum)===expected.number,'Settled selected state differs',actual);
 assert((expected.book==='preface'?actual.state.bookNum==='preface':Number(actual.state.bookNum)===Number(expected.book)),'Settled book state differs',actual);
 const params=new URLSearchParams(actual.url);assert(Number(params.get('niese'))===expected.number,'Selected Niese URL differs',actual);
 const all=oracle.filter(e=>e.book===expected.book);const first=Math.min(...all.map(e=>e.number)),last=Math.max(...all.map(e=>e.number));
 assert(actual.controls.previous===(expected.number===first)&&actual.controls.next===(expected.number===last),'Navigation limit state differs',actual);
 assert(!s.allVisible''')
s=s.replace('GreekLatinPresentationUnchanged:true,URL:new URL(page.url()).search', 'GreekLatinPresentationUnchanged:true,settledStateAndURLVerified:true,navigationLimitsVerified:true,URL:new URL(page.url()).search')
f.write_text(s,encoding='utf-8')
print('Final exhaustive section checks strengthened with settled state, URL and navigation limits')
